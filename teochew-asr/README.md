# 潮语 ASR 微服务

给「阿嫲的小管家」提供 `/v1/transcribe`。主站通过 `TEOCHEW_ASR_URL` 调用；失败则回退 Groq。

## 快速启动（mock，无需 GPU）

```bash
cd teochew-asr
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8790
```

健康检查：http://127.0.0.1:8790/health

## 真模型（需 GPU / 大内存）

```bash
pip install torch transformers accelerate librosa soundfile
set TEOCHEW_ASR_MODE=transformers
set TEOCHEW_ASR_MODEL=panlr/whisper-finetune-teochew
uvicorn main:app --host 127.0.0.1 --port 8790
```

首次会从 HuggingFace 拉模型，请保证网络可用。

## 接到 nana-agent

在 `nana-agent/.env`：

```env
TEOCHEW_ASR_URL=http://127.0.0.1:8790
TEOCHEW_ASR_MIN_CONF=0.35
```

## 数据

录音与标注见仓库根目录 [`data/asr/`](../data/asr/)。
