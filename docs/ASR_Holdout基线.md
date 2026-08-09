# Hold-out 基线结果（2026-08-08 / 09）

锁定集：32 条（16 phrase × family1/family2）

| Backend | 意图准确率 | 说明 |
| --- | --- | --- |
| **gold**（标注文本→意图） | **100%** (32/32) | 意图层上限；已补 `头壳痛` / `食了` 等关键词 |
| **groq**（现网普通话 Whisper） | **40.6%** (13/32) | 潮语录音被听成乱码/普通话，基线偏低 |
| **transformers** `panlr/whisper-finetune-teochew`（AutoDL T4） | **50.0%** (16/32) | 零样本；family1 11/16、family2 5/16 |
| **transformers + L1 LoRA**（train=36，merged） | **84.4%** (27/32) | 空转写 0；已超 70% 目标；失败：health_02×2、opera_01×2、grandson_02→miss_family |

报告文件在本地：`data/asr/eval_holdout/reports/`（不进 git）  
最新微调复测：`holdout_transformers_20260809_110641.json`  
远端权重：`teochew-asr/checkpoints/l1_lora/merged`（在 AutoDL 盘，未进 git）

## 结论

1. 产品意图层在金标文本上已通。  
2. 现网 Groq 耳对这批真潮语录音不够用 → 必须上潮语 ASR。  
3. 开源潮语 Whisper 零样本 50% → **L1 LoRA 后 84.4%**（+34pt），闸门 ≥70% 已过。  
4. 下一步：导出/部署 merged 到 `TEOCHEW_ASR_URL`（或云 GPU 推理）；补 `头壳痛`/`潮剧` 训练句；交卷演示仍以快捷钮兜底。

## 复现

见 [ASR_Holdout评测.md](./ASR_Holdout评测.md) 与 [ASR_AutoDL操作手册.md](./ASR_AutoDL操作手册.md)
