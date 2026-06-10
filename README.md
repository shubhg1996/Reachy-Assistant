# Reachy Assistant

A voice‑controlled AI assistant for the **Reachy Mini** robot.  
Say the wake word, speak to the robot – it processes your intent, performs actions, and responds with speech accompanied by expressive movements.

Built from six reusable internal libraries:
- `wakeword` – minimal, localized wake word detection utilizing openWakeWord.
- `speech2text` – local transcription via OpenAI Whisper.
- `llmclient` – OpenRouter API integration for contextual fallback text generation and structured intent classification.
- `intent_handlers` – architectural routing for executable actions (e.g., photo capture).
- `iphone_cam` – automated multi-camera scanner and frame grabber optimized for Apple Continuity Camera backends.
- `ttsclient` – high-fidelity text‑to‑speech conversion via edge‑tts.
- `reachy_mini_lib` – a clean, safe-default hardware abstraction wrapper around the official Reachy Mini SDK.

---

## Quick Start

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/shubhg1996-reachy-assistant.git](https://github.com/yourusername/shubhg1996-reachy-assistant.git)
cd shubhg1996-reachy-assistant
```

### 2. Create a Python environment (Python 3.11 recommended)
```
python -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` on Windows
```

### 3. Install all packages (editable)
```
pip install -e packages/wakeword
pip install -e packages/speech2text
pip install -e packages/llmclient
pip install -e packages/iphone_cam
pip install -e packages/ttsclient
pip install -e packages/reachy_mini_lib
pip install -e .
```

### 4. Set your OpenRouter API key
```
export OPENROUTER_API_KEY="your-key-here"
```

### 5. Run the assistant
```
python -m reachy_assistant
```

Trigger Workflow: Say "hey mycroft". The system will chime audio feedback, open a 4-second local recording window, run inference for downstream tasks, and move the robot concurrently with streaming speech responses.

## Capabilities & Intent Handling

The assistant coordinates user prompts into actionable events using the llmclient structured JSON encoder framework. Current native capabilities include:
- `chat` – No hardware-level action. Evaluates text semantics via keyword mappings inside action_mapper.py to play reactive emotion files.
- `take_picture` – Wakes the camera abstraction subsystem via iphone_cam, captures an explicit high-definition frame (1280x720), and saves it locally inside the photos/ directory.

## Requirements

- Reachy Mini (Lite or Wireless) or simulation mode (motion only)
- Microphone (robot’s USB mic or fallback to system mic)
- Speakers (robot’s USB speaker or fallback to system audio)
- Internet connection (first run downloads Whisper & emotion library)

## Repository structure
```
shubhg1996-reachy-assistant/
├── pyproject.toml         # Top-level dependencies & installation metadata
├── examples/              # Isolated subsystem validation scripts
├── packages/              # Reusable localized library suites
│   ├── iphone_cam/        # Continuity Camera video capture wrappers
│   ├── llmclient/         # OpenRouter communication & structured intent decoding
│   ├── reachy_mini_lib/   # Encapsulated Reachy Mini SDK control layer
│   ├── speech2text/       # Local Whisper transcription setup
│   ├── ttsclient/         # Edge-TTS speech generation client
│   └── wakeword/          # openWakeWord listener & VAD framework
└── src/
    └── reachy_assistant/  # Core orchestration runtime and intent loops
```
