# Hold-out 基线结果（2026-08-08 / 09）

锁定集：32 条（16 phrase × family1/family2）

| Backend | 意图准确率 | 说明 |
| --- | --- | --- |
| **gold**（标注文本→意图） | **100%** (32/32) | 意图层上限；已补 `头壳痛` / `食了` 等关键词 |
| **groq**（现网普通话 Whisper） | **40.6%** (13/32) | 潮语录音被听成乱码/普通话，基线偏低 |
| **transformers** `panlr/whisper-finetune-teochew`（AutoDL T4） | **50.0%** (16/32) | 空转写 0；family1 11/16、family2 5/16；仍低于 70% 目标 |

报告文件在本地：`data/asr/eval_holdout/reports/`（不进 git）  
最新 transformers：`holdout_transformers_20260809_004104.json`

## 结论

1. 产品意图层在金标文本上已通。  
2. 现网 Groq 耳对这批真潮语录音不够用 → 必须上潮语 ASR。  
3. 开源潮语 Whisper 零样本比 Groq **+9.4pt**，但离 **≥70%** 仍差一截；失败多为英文乱听 / 拼音（尤其 family2）。  
4. 下一步：用 L1 非 holdout 约 36 条在 GPU 上 LoRA 微调，再复测同一 holdout（见 [ASR_微调_L1.md](./ASR_微调_L1.md)）。

## 复现

见 [ASR_Holdout评测.md](./ASR_Holdout评测.md) 与 [ASR_AutoDL操作手册.md](./ASR_AutoDL操作手册.md)
