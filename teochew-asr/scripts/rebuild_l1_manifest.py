#!/usr/bin/env python3
"""Rebuild l1_commands/manifest.csv from audio/ + phrases.csv."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
L1 = ROOT / "data" / "asr" / "l1_commands"
PHRASES = L1 / "phrases.csv"
MANIFEST = L1 / "manifest.csv"
AUDIO = L1 / "audio"

PAT = re.compile(
    r"^(?P<phrase>.+)_(?P<speaker>[^_]+)_(?P<take>\d+)\.(?P<ext>m4a|mp3|wav)$",
    re.I,
)


def main() -> int:
    phrases = {
        r["id"]: r
        for r in csv.DictReader(PHRASES.open(encoding="utf-8-sig"))
    }
    rows: list[dict[str, str]] = []
    for f in sorted(AUDIO.iterdir()):
        if not f.is_file() or f.name.startswith("."):
            continue
        m = PAT.match(f.name)
        if not m:
            print(f"skip unrecognized: {f.name}")
            continue
        pid = m.group("phrase")
        if pid not in phrases:
            print(f"unknown phrase_id: {pid} ({f.name})")
            continue
        speaker = m.group("speaker")
        take = m.group("take")
        ext = m.group("ext").lower()
        pr = phrases[pid]
        rows.append(
            {
                "id": f"{pid}_{speaker}_{take}",
                "audio_path": f"audio/{f.name}",
                "phrase_id": pid,
                "text_teochew": pr["text_teochew"],
                "text_zh": pr["text_zh"],
                "intent": pr["intent"],
                "speaker": speaker,
                "accent": "",
                "take": take,
                "noise": "quiet",
                "duration_sec": "",
                "split": "train",
                "notes": f"format={ext}",
            }
        )

    fields = [
        "id",
        "audio_path",
        "phrase_id",
        "text_teochew",
        "text_zh",
        "intent",
        "speaker",
        "accent",
        "take",
        "noise",
        "duration_sec",
        "split",
        "notes",
    ]
    with MANIFEST.open("w", encoding="utf-8", newline="") as out:
        w = csv.DictWriter(out, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {len(rows)} rows -> {MANIFEST}")
    print("by speaker:", dict(Counter(r["speaker"] for r in rows)))
    missing = []
    for pid in phrases:
        for sp in ("family1", "family2"):
            if not any(r["phrase_id"] == pid and r["speaker"] == sp for r in rows):
                missing.append(f"{pid}/{sp}")
    print(f"missing speaker pairs: {len(missing)}")
    for x in missing:
        print(" ", x)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
