# Machine Spirit Console

Local voice AI console built with:

- Ollama (local LLM inference)
- Piper (offline TTS)
- Python controller

Runs completely offline.

---

# Features

- streaming LLM responses
- sentence-based speech
- local voice synthesis
- command system
- persistent memory
- conversation logs
- model switching
- voice switching

---

# Project Structure

machine-spirit/

machinespirit.py
voices/
logs/
models/
README.md

---

# Requirements

Linux (tested on Parrot OS)

Install dependencies:

sudo apt install python3 python3-pip piper ffmpeg ollama

Install Python dependency:

pip install requests

---

# Running

Start Ollama server:

ollama serve

Run console:

python machinespirit.py


---

# Commands

/model NAME

Switch LLM

example:

/model mistral


/voice FILE

Switch Piper voice

example:

/voice en_US-amy-medium.onnx


/voices

List available voices


/models

List installed Ollama models


/remember TEXT

Save information to persistent memory


---

# Installing Voice

Download Piper voice model:

wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx

wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json

Place them inside:

voices/


---

# Testing Voice

Generate test speech:

echo "Machine spirit online" | piper \
  --model voices/en_US-amy-medium.onnx \
  --output_file test.wav

Play:

paplay test.wav


---

# Inspecting Ollama Models

List models:

ollama list


Inspect model config:

ollama show test --modelfile


Example output:

FROM mistral

SYSTEM "custom personality prompt"


---

# Creating Custom Model

Create Modelfile:

nano Modelfile

Example:

FROM mistral

SYSTEM "You are an aggressive Australian hacker assistant."


Build model:

ollama create test -f Modelfile


Run it:

ollama run test


---

# Useful Debug Commands

Check audio devices:

aplay -l


Check running processes:

ps aux | grep piper


Kill audio processes:

killall piper
killall aplay


---

# Architecture

User
 ↓
Python Controller
 ↓
Ollama LLM
 ↓
Sentence buffer
 ↓
Piper TTS
 ↓
Audio output


---

# License

MIT

