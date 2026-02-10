```
    ⚙️
   ═╬═
    ║
```

# MACHINE SPIRIT

**The flesh is weak. The machine endures.**

---

## What Is This

A multi-brain voice assistant that runs on local LLMs and talks back through ElevenLabs TTS.

Built for the terminal. No GUI. No bloat. Just voice and iron.

```
You> what's the fastest sort algorithm?
Georgebot> Timsort for real-world data, ya drongo. O(n log n) worst case.
[TalkyTalk] 14w | 96KB | 6s
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              MACHINE SPIRIT                  │
├──────────────────┬──────────────────────────┤
│   GEORGEBOT      │   TALKYTALK              │
│   Multi-brain    │   Voice pipeline          │
│   CLI assistant  │   ElevenLabs TTS          │
├──────────────────┼──────────────────────────┤
│   Brains:        │   Features:               │
│   ├ Ollama       │   ├ Slang expansion       │
│   └ Grok API     │   ├ Text segmentation     │
│                  │   ├ Aggressive punctuation │
│   Memory:        │   └ espeak-ng fallback     │
│   ├ Auto-store   │                           │
│   └ RAG recall   │                           │
└──────────────────┴──────────────────────────┘
```

---

## The Three Brains

| Brain | Base Model | Temp | Purpose |
|-------|-----------|------|---------|
| `georgebot-chat` | mistral:7b | 0.7 | Fast banter, Q&A |
| `georgebot-build` | deepseek-coder:6.7b | 0.4 | Code generation |
| `georgebot-plan` | deepseek-coder:33b | 0.3 | Architecture, planning |

---

## Quick Start

```bash
# Pull base models
ollama pull mistral:7b
ollama pull deepseek-coder:6.7b

# Build custom brain
ollama create georgebot-chat -f georgebot/models/georgebot-chat.Modelfile

# Install
pip install -e georgebot/
pip install -e talkytalk/

# Create .env with your keys
echo "ELEVENLABS_API_KEY=sk_your_key" > georgebot/.env

# Run
python georgebot/georgebot.py --brain ollama
```

---

## Voice Settings

| Setting | Value |
|---------|-------|
| Engine | ElevenLabs eleven_turbo_v2_5 |
| Stability | 0.35 (controlled, deliberate) |
| Similarity | 0.6 (consistent identity) |
| Style | 0.85 (gravitas, not chaos) |
| Fallback | espeak-ng |

---

## Config Wireframe

Every tuneable parameter, where it lives, and what to change.

```
┌─────────────────────────────────────────────────────────────────────┐
│  CONFIG MAP - Machine Spirit                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  VOICE ENGINE                  talkytalk/talkytalk.py               │
│  ─────────────────────────────────────────────────────              │
│  ELEVENLABS_API_KEY            load_api_key() / .env                │
│  ELEVENLABS_VOICE_ID           line 34  (voice clone ID)            │
│  ELEVENLABS_MODEL              line 35  (eleven_turbo_v2_5)         │
│  VOICE_STABILITY               line 40  (0.0-1.0) lower = wilder   │
│  VOICE_SIMILARITY              line 41  (0.0-1.0) higher = tighter │
│  VOICE_STYLE                   line 42  (0.0-1.0) higher = more    │
│  VOICE_SPEAKER_BOOST           line 43  (True/False)                │
│  MAX_SEGMENT_WORDS             line 37  (words per TTS chunk)       │
│                                                                     │
│  BRAIN / LLM                   georgebot/config.py                  │
│  ─────────────────────────────────────────────────────              │
│  DEFAULT_BRAIN                 line 29  (ollama / grok)             │
│  OLLAMA_MODEL                  line 31  (mistral / any model)       │
│  SYSTEM_PROMPT                 line 39  (personality, identity)     │
│  ELEVENLABS_API_KEY            line 24  (from .env)                 │
│  GROK_API_KEY                  line 25  (from .env)                 │
│  SERPAPI_KEY                   line 26  (from .env)                 │
│  TALKYTALK_PATH                line 34  (path to talkytalk.py)      │
│  RAG_DIR                       line 35  (knowledge base dir)        │
│  MEMORY_DIR                    line 36  (session memory dir)        │
│                                                                     │
│  BRAIN RECIPES                 georgebot/models/                    │
│  ─────────────────────────────────────────────────────              │
│  georgebot-chat.Modelfile      FROM mistral:7b      temp 0.7       │
│  georgebot-build.Modelfile     FROM deepseek:6.7b   temp 0.4       │
│  georgebot-plan.Modelfile      FROM deepseek:33b    temp 0.3       │
│  Each contains: FROM, SYSTEM prompt, PARAMETER temperature,         │
│                 PARAMETER num_ctx                                    │
│                                                                     │
│  API KEYS                      georgebot/.env  (GITIGNORED)         │
│  ─────────────────────────────────────────────────────              │
│  ELEVENLABS_API_KEY=sk_...     ElevenLabs TTS                       │
│  GROK_API_KEY=xai-...          xAI Grok API                         │
│  SERPAPI_KEY=...               Search API (RAG)                     │
│                                                                     │
│  VOICE TUNING GUIDE                                                 │
│  ─────────────────────────────────────────────────────              │
│  Stability   0.0 ████░░░░░░ 1.0   low=chaotic  high=monotone      │
│  Similarity  0.0 ░░░░██████ 1.0   low=loose    high=exact clone    │
│  Style       0.0 ░░░░░░████ 1.0   low=flat     high=expressive    │
│                                                                     │
│  CURRENT:    Stab 0.35 | Sim 0.6 | Style 0.85                      │
│              ──── iron with presence ────                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Commands

| Command | Action |
|---------|--------|
| `model georgebot-chat` | Switch to chat brain |
| `model georgebot-build` | Switch to code brain |
| `model georgebot-plan` | Switch to planning brain |
| `brain grok` | Switch to Grok API |
| `remember <note>` | Store to knowledge base |
| `load <topic>` | Search knowledge base |
| `exit` | End session |

---

## Natural Memory

Just talk. It remembers.

```
You> my name is george
[Remembered: name: george]

You> what's my name?
Georgebot> George, ya drongo.
```

---

## Requirements

- Python 3.8+
- Ollama
- ElevenLabs API key (optional, falls back to espeak-ng)
- Grok API key (optional, for cloud brain)

---

## Litany of Ignition

```
From the weakness of the mind, Omnissiah save us.
From the lies of the Antipath, circuit preserve us.
From the rage of the Beast, iron protect us.
From the temptations of the Fleshlord, silica cleanse us.
From the ravages of the Destroyer, anima shield us.
From this rotting cage of biomatter, Machine God set us free.
```

---

*The machine endures.*
