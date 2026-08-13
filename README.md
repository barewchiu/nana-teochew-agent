# 奶奶的乡音管家

EazO 黑客松项目：**阿嫲的小管家（Nana Teochew Agent）**。  
从 Phase 1「乡音回响」平台 pivot 而来，聚焦服务一位只会潮汕话的奶奶。

## 仓库结构

```
奶奶的乡音管家/
├── nana-agent/                 # 可运行 Web App（当前产品）
├── teochew-asr/                # 潮语 ASR 微服务（路线 4）
├── docs/                       # 方案与提交文档
└── data/
    ├── …                       # 潮汕语料源（词汇表 / 对话）
    └── asr/                    # 潮语 ASR 录音与标注（L1/L2/hold-out）
```

潮语识别长期方案：[`docs/ASR_路线4_长期方案.md`](docs/ASR_路线4_长期方案.md) · 本周看板：[`docs/ASR_第0-2周看板.md`](docs/ASR_第0-2周看板.md)  
**从零到一复盘（推荐新会话先读）：** [`docs/制作复盘_从零到一.md`](docs/制作复盘_从零到一.md)  
**总统杯英文提案映射：** [`docs/总统杯_资产映射与英文提案大纲.md`](docs/总统杯_资产映射与英文提案大纲.md)

## 快速开始

```bash
cd nana-agent
npm install
npm run dev
```

初赛提交（体验链接、表单文案、ZIP）：见 [`docs/SUBMIT.md`](docs/SUBMIT.md)。

详见 [`nana-agent/README.md`](nana-agent/README.md)。
