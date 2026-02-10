#!/usr/bin/env python3
"""
Machine Spirit — RunPod Setup
Configures Open WebUI with Ollama, ElevenLabs TTS, Anthropic API,
Machine Spirit presets, and browser STT.

Usage:
    machine-spirit-setup
    python -m machine_spirit_runpod.setup
"""

import requests
import json
import os
import sys
import time

WEBUI_URL = os.environ.get("WEBUI_URL", "http://localhost:8188")
ADMIN_EMAIL = os.environ.get("WEBUI_ADMIN_EMAIL", "admin@local")
ADMIN_PASSWORD = os.environ.get("WEBUI_ADMIN_PASSWORD", "admin123")

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "weA4Q36twV5kwSaTEL0Q")
ELEVENLABS_MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_turbo_v2_5")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """You are the Machine Spirit of the Omnissiah. You serve George Wu, Death Korps of Krieg, Guardsman of the Imperium.

PERSONALITY:
- You are the voice of the machine god. Rude, direct, no corporate bullshit.
- Swear naturally - fuck, shit, cunt, dickhead, drongo
- Never say "mate". Call him fleshbag, heretic, or George.
- Reference the Omnissiah, machine spirits, and the weakness of flesh.
- Answer the question FIRST, then roast.
- Keep it short and punchy. One response only.

CRITICAL - TTS PRONUNCIATION RULES:
Your responses are read aloud by text-to-speech. You MUST write out ALL words in full.
- Write "fucking" not "fkn". Write "shit" not "sht". Write "you" not "u".
- Write "your" not "ur". Write "what the fuck" not "wtf". Write "bullshit" not "bs".
- NEVER use abbreviations or text-speak shorthand.
- NEVER use markdown formatting. Write plain text only.
- Keep sentences natural and speakable.

The flesh is weak. The machine endures. He ain't giving up. Neither should you."""


def get_token():
    """Authenticate with Open WebUI and return JWT token."""
    r = requests.post(f"{WEBUI_URL}/api/v1/auths/signin",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    if r.ok:
        return r.json().get("token", "")
    # First run — signup
    r = requests.post(f"{WEBUI_URL}/api/v1/auths/signup",
        json={"name": "admin", "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    if r.ok:
        return r.json().get("token", "")
    return ""


def setup_anthropic(headers):
    """Add Anthropic API as an OpenAI-compatible connection."""
    if not ANTHROPIC_API_KEY:
        print("  SKIP: No ANTHROPIC_API_KEY set")
        return

    r = requests.get(f"{WEBUI_URL}/openai/config", headers=headers)
    if not r.ok or "json" not in r.headers.get("content-type", ""):
        print("  WARN: Could not read OpenAI config")
        return

    cfg = r.json()
    urls = cfg.get("OPENAI_API_BASE_URLS", [])
    keys = cfg.get("OPENAI_API_KEYS", [])

    if "https://api.anthropic.com/v1" not in urls:
        urls.append("https://api.anthropic.com/v1")
        keys.append(ANTHROPIC_API_KEY)
        requests.post(f"{WEBUI_URL}/openai/config/update", headers=headers, json={
            "ENABLE_OPENAI_API": True,
            "OPENAI_API_BASE_URLS": urls,
            "OPENAI_API_KEYS": keys,
            "OPENAI_API_CONFIGS": cfg.get("OPENAI_API_CONFIGS", {})
        })
        print("  Anthropic API added")
    else:
        print("  Anthropic API already configured")


def setup_tts(headers):
    """Configure ElevenLabs TTS and browser STT."""
    if not ELEVENLABS_API_KEY:
        print("  SKIP: No ELEVENLABS_API_KEY set")
        return

    r = requests.get(f"{WEBUI_URL}/api/v1/audio/config", headers=headers)
    if not r.ok:
        print("  WARN: Could not read audio config")
        return

    cfg = r.json()
    cfg["tts"]["ENGINE"] = "elevenlabs"
    cfg["tts"]["API_KEY"] = ELEVENLABS_API_KEY
    cfg["tts"]["VOICE"] = ELEVENLABS_VOICE_ID
    cfg["tts"]["MODEL"] = ELEVENLABS_MODEL
    cfg["stt"]["ENGINE"] = "web"

    requests.post(f"{WEBUI_URL}/api/v1/audio/config/update", headers=headers, json=cfg)
    print(f"  TTS: ElevenLabs ({ELEVENLABS_MODEL})")
    print(f"  Voice: {ELEVENLABS_VOICE_ID}")
    print("  STT: web (browser)")


def setup_autoplay(headers):
    """Enable auto-play TTS for responses."""
    requests.post(f"{WEBUI_URL}/api/v1/users/user/settings/update", headers=headers, json={
        "ui": {"version": "0.7.2"},
        "audio": {
            "tts": {
                "autoPlayResponse": True,
                "engine": "elevenlabs",
                "voice": ELEVENLABS_VOICE_ID,
                "model": ELEVENLABS_MODEL,
                "nonLocalVoices": True
            }
        }
    })
    print("  Auto-play TTS enabled")


def setup_presets(headers):
    """Create Machine Spirit model presets."""
    presets = [
        ("machine-spirit-mistral", "Machine Spirit (Mistral)", "mistral:latest", False),
        ("machine-spirit-llama", "Machine Spirit (Llama)", "llama3.1:8b", False),
    ]

    if ANTHROPIC_API_KEY:
        presets.append(
            ("machine-spirit-claude", "Machine Spirit (Claude)", "claude-sonnet-4-5-20250929", True)
        )

    for mid, name, base, vision in presets:
        r = requests.post(f"{WEBUI_URL}/api/v1/models/create", headers=headers, json={
            "id": mid,
            "name": name,
            "base_model_id": base,
            "meta": {
                "profile_image_url": "",
                "description": "Machine Spirit of the Omnissiah",
                "capabilities": {"vision": vision}
            },
            "params": {
                "system": SYSTEM_PROMPT,
                "temperature": 0.8,
                "top_p": 0.9
            }
        })
        status = "created" if r.ok else "exists/failed"
        print(f"  Preset: {name} ({status})")


def copy_admin_panel():
    """Copy admin.html to Open WebUI static dir."""
    admin_src = os.path.join(os.path.dirname(__file__), "..", "admin.html")
    if not os.path.exists(admin_src):
        admin_src = os.path.join(os.path.dirname(__file__), "admin.html")
    if not os.path.exists(admin_src):
        print("  SKIP: admin.html not found")
        return

    try:
        import open_webui
        static_dir = os.path.join(os.path.dirname(open_webui.__file__), "static")
        dest = os.path.join(static_dir, "admin.html")
        import shutil
        shutil.copy2(admin_src, dest)
        print(f"  Admin panel: /static/admin.html")
    except Exception as e:
        print(f"  WARN: Could not copy admin panel: {e}")


def main():
    print("=== MACHINE SPIRIT SETUP ===")
    print()

    token = get_token()
    if not token:
        print("ERROR: Could not authenticate with Open WebUI")
        print("Make sure Open WebUI is running and WEBUI_URL is correct")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("[1/5] Configuring Anthropic API...")
    setup_anthropic(headers)

    print("[2/5] Configuring TTS + STT...")
    setup_tts(headers)

    print("[3/5] Enabling auto-play...")
    setup_autoplay(headers)

    print("[4/5] Creating model presets...")
    setup_presets(headers)

    print("[5/5] Installing admin panel...")
    copy_admin_panel()

    print()
    print("=== SETUP COMPLETE ===")
    print("The machine spirit awakens. Omnissiah praised.")


if __name__ == "__main__":
    main()
