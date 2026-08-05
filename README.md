# 奶奶的乡音管家

EazO 黑客松项目：**阿嫲的小管家（Nana Teochew Agent）**。  
从 Phase 1「乡音回响」平台 pivot 而来，聚焦服务一位只会潮汕话的奶奶。

## 仓库结构

```
奶奶的乡音管家/
├── nana-agent/                 # 可运行 Web App（当前产品）
├── docs/
│   ├── Pivot_To_Nana_Agent.md  # 转型指令
│   ├── Nana_Agent_实施指南.md  # 分步实施参考
│   └── archive/phase1/         # 旧 Echo of Roots 文档
└── data/                       # 潮汕语料源（词汇表 / 50句对话）
```

## 快速开始

```bash
cd nana-agent
npm install
npm run dev
```

初赛提交（体验链接、表单文案、ZIP）：见 [`docs/SUBMIT.md`](docs/SUBMIT.md)。

详见 [`nana-agent/README.md`](nana-agent/README.md)。
