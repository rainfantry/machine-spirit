#!/usr/bin/env python3
"""
TalkyTalk - Linux Version
Audio playback via mpv/ffplay/aplay
Offline TTS via espeak/piper (TODO)
"""

import subprocess
import sys
import os
import socket
import shutil

# Config
ELEVENLABS_API_KEY = "sk_329b44b8e33cb35e3ab400fb735578c87bb2affe3afd173d"
ELEVENLABS_VOICE_ID = "CwhRBWXzGAHq8TQ4Fs17"
ELEVENLABS_MODEL = "eleven_flash_v2_5"
VOICE_DIR = os.path.expanduser("~/.talkytalk/voice")
MAX_SEGMENT_WORDS = 100


def is_online():
    """Check internet connectivity"""
    try:
        socket.create_connection(("api.elevenlabs.io", 443), timeout=2)
        return True
    except OSError:
        return False


def find_player():
    """Find available audio player"""
    for player in ["mpv", "ffplay", "aplay", "paplay"]:
        if shutil.which(player):
            return player
    return None


def speak_espeak(text):
    """Linux espeak fallback"""
    subprocess.run(["espeak", text], shell=False)


def speak_piper(text):
    """Piper TTS fallback (high quality offline)"""
    # TODO: Implement piper integration
    # echo "text" | piper --model en_US-lessac-medium --output_file out.wav
    speak_espeak(text)  # Fallback to espeak for now


def play_audio(path):
    """Play audio file with available player"""
    player = find_player()
    if player == "mpv":
        subprocess.run(["mpv", "--no-video", "--really-quiet", path], shell=False)
    elif player == "ffplay":
        subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path], shell=False)
    elif player == "aplay":
        # Convert mp3 to wav first
        wav_path = path.replace(".mp3", ".wav")
        subprocess.run(["ffmpeg", "-y", "-i", path, wav_path], capture_output=True)
        subprocess.run(["aplay", wav_path], shell=False)
    elif player == "paplay":
        wav_path = path.replace(".mp3", ".wav")
        subprocess.run(["ffmpeg", "-y", "-i", path, wav_path], capture_output=True)
        subprocess.run(["paplay", wav_path], shell=False)
    else:
        print("[TalkyTalk] No audio player found. Install mpv or ffplay.", file=sys.stderr)


def speak_elevenlabs(text, segment_num=0):
    """ElevenLabs TTS"""
    try:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id=ELEVENLABS_MODEL
        )

        os.makedirs(VOICE_DIR, exist_ok=True)
        path = f"{VOICE_DIR}/segment_{segment_num}.mp3"
        with open(path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        play_audio(path)
        return True

    except Exception as e:
        print(f"[TalkyTalk] ElevenLabs error: {e}", file=sys.stderr)
        return False


def segment_text(text, max_words=MAX_SEGMENT_WORDS):
    """Split text into speakable segments"""
    words = text.split()
    if len(words) <= max_words:
        return [text]

    segments = []
    current = []

    for word in words:
        current.append(word)
        if len(current) >= max_words or word.endswith(('.', '!', '?')):
            if current:
                segments.append(' '.join(current))
                current = []

    if current:
        segments.append(' '.join(current))

    return segments


def speak(text, force_offline=False):
    """Main speak function"""
    if force_offline or not is_online():
        print("[TalkyTalk] Using espeak (offline)")
        speak_espeak(text)
        return "espeak"

    segments = segment_text(text)

    for i, segment in enumerate(segments):
        success = speak_elevenlabs(segment, i)
        if not success:
            speak_espeak(segment)

    return "elevenlabs"


def main():
    if len(sys.argv) < 2:
        print("Usage: talkytalk_linux.py <text> [--offline]")
        print("       talkytalk_linux.py --test")
        sys.exit(1)

    if sys.argv[1] == "--test":
        print("[TalkyTalk Linux] Testing...")
        print(f"  Online: {is_online()}")
        print(f"  Player: {find_player()}")
        speak("TalkyTalk Linux test.")
        print("[TalkyTalk Linux] Done.")
        sys.exit(0)

    force_offline = "--offline" in sys.argv
    text = " ".join(arg for arg in sys.argv[1:] if arg != "--offline")

    engine = speak(text, force_offline=force_offline)
    print(f"[TalkyTalk] Used: {engine}")


if __name__ == "__main__":
    main()
