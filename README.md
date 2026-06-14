# Jarvis

A personal Python AI assistant project by Panagiota Grosdouli.

This is not a copy of another Jarvis repository. It is a clean, original starter project that you can extend with your own features.

## Features

- Text-based assistant mode
- Optional voice input and speech output
- Simple command system
- Local memory using SQLite
- OpenAI API integration when an API key is provided
- Safe fallback responses when no API key is configured

## Project structure

```text
jarvis/
├── main.py
├── assistant/
│   ├── __init__.py
│   ├── brain.py
│   ├── commands.py
│   ├── memory.py
│   └── speech.py
├── .env.example
├── .gitignore
└── requirements.txt
```

## Setup

```bash
git clone https://github.com/panagiotagrosdouli/jarvis.git
cd jarvis
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS / Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment variables

Copy `.env.example` to `.env` and add your API key:

```bash
OPENAI_API_KEY=your_api_key_here
```

## Run

```bash
python main.py
```

Useful commands:

```text
help
remember my favorite language is Python
recall
open youtube
open google
time
exit
```

## Next goals

- Add Greek voice commands
- Add a graphical interface
- Add calendar/email integrations
- Add wake-word detection
- Add plugin support
