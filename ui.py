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
        self.geometry("400x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Load config
        self.config = load_config()
        self.engine = ClickEngine(self.config)

        # UI Layout
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(self, text="Autoclicker Pro", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=20)

        # Click Rate Section
        rate_frame = ctk.CTkFrame(self)
        rate_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        rate_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(rate_frame, text="Interval:").grid(row=0, column=0, padx=10, pady=10)
        
        self.min_entry = ctk.CTkEntry(rate_frame, placeholder_text="Min", width=70)
        self.min_entry.insert(0, str(self.config.get("click_rate_min", 0)))
        self.min_entry.grid(row=0, column=1, padx=5)

        self.sec_entry = ctk.CTkEntry(rate_frame, placeholder_text="Sec", width=70)
        self.sec_entry.insert(0, str(self.config.get("click_rate_sec", 1)))
        self.sec_entry.grid(row=0, column=2, padx=5)

        self.ms_entry = ctk.CTkEntry(rate_frame, placeholder_text="ms", width=70)
        self.ms_entry.insert(0, str(self.config.get("click_rate_ms", 500)))
        self.ms_entry.grid(row=0, column=3, padx=5)

        # Type Section
        type_frame = ctk.CTkFrame(self)
        type_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.type_var = ctk.StringVar(value=self.config.get("click_type", "single"))
        ctk.CTkRadioButton(type_frame, text="Single Click", variable=self.type_var, value="single").grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkRadioButton(type_frame, text="Double Click", variable=self.type_var, value="double").grid(row=0, column=1, padx=10, pady=10)

        # Freeze Pointer Section
        freeze_frame = ctk.CTkFrame(self)
        freeze_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        freeze_frame.grid_columnconfigure(1, weight=1)
        
        self.freeze_var = ctk.BooleanVar(value=self.config.get("freeze_pointer", True))
        ctk.CTkCheckBox(freeze_frame, text="Freeze Pointer", variable=self.freeze_var).grid(row=0, column=0, padx=10, pady=10)
        
        self.freeze_x_entry = ctk.CTkEntry(freeze_frame, placeholder_text="X", width=70)
        self.freeze_x_entry.insert(0, str(self.config.get("freeze_x", 500)))
        self.freeze_x_entry.grid(row=0, column=1, padx=5)

        self.freeze_y_entry = ctk.CTkEntry(freeze_frame, placeholder_text="Y", width=70)
        self.freeze_y_entry.insert(0, str(self.config.get("freeze_y", 500)))
        self.freeze_y_entry.grid(row=0, column=2, padx=5)

        # Pick Location Section
        self.pick_btn = ctk.CTkButton(self, text="Pick Location", command=self.pick_location)
        self.pick_btn.grid(row=4, column=0, padx=20, pady=5)

        # Hotkey Section
        self.hotkey_label = ctk.CTkLabel(self, text=f"Hotkey: {self.config.get('hotkey', 'F8')}")
        self.hotkey_label.grid(row=5, column=0, padx=20, pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, padx=20, pady=20)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.start_btn = ctk.CTkButton(btn_frame, text="Start", command=self.start_clicking, fg_color="green", hover_color="darkgreen")
        self.start_btn.grid(row=0, column=0, padx=10, pady=10)

        self.stop_btn = ctk.CTkButton(btn_frame, text="Stop", command=self.stop_clicking, fg_color="red", hover_color="darkred", state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=10, pady=10)

        # Status
        self.status_label = ctk.CTkLabel(self, text="Status: Ready", text_color="gray")
        self.status_label.grid(row=7, column=0, padx=20, pady=5)

    def pick_location(self):
        # Simple way to pick: wait 3 seconds for user to move mouse, then capture
        self.status_label.configure(text="Status: Move mouse to target... (3s)", text_color="yellow")
        self.pick_btn.configure(state="disabled")
        
        def capture():
            x, y = pyautogui.position()
            self.freeze_x_entry.delete(0, "end")
            self.freeze_x_entry.insert(0, str(x))
            self.freeze_y_entry.delete(0, "end")
            self.freeze_y_entry.insert(0, str(y))
            
            self.config["freeze_x"] = x
            self.config["freeze_y"] = y
            save_config(self.config)
            
            self.status_label.configure(text=f"Location Picked: {x}, {y}", text_color="green")
            self.pick_btn.configure(state="normal")

        threading.Thread(target=capture, daemon=True).start()
        self.after(3000, lambda: self.status_label.configure(text="Status: Ready", text_color="gray"))

    def start_clicking(self):
        try:
            mins = float(self.min_entry.get())
            secs = float(self.sec_entry.get())
            ms = float(self.ms_entry.get())
            fx = int(self.freeze_x_entry.get())
            fy = int(self.freeze_y_entry.get())
            
            self.engine.update_config({
                "click_rate_min": mins,
                "click_rate_sec": secs,
                "click_rate_ms": ms,
                "click_type": self.type_var.get(),
                "freeze_pointer": self.freeze_var.get(),
                "freeze_x": fx,
                "freeze_y": fy
            })
            save_config(self.engine.config)
            
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

if __name__ == "__main__":
    app = AutoclickerUI()
    app.mainloop()
