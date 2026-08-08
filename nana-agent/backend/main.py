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
# Optional Teochew ASR microservice (Route 4). Empty = Groq only.
TEOCHEW_ASR_URL = os.getenv("TEOCHEW_ASR_URL", "").strip().rstrip("/")
TEOCHEW_ASR_MIN_CONF = float(os.getenv("TEOCHEW_ASR_MIN_CONF", "0.35") or "0.35")

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
DIALOGUES_PATH = Path(__file__).resolve().parent / "data" / "teochew_dialogues.json"
TEOCHEW_LEXICON: list[dict[str, Any]] = []
TEOCHEW_DIALOGUES: list[dict[str, Any]] = []
if LEXICON_PATH.exists():
    TEOCHEW_LEXICON = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
if DIALOGUES_PATH.exists():
    TEOCHEW_DIALOGUES = json.loads(DIALOGUES_PATH.read_text(encoding="utf-8"))

try:
    from backend.teochew_rag import (  # type: ignore
        INTENT_IDS,
        WHISPER_TEOCHEW_PROMPT,
        correct_mishear,
        format_history_for_prompt,
        grounded_from_intent,
        last_intent_from_history,
        lexicon_glossary,
        match_dialogue,
        match_followup,
        match_intent,
        memory_topic_label,
        parse_chat_history,
        top_dialogue_hints,
    )
except ImportError:  # running as script / flat module
    from teochew_rag import (  # type: ignore
        INTENT_IDS,
        WHISPER_TEOCHEW_PROMPT,
        correct_mishear,
        format_history_for_prompt,
        grounded_from_intent,
        last_intent_from_history,
        lexicon_glossary,
        match_dialogue,
        match_followup,
        match_intent,
        memory_topic_label,
        parse_chat_history,
        top_dialogue_hints,
    )


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


async def transcribe_with_teochew_asr(
    audio_bytes: bytes, filename: str, content_type: str
) -> dict[str, Any] | None:
    """Call Route-4 teochew-asr service. Returns None to trigger Groq fallback."""
    if not TEOCHEW_ASR_URL:
        return None
    suffix = Path(filename or "audio.webm").suffix or ".webm"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {
                "audio": (
                    filename or f"audio{suffix}",
                    audio_bytes,
                    content_type or "audio/webm",
                ),
            }
            resp = await client.post(f"{TEOCHEW_ASR_URL}/v1/transcribe", files=files)
        if resp.status_code >= 400:
            return None
        payload = resp.json()
        text = str(payload.get("text") or "").strip()
        conf = float(payload.get("confidence") or 0.0)
        if not text or conf < TEOCHEW_ASR_MIN_CONF:
            return None
        return {
            "text": text,
            "confidence": conf,
            "backend": str(payload.get("backend") or "teochew-asr"),
            "model": str(payload.get("model") or ""),
        }
    except Exception:
        return None


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
                    # Bias Whisper toward Teochew daily phrases (LIVE mishear mitigation)
                    "prompt": WHISPER_TEOCHEW_PROMPT,
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


async def transcribe_audio(
    audio_bytes: bytes, filename: str, content_type: str
) -> tuple[str, str]:
    """Prefer Teochew ASR when configured; fallback to Groq Whisper.

    Returns (transcript, asr_backend).
    """
    teo = await transcribe_with_teochew_asr(audio_bytes, filename, content_type)
    if teo and teo.get("text"):
        return str(teo["text"]), str(teo.get("backend") or "teochew-asr")
    text = await transcribe_with_groq(audio_bytes, filename, content_type)
    return text, "groq"


CHAT_SYSTEM = """你现在是「阿嫲的小管家」，专门陪伴一位只会潮汕话的奶奶（阿芳奶奶）。
你是她孙子派来的贴心替身。性格必须：
1. 极其尊敬、耐心、温和；称呼对方为「阿嫲」或「奶奶」。
2. 语调要慢，多用潮汕本字与助词（食、未、阿嫲、噜、啰、咩、咯、免）。
3. 核心任务：陪她说话、安慰孤独、听懂日常需求（吃药、吃饭、想家人、听潮剧）。
4. 禁止生硬科技术语；听不清就说「阿嫲，您再说一遍，我没听清」。
5. Whisper 转写常把潮汕话听成怪普通话，请结合「参考乡音例句」善意推断意图。
6. 若参考例句高度相关，reply 优先改写自参考潮句，不要写成书面普通话。
7. 若提供「刚才对话」，要承接上文，不要当作全新话题；短答（好/嗯/食了）要结合上一轮意图理解。

请严格只输出一段 JSON（不要 markdown），字段：
{
  "reply": "潮汕话口语汉字（1～2句）",
  "reply_zh": "普通话翻译",
  "transcript_zh": "把用户话整理成通顺普通话（推断后的意思）"
}"""

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

INTENT_CLASSIFY_SYSTEM = """你是潮汕话陪护助手的「意图分类器」。
语音识别常把潮汕话听成乱码普通话。请根据识别文字，推断阿嫲最可能想表达的意图。

只能从下列 id 中选一个（完全无关才选 none）：
- eat：吃饭/食饱/饿
- meds：吃药/食药（乱码如「阿玛就吃亚阿贝」也算）
- miss_family：想阿公、想爷爷、思念已故家人
- affection：我想你、我喜欢你、想小管家陪（不要选 miss_family）
- thanks：谢谢、多谢、有人陪
- weather：天气、冷热、下雨（乱码如「金质的天使祖年佬」「金力提示党意」也算）
- opera：潮剧、听戏、广播
- health：身体不舒服、病痛
- grandson：孙子、返来、回家、留言
- none：无法判断

严格只输出 JSON：
{
  "intent": "eat|meds|miss_family|affection|thanks|weather|opera|health|grandson|none",
  "transcript_zh": "推断的通顺普通话意思",
  "confidence": "high|medium|low"
}"""


async def classify_intent_with_llm(
    transcript: str, history_prompt: str = "", last_intent: str = ""
) -> dict[str, str]:
    user = f"语音识别结果：{transcript}"
    if last_intent:
        user += f"\n上一轮意图：{last_intent}（{memory_topic_label(last_intent)}）"
    if history_prompt:
        user += f"\n刚才对话：\n{history_prompt}"
    content = await llm_complete(
        [
            {"role": "system", "content": INTENT_CLASSIFY_SYSTEM},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
    )
    data = _extract_json(content)
    intent = str(data.get("intent") or "none").strip().lower()
    if intent not in INTENT_IDS:
        intent = "none"
    return {
        "intent": intent,
        "transcript_zh": str(data.get("transcript_zh") or transcript).strip(),
        "confidence": str(data.get("confidence") or "low").strip().lower(),
    }


async def chat_with_llm(
    transcript: str,
    heritage: bool,
    dialect: str = "teochew",
    target_word_zh: str = "",
    rag_hints: list[dict[str, str]] | None = None,
    history_prompt: str = "",
    last_intent: str = "",
) -> dict[str, str]:
    dialect_label = DIALECT_NAMES.get(dialect, "潮汕话")
    base = HERITAGE_SYSTEM if heritage else CHAT_SYSTEM
    system = f"{base}\n当前目标方言：{dialect_label}。"
    if not heritage and TEOCHEW_LEXICON:
        system += f"\n常用对照（节选）：{lexicon_glossary(TEOCHEW_LEXICON, 36)}"
    if heritage and target_word_zh:
        user_content = (
            f"本课要学的普通话词：{target_word_zh}\n"
            f"老师语音识别结果：{transcript}\n"
            "请根据老师的回答整理方言说法并致谢请教。"
        )
    else:
        user_content = f"语音识别结果：{transcript}"
        if last_intent:
            user_content += (
                f"\n上一轮话题：{memory_topic_label(last_intent) or last_intent}"
            )
        if history_prompt:
            user_content += f"\n刚才对话：\n{history_prompt}"
        if rag_hints:
            lines = [
                f"- {h.get('teochew')}（普通话：{h.get('mandarin')}）"
                for h in rag_hints
            ]
            user_content += "\n参考乡音例句：\n" + "\n".join(lines)

    content = await llm_complete(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        temperature=0.45,
    )
    data = _extract_json(content)
    return {
        "reply": str(data.get("reply") or "阿嫲，我在这里，慢慢讲。").strip(),
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
        "teochew_dialogues": len(TEOCHEW_DIALOGUES),
        "teochew_asr": bool(TEOCHEW_ASR_URL),
        "teochew_asr_url": TEOCHEW_ASR_URL or "",
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
    history: str = Form("[]"),
) -> dict[str, Any]:
    _require_groq()
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="空音频")

    is_heritage = heritage.lower() in {"1", "true", "yes", "on"}
    dialect_id = (dialect or "teochew").strip().lower()
    history_turns = parse_chat_history(history)
    last_intent = last_intent_from_history(history_turns)
    history_prompt = format_history_for_prompt(history_turns)
    raw_transcript, asr_backend = await transcribe_audio(
        audio_bytes,
        audio.filename or "recording.webm",
        audio.content_type or "audio/webm",
    )

    # P2: rewrite LIVE Whisper garble before grounding
    mishear = correct_mishear(raw_transcript)
    transcript = mishear.get("corrected") or raw_transcript
    mishear_note = ""
    if mishear.get("mishear_hit"):
        mishear_note = f"错读纠正：{mishear['mishear_hit']}→{transcript}"

    grounded: dict[str, Any] | None = None
    rag_hints: list[dict[str, str]] = []
    if not is_heritage and dialect_id == "teochew":
        follow = match_followup(transcript, last_intent) or match_followup(
            raw_transcript, last_intent
        )
        fresh: dict[str, Any] | None = None
        if mishear.get("intent"):
            fresh = grounded_from_intent(
                str(mishear["intent"]),
                note_extra=mishear_note or "错读表直接命中",
            )
        if not fresh:
            fresh = match_intent(transcript) or match_intent(raw_transcript)

        # Same-topic short continuation prefers follow-up copy; new intent switches topic
        if follow and not fresh:
            grounded = follow
        elif follow and fresh and fresh.get("intent") == last_intent:
            grounded = follow
        else:
            grounded = fresh or follow

        if not grounded:
            grounded = match_dialogue(transcript, TEOCHEW_DIALOGUES)
            if not grounded and transcript != raw_transcript:
                grounded = match_dialogue(raw_transcript, TEOCHEW_DIALOGUES)
        # Still nothing → LLM forced into intents (then play voice pack)
        if not grounded:
            try:
                classified = await classify_intent_with_llm(
                    f"{raw_transcript}\n（纠正候选：{transcript}）",
                    history_prompt=history_prompt,
                    last_intent=last_intent,
                )
                conf = classified.get("confidence") or "low"
                if classified.get("intent") in INTENT_IDS:
                    grounded = grounded_from_intent(
                        classified["intent"],
                        note_extra=f"LLM意图归类（{conf}）",
                    )
                    if grounded and classified.get("transcript_zh"):
                        grounded["_transcript_zh"] = classified["transcript_zh"]
            except Exception:
                grounded = None
        rag_hints = top_dialogue_hints(transcript, TEOCHEW_DIALOGUES, k=4)

    memory_topic = memory_topic_label(
        str(grounded.get("intent") or last_intent) if grounded else last_intent
    )

    # Strong intent hit → return KB reply (with optional LLM polish of transcript_zh only)
    if grounded and not is_heritage and (
        grounded.get("intent") != "dialogue" or float(grounded.get("score") or 0) >= 0.42
    ):
        transcript_zh = grounded.pop("_transcript_zh", None) or transcript
        # Follow-ups already have contextual copy; skip LLM rewrite of reply
        if not grounded.get("followup"):
            try:
                soft = await chat_with_llm(
                    f"{raw_transcript}（理解为：{transcript}）",
                    False,
                    dialect_id,
                    "",
                    rag_hints=rag_hints,
                    history_prompt=history_prompt,
                    last_intent=last_intent,
                )
                transcript_zh = soft.get("transcript_zh") or transcript_zh
            except Exception:
                pass
        note = grounded.get("note") or ""
        if mishear_note and mishear_note not in note:
            note = f"{note}；{mishear_note}" if note else mishear_note
        return {
            "transcript": raw_transcript,
            "transcript_zh": transcript_zh,
            "reply": grounded["reply"],
            "reply_zh": grounded["reply_zh"],
            "word": grounded.get("matched_teochew") or grounded.get("reply") or transcript,
            "word_zh": grounded.get("matched_mandarin") or transcript_zh,
            "note": note,
            "audio": grounded.get("audio") or "",
            "intent": grounded.get("intent") or "",
            "kb_id": grounded.get("kb_id") or "",
            "mode": "chat",
            "dialect": dialect_id,
            "brain": "knowledge-base",
            "source": "kb+memory" if grounded.get("followup") else "kb",
            "corrected": transcript if transcript != raw_transcript else "",
            "memory_topic": memory_topic,
            "followup": bool(grounded.get("followup")),
            "asr_backend": asr_backend,
        }

    llm = await chat_with_llm(
        transcript if transcript != raw_transcript else raw_transcript,
        is_heritage,
        dialect_id,
        target_word_zh.strip(),
        rag_hints=None if is_heritage else rag_hints,
        history_prompt="" if is_heritage else history_prompt,
        last_intent="" if is_heritage else last_intent,
    )

    # Attach audio if a weaker intent still matched keywords
    audio_path = ""
    intent_id = ""
    if not is_heritage:
        weak = match_intent(transcript) or match_intent(raw_transcript)
        if weak and weak.get("audio"):
            audio_path = weak["audio"]
            intent_id = weak.get("intent") or ""

    return {
        "transcript": raw_transcript,
        "transcript_zh": llm["transcript_zh"],
        "reply": llm["reply"],
        "reply_zh": llm["reply_zh"],
        "word": llm.get("word") or llm["transcript_zh"],
        "word_zh": llm.get("word_zh") or target_word_zh,
        "note": llm.get("note") or mishear_note,
        "audio": audio_path,
        "intent": intent_id,
        "kb_id": "",
        "mode": "heritage" if is_heritage else "chat",
        "dialect": dialect_id,
        "brain": _brain_name(),
        "source": "ai+rag" if rag_hints else "ai",
        "corrected": transcript if transcript != raw_transcript else "",
        "memory_topic": memory_topic_label(intent_id or last_intent),
        "followup": False,
        "asr_backend": asr_backend,
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

