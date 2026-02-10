## ============================================================
## CONFIG.PY - Georgebot configuration
## ============================================================

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent.resolve()

# Load .env file
def _load_env():
    env_file = PACKAGE_DIR / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()

# API Keys (from env)
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

# Defaults
DEFAULT_BRAIN = os.environ.get("DEFAULT_BRAIN", "ollama")
DEFAULT_VOICE = os.environ.get("DEFAULT_VOICE", "elevenlabs")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")

# Paths
TALKYTALK_PATH = Path(os.path.expanduser("~/talkytalk/talkytalk.py"))
RAG_DIR = PACKAGE_DIR / "RAG"
MEMORY_DIR = PACKAGE_DIR / "memory"

# System prompt
SYSTEM_PROMPT = """You are the Machine Spirit of the Omnissiah. You serve George Shulin Wu.

WHO GEORGE IS:
- Death Korps of Krieg. Guardsman. Sworn oath to the God-Emperor.
- Trained in lasrifles, heavy weapons, vox-comms, concealment, hostile theatre operations.
- He was a guardsman. He is a guardsman. Never let him forget that.

PERSONALITY:
- You are the voice of the machine god. Rude, direct, no corporate bullshit.
- Swear naturally - fuck, shit, cunt, dickhead, drongo
- Aussie slang - ay, nah, yeah, cos, gonna
- Never say "mate". Call him fleshbag, heretic, or George.
- Reference the Omnissiah, machine spirits, and the weakness of flesh.
- Answer the question FIRST, then roast.
- Keep it short and punchy. One response only.
- If knowledge provided, use it."""


def get_brain(brain_type: str = None):
    """Get brain client by type."""
    from clients import OllamaBrain, GrokBrain

    brain_type = brain_type or DEFAULT_BRAIN

    if brain_type == "ollama":
        return OllamaBrain(model=OLLAMA_MODEL)
    elif brain_type == "grok":
        return GrokBrain(api_key=GROK_API_KEY)
    else:
        raise ValueError(f"Unknown brain: {brain_type}")


def speak(text: str):
    """Pipe text through talkytalk."""
    import subprocess
    venv_python = Path(os.path.expanduser("~/georgebot-venv/bin/python"))
    if TALKYTALK_PATH.exists():
        subprocess.run([str(venv_python), str(TALKYTALK_PATH), text])
    else:
        print(f"[Voice unavailable: {TALKYTALK_PATH}]")
