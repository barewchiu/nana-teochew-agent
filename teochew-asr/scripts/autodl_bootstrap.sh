#!/usr/bin/env bash
# AutoDL one-shot: install deps + run Teochew Whisper holdout eval.
# Usage on AutoDL:
#   cd /root/autodl-tmp
#   bash autodl_bootstrap.sh
# Optional env:
#   REPO_DIR=/root/autodl-tmp/nana-teochew-agent
#   MODEL=panlr/whisper-finetune-teochew
#   HOLDOUT_ZIP=/root/autodl-tmp/holdout_audio.zip

set -euo pipefail

WORKDIR="${WORKDIR:-/root/autodl-tmp}"
REPO_DIR="${REPO_DIR:-$WORKDIR/nana-teochew-agent}"
REPO_URL="${REPO_URL:-https://github.com/barewchiu/nana-teochew-agent.git}"
MODEL="${MODEL:-panlr/whisper-finetune-teochew}"
HOLDOUT_ZIP="${HOLDOUT_ZIP:-$WORKDIR/holdout_audio.zip}"

echo "== GPU =="
nvidia-smi || true

mkdir -p "$WORKDIR"
cd "$WORKDIR"

if [[ ! -d "$REPO_DIR/.git" ]]; then
  echo "== clone repo =="
  git clone --depth 1 "$REPO_URL" "$REPO_DIR"
else
  echo "== update repo =="
  git -C "$REPO_DIR" pull --ff-only || true
fi

echo "== python deps =="
pip install -U pip
pip install -U "transformers>=4.40" accelerate librosa soundfile

HOLDOUT_DIR="$REPO_DIR/data/asr/eval_holdout"
mkdir -p "$HOLDOUT_DIR/audio" "$HOLDOUT_DIR/reports"

if [[ -f "$HOLDOUT_ZIP" ]]; then
  echo "== unpack holdout audio from $HOLDOUT_ZIP =="
  unzip -o "$HOLDOUT_ZIP" -d "$WORKDIR/_holdout_unpack"
  # accept either audio/*.m4a at root or nested paths
  find "$WORKDIR/_holdout_unpack" -type f \( -name '*.m4a' -o -name '*.mp3' -o -name '*.wav' \) -exec cp -f {} "$HOLDOUT_DIR/audio/" \;
  if [[ -f "$WORKDIR/_holdout_unpack/manifest.csv" ]]; then
    cp -f "$WORKDIR/_holdout_unpack/manifest.csv" "$HOLDOUT_DIR/manifest.csv"
  fi
  # also support zip that contains audio/ + manifest.csv
  if [[ -f "$WORKDIR/_holdout_unpack/eval_holdout/manifest.csv" ]]; then
    cp -f "$WORKDIR/_holdout_unpack/eval_holdout/manifest.csv" "$HOLDOUT_DIR/manifest.csv"
  fi
  if [[ -d "$WORKDIR/_holdout_unpack/eval_holdout/audio" ]]; then
    cp -f "$WORKDIR/_holdout_unpack/eval_holdout/audio/"* "$HOLDOUT_DIR/audio/" 2>/dev/null || true
  fi
fi

AUDIO_N=$(find "$HOLDOUT_DIR/audio" -type f \( -name '*.m4a' -o -name '*.mp3' -o -name '*.wav' \) | wc -l)
echo "holdout audio files: $AUDIO_N"
if [[ "$AUDIO_N" -lt 1 ]]; then
  echo "ERROR: no holdout audio. Upload holdout_audio.zip to $HOLDOUT_ZIP first."
  exit 1
fi

echo "== run eval =="
cd "$REPO_DIR"
python teochew-asr/scripts/eval_holdout.py --backend transformers --model "$MODEL"

echo "== latest report =="
ls -lt "$HOLDOUT_DIR/reports" | head -n 5
echo "DONE. Remember to shutdown the AutoDL instance."
