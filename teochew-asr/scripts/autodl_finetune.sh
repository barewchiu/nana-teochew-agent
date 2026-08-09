#!/usr/bin/env bash
# AutoDL: LoRA finetune on L1 train (~36) then holdout eval with merged ckpt.
# Usage:
#   cd /root/autodl-tmp
#   bash autodl_finetune.sh
#
# Expects (optional uploads under /root/autodl-tmp):
#   l1_train_audio.zip
#   holdout_audio.zip

set -euo pipefail

WORKDIR="${WORKDIR:-/root/autodl-tmp}"
REPO_DIR="${REPO_DIR:-$WORKDIR/nana-teochew-agent}"
REPO_URL="${REPO_URL:-https://github.com/barewchiu/nana-teochew-agent.git}"
BASE_MODEL="${BASE_MODEL:-panlr/whisper-finetune-teochew}"
TRAIN_ZIP="${TRAIN_ZIP:-$WORKDIR/l1_train_audio.zip}"
HOLDOUT_ZIP="${HOLDOUT_ZIP:-$WORKDIR/holdout_audio.zip}"
EPOCHS="${EPOCHS:-30}"

export PATH="/root/miniconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin${PATH:+:$PATH}"
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
export HF_HUB_ENABLE_HF_TRANSFER="${HF_HUB_ENABLE_HF_TRANSFER:-0}"

echo "== GPU =="
nvidia-smi || true
echo "HF_ENDPOINT=$HF_ENDPOINT"

mkdir -p "$WORKDIR"
cd "$WORKDIR"

if [[ ! -d "$REPO_DIR/.git" ]]; then
  echo "== clone repo =="
  git clone --depth 1 "$REPO_URL" "$REPO_DIR"
else
  echo "== update repo =="
  git -C "$REPO_DIR" pull --ff-only || true
fi

if [[ -x /root/miniconda3/bin/python ]]; then
  PY=/root/miniconda3/bin/python
elif command -v python >/dev/null 2>&1; then
  PY=python
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
    echo "ERROR: ffmpeg missing"; exit 1
  fi
fi

echo "== python deps =="
$PY -m pip install -q "transformers>=4.40" accelerate librosa soundfile peft datasets

L1_DIR="$REPO_DIR/data/asr/l1_commands"
HOLD_DIR="$REPO_DIR/data/asr/eval_holdout"
mkdir -p "$L1_DIR/audio" "$HOLD_DIR/audio" "$HOLD_DIR/reports"

if [[ -f "$TRAIN_ZIP" ]]; then
  echo "== unpack train zip =="
  rm -rf "$WORKDIR/_l1_train_unpack"
  unzip -o "$TRAIN_ZIP" -d "$WORKDIR/_l1_train_unpack" || {
    rc=$?; [[ "$rc" -gt 1 ]] && exit "$rc"; echo "(unzip warning ignored)"
  }
  if [[ -f "$WORKDIR/_l1_train_unpack/manifest.csv" ]]; then
    cp -f "$WORKDIR/_l1_train_unpack/manifest.csv" "$L1_DIR/manifest.csv"
  fi
  find "$WORKDIR/_l1_train_unpack" -type f \( -name '*.m4a' -o -name '*.mp3' -o -name '*.wav' \) \
    -exec cp -f {} "$L1_DIR/audio/" \;
fi

TRAIN_N=$(find "$L1_DIR/audio" -type f \( -name '*.m4a' -o -name '*.mp3' -o -name '*.wav' \) | wc -l)
echo "L1 audio files present: $TRAIN_N"
if [[ "$TRAIN_N" -lt 1 ]]; then
  echo "ERROR: upload l1_train_audio.zip to $TRAIN_ZIP first"
  exit 1
fi

if [[ -f "$HOLDOUT_ZIP" ]]; then
  echo "== unpack holdout zip =="
  rm -rf "$WORKDIR/_holdout_unpack"
  unzip -o "$HOLDOUT_ZIP" -d "$WORKDIR/_holdout_unpack" || {
    rc=$?; [[ "$rc" -gt 1 ]] && exit "$rc"; echo "(unzip warning ignored)"
  }
  find "$WORKDIR/_holdout_unpack" -type f \( -name '*.m4a' -o -name '*.mp3' -o -name '*.wav' \) \
    -exec cp -f {} "$HOLD_DIR/audio/" \;
  if [[ -f "$WORKDIR/_holdout_unpack/manifest.csv" ]]; then
    cp -f "$WORKDIR/_holdout_unpack/manifest.csv" "$HOLD_DIR/manifest.csv"
  fi
fi

CKPT="$REPO_DIR/teochew-asr/checkpoints/l1_lora"
MERGED="$CKPT/merged"

echo "== finetune (LoRA, epochs=$EPOCHS) =="
cd "$REPO_DIR"
$PY teochew-asr/scripts/finetune_whisper_l1.py \
  --base-model "$BASE_MODEL" \
  --manifest "$L1_DIR/manifest.csv" \
  --audio-root "$L1_DIR" \
  --output-dir "$CKPT" \
  --epochs "$EPOCHS"

if [[ ! -d "$MERGED" ]]; then
  echo "ERROR: merged checkpoint missing at $MERGED"
  exit 1
fi

echo "== holdout eval with merged ckpt =="
$PY teochew-asr/scripts/eval_holdout.py --backend transformers --model "$MERGED"

echo "== latest reports =="
ls -lt "$HOLD_DIR/reports" | head -n 8
echo "DONE. Compare intent_accuracy to baseline 0.50. Remember to shutdown AutoDL."
