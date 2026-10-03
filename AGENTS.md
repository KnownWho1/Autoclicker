# Agent Instructions - Autoclicker

## Project Overview
A high-precision Python desktop application for automating mouse clicks with sub-millisecond accuracy.

## High-Signal Facts
- **Architecture:** 
    - `autoclicker.py`: Entry point.
    - `ui.py`: GUI layer using `customtkinter`.
    - `click_engine.py`: Core logic. Uses `pynput.mouse.Controller` for high-speed clicking (avoiding `pyautogui.click` due to internal delays).
    - `config_manager.py`: Persistence layer for `config.json`.
- **High-Precision Timing:** 
    - The engine uses a hybrid wait loop: `time.sleep(0.001)` for >1.5ms and a busy-wait loop for <1.5ms to ensure accuracy for fractional millisecond inputs (e.g., `0.002ms`).
- **Dependencies:** `customtkinter`, `pynput`, `keyboard`, `pyautogui`.
- **Concurrency:** The clicking engine runs in a background `threading.Thread` to keep the `customtkinter` UI responsive.

## Commands & Execution
- **Run App:** `python autoclicker.py`
- **Install Deps:** `pip install pyautogui keyboard customtkinter pynput`

## Operational Gotchas
- **Click Speed:** Never use `pyautogui.click()` for high-frequency requirements; it has a forced delay. Always use `pynput.mouse.Controller`.
- **GUI Blocking:** Ensure any long-running logic (like the clicking loop) is offloaded to a thread to prevent `customtkinter` from hanging.
- **Configuration:** User settings are automatically persisted to `config.json`. Always use `config_manager.py` to load/save settings.
