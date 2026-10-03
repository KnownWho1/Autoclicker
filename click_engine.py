import threading
import time
import pyautogui
from pynput import mouse
import keyboard

# Disable PyAutoGUI's internal delay for faster execution
pyautogui.PAUSE = 0

class ClickEngine:
    def __init__(self, config):
        self.config = config
        self.is_running = False
        self.click_type = config.get("click_type", "single")
        self.click_rate_min = config.get("click_rate_min", 0)
        self.click_rate_sec = config.get("click_rate_sec", 1)
        self.click_rate_ms = config.get("click_rate_ms", 500.0)
        self.freeze_pointer = config.get("freeze_pointer", True)
        self.freeze_x = config.get("freeze_x", 500)
        self.freeze_y = config.get("freeze_y", 500)
        self.hotkey = config.get("hotkey", "F8")
        
        self.thread = None
        self.mouse_ctrl = mouse.Controller()
        
        # Register hotkey
        keyboard.add_hotkey(self.hotkey, self.toggle_hotkey)

    def toggle_hotkey(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.start()
        else:
            self.stop()

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False

    def _run_loop(self):
        while self.is_running:
            start_time = time.perf_counter()
            
            # Calculate total interval in seconds
            total_ms = (self.click_rate_min * 60 * 1000) + (self.click_rate_sec * 1000) + self.click_rate_ms
            target_duration = total_ms / 1000.0
            
            if self.freeze_pointer:
                pyautogui.moveTo(self.freeze_x, self.freeze_y)
            
            # Use pynput for much faster click registration
            if self.click_type == "single":
                self.mouse_ctrl.press(mouse.Button.left)
                self.mouse_ctrl.release(mouse.Button.left)
            else:
                self.mouse_ctrl.press(mouse.Button.left)
                self.mouse_ctrl.release(mouse.Button.left)
                self.mouse_ctrl.press(mouse.Button.left)
                self.mouse_ctrl.release(mouse.Button.left)
            
            # High-precision wait loop
            while (time.perf_counter() - start_time) < target_duration:
                if not self.is_running:
                    return
                
                remaining = target_duration - (time.perf_counter() - start_time)
                if remaining > 0.001: # Sleep if more than 1ms left to save CPU
                    time.sleep(0.0005)
                else:
                    # Busy wait for sub-millisecond precision
                    pass

    def update_config(self, new_config):
        self.config.update(new_config)
        self.click_type = self.config.get("click_type", "single")
        self.click_rate_min = self.config.get("click_rate_min", 0)
        self.click_rate_sec = self.config.get("click_rate_sec", 1)
        self.click_rate_ms = self.config.get("click_rate_ms", 500.0)
        self.freeze_pointer = self.config.get("freeze_pointer", True)
        self.freeze_x = self.config.get("freeze_x", 500)
        self.freeze_y = self.config.get("freeze_y", 500)
