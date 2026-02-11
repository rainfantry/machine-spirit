#!/usr/bin/env python3
"""
TalkyTalk - Voice Pipeline System
Features:
- ElevenLabs primary TTS with NON-BLOCKING playback
- Audio plays in detached background process (survives script exit)
- Fast math-based duration estimation (no slow MediaPlayer probe)
- Pipeline: generate -> fire playback -> exit immediately
- espeak-ng fallback (Linux) / Windows SAPI fallback
- Segmented audio for long text
- Kills previous playback on new call (no overlap)
"""

import subprocess
import sys
import os
import socket
import re
import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Config - API key from environment or .env file
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

ELEVENLABS_API_KEY = load_api_key()
ELEVENLABS_VOICE_ID = "weA4Q36twV5kwSaTEL0Q"
ELEVENLABS_MODEL = "eleven_turbo_v2_5"  # Faster
VOICE_DIR = os.path.join(os.path.expanduser("~"), ".talkytalk", "voice")
PID_FILE = os.path.join(os.path.expanduser("~"), ".talkytalk", "player.pid")
MAX_SEGMENT_WORDS = 100  # Split long text into segments

# Voice settings - Machine Spirit of the Omnissiah
VOICE_STABILITY = 0.42         # Tighter than before — expressive but not erratic. Realism.
VOICE_SIMILARITY = 0.78        # Voice-faithful. The spirit knows EXACTLY its voice.
VOICE_STYLE = 0.92             # Maximum gravitas. Emotion per syllable.
VOICE_SPEAKER_BOOST = True     # Clarity


def is_online():
    """Check internet connectivity"""
    try:
        socket.create_connection(("api.elevenlabs.io", 443), timeout=2)
        return True
    except OSError:
        return False


## Slang expansion - so TTS pronounces shit right
SLANG_MAP = {
    # vulgar
    r'\bfkn\b': 'fucken',
    r'\bfk\b': 'fuck',
    r'\bfkd\b': 'fucked',
    r'\bfkr\b': 'fucker',
    r'\bfks\b': 'fucks',
    r'\bmf\b': 'motherfucker',
    r'\bmfer\b': 'motherfucker',
    r'\bbs\b': 'bullshit',
    r'\bpos\b': 'piece of shit',
    r'\bstfu\b': 'shut the fuck up',
    r'\bgtfo\b': 'get the fuck out',
    r'\bwtf\b': 'what the fuck',
    r'\bdmn\b': 'damn',
    r'\bffs\b': 'for fucks sake',
    r'\bjfc\b': 'jesus fucken christ',
    r'\bfml\b': 'fuck my life',
    r'\bsht\b': 'shit',
    r'\bsh1t\b': 'shit',
    r'\bass\b': 'ass',
    r'\ba\$\$\b': 'ass',
    r'\bbstd\b': 'bastard',
    r'\bcnt\b': 'cunt',
    r'\bdck\b': 'dick',
    r'\bdkhead\b': 'dickhead',
    r'\bfag\b': 'fag',
    r'\bpoof\b': 'poof',
    r'\bdrongo\b': 'drongo',
    # casual
    r'\bu\b': 'you',
    r'\bur\b': 'your',
    r'\bya\b': 'yeah',
    r'\byh\b': 'yeah',
    r'\bcos\b': 'cause',
    r'\bcoz\b': 'cause',
    r'\bwanna\b': 'wanna',
    r'\bgonna\b': 'gonna',
    r'\bgotta\b': 'gotta',
    r'\blem+e\b': 'let me',
    r'\bw/\b': 'with',
    r'\bw/o\b': 'without',
    r'\bidk\b': 'I dunno',
    r'\bimo\b': 'in my opinion',
    r'\btbh\b': 'to be honest',
    r'\bngl\b': 'not gonna lie',
    r'\brn\b': 'right now',
    r'\baf\b': 'as fuck',
    r'\blol\b': 'lol',
    r'\blmao\b': 'lmao',
    r'\bsmh\b': 'shaking my head',
    r'\bbtw\b': 'by the way',
    r'\bpls\b': 'please',
    r'\bthx\b': 'thanks',
    r'\bty\b': 'thank you',
    r'\bnp\b': 'no problem',
    r'\bk\b': 'okay',
    r'\bmk\b': 'mmkay',
    r'\baight\b': 'alright',
    r'\baint\b': "ain't",
    r'\binnit\b': "isn't it",
    r'\baye\b': 'ay',
}


def expand_slang(text):
    """Expand slang/abbreviations for proper TTS pronunciation"""
    for pattern, replacement in SLANG_MAP.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def filter_text(text):
    """Filter text for TTS - remove code blocks, markdown, symbols"""
    # Remove code blocks (```...```)
    text = re.sub(r'```[\s\S]*?```', '', text)

    # Remove inline code (`...`)
    text = re.sub(r'`[^`]*`', '', text)

    # Remove bold/italic markers but keep text
    text = re.sub(r'\*\*([^*]*)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]*)\*', r'\1', text)
    text = re.sub(r'__([^_]*)__', r'\1', text)
    text = re.sub(r'_([^_]*)_', r'\1', text)

    # Filter lines that look like code
    lines = text.split('\n')
    filtered = []
    for line in lines:
        if re.search(r'^\s*(def |class |import |from |print\(|if |for |while |return )', line):
            continue
        if re.search(r'[{};\[\]]=', line):
            continue
        filtered.append(line)

    text = '\n'.join(filtered)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def punch_text(text):
    """Add aggressive punctuation to manipulate voice tone"""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    punched = []

    for s in sentences:
        s = s.strip()
        if not s:
            continue

        # Short punchy sentences get exclamation
        words = s.split()
        if len(words) <= 4 and not s.endswith(('!', '?')):
            s = s.rstrip('.') + '!'

        # Add emphasis pause with comma after first word in longer sentences
        elif len(words) > 6 and ',' not in s[:20]:
            words[0] = words[0] + ','
            s = ' '.join(words)

        # Statements over 8 words that end flat get period emphasis
        if len(words) > 8 and s.endswith('.'):
            s = s[:-1] + '...'

        punched.append(s)

    return ' '.join(punched)


def speak_local(text):
    """Local TTS fallback - espeak-ng on Linux, SAPI on Windows"""
    if sys.platform == "win32":
        ps_script = f'''
        Add-Type -AssemblyName System.Speech
        $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $synth.Rate = 1
        $synth.Speak("{text.replace('"', "'")}")
        '''
        subprocess.run(["powershell", "-Command", ps_script], shell=False)
    else:
        subprocess.run(["espeak-ng", "-s", "160", text], shell=False)


def estimate_duration(word_count, file_size_bytes):
    """Fast math-based duration estimate — no file probing, no PowerShell overhead.
    Replaces the old get_audio_duration() which spawned a PowerShell MediaPlayer
    process and waited 500ms+ just to read the file length.
    """
    # ~2.8 words/sec for this voice at current settings
    word_est = word_count / 2.8
    # ElevenLabs turbo MP3 averages ~48kbps = ~6000 bytes/sec
    size_est = file_size_bytes / 6000
    # Weighted blend: word count is more reliable, file size as sanity check
    # +1s buffer so audio doesn't get cut off
    return max(int(word_est * 0.6 + size_est * 0.4) + 1, 2)


def kill_previous_playback():
    """Kill any still-playing audio from a previous talkytalk call.
    Reads PID from file, kills that process tree, cleans up.
    Prevents old audio from overlapping new speech.
    """
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                old_pid = int(f.read().strip())
            if sys.platform == "win32":
                # /T = kill process tree, /F = force
                subprocess.run(
                    ["taskkill", "/PID", str(old_pid), "/T", "/F"],
                    capture_output=True, shell=False
                )
            else:
                import signal
                os.kill(old_pid, signal.SIGTERM)
            os.remove(PID_FILE)
    except (ValueError, ProcessLookupError, OSError, PermissionError):
        # Process already dead or PID file corrupt — ignore
        try:
            os.remove(PID_FILE)
        except OSError:
            pass


def generate_elevenlabs(text, segment_num=0):
    """Generate audio via ElevenLabs API.
    ONLY generates and saves the file. Does NOT play.
    Returns (path, duration_est, word_count, file_size) or (None, 0, 0, 0) on failure.
    """
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import VoiceSettings

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id=ELEVENLABS_MODEL,
            voice_settings=VoiceSettings(
                stability=VOICE_STABILITY,
                similarity_boost=VOICE_SIMILARITY,
                style=VOICE_STYLE,
                use_speaker_boost=VOICE_SPEAKER_BOOST
            )
        )

        os.makedirs(VOICE_DIR, exist_ok=True)
        # Timestamp prevents conflicts with concurrent/overlapping calls
        ts = int(time.time() * 1000)
        path = os.path.join(VOICE_DIR, f"seg_{ts}_{segment_num}.mp3")
        with open(path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        file_size = os.path.getsize(path)
        word_count = len(text.split())
        duration = estimate_duration(word_count, file_size)

        return path, duration, word_count, file_size
    except Exception as e:
        print(f"[TalkyTalk] ElevenLabs error: {e}", file=sys.stderr)
        return None, 0, 0, 0


def play_detached(audio_segments):
    """Play audio segments sequentially in a FULLY DETACHED background process.
    The process survives after talkytalk.py exits. Audio keeps playing
    while Claude returns control and outputs text.

    audio_segments: list of (path, duration_seconds) tuples
    Writes PID to file so next call can kill it if needed.
    """
    if not audio_segments:
        return

    os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)

    if sys.platform == "win32":
        # Build PowerShell script that plays each segment in sequence
        ps_lines = ["Add-Type -AssemblyName presentationCore"]
        for path, duration in audio_segments:
            # Normalize path separators for PowerShell
            ps_path = path.replace('/', '\\')
            ps_lines.append(
                f"$p = New-Object System.Windows.Media.MediaPlayer; "
                f"$p.Open('{ps_path}'); "
                f"Start-Sleep -Milliseconds 100; "
                f"$p.Play(); "
                f"Start-Sleep -Seconds {duration}; "
                f"$p.Stop(); $p.Close()"
            )

        # Write script to file (avoids command-line length limits)
        script_path = os.path.join(VOICE_DIR, "play.ps1")
        with open(script_path, 'w') as f:
            f.write('\n'.join(ps_lines))

        # CREATE_NO_WINDOW keeps audio session alive (DETACHED_PROCESS kills it)
        # CREATE_NEW_PROCESS_GROUP lets it survive parent exit
        proc = subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass",
             "-File", script_path],
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            close_fds=True
        )
        # Save PID so next call can kill this if needed
        with open(PID_FILE, 'w') as f:
            f.write(str(proc.pid))
    else:
        # Linux: chain mpv commands
        cmd_parts = []
        for path, _ in audio_segments:
            cmd_parts.append(f"mpv --no-video --really-quiet '{path}'")
        full_cmd = " && ".join(cmd_parts)
        proc = subprocess.Popen(
            ["bash", "-c", full_cmd],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        with open(PID_FILE, 'w') as f:
            f.write(str(proc.pid))


def color(val):
    """Color intensity for terminal output: red=low, yellow=mid, green=high"""
    if val <= 0.3: return f"\033[91m{val}\033[0m"
    elif val <= 0.6: return f"\033[93m{val}\033[0m"
    else: return f"\033[92m{val}\033[0m"


def speak(text, force_local=False):
    """Main speak function — NON-BLOCKING pipeline.

    1. Kill any previous playback
    2. Process text (slang, filter, punch)
    3. Generate all audio segments (API calls — fast, ~1-2s each)
    4. Fire detached background player for ALL segments
    5. Print stats and EXIT IMMEDIATELY

    Audio continues playing in background after script exits.
    Claude gets control back and can output text while user hears voice.
    """
    # Process text for TTS
    text = expand_slang(text)   # fkn -> fucken, u -> you, etc
    text = filter_text(text)    # Remove code/markdown
    text = punch_text(text)     # Add aggressive punctuation
    if not text:
        return "empty"

    if force_local or not is_online():
        print("[TalkyTalk] Using local TTS")
        speak_local(text)
        return "local"

    # Kill any still-playing audio from previous call
    kill_previous_playback()

    # Segment long text
    segments = segment_text(text)
    audio_files = []  # (path, duration) tuples
    total_words = 0
    total_size = 0
    total_duration = 0
    gen_start = time.time()

    for i, segment in enumerate(segments):
        path, duration, words, file_size = generate_elevenlabs(segment, i)

        if path is None:
            print(f"[TalkyTalk] Seg {i} failed — local fallback")
            speak_local(segment)
            continue

        audio_files.append((path, duration))
        total_words += words
        total_size += file_size
        total_duration += duration

    gen_time = time.time() - gen_start

    if audio_files:
        # Fire detached playback — returns immediately
        play_detached(audio_files)

        # Stats
        seg_count = len(audio_files)
        seg_label = f"{seg_count} seg{'s' if seg_count > 1 else ''}"
        print(f"[TalkyTalk] {total_words}w | {total_size/1024:.1f}KB | ~{total_duration}s audio | {seg_label} | gen:{gen_time:.1f}s")
        print(f"  Voice: {ELEVENLABS_VOICE_ID[:8]}... | Stab: {color(VOICE_STABILITY)} | Sim: {color(VOICE_SIMILARITY)} | Style: {color(VOICE_STYLE)}")
        print(f"  Playback: DETACHED (audio continues after exit)")

    return "elevenlabs"


def segment_text(text, max_words=MAX_SEGMENT_WORDS):
    """Split text into speakable segments at sentence boundaries"""
    words = text.split()
    if len(words) <= max_words:
        return [text]

    segments = []
    current = []

    for word in words:
        current.append(word)
        # Split at sentence end or max words
        if len(current) >= max_words or word.endswith(('.', '!', '?')):
            if current:
                segments.append(' '.join(current))
                current = []

    if current:
        segments.append(' '.join(current))

    return segments


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: talkytalk.py <text> [--local] [--silent] [--block]")
        print("       talkytalk.py --test")
        print("       talkytalk.py --kill")
        print("Flags:")
        print("  --silent   Print only, no voice (saves API cost)")
        print("  --local    Force local TTS fallback (espeak-ng / SAPI)")
        print("  --block    Wait for audio to finish before exiting (old behavior)")
        print("  --kill     Kill any currently playing audio and exit")
        sys.exit(1)

    if sys.argv[1] == "--test":
        print("[TalkyTalk] Testing system...")
        online = is_online()
        print(f"  Online: {online}")
        speak("TalkyTalk system test. " + ("ElevenLabs connected." if online else "Offline mode, using local TTS."))
        print("[TalkyTalk] Test complete.")
        sys.exit(0)

    if sys.argv[1] == "--kill":
        kill_previous_playback()
        print("[TalkyTalk] Killed previous playback.")
        sys.exit(0)

    flags = ["--local", "--windows", "--silent", "--block"]
    force_local = "--local" in sys.argv or "--windows" in sys.argv
    silent_mode = "--silent" in sys.argv
    block_mode = "--block" in sys.argv
    text = " ".join(arg for arg in sys.argv[1:] if arg not in flags)

    if silent_mode:
        # Just print, no voice
        filtered = filter_text(text)
        print(f"[TalkyTalk] Silent: {filtered}")
        print(f"[TalkyTalk] Used: silent (0 API cost)")
    elif block_mode:
        # Old blocking behavior — wait for audio to finish
        engine = speak(text, force_local=force_local)
        # If elevenlabs, wait for the detached process to finish
        if engine == "elevenlabs" and os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, 'r') as f:
                    pid = int(f.read().strip())
                if sys.platform == "win32":
                    # Poll until process exits
                    while True:
                        result = subprocess.run(
                            ["tasklist", "/FI", f"PID eq {pid}"],
                            capture_output=True, text=True, shell=False
                        )
                        if str(pid) not in result.stdout:
                            break
                        time.sleep(0.5)
            except (ValueError, OSError):
                pass
        print(f"[TalkyTalk] Used: {engine} (blocking)")
    else:
        engine = speak(text, force_local=force_local)
        print(f"[TalkyTalk] Used: {engine}")


if __name__ == "__main__":
    main()
