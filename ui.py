import customtkinter as ctk
from click_engine import ClickEngine
from config_manager import load_config, save_config
import pyautogui
import threading
import time

class AutoclickerUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Autoclicker Pro")
        self.geometry("520x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Load config
        self.config = load_config()
        self.engine = ClickEngine(self.config)

        # UI Layout
        self.setup_ui()
        self.after(500, self._update_status_loop)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(self, text="Autoclicker Pro", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=20)

        # Click Rate Section
        rate_frame = ctk.CTkFrame(self)
        rate_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        rate_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(rate_frame, text="Interval").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.min_entry = ctk.CTkEntry(rate_frame, placeholder_text="Min", width=80)
        self.min_entry.insert(0, str(self.config.get("click_rate_min", 0)))
        self.min_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.sec_entry = ctk.CTkEntry(rate_frame, placeholder_text="Sec", width=80)
        self.sec_entry.insert(0, str(self.config.get("click_rate_sec", 0)))
        self.sec_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.ms_entry = ctk.CTkEntry(rate_frame, placeholder_text="ms", width=80)
        self.ms_entry.insert(0, str(self.config.get("click_rate_ms", 500.0)))
        self.ms_entry.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        rate_frame.grid_columnconfigure((0,1,2), weight=1)

        # Type & Button Section
        type_frame = ctk.CTkFrame(self)
        type_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        type_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(type_frame, text="Click Type").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.type_var = ctk.StringVar(value=self.config.get("click_type", "single"))
        ctk.CTkRadioButton(type_frame, text="Single", variable=self.type_var, value="single").grid(row=1, column=0, padx=10, pady=2, sticky="w")
        ctk.CTkRadioButton(type_frame, text="Double", variable=self.type_var, value="double").grid(row=1, column=1, padx=10, pady=2, sticky="w")
        ctk.CTkRadioButton(type_frame, text="Triple", variable=self.type_var, value="triple").grid(row=1, column=2, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(type_frame, text="Button").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.button_var = ctk.StringVar(value=self.config.get("click_button", "left"))
        ctk.CTkOptionMenu(type_frame, variable=self.button_var, values=["left","right","middle"]).grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        type_frame.grid_columnconfigure(0, weight=1)

        # Safety Section
        safety_frame = ctk.CTkFrame(self)
        safety_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        safety_frame.grid_columnconfigure(0, weight=1)

        self.max_cps_var = ctk.CTkEntry(safety_frame, placeholder_text="Max CPS (0=off)")
        self.max_cps_var.insert(0, str(self.config.get("max_cps", 0)))
        self.max_cps_var.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.max_clicks_var = ctk.CTkEntry(safety_frame, placeholder_text="Max Clicks (0=off)")
        self.max_clicks_var.insert(0, str(self.config.get("max_clicks", 0)))
        self.max_clicks_var.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.jitter_var = ctk.BooleanVar(value=self.config.get("jitter_enabled", False))
        ctk.CTkCheckBox(safety_frame, text="Enable Jitter", variable=self.jitter_var).grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.jitter_range_var = ctk.CTkEntry(safety_frame, placeholder_text="Jitter Range ms")
        self.jitter_range_var.insert(0, str(self.config.get("jitter_range_ms", 10.0)))
        self.jitter_range_var.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Freeze Pointer Section
        freeze_frame = ctk.CTkFrame(self)
        freeze_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        freeze_frame.grid_columnconfigure(0, weight=1)
        
        self.freeze_var = ctk.BooleanVar(value=self.config.get("freeze_pointer", True))
        ctk.CTkCheckBox(freeze_frame, text="Freeze Pointer", variable=self.freeze_var).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.freeze_x_entry = ctk.CTkEntry(freeze_frame, placeholder_text="X")
        self.freeze_x_entry.insert(0, str(self.config.get("freeze_x", 500)))
        self.freeze_x_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.freeze_y_entry = ctk.CTkEntry(freeze_frame, placeholder_text="Y")
        self.freeze_y_entry.insert(0, str(self.config.get("freeze_y", 500)))
        self.freeze_y_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Pick Location Section
        self.pick_btn = ctk.CTkButton(self, text="Pick Location", command=self.pick_location)
        self.pick_btn.grid(row=5, column=0, padx=20, pady=5)

        # Hotkey Section
        hotkey_frame = ctk.CTkFrame(self)
        hotkey_frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        self.hotkey_label = ctk.CTkLabel(hotkey_frame, text=f"Hotkey: {self.config.get('hotkey','F8')}  |  Emergency Stop: {self.config.get('emergency_stop_hotkey','F9')}")
        self.hotkey_label.grid(row=0, column=0, padx=10, pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=7, column=0, padx=20, pady=20)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.start_btn = ctk.CTkButton(btn_frame, text="Start", command=self.start_clicking, fg_color="green", hover_color="darkgreen")
        self.start_btn.grid(row=0, column=0, padx=10, pady=10)

        self.stop_btn = ctk.CTkButton(btn_frame, text="Stop", command=self.stop_clicking, fg_color="red", hover_color="darkred", state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=10, pady=10)

        # Status
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=8, column=0, padx=20, pady=5, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(status_frame, text="Status: Ready", text_color="gray")
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.stats_label = ctk.CTkLabel(status_frame, text="Clicks: 0", text_color="gray")
        self.stats_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")

    def pick_location(self):
        self.status_label.configure(text="Status: Move mouse to target... (3s)", text_color="yellow")
        self.pick_btn.configure(state="disabled")
        def capture():
            try:
                x, y = pyautogui.position()
                self.freeze_x_entry.delete(0, "end")
                self.freeze_x_entry.insert(0, str(x))
                self.freeze_y_entry.delete(0, "end")
                self.freeze_y_entry.insert(0, str(y))
                self.config["freeze_x"] = x
                self.config["freeze_y"] = y
                save_config(self.config)
                self.status_label.configure(text=f"Location Picked: {x}, {y}", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"Error picking location: {e}", text_color="red")
            finally:
                self.pick_btn.configure(state="normal")
        threading.Thread(target=capture, daemon=True).start()
        self.after(3000, lambda: self.status_label.configure(text="Status: Ready", text_color="gray") if self.status_label.cget("text").startswith("Status: Move") else None)

    def start_clicking(self):
        try:
            mins = float(self.min_entry.get() or 0)
            secs = float(self.sec_entry.get() or 0)
            ms = float(self.ms_entry.get() or 500)
            fx = int(self.freeze_x_entry.get() or 0)
            fy = int(self.freeze_y_entry.get() or 0)
            max_cps = float(self.max_cps_var.get() or 0)
            max_clicks = int(self.max_clicks_var.get() or 0)
            jitter_enabled = self.jitter_var.get()
            jitter_range = float(self.jitter_range_var.get() or 0)

            cfg_update = {
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
            self.engine.update_config(cfg_update)
            # Persist
            self.config.update(cfg_update)
            save_config(self.config)
            # Update hotkey label
            self.hotkey_label.configure(text=f"Hotkey: {self.config.get('hotkey','F8')}  |  Emergency Stop: {self.config.get('emergency_stop_hotkey','F9')}")

            self.engine.start()
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.status_label.configure(text="Status: Clicking...", text_color="green")
        except ValueError:
            self.status_label.configure(text="Error: Invalid input", text_color="red")

    def stop_clicking(self):
        self.engine.stop()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Ready", text_color="gray")

    def _update_status_loop(self):
        # Update stats every 500ms
        if self.engine.is_running:
            clicks = getattr(self.engine, "click_count", 0)
            self.stats_label.configure(text=f"Clicks: {clicks}")
            self.status_label.configure(text="Status: Clicking...", text_color="green")
        else:
            self.stats_label.configure(text=f"Clicks: {getattr(self.engine, 'click_count', 0)}")
            if self.status_label.cget("text") != "Status: Ready":
                # keep ready if stopped
                self.status_label.configure(text="Status: Ready", text_color="gray")
        self.after(500, self._update_status_loop)

if __name__ == "__main__":
    app = AutoclickerUI()
    app.mainloop()
