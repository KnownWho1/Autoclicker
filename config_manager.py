import json
import os
import tempfile

CONFIG_FILE = "config.json"
CONFIG_VERSION = 1

DEFAULT_CONFIG = {
    "version": CONFIG_VERSION,
    "hotkey": "F8",
    "emergency_stop_hotkey": "F9",
    "click_type": "single",
    "click_button": "left",
    "freeze_pointer": True,
    "freeze_x": 500,
    "freeze_y": 500,
    "click_rate_min": 0,
    "click_rate_sec": 1,
    "click_rate_ms": 500.0,
    "jitter_enabled": False,
    "jitter_range_ms": 10.0,
    "max_cps": 0,
    "max_clicks": 0,
}

def migrate_config(cfg):
    if not isinstance(cfg, dict):
        return DEFAULT_CONFIG.copy()
    version = cfg.get("version", 0)
    if version < CONFIG_VERSION:
        # Simple migration: copy defaults over missing keys
        # Ensure sane defaults for timing values
        if cfg.get("click_rate_ms", 0) <= 0:
            cfg["click_rate_ms"] = 500.0
        migrated = DEFAULT_CONFIG.copy()
        migrated.update(cfg)
        migrated["version"] = CONFIG_VERSION
        return migrated
    return cfg

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        cfg = migrate_config(cfg)
        # Ensure all defaults present
        merged = DEFAULT_CONFIG.copy()
        merged.update(cfg)
        return merged
    except Exception as e:
        print(f"Error loading config: {e}")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        # Ensure version set
        if "version" not in config:
            config["version"] = CONFIG_VERSION
        # Atomic write
        dir_name = os.path.dirname(os.path.abspath(CONFIG_FILE)) or "."
        fd, temp_path = tempfile.mkstemp(dir=dir_name)
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(config, f, indent=4)
            os.replace(temp_path, CONFIG_FILE)
        except:
            try:
                os.remove(temp_path)
            except:
                pass
            raise
    except Exception as e:
        print(f"Error saving config: {e}")
