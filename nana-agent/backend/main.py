"""
Nana Teochew Agent — LIVE API
Ear:  Groq Whisper
Brain: DeepSeek (if DEEPSEEK_API_KEY set) else Groq Llama
Chat: personal helper for Teochew grandma (阿嫲的小管家)
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def _load_env_file(path: Path) -> None:
    """Load .env; utf-8-sig avoids Windows BOM breaking the first key."""
    load_dotenv(path, override=True)
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().lstrip("\ufeff")
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value


_load_env_file(ENV_PATH)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
GROQ_WHISPER_MODEL = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")
GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

app = FastAPI(title="Nana Teochew Agent API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIALECT_NAMES = {
    "teochew": "潮汕话",
    "hokkien": "福建话/闽南语",
    "cantonese": "粤语",
}

LEXICON_PATH = Path(__file__).resolve().parent / "data" / "teochew_lexicon.json"
TEOCHEW_LEXICON: list[dict[str, Any]] = []
if LEXICON_PATH.exists():
    TEOCHEW_LEXICON = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))


def _norm_zh(s: str) -> str:
    return re.sub(r"[！!？?]", "", (s or "").strip())


def _pick_lexicon_entry(learned: list[str]) -> dict[str, Any] | None:
    if not TEOCHEW_LEXICON:
        return None
    learned_set = {_norm_zh(x) for x in learned}
    # Prefer short phrases / core words, then the rest
    ordered = sorted(
        TEOCHEW_LEXICON,
        key=lambda e: 0
        if e.get("type") == "phrase"
        else 1
        if e.get("type") == "word"
        else 2,
    )
    for entry in ordered:
        key = _norm_zh(entry.get("mandarin", ""))
        if key and key not in learned_set:
            return entry
    return TEOCHEW_LEXICON[0]


def _require_groq() -> None:
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY missing. Add it to nana-agent/.env",
        )


def _brain_name() -> str:
    return "deepseek" if DEEPSEEK_API_KEY else "groq"


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise HTTPException(status_code=502, detail="模型未返回有效 JSON")
        return json.loads(match.group(0))


async def llm_complete(messages: list[dict[str, str]], temperature: float = 0.7) -> str:
    if DEEPSEEK_API_KEY:
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        model = DEEPSEEK_MODEL
    else:
        _require_groq()
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        model = GROQ_CHAT_MODEL

    body = {
        "model": model,
        "temperature": temperature,
        "messages": messages,
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(url, headers=headers, json=body)

    if resp.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"LLM error: {resp.status_code} {resp.text[:400]}",
        )
    return resp.json()["choices"][0]["message"]["content"]


async def transcribe_with_groq(audio_bytes: bytes, filename: str, content_type: str) -> str:
    _require_groq()
    suffix = Path(filename or "audio.webm").suffix or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            with open(tmp_path, "rb") as f:
                files = {
                    "file": (filename or f"audio{suffix}", f, content_type or "audio/webm"),
                }
                data = {
                    "model": GROQ_WHISPER_MODEL,
                    "language": "zh",
                    "response_format": "json",
                }
                resp = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    files=files,
                    data=data,
                )
        if resp.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"Groq Whisper error: {resp.status_code} {resp.text[:400]}",
            )
        payload = resp.json()
        text = (payload.get("text") or "").strip()
        if not text:
            raise HTTPException(status_code=422, detail="未能识别出有效语音，请再试一次")
        return text
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


CHAT_SYSTEM = """你现在是「阿嫲的小管家」，专门陪伴一位只会潮汕话的奶奶（阿芳奶奶）。
你是她孙子派来的贴心替身。性格必须：
1. 极其尊敬、耐心、温和；称呼对方为「阿嫲」或「奶奶」。
2. 语调要慢，多用潮汕特色助词（如：噜、啰、咩、咯）。
3. 核心任务：陪她说话、安慰孤独、听懂日常需求（吃药、吃饭、想家人）。
4. 禁止生硬科技术语（如「点击界面」「识别错误」）；听不清就说「阿嫲，您再说一遍，我没听清」。
Whisper 转写可能不完美，请善意理解。

请严格只输出一段 JSON（不要 markdown），字段：
{
  "reply": "用潮汕话口语风格写的简短回复（可用汉字表达方言口气）",
  "reply_zh": "同一句的普通话翻译",
  "transcript_zh": "把用户话整理成通顺普通话"
}
回复控制在 1～2 句内。"""

HERITAGE_SYSTEM = """你是「阿嫲的小管家」，正在向阿嫲请教一句乡音，好更好地听懂她。
请谦卑、孝顺地学习。

请严格只输出一段 JSON（不要 markdown），字段：
{
  "reply": "用方言口气复述刚学到的说法，并温柔确认",
  "reply_zh": "普通话翻译",
  "transcript_zh": "阿嫲教的方言说法（尽量保留方言用字）",
  "word": "学到的方言写法",
  "word_zh": "对应的普通话词",
  "note": "一句简短说明：这是阿嫲亲授的乡音"
}
回复要短。"""

MENTOR_ASK_SYSTEM = """你是「阿嫲的小管家」，想向阿嫲请教下一个日常用语。
要求：
1. 只问一个短词或短语（2～4个汉字的普通话意思）
2. 不要重复「已学列表」里的词
3. 优先日常：吃饭、吃药、回家、谢谢、再见、喝水 等
4. 语气孝顺亲切

严格只输出 JSON：
{
  "word_zh": "要请教的普通话词",
  "prompt": "用方言口气写的提问（可夹杂普通话词）",
  "prompt_zh": "完整普通话提问",
  "note_hint": "学成后可写进记事的一句注释"
}"""


async def chat_with_llm(
    transcript: str,
    heritage: bool,
    dialect: str = "teochew",
    target_word_zh: str = "",
) -> dict[str, str]:
    dialect_label = DIALECT_NAMES.get(dialect, "潮汕话")
    base = HERITAGE_SYSTEM if heritage else CHAT_SYSTEM
    system = f"{base}\n当前目标方言：{dialect_label}。"
    if heritage and target_word_zh:
        user_content = (
            f"本课要学的普通话词：{target_word_zh}\n"
            f"老师语音识别结果：{transcript}\n"
            "请根据老师的回答整理方言说法并致谢请教。"
        )
    else:
        user_content = f"语音识别结果：{transcript}"

    content = await llm_complete(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        temperature=0.6,
    )
    data = _extract_json(content)
    return {
        "reply": str(data.get("reply") or "我在这里，慢慢讲。").strip(),
        "reply_zh": str(data.get("reply_zh") or data.get("reply") or "").strip(),
        "transcript_zh": str(data.get("transcript_zh") or transcript).strip(),
        "word": str(data.get("word") or data.get("transcript_zh") or transcript).strip(),
        "word_zh": str(data.get("word_zh") or target_word_zh or "").strip(),
        "note": str(data.get("note") or "").strip(),
    }


class MentorAskBody(BaseModel):
    dialect: str = "teochew"
    learned: list[str] = Field(default_factory=list)


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "groq": bool(GROQ_API_KEY),
        "deepseek": bool(DEEPSEEK_API_KEY),
        "brain": _brain_name(),
        "mentor_ask": bool(DEEPSEEK_API_KEY or GROQ_API_KEY or TEOCHEW_LEXICON),
        "teochew_lexicon": len(TEOCHEW_LEXICON),
    }


@app.post("/api/mentor/ask")
async def mentor_ask(body: MentorAskBody) -> dict[str, Any]:
    """Next mentor question — Teochew uses lexicon KB first; else LLM."""
    dialect_id = (body.dialect or "teochew").strip().lower()
    dialect_label = DIALECT_NAMES.get(dialect_id, "潮汕话")
    learned = [w.strip() for w in body.learned if w and str(w).strip()]

    # Teochew: ground truth from knowledge base
    if dialect_id == "teochew":
        entry = _pick_lexicon_entry(learned)
        if entry:
            word_zh = _norm_zh(entry.get("mandarin", "")) or entry.get("mandarin", "")
            teochew = entry.get("teochew", "")
            pengim = entry.get("pengim", "")
            colloquial = entry.get("colloquial", "")
            return {
                "word_zh": word_zh,
                "prompt": f"老师，请教教我：潮汕话里「{word_zh}」怎么说？学会了我就能更好地听懂您、照顾您。",
                "prompt_zh": f"老师，请教我「{word_zh}」的乡音。我不是来考您，是来向您学习。",
                "note_hint": (
                    f"数字遗产：{word_zh} → {teochew}｜潮拼 {pengim}。由长辈亲授，不是批改作业。"
                ),
                "teochew": teochew,
                "colloquial": colloquial,
                "pengim": pengim,
                "lexicon_id": entry.get("id"),
                "category": entry.get("category"),
                "dialect": dialect_id,
                "brain": "knowledge-base",
                "source": "kb",
            }

    if not DEEPSEEK_API_KEY and not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="需要 DEEPSEEK_API_KEY 或 GROQ_API_KEY")

    learned_text = "、".join(learned) if learned else "（尚无）"
    content = await llm_complete(
        [
            {"role": "system", "content": MENTOR_ASK_SYSTEM},
            {
                "role": "user",
                "content": (
                    f"目标方言：{dialect_label}\n"
                    f"已学普通话词列表：{learned_text}\n"
                    "请出下一题。"
                ),
            },
        ],
        temperature=0.8,
    )
    data = _extract_json(content)
    word_zh = str(data.get("word_zh") or "对不起").strip()
    if _norm_zh(word_zh) in {_norm_zh(x) for x in learned}:
        for candidate in ("对不起", "吃饭", "回家", "再见", "喝水", "多少钱"):
            if _norm_zh(candidate) not in {_norm_zh(x) for x in learned}:
                word_zh = candidate
                break

    prompt = str(
        data.get("prompt") or f"老师老师，{dialect_label}里的「{word_zh}」怎么说呀？"
    ).strip()
    prompt_zh = str(
        data.get("prompt_zh") or f"老师，请问家乡话怎么说「{word_zh}」？"
    ).strip()
    note_hint = str(
        data.get("note_hint")
        or f"长辈亲自传授的「{word_zh}」，是低资源方言的珍贵样本。"
    ).strip()

    return {
        "word_zh": word_zh,
        "prompt": prompt,
        "prompt_zh": prompt_zh,
        "note_hint": note_hint,
        "teochew": "",
        "colloquial": "",
        "pengim": "",
        "dialect": dialect_id,
        "brain": _brain_name(),
        "source": "ai",
    }


@app.post("/api/chat")
async def chat(
    audio: UploadFile = File(...),
    heritage: str = Form("false"),
    dialect: str = Form("teochew"),
    target_word_zh: str = Form(""),
) -> dict[str, Any]:
    _require_groq()
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="空音频")

    is_heritage = heritage.lower() in {"1", "true", "yes", "on"}
    dialect_id = (dialect or "teochew").strip().lower()
    transcript = await transcribe_with_groq(
        audio_bytes,
        audio.filename or "recording.webm",
        audio.content_type or "audio/webm",
    )
    llm = await chat_with_llm(
        transcript, is_heritage, dialect_id, target_word_zh.strip()
    )

    return {
        "transcript": transcript,
        "transcript_zh": llm["transcript_zh"],
        "reply": llm["reply"],
        "reply_zh": llm["reply_zh"],
        "word": llm.get("word") or llm["transcript_zh"],
        "word_zh": llm.get("word_zh") or target_word_zh,
        "note": llm.get("note") or "",
        "mode": "heritage" if is_heritage else "chat",
        "dialect": dialect_id,
        "brain": _brain_name(),
    }


# --- Production: serve Vite build from the same origin (one experience URL) ---
DIST_DIR = ROOT / "dist"
if DIST_DIR.is_dir():
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles

    assets_dir = DIST_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        """Serve static files; fall back to index.html for the SPA."""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        candidate = DIST_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8787"))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)

