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
| 落地体验地址 | **https://nana-teochew-agent.onrender.com** |
| 后端 MCP | 可不填 |
| 头像 | `submit/nana-agent-avatar.png` |
| 源码 ZIP | 运行打包脚本生成（见第 3 节） |

### Agent 简介（可粘贴）

「阿嫲的小管家」是为只会潮汕话的阿芳奶奶打造的 Personal Agent。孙子用普通话留言，Agent 用乡音念给她听；她用潮汕话跟小管家聊天，获得陪伴与日常提醒；一键收听潮剧与澄海电台。核心不是教老人学 App，而是让数字世界听懂奶奶——用大模型 + 乡音知识库理解意图，用流程编排连接「留言桥 / 陪伴对话 / 吃药提醒 / 潮剧娱乐」。

### 使用方式（可粘贴）

1. 打开 https://nana-teochew-agent.onrender.com （免费实例首次打开可能需等待约 1 分钟唤醒）。  
2. 首页三键：听孙子的信 / 跟管家讲话 / 听潮剧。  
3. 「听孙子的信」：点留言卡片，播放潮汕录音。  
4. 「跟管家讲话」：演示模式可直接试；打开「真人听懂 LIVE」后按麦克风说话（Whisper + 知识库/LLM）。  
5. 打开时会弹出吃药提醒，可点「听提醒」。  
6. 「听潮剧」：苏六娘/告亲夫可选段播放；潮语广播可本页收听澄海 FM100.5。  

### 评委 1 分钟演示路径

吃药提醒 → 听孙子的信 → 跟管家讲话（LIVE，说「食饱未」）→ 听潮剧选段 / 潮语广播。

---

## 2. 公网体验链接

**当前线上地址：** https://nana-teochew-agent.onrender.com  

Render 免费实例闲置会休眠；评测时若首开较慢属正常。

本地一体预览：

```bash
cd nana-agent
npm install && npm run build
backend\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8787
```

---

## 3. 源码 ZIP

```bash
cd nana-agent
npm run pack:submit
```

产物：仓库根目录 `submit/nana-teochew-agent_submit_*.zip`（小于 50MB）。  
已排除：`node_modules`、`.venv`、`dist`、`.env`。

---

## 4. 提交前检查清单

- [x] 体验链接公网可开  
- [ ] DEMO 三键可点、有声音  
- [ ] LIVE 模式能返回 AI/知识库回复（Key 已配置）  
- [ ] ZIP 已重新打包且无密钥  
- [ ] 头像已备（`submit/nana-agent-avatar.png`）  
- [ ] 勾选原创承诺后提交  

---

## 5. 技术说明（给静态测评）

- 前端：React + Vite + Tailwind（适老三键 UI）  
- 后端：FastAPI；Ear=Groq Whisper；Brain=DeepSeek 或 Groq Llama  
- Agent 流程：录音 → ASR → 意图/对话知识库 或 LLM → 界面播放（含预录乡音）  
- 孙子留言：普通话文本映射预录潮汕音频（Voice Echo）  
- 潮语广播：本页播放澄海电台直播流（蜻蜓直链）+ Radio Garden 备用  
