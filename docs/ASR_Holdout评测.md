# Hold-out 评测（ASR → 意图）

锁定集：`data/asr/eval_holdout/`（32 条，勿用于训练）  
已跑基线数字见 [ASR_Holdout基线.md](./ASR_Holdout基线.md)。

## 一键评测

在仓库根目录：

```bash
# 1) 金标文本 → 意图（测知识库上限，应接近 100%）
python teochew-asr/scripts/eval_holdout.py --backend gold

# 2) 当前线上耳朵（Groq 普通话 Whisper）基线
python teochew-asr/scripts/eval_holdout.py --backend groq

# 3) 潮语 ASR 微服务（先启动 teochew-asr）
python teochew-asr/scripts/eval_holdout.py --backend http --asr-url http://127.0.0.1:8790

# 4) 本地潮语 Whisper（需安装 torch + transformers，建议 GPU）
pip install torch transformers accelerate librosa soundfile
python teochew-asr/scripts/eval_holdout.py --backend transformers --model panlr/whisper-finetune-teochew
```

报告输出：`data/asr/eval_holdout/reports/`（已 gitignore）

## 主站联调

```env
# nana-agent/.env
TEOCHEW_ASR_URL=http://127.0.0.1:8790
TEOCHEW_ASR_MIN_CONF=0.35
```

先起 ASR：

```bash
cd teochew-asr
uvicorn main:app --host 127.0.0.1 --port 8790
```

本机无 NVIDIA 时把 `TEOCHEW_ASR_MODE=transformers` 写入 `teochew-asr/.env`。
