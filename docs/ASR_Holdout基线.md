# Hold-out 基线结果（2026-08-08）

锁定集：32 条（16 phrase × family1/family2）

| Backend | 意图准确率 | 说明 |
| --- | --- | --- |
| **gold**（标注文本→意图） | **100%** (32/32) | 意图层上限；已补 `头壳痛` / `食了` 等关键词 |
| **groq**（现网普通话 Whisper） | **40.6%** (13/32) | 潮语录音被听成乱码/普通话，基线偏低 |

报告文件在本地：`data/asr/eval_holdout/reports/`（不进 git）

## 结论

1. 产品意图层在金标文本上已通。  
2. 现网 Groq 耳对这批真潮语录音不够用 → 必须上潮语 ASR。  
3. 下一步：在有 GPU / 云主机上跑  

```bash
pip install torch transformers accelerate librosa soundfile
python teochew-asr/scripts/eval_holdout.py --backend transformers --model panlr/whisper-finetune-teochew
```

对比 groq 的 40.6%，目标先冲 **≥70%** 意图准确，再微调。

## 复现

见 [ASR_Holdout评测.md](./ASR_Holdout评测.md)
