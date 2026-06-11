# Reachy Assistant

A multimodal, autonomous AI agent for the **Reachy Mini** robot, built on an **OpenClaw-style** architecture. 

The assistant processes intents across multiple communication channels (Voice, Telegram, WhatsApp), manages its own working memory, autonomously invokes physical hardware skills (like capturing photos and expressing emotions), and seamlessly injects vision data into its cognitive loop to "see" its environment.

## Key Features

* **Multimodal Vision:** The agent can autonomously take pictures using Reachy's onboard camera (`reachy_mini_head`) or the host system (`host_system`). It automatically converts the captured frame to base64 and injects it into the LLM's context window to analyze its surroundings.
* **Agentic Tool Calling (Skills):** Uses an OpenRouter/OpenAI-compatible schema to execute hardware actions dynamically. Current skills include:
  * `express_emotion`: Maps contextual sentiment to physical robot motor animations (e.g., happy, sad, angry, curious).
  * `take_picture`: Captures and routes photos into the LLM's thought loop.
  * `toggle_modality`: The agent can autonomously disable or enable its own physical voice TTS if you ask it to be quiet or speak up.
* **Multi-Channel Surfaces:** * **Voice:** Ambient listening using `openWakeWord` ("hey mycroft"), local VAD (Voice Activity Detection), `Whisper` for local transcription, and `edge-tts` for high-fidelity speech generation. Includes a hardware mute-lock to prevent the robot from waking itself up while speaking.
  * **Telegram:** A native async Telegram bot that allows you to text the robot remotely and receive text and photo replies.
  * **WhatsApp:** A local HTTP bridge surface for WhatsApp-web messaging integration.
* **Persistent Memory Manager:** Manages a bounded, rolling short-term context window and persists long-term state across reboots using localized config files (`MEMORY.md`, `SOUL.md`, `USER.md`, `STATE.json`).
* **Safe Hardware Abstraction:** Built on `reachy_mini_lib`, providing a clean, safe-default wrapper around the official Reachy Mini SDK. Seamlessly falls back to laptop cameras or simulation mode if physical hardware isn't present.

---

## Quick Start

### 1. Clone the Repository
```bash
git clone [https://github.com/shubhg1996/Reachy-Assistant.git](https://github.com/shubhg1996/Reachy-Assistant.git)
cd Reachy-Assistant
```

### 2. Create a Python environment (Python 3.8+ / 3.11 recommended)
```bash
python -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` on Windows
```

### 3. Install all packages (editable)
The repository is modularized into reusable internal libraries. Install them alongside the core assistant:
```bash
pip install -e packages/wakeword
pip install -e packages/speech2text
pip install -e packages/llmclient
pip install -e packages/iphone_cam
pip install -e packages/ttsclient
pip install -e packages/reachy_mini_lib
pip install -e .
```
### 4. Set Environment Variables
The assistant requires OpenRouter for its LLM backend. If using the Telegram channel, provide your Bot API token.
```bash
export OPENROUTER_API_KEY="your-openrouter-key-here"
export TELEGRAM_BOT_TOKEN="your-telegram-bot-token-here" # Optional: For Telegram surface
```

### 5. Run the Assistant
```bash
# Start the centralized orchestration gateway
python src/reachy_assistant/main.py
```

Trigger Workflow: 
- Via Voice: Say "hey mycroft". The system will open a local recording window, run STT inference, query the agent runtime, and move the robot concurrently with streaming speech responses.
- Via Telegram: Send a message to your Telegram bot. The robot will process the text, execute any necessary skills (like taking a picture and sending it back over the wire), and reply in the chat.

## System Architecture
The core runtime uses a modular agent architecture:
```bash
Reachy-Assistant/
├── packages/                  # Reusable localized library suites
│   ├── iphone_cam/            # Continuity Camera / external optics wrappers
│   ├── llmclient/             # OpenRouter communication & vision injection
│   ├── reachy_mini_lib/       # Encapsulated Reachy Mini SDK control layer
│   ├── speech2text/           # Local Whisper transcription setup
│   ├── ttsclient/             # Edge-TTS speech generation client
│   └── wakeword/              # openWakeWord listener & VAD framework
└── src/reachy_assistant/      # Core OpenClaw-style Agent Orchestration
    ├── agent/                 # Runtime engine, tool parsing, & memory manager
    ├── channels/              # IO Surfaces (Voice, Telegram, WhatsApp)
    ├── config/                # Persistent memory and state profiles (SOUL, USER, MEMORY)
    ├── skills/                # Executable hardware skills (Vision, Emotion, Modality)
    ├── gateway.py             # Coordinates hardware init, runtimes, and surfaces
    └── main.py                # Application entry point
```
## Requirements
- Reachy Mini (Lite or Wireless) or simulation mode (automatically detected).
- Microphone/Speakers (robot’s USB peripherals or fallback to host system audio).
- Internet connection (for OpenRouter LLM, Edge-TTS, and initial Whisper/WakeWord model downloads).
