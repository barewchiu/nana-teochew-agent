#!/usr/bin/env python3
"""Pack holdout audio + manifest with forward-slash zip paths (AutoDL-friendly)."""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOLD = ROOT / "data" / "asr" / "eval_holdout"
OUT = HOLD / "holdout_audio.zip"


def main() -> int:
    manifest = HOLD / "manifest.csv"
    audio_dir = HOLD / "audio"
    if not manifest.exists():
        raise SystemExit(f"missing {manifest}")
    files = sorted(
        p
        for p in audio_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".m4a", ".mp3", ".wav"}
    )
    if not files:
        raise SystemExit(f"no audio under {audio_dir}")

    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(manifest, "manifest.csv")
        for p in files:
            zf.write(p, f"audio/{p.name}")
    mb = OUT.stat().st_size / (1024 * 1024)
    print(f"Wrote {OUT} ({mb:.2f} MB, {len(files)} clips)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
