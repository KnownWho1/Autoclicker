import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "hotkey": "F8",
    "click_type": "single",
    "freeze_pointer": True,
    "freeze_x": 500,
    "freeze_y": 500,
    "click_rate_min": 0,
    "click_rate_sec": 1,
    "click_rate_ms": 500.0
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")
