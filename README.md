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

## Function Breakdown

How every function works and how to modify them.

### TALKYTALK — Voice Pipeline (`talkytalk/talkytalk.py`)

```
Input text → expand_slang() → filter_text() → punch_text() → segment_text() → speak_elevenlabs()
                                                                                     ↓ (if fail)
                                                                                speak_local()
```

**`load_api_key()`** — Loads ElevenLabs API key
```python
# Checks os.environ first, then reads .env file
# To modify: change the .env key name or add a new source
key = os.environ.get("ELEVENLABS_API_KEY")
```

**`is_online()`** — Checks if ElevenLabs API is reachable
```python
# Opens socket to api.elevenlabs.io:443 with 2s timeout
# Returns True/False. If False, voice falls back to espeak-ng
# To modify: change timeout or target host
socket.create_connection(("api.elevenlabs.io", 443), timeout=2)
```

**`expand_slang(text)`** — Expands abbreviations for TTS pronunciation
```python
# SLANG_MAP is a dict of regex → replacement
# "fkn" → "fucken", "u" → "you", "cos" → "cause"
# To add new slang: add to SLANG_MAP dict
SLANG_MAP = {
    r'\bfkn\b': 'fucken',    # regex word boundary match
    r'\bu\b': 'you',          # prevents matching inside words
}
# Each entry: r'\bSLANG\b': 'full word'
# \b = word boundary so "fun" doesn't become "fyoun"
```

**`filter_text(text)`** — Strips code and markdown before speaking
```python
# Removes: ```code blocks```, `inline code`, **bold**, _italic_
# Skips lines starting with: def, class, import, if, for, return
# To modify: add regex patterns to remove, or add to the skip list
text = re.sub(r'```[\s\S]*?```', '', text)  # kill code blocks
```

**`punch_text(text)`** — Manipulates punctuation to control voice tone
```python
# Short sentences (≤4 words) → adds ! (punchy)
# Long sentences (>6 words, no comma) → adds comma after first word (pause)
# Sentences >8 words ending with . → changes to ... (trailing emphasis)
# To modify: change word count thresholds or punctuation rules
if len(words) <= 4 and not s.endswith(('!', '?')):
    s = s.rstrip('.') + '!'   # "Done mate" → "Done mate!"
```

**`speak_local(text)`** — Fallback TTS when offline
```python
# Linux: espeak-ng with speed 160
# Windows: PowerShell SAPI speech synthesis
# To modify: change espeak-ng flags (-s speed, -p pitch, -v voice)
subprocess.run(["espeak-ng", "-s", "160", text])
```

**`get_audio_duration(path)`** — Gets MP3 length for playback timing
```python
# Linux: uses ffprobe to read duration
# Windows: uses PowerShell MediaPlayer
# Returns seconds (int). Fallback: 10 seconds
# To modify: change fallback duration or add new audio tool
```

**`speak_elevenlabs(text, segment_num=0)`** — Core TTS function
```python
# 1. Creates ElevenLabs client with API key
# 2. Calls text_to_speech.convert() with voice settings
# 3. Saves MP3 to ~/.talkytalk/voice/segment_N.mp3
# 4. Gets duration, prints stats
# 5. Plays with mpv (Linux) or PowerShell MediaPlayer (Windows)
# To modify voice: change VOICE_STABILITY, VOICE_SIMILARITY, VOICE_STYLE
# To change player: swap mpv command on line 278
audio = client.text_to_speech.convert(
    text=text,
    voice_id=ELEVENLABS_VOICE_ID,
    model_id=ELEVENLABS_MODEL,
    voice_settings=VoiceSettings(
        stability=VOICE_STABILITY,       # 0.0-1.0
        similarity_boost=VOICE_SIMILARITY, # 0.0-1.0
        style=VOICE_STYLE,               # 0.0-1.0
        use_speaker_boost=VOICE_SPEAKER_BOOST
    )
)
```

**`segment_text(text, max_words=100)`** — Splits long text for TTS
```python
# ElevenLabs has limits, long text sounds bad in one shot
# Splits at sentence boundaries (. ! ?) or at max_words
# Returns list of strings
# To modify: change MAX_SEGMENT_WORDS (default 100)
```

**`speak(text, force_local=False)`** — Main entry point
```python
# The whole pipeline in order:
# 1. expand_slang()  → fix abbreviations
# 2. filter_text()   → strip code/markdown
# 3. punch_text()    → aggressive punctuation
# 4. Check online    → if offline, use speak_local()
# 5. segment_text()  → split if long
# 6. speak_elevenlabs() per segment → fallback to speak_local() if fail
# Returns: "elevenlabs", "local", or "empty"
```

---

### GEORGEBOT — Brain & CLI (`georgebot/georgebot.py`)

```
User input → detect_and_store() → auto_search() → build context → brain.chat() → speak()
```

**`detect_and_store(text, rag)`** — Auto-detects facts and saves them
```python
# Regex patterns match natural language:
#   "my name is X"     → stores "name: X"
#   "i work at X"      → stores "work: X"
#   "i like X"         → stores "likes: X"
#   "i live in X"      → stores "location: X"
# To add new patterns:
patterns = [
    (r"my name is (\w+)", "name: {}"),     # regex, template
    (r"i work (?:at|for) (.+?)(?:\.|$)", "work: {}"),
]
# Add your own: (r"regex with (capture group)", "label: {}")
# The {} gets replaced with the captured text
# Saved via rag.add_note() to knowledge/notes.md
```

**`auto_search(text, rag)`** — Searches memory when questions detected
```python
# Triggers on: what, who, where, my, remember, know
# Extracts keywords (words >3 chars, not in stopwords)
# Searches RAG for each keyword (max 3)
# Returns matched context string or ""
# To modify triggers: edit memory_triggers list
# To modify filtering: edit stopwords set
memory_triggers = ["what", "who", "where", "my", "remember", "know"]
```

**`main()`** — The CLI loop
```python
# 1. Parse args (--brain, --no-voice, --list-brains)
# 2. Load brain via get_brain()
# 3. Init RAG search and Session
# 4. Print banner, startup voice
# 5. Loop:
#    - Read input
#    - Check for commands (exit, model, brain, remember, load, etc)
#    - detect_and_store() → save facts
#    - auto_search() → find relevant memory
#    - Build context: SYSTEM_PROMPT + RAG context + history + input
#    - brain.chat(context) → get response
#    - speak(response) → voice output
# To add a new command: add an if block after the existing ones
if user_input.lower() == "your_command":
    # do something
    continue
```

---

### CONFIG — Brain Factory (`georgebot/config.py`)

**`_load_env()`** — Reads .env file into os.environ
```python
# Reads key=value pairs, skips comments (#) and blank lines
# Uses setdefault() so real env vars take priority over .env
# To add new keys: just add them to .env, access with os.environ.get()
```

**`get_brain(brain_type)`** — Returns the right brain client
```python
# "ollama" → OllamaBrain(model=OLLAMA_MODEL)
# "grok"   → GrokBrain(api_key=GROK_API_KEY)
# To add a new brain:
# 1. Create clients/newbrain.py with class that extends BaseBrain
# 2. Add elif here: elif brain_type == "newbrain": return NewBrain()
# 3. Add to argparse choices in georgebot.py
```

**`speak(text)`** — Pipes text to TalkyTalk
```python
# Calls: ~/georgebot-venv/bin/python ~/talkytalk/talkytalk.py "text"
# To modify: change venv path or talkytalk path
# TALKYTALK_PATH is set at top of file
```

---

### Writing a New Function — Pattern

```python
# Every function in the machine follows this pattern:
# 1. Take simple inputs (text, path, config value)
# 2. Do one thing
# 3. Return a simple output (string, bool, list)

# Example: add a new text filter to the voice pipeline
def add_echo(text):
    """Repeat last word for dramatic effect"""
    words = text.split()
    if words:
        last = words[-1].rstrip('.!?')
        text += f"... {last}."
    return text

# Then insert it into speak() pipeline in talkytalk.py:
# text = expand_slang(text)
# text = filter_text(text)
# text = punch_text(text)
# text = add_echo(text)     ← new step
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
