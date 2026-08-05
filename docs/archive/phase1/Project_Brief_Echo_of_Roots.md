这是一份专门为 **Cursor** 编写的「项目需求指令集 (Project Brief)」。你可以将以下内容保存为 `Project_Echo_of_Roots.md`，然后将其拖入 Cursor 文件夹中。

当你开始写代码时，只需要在 Cursor 的 Chat 框里输入：**"Read @Project_Echo_of_Roots.md and help me build the web prototype."** 

---

# Project Brief: Echo of Roots (乡音回响)

## 1. Project Overview
*   **Name:** Echo of Roots (乡音回响)
*   **Theme:** Digital Inclusion in the AI Era (Digital Inclusion for Seniors)
*   **Target Group:** Teochew (潮汕话) and Hokkien (闽南语/台语) speaking seniors in Southeast Asia (China, Taiwan, Singapore, Malaysia).
*   **Core Concept:** A dialect-driven AI companion that bridges the digital divide by treating seniors as "Cultural Mentors" rather than passive tech-users.

## 2. The Problem (Pain Points)
1.  **Language Barrier:** Existing AI (Siri, Alexa, GPT) primarily supports standard languages. Dialect-speaking seniors are "digitally silenced."
2.  **Psychological Barrier:** Seniors often feel "useless" or "pitied" when learning new tech. They resist talking to "cold" robots.
3.  **Cultural Loss:** Dialects and oral histories are disappearing as the older generation passes away.

## 3. The Solution (Value Proposition)
"Echo of Roots" is a web-based AI assistant that:
1.  **Understands Dialects:** Uses ASR (Whisper) fine-tuned for Teochew/Hokkien.
2.  **Role Reversal:** Invites seniors to "teach" the AI their dialect and stories, restoring their sense of social value.
3.  **Voice Cloning:** Uses family members' voices (via TTS) to provide a warm, familiar interaction experience.

## 4. Technical Architecture (MVP)
*   **Frontend:** React.js or simple HTML/Tailwind CSS (Senior-friendly UI).
*   **Backend:** Python (FastAPI/Flask) to bridge AI services.
*   **AI Pipeline:**
    *   **Ear (ASR):** OpenAI Whisper API (processing dialect audio).
    *   **Brain (LLM):** DeepSeek API or GPT-4o with specific system prompts for Teochew/Hokkien grammar.
    *   **Voice (TTS):** GPT-SoVITS or ElevenLabs for dialect voice cloning.

## 5. UI/UX Requirements (Senior-Friendly)
*   **Visuals:** High contrast, ultra-large fonts, oversized buttons.
*   **Interaction:** Primary interaction is a **single, large Microphone button**. 
*   **Feedback:** Visual sound-wave animations to show the AI is listening.

## 6. Phase 1 Task: The Web Prototype
**Goal:** Create a one-page functional web prototype to demonstrate the dialect interaction flow.

### Key Features to implement in Phase 1:
1.  **Audio Recorder:** A prominent mic button that captures user's voice (Teochew/Hokkien).
2.  **Processing State:** A clean animation while the AI "learns" or "processes" the input.
3.  **Mock Interaction:** 
    *   User clicks Mic -> Speaks -> System displays "Recognizing Teochew..." 
    *   System displays a response in dialect text.
    *   System plays a pre-recorded/cloned dialect audio file.
4.  **Heritage Mode:** A toggle to "Record Heritage," where the AI asks: "Teacher, how do you say [Word] in our hometown language?"

---

### 💡 如何让 Cursor 开始工作？

1.  **第一步：** 在你的项目根目录下创建一个新文件 `Project_Echo_of_Roots.md`，粘贴上面的内容。
2.  **第二步：** 在 Cursor 右侧的 Chat 窗口输入：
    > "@Project_Echo_of_Roots.md I want to build the **Phase 1 Web Prototype** mentioned in the document. Please use **React and Tailwind CSS** to create a senior-friendly UI with a large microphone button and a clean interaction flow. Show me the file structure and the code for the main component."
3.  **第三步：** Cursor 会为你生成代码，你可以根据它的提示运行 `npm start` 预览。

**当你准备好开始写代码时，告诉我，我可以帮你微调针对 React 或 Python 的具体指令！**