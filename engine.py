"""
engine.py
Core input dispatch and statistical cadence modeling engine.
"""

import time
import math
import random
import threading
from pynput.keyboard import Controller, Key
from keyboard_map import get_neighbor


class TypingEngine:
    def __init__(self, target_wpm: float = 65.0, error_rate: float = 0.02):
        self.target_wpm = target_wpm
        self.error_rate = error_rate
        self.keyboard = Controller()
        self.stop_event = threading.Event()

    def _calculate_base_delay(self) -> float:
        """
        Calculates the average delay per character based on standard WPM.
        Standard typographic definition: 1 Word = 5 characters (including spaces).
        """
        chars_per_second = (self.target_wpm * 5.0) / 60.0
        return 1.0 / max(chars_per_second, 0.1)

    def _sleep_with_check(self, duration: float):
        """
        Sleeps in 15ms slices to ensure immediate response
        if the emergency stop event is triggered.
        """
        slice_time = 0.015
        elapsed = 0.0
        while elapsed < duration:
            if self.stop_event.is_set():
                return
            remaining = duration - elapsed
            sleep_chunk = min(slice_time, remaining)
            time.sleep(sleep_chunk)
            elapsed += sleep_chunk

    def _sample_keystroke_delay(self) -> float:
        """
        Samples an inter-keystroke interval (IKI) using a log-normal distribution.
        This accurately captures human right-skewed cadence (fast bursts + micro-hesitations).
        """
        base_delay = self._calculate_base_delay()
        mu = math.log(base_delay)
        sigma = 0.28  # Variance coefficient
        sampled = random.lognormvariate(mu, sigma)

        # Clamp between 30ms (maximum physical burst speed) and 450ms
        return max(0.03, min(sampled, 0.45))

    def _simulate_typo_and_correction(self, intended_char: str) -> bool:
        """
        Types a physically adjacent wrong key, pauses briefly to simulate
        cognitive latency/recognition, hits Backspace, and settles before correcting.
        """
        wrong_char = get_neighbor(intended_char)
        if wrong_char == intended_char:
            return False

        # 1. Type erroneous character
        self.keyboard.press(wrong_char)
        self.keyboard.release(wrong_char)

        # 2. Cognitive latency (realizing the error)
        self._sleep_with_check(random.uniform(0.18, 0.36))
        if self.stop_event.is_set():
            return True

        # 3. Hit backspace to delete error
        self.keyboard.press(Key.backspace)
        self.keyboard.release(Key.backspace)

        # 4. Brief hesitation before recovery
        self._sleep_with_check(random.uniform(0.08, 0.16))
        return True

    def type_text(self, text: str):
        """
        Iterates over the input string, applying cadence modeling,
        punctuation pauses, and periodic typo/correction routines.
        """
        self.stop_event.clear()

        for char in text:
            if self.stop_event.is_set():
                break

            # Handle newline / carriage return
            if char in ('\n', '\r'):
                self.keyboard.press(Key.enter)
                self.keyboard.release(Key.enter)
                # Cognitive pause between paragraphs/lines
                self._sleep_with_check(random.uniform(0.6, 1.4))
                continue

            # Stochastic typo simulation (applies only to alphanumeric characters)
            if char.isalnum() and random.random() < self.error_rate:
                self._simulate_typo_and_correction(char)
                if self.stop_event.is_set():
                    break

            # Dispatch the intended keystroke
            self.keyboard.press(char)
            self.keyboard.release(char)

            # Sample individual keystroke interval
            delay = self._sample_keystroke_delay()

            # Linguistic boundary pauses
            if char == ' ':
                # Word boundary pause
                delay += random.uniform(0.08, 0.20)
            elif char in ('.', '!', '?'):
                # Sentence boundary pause
                delay += random.uniform(0.40, 0.90)
            elif char in (',', ';', ':'):
                # Clause boundary pause
                delay += random.uniform(0.15, 0.35)

            self._sleep_with_check(delay)

    def abort(self):
        """Trips the cancellation flag immediately."""
        self.stop_event.set()
