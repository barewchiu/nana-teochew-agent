#!/usr/bin/env python3
"""
Evaluate ASR on data/asr/eval_holdout and measure intent accuracy.

Backends:
  groq         — current product ear (Whisper zh via Groq)
  http         — teochew-asr service at TEOCHEW_ASR_URL
  transformers — local HuggingFace Teochew Whisper
  gold         — use labeled text_teochew (upper bound for intent layer)

Examples:
  python teochew-asr/scripts/eval_holdout.py --backend groq
  python teochew-asr/scripts/eval_holdout.py --backend http
  python teochew-asr/scripts/eval_holdout.py --backend transformers
  python teochew-asr/scripts/eval_holdout.py --backend gold
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOLD = ROOT / "data" / "asr" / "eval_holdout"
NANA_BACKEND = ROOT / "nana-agent" / "backend"
REPORT_DIR = ROOT / "data" / "asr" / "eval_holdout" / "reports"

# Import product intent matcher
sys.path.insert(0, str(NANA_BACKEND))
from teochew_rag import (  # noqa: E402
    correct_mishear,
    match_followup,
    match_intent,
)


def load_env() -> None:
    env_path = ROOT / "nana-agent" / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def predict_intent(transcript: str) -> str:
    mis = correct_mishear(transcript)
    text = mis.get("corrected") or transcript
    if mis.get("intent"):
        return str(mis["intent"])
    hit = match_intent(text) or match_intent(transcript)
    if hit and hit.get("intent"):
        return str(hit["intent"])
    return ""


def asr_gold(row: dict[str, str]) -> tuple[str, float]:
    return (row.get("text_teochew") or "").strip(), 1.0


def asr_groq(audio_path: Path) -> tuple[str, float]:
    import httpx

    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise SystemExit("GROQ_API_KEY missing (nana-agent/.env)")
    model = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")
    prompt = (
        "潮汕话日常。哩食饱未？阿嫲爱食药未？今日想阿公了。"
        "谢谢你陪我。今日天气怎样？想听潮剧。身体有点不舒服。"
        "孙子有无返来？我想你。我喜欢你。"
    )
    with audio_path.open("rb") as f:
        files = {"file": (audio_path.name, f, "application/octet-stream")}
        data = {
            "model": model,
            "language": "zh",
            "response_format": "json",
            "prompt": prompt,
        }
        resp = httpx.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {key}"},
            files=files,
            data=data,
            timeout=120.0,
        )
    if resp.status_code >= 400:
        raise RuntimeError(f"Groq {resp.status_code}: {resp.text[:300]}")
    text = str(resp.json().get("text") or "").strip()
    return text, 0.5 if text else 0.0


def asr_http(audio_path: Path, base_url: str) -> tuple[str, float]:
    import httpx

    url = base_url.rstrip("/") + "/v1/transcribe"
    with audio_path.open("rb") as f:
        files = {"audio": (audio_path.name, f, "application/octet-stream")}
        resp = httpx.post(url, files=files, timeout=180.0)
    if resp.status_code >= 400:
        raise RuntimeError(f"ASR http {resp.status_code}: {resp.text[:300]}")
    payload = resp.json()
    return str(payload.get("text") or "").strip(), float(payload.get("confidence") or 0.0)


_pipe = None


def _load_audio_16k(audio_path: Path):
    """Load any ffmpeg-readable format to mono float32 @16k (m4a needs ffmpeg)."""
    import numpy as np

    try:
        import librosa

        wav, _sr = librosa.load(str(audio_path), sr=16000, mono=True)
        return np.asarray(wav, dtype=np.float32)
    except Exception:
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = Path(tmp.name)
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(audio_path),
                    "-ac",
                    "1",
                    "-ar",
                    "16000",
                    str(wav_path),
                ],
                check=True,
                capture_output=True,
            )
            import librosa

            wav, _sr = librosa.load(str(wav_path), sr=16000, mono=True)
            return np.asarray(wav, dtype=np.float32)
        finally:
            wav_path.unlink(missing_ok=True)


def asr_transformers(audio_path: Path, model_id: str) -> tuple[str, float]:
    global _pipe
    if _pipe is None:
        import torch
        from transformers import pipeline

        device = 0 if torch.cuda.is_available() else -1
        print(f"Loading {model_id} on device={device} …")
        _pipe = pipeline(
            "automatic-speech-recognition",
            model=model_id,
            device=device,
            torch_dtype=torch.float16 if device == 0 else torch.float32,
        )
    # Pass waveform so m4a/mp3 work (soundfile alone cannot decode m4a).
    # Do not pass language/task — panlr checkpoint has an outdated generation_config.
    wav = _load_audio_16k(audio_path)
    result = _pipe({"array": wav, "sampling_rate": 16000})
    text = str(result.get("text") if isinstance(result, dict) else result or "").strip()
    return text, 0.7 if text else 0.0


def main() -> int:
    load_env()
    parser = argparse.ArgumentParser(description="Eval holdout ASR → intent")
    parser.add_argument(
        "--backend",
        choices=["groq", "http", "transformers", "gold"],
        default="groq",
    )
    parser.add_argument(
        "--asr-url",
        default=os.getenv("TEOCHEW_ASR_URL", "http://127.0.0.1:8790"),
    )
    parser.add_argument(
        "--model",
        default=os.getenv("TEOCHEW_ASR_MODEL", "panlr/whisper-finetune-teochew"),
    )
    parser.add_argument("--limit", type=int, default=0, help="only first N rows")
    args = parser.parse_args()

    manifest = HOLD / "manifest.csv"
    if not manifest.exists():
        raise SystemExit(f"missing {manifest}")

    rows = list(csv.DictReader(manifest.open(encoding="utf-8-sig")))
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        raise SystemExit("holdout manifest empty")

    results = []
    t_all = time.perf_counter()
    for i, row in enumerate(rows, 1):
        audio = HOLD / row["audio_path"]
        gold_intent = (row.get("intent") or "").strip()
        gold_text = (row.get("text_teochew") or "").strip()
        t0 = time.perf_counter()
        try:
            if args.backend == "gold":
                hyp, conf = asr_gold(row)
            elif args.backend == "groq":
                hyp, conf = asr_groq(audio)
            elif args.backend == "http":
                hyp, conf = asr_http(audio, args.asr_url)
            else:
                hyp, conf = asr_transformers(audio, args.model)
            err = ""
        except Exception as exc:  # noqa: BLE001
            hyp, conf, err = "", 0.0, str(exc)
        pred = predict_intent(hyp) if hyp else ""
        ok = bool(pred) and pred == gold_intent
        latency = int((time.perf_counter() - t0) * 1000)
        results.append(
            {
                "id": row.get("id"),
                "speaker": row.get("speaker"),
                "gold_intent": gold_intent,
                "gold_text": gold_text,
                "asr_text": hyp,
                "pred_intent": pred,
                "intent_ok": ok,
                "confidence": conf,
                "latency_ms": latency,
                "error": err,
            }
        )
        mark = "OK" if ok else "NO"
        extra = f" ERR={err}" if err else ""
        print(
            f"[{i}/{len(rows)}] {mark} {row.get('id')}: "
            f"[{gold_intent}] <- {hyp!r} => {pred or '-'}{extra}"
        )

    n = len(results)
    n_ok = sum(1 for r in results if r["intent_ok"])
    n_empty = sum(1 for r in results if not r["asr_text"])
    acc = (n_ok / n) if n else 0.0
    summary = {
        "backend": args.backend,
        "model": args.model if args.backend == "transformers" else args.backend,
        "n": n,
        "intent_correct": n_ok,
        "intent_accuracy": round(acc, 4),
        "empty_asr": n_empty,
        "elapsed_sec": round(time.perf_counter() - t_all, 2),
    }
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_json = REPORT_DIR / f"holdout_{args.backend}_{stamp}.json"
    out_csv = REPORT_DIR / f"holdout_{args.backend}_{stamp}.csv"
    out_json.write_text(
        json.dumps({"summary": summary, "rows": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    print(f"wrote {out_json}")
    print(f"wrote {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
