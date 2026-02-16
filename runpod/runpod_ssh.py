#!/usr/bin/env python3
"""RunPod SSH helper — runs commands on RunPod via paramiko with PTY.

Usage:
    python runpod_ssh.py "command1 && command2"
    python runpod_ssh.py  # interactive-ish: reads commands from stdin
"""

import paramiko
import re
import sys
import time

HOST = "ssh.runpod.io"
PORT = 22
USER = "qvqos9g5502qun-64411e93"
KEY_PATH = "C:/Users/gwu07/.ssh/id_ed25519"
TIMEOUT = 15
CMD_WAIT = 3  # seconds to wait for output after sending command


def run_on_runpod(command: str, wait: float = CMD_WAIT) -> str:
    """SSH into RunPod, run a command, return cleaned output."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.Ed25519Key.from_private_key_file(KEY_PATH)
    client.connect(HOST, port=PORT, username=USER, pkey=pkey, timeout=TIMEOUT)

    transport = client.get_transport()
    channel = transport.open_session()
    channel.get_pty(term="xterm", width=200, height=50)
    channel.invoke_shell()
    time.sleep(2)

    # Drain welcome banner
    while channel.recv_ready():
        channel.recv(4096)

    # Send command with a marker so we know when it's done
    marker = "___RUNPOD_CMD_DONE___"
    channel.send(f"{command}; echo {marker}\n")

    output = b""
    deadline = time.time() + wait + 30  # max 30s + wait
    while time.time() < deadline:
        time.sleep(0.5)
        while channel.recv_ready():
            output += channel.recv(4096)
        if marker.encode() in output:
            break

    channel.close()
    client.close()

    # Clean ANSI escape codes
    clean = re.sub(
        r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\][^\x07]*\x07|\x1b\[\?[0-9]*[a-zA-Z]",
        "",
        output.decode(errors="replace"),
    )

    # Extract output between echoed command and marker
    # The shell echoes the command back, then outputs, then the marker
    marker_pattern = re.escape(marker)
    # Find content after the first line containing our marker-echo command, up to marker output
    parts = re.split(rf"echo {marker_pattern}\r?\n", clean, maxsplit=1)
    if len(parts) > 1:
        result = parts[1]
    else:
        result = clean
    # Remove everything from marker onward
    result = result.split(marker)[0]
    # Remove trailing prompt
    result = re.sub(r"root@[^:]+:[^$#]*[$#]\s*$", "", result)
    return result.strip()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
    else:
        print("Enter command to run on RunPod:")
        cmd = input("> ").strip()
        if not cmd:
            print("No command given.")
            sys.exit(1)

    result = run_on_runpod(cmd)
    print(result)
