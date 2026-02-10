#!/bin/bash
# Machine Spirit — RunPod Startup Script
# Run after pod restart: bash /workspace/runpod-slim/machine-spirit/runpod/start.sh
# Or set as Docker Command for auto-start.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== MACHINE SPIRIT STARTUP ==="
echo "The flesh is weak. The machine endures."
echo ""

# 1. Kill ComfyUI if running
echo "[1/8] Killing ComfyUI..."
pkill -f "python main.py.*--port 8188" 2>/dev/null || true
sleep 2

# 2. Install system dependencies
echo "[2/8] Installing system packages..."
apt-get update -qq && apt-get install -y -qq zstd mpv espeak-ng > /dev/null 2>&1

# 3. Install Ollama
echo "[3/8] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh 2>&1 | tail -1

# 4. Install runpod package (pulls open-webui + elevenlabs as deps)
echo "[4/8] Installing machine-spirit-runpod..."
pip install -q -e "$SCRIPT_DIR" 2>&1 | tail -1

# 5. Start Ollama
echo "[5/8] Starting Ollama..."
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 3

# 6. Pull models
echo "[6/8] Pulling models..."
ollama pull mistral 2>&1 | tail -1
ollama pull llama3.1:8b 2>&1 | tail -1

# 7. Set root password
echo "[7/8] Setting SSH password..."
echo "root:${SSH_PASSWORD:-668340}" | chpasswd

# 8. Start Open WebUI
echo "[8/8] Starting Open WebUI..."
WEBUI_AUTH=false \
AUDIO_TTS_ENGINE=elevenlabs \
AUDIO_TTS_API_KEY="${ELEVENLABS_API_KEY}" \
AUDIO_TTS_VOICE="${ELEVENLABS_VOICE_ID:-weA4Q36twV5kwSaTEL0Q}" \
AUDIO_TTS_MODEL="${ELEVENLABS_MODEL:-eleven_turbo_v2_5}" \
nohup open-webui serve --host 0.0.0.0 --port 8188 > /tmp/open-webui.log 2>&1 &
sleep 10

# 9. Run setup (Anthropic, TTS, STT, presets, admin panel)
echo "[9/9] Configuring services..."
ELEVENLABS_API_KEY="${ELEVENLABS_API_KEY}" \
ELEVENLABS_VOICE_ID="${ELEVENLABS_VOICE_ID:-weA4Q36twV5kwSaTEL0Q}" \
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}" \
python3 -m machine_spirit_runpod.setup

# Status
echo ""
echo "=== STATUS ==="
ollama list 2>&1 | head -5
echo "Open WebUI: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8188)"
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader 2>/dev/null
echo ""
echo "=== READY ==="
echo "Open WebUI:  https://${RUNPOD_POD_HOSTNAME}-8188.proxy.runpod.net"
echo "Admin Panel: https://${RUNPOD_POD_HOSTNAME}-8188.proxy.runpod.net/static/admin.html"
echo "SSH:         ssh root@${RUNPOD_PUBLIC_IP} -p ${RUNPOD_TCP_PORT_22}"
echo ""
echo "The machine spirit awakens. Omnissiah praised."
