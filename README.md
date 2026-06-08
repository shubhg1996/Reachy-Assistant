# Reachy Assistant

A voice‑controlled AI assistant for the **Reachy Mini** robot.  
Hold a key, speak to the robot – it responds with speech and expressive movements.

Built from four reusable libraries:
- `speech2text` – local transcription (OpenAI Whisper)
- `llmclient` – OpenRouter API for LLM responses
- `ttsclient` – text‑to‑speech (edge‑tts)
- `reachy_mini_lib` – simplified Reachy Mini SDK wrapper

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/Reachy_Assistant.git
cd Reachy_Assistant
```

### 2. Create a Python environment (Python 3.11 recommended)
```
python -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` on Windows
```

### 3. Install all packages (editable)
```
pip install -e packages/speech2text
pip install -e packages/llmclient
pip install -e packages/ttsclient
pip install -e packages/reachy_mini_lib
pip install -e assistant
```

### 4. Set your OpenRouter API key
```
export OPENROUTER_API_KEY="your-key-here"
```

### 5. Run the assistant
```
python -m reachy_assistant
```

- Hold SPACE – start speaking to the robot.
- Release SPACE – the robot processes your voice, answers, and moves.

## Requirements

- Reachy Mini (Lite or Wireless) or simulation mode (motion only)
- Microphone (robot’s USB mic or fallback to system mic)
- Speakers (robot’s USB speaker or fallback to system audio)
- Internet connection (first run downloads Whisper & emotion library)

## Repository structure
```
Reachy_Assistant/
├── packages/
│   ├── speech2text/       # Speech‑to‑text library
│   ├── llmclient/         # OpenRouter LLM client
│   ├── ttsclient/         # Text‑to‑speech library
│   └── reachy_mini_lib/   # Reachy Mini SDK wrapper
├── assistant/             # The voice assistant itself
│   └── src/reachy_assistant/
├── README.md
```
