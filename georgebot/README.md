# GEORGEBOT
## Multi-Brain Aussie Voice Assistant
**Author:** George Wu | **Platform:** Windows | **Version:** 0.2

---

## WHAT IS THIS

Georgebot is a terminal-based voice assistant that:
- Talks back using ElevenLabs TTS (or Windows voice as fallback)
- Has swappable AI "brains" - local Ollama models or cloud Grok API
- Remembers facts you tell it without explicit commands
- Recalls those facts when you ask questions

**Why it exists:** Ported from Linux "Digger" project to Windows. Built for hands-free coding assistance with an Aussie personality that swears.

---

## ARCHITECTURE (HOW IT WORKS)

```
┌─────────────────────────────────────────────────────────────┐
│                         GEORGEBOT                           │
├─────────────────────────────────────────────────────────────┤
│  georgebot.py          Main CLI loop, handles commands      │
│  config.py             Loads .env, picks brain, TTS setup   │
│  session.py            Conversation history per session     │
│  rag.py                Knowledge base search (RAG)          │
├─────────────────────────────────────────────────────────────┤
│  clients/                                                   │
│  ├── base.py           Brain interface (abstract class)     │
│  ├── ollama.py         Local Ollama subprocess client       │
│  └── grok.py           xAI Grok HTTP API client             │
├─────────────────────────────────────────────────────────────┤
│  models/               Ollama Modelfiles (brain recipes)    │
│  knowledge/            Markdown files for RAG search        │
│  memory/               Session files (gitignored)           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        TALKYTALK                            │
├─────────────────────────────────────────────────────────────┤
│  Separate module at C:\Users\gwu07\Desktop\talkytalk        │
│  Handles ElevenLabs TTS with slang expansion                │
│  Falls back to Windows SAPI if ElevenLabs fails             │
└─────────────────────────────────────────────────────────────┘
```

---

## THE THREE BRAINS

Georgebot has 3 custom Ollama models, each optimized for different tasks:

| Brain | Base Model | Size | Speed | Temperature | Use For |
|-------|------------|------|-------|-------------|---------|
| `georgebot-chat` | mistral:7b | 4.4GB | Fast | 0.7 (creative) | Casual chat, banter, quick Q&A |
| `georgebot-plan` | deepseek-coder:33b | 18GB | Slow | 0.3 (precise) | Architecture, planning, complex reasoning |
| `georgebot-build` | deepseek-coder:6.7b | 3.8GB | Fast | 0.4 (balanced) | Code generation, fixes, debugging |

**Modelfiles location:** `georgebot/models/`

Each Modelfile contains:
- `FROM <base>` - which model to build on
- `SYSTEM "..."` - personality/instructions baked in
- `PARAMETER temperature X` - creativity level
- `PARAMETER num_ctx X` - context window size

---

## INSTALLATION (FROM SCRATCH)

### Prerequisites
- Windows 10/11
- Python 3.8+ (use `python`, NOT `python3` on Windows)
- Git
- Ollama (https://ollama.ai)
- ElevenLabs API key (optional, for good voice)
- Grok API key (optional, for cloud brain)

### Step 1: Clone repos
```powershell
cd C:\Users\gwu07\Desktop
git clone https://github.com/rainfantry/georgebot.git
git clone https://github.com/rainfantry/talkytalk.git
```

### Step 2: Install Python packages
```powershell
cd georgebot
pip install -e .
cd ..\talkytalk
pip install -e .
```

### Step 3: Install Ollama
1. Download from https://ollama.ai
2. Run installer
3. Restart PowerShell
4. Verify: `ollama --version`

### Step 4: Pull base models
```powershell
ollama pull mistral:7b
ollama pull deepseek-coder:6.7b
ollama pull deepseek-coder:33b
```

### Step 5: Build custom brains
```powershell
cd C:\Users\gwu07\Desktop\georgebot
ollama create georgebot-chat -f models\georgebot-chat.Modelfile
ollama create georgebot-plan -f models\georgebot-plan.Modelfile
ollama create georgebot-build -f models\georgebot-build.Modelfile
```

### Step 6: Create .env file
```powershell
notepad .env
```
Add:
```
ELEVENLABS_API_KEY=sk_your_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here
GROK_API_KEY=xai-your_key_here
```

### Step 7: Set up PowerShell aliases
```powershell
notepad $PROFILE
```
Add:
```powershell
function gb { python C:\Users\gwu07\Desktop\georgebot\georgebot.py --brain ollama $args }
function gb-grok { python C:\Users\gwu07\Desktop\georgebot\georgebot.py --brain grok $args }
function gb-silent { python C:\Users\gwu07\Desktop\georgebot\georgebot.py --brain ollama --no-voice $args }
function say { python C:\Users\gwu07\Desktop\talkytalk\talkytalk.py $args }
```

### Step 8: Reload and test
```powershell
. $PROFILE
gb
```

---

## DAILY USAGE

### PowerShell Aliases
| Alias | What it does |
|-------|--------------|
| `gb` | Launch georgebot with Ollama + voice |
| `gb-grok` | Launch with Grok API instead |
| `gb-silent` | Launch without voice output |
| `say "text"` | Speak text through TalkyTalk |

### In-Session Commands
| Command | Action |
|---------|--------|
| `exit` | End session |
| `clear` | Wipe conversation memory |
| `model georgebot-chat` | Switch to chat brain |
| `model georgebot-plan` | Switch to planning brain |
| `model georgebot-build` | Switch to coding brain |
| `models` | List all installed Ollama models |
| `pull <name>` | Download new Ollama model |
| `brain ollama` | Switch to local Ollama |
| `brain grok` | Switch to Grok API |
| `files` | List knowledge base files |
| `load <topic>` | Search knowledge base |
| `remember <note>` | Save note to knowledge base |
| `help` | Show all commands |

---

## NATURAL LANGUAGE MEMORY

Georgebot auto-detects facts and stores them. No commands needed.

### Auto-Store (just say it)
```
You> my name is george
[Remembered: name: george]

You> i work at TAFE
[Remembered: work: tafe]

You> i like python
[Remembered: likes: python]
```

### Auto-Recall (just ask)
```
You> what's my name?
Georgebot: George, ya drongo.

You> where do i work?
Georgebot: TAFE, mate.
```

### Patterns Detected
- `my name is X` → stores name
- `i am X` → stores identity
- `call me X` → stores name
- `i live in X` → stores location
- `i work at/for X` → stores work
- `i like X` → stores preference
- `i hate X` → stores dislike

### How It Works (Technical)
1. `detect_and_store()` in georgebot.py regex-matches input
2. Matched facts saved to `knowledge/notes.md` via rag.py
3. `auto_search()` checks if input contains question words
4. If question detected, searches RAG for relevant facts
5. Found context injected into prompt before sending to brain

---

## FILE STRUCTURE

```
C:\Users\gwu07\Desktop\georgebot\
├── georgebot.py              # Main entry point, CLI loop
├── config.py                 # Environment loader, brain factory, TTS
├── rag.py                    # RAGSearch class, knowledge base
├── session.py                # Session class, conversation history
├── pyproject.toml            # pip install config
├── .env                      # API keys (GITIGNORED)
├── .gitignore                # Ignore patterns
├── README.md                 # This file
├── FIELD_MANUAL.md           # Ollama-specific operations guide
├── GEORGEBOT_QUICKSTART.txt  # Quick reference card
├── clients/
│   ├── __init__.py
│   ├── base.py               # BaseBrain abstract class
│   ├── ollama.py             # OllamaBrain - subprocess client
│   └── grok.py               # GrokBrain - HTTP API client
├── models/
│   ├── georgebot-chat.Modelfile    # Chat brain recipe
│   ├── georgebot-plan.Modelfile    # Planning brain recipe
│   └── georgebot-build.Modelfile   # Coding brain recipe
├── knowledge/                # RAG markdown files
│   └── notes.md              # Auto-stored facts
└── memory/                   # Session files (GITIGNORED)

C:\Users\gwu07\Desktop\talkytalk\
├── talkytalk.py              # TTS module with slang expansion
├── config.py                 # TTS settings
└── pyproject.toml            # pip install config
```

---

## TROUBLESHOOTING

### "ollama: command not found"
Ollama not in PATH. Either:
- Restart PowerShell after install
- Or use full path: `C:\Users\gwu07\AppData\Local\Programs\Ollama\ollama.exe`

### "Model not found"
```powershell
ollama list                    # see what's installed
ollama pull mistral:7b         # download if missing
```

### "No module named elevenlabs"
Wrong Python. Windows has two:
- `python` → C:\Python314 (correct, has packages)
- `python3` → Windows Store Python (wrong, empty)

Always use `python`, not `python3`.

### Voice not working
1. Check .env has ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID
2. Will fallback to Windows SAPI automatically
3. Test with: `say "test"`

### Slow responses
- `georgebot-plan` uses 33b model, it's slow by design
- Switch to `georgebot-chat` for speed
- Or use smaller model: `model mistral:7b`

### Out of memory
```powershell
ollama pull mistral:7b-q4_0    # smaller quantization
ollama pull tinyllama          # tiny model
```

---

## API KEYS

Store in `.env` (gitignored, never committed):

```
# ElevenLabs TTS (https://elevenlabs.io)
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=...

# Grok API (https://x.ai)
GROK_API_KEY=xai-...
```

Get keys from:
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys
- Grok: https://console.x.ai/

---

## REBUILDING FROM NOTHING

If laptop falls into black hole:

1. Get new Windows machine
2. Install Python 3.8+ from python.org
3. Install Git from git-scm.com
4. Install Ollama from ollama.ai
5. Clone: `git clone https://github.com/rainfantry/georgebot.git`
6. Clone: `git clone https://github.com/rainfantry/talkytalk.git`
7. Install: `pip install -e georgebot && pip install -e talkytalk`
8. Pull models: `ollama pull mistral:7b && ollama pull deepseek-coder:6.7b && ollama pull deepseek-coder:33b`
9. Build brains: run the 3 `ollama create` commands
10. Create `.env` with your API keys
11. Set up PowerShell aliases
12. Run: `gb`

Everything else is in the repo.

---

## RELATED PROJECTS

| Project | Location | Purpose |
|---------|----------|---------|
| georgebot | github.com/rainfantry/georgebot | This project |
| talkytalk | github.com/rainfantry/talkytalk | TTS module |
| digger | github.com/rainfantry/digger | Original Linux version |

---

## LICENSE

MIT - Do whatever you want.

---

**George Wu - 2026**
