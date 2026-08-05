这是一份专门为 **Cursor** 编写的「项目转型指令集 (Pivot Brief)」。它能让 Cursor 明白为什么我们要从宏大的《乡音回响》缩减到具体的《奶奶的乡音管家》，并指导它完成代码修改。

你可以将以下内容保存为 `Pivot_To_Nana_Agent.md`，放在项目根目录下，然后在 Cursor Chat 中输入：**"Read @Pivot_To_Nana_Agent.md and help me transform the project."**

---

# Project Pivot: From "Echo of Roots" to "Nana's Teochew Agent"

## 1. Context & Goal
*   **Original Project:** *Echo of Roots* (A large-scale digital inclusion platform for dialect-speaking seniors).
*   **New Target:** *Teochew-Nana-Agent* (A personalized AI Agent specifically for **my grandma** who lives in our hometown).
*   **Hackathon Context:** Participating in the **EazO Global Youth AI Agent Hackathon**. 
*   **Mission:** Build a "Just enough" Agent for a **Specific Person** to solve her real-life daily challenges.

## 2. Target Persona: My Grandma (阿芳奶奶)
*   **Linguistic Background:** Speaks **ONLY Teochew**. Cannot understand Mandarin well.
*   **Tech Barrier:** Afraid of complex smartphone interfaces. 
*   **Primary Needs:**
    1.  **Connecting with Grandson:** Wants to hear messages from me (who speaks Mandarin).
    2.  **Daily Reminders:** Needs to be reminded to take medication and check the weather.
    3.  **Loneliness:** Needs a "living" companion to talk to in her mother tongue.
    4.  **Entertainment:** Loves Teochew Opera but finds it hard to search for it.

## 3. Core Modifications (The "Pivots")

### A. Narrative Shift (Identity)
*   The AI is no longer a "Platform." It is **"Nana's Little Helper" (阿嫲的小管家)**.
*   Tone of voice: Humble, filial, and respectful (using grandson-to-grandma honorifics).

### B. Simplified UI (The 3-Button Rule)
Replace the current multi-mode UI with **3 Ultra-Large Buttons**:
1.  **"Listen to Grandson" (听孙子留言 - Blue):** A bridge for Mandarin-to-Teochew messages.
2.  **"Talk to Helper" (跟管家聊天 - Red):** The dialect conversation mode we previously built.
3.  **"Teochew Opera/Radio" (听潮剧/广播 - Green):** Quick access to her favorite audio content.

### C. Feature Implementation
1.  **Mandarin-Teochew Bridge:** 
    - Simulate a function where a text message (Mandarin) is sent to the Agent.
    - The Agent reads the message, translates the intent, and plays the **Teochew recording** (Voice Echo).
2.  **Smart Reminders:** 
    - Automatically trigger a "Medication Reminder" in Teochew when the app starts or a button is pressed.
3.  **Knowledge Base Integration:**
    - Continue using `@dialect_data.json` but focus on the "Daily Life" and "Family" categories.

## 4. Technical Instructions for Cursor

### Task 1: UI Refactoring
*   Modify `App.jsx` to reflect the 3-button layout.
*   Ensure high contrast and use even larger icons (Lucide-react).
*   Remove "Mentor Mode" and "Safety Scan" from the main view (keep them as hidden functions or simplified logic).

### Task 2: Interaction Logic Update
*   **Status Management:** Update the state machine to handle: `IDLE`, `LISTENING_TO_NANA`, `PLAYING_GRANDSON_MESSAGE`, `PLAYING_OPERA`.
*   **Voice Echo Mapping:** Map "Grandson's Message" (Mandarin text) to specific Teochew audio files (e.g., "I'm coming home this weekend" -> `back_home.mp3`).

### Task 3: Persona Prompting
*   Update the System Prompt for the LLM: 
    > "You are the personal AI Agent for a Teochew Grandma. Your name is 'Little Helper'. You are her grandson's representative. Always speak with filial respect. If she speaks Teochew, respond by matching her dialect's rhythm and emotion."

## 5. Success Criteria for EazO Hackathon
*   **Deliverability:** A working web app that my grandma can actually tap.
*   **Specific Utility:** Prove that the Agent understands Nana's specific dialect and makes her life easier.
*   **Emotional Connection:** The Agent must sound like a family member, not a machine.

---

### 💡 接下来如何操作？

1.  **在 Cursor 中新建文件**：命名为 `Pivot_To_Nana_Agent.md` 并粘贴上述内容。
2.  **启动 Chat**：选中该文件，输入指令：
    > "I want to pivot my project to the Nana Agent as described in @Pivot_To_Nana_Agent.md. Please start by refactoring the **App.jsx UI** to the 3-button layout and update the theme to be more warm and personal."
3.  **准备素材**：既然是为了奶奶，录音时语气可以更亲昵一点。

**这个 MD 文档会让 Cursor 瞬间从“社会责任模式”切换到“孝顺孙子模式”，开始你的快速迭代吧！**