"""
main.py
CLI orchestrator and safety listener for CadenceType.
"""

import sys
import time
import threading
import pyperclip
from pynput import keyboard
from engine import TypingEngine


def main():
    print("=" * 48)
    print("       CadenceType: Native Input Daemon         ")
    print("=" * 48)
    print("• Panic switch: Press 'ESC' at any time to abort.\n")

    # 1. Fetch text from system clipboard
    raw_text = pyperclip.paste()
    if not raw_text or not raw_text.strip():
        print("[!] Error: Clipboard is empty.")
        print("    Copy some text first, then run this script again.")
        sys.exit(1)

    char_count = len(raw_text)
    word_count = len(raw_text.split())
    preview = raw_text[:70].replace("\n", " ")

    print(f"Loaded content: {word_count} words ({char_count} characters)")
    print(f"Preview: \"{preview}...\"\n")

    # 2. Get user configuration with sensible defaults
    try:
        wpm_prompt = input("Target WPM [Default: 65]: ").strip()
        target_wpm = float(wpm_prompt) if wpm_prompt else 65.0

        err_prompt = input("Error rate % (0.0 to 5.0) [Default: 2.0]: ").strip()
        error_rate = (float(err_prompt) if err_prompt else 2.0) / 100.0
    except ValueError:
        print("[!] Invalid numerical value. Falling back to defaults (65 WPM, 2% typos).")
        target_wpm = 65.0
        error_rate = 0.02

    # 3. Instantiate the engine
    engine = TypingEngine(target_wpm=target_wpm, error_rate=error_rate)

    # 4. Set up non-blocking global escape key listener
    def on_key_press(key):
        if key == keyboard.Key.esc:
            print("\n\n[!] Emergency abort signal received ('ESC'). Halting...")
            engine.abort()
            return False  # Deregisters this listener

    esc_listener = keyboard.Listener(on_press=on_key_press)
    esc_listener.daemon = True
    esc_listener.start()

    # 5. Countdown buffer for switching windows
    print("\nSwitch to your destination editor now.")
    for remaining in range(5, 0, -1):
        print(f"Starting in {remaining} second(s)... (Press ESC to cancel)", end="\r", flush=True)
        time.sleep(1)
        if engine.stop_event.is_set():
            print("\n[x] Cancelled before typing started.")
            sys.exit(0)

    print("\n\n[>>>] Typing initiated. Keep the destination window active.")

    # 6. Execute typing routine on an isolated thread
    worker = threading.Thread(target=engine.type_text, args=(raw_text,), daemon=True)
    worker.start()

    # Wait for the worker to conclude or be aborted
    while worker.is_alive():
        worker.join(timeout=0.2)

    # 7. Final status reporting
    if engine.stop_event.is_set():
        print("[x] Process was stopped prematurely.")
    else:
        print("[✓] Finished typing all content successfully.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Process terminated via Ctrl+C.")
        sys.exit(0)
