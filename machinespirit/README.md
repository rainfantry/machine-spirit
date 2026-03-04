# MACHINE SPIRIT — Voice Pipeline System

ElevenLabs TTS with non-blocking detached playback. Two voices. Multi-voice conversation runner.  
Pipeline: generate → fire detached player → exit immediately. Audio keeps playing after script exits.

---

## FILES

| File | Purpose |
|------|---------|
| `talkytalk.py` | Poof Aussie voice — caller / scammer side |
| `machinespirit.py` | Machine Spirit voice — agent / me |
| `convo.py` | Multi-voice conversation runner — pre-generates all audio, plays seamlessly |
| `config.py` | Config management (API key, voice params) |

---

## TWO VOICES — SAME CODE, DIFFERENT VOICE ID

`talkytalk.py` and `machinespirit.py` are the same pipeline with different voice IDs.  
To clone a new voice: copy either file, change `ELEVENLABS_VOICE_ID` at the top.

```python
# talkytalk.py
ELEVENLABS_VOICE_ID = "dOdGri2hgsKdUEaU09Ct"   # Poof Aussie

# machinespirit.py  
ELEVENLABS_VOICE_ID = "twLPF55UcxNYRmxaWLAn"   # Machine Spirit (me)
```

### Voice parameters (same in both, tune per voice)

```python
VOICE_STABILITY      = 0.42   # lower = more expressive/erratic, higher = controlled
VOICE_SIMILARITY     = 0.78   # how faithful to the original voice clone
VOICE_STYLE          = 0.92   # emotion intensity per syllable
VOICE_SPEAKER_BOOST  = True   # clarity
ELEVENLABS_MODEL     = "eleven_turbo_v2_5"   # fastest, swap to eleven_multilingual_v2 for quality
```

---

## SETUP

```bash
# 1. Install elevenlabs (Windows long-path workaround)
python -m pip install elevenlabs --target C:\py\libs

# 2. Add C:\py\libs to Python path permanently
# create file: C:\...\Python313\site-packages\shortpath_libs.pth
# contents: C:\py\libs

# 3. Copy .env.example to .env and add your key
ELEVENLABS_API_KEY=your_key_here
```

---

## WINDOWS ALIASES — MAKE ANY PYTHON SCRIPT A COMMAND

Drop a `.cmd` file in a folder that's in your PATH.  
`C:\Users\<you>\.local\bin\` is already in PATH on most setups.

```batch
# C:\Users\veren\.local\bin\tts.cmd
@echo off
python C:\Users\veren\machine-spirit\machinespirit\talkytalk.py %*
```

```batch
# C:\Users\veren\.local\bin\machinespirit.cmd
@echo off
python C:\Users\veren\machine-spirit\machinespirit\machinespirit.py %*
```

```batch
# C:\Users\veren\.local\bin\convo.cmd
@echo off
python C:\Users\veren\machine-spirit\machinespirit\convo.py %*
```

`%*` passes every argument and flag through unchanged. That's the whole trick.

### Pipe support (stdin)

Add this block to `main()` in any Python script to support `echo text | yourcommand`:

```python
try:
    import msvcrt, ctypes
    _handle = msvcrt.get_osfhandle(sys.stdin.fileno())
    _bytes_avail = ctypes.c_ulong(0)
    if ctypes.windll.kernel32.PeekNamedPipe(
            _handle, None, 0, None,
            ctypes.byref(_bytes_avail), None) and _bytes_avail.value > 0:
        piped = sys.stdin.read(_bytes_avail.value).strip()
        if piped:
            sys.argv.append(piped)
except Exception:
    pass
```

Uses `PeekNamedPipe` — checks bytes available before reading so it never blocks when launched from subprocesses or tools.

---

## COMMANDS

```
tts "text"                   direct text
tts "text" --block           wait for audio to finish before returning
tts "text" --local           force SAPI fallback (no API cost)
tts "text" --silent          print only, no voice
tts --kill                   stop current playback
tts --test                   test ElevenLabs connection

echo text | tts              pipe from anything
type file.txt | tts          read a file aloud
```

Same flags work on `machinespirit`.

---

## CHAINING (PowerShell)

```powershell
# sequential — each waits for audio to finish before next fires
tts "first" --block; machinespirit "second" --block

# conditional — only fires second if first succeeded (PS7+)
tts "first" --block; if ($?) { machinespirit "second" --block }

# multiline with backtick continuation
tts 'line one' --block; `
machinespirit 'line two' --block; `
tts 'line three' --block
```

**Note:** `--block` chains always have a ~1s gap between lines (polling + API call).  
Use `convo` for seamless zero-gap playback.

---

## CONVO — SEAMLESS MULTI-VOICE CONVERSATIONS

Pre-generates ALL audio first, fires one continuous stream. No gaps between lines.

```
convo script.txt
convo script.txt --block
```

### Script format

```
# comments and blank lines ignored
tts: Hello I am from the tax department.
ms:  Oh thank god you called I was on the dunny.
tts: You owe four thousand dollars.
ms:  FOUR GRAND?! Mate I am on Centrelink!
```

Prefixes: `tts:` = Poof Aussie voice, `ms:` = Machine Spirit voice.

CAPS and `!` push the ElevenLabs model harder on stress and pitch.

### How it works
1. Reads script file
2. Calls ElevenLabs API for every line sequentially (~0.5s each)
3. Builds one PowerShell play session with all segments
4. Fires detached — exits immediately, audio plays in background
5. Deletes all mp3 files after playback (no cache buildup)

---

## SLANG EXPANSION

Both scripts and `convo.py` expand slang before sending to API so pronunciation is correct:

| Write | Speaks as |
|-------|-----------|
| `fkn` | fucken |
| `fk`  | fuck |
| `wtf` | what the fuck |
| `stfu`| shut the fuck up |
| `mf`  | motherfucker |
| `bs`  | bullshit |
| `u`   | you |

---

## VOICE IDs

```
twLPF55UcxNYRmxaWLAn   Machine Spirit (me)
dOdGri2hgsKdUEaU09Ct   Poof Aussie (caller/scammer side)
```

---

VIDIMUS OMNIA
