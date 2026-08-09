#!/usr/bin/env python3
"""Pack L1 train-split audio + manifest (forward-slash zip) for AutoDL finetune."""

from __future__ import annotations

import csv
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
L1 = ROOT / "data" / "asr" / "l1_commands"
OUT = L1 / "l1_train_audio.zip"


def main() -> int:
    manifest = L1 / "manifest.csv"
    if not manifest.exists():
        raise SystemExit(f"missing {manifest}")
    rows = [
        r
        for r in csv.DictReader(manifest.open(encoding="utf-8-sig"))
        if (r.get("split") or "").strip() == "train"
    ]
    if not rows:
        raise SystemExit("no train rows")

    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # full manifest so remote can filter split=train and verify holdout unused
        zf.write(manifest, "manifest.csv")
        for r in rows:
            src = L1 / r["audio_path"]
            if not src.exists():
                raise SystemExit(f"missing {src}")
            zf.write(src, r["audio_path"].replace("\\", "/"))
    mb = OUT.stat().st_size / (1024 * 1024)
    print(f"Wrote {OUT} ({mb:.2f} MB, {len(rows)} train clips)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
