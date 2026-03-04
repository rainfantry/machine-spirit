#!/bin/bash
# TalkyTalk Linux Launcher
# Usage: ./talkytalk.sh "your message here"
#        ./talkytalk.sh --test

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/talkytalk.py" "$@"
