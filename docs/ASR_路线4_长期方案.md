# 路线 4 · 潮语 ASR 长期方案

目标：自建数据 + 微调，让 LIVE「耳朵」从普通话 Whisper 升级为潮语识别。  
产品层（意图库 / 乡音包 / P3 / P4）尽量复用，只替换转写第一环。

## 成功标准

| 阶段 | 指标 | 门槛 |
| --- | --- | --- |
| M1 | 核心指令意图准确率 | ≥ 90% |
| M2 | 高频句 CER / 意图 | CER ≤ 25%，意图 ≥ 85% |
| M3 | 阿嫲 hold-out 意图 | ≥ 90% |
| M4 | 转写延迟 | ≤ 2～3s |

原则：**先意图，后字准**；公开模型冷启动，**阿嫲数据定胜负**。

## 架构

```
麦克风 → teochew-asr 服务 → 文本规范 → teochew_rag 意图 → 乡音回复
                ↓ 失败/低置信
           Groq Whisper（回退）
```

| 组件 | 路径 |
| --- | --- |
| ASR 服务骨架 | [`teochew-asr/`](../teochew-asr/) |
| 训练/标注数据 | [`data/asr/`](../data/asr/) |
| 第 0～2 周看板 | [ASR_第0-2周看板.md](./ASR_第0-2周看板.md) |
| 主站联调开关 | `nana-agent` 环境变量 `TEOCHEW_ASR_URL` |

## 数据分层

| 层 | 目录 | 说明 |
| --- | --- | --- |
| L1 指令 | `data/asr/l1_commands/` | 产品 9 意图短句，先录这个 |
| L2 阿嫲 | `data/asr/l2_nana/` | 家人口音域适应 |
| Hold-out | `data/asr/eval_holdout/` | **永不训练**，专测 |
| 公开底模 | HuggingFace Teochew-Wild 等 | 微调冷启动 |

口播清单见 `data/asr/l1_commands/phrases.csv`。  
录音填入 `manifest.csv`（模板已给）。

## 模型路线（摘要）

1. **零样本评测**：`panlr/whisper-finetune-teochew` 或 `efficient-nlp/teochew-whisper-medium`  
2. **指令微调**：L1 +（可选）公开数据  
3. **阿嫲域适应**：L2 小学习率续训  
4. **可选**：音频→意图多任务；潮语 TTS 另线推进  

## 主站如何打开潮语耳

1. 启动 ASR 服务（见 `teochew-asr/README.md`）  
2. 在 `nana-agent/.env` 设置：

```env
TEOCHEW_ASR_URL=http://127.0.0.1:8790
TEOCHEW_ASR_MIN_CONF=0.35
```

3. 重启后端；`/api/health` 会出现 `teochew_asr: true`  
4. 未配置或 ASR 失败时，自动回退 Groq Whisper（现有行为）

## 近期只做这些

见 [ASR_第0-2周看板.md](./ASR_第0-2周看板.md)：定规范 → 按 `phrases.csv` 录音 → 填 manifest → 起 ASR 服务做联调。
