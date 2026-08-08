#!/usr/bin/env python3
"""Carve a locked eval_holdout set from L1 commands (~30 clips)."""

from __future__ import annotations

import csv
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
L1 = ROOT / "data" / "asr" / "l1_commands"
HOLD = ROOT / "data" / "asr" / "eval_holdout"
AUDIO_DST = HOLD / "audio"

# Both speakers for these phrase_ids → ~30 rows
HOLD_PHRASE_IDS = [
    "eat_01",
    "eat_02",
    "meds_01",
    "meds_05",
    "miss_01",
    "miss_02",
    "aff_01",
    "aff_02",
    "thanks_01",
    "weather_01",
    "weather_03",
    "opera_01",
    "health_01",
    "health_02",
    "grandson_01",
    "grandson_02",
]


def main() -> int:
    AUDIO_DST.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader((L1 / "manifest.csv").open(encoding="utf-8-sig")))
    if not rows:
        raise SystemExit("L1 manifest empty")

    hold_set = set(HOLD_PHRASE_IDS)
    hold_rows = [r for r in rows if r["phrase_id"] in hold_set]
    hold_ids = {r["id"] for r in hold_rows}

    for r in hold_rows:
        src = L1 / r["audio_path"]
        if not src.exists():
            raise SystemExit(f"missing audio: {src}")
        dst = AUDIO_DST / Path(r["audio_path"]).name
        shutil.copy2(src, dst)

    fields = list(rows[0].keys())

    with (HOLD / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in sorted(hold_rows, key=lambda x: x["id"]):
            rr = dict(r)
            rr["split"] = "holdout"
            rr["audio_path"] = f"audio/{Path(r['audio_path']).name}"
            note = (rr.get("notes") or "").strip()
            rr["notes"] = (note + "; locked holdout never train").strip("; ")
            w.writerow(rr)

    with (L1 / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            rr = dict(r)
            rr["split"] = "holdout" if rr["id"] in hold_ids else "train"
            w.writerow(rr)

    print(f"holdout rows: {len(hold_rows)}")
    print("by intent:", dict(Counter(r["intent"] for r in hold_rows)))
    print("by speaker:", dict(Counter(r["speaker"] for r in hold_rows)))
    print("phrase_ids:", HOLD_PHRASE_IDS)
    print(f"train left: {sum(1 for r in rows if r['id'] not in hold_ids)}")
    print(f"copied audio -> {AUDIO_DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
