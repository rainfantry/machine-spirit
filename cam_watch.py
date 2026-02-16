"""
CAM WATCH -- EseeCloud Screenshot Capture (On-Demand)
Captures the EseeCloud window WITHOUT stealing focus by default.
Uses Win32 PrintWindow for background capture, pyautogui as fallback.

Usage:
  python cam_watch.py --once              # Single background capture (default)
  python cam_watch.py --once --focus      # Single capture WITH focus steal
  python cam_watch.py --once --fullscreen # Full screen capture
  python cam_watch.py --latest            # Show path to most recent capture

Output: C:/Users/gwu07/machine-spirit/cam_captures/
"""

import os
import sys
import time
import glob
import argparse
from datetime import datetime

CAPTURE_DIR = "C:/Users/gwu07/machine-spirit/cam_captures"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Minimum valid capture size in bytes (screens smaller than this are likely black/corrupt)
MIN_CAPTURE_SIZE = 10240  # 10KB


def find_eseecloud_hwnd():
    """Find EseeCloud window handle. Returns hwnd or None."""
    import ctypes
    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW(None, 'EseeCloud')
    return hwnd if hwnd else None


def get_window_rect(hwnd):
    """Get window rectangle without changing focus."""
    import ctypes
    import ctypes.wintypes
    user32 = ctypes.windll.user32
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    left = max(0, rect.left)
    top = max(0, rect.top)
    width = rect.right - left
    height = rect.bottom - top
    return left, top, width, height


def capture_background(hwnd, filepath):
    """Capture window using PrintWindow (no focus steal).
    Returns True on success, False on failure."""
    import ctypes
    import ctypes.wintypes
    from ctypes import windll

    user32 = windll.user32
    gdi32 = windll.gdi32

    # Get window dimensions
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    if width <= 0 or height <= 0:
        return False

    # Create device context and bitmap
    hwnd_dc = user32.GetWindowDC(hwnd)
    if not hwnd_dc:
        return False

    try:
        mem_dc = gdi32.CreateCompatibleDC(hwnd_dc)
        if not mem_dc:
            return False

        try:
            bitmap = gdi32.CreateCompatibleBitmap(hwnd_dc, width, height)
            if not bitmap:
                return False

            try:
                gdi32.SelectObject(mem_dc, bitmap)

                # PrintWindow with PW_RENDERFULLCONTENT (flag 2) for better capture
                result = user32.PrintWindow(hwnd, mem_dc, 2)
                if not result:
                    # Try without flag
                    result = user32.PrintWindow(hwnd, mem_dc, 0)

                if not result:
                    return False

                # Extract bitmap data
                import struct

                # BITMAPINFOHEADER
                bmi = struct.pack('IiiHHIIiiII',
                    40,        # biSize
                    width,     # biWidth
                    -height,   # biHeight (negative = top-down)
                    1,         # biPlanes
                    32,        # biBitCount (BGRA)
                    0,         # biCompression (BI_RGB)
                    0,         # biSizeImage
                    0, 0,      # biXPelsPerMeter, biYPelsPerMeter
                    0, 0       # biClrUsed, biClrImportant
                )

                buf_size = width * height * 4
                buf = ctypes.create_string_buffer(buf_size)
                gdi32.GetDIBits(mem_dc, bitmap, 0, height, buf, bmi, 0)

                # Convert BGRA buffer to PIL Image and save
                from PIL import Image
                img = Image.frombuffer('RGBA', (width, height), buf, 'raw', 'BGRA', 0, 1)
                img = img.convert('RGB')
                img.save(filepath, 'PNG')
                return True

            finally:
                gdi32.DeleteObject(bitmap)
        finally:
            gdi32.DeleteDC(mem_dc)
    finally:
        user32.ReleaseDC(hwnd, hwnd_dc)


def capture_with_focus(hwnd, filepath):
    """Capture window by bringing to foreground (legacy method)."""
    import ctypes
    import pyautogui

    user32 = ctypes.windll.user32
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    left, top, width, height = get_window_rect(hwnd)
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    screenshot.save(filepath)
    return True


def is_mostly_black(filepath, threshold=0.95):
    """Check if image is mostly black (failed capture). Returns True if black."""
    try:
        from PIL import Image
        import struct
        img = Image.open(filepath).convert('RGB')
        w, h = img.size
        if w == 0 or h == 0:
            return True
        # Sample up to 2000 evenly spaced pixels
        raw = img.tobytes()
        total_pixels = w * h
        sample_count = min(2000, total_pixels)
        step = max(1, total_pixels // sample_count)
        black_count = 0
        for i in range(0, total_pixels, step):
            offset = i * 3
            r, g, b = raw[offset], raw[offset + 1], raw[offset + 2]
            if r + g + b < 30:
                black_count += 1
        sampled = total_pixels // step
        return (black_count / sampled) > threshold if sampled > 0 else True
    except Exception:
        return False


def capture_screenshot(full_screen=False, focus=False):
    """Capture screenshot. Returns filepath on success, None on failure."""
    import pyautogui

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cam_{timestamp}.png"
    filepath = os.path.join(CAPTURE_DIR, filename)

    if full_screen:
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        if os.path.exists(filepath) and os.path.getsize(filepath) > MIN_CAPTURE_SIZE:
            print(f"[+] Full screen capture -> {filepath}")
            return filepath
        print("[!] Full screen capture failed or too small")
        return None

    # Find EseeCloud window
    hwnd = find_eseecloud_hwnd()
    if not hwnd:
        print("[!] EseeCloud window not found. Is it running?")
        print("[!] Launch with: start \"\" \"C:/Program Files (x86)/EseeCloud/EseeCloud.exe\"")
        return None

    if focus:
        # Legacy method: steal focus + pyautogui
        try:
            capture_with_focus(hwnd, filepath)
        except Exception as e:
            print(f"[!] Focus capture failed: {e}")
            return None
    else:
        # Background method: PrintWindow (no focus steal)
        try:
            ok = capture_background(hwnd, filepath)
        except Exception as e:
            print(f"[!] Background capture failed: {e}")
            print("[!] Retrying with focus mode...")
            try:
                capture_with_focus(hwnd, filepath)
            except Exception as e2:
                print(f"[!] Focus capture also failed: {e2}")
                return None

    # Validate output
    if not os.path.exists(filepath):
        print("[!] Capture file was not created")
        return None

    fsize = os.path.getsize(filepath)
    if fsize < MIN_CAPTURE_SIZE:
        print(f"[!] Capture too small ({fsize} bytes), likely failed")
        os.remove(filepath)
        return None

    # Check for all-black image (common PrintWindow failure)
    if not focus and is_mostly_black(filepath):
        print("[!] Background capture returned black image, retrying with focus...")
        os.remove(filepath)
        try:
            capture_with_focus(hwnd, filepath)
            if os.path.exists(filepath) and os.path.getsize(filepath) > MIN_CAPTURE_SIZE:
                if not is_mostly_black(filepath):
                    print(f"[+] Focus capture fallback -> {filepath}")
                    return filepath
            print("[!] Focus fallback also returned black/small image")
            if os.path.exists(filepath):
                os.remove(filepath)
            return None
        except Exception as e:
            print(f"[!] Focus fallback failed: {e}")
            return None

    mode = "focus" if focus else "background"
    print(f"[+] Captured ({mode}) -> {filepath}")
    return filepath


def get_latest():
    """Return path to most recent capture."""
    files = sorted(glob.glob(os.path.join(CAPTURE_DIR, "cam_*.png")))
    return files[-1] if files else None


def cleanup_old(max_files=200):
    """Keep only the most recent N captures."""
    files = sorted(glob.glob(os.path.join(CAPTURE_DIR, "cam_*.png")))
    if len(files) > max_files:
        for f in files[:-max_files]:
            os.remove(f)
            print(f"[-] Cleaned up: {os.path.basename(f)}")


def main():
    parser = argparse.ArgumentParser(description="CAM WATCH -- EseeCloud Screenshot Capture")
    parser.add_argument('--once', action='store_true', help='Single capture then exit (default behavior)')
    parser.add_argument('--latest', action='store_true', help='Show most recent capture path')
    parser.add_argument('--focus', action='store_true', help='Steal focus for capture (legacy mode)')
    parser.add_argument('--fullscreen', action='store_true', help='Capture full screen instead of window')
    parser.add_argument('--max-files', type=int, default=200, help='Max captures to keep (default: 200)')
    args = parser.parse_args()

    if args.latest:
        latest = get_latest()
        print(latest if latest else "No captures found")
        return

    # Default behavior is single capture (--once is implicit)
    filepath = capture_screenshot(full_screen=args.fullscreen, focus=args.focus)
    if filepath:
        cleanup_old(args.max_files)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
