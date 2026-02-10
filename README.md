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
| Stability | 0.1 (maximum chaos) |
| Similarity | 0.4 (loose) |
| Style | 1.0 (max expressiveness) |
| Fallback | espeak-ng |

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
