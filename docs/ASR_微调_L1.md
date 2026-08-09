# L1 微调（冲 holdout ≥70%）

零样本潮语 Whisper holdout 意图准确率 **50%**。用 L1 **train=36**（永不碰 holdout=32）做 LoRA 微调后再测。

## 本机打包

```powershell
python teochew-asr/scripts/pack_l1_train_for_autodl.py
python teochew-asr/scripts/pack_holdout_for_autodl.py
```

产物：
- `data/asr/l1_commands/l1_train_audio.zip`
- `data/asr/eval_holdout/holdout_audio.zip`

## AutoDL（推荐 Cursor 代跑）

1. 开机同一类 GPU（T4 即可）
2. 把 SSH（含端口）和密码发给 Agent，或本机执行：

```powershell
$env:AUTODL_SSH_HOST="…"
$env:AUTODL_SSH_PORT="…"
$env:AUTODL_SSH_PASSWORD="…"
$env:PYTHONIOENCODING="utf-8"
python teochew-asr/scripts/run_autodl_finetune.py
```

3. 看终端 `intent_accuracy`；目标 **≥0.70**  
4. **关机**

## 手工终端

```bash
cd /root/autodl-tmp
# 上传两个 zip + 可选 scripts
git clone --depth 1 https://github.com/barewchiu/nana-teochew-agent.git
bash nana-teochew-agent/teochew-asr/scripts/autodl_finetune.sh
```

合并权重路径：`teochew-asr/checkpoints/l1_lora/merged`  
复测：

```bash
python teochew-asr/scripts/eval_holdout.py --backend transformers \
  --model teochew-asr/checkpoints/l1_lora/merged
```

## 说明

- 数据极少，LoRA + 约 30 epoch，可能过拟合；以 **holdout 意图准确率** 为唯一闸门  
- 基线对照见 [ASR_Holdout基线.md](./ASR_Holdout基线.md)
