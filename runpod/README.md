# RunPod Cloud Deployment

Cloud deployment of Machine Spirit on a RunPod GPU pod. Replaces ComfyUI with Open WebUI + Ollama + ElevenLabs TTS + Claude API.

---

## What Changed

The original Machine Spirit is a terminal CLI chatbot. This adds a cloud deployment layer:

| Original | RunPod |
|----------|--------|
| Terminal CLI only | Web UI (Open WebUI) |
| Local audio playback | Browser audio playback |
| Ollama + Grok brains | Ollama + Grok + Claude brains |
| Manual voice config | Admin panel for voice/preset management |
| Single user, local | Accessible from any browser/phone |

### New Files

```
runpod/
  start.sh                          # Pod startup script (installs everything)
  admin.html                        # Admin panel (system prompts, voice selector, TTS settings)
  pyproject.toml                    # Installable package with deps
  machine_spirit_runpod/
    __init__.py
    setup.py                        # Configures Open WebUI (Anthropic, TTS, STT, presets)
```

### New Dependencies

```
open-webui >= 0.7.0                 # Web UI for LLM chat
elevenlabs >= 1.0.0                 # TTS API
requests >= 2.28.0                  # HTTP client
```

System packages (installed by start.sh):
```
ollama                              # Local LLM server
zstd                                # Ollama extraction dep
mpv                                 # Audio playback
espeak-ng                           # Offline TTS fallback
```

---

## Install

### Quick (one command)

Set your API keys as RunPod environment variables, then:

```bash
bash /workspace/runpod-slim/machine-spirit/runpod/start.sh
```

### With pip

```bash
cd /workspace/runpod-slim/machine-spirit/runpod
pip install -e .
```

This installs `open-webui`, `elevenlabs`, and the `machine-spirit-setup` CLI command.

### Environment Variables

Set these in RunPod pod config or export before running `start.sh`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ELEVENLABS_API_KEY` | Yes | — | ElevenLabs TTS API key |
| `ELEVENLABS_VOICE_ID` | No | `weA4Q36twV5kwSaTEL0Q` | ElevenLabs voice ID |
| `ELEVENLABS_MODEL` | No | `eleven_turbo_v2_5` | ElevenLabs model |
| `ANTHROPIC_API_KEY` | No | — | Anthropic API key for Claude |
| `SSH_PASSWORD` | No | `668340` | Root SSH password |

---

## What start.sh Does

Step by step:

1. Kills ComfyUI (frees GPU)
2. Installs system packages (zstd, mpv, espeak-ng)
3. Installs Ollama
4. Installs this package via `pip install -e .` (pulls open-webui + elevenlabs)
5. Starts Ollama server
6. Pulls Mistral 7B + Llama 3.1 8B models
7. Sets SSH root password
8. Starts Open WebUI on port 8188 with ElevenLabs TTS
9. Runs `machine-spirit-setup` which:
   - Adds Anthropic API connection
   - Configures ElevenLabs TTS + browser STT
   - Enables auto-play for responses
   - Creates Machine Spirit model presets (Mistral, Llama, Claude)
   - Copies admin panel to Open WebUI static dir

---

## Access

| Service | URL |
|---------|-----|
| Chat | `https://<pod>-8188.proxy.runpod.net` |
| Admin | `https://<pod>-8188.proxy.runpod.net/static/admin.html` |
| SSH | `ssh root@<ip> -p <port>` |

---

## Persistence

`/workspace` survives pod restarts. Everything else is rebuilt by `start.sh`.

Set `bash /workspace/runpod-slim/machine-spirit/runpod/start.sh` as the pod's Docker Command for automatic startup.
