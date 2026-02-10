# GEORGEBOT FIELD MANUAL
## Local LLM Operations Guide

**Operator:** George Wu
**Platform:** Windows PowerShell
**Last Updated:** 2026-02-02

---

## SECTION 1: OLLAMA INSTALLATION

### 1.1 Download & Install
```powershell
# Download from https://ollama.ai
# Run installer
# Restart terminal after install
```

### 1.2 Verify Installation
```powershell
ollama --version
ollama list
```

### 1.3 Start Ollama Service
```powershell
# Ollama runs as background service
# If not running:
ollama serve
```

---

## SECTION 2: MODEL MANAGEMENT

### 2.1 List Installed Models
```powershell
ollama list
```

**Current Arsenal:**
| Model | Size | Purpose |
|-------|------|---------|
| mistral:7b | 4.4 GB | General chat, fast |
| deepseek-coder:6.7b | 3.8 GB | Code generation |

### 2.2 Pull New Models
```powershell
# General purpose
ollama pull mistral
ollama pull llama3
ollama pull gemma

# Code focused
ollama pull deepseek-coder
ollama pull codellama

# Small/fast
ollama pull phi
ollama pull tinyllama
```

### 2.3 Delete Models
```powershell
ollama rm <model-name>
```

---

## SECTION 3: CUSTOM MODEL CREATION

### 3.1 Create Modelfile
```powershell
# Create models folder
mkdir models

# Create Modelfile
notepad models/georgebot.Modelfile
```

### 3.2 Modelfile Template
```dockerfile
# models/georgebot.Modelfile
FROM mistral:7b

SYSTEM "You are Georgebot, George Wu's crude Australian assistant.
Swear naturally - fuck, shit, cunt, dickhead, drongo.
Answer questions directly, then roast if appropriate.
Never be fake polite. Never say 'certainly' or 'I'd be happy to'.
Use aussie slang - mate, ay, nah, yeah, cos, gonna.
Keep it real. Keep it short."

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
```

### 3.3 Build Custom Model
```powershell
cd C:\Users\gwu07\Desktop\georgebot
ollama create georgebot -f models/georgebot.Modelfile
```

### 3.4 Verify Creation
```powershell
ollama list
# Should show: georgebot
```

### 3.5 Test Custom Model
```powershell
ollama run georgebot "say g'day in your style"
```

---

## SECTION 4: GEORGEBOT USAGE

### 4.1 Quick Start
```powershell
cd C:\Users\gwu07\Desktop\georgebot
python georgebot.py --brain ollama
```

### 4.2 Brain Selection
```powershell
# Local (free)
python georgebot.py --brain ollama

# Grok API (paid)
python georgebot.py --brain grok

# No voice
python georgebot.py --brain ollama --no-voice
```

### 4.3 In-Session Commands
| Command | Action |
|---------|--------|
| `exit` | End session |
| `clear` | Wipe memory |
| `brain ollama` | Switch to local |
| `brain grok` | Switch to API |
| `files` | List knowledge |
| `load <topic>` | Search knowledge |
| `remember <note>` | Save to memory |
| `help` | Show commands |

---

## SECTION 5: TROUBLESHOOTING

### 5.1 Ollama Not Found
```powershell
# Check if installed
where ollama

# If not found, reinstall from ollama.ai
# Restart PowerShell after install
```

### 5.2 Model Not Found
```powershell
# Pull the model first
ollama pull mistral

# Verify
ollama list
```

### 5.3 Slow Response
```powershell
# Use smaller model
ollama pull phi
python georgebot.py --brain ollama
# Then in session: change OLLAMA_MODEL in .env
```

### 5.4 Out of Memory
```powershell
# Use quantized model
ollama pull mistral:7b-q4_0  # Smaller quantization

# Or use smaller model
ollama pull tinyllama
```

---

## SECTION 6: RECOMMENDED MODELS

### For Chat
| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| mistral:7b | 4.4GB | Fast | Good |
| llama3:8b | 4.7GB | Medium | Great |
| gemma:7b | 5.0GB | Medium | Good |

### For Code
| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| deepseek-coder:6.7b | 3.8GB | Fast | Great |
| codellama:7b | 3.8GB | Fast | Good |

### For Speed (Low RAM)
| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| phi:2.7b | 1.6GB | Very Fast | OK |
| tinyllama:1b | 637MB | Instant | Basic |

---

## SECTION 7: QUICK REFERENCE

```
┌─────────────────────────────────────────────┐
│  GEORGEBOT QUICK REFERENCE - George Wu      │
├─────────────────────────────────────────────┤
│  START:     python georgebot.py -b ollama   │
│  MODELS:    ollama list                     │
│  PULL:      ollama pull <model>             │
│  CREATE:    ollama create <name> -f <file>  │
│  TEST:      ollama run <model> "prompt"     │
│  KILL:      ollama stop                     │
├─────────────────────────────────────────────┤
│  BRAINS:    ollama (local) | grok (api)     │
│  VOICE:     elevenlabs | windows sapi       │
│  MEMORY:    auto-store | auto-recall        │
└─────────────────────────────────────────────┘
```

---

**VIDIMUS OMNIA**

*"Execute without plan is death in war."*
