# Echo of Roots（乡音回响）—— Phase 1 开发总结

> 文档用途：记录总统盃黑客松报名阶段已完成的产品定位、功能、技术架构与开发过程。  
> 阶段状态：**报名成功 · 第一阶段开发完成**  
> 整理日期：2026-08-01

---

## 1. 项目一句话

**乡音回响（Echo of Roots）** 是面向东南亚潮汕话 / 闽南语长者的方言驱动 AI 陪伴产品。  
核心不是「教老人学方言」，而是 **请长辈当文化导师，教 AI 听懂乡音**，实现 AI 时代的数字包容。

---

## 2. 主题与价值主张

| 维度 | 内容 |
| --- | --- |
| 赛事主题 | Digital Inclusion in the AI Era（银发数字包容） |
| 目标用户 | 潮汕话、闽南语（含新加坡福建话）长者及家庭 |
| 核心概念 | Role Reversal：长者 = Cultural Mentor，而非被动学科技的人 |
| 三大价值 | **赋权**（教 AI）· **安全**（方言反诈）· **连接**（数字族谱留给后辈） |

### 要解决的痛点

1. **语言壁垒**：主流 AI 听不懂方言，长者被「数字静音」。  
2. **心理壁垒**：学 App 带来无能感与抵触。  
3. **文化流失**：口述历史与乡音随世代消失。

---

## 3. Phase 1 交付物总览

### 3.1 产品形态

- Web 原型（Vite + React + Tailwind），适老化单页交互  
- 路径：`echo-of-roots/`  
- 本地预览：前端 `http://localhost:5173/`，后端（可选）`http://127.0.0.1:8787`

### 3.2 已完成能力清单

| 模块 | 说明 |
| --- | --- |
| 适老 UI | 大麦克风、高对比、大字体、实时麦音波形 |
| DEMO / LIVE 双模式 | DEMO 稳拍 Pitch；LIVE 接真 ASR+LLM |
| 让 AI 听懂您（导师模式） | 谦卑请教 → 长辈录音教学 → 服务承诺 + 数字遗产 |
| 乡音知识库 | 67 词词汇表 + 50 句日常对话（本字/音译/潮拼） |
| 数字族谱 | localStorage 存词条 + **亲授录音**，可回放 |
| 录音库回复 | 回复优先播放族谱原声（基础乡音互动） |
| 多方言切换占位 | 潮汕话 / 福建话 / 粤语 |
| 数字保镖（反诈） | 可疑短信扫描 + 大红警告 + 乡音警告音 |
| 数字化包容文案校准 | 弱化「学习机」观感，强化助手/遗产/服务 |

---

## 4. 技术架构（Phase 1）

```
浏览器 (React)
  ├─ DEMO：剧本 + 预录 m4a + 用户亲授录音回放
  └─ LIVE：录音 Blob → FastAPI
                ├─ Ear：Groq Whisper（ASR）
                ├─ Brain：DeepSeek（若配置）/ Groq Llama
                └─ 导师出题：潮汕优先走本地知识库
```

### 4.1 前端

- React + Vite + Tailwind CSS + lucide-react  
- 主文件：`src/App.jsx`  
- 关键库：  
  - `src/lib/teochewKb.js`（知识库）  
  - `src/lib/dialectBook.js`（数字族谱 + 录音存储）  
  - `src/lib/voiceBank.js`（回复音频解析）  
  - `src/lib/serviceReward.js`（教完服务承诺）  
  - `src/lib/antiFraud.js`（反诈规则原型）  
- 数据：`src/data/teochew_lexicon.json`、`teochew_dialogues.json`

### 4.2 后端

- Python FastAPI：`backend/main.py`  
- 接口：  
  - `GET /api/health`  
  - `POST /api/chat`（上传音频 → 转写 + 对话）  
  - `POST /api/mentor/ask`（下一题；潮汕优先知识库）  
- 密钥：本地 `.env`（`GROQ_API_KEY`、可选 `DEEPSEEK_API_KEY`），已 gitignore  

### 4.3 已知技术边界（诚实记录）

- 通用 Whisper **听不准潮汕话**（普通话/粤语较好）→ Pitch 用 DEMO 乡音 + LIVE 证管道。  
- 潮拼（如 `ziah8 mue5 buê7`）**不能**被通用 TTS 念成正宗潮汕话。  
- 乡音回复现阶段靠 **预录 / 亲授录音库回放**，不是方言 TTS 合成。

---

## 5. 开发过程回顾（时间线）

### 阶段 A：项目 Brief 与冷启动

- 阅读《Project Brief Echo of Roots》  
- 明确 Phase 1：单页原型、大麦克风、Mock 方言交互、Heritage/导师模式  

### 阶段 B：适老界面 MVP

- 初始化 Vite React + Tailwind + lucide-react  
- 实现大按钮、状态机（idle → listening → thinking → responding）  
- 接入预录潮汕语音频（如「食饱咯，你呢？」）  

### 阶段 C：Demo 可信度升级

- 真麦克风 `MediaRecorder` + 录音计时  
- Web Audio **实时波形**  
- 自动播放回复、双语字幕、对话气泡  
- 三轮 DEMO 剧本 + 导师完整小流程  

### 阶段 D：迈向半真 MVP（LIVE）

- 因暂无 OpenAI Key，改用 **Groq Whisper**  
- FastAPI 桥接 ASR + LLM；前端 DEMO/LIVE 开关  
- 实测：普通话/粤语可识别；潮汕话弱 → 确立 Pitch 策略  

### 阶段 E：产品延展（评审叙事）

参考 AI Studio 路线并校准优先级：  

1. 乡音记事本 / 数字族谱（文化沉淀）  
2. 多方言切换占位（国际扩展）  
3. 反诈乡音原型（公共安全加分）  
4. **不硬磕**专用潮汕 ASR  

### 阶段 F：导师连续出题 + 知识库

- DEMO：固定/知识库词表连课  
- LIVE：AI 出题（潮汕优先 KB）  
- 导入两份语料 MD → JSON 知识库（67 词 + 50 句）  
- 卡片展示本字、普通话、潮拼对照  

### 阶段 G：航向校准（数字化包容）

发现问题：界面一度像「潮汕话学习机」。  

校准动作：  

- 文案改为谦卑助手：「让 AI 听懂您」  
- 教完先给 **服务承诺**，弱化「下一课」  
- 记事本升级为 **数字族谱 / 寄语后辈 / 数字遗产**  
- 安全入口命名为 **数字保镖**  

### 阶段 H：亲授录音库

- 教学时保存 MediaRecorder 音频到族谱（localStorage）  
- 回复优先播放老师原声  
- 形成「录音越多 → 基础乡音互动越丰富」的可演示闭环  

### 阶段 I：报名视频与收官

- 完成录屏脚本与中英口播稿  
- **报名成功**  
- 宣告 Phase 1 完成  

---

## 6. 产品主路径（当前正确叙事）

```
陪聊（主） → 让 AI 听懂您（教） → 服务承诺 + 数字遗产
                ↓
            数字族谱（原声）
                ↓
            数字保镖（反诈）
```

Pitch 金句：  

> 我们不是教老人说潮汕话；我们请老人教 AI，好让只会乡音的长辈也能被数字世界听见、被保护、被后辈听见。

---

## 7. 关键文件索引

| 路径 | 说明 |
| --- | --- |
| `Project Brief Echo of Roots (乡音回响).md` | 原始 Brief |
| `aistudio向MVP制作方案.md` | 进阶模块建议 |
| `潮汕话常用词汇表（普通话对照+汉字音译）.md` | 词汇语料 |
| `50句潮汕长者日常完整对话…专用数据集.md` | 对话语料 |
| `echo-of-roots/` | 可运行 Web 原型 |
| `echo-of-roots/.env.example` | 环境变量模板（勿提交真 Key） |
| `Phase1_开发总结_Echo_of_Roots.md` | 本文档 |

---

## 8. 本地运行（备忘）

```bash
# 前端
cd echo-of-roots
npm install
npm run dev

# 后端（LIVE 需要）
cd echo-of-roots
backend\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8787
```

前端已将 `/api` 代理到 `8787`。

---

## 9. Phase 2 可延续方向（未做 / 可选）

1. 亲授录音云端持久化（替代 localStorage 限额）  
2. 按知识库批量预录标准音色包  
3. 轻量 RAG：50 句对话增强陪伴回复  
4. 新加坡队友福建话语料与出镜素材  
5. 反诈警告改真潮汕录音  
6. 专用方言 ASR / TTS（中长期科研向）  

---

## 10. 阶段结论

Phase 1 已完成从 **Brief → 适老 Demo → LIVE 管道 → 知识库与族谱 → 包容叙事校准 → 亲授录音互动 → 报名提交** 的完整闭环。  

技术上证明「能听、能记、能播乡音原声」；叙事上锚定「数字包容 + 文化导师 + 安全与跨代连接」。  

**报名成功，第一阶段开发完成。**
