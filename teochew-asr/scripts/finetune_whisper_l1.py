#!/usr/bin/env python3
"""
Fine-tune Teochew Whisper on L1 train split only (never holdout).

Base: panlr/whisper-finetune-teochew (LoRA)
Train rows: data/asr/l1_commands/manifest.csv where split=train (~36)

Example (GPU):
  export HF_ENDPOINT=https://hf-mirror.com
  python teochew-asr/scripts/finetune_whisper_l1.py
  python teochew-asr/scripts/eval_holdout.py --backend transformers \\
      --model teochew-asr/checkpoints/l1_lora_merged
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
L1_DIR = ROOT / "data" / "asr" / "l1_commands"
DEFAULT_OUT = ROOT / "teochew-asr" / "checkpoints" / "l1_lora"


def load_audio_16k(path: Path) -> np.ndarray:
    import librosa

    try:
        y, _ = librosa.load(str(path), sr=16000, mono=True)
        return np.asarray(y, dtype=np.float32)
    except Exception:
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav = Path(tmp.name)
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(path), "-ac", "1", "-ar", "16000", str(wav)],
                check=True,
                capture_output=True,
            )
            y, _ = librosa.load(str(wav), sr=16000, mono=True)
            return np.asarray(y, dtype=np.float32)
        finally:
            wav.unlink(missing_ok=True)


def load_train_rows(manifest: Path) -> list[dict[str, str]]:
    rows = list(csv.DictReader(manifest.open(encoding="utf-8-sig")))
    train = [r for r in rows if (r.get("split") or "").strip() == "train"]
    if not train:
        raise SystemExit(f"no train rows in {manifest}")
    hold = sum(1 for r in rows if (r.get("split") or "").strip() == "holdout")
    print(f"manifest rows={len(rows)} train={len(train)} holdout={hold} (holdout unused)")
    return train


@dataclass
class Sample:
    path: Path
    text: str


class L1TrainDataset:
    def __init__(self, samples: list[Sample], processor):
        self.samples = samples
        self.processor = processor

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict:
        s = self.samples[idx]
        audio = load_audio_16k(s.path)
        feats = self.processor.feature_extractor(
            audio, sampling_rate=16000, return_tensors="pt"
        ).input_features[0]
        labels = self.processor.tokenizer(
            s.text, return_tensors="pt"
        ).input_ids[0]
        return {"input_features": feats, "labels": labels}


@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: object

    def __call__(self, features: list[dict]) -> dict:
        import torch

        input_features = [{"input_features": f["input_features"]} for f in features]
        label_features = [{"input_ids": f["labels"]} for f in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
        labels = labels_batch["input_ids"].masked_fill(
            labels_batch.attention_mask.ne(1), -100
        )
        if (labels[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            labels = labels[:, 1:]
        batch["labels"] = labels
        return batch


def merge_and_save(model, processor, out_merged: Path) -> None:
    out_merged.mkdir(parents=True, exist_ok=True)
    print(f"merging LoRA → {out_merged}")
    merged = model.merge_and_unload()
    merged.save_pretrained(out_merged)
    processor.save_pretrained(out_merged)
    # Keep generation config usable for pipeline (avoid forced language kwargs).
    print("saved merged checkpoint")


def main() -> int:
    parser = argparse.ArgumentParser(description="LoRA finetune Whisper on L1 train")
    parser.add_argument(
        "--base-model",
        default=os.getenv("TEOCHEW_ASR_MODEL", "panlr/whisper-finetune-teochew"),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=L1_DIR / "manifest.csv",
    )
    parser.add_argument("--audio-root", type=Path, default=L1_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--epochs", type=float, default=30.0)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--grad-accum", type=int, default=2)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--skip-merge",
        action="store_true",
        help="only save LoRA adapter, do not merge full weights",
    )
    args = parser.parse_args()

    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")

    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import (
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
        WhisperForConditionalGeneration,
        WhisperProcessor,
        set_seed,
    )

    set_seed(args.seed)
    train_rows = load_train_rows(args.manifest)
    samples: list[Sample] = []
    for r in train_rows:
        path = args.audio_root / r["audio_path"]
        if not path.exists():
            raise SystemExit(f"missing audio: {path}")
        text = (r.get("text_teochew") or "").strip()
        if not text:
            raise SystemExit(f"empty text for {r.get('id')}")
        samples.append(Sample(path=path, text=text))
    print(f"training clips: {len(samples)}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"base={args.base_model} device={device} HF_ENDPOINT={os.getenv('HF_ENDPOINT')}")

    processor = WhisperProcessor.from_pretrained(args.base_model)
    # Prefer Chinese token ids when available; panlr gen_config may be outdated.
    try:
        processor.tokenizer.set_prefix_tokens(language="zh", task="transcribe")
    except Exception as exc:  # noqa: BLE001
        print(f"(prefix tokens skipped: {exc})")

    model = WhisperForConditionalGeneration.from_pretrained(
        args.base_model,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    model.config.forced_decoder_ids = None
    model.config.suppress_tokens = []
    model.config.use_cache = False

    lora = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_r * 2,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    dataset = L1TrainDataset(samples, processor)
    collator = DataCollatorSpeechSeq2SeqWithPadding(processor=processor)

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    # ~36 clips; step-based logging keeps console useful on AutoDL.
    steps_per_epoch = max(1, len(dataset) // max(1, args.batch_size * args.grad_accum))
    logging_steps = max(1, steps_per_epoch)

    targs = Seq2SeqTrainingArguments(
        output_dir=str(out / "runs"),
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        fp16=device == "cuda",
        logging_steps=logging_steps,
        save_strategy="epoch",
        save_total_limit=2,
        remove_unused_columns=False,
        label_names=["labels"],
        report_to=[],
        seed=args.seed,
        dataloader_num_workers=0,
        predict_with_generate=False,
    )

    trainer_kwargs = dict(
        args=targs,
        model=model,
        train_dataset=dataset,
        data_collator=collator,
    )
    try:
        trainer = Seq2SeqTrainer(
            **trainer_kwargs,
            processing_class=processor.feature_extractor,
        )
    except TypeError:
        trainer = Seq2SeqTrainer(
            **trainer_kwargs,
            tokenizer=processor.feature_extractor,
        )
    trainer.train()

    adapter_dir = out / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(adapter_dir)
    processor.save_pretrained(adapter_dir)
    print(f"saved LoRA adapter → {adapter_dir}")

    if not args.skip_merge:
        merge_and_save(model, processor, out / "merged")

    meta = {
        "base_model": args.base_model,
        "n_train": len(samples),
        "epochs": args.epochs,
        "lr": args.lr,
        "lora_r": args.lora_r,
        "adapter": str(adapter_dir),
        "merged": str(out / "merged") if not args.skip_merge else None,
    }
    (out / "train_meta.json").write_text(
        __import__("json").dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("DONE", meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
