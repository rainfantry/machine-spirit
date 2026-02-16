# CAM SENTINEL RECOVERY PROTOCOL
**Effective:** 2026-02-16
**Author:** Claude Code (Lieutenant)
**Classification:** OPERATIONAL CRITICAL

## INCIDENT: CAM SENTINEL DESTRUCTION (16:36 UTC)

### Root Cause
Aggressive Unicode-to-ASCII conversion using `errors='ignore'` **blanked entire file** (439 lines → 0 bytes).

**Failed approach:**
```python
content.encode('ascii', errors='ignore').decode('ascii')
```
Result: File deleted in memory, catastrophic data loss.

---

## RECOVERY SOLUTION

### Method: Binary-Level Targeted Replacement
Replace specific Unicode byte sequences at bytes level. Preserves file structure.

```python
# Safe binary replacement pattern
replacements = {
    b'\xe2\x94\x80': b'-',      # ─ box drawing
    b'\xe2\x94\x82': b'|',      # │ vertical
    b'\xe2\x94\x8c': b'+',      # ┌ corners
    b'\xe2\x94\x90': b'+',      # ┐
    b'\xe2\x94\x98': b'+',      # ┘
    b'\xe2\x94\x94': b'+',      # └
    b'\xe2\x80\x94': b'-',      # — em dash
    b'\xe2\x9a\xa0': b'*',      # ⚠ warning
    b'\xe2\x97\x89': b'*',      # ◉ circle
    b'\xe2\x97\x8f': b'*',      # ● bullet
}

with open(filepath, 'rb') as f:
    content = f.read()

for old, new in replacements.items():
    content = content.replace(old, new)

with open(filepath, 'wb') as f:
    f.write(content)
```

### Why This Works
- **Byte-level**: Operates on raw file bytes, never loses data
- **Targeted**: Replaces only known problematic sequences
- **Preserves structure**: Doesn't touch code logic, only terminal glyphs
- **Reversible**: Can restore from git if needed

---

## RESTORATION STEPS (If Needed Again)

1. **Identify affected file**
   ```bash
   python -c "
   with open('cam_sentinel.py', 'rb') as f:
       content = f.read()
       try:
           content.decode('ascii')
       except UnicodeDecodeError as e:
           print(f'Non-ASCII at byte {e.start}')
   "
   ```

2. **Apply binary fix**
   ```bash
   python UNICODE_FIX.py cam_sentinel.py
   ```

3. **Verify**
   ```bash
   python -m py_compile cam_sentinel.py && echo "OK"
   ```

---

## ALTERNATIVE: Restore from GitHub

```bash
cp /tmp/claude-skills/scripts/cam-watch/cam_sentinel.py C:/Users/gwu07/machine-spirit/cam_sentinel.py
```

**GitHub location:** `rainfantry/claude-skills` (private)

---

## PREVENTION RULES

1. **NEVER use `errors='ignore'`** on entire files
2. **ALWAYS test syntax** after conversion: `python -m py_compile file.py`
3. **ALWAYS commit to git** before modifying
4. **PREFER targeted replacements** over global conversions
5. **TEST with small files first**

---

## DEPLOYMENT

- **Status:** ✅ CAM SENTINEL online (PID tracked)
- **Last scan:** 2026-02-16 16:50 UTC
- **Threat level:** CLEAR
- **Next action:** Monitor logs, respond to ALERT/CRITICAL

---

## AGENT AUTOMATION

When CAM SENTINEL breaks:
1. Detect file corruption (0 bytes or syntax error)
2. Restore from GitHub or apply binary fix
3. Run syntax check
4. Restart daemon
5. Report status

**This protocol is now PERMANENT SKILL.**
