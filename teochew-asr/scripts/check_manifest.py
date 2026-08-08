#!/usr/bin/env python3
"""Validate an ASR manifest.csv against SCHEMA / audio files."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REQUIRED = [
    "id",
    "audio_path",
    "phrase_id",
    "text_teochew",
    "text_zh",
    "intent",
    "speaker",
    "take",
]

INTENTS = {
    "eat",
    "meds",
    "miss_family",
    "affection",
    "thanks",
    "weather",
    "opera",
    "health",
    "grandson",
}


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python check_manifest.py <path/to/manifest.csv>")
        return 2
    path = Path(sys.argv[1]).resolve()
    if not path.exists():
        print(f"Missing file: {path}")
        return 1
    base = path.parent
    errors = 0
    rows = 0
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("Empty CSV")
            return 1
        missing_cols = [c for c in REQUIRED if c not in reader.fieldnames]
        if missing_cols:
            print(f"Missing columns: {missing_cols}")
            return 1
        seen: set[str] = set()
        for i, row in enumerate(reader, start=2):
            if not any((v or "").strip() for v in row.values()):
                continue
            rows += 1
            rid = (row.get("id") or "").strip()
            if not rid:
                print(f"L{i}: empty id")
                errors += 1
            elif rid in seen:
                print(f"L{i}: duplicate id {rid}")
                errors += 1
            else:
                seen.add(rid)
            intent = (row.get("intent") or "").strip()
            if intent and intent not in INTENTS:
                print(f"L{i}: unknown intent {intent}")
                errors += 1
            for col in REQUIRED:
                if not (row.get(col) or "").strip():
                    print(f"L{i}: empty {col}")
                    errors += 1
            rel = (row.get("audio_path") or "").strip()
            if rel:
                audio = (base / rel).resolve()
                if not audio.exists():
                    print(f"L{i}: audio not found {rel}")
                    errors += 1
    print(f"Checked {rows} rows, {errors} issues → {path}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
