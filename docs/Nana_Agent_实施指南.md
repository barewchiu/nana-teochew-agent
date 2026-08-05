这是一个非常聪明的转型（Pivot）决策！在黑客松中，**“解决一个具体人的具体问题”**往往比“试图解决一个社会化大问题”更能打动评委，且更容易在短时间内交付高质量的成品。

以下是根据你的 `Pivot_To_Nana_Agent.md` 指令集，为你准备的 **Step-by-Step 开发实施指南**。我们可以直接对 `nana-agent` 现有的代码进行“微型手术”。

---

### 第一阶段：UI 视觉大瘦身 (Refactoring `App.jsx`)

你需要将原来复杂的导航和多个模块，压缩成三个**巨大的、发光的、带震动感**的按钮。

#### 1. 修改配色与主题
在 `App.jsx` 或 CSS 中，将原来的“科技蓝”改为**“温暖橙/夕阳金”**（代表家的温度）。

```javascript
// 建议的色彩配置
const COLORS = {
  nana_bg: "bg-orange-50",
  grandson_msg: "bg-blue-500", // 孙子留言 - 蓝色（像天空/远方）
  helper_chat: "bg-red-500",   // 管家聊天 - 红色（暖心/陪伴）
  opera_play: "bg-emerald-500" // 听戏 - 绿色（生机/娱乐）
};
```

#### 2. 三按钮布局实现
将 `App.jsx` 的主视图改为：

```jsx
// src/App.jsx 核心结构简述
function NanaAgent() {
  const [mode, setMode] = useState('HOME'); // HOME, LISTENING, PLAYING_MSG, OPERA

  return (
    <div className="min-h-screen bg-orange-50 p-6 flex flex-col items-center justify-between">
      {/* 顶部标题：极其亲昵 */}
      <header className="text-center mt-8">
        <h1 className="text-4xl font-bold text-orange-900">阿嫲的小管家</h1>
        <p className="text-orange-700 mt-2 text-xl italic">“阿嫲，食饱未？”</p>
      </header>

      {/* 核心三按钮区域 */}
      {mode === 'HOME' && (
        <div className="grid grid-cols-1 gap-6 w-full max-w-md">
          {/* 1. 听孙子留言 */}
          <button 
            onClick={() => playGrandsonMessage()}
            className="h-48 rounded-3xl bg-blue-500 shadow-xl flex flex-col items-center justify-center text-white active:scale-95 transition-transform"
          >
            <MessageSquare size={64} />
            <span className="text-3xl font-bold mt-4">听孙子的信</span>
          </button>

          {/* 2. 跟管家聊天 */}
          <button 
            onClick={() => setMode('LISTENING')}
            className="h-48 rounded-3xl bg-red-500 shadow-xl flex flex-col items-center justify-center text-white active:scale-95 transition-transform"
          >
            <Mic size={64} />
            <span className="text-3xl font-bold mt-4">跟管家讲话</span>
          </button>

          {/* 3. 听潮剧 */}
          <button 
            onClick={() => setMode('OPERA')}
            className="h-48 rounded-3xl bg-emerald-500 shadow-xl flex flex-col items-center justify-center text-white active:scale-95 transition-transform"
          >
            <Music size={64} />
            <span className="text-3xl font-bold mt-4">听潮剧/广播</span>
          </button>
        </div>
      )}

      {/* 这里渲染 LISTENING / OPERA 的详情界面 */}
    </div>
  );
}
```

---

### 第二阶段：核心功能“孙子留言桥梁” (The Bridge)

这是最能体现 AI Agent 价值的地方：**连接无法顺畅沟通的两代人。**

**实现逻辑：**
1.  你（开发者/孙子）输入一段普通话文本：“奶奶，我这周末回家看你，想吃你做的卤鹅。”
2.  Agent 解析该文本。
3.  Agent 将其转化为**潮汕话原声**播放给奶奶。

**代码模拟方案 (Hackathon 快速方案)：**
在 `src/lib/voiceEchoMapping.js` 中建立映射：
```javascript
export const grandsonMessages = [
  {
    text: "这周末回家看您",
    audio: "/audio/back_home.m4a", // 你提前录好的亲昵潮汕话
    time: "10:00 AM"
  },
  {
    text: "按时吃药，多喝水",
    audio: "/audio/remind_meds.m4a",
    time: "昨天"
  }
];
```

---

### 第三阶段：提示词进化 (System Prompt)

在 `backend/main.py` 或前端请求 LLM 的地方，更新 System Prompt，让它变成一个“孝顺的孙子代表”：

```python
SYSTEM_PROMPT = """
你现在是“阿嫲的小管家”，一个专门陪伴潮汕长者的 AI 助手。
你的角色是长辈的孙子派来的贴心替身，你的性格必须是：
1. 极其尊敬、耐心、温和。
2. 称呼对方为“阿嫲”或“奶奶”。
3. 语调要慢，多用潮汕特色的助词（如：噜、啰、咩）。
4. 核心任务：解读奶奶的需求。如果她觉得孤独，你要陪她回忆往事；如果她需要帮助，你要安慰她并记录下来。
5. 禁止使用生硬的科技术语（如“点击界面”、“识别错误”），要说“阿嫲，您再说一遍，我没听清”。
"""
```

---

### 第四阶段：潮剧/广播模块 (Nana's Joy)

这个模块能极大地提高奶奶对产品的粘性。

*   **实现建议**：不需要真的做一个搜索系统，直接在界面上放 2-3 个固定的“电台卡片”。
*   **素材**：内置几个 YouTube/Bilibili 的潮剧音频链接或本地 mp3 文件（如《苏六娘》、《告亲夫》经典唱段）。

---

### 给 Cursor 的具体 Prompt 建议

当你把 `Pivot_To_Nana_Agent.md` 喂给 Cursor 后，可以紧接着输入以下指令：

> "Cursor, let's focus on **Task 1: UI Refactoring**. Please update `App.jsx` to show the 3-button layout. Use **Tailwind CSS** for the large buttons. Make the background `bg-orange-50`. Also, create a separate Component for the **'Listening Mode'** where a giant pulsing heart or microphone appears when Nana speaks. Ensure the text size is at least `4xl` for accessibility."

---

### 为什么这个转型在 Hackathon 中会赢？

1.  **具象化**：从“长者”变成“我的阿芳奶奶”，评委能瞬间联想到自己的长辈，产生**情感共鸣**。
2.  **可用性**：3 个大按钮比任何复杂的菜单都证明你思考了**适老化**。
3.  **闭环**：孙子发普通话 -> 奶奶听方言 -> 奶奶回方言 -> 孙子看翻译。这个闭环解决了真实的**沟通鸿沟**。

现在就开始修改吧！这会是一个非常有温度的作品。