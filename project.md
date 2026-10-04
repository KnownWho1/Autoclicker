# Autoclicker

A high-precision, modern Python desktop application for automating mouse clicks.

## 🚀 Features

- **High-Precision Timing:** Supports fractional milliseconds (e.g., 0.002ms) using a hybrid sleep/busy-wait loop for maximum accuracy. Minimum interval `0.1ms`; no 50ms clamp. Use `max_cps` / `max_clicks` for safety.
- **Modern GUI:** Built with `customtkinter` for a sleek, dark-themed interface.
- **Hotkey Support:** Configurable global hotkey for starting/stopping (Default: `F8`), plus emergency stop (Default: `F9`).
- **Click Types:** Single, double, triple (`click_engine.py:93`). Buttons: left/right/middle.
- **Pointer Freeze + Picker:** Option to lock the mouse at a specific coordinate. `Pick Location` captures via `pyautogui.position()` after 3s, updates entries, syncs engine, and persists to disk.
- **Persistent Settings:** Autosaves to `config.json` on field edit (`FocusOut`/`Return`), option change (`trace_add`), `Start`, picker, and window close (`WM_DELETE_WINDOW`).
- **Safety:** `max_cps` (0=off), `max_clicks` (0=off), `jitter_enabled` + `jitter_range_ms`.
- **Threaded Execution:** Clicking engine runs in a background `threading.Thread` to keep UI responsive.
- **Clicking Indicator:** Dedicated `●` dot + text in status frame (`ui.py`): green `CLICKING` / `CLICKING (hotkey)`, gray `IDLE` / `IDLE (HOTKEY STOP)`, red `STOPPED (EMERGENCY)`, orange `DONE (MAX CLICKS)`. Green is reserved for an active session only — the hotkey `●` marker and idle states stay gray so startup never looks active. Event-driven via `engine.on_state_change` (reasons: `button`, `hotkey`, `emergency`, `max_clicks`) handed off through a `SimpleQueue` drained on the Tk main thread (`after` nudge + 200ms poll fallback). Start/Stop buttons sync on every transition, including hotkey and force-stop.
- **Interval Markers:** Permanent `Minutes` / `Seconds` / `Milliseconds` labels above the interval fields (placeholders vanish once typed) plus a live `Total: X ms ≈ Y clicks/sec` readout refreshed on every save, so it is always clear what the fields control.

## 🛠 Tech Stack

- **Python 3.x**
- **CustomTkinter:** Modernized Tkinter widgets.
- **Pynput (`pynput.mouse.Controller`):** Low-level mouse control for high-speed clicking. Never use `pyautogui.click()` (forced delay).
- **PyAutoGUI:** `moveTo` / `position` only, with `PAUSE = 0`.
- **Keyboard:** Hotkey registration.
- **Threading:** Concurrent execution.

## 📂 Project Structure

- `autoclicker.py`: Main entry point.
- `ui.py`: Main GUI implementation (`AutoclickerUI`, default `660x880`, min `600x650`). Two-column layout inside a `CTkScrollableFrame`: Interval (full width) → Click Type | Pointer (freeze + pick) → Limits (two-column) → hotkeys → Start/Stop → status/indicator. Every editable field has a persistent gray description below it (placeholders alone vanish once typed) plus a live `Total: X ms ≈ Y clicks/sec` readout.
  - `collect_ui_config()` (`ui.py:137`): single read/validate path for all widgets.
  - `persist_current_settings()` (`ui.py:168`): UI -> `engine.update_config()` -> `config.json` -> hotkey label.
  - `_bind_autosave()` (`ui.py:177`): `trace_add` for radio/option/checkbox vars; `<FocusOut>` + `<Return>` for entries.
  - `on_closing()` (`ui.py:200`): persist + `engine.stop()` + `destroy`, bound via `WM_DELETE_WINDOW`.
  - `_apply_picked_location()` (`ui.py:212`) / `pick_location()` (`ui.py:230`): updates `freeze_x/y` entries, syncs engine immediately (so hotkey-start uses new coords), holds status message 2s via `_status_hold_until`.
  - `_update_status_loop()` (`ui.py:270`): 500ms stats refresh; respects `_status_hold_until` so transient messages are not wiped.
- `click_engine.py`: Core clicking logic and timing engine (`ClickEngine`).
  - `_get_interval_seconds()` (`click_engine.py:79`): `total_ms = min*60000 + sec*1000 + ms`; floor `0.1ms`; jitter `max(0.1, total+jitter)`; `max_cps` enforced as `1000/max_cps`.
  - `_hybrid_wait()` (`click_engine.py:112`): `sleep(min(remaining - 0.001, 0.05))` when `remaining > 0.0015`, else busy-wait. Chunked so F8-stop wakes the worker within ~50ms even on minute-long intervals (a single long sleep would block the hotkey thread in `join()` and make F8 appear dead).
  - `_perform_click()` (`click_engine.py:93`): 1x / 2x / 3x press-release.
  - `update_config()` (`click_engine.py:150`): thread-safe `config.update` + `_apply_config`.
- `config_manager.py`: Configuration loading and saving.
  - `DEFAULT_CONFIG` (`config_manager.py:8`), `CONFIG_VERSION = 1`.
  - `migrate_config()` (`config_manager.py:26`): resets timing to `500ms` only if total interval `<= 0` (allows `ms=0` with `sec>0`).
  - `save_config()` (`config_manager.py:65`): atomic write via `tempfile.mkstemp` + `os.replace`.
- `config.json`: Persisted user settings (all keys in `DEFAULT_CONFIG` + `version`).

## ⚙️ Config Schema (`config.json`)

`version, hotkey, emergency_stop_hotkey, click_type, click_button, freeze_pointer, freeze_x, freeze_y, click_rate_min, click_rate_sec, click_rate_ms, jitter_enabled, jitter_range_ms, max_cps, max_clicks`

## 📋 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/Autoclicker.git
   cd Autoclicker
   ```

2. **Install dependencies:**
   ```bash
   pip install pyautogui keyboard customtkinter pynput
   ```

3. **Run the application:**
   ```bash
   python autoclicker.py
   ```

## Operational Gotchas

- **Click Speed:** Never use `pyautogui.click()`; always `pynput.mouse.Controller`.
- **GUI Blocking:** Clicking loop stays off UI thread; Tkinter widget reads stay on main thread (autosave keeps engine synced so hotkey thread needs no UI access).
- **Hotkeys:** Registered via `keyboard.add_hotkey` in `ClickEngine.__init__`. Registration success/failure is recorded (`hotkey_registered` / `hotkey_error`) and shown in the hotkey label (`●` vs `⚠`). Hotkey callbacks are exception-guarded with console logging so one failure never kills the hook.
- **Invalid Input:** Autosave silently ignores `ValueError`; `Start` surfaces `Error: Invalid input`. `on_closing` keeps last good config.
- **Status Messages:** Use `_status_hold_until` (`time.perf_counter() + seconds`) for transient status; loop must check it before resetting to `Ready`.

## ⚖️ License
[Specify License, e.g., MIT]
