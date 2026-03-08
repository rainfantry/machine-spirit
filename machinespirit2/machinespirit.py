# ==========================================================
# MACHINE SPIRIT CONSOLE (PulseAudio / PipeWire friendly)
# Uses Piper -> speech.wav -> paplay
# ==========================================================

import requests
import subprocess
import json
import sys
import os
from datetime import datetime

MODEL = "test"
VOICE_DIR = "voices"
LOG_DIR = "logs"
MEMORY_FILE = "memory.txt"
SPEECH_FILE = "speech.wav"

OLLAMA_URL = "http://localhost:11434/api/generate"

os.makedirs(LOG_DIR, exist_ok=True)


# ----------------------------------------------------------
# VOICE DETECTION
# ----------------------------------------------------------

def detect_voice():
    for f in os.listdir(VOICE_DIR):
        if f.endswith(".onnx"):
            return os.path.join(VOICE_DIR, f)
    return None

VOICE = detect_voice()


# ----------------------------------------------------------
# MEMORY
# ----------------------------------------------------------

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return ""
    with open(MEMORY_FILE) as f:
        return f.read()


def save_memory(text):
    with open(MEMORY_FILE, "a") as f:
        f.write(text + "\n")


# ----------------------------------------------------------
# LOGGING
# ----------------------------------------------------------

def log_interaction(user, ai):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logfile = os.path.join(LOG_DIR, "session.log")

    with open(logfile, "a") as f:
        f.write(f"[{timestamp}]\n")
        f.write(f"You: {user}\n")
        f.write(f"AI: {ai}\n\n")


# ----------------------------------------------------------
# SPEECH FUNCTION (uses paplay instead of aplay)
# ----------------------------------------------------------

def speak(text):

    text = text.strip()

    if not text:
        return

    # generate speech wav with Piper
    subprocess.run(
        ["piper", "--model", VOICE, "--output_file", SPEECH_FILE],
        input=text.encode("utf-8")
    )

    # play using PulseAudio / PipeWire
    subprocess.run(["paplay", SPEECH_FILE])


# ----------------------------------------------------------
# STREAM OLLAMA RESPONSE
# ----------------------------------------------------------

def stream_ollama(prompt):

    memory = load_memory()

    payload = {
        "model": MODEL,
        "prompt": memory + "\nUser: " + prompt,
        "stream": True
    }

    r = requests.post(OLLAMA_URL, json=payload, stream=True)

    full_text = ""
    sentence_buffer = ""

    for line in r.iter_lines():

        if not line:
            continue

        data = json.loads(line)

        if "response" in data:

            chunk = data["response"]

            sys.stdout.write(chunk)
            sys.stdout.flush()

            full_text += chunk
            sentence_buffer += chunk

            if any(x in sentence_buffer for x in [".", "!", "?"]):

                speak(sentence_buffer)
                sentence_buffer = ""

    if sentence_buffer:
        speak(sentence_buffer)

    print("\n")

    return full_text


# ----------------------------------------------------------
# COMMANDS
# ----------------------------------------------------------

def handle_command(cmd):

    global MODEL
    global VOICE

    parts = cmd.split()

    if parts[0] == "/model":

        if len(parts) < 2:
            print("Usage: /model <name>")
            return

        MODEL = parts[1]
        print("Model switched to:", MODEL)

    elif parts[0] == "/voice":

        if len(parts) < 2:
            print("Usage: /voice <filename>")
            return

        new_voice = os.path.join(VOICE_DIR, parts[1])

        if not os.path.exists(new_voice):
            print("Voice not found")
            return

        VOICE = new_voice
        print("Voice switched to:", VOICE)

    elif parts[0] == "/voices":

        print("Available voices:")
        for f in os.listdir(VOICE_DIR):
            if f.endswith(".onnx"):
                print(" ", f)

    elif parts[0] == "/models":

        subprocess.run(["ollama", "list"])

    elif parts[0] == "/remember":

        text = " ".join(parts[1:])
        save_memory(text)
        print("Memory saved")


# ----------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------

def main():

    print("\nMachine Spirit Console Online\n")

    while True:

        try:

            prompt = input("You > ")

            if prompt.startswith("/"):
                handle_command(prompt)
                continue

            print("\nMachine Spirit >", end=" ", flush=True)

            response = stream_ollama(prompt)

            log_interaction(prompt, response)

        except KeyboardInterrupt:

            print("\nExiting Machine Spirit\n")
            break


# ----------------------------------------------------------
# ENTRY
# ----------------------------------------------------------

if __name__ == "__main__":
    main()