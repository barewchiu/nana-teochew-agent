"""
Lightweight Teochew chat grounding: intent rules + dialogue/lexicon fuzzy match.
Used to improve LIVE chat when Whisper mishears dialect speech.
"""

from __future__ import annotations

import re
from typing import Any


def norm_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[！!？?。，、,.~～\s\-_/\\（）()【】\[\]\"'“”‘’]", "", s)
    return s


# Whisper / Mandarin mishearings → intent id
INTENT_RULES: list[tuple[str, tuple[str, ...]]] = [
    (
        "eat",
        (
            "食饱",
            "食未",
            "食糜",
            "吃饭",
            "吃了吗",
            "吃过",
            "甲梅",
            "饿",
            "肚饿",
            "早饭",
            "午饭",
            "晚饭",
        ),
    ),
    (
        "meds",
        (
            "吃药",
            "食药",
            "服药",
            "药片",
            "高血压药",
            "忘记药",
            "药吞",
        ),
    ),
    (
        "miss_family",
        (
            "想阿公",
            "想爷爷",
            "想孙",
            "想你",
            "想伊",
            "孤单",
            "寂寞",
            "无人陪",
            "一个人",
        ),
    ),
    (
        "thanks",
        (
            "谢谢",
            "多谢",
            "感谢",
            "有心",
            "麻烦你",
        ),
    ),
    (
        "weather",
        (
            "天气",
            "天时",
            "落雨",
            "下雨",
            "热死",
            "好热",
            "好冷",
            "刮风",
        ),
    ),
    (
        "opera",
        (
            "潮剧",
            "听戏",
            "苏六娘",
            "告亲夫",
            "广播",
            "电台",
            "唱歌",
        ),
    ),
    (
        "health",
        (
            "身体",
            "身泰",
            "不舒服",
            "头痛",
            "头晕",
            "睡不好",
            "夗",
            "失眠",
        ),
    ),
    (
        "grandson",
        (
            "孙子",
            "孙仔",
            "回家",
            "返来",
            "周末",
            "礼拜",
            "留言",
        ),
    ),
]

# Grounded Teochew replies + voice-pack audio under /audio/replies/
INTENT_REPLIES: dict[str, dict[str, str]] = {
    "eat": {
        "reply": "食饱咯，阿嫲您呢？慢慢食，唔好急。",
        "reply_zh": "吃饱了，奶奶您呢？慢慢吃，别着急。",
        "audio": "/audio/replies/eat.m4a",
        "note": "乡音回复包：吃饭问候",
    },
    "meds": {
        "reply": "阿嫲，爱准时食药啰，记得多饮水。我陪您记着。",
        "reply_zh": "奶奶，要按时吃药，记得多喝水。我帮您记着。",
        "audio": "/audio/replies/meds.m4a",
        "note": "乡音回复包：吃药提醒",
    },
    "miss_family": {
        "reply": "阿公在天顶看着您，唔好哭，我陪您讲。",
        "reply_zh": "爷爷在天上看着您，别哭，我陪您说。",
        "audio": "/audio/replies/miss_family.m4a",
        "note": "乡音回复包：思念家人",
    },
    "thanks": {
        "reply": "阿嫲，我在这里，随时听您讲话。",
        "reply_zh": "奶奶，我在这里，随时听您说话。",
        "audio": "/audio/replies/thanks.m4a",
        "note": "乡音回复包：道谢陪伴",
    },
    "weather": {
        "reply": "今日天时看着还好，阿嫲出门爱加件衫，免着凉。",
        "reply_zh": "今天天气看着还好，奶奶出门要加件衣服，别着凉。",
        "audio": "/audio/replies/weather.m4a",
        "note": "乡音回复包：天气关心（若无文件则前端回退文字）",
    },
    "opera": {
        "reply": "好呀阿嫲，想听潮剧就按绿色钮，我帮您开戏。",
        "reply_zh": "好呀奶奶，想听潮剧就按绿色按钮，我帮您打开。",
        "audio": "/audio/replies/opera.m4a",
        "note": "乡音回复包：潮剧娱乐（若无文件则前端回退文字）",
    },
    "health": {
        "reply": "阿嫲身体有无要紧？慢慢讲，我听着。要紧就喊家里后生。",
        "reply_zh": "奶奶身体有没有事？慢慢说，我听着。要紧就叫家里年轻人。",
        "audio": "/audio/replies/health.m4a",
        "note": "乡音回复包：身体关怀（若无文件则前端回退文字）",
    },
    "grandson": {
        "reply": "孙仔惦记您啰。想听留言，就按蓝色钮「听孙子的信」。",
        "reply_zh": "孙子惦记您呢。想听留言，就按蓝色按钮「听孙子的信」。",
        "audio": "/audio/replies/grandson.m4a",
        "note": "乡音回复包：孙子/回家",
    },
}


def match_intent(transcript: str) -> dict[str, Any] | None:
    text = norm_text(transcript)
    if not text:
        return None
    best_id = None
    best_hits = 0
    for intent_id, keys in INTENT_RULES:
        hits = sum(1 for k in keys if norm_text(k) and norm_text(k) in text)
        # also allow partial: any key char-sequence length>=2 contained
        if hits > best_hits:
            best_hits = hits
            best_id = intent_id
    if not best_id or best_hits <= 0:
        # looser: single keyword hit already counted; try raw includes
        for intent_id, keys in INTENT_RULES:
            for k in keys:
                nk = norm_text(k)
                if len(nk) >= 2 and (nk in text or text in nk):
                    return {
                        "intent": intent_id,
                        "hits": 1,
                        **INTENT_REPLIES[intent_id],
                    }
        return None
    return {"intent": best_id, "hits": best_hits, **INTENT_REPLIES[best_id]}


def _token_set(s: str) -> set[str]:
    t = norm_text(s)
    if not t:
        return set()
    # bigrams + full string for short phrases
    grams = {t[i : i + 2] for i in range(max(0, len(t) - 1))}
    grams.add(t)
    return grams


def score_against_dialogue(query: str, dlg: dict[str, Any]) -> float:
    q = _token_set(query)
    if not q:
        return 0.0
    fields = [
        dlg.get("mandarin", ""),
        dlg.get("teochew", ""),
        dlg.get("colloquial", ""),
    ]
    best = 0.0
    for f in fields:
        fset = _token_set(str(f))
        if not fset:
            continue
        inter = len(q & fset)
        union = len(q | fset) or 1
        jacc = inter / union
        # bonus if mandarin/teochew fully contained
        nf = norm_text(str(f))
        nq = norm_text(query)
        if nf and (nf in nq or nq in nf):
            jacc += 0.35
        best = max(best, jacc)
    return best


def match_dialogue(
    transcript: str, dialogues: list[dict[str, Any]], min_score: float = 0.28
) -> dict[str, Any] | None:
    if not dialogues:
        return None
    scored: list[tuple[float, dict[str, Any]]] = []
    for dlg in dialogues:
        sc = score_against_dialogue(transcript, dlg)
        if sc >= min_score:
            scored.append((sc, dlg))
    if not scored:
        return None
    scored.sort(key=lambda x: x[0], reverse=True)
    sc, dlg = scored[0]
    # Pair reply: prefer next line in same scene if even index greeting-like
    reply_teochew = dlg.get("teochew") or ""
    reply_zh = dlg.get("mandarin") or ""
    # If user matched a question-like line, try following answer in list
    idx = dialogues.index(dlg) if dlg in dialogues else -1
    if idx >= 0 and idx + 1 < len(dialogues):
        nxt = dialogues[idx + 1]
        if nxt.get("scene") == dlg.get("scene"):
            # Use next as helper reply when current looks like user utterance
            reply_teochew = nxt.get("teochew") or reply_teochew
            reply_zh = nxt.get("mandarin") or reply_zh

    return {
        "intent": "dialogue",
        "score": round(sc, 3),
        "kb_id": dlg.get("id"),
        "reply": f"阿嫲，{reply_teochew}",
        "reply_zh": reply_zh,
        "matched_mandarin": dlg.get("mandarin"),
        "matched_teochew": dlg.get("teochew"),
        "audio": "",
        "note": f"对话知识库命中 {dlg.get('id')}（{dlg.get('scene', '')}）",
    }


def top_dialogue_hints(
    transcript: str, dialogues: list[dict[str, Any]], k: int = 4
) -> list[dict[str, str]]:
    ranked = sorted(
        ((score_against_dialogue(transcript, d), d) for d in dialogues),
        key=lambda x: x[0],
        reverse=True,
    )
    out = []
    for sc, d in ranked[:k]:
        if sc <= 0:
            continue
        out.append(
            {
                "id": str(d.get("id") or ""),
                "mandarin": str(d.get("mandarin") or ""),
                "teochew": str(d.get("teochew") or ""),
                "score": f"{sc:.2f}",
            }
        )
    return out


def lexicon_glossary(lexicon: list[dict[str, Any]], limit: int = 40) -> str:
    lines = []
    for e in lexicon[:limit]:
        m = e.get("mandarin") or ""
        t = e.get("teochew") or ""
        if m and t:
            lines.append(f"{m}→{t}")
    return "；".join(lines)
