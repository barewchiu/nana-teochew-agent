# 初赛提交指南 · 上海赛区

> 提交入口：https://open.hirebox.cn/submit/competition?competition=young-plus-2026&region=shanghai  
> 截止：**2026-08-10 22:00**（提交后锁定，每组仅一份）

---

## 1. 表单填写草稿

| 字段 | 建议内容 |
| --- | --- |
| Agent 名称 | 阿嫲的小管家 |
| 团队名称 / 队长信息 | （填写真实信息） |
| Agent 简介 | 见下方 |
| 使用方式 | 见下方 |
| 落地体验地址 | 部署后的 `https://…`（见第 2 节） |
| 后端 MCP | 可不填 |
| 头像 | PNG/JPG/WEBP，&lt;2MB |
| 源码 ZIP | 运行打包脚本生成（见第 3 节） |

### Agent 简介（可粘贴）

「阿嫲的小管家」是为只会潮汕话的阿芳奶奶打造的 Personal Agent。孙子用普通话留言，Agent 用乡音念给她听；她用潮汕话跟小管家聊天，获得陪伴与日常提醒；一键收听潮剧。核心不是教老人学 App，而是让数字世界听懂奶奶——用大模型理解意图，用流程编排连接「留言桥 / 陪伴对话 / 吃药提醒 / 潮剧娱乐」。

### 使用方式（可粘贴）

1. 打开体验链接，首页三键：听孙子的信 / 跟管家讲话 / 听潮剧。  
2. 点「听孙子的信」选留言，播放潮汕录音。  
3. 点「跟管家讲话」：演示模式可直接试；打开「真人听懂 LIVE」后按麦克风说话，后端 Whisper+LLM 听懂并回复。  
4. 打开时会弹出吃药提醒，可点「听提醒」。  
5. 「听潮剧」点卡片即可。适老超大按钮，建议手机访问。

---

## 2. 公网体验链接（P0）

推荐 **一个 URL**：Docker 部署，前端静态资源 + FastAPI 同源。

### 方案 A：Render（推荐）

1. 将 `nana-agent` 推到 GitHub（不要提交 `.env`）。  
2. [Render](https://render.com) → New → Blueprint，选含 `render.yaml` 的仓库；或 New Web Service → Docker，根目录设为 `nana-agent`。  
3. Environment 填入：
   - `GROQ_API_KEY`（必填，LIVE 语音）
   - `DEEPSEEK_API_KEY`（可选）
4. Deploy 完成后，把服务 URL 填进「落地体验地址」。  
5. 自测：打开链接 → 跟管家讲话 → 打开 LIVE → 说话，应有回复。

### 方案 B：本机先验证一体服务

```bash
cd nana-agent
npm install && npm run build
# 需已配置 .env
backend\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8787
```

浏览器打开 `http://127.0.0.1:8787/`（此时由后端托管 `dist`）。

### 评委演示路径（建议写进路演稿）

吃药提醒 → 听孙子的信 → 跟管家讲话（LIVE）→ 听潮剧。

---

## 3. 源码 ZIP

```bash
cd nana-agent
npm run pack:submit
```

产物在仓库根目录 `submit/nana-teochew-agent_submit_*.zip`。  
已排除：`node_modules`、`.venv`、`dist`、`.env`。体积约数 MB（限制 50MB）。

ZIP 内含：`README.md`、`nana-agent/`、`docs/`、`data/`。

---

## 4. 提交前检查清单

- [ ] 体验链接公网可开（非 localhost）  
- [ ] DEMO 三键可点、有声音  
- [ ] LIVE 模式能返回 AI 回复（需 Key）  
- [ ] ZIP &lt; 50MB 且无密钥  
- [ ] 头像已备  
- [ ] 勾选原创承诺后提交  

---

## 5. 技术说明（给静态测评）

- 前端：React + Vite + Tailwind（适老三键 UI）  
- 后端：FastAPI；Ear=Groq Whisper；Brain=DeepSeek 或 Groq Llama  
- Agent 流程：录音 → ASR → 人设 System Prompt → JSON 回复 → 界面播放  
- 孙子留言：普通话文本映射预录潮汕音频（Voice Echo）  
