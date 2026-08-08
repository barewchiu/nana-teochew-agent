# 潮语 ASR · 第 0～2 周看板

对照 [`ASR_路线4_长期方案.md`](./ASR_路线4_长期方案.md)。做完一项就勾一项。

## 第 0 周 · 基建（本周立刻做）

- [ ] 读完长期方案与 `data/asr/README.md`
- [ ] 定录音设备：手机即可；尽量安静；靠近嘴
- [ ] 打开 `data/asr/l1_commands/phrases.csv`，按行用潮汕话录
- [ ] 每句至少：**2 人 × 2 遍**（起步）；理想 3×3
- [ ] 文件命名：`{phrase_id}_{speaker}_{take}.m4a`  
  例：`eat_01_bafang_1.m4a`
- [ ] 音频放进 `data/asr/l1_commands/audio/`
- [ ] 每录一条，在 `data/asr/l1_commands/manifest.csv` 加一行
- [x] 从 L1 里**抽出 32 条**拷到 `eval_holdout/`（16 phrase × 2 说话人；之后禁止拿去训练）
- [ ] 本地启动 `teochew-asr`（可先 mock 模式跑通接口）
- [ ] `nana-agent/.env` 配置 `TEOCHEW_ASR_URL` 做联调

## 第 1 周 · 凑齐 L1

- [ ] L1 有效条数 ≥ **400**（或至少覆盖 phrases 全表 × 2 说话人）
- [ ] manifest 无空 `text_teochew` / `intent`
- [x] 用 `python teochew-asr/scripts/check_manifest.py` 检查
- [x] Hold-out 评测脚本已接通；groq 基线 40.6%，gold 100%
- [ ] 选定基座模型，在 GPU 上跑 `eval_holdout.py --backend transformers`

## 第 2 周 · 第一次微调准备

- [ ] 租/备 GPU（或确认本机显卡）
- [ ] 导出训练清单（manifest 过滤 hold-out）
- [ ] 跑通官方/社区 Whisper 微调脚本（夜雨飘零或 transformers）
- [ ] 产出 `checkpoint/`，用 teochew-asr `TRANSFORMERS` 模式加载
- [ ] 对比：Groq vs 潮语 ASR 在 hold-out 上的意图准确率

## 录音口播（高频优先）

先录这些 intent：`eat` `meds` `miss_family` `weather` `opera` `health` `grandson` `affection` `thanks`  

完整句子表：`data/asr/l1_commands/phrases.csv`
