#!/usr/bin/env python3
"""
TalkyTalk - Voice Pipeline System
Features:
- ElevenLabs primary TTS
- espeak-ng fallback (Linux) / Windows SAPI fallback
- Segmented audio for long text
- Dynamic duration calculation
- Offline detection
"""

import subprocess
import sys
import os
import socket
import re
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
MAX_SEGMENT_WORDS = 100  # Split long text into segments

# Voice settings - Machine Spirit of the Omnissiah
VOICE_STABILITY = 0.35         # Controlled, deliberate
VOICE_SIMILARITY = 0.6         # The spirit knows its voice
VOICE_STYLE = 0.85             # Gravitas, not chaos
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

        # Questions stay questions
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


def get_audio_duration(path):
    """Get actual MP3 duration using ffprobe (Linux) or PowerShell (Windows)"""
    try:
        if sys.platform == "win32":
            result = subprocess.run([
                "powershell", "-Command",
                f"Add-Type -AssemblyName presentationCore; "
                f"$p = New-Object System.Windows.Media.MediaPlayer; "
                f"$p.Open('{path}'); "
                f"Start-Sleep -Milliseconds 500; "
                f"while(-not $p.NaturalDuration.HasTimeSpan) {{ Start-Sleep -Milliseconds 100 }}; "
                f"[int]$p.NaturalDuration.TimeSpan.TotalSeconds + 1"
            ], capture_output=True, text=True, shell=False)
            return int(result.stdout.strip())
        else:
            result = subprocess.run([
                "ffprobe", "-v", "quiet", "-show_entries",
                "format=duration", "-of", "csv=p=0", path
            ], capture_output=True, text=True, timeout=5)
            return int(float(result.stdout.strip())) + 1
    except:
        return 10  # Fallback


def speak_elevenlabs(text, segment_num=0):
    """ElevenLabs TTS with blocking playback"""
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

        # Save audio
        os.makedirs(VOICE_DIR, exist_ok=True)
        path = f"{VOICE_DIR}/segment_{segment_num}.mp3"
        with open(path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        # Get file size and duration
        file_size = os.path.getsize(path)
        duration = get_audio_duration(path)
        words = len(text.split())

        # Color intensity: red=low, yellow=mid, green=high
        def color(val):
            if val <= 0.3: return f"\033[91m{val}\033[0m"    # Red
            elif val <= 0.6: return f"\033[93m{val}\033[0m"  # Yellow
            else: return f"\033[92m{val}\033[0m"             # Green

        print(f"[TalkyTalk] {words}w | {file_size/1024:.1f}KB | {duration}s")
        print(f"  Voice: {ELEVENLABS_VOICE_ID[:8]}... | Stab: {color(VOICE_STABILITY)} | Sim: {color(VOICE_SIMILARITY)} | Style: {color(VOICE_STYLE)}")

        # Play audio
        if sys.platform == "win32":
            subprocess.run([
                "powershell", "-Command",
                f"Add-Type -AssemblyName presentationCore; "
                f"$p = New-Object System.Windows.Media.MediaPlayer; "
                f"$p.Open('{path}'); "
                f"Start-Sleep -Milliseconds 300; "
                f"$p.Play(); "
                f"Start-Sleep -Seconds {duration}"
            ], shell=False)
        else:
            subprocess.run(["mpv", "--no-video", "--really-quiet", path], shell=False)

        return True
    except Exception as e:
        print(f"[TalkyTalk] ElevenLabs error: {e}", file=sys.stderr)
        return False


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


def speak(text, force_local=False):
    """Main speak function with fallback logic"""

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

    # Segment long text
    segments = segment_text(text)

    for i, segment in enumerate(segments):
        success = speak_elevenlabs(segment, i)
        if not success:
            print(f"[TalkyTalk] Falling back to local TTS for segment {i}")
            speak_local(segment)

    return "elevenlabs"


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: talkytalk.py <text> [--local] [--silent]")
        print("       talkytalk.py --test")
        print("Flags:")
        print("  --silent   Print only, no voice (saves API cost)")
        print("  --local    Force local TTS fallback (espeak-ng / SAPI)")
        sys.exit(1)

    if sys.argv[1] == "--test":
        print("[TalkyTalk] Testing system...")
        online = is_online()
        print(f"  Online: {online}")
        speak("TalkyTalk system test. " + ("ElevenLabs connected." if online else "Offline mode, using local TTS."))
        print("[TalkyTalk] Test complete.")
        sys.exit(0)

    flags = ["--local", "--windows", "--silent"]
    force_local = "--local" in sys.argv or "--windows" in sys.argv
    silent_mode = "--silent" in sys.argv
    text = " ".join(arg for arg in sys.argv[1:] if arg not in flags)

    if silent_mode:
        # Just print, no voice
        filtered = filter_text(text)
        print(f"[TalkyTalk] Silent: {filtered}")
        print(f"[TalkyTalk] Used: silent (0 API cost)")
    else:
        engine = speak(text, force_local=force_local)
        print(f"[TalkyTalk] Used: {engine}")


if __name__ == "__main__":
    main()
