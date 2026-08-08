# AutoDL 全自动评测（T4）

本机无 GPU 时，用仓库脚本一键跑 hold-out。

实测零样本基线（2026-08-09）：`panlr/whisper-finetune-teochew` → **意图准确率 50%**（16/32），高于 Groq 40.6%。详见 [ASR_Holdout基线.md](./ASR_Holdout基线.md)。

## 你需要上传的只有一个 zip

本机生成（在仓库根目录）：

```powershell
python teochew-asr/scripts/pack_holdout_for_autodl.py
# 或: powershell -File teochew-asr/scripts/pack_holdout_for_autodl.ps1
```

产物：`data/asr/eval_holdout/holdout_audio.zip`（含 32 条录音 + manifest；正斜杠路径，避免 unzip 告警）

## AutoDL 上操作（约 3 步）

1. JupyterLab → 上传到 `/root/autodl-tmp/`：
   - `holdout_audio.zip`
   - （可选）`autodl_bootstrap.sh`；也可直接从 GitHub clone 后用仓库内脚本
2. 终端执行：

```bash
cd /root/autodl-tmp
git clone --depth 1 https://github.com/barewchiu/nana-teochew-agent.git
cp nana-teochew-agent/teochew-asr/scripts/autodl_bootstrap.sh .
bash autodl_bootstrap.sh
```

若 zip 已放在 `/root/autodl-tmp/holdout_audio.zip`，脚本会自动解压并评测。

3. 看终端 `intent_accuracy`，然后控制台 **关机**。

## 本机 SSH 一键代跑

```powershell
$env:AUTODL_SSH_HOST="region-9.autodl.pro"   # 以实例页为准
$env:AUTODL_SSH_PORT="21779"                 # 以实例页为准
$env:AUTODL_SSH_PASSWORD="****"
$env:PYTHONIOENCODING="utf-8"
python teochew-asr/scripts/run_autodl_eval.py
```

依赖：本机 `pip install paramiko`；远端自动装 `ffmpeg`、走 `HF_ENDPOINT=https://hf-mirror.com`。

## 踩坑备忘

| 问题 | 处理 |
| --- | --- |
| Windows zip 解压警告导致脚本退出 | bootstrap 容忍 `unzip` exit code 1 |
| `huggingface.co` Errno 99 | 设 `HF_ENDPOINT=https://hf-mirror.com`，勿开 network_turbo |
| m4a 读失败 | `eval_holdout.py` 用 librosa/ffmpeg 转 16k waveform |
| 无 `python3` | 用 `/root/miniconda3/bin/python` |
| 按量计费 | 评测完立刻 **关机** |

## 下一步

L1 非 holdout 约 36 条微调同一模型，目标 holdout 意图准确率 **≥70%**。
