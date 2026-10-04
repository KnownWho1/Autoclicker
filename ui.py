import customtkinter as ctk
from click_engine import ClickEngine
from config_manager import load_config, save_config
import pyautogui
import queue
import threading
import time

class AutoclickerUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Autoclicker Pro")
        self.geometry("660x880")
        self.minsize(600, 650)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Load config
        self.config = load_config()
        self.engine = ClickEngine(self.config)
        # Clicking indicator state (mirrors engine.is_running).
        self._clicking = False
        self._indicator_reason = "ready"
        # Thread-safe handoff for engine state changes from hotkey/worker
        # threads (Tk widgets may only be touched on the main thread).
        self._state_queue = queue.SimpleQueue()
        # Engine fires from worker/keyboard threads -> marshal to Tk thread.
        self.engine.on_state_change = self._on_engine_state_change
        # Until timestamp (perf_counter) for which status loop must not
        # overwrite transient messages like "Location Picked".
        self._status_hold_until = 0.0

        # UI Layout
        self.setup_ui()
        self._bind_autosave()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._refresh_interval_total()
        self._set_clicking_state(False, "ready")
        self.after(200, self._update_status_loop)

    def setup_ui(self):
        # Scrollable container so the bottom (indicator/buttons) is reachable
        # on short screens instead of being cut off by a fixed window size.
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True)
        self.scroll.grid_columnconfigure((0, 1), weight=1, uniform="col")

        title_label = ctk.CTkLabel(self.scroll, text="Autoclicker Pro", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        # Click Rate Section (full width: 3 columns need the room)
        rate_frame = ctk.CTkFrame(self.scroll)
        rate_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(rate_frame, text="Interval").grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        ctk.CTkLabel(rate_frame, text="Time waited between clicks. Minutes + Seconds + Ms are added together.",
                      font=ctk.CTkFont(size=11), text_color="gray", wraplength=560, justify="left").grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")

        self.min_entry = ctk.CTkEntry(rate_frame, placeholder_text="Min", width=80)
        self.min_entry.insert(0, str(self.config.get("click_rate_min", 0)))
        self.min_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.sec_entry = ctk.CTkEntry(rate_frame, placeholder_text="Sec", width=80)
        self.sec_entry.insert(0, str(self.config.get("click_rate_sec", 0)))
        self.sec_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.ms_entry = ctk.CTkEntry(rate_frame, placeholder_text="ms", width=80)
        self.ms_entry.insert(0, str(self.config.get("click_rate_ms", 500.0)))
        self.ms_entry.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

        # Permanent per-field descriptions (placeholders vanish once values are typed).
        ctk.CTkLabel(rate_frame, text="Minutes between clicks", font=ctk.CTkFont(size=11), text_color="gray", wraplength=170, justify="left").grid(row=3, column=0, padx=10, pady=(0, 5), sticky="w")
        ctk.CTkLabel(rate_frame, text="Seconds between clicks", font=ctk.CTkFont(size=11), text_color="gray", wraplength=170, justify="left").grid(row=3, column=1, padx=5, pady=(0, 5), sticky="w")
        ctk.CTkLabel(rate_frame, text="Milliseconds — fractions like 0.002 allowed", font=ctk.CTkFont(size=11), text_color="gray", wraplength=170, justify="left").grid(row=3, column=2, padx=5, pady=(0, 5), sticky="w")

        # Live readout of what the interval actually controls.
        self.interval_total_label = ctk.CTkLabel(rate_frame, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.interval_total_label.grid(row=4, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")
        rate_frame.grid_columnconfigure((0,1,2), weight=1)

        # Type & Button Section (left column)
        type_frame = ctk.CTkFrame(self.scroll)
        type_frame.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="nsew")
        type_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(type_frame, text="Click Type").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.type_var = ctk.StringVar(value=self.config.get("click_type", "single"))
        ctk.CTkRadioButton(type_frame, text="Single", variable=self.type_var, value="single").grid(row=1, column=0, padx=10, pady=2, sticky="w")
        ctk.CTkRadioButton(type_frame, text="Double", variable=self.type_var, value="double").grid(row=1, column=1, padx=10, pady=2, sticky="w")
        ctk.CTkRadioButton(type_frame, text="Triple", variable=self.type_var, value="triple").grid(row=1, column=2, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(type_frame, text="Presses fired on each interval tick.", font=ctk.CTkFont(size=11), text_color="gray", wraplength=260, justify="left").grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")

        ctk.CTkLabel(type_frame, text="Button").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.button_var = ctk.StringVar(value=self.config.get("click_button", "left"))
        ctk.CTkOptionMenu(type_frame, variable=self.button_var, values=["left","right","middle"]).grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(type_frame, text="Which mouse button to press.", font=ctk.CTkFont(size=11), text_color="gray", wraplength=260, justify="left").grid(row=5, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")
        type_frame.grid_columnconfigure(0, weight=1)

        # Safety Section (full width, two columns)
        safety_frame = ctk.CTkFrame(self.scroll)
        safety_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        safety_frame.grid_columnconfigure((0, 1), weight=1, uniform="safe")

        ctk.CTkLabel(safety_frame, text="Limits").grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.max_cps_var = ctk.CTkEntry(safety_frame, placeholder_text="Max CPS (0=off)")
        self.max_cps_var.insert(0, str(self.config.get("max_cps", 0)))
        self.max_cps_var.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(safety_frame, text="Speed cap in clicks/sec. 0 = no cap.", font=ctk.CTkFont(size=11), text_color="gray", wraplength=260, justify="left").grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")

        self.max_clicks_var = ctk.CTkEntry(safety_frame, placeholder_text="Max Clicks (0=off)")
        self.max_clicks_var.insert(0, str(self.config.get("max_clicks", 0)))
        self.max_clicks_var.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(safety_frame, text="Auto-stop after this many clicks. 0 = unlimited.", font=ctk.CTkFont(size=11), text_color="gray", wraplength=260, justify="left").grid(row=4, column=0, padx=10, pady=(0, 5), sticky="w")

        self.jitter_var = ctk.BooleanVar(value=self.config.get("jitter_enabled", False))
        ctk.CTkCheckBox(safety_frame, text="Enable Jitter", variable=self.jitter_var).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(safety_frame, text="Randomize each interval ± the range below.", font=ctk.CTkFont(size=11), text_color="gray", wraplength=260, justify="left").grid(row=2, column=1, padx=10, pady=(0, 5), sticky="w")

        self.jitter_range_var = ctk.CTkEntry(safety_frame, placeholder_text="Jitter Range ms")
        self.jitter_range_var.insert(0, str(self.config.get("jitter_range_ms", 10.0)))
        self.jitter_range_var.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(safety_frame, text="Max random offset in milliseconds.", font=ctk.CTkFont(size=11), text_color="gray", wraplength=260, justify="left").grid(row=4, column=1, padx=10, pady=(0, 5), sticky="w")

        # Pointer Section (right column): freeze + coordinates + picker together
        freeze_frame = ctk.CTkFrame(self.scroll)
        freeze_frame.grid(row=2, column=1, padx=(10, 20), pady=10, sticky="nsew")
        freeze_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(freeze_frame, text="Pointer").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.freeze_var = ctk.BooleanVar(value=self.config.get("freeze_pointer", True))
        ctk.CTkCheckBox(freeze_frame, text="Freeze Pointer", variable=self.freeze_var).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(freeze_frame, text="Lock the cursor at X / Y while clicking.", font=ctk.CTkFont(size=11), text_color="gray", wraplength=260, justify="left").grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")

        self.freeze_x_entry = ctk.CTkEntry(freeze_frame, placeholder_text="X")
        self.freeze_x_entry.insert(0, str(self.config.get("freeze_x", 500)))
        self.freeze_x_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(freeze_frame, text="Cursor X position.", font=ctk.CTkFont(size=11), text_color="gray").grid(row=4, column=0, padx=10, pady=(0, 5), sticky="w")

        self.freeze_y_entry = ctk.CTkEntry(freeze_frame, placeholder_text="Y")
        self.freeze_y_entry.insert(0, str(self.config.get("freeze_y", 500)))
        self.freeze_y_entry.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(freeze_frame, text="Cursor Y position.", font=ctk.CTkFont(size=11), text_color="gray").grid(row=6, column=0, padx=10, pady=(0, 5), sticky="w")

        # Pick Location (lives with the coordinates it fills in)
        self.pick_btn = ctk.CTkButton(freeze_frame, text="Pick Location", command=self.pick_location)
        self.pick_btn.grid(row=7, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(freeze_frame, text="Captures the cursor position after a 3s delay.", font=ctk.CTkFont(size=11), text_color="gray", wraplength=260, justify="left").grid(row=8, column=0, padx=10, pady=(0, 5), sticky="w")

        # Hotkey Section
        hotkey_frame = ctk.CTkFrame(self.scroll)
        hotkey_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.hotkey_label = ctk.CTkLabel(hotkey_frame, text="")
        self.hotkey_label.grid(row=0, column=0, padx=10, pady=10)
        self._refresh_hotkey_label()

        # Buttons
        btn_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=20)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.start_btn = ctk.CTkButton(btn_frame, text="Start", command=self.start_clicking, fg_color="green", hover_color="darkgreen")
        self.start_btn.grid(row=0, column=0, padx=10, pady=10)

        self.stop_btn = ctk.CTkButton(btn_frame, text="Stop", command=self.stop_clicking, fg_color="red", hover_color="darkred", state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=10, pady=10)

        # Status
        status_frame = ctk.CTkFrame(self.scroll)
        status_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_columnconfigure(1, weight=1)
        self.status_label = ctk.CTkLabel(status_frame, text="Status: Ready", text_color="gray")
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.stats_label = ctk.CTkLabel(status_frame, text="Clicks: 0", text_color="gray")
        self.stats_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        # Dedicated clicking indicator (independent of transient status text
        # so hotkey / emergency-stop / max-clicks are always visible).
        self.indicator_dot = ctk.CTkLabel(status_frame, text="●", font=ctk.CTkFont(size=18), text_color="gray")
        self.indicator_dot.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")
        self.indicator_text = ctk.CTkLabel(status_frame, text="IDLE", font=ctk.CTkFont(weight="bold"), text_color="gray")
        self.indicator_text.grid(row=1, column=1, padx=10, pady=(0, 5), sticky="e")

    def collect_ui_config(self):
        """Read and validate all settings widgets. Raises ValueError on bad input."""
        mins = float(self.min_entry.get() or 0)
        secs = float(self.sec_entry.get() or 0)
        ms = float(self.ms_entry.get() or 0)
        fx = int(float(self.freeze_x_entry.get() or 0))
        fy = int(float(self.freeze_y_entry.get() or 0))
        max_cps = float(self.max_cps_var.get() or 0)
        max_clicks = int(float(self.max_clicks_var.get() or 0))
        jitter_enabled = self.jitter_var.get()
        jitter_range = float(self.jitter_range_var.get() or 0)
        if mins < 0 or secs < 0 or ms < 0:
            raise ValueError("Interval values must be >= 0")
        if max_cps < 0 or max_clicks < 0 or jitter_range < 0:
            raise ValueError("Safety values must be >= 0")

        return {
            "click_rate_min": mins,
            "click_rate_sec": secs,
            "click_rate_ms": ms,
            "click_type": self.type_var.get(),
            "click_button": self.button_var.get(),
            "freeze_pointer": self.freeze_var.get(),
            "freeze_x": fx,
            "freeze_y": fy,
            "max_cps": max_cps,
            "max_clicks": max_clicks,
            "jitter_enabled": jitter_enabled,
            "jitter_range_ms": jitter_range,
        }

    def persist_current_settings(self):
        """Push UI -> engine -> config.json. Raises ValueError on bad input."""
        cfg_update = self.collect_ui_config()
        self.engine.update_config(cfg_update)
        self.config.update(cfg_update)
        save_config(self.config)
        self._refresh_hotkey_label()
        self._refresh_interval_total()
        return cfg_update

    def _refresh_interval_total(self):
        """Show the effective interval so the Min/Sec/Ms fields are unambiguous."""
        try:
            mins = float(self.min_entry.get() or 0)
            secs = float(self.sec_entry.get() or 0)
            ms = float(self.ms_entry.get() or 0)
            total_ms = mins * 60 * 1000 + secs * 1000 + ms
            if total_ms <= 0:
                self.interval_total_label.configure(text="Total: 0.1 ms minimum (engine floor — increase interval or set Max CPS)")
            else:
                cps = 1000.0 / total_ms
                self.interval_total_label.configure(text=f"Total: {total_ms:g} ms  ≈  {cps:.2f} clicks/sec")
        except ValueError:
            self.interval_total_label.configure(text="Total: — (invalid input)")

    def _refresh_hotkey_label(self):
        base = f"Hotkey: {self.config.get('hotkey','F8')}  |  Emergency Stop: {self.config.get('emergency_stop_hotkey','F9')}"
        if getattr(self.engine, "hotkey_registered", True):
            # Neutral gray: green is reserved for the CLICKING indicator so a
            # registered hotkey is never mistaken for an active session.
            self.hotkey_label.configure(text=f"{base}  ●", text_color="gray")
        else:
            err = getattr(self.engine, "hotkey_error", "") or "unknown error"
            self.hotkey_label.configure(text=f"{base}  ⚠ hotkey NOT registered: {err}", text_color="red")

    def _bind_autosave(self):
        # Option/check variables save immediately (always valid).
        for var in (self.type_var, self.button_var, self.freeze_var, self.jitter_var):
            var.trace_add("write", lambda *_: self._on_autosave_var())
        # Text entries: save on focus-out and Return (avoids saving mid-keystroke).
        for entry in (self.min_entry, self.sec_entry, self.ms_entry,
                      self.max_cps_var, self.max_clicks_var, self.jitter_range_var,
                      self.freeze_x_entry, self.freeze_y_entry):
            entry.bind("<FocusOut>", lambda _e: self._on_entry_autosave())
            entry.bind("<Return>", lambda _e: self._on_entry_autosave())

    def _on_autosave_var(self):
        try:
            self.persist_current_settings()
        except ValueError:
            pass  # wait for valid input; Start will report the error

    def _on_entry_autosave(self):
        try:
            self.persist_current_settings()
        except ValueError:
            pass

    def on_closing(self):
        try:
            self.persist_current_settings()
        except ValueError:
            pass  # keep last good config on disk
        finally:
            try:
                self.engine.on_state_change = None
            except Exception:
                pass
            try:
                self.engine.stop(reason="button")
            except Exception:
                pass
            self.destroy()

    def _apply_picked_location(self, x, y):
        self.freeze_x_entry.delete(0, "end")
        self.freeze_x_entry.insert(0, str(x))
        self.freeze_y_entry.delete(0, "end")
        self.freeze_y_entry.insert(0, str(y))
        # Sync engine immediately so hotkey-start uses the new location,
        # then persist everything (picks up any pending UI edits too).
        try:
            self.persist_current_settings()
        except ValueError:
            # Entry fields invalid; at least save the picked coordinates.
            patch = {"freeze_x": x, "freeze_y": y}
            self.engine.update_config(patch)
            self.config.update(patch)
            save_config(self.config)
        self._status_hold_until = time.perf_counter() + 2.0
        self.status_label.configure(text=f"Location Picked: {x}, {y}", text_color="green")

    def pick_location(self):
        # Inform user to move mouse and wait 3 seconds before capturing
        self._status_hold_until = time.perf_counter() + 3.5
        self.status_label.configure(text="Status: Move mouse to target... (3s)", text_color="yellow")
        self.pick_btn.configure(state="disabled")

        def capture():
            try:
                time.sleep(3)                       # delay before getting position
                x, y = pyautogui.position()
                # Update UI in main thread
                self.after(0, lambda: self._apply_picked_location(x, y))
            except Exception as e:
                self.after(0, lambda err=e: self.status_label.configure(
                    text=f"Error picking location: {err}", text_color="red"))
            finally:
                self.after(0, lambda: self.pick_btn.configure(state="normal"))

        threading.Thread(target=capture, daemon=True).start()
    def start_clicking(self):
        try:
            self.persist_current_settings()

            if self.engine.is_running:
                self.engine.stop(reason="button")
            self.engine.start(reason="button")
            # Indicator/buttons updated via engine callback (_set_clicking_state).
        except ValueError:
            self._status_hold_until = time.perf_counter() + 2.0
            self.status_label.configure(text="Error: Invalid input", text_color="red")

    def stop_clicking(self, reason="button"):
        self.engine.stop(reason=reason)
        # Indicator/buttons updated via engine callback. If engine was not
        # running, no callback fires, so force the idle UI here.
        if not self.engine.is_running:
            try:
                self.after(0, lambda r=reason: self._set_clicking_state(False, r))
            except Exception:
                pass

    def _on_engine_state_change(self, is_running, reason):
        # Called from keyboard-hook or worker threads: never touch Tk widgets
        # here, enqueue and let the main thread apply it.
        try:
            self._state_queue.put((bool(is_running), reason))
        except Exception:
            pass
        try:
            self.after(0, self._drain_state_queue)
        except Exception:
            pass  # main loop will drain via _update_status_loop fallback

    def _drain_state_queue(self):
        latest = None
        try:
            while True:
                latest = self._state_queue.get_nowait()
        except queue.Empty:
            pass
        except Exception:
            return
        if latest is not None:
            try:
                self._set_clicking_state(latest[0], latest[1])
            except Exception:
                pass

    def _set_clicking_state(self, is_running, reason):
        if not hasattr(self, "indicator_dot") or not hasattr(self, "start_btn"):
            return
        self._clicking = bool(is_running)
        self._indicator_reason = reason
        if is_running:
            source = " (hotkey)" if reason == "hotkey" else ""
            self.indicator_dot.configure(text_color="green")
            self.indicator_text.configure(text=f"CLICKING{source}", text_color="green")
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self._status_hold_until = 0.0
            self.status_label.configure(text="Status: Clicking...", text_color="green")
        else:
            if reason == "emergency":
                self.indicator_dot.configure(text_color="red")
                self.indicator_text.configure(text="STOPPED (EMERGENCY)", text_color="red")
                self._status_hold_until = time.perf_counter() + 3.0
                self.status_label.configure(text="Status: Emergency stopped", text_color="red")
            elif reason == "max_clicks":
                self.indicator_dot.configure(text_color="orange")
                self.indicator_text.configure(text="DONE (MAX CLICKS)", text_color="orange")
                self._status_hold_until = time.perf_counter() + 3.0
                self.status_label.configure(text="Status: Done (max clicks)", text_color="orange")
            elif reason == "hotkey":
                self.indicator_dot.configure(text_color="gray")
                self.indicator_text.configure(text="IDLE (HOTKEY STOP)", text_color="gray")
                self._status_hold_until = 0.0
                self.status_label.configure(text="Status: Ready", text_color="gray")
            else:
                self.indicator_dot.configure(text_color="gray")
                self.indicator_text.configure(text="IDLE", text_color="gray")
                if time.perf_counter() >= self._status_hold_until:
                    self.status_label.configure(text="Status: Ready", text_color="gray")
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

    def _update_status_loop(self):
        # Drain queued state changes on the main thread first (hotkey /
        # emergency-stop / max-clicks arrive here thread-safely).
        self._drain_state_queue()
        # Click counts every 200ms; reconcile as fallback in case a callback
        # was missed entirely.
        try:
            running = bool(self.engine.is_running)
        except Exception:
            running = False
        if running != getattr(self, "_clicking", False):
            if running:
                reason = getattr(self.engine, "last_start_reason", "hotkey")
            else:
                reason = getattr(self.engine, "last_stop_reason", "hotkey")
            self._set_clicking_state(running, reason)
        try:
            self.stats_label.configure(text=f"Clicks: {getattr(self.engine, 'click_count', 0)}")
            if running:
                if self.status_label.cget("text") != "Status: Clicking...":
                    self.status_label.configure(text="Status: Clicking...", text_color="green")
            else:
                if time.perf_counter() >= self._status_hold_until:
                    if self.status_label.cget("text") not in ("Status: Ready",):
                        # Preserve explicit error/done messages until hold expires;
                        # default back to Ready otherwise.
                        if self._indicator_reason in ("button", "hotkey", "ready"):
                            self.status_label.configure(text="Status: Ready", text_color="gray")
        except Exception:
            pass
        self.after(200, self._update_status_loop)

if __name__ == "__main__":
    app = AutoclickerUI()
    app.mainloop()
