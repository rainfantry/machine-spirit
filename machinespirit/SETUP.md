# TALKYTALK SETUP

## Windows vs Linux - Know the Difference

### WINDOWS (PowerShell)
- Profile: `C:\Users\<you>\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`
- Uses `function` not `alias`
- No `source` command - just restart PowerShell
- Audio: PowerShell MediaPlayer (built-in)

```powershell
# Add to profile:
function georgebot {
    Set-Location C:\Users\gwu07\Desktop\talkytalk
    claude
}

function say {
    python "C:\Users\gwu07\Desktop\talkytalk\talkytalk.py" $args
}
```

Reload: Close PowerShell, open new one.

---

### WINDOWS (Git Bash)
- Profile: `~/.bashrc` or `~/.bash_profile`
- Uses `alias`
- Reload with `source ~/.bashrc`
- Audio: PowerShell MediaPlayer (called from bash)

```bash
# Add to ~/.bashrc:
alias georgebot='cd C:/Users/gwu07/Desktop/talkytalk && claude'
alias say='python C:/Users/gwu07/Desktop/talkytalk/talkytalk.py'
```

Reload: `source ~/.bashrc` or restart terminal.

---

### LINUX
- Profile: `~/.bashrc` or `~/.zshrc`
- Uses `alias`
- Reload with `source ~/.bashrc`
- Audio: `mpg123` (install: `apt install mpg123`)

```bash
# Add to ~/.bashrc:
alias georgebot='cd ~/Desktop/talkytalk && claude'
alias say='python ~/Desktop/talkytalk/talkytalk.py'
```

Reload: `source ~/.bashrc`

**NOTE:** Linux needs mpg123 for audio playback. Current talkytalk.py uses PowerShell MediaPlayer which is Windows-only. For Linux, swap the playback to mpg123 (see digger/voice.py for example).

---

## Quick Reference

| Thing | Windows PowerShell | Windows Git Bash | Linux |
|-------|-------------------|------------------|-------|
| Profile location | Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1 | ~/.bashrc | ~/.bashrc |
| Alias syntax | `function name { }` | `alias name='cmd'` | `alias name='cmd'` |
| Reload | Restart terminal | `source ~/.bashrc` | `source ~/.bashrc` |
| Audio player | PowerShell MediaPlayer | PowerShell MediaPlayer | mpg123 |

---

## Current Build: WINDOWS

This repo is currently configured for Windows with PowerShell MediaPlayer.

To port to Linux:
1. Replace PowerShell audio commands with mpg123
2. Update paths from `C:/Users/...` to `~/...`
3. Use ~/.bashrc instead of PowerShell profile
