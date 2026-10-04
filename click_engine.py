import threading
import time
import random
import pyautogui
from pynput import mouse
import keyboard

pyautogui.PAUSE = 0

class ClickEngine:
    def __init__(self, config):
        self.config = config
        self._lock = threading.Lock()
        self.is_running = False
        self._stop_event = threading.Event()
        self.thread = None
        self.mouse_ctrl = mouse.Controller()
        self.click_count = 0

        self._apply_config()

        # Register hotkeys
        try:
            keyboard.add_hotkey(self.hotkey, self.toggle_hotkey)
            if self.emergency_stop_hotkey:
                keyboard.add_hotkey(self.emergency_stop_hotkey, self.emergency_stop)
        except Exception:
            pass

    def _apply_config(self):
        c = self.config
        self.click_type = c.get("click_type", "single")
        self.click_button = c.get("click_button", "left")
        self.click_rate_min = float(c.get("click_rate_min", 0))
        self.click_rate_sec = float(c.get("click_rate_sec", 0))
        self.click_rate_ms = float(c.get("click_rate_ms", 500.0))
        self.freeze_pointer = bool(c.get("freeze_pointer", True))
        self.freeze_x = int(c.get("freeze_x", 500))
        self.freeze_y = int(c.get("freeze_y", 500))
        self.hotkey = c.get("hotkey", "F8")
        self.emergency_stop_hotkey = c.get("emergency_stop_hotkey", "F9")
        self.jitter_enabled = bool(c.get("jitter_enabled", False))
        self.jitter_range_ms = float(c.get("jitter_range_ms", 10.0))
        self.max_cps = float(c.get("max_cps", 0))
        self.max_clicks = int(c.get("max_clicks", 0))

    def toggle_hotkey(self):
        if self.is_running:
            self.stop()
        else:
            self.start()

    def emergency_stop(self):
        with self._lock:
            self._stop_event.set()
            self.is_running = False
        self.stop()

    def start(self):
        with self._lock:
            if self.is_running:
                return
            self.is_running = True
            self._stop_event.clear()
            self.click_count = 0
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        with self._lock:
            if not self.is_running:
                return
            self.is_running = False
            self._stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.thread = None

    def _get_interval_seconds(self):
        total_ms = (self.click_rate_min * 60 * 1000) + (self.click_rate_sec * 1000) + self.click_rate_ms
        if total_ms <= 0:
            total_ms = 50.0  # minimum 50ms to avoid insane speed
        if self.jitter_enabled and self.jitter_range_ms > 0:
            jitter = random.uniform(-self.jitter_range_ms, self.jitter_range_ms)
            total_ms = max(0.1, total_ms + jitter)
        # Enforce min interval of 50ms to avoid insane speed
        if total_ms < 50.0:
            total_ms = 50.0
        # Enforce max CPS
        if self.max_cps > 0:
            min_interval_ms = 1000.0 / self.max_cps
            if total_ms < min_interval_ms:
                total_ms = min_interval_ms
        return total_ms / 1000.0

    def _perform_click(self):
        btn_map = {
            "left": mouse.Button.left,
            "right": mouse.Button.right,
            "middle": mouse.Button.middle,
        }
        button = btn_map.get(self.click_button, mouse.Button.left)
        if self.click_type == "single":
            self.mouse_ctrl.press(button)
            self.mouse_ctrl.release(button)
        elif self.click_type == "double":
            for _ in range(2):
                self.mouse_ctrl.press(button)
                self.mouse_ctrl.release(button)
        else:
            self.mouse_ctrl.press(button)
            self.mouse_ctrl.release(button)

    def _hybrid_wait(self, target_duration):
        start = time.perf_counter()
        while True:
            elapsed = time.perf_counter() - start
            remaining = target_duration - elapsed
            if remaining <= 0 or self._stop_event.is_set():
                break
            # Use a single sleep for the majority of the wait
            if remaining > 0.0015:
                time.sleep(remaining)
            else:
                # busy wait for sub-ms precision
                pass

    def _run_loop(self):
        # Move pointer once if freeze
        if self.freeze_pointer:
            try:
                pyautogui.moveTo(self.freeze_x, self.freeze_y)
            except Exception:
                pass

        while self.is_running and not self._stop_event.is_set():
            interval = self._get_interval_seconds()
            start_time = time.perf_counter()

            # Perform click
            self._perform_click()
            self.click_count += 1

            # Check max clicks limit
            if self.max_clicks > 0 and self.click_count >= self.max_clicks:
                self.stop()
                break

            # Wait for next interval
            self._hybrid_wait(interval)

    def update_config(self, new_config):
        with self._lock:
            self.config.update(new_config)
            self._apply_config()
