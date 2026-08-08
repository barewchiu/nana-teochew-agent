"""
Teochew ASR microservice for 阿嫲的小管家.

Modes:
  - mock:         no GPU; returns empty / echo for pipeline tests
  - transformers: HuggingFace Whisper fine-tune (needs torch + model download)
"""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

ASR_MODE = os.getenv("TEOCHEW_ASR_MODE", "mock").strip().lower()
ASR_MODEL = os.getenv(
    "TEOCHEW_ASR_MODEL",
    "panlr/whisper-finetune-teochew",
).strip()
HOST_DEVICE = os.getenv("TEOCHEW_ASR_DEVICE", "").strip()  # cuda / cpu / empty=auto

app = FastAPI(title="Teochew ASR", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_pipe: Any = None
_load_error: str = ""


def _device() -> str:
    if HOST_DEVICE:
        return HOST_DEVICE
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def _ensure_transformers() -> None:
    global _pipe, _load_error
    if _pipe is not None:
        return
    if _load_error:
        raise HTTPException(status_code=503, detail=_load_error)
    try:
        import torch
        from transformers import pipeline

        device = 0 if _device() == "cuda" else -1
        _pipe = pipeline(
            "automatic-speech-recognition",
            model=ASR_MODEL,
            device=device,
            torch_dtype=torch.float16 if device == 0 else torch.float32,
        )
    except Exception as exc:  # noqa: BLE001
        _load_error = f"Failed to load ASR model {ASR_MODEL}: {exc}"
        raise HTTPException(status_code=503, detail=_load_error) from exc


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "mode": ASR_MODE,
        "model": ASR_MODEL if ASR_MODE == "transformers" else "",
        "device": _device() if ASR_MODE == "transformers" else "n/a",
        "loaded": _pipe is not None,
        "load_error": _load_error,
    }


@app.post("/v1/transcribe")
async def transcribe(audio: UploadFile = File(...)) -> dict[str, Any]:
    t0 = time.perf_counter()
    raw = await audio.read()
    if not raw:
        raise HTTPException(status_code=400, detail="empty audio")

    filename = audio.filename or "audio.webm"
    if ASR_MODE == "mock":
        # Pipeline smoke test: no real recognition
        return {
            "text": "",
            "text_zh_guess": "",
            "confidence": 0.0,
            "backend": "mock",
            "model": "",
            "latency_ms": int((time.perf_counter() - t0) * 1000),
            "note": "mock mode — set TEOCHEW_ASR_MODE=transformers and install GPU deps",
        }

    if ASR_MODE != "transformers":
        raise HTTPException(
            status_code=500,
            detail=f"Unknown TEOCHEW_ASR_MODE={ASR_MODE}",
        )

    _ensure_transformers()
    suffix = Path(filename).suffix or ".webm"
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name
        # transformers pipeline accepts file path
        result = _pipe(tmp_path)
        text = ""
        if isinstance(result, dict):
            text = str(result.get("text") or "").strip()
        else:
            text = str(result or "").strip()
        # Heuristic confidence: non-empty short utterance → mid-high
        conf = 0.0
        if text:
            conf = 0.75 if 1 <= len(text) <= 40 else 0.55
        return {
            "text": text,
            "text_zh_guess": "",
            "confidence": conf,
            "backend": "transformers",
            "model": ASR_MODEL,
            "latency_ms": int((time.perf_counter() - t0) * 1000),
            "note": "",
        }
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"ASR failed: {exc}") from exc
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

