# PLATFORM COMPARISON

## Two Artifacts - Same Goal

| | GEORGEBOT (Windows) | DIGGER (Linux) |
|---|---|---|
| **OS** | Windows 10/11 | Linux (Debian/Ubuntu) |
| **Audio** | PowerShell MediaPlayer | mpg123 |
| **Shell** | PowerShell / Git Bash | Bash / Zsh |
| **Python** | C:\Python314 | /usr/bin/python3 |
| **Profile** | Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1 | ~/.bashrc |
| **Alias syntax** | `function name { }` | `alias name='cmd'` |

---

## GEORGEBOT (Windows)

**Advantages:**
- Native Windows integration
- PowerShell MediaPlayer built-in (no install)
- Works with Windows Store Python or standalone
- PowerShell profile for aliases
- Fallback to Windows SAPI if ElevenLabs fails

**Disadvantages:**
- PowerShell syntax different from bash
- Path handling (backslash vs forward slash)
- Some Python packages harder to install
- No native `mpg123`

**Audio Pipeline:**
```
ElevenLabs API → MP3 file → PowerShell MediaPlayer → Speaker
                    ↓ (if fail)
              Windows SAPI TTS → Speaker
```

---

## DIGGER (Linux)

**Advantages:**
- Native bash environment
- mpg123 fast and lightweight
- Better subprocess handling
- Standard Python paths
- Easy package management (apt + pip)

**Disadvantages:**
- Needs mpg123 installed (`apt install mpg123`)
- No native fallback TTS (need espeak or similar)
- Different audio system (ALSA/PulseAudio)

**Audio Pipeline:**
```
ElevenLabs API → MP3 file → mpg123 → Speaker
```

---

## Key Differences in Code

### Audio Playback

**Windows (georgebot/talkytalk):**
```python
subprocess.run([
    "powershell", "-Command",
    f"$p = New-Object System.Windows.Media.MediaPlayer; "
    f"$p.Open('{path}'); $p.Play(); Start-Sleep -Seconds {duration}"
])
```

**Linux (digger):**
```python
subprocess.Popen(
    ["mpg123", "-q", self.temp_file],
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL
)
```

### Paths

**Windows:**
```python
PACKAGE_DIR = Path("C:/Users/gwu07/Desktop/georgebot")
```

**Linux:**
```python
PACKAGE_DIR = Path.home() / "projects" / "digger"
```

---

## Which to Use?

- **Windows user?** → Use GEORGEBOT
- **Linux user?** → Use DIGGER
- **WSL?** → Either works, but DIGGER more native
- **Mac?** → Adapt DIGGER (uses similar audio tools)

---

## Porting Notes

To port GEORGEBOT → Linux:
1. Replace PowerShell audio with mpg123
2. Change paths to Unix style
3. Use ~/.bashrc for aliases

To port DIGGER → Windows:
1. Replace mpg123 with PowerShell MediaPlayer
2. Change paths to Windows style
3. Use PowerShell profile for aliases
4. Add Windows SAPI fallback
