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
export PATH="/root/miniconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin${PATH:+:$PATH}"
if [[ -x /root/miniconda3/bin/python ]]; then
  PY=/root/miniconda3/bin/python
elif command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "ERROR: python not found"; exit 1
fi
echo "using $PY ($($PY -V))"
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "== install ffmpeg =="
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg
  elif command -v conda >/dev/null 2>&1; then
    conda install -y -c conda-forge ffmpeg
  else
    echo "ERROR: ffmpeg missing and no apt-get/conda"; exit 1
  fi
fi
command -v ffmpeg
$PY -m pip install -q "transformers>=4.40" accelerate librosa soundfile

HOLDOUT_DIR="$REPO_DIR/data/asr/eval_holdout"
mkdir -p "$HOLDOUT_DIR/audio" "$HOLDOUT_DIR/reports"

if [[ -f "$HOLDOUT_ZIP" ]]; then
  echo "== unpack holdout audio from $HOLDOUT_ZIP =="
  # Windows Compress-Archive zips often warn about backslashes; unzip exits 1 on warning.
  unzip -o "$HOLDOUT_ZIP" -d "$WORKDIR/_holdout_unpack" || {
    rc=$?
    if [[ "$rc" -gt 1 ]]; then
      echo "ERROR: unzip failed with code $rc"
      exit "$rc"
    fi
    echo "(unzip warning ignored, code=$rc)"
  }
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
# AutoDL often cannot reach huggingface.co; prefer China mirror.
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
export HF_HUB_ENABLE_HF_TRANSFER="${HF_HUB_ENABLE_HF_TRANSFER:-0}"
echo "HF_ENDPOINT=$HF_ENDPOINT"
$PY teochew-asr/scripts/eval_holdout.py --backend transformers --model "$MODEL"

echo "== latest report =="
ls -lt "$HOLDOUT_DIR/reports" | head -n 5
echo "DONE. Remember to shutdown the AutoDL instance."
