# 阿嫲的小管家 · Nana Teochew Agent

面向阿芳奶奶的个人潮汕话 AI Agent（Eazo · Personal Agent 赛道）。  
首页三键：**听孙子的信** · **跟管家讲话** · **听潮剧/广播**。

## 本地开发

```bash
# 前端
cd nana-agent
npm install
npm run dev
# → http://localhost:5173/
```

```bash
# 后端 LIVE（另开终端）
cd nana-agent
# Windows 示例：
backend\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8787
```

复制 `.env.example` → `.env`，填入 `GROQ_API_KEY`（可选 `DEEPSEEK_API_KEY`）。  
Vite 已将 `/api` 代理到 `8787`。

## 一体预览（模拟线上）

```bash
npm run build
backend\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8787
# → http://127.0.0.1:8787/
```

## 公网部署

见 [`../docs/SUBMIT.md`](../docs/SUBMIT.md)（Render Docker 一键 URL）。

简要：用仓库内 `Dockerfile` / `render.yaml`，环境变量配置 `GROQ_API_KEY`。

## 初赛打包

```bash
npm run pack:submit
# → ../submit/nana-teochew-agent_submit_*.zip
```

## 目录

| 路径 | 说明 |
| --- | --- |
| `src/App.jsx` | 三键主界面 |
| `src/lib/voiceEchoMapping.js` | 孙子留言 → 潮汕录音 |
| `src/lib/operaStations.js` | 潮剧卡片 |
| `src/lib/api.js` | LIVE API 基址 |
| `public/audio/` | 预录音频 |
| `backend/main.py` | Whisper + LLM + 静态托管 |
| `Dockerfile` | 生产一体镜像 |
| `_archive/phase1/` | 旧平台模块（不参与运行） |
