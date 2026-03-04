"""
convo.py - Multi-voice conversation runner
Pre-generates ALL audio first, then plays as one seamless stream. No gaps.

Script file format:
    tts: Hello I am from Microsoft your computer is hacked.
    ms:  Oh thank god you called I was literally on the dunny.
    tts: This is very serious please pay now.
    ms:  Yeah nah.

    # lines starting with # are comments, blank lines ignored

Usage:
    convo scam.txt
    convo scam.txt --block      <- wait for full playback to finish
"""

import sys
import os
import time
import subprocess

# Add lib paths (same as talkytalk/machinespirit)
for _p in [r"C:\py\libs", r"C:\Users\veren\py_libs"]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import re

VOICES = {
    "tts": "dOdGri2hgsKdUEaU09Ct",   # poof aussie
    "ms":  "twLPF55UcxNYRmxaWLAn",   # machine spirit (me)
}

STABILITY  = 0.42
SIMILARITY = 0.78
STYLE      = 0.92

SLANG_MAP = {
    r'\bfkn\b':   'fucken',
    r'\bfk\b':    'fuck',
    r'\bfkd\b':   'fucked',
    r'\bfkr\b':   'fucker',
    r'\bfks\b':   'fucks',
    r'\bmf\b':    'motherfucker',
    r'\bbs\b':    'bullshit',
    r'\bpos\b':   'piece of shit',
    r'\bstfu\b':  'shut the fuck up',
    r'\bwtf\b':   'what the fuck',
    r'\bffs\b':   'for fucks sake',
    r'\bjfc\b':   'jesus fucken christ',
    r'\bu\b':     'you',
    r'\bur\b':    'your',
    r'\bya\b':    'you',
    r'\bnah\b':   'nah',
    r'\bmate\b':  'mate',
    r'\boi\b':    'oi',
}

def expand_slang(text):
    for pattern, replacement in SLANG_MAP.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

VOICE_DIR = os.path.join(os.path.expanduser("~"), ".talkytalk", "voice")
PID_FILE  = os.path.join(os.path.expanduser("~"), ".talkytalk", "player.pid")


def load_api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if key:
        return key
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("ELEVENLABS_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"\'')
    return None


def generate_segment(client, text, voice_id, index):
    text = expand_slang(text)
    """Call ElevenLabs API and save mp3. Returns (path, estimated_duration_sec)."""
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=STABILITY,
            similarity_boost=SIMILARITY,
            style=STYLE,
            use_speaker_boost=True,
        ),
    )
    os.makedirs(VOICE_DIR, exist_ok=True)
    path = os.path.join(VOICE_DIR, f"convo_{int(time.time()*1000)}_{index}.mp3")
    with open(path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    size  = os.path.getsize(path)
    words = len(text.split())
    dur   = max(int(words / 2.8 * 0.6 + (size / 6000) * 0.4) + 1, 2)
    return path, dur


def play_all(segments):
    """Build ONE powershell script for all segments and fire it detached.
    Cleans up mp3 files and the ps1 itself after playback finishes."""
    ps_lines = ["Add-Type -AssemblyName presentationCore"]
    for path, duration in segments:
        ps_path = path.replace("/", "\\")
        ps_lines.append(
            f"$p = New-Object System.Windows.Media.MediaPlayer; "
            f"$p.Open('{ps_path}'); "
            f"Start-Sleep -Milliseconds 100; "
            f"$p.Play(); "
            f"Start-Sleep -Seconds {duration}; "
            f"$p.Stop(); $p.Close()"
        )
    # cleanup — delete all mp3s and the script itself after playing
    for path, _ in segments:
        ps_path = path.replace("/", "\\")
        ps_lines.append(f"Remove-Item -Force '{ps_path}' -ErrorAction SilentlyContinue")
    script_path = os.path.join(VOICE_DIR, "convo_play.ps1")
    ps_lines.append(f"Remove-Item -Force '{script_path}' -ErrorAction SilentlyContinue")
    with open(script_path, "w") as f:
        f.write("\n".join(ps_lines))
    proc = subprocess.Popen(
        ["powershell", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass",
         "-File", script_path],
        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        close_fds=True,
    )
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    return proc.pid


def main():
    if len(sys.argv) < 2:
        print("Usage: convo <script.txt> [--block]")
        print("  script format:  tts: your text here")
        print("                  ms:  your text here")
        sys.exit(1)

    script_file = sys.argv[1]
    block_mode  = "--block" in sys.argv

    if not os.path.exists(script_file):
        print(f"[convo] File not found: {script_file}")
        sys.exit(1)

    # Parse script file
    lines = []
    with open(script_file, encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            for prefix in VOICES:
                if raw.lower().startswith(f"{prefix}:"):
                    text = raw[len(prefix)+1:].strip()
                    if text:
                        lines.append((prefix, VOICES[prefix], text))
                    break

    if not lines:
        print("[convo] No lines found. Use format:  tts: text  or  ms: text")
        sys.exit(1)

    # Pre-generate all audio
    print(f"[convo] Generating {len(lines)} lines...")
    client    = ElevenLabs(api_key=load_api_key())
    gen_start = time.time()
    segments  = []

    for i, (prefix, voice_id, text) in enumerate(lines):
        t0 = time.time()
        path, dur = generate_segment(client, text, voice_id, i)
        elapsed = time.time() - t0
        label = "tts" if prefix == "tts" else " ms"
        print(f"  [{i+1}/{len(lines)}] {label} | {len(text.split())}w | ~{dur}s | gen:{elapsed:.1f}s")
        segments.append((path, dur))

    gen_time = time.time() - gen_start
    total    = sum(d for _, d in segments)
    print(f"[convo] All generated in {gen_time:.1f}s | ~{total}s total audio | firing...")

    pid = play_all(segments)
    print(f"[convo] Playing (PID {pid})")

    if block_mode:
        while True:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True, text=True
            )
            if str(pid) not in result.stdout:
                break
            time.sleep(0.1)
        print("[convo] Done.")


if __name__ == "__main__":
    main()
