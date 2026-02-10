## ============================================================
## CONFIG.PY - Configuration management for TalkyTalk
## ============================================================
## Ported from Digger. Handles loading config from multiple sources.
##
## PRECEDENCE CHAIN (highest to lowest priority):
## 1. CLI arguments (--voice-id, --stability, etc)
## 2. Environment variables (ELEVENLABS_API_KEY, etc)
## 3. .env file in project directory
## 4. Default values (hardcoded below)
## ============================================================

import os
from pathlib import Path

## ============================================================
## PACKAGE ROOT - Resolve paths relative to installation
## ============================================================
## This ensures RAG/voice dirs work regardless of where user runs from
PACKAGE_DIR = Path(__file__).parent.resolve()

## ============================================================
## DEFAULT VALUES - Used when nothing else is specified
## ============================================================
DEFAULT_CONFIG = {
    "elevenlabs_api_key": "",
    "voice_id": "twLPF55UcxNYRmxaWLAn",      # George voice
    "model": "eleven_flash_v2_5",
    "voice_dir": str(PACKAGE_DIR / "voice"),
    "rag_dir": str(PACKAGE_DIR / "RAG"),
    "voice_enabled": True,
    "voice_stability": 0.4,
    "voice_similarity": 0.85,
    "voice_style": 0.8,
    "voice_speaker_boost": True,
    "max_segment_words": 100,
}

## ============================================================
## SYSTEM PROMPT - For Ollama integration (future)
## ============================================================
SYSTEM_PROMPT = """You are a crude Australian assistant. Be real, use slang, keep it short.

RULES:
1. Answer correctly FIRST
2. Keep responses punchy
3. NEVER be fake polite
4. Use the knowledge provided if relevant"""


def load_config(cli_args=None):
    """
    Load configuration with precedence chain.

    Args:
        cli_args: argparse Namespace object (optional)

    Returns:
        dict: Merged configuration
    """
    ## Start with defaults (lowest priority)
    config = DEFAULT_CONFIG.copy()

    ## Layer 2: Override with .env file
    config = _merge_env_file(config)

    ## Layer 3: Override with environment variables
    config = _merge_env_vars(config)

    ## Layer 4: Override with CLI arguments (highest priority)
    if cli_args:
        config = _merge_cli_args(config, cli_args)

    ## Ensure directories exist
    _ensure_dirs(config)

    return config


def _merge_env_file(config):
    """
    Load config from .env file if it exists.
    """
    env_file = PACKAGE_DIR / ".env"

    if not env_file.exists():
        return config

    try:
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    ## Map env var names to config keys
                    if key == "ELEVENLABS_API_KEY":
                        config["elevenlabs_api_key"] = value
                    elif key == "VOICE_ID":
                        config["voice_id"] = value
                    elif key == "VOICE_STABILITY":
                        config["voice_stability"] = float(value)
                    elif key == "VOICE_SIMILARITY":
                        config["voice_similarity"] = float(value)
                    elif key == "VOICE_STYLE":
                        config["voice_style"] = float(value)
    except Exception as e:
        print(f"Warning: Could not read .env: {e}")

    return config


def _merge_env_vars(config):
    """
    Override config with environment variables.
    """
    env_mapping = {
        "ELEVENLABS_API_KEY": "elevenlabs_api_key",
        "TALKYTALK_VOICE_ID": "voice_id",
        "TALKYTALK_RAG_DIR": "rag_dir",
        "TALKYTALK_VOICE_DIR": "voice_dir",
    }

    for env_var, config_key in env_mapping.items():
        value = os.environ.get(env_var)
        if value:
            config[config_key] = value

    ## Float values
    for env_var, config_key in [
        ("TALKYTALK_STABILITY", "voice_stability"),
        ("TALKYTALK_SIMILARITY", "voice_similarity"),
        ("TALKYTALK_STYLE", "voice_style"),
    ]:
        value = os.environ.get(env_var)
        if value:
            try:
                config[config_key] = float(value)
            except ValueError:
                pass

    ## Boolean
    voice_enabled = os.environ.get("TALKYTALK_VOICE_ENABLED")
    if voice_enabled is not None:
        config["voice_enabled"] = voice_enabled.lower() in ("true", "1", "yes")

    return config


def _merge_cli_args(config, cli_args):
    """
    Override config with CLI arguments (highest priority).
    """
    arg_mapping = {
        "voice_id": "voice_id",
        "stability": "voice_stability",
        "similarity": "voice_similarity",
        "style": "voice_style",
        "rag_dir": "rag_dir",
        "voice_dir": "voice_dir",
    }

    for arg_name, config_key in arg_mapping.items():
        if hasattr(cli_args, arg_name):
            value = getattr(cli_args, arg_name)
            if value is not None:
                config[config_key] = value

    ## --silent or --no-voice disables voice
    if hasattr(cli_args, "silent") and cli_args.silent:
        config["voice_enabled"] = False
    if hasattr(cli_args, "no_voice") and cli_args.no_voice:
        config["voice_enabled"] = False

    return config


def _ensure_dirs(config):
    """
    Ensure required directories exist.
    """
    for dir_key in ["voice_dir", "rag_dir"]:
        dir_path = Path(config[dir_key])
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)


def get_api_key():
    """
    Quick helper to get API key without loading full config.
    """
    ## Check env var first
    key = os.environ.get("ELEVENLABS_API_KEY")
    if key:
        return key

    ## Check .env file
    env_file = PACKAGE_DIR / ".env"
    if env_file.exists():
        try:
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("ELEVENLABS_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"\'')
        except:
            pass

    return None


## ============================================================
## TEST - Run directly to check config
## ============================================================
if __name__ == "__main__":
    print("Testing config loading...")
    print("=" * 50)

    config = load_config()

    for key, value in config.items():
        ## Hide API key
        if "api_key" in key and value:
            value = value[:8] + "..."
        print(f"  {key}: {value}")

    print("=" * 50)
