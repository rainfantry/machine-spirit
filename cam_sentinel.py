"""
CAM SENTINEL -- Single-Shot Security Camera Analysis
Captures ONE EseeCloud screenshot and optionally sends to Claude Sonnet for analysis.
NO continuous loop. NO daemon mode. Runs once and exits.

Usage:
  python cam_sentinel.py                 # Capture only (for Claude Code to read)
  python cam_sentinel.py --analyze       # Capture + send to Sonnet API for analysis
  python cam_sentinel.py --analyze --cli # Capture + send to Claude CLI for analysis
  python cam_sentinel.py --focus         # Steal focus for capture
  python cam_sentinel.py --fullscreen    # Full screen capture
  python cam_sentinel.py --log           # Save analysis to log file

Output: C:/Users/gwu07/machine-spirit/cam_captures/
Log:    C:/Users/gwu07/machine-spirit/cam_sentinel.log
"""

import os
import sys
import time
import json
import base64
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cam_watch import capture_screenshot, get_latest, CAPTURE_DIR

LOG_FILE = "C:/Users/gwu07/machine-spirit/cam_sentinel.log"
ENV_FILE = "C:/Users/gwu07/machine-spirit/.env"
TALKYTALK = "C:/Users/gwu07/machine-spirit/talkytalk/talkytalk.py"

CHANNEL_MAP = {
    "CAM1": "Front yard/street",
    "CAM2": "Front path/entrance",
    "CAM3": "Driveway",
    "CAM4": "Side porch",
    "CAM5": "Back storage area",
    "CAM6": "Side garden",
    "CAM7": "Backyard lawn",
    "CAM8": "Back patio",
}

ANALYSIS_PROMPT = """TACTICAL SECURITY CAMERA ANALYSIS -- 8-CAMERA NVR GRID

You are a threat assessment operative. Analyze this NVR grid for ANY deviations from baseline security state.

Camera layout:
  CAM1 - Front yard/street  |  CAM2 - Front path/entrance  |  CAM3 - Driveway
  CAM4 - Side porch         |  CAM5 - Back storage area     |  CAM6 - Side garden
  CAM7 - Backyard lawn      |  CAM8 - Back patio            |  CH9  - Offline

RESPOND IN EXACTLY THIS FORMAT:

CAM1: [status - weather, lighting, movement, objects, people, vehicles]
CAM2: [status]
CAM3: [status]
CAM4: [status]
CAM5: [status]
CAM6: [status]
CAM7: [status]
CAM8: [status]
THREAT: [CLEAR / WATCH / ALERT / CRITICAL] - [brief assessment]

Rules:
- Describe visible state, never just say "nothing" or "empty"
- Vehicles: color, type, position
- People: count, clothing, posture, activity
- Doors/gates: open/closed/ajar
- Weather/lighting conditions
- CLEAR = baseline normal | WATCH = minor oddity | ALERT = suspicious | CRITICAL = immediate threat"""

# -- Terminal Colors ---------------------------------------------------------
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_RED  = "\033[41m"
    BG_YEL  = "\033[43m"


def threat_color(level):
    level = level.upper().strip()
    if "CRITICAL" in level:
        return C.BG_RED + C.WHITE + C.BOLD
    elif "ALERT" in level:
        return C.BG_YEL + C.WHITE + C.BOLD
    elif "WATCH" in level:
        return C.YELLOW
    return C.GREEN


def load_api_key():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('ANTHROPIC_API_KEY='):
                    return line.split('=', 1)[1].strip()
    return os.environ.get('ANTHROPIC_API_KEY')


def analyze_api(filepath, api_key):
    """Send screenshot to Sonnet API. Returns raw response text."""
    try:
        import anthropic

        with open(filepath, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
                    {"type": "text", "text": ANALYSIS_PROMPT},
                ],
            }],
        )
        return message.content[0].text.strip()

    except Exception as e:
        return f"API ERROR: {e}"


def analyze_cli(filepath):
    """Send screenshot to Claude CLI. Returns raw response text."""
    import subprocess
    prompt = f"Read the image at {filepath} and analyze it.\n\n{ANALYSIS_PROMPT}"

    try:
        env = os.environ.copy()
        env.pop('CLAUDECODE', None)

        result = subprocess.run(
            ['claude', '-p', prompt, '--allowedTools', 'Read',
             '--output-format', 'text', '--model', 'sonnet', '--max-turns', '2'],
            capture_output=True, text=True, timeout=120, env=env,
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        err = result.stderr.strip()[:200] if result.stderr else "Unknown error"
        return f"CLI ERROR: {err}"

    except subprocess.TimeoutExpired:
        return "CLI TIMEOUT: >120s"
    except FileNotFoundError:
        return "CLI ERROR: Claude CLI not found on PATH"
    except Exception as e:
        return f"CLI ERROR: {e}"


def parse_analysis(raw):
    """Parse response into cameras dict, threat level, summary."""
    cameras = {}
    threat_level = "NONE"
    threat_summary = "Parse failed"

    for line in raw.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        for cam_id in CHANNEL_MAP:
            if line.upper().startswith(cam_id + ":"):
                cameras[cam_id] = line.split(":", 1)[1].strip()
                break

        if line.upper().startswith("THREAT:"):
            threat_part = line.split(":", 1)[1].strip()
            for level in ["CRITICAL", "ALERT", "WATCH", "CLEAR"]:
                if level in threat_part.upper():
                    threat_level = level
                    idx = threat_part.upper().find(level)
                    remainder = threat_part[idx + len(level):].strip(" -—")
                    if remainder:
                        threat_summary = remainder
                    else:
                        threat_summary = level
                    break

    return cameras, threat_level, threat_summary


def voice_alert(message):
    """Speak alert through TalkyTalk."""
    import subprocess
    try:
        subprocess.Popen(['python', TALKYTALK, message],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="CAM SENTINEL -- Single-Shot Camera Analysis")
    parser.add_argument('--analyze', action='store_true', help='Send to Claude API for analysis (default: capture only)')
    parser.add_argument('--cli', action='store_true', help='Use Claude CLI instead of API')
    parser.add_argument('--focus', action='store_true', help='Steal focus for capture')
    parser.add_argument('--fullscreen', action='store_true', help='Capture full screen')
    parser.add_argument('--no-voice', action='store_true', help='Disable TTS alerts')
    parser.add_argument('--log', action='store_true', help='Save analysis to log file')
    args = parser.parse_args()

    print(f"\n{C.CYAN}{C.BOLD}  [*]  CAM SENTINEL -- Single Shot{C.RESET}\n")

    # 1. Capture
    filepath = capture_screenshot(full_screen=args.fullscreen, focus=args.focus)
    if not filepath:
        print(f"\n{C.RED}  [!]  Capture failed. Exiting.{C.RESET}\n")
        sys.exit(1)

    print(f"  {C.GREEN}Captured:{C.RESET} {filepath}")
    print(f"  {C.DIM}Size: {os.path.getsize(filepath)} bytes{C.RESET}")

    if not args.analyze:
        print(f"\n  {C.DIM}Use --analyze to send to Claude API, or read the image in Claude Code.{C.RESET}\n")
        sys.exit(0)

    # 2. Analyze
    backend = "CLI" if args.cli else "API"
    print(f"\n  {C.YELLOW}Analyzing via {backend}...{C.RESET}")

    if args.cli:
        raw = analyze_cli(filepath)
    else:
        api_key = load_api_key()
        if not api_key:
            print(f"\n{C.RED}  [!]  No API key found in {ENV_FILE}{C.RESET}")
            print(f"  {C.DIM}Use --cli for Claude CLI, or just read the image in Claude Code.{C.RESET}\n")
            sys.exit(1)
        raw = analyze_api(filepath, api_key)

    # 3. Parse
    cameras, threat_level, threat_summary = parse_analysis(raw)
    tc = threat_color(threat_level)

    # 4. Display
    print(f"\n  {tc}  THREAT: {threat_level}  {C.RESET}  {threat_summary}\n")

    if cameras:
        for cam_id, location in CHANNEL_MAP.items():
            status = cameras.get(cam_id, "No data")
            print(f"  {C.BOLD}{cam_id}{C.RESET} {C.DIM}({location}){C.RESET} {status}")
    else:
        print(f"  {C.RED}[!] Could not parse camera data from response.{C.RESET}")
        print(f"  {C.DIM}Raw response:{C.RESET}")
        print(f"  {raw[:500]}")

    # 5. Voice alert
    if threat_level in ("ALERT", "CRITICAL") and not args.no_voice:
        voice_alert(f"Security alert. Threat level {threat_level}. {threat_summary}")
        print(f"\n  {C.RED}{C.BOLD}  *  VOICE ALERT SENT  {C.RESET}")

    # 6. Log
    if args.log:
        try:
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "threat_level": threat_level,
                "threat_summary": threat_summary,
                "cameras": cameras,
                "screenshot": filepath,
                "raw_response": raw[:500],
            }
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception:
            pass

    print()


if __name__ == "__main__":
    main()
