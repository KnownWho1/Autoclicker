# Autoclicker Pro

## Introduction
Autoclicker Pro is a high-precision, modern Python desktop application designed for automating mouse clicks at customizable rates. Featuring a sleek dark-themed GUI and a high-performance clicking engine, it is ideal for repetitive tasks, gaming, testing, and any scenario requiring consistent, high-frequency mouse interaction.

## 🚀 Features

- **High-Precision Timing:** Supports fractional millisecond intervals (e.g., `0.002ms`) using a hybrid sleep/busy-wait loop to ensure maximum accuracy. Minimum interval `0.1ms` — use Max CPS / Max Clicks to stay safe.
- **Modern GUI:** Built with `customtkinter` for a sleek, professional user experience. Two-column layout with a persistent description under every field, plus a live `Total: X ms ≈ Y clicks/sec` readout so you always see what the interval controls.
- **Clicking Indicator:** A dedicated `●` dot shows green `CLICKING`, gray `IDLE`, red `STOPPED (EMERGENCY)`, or orange `DONE (MAX CLICKS)` — stays in sync whether you use the buttons, the hotkey, or the emergency stop.
- **Pick Location System:** Easily capture and save specific screen coordinates to use as a fixed clicking point. Click **Pick Location**, move your mouse to the target, and the app captures and saves it after 3 seconds.
- **Freeze Pointer:** Option to lock the mouse at a recorded location during automated clicking.
- **Hotkey Support:** Start and stop instantly with the global hotkey (Default: `F8`). Emergency stop (Default: `F9`) halts immediately, even on long intervals. The hotkey line shows `●` when the hook is live and `⚠` with the reason if registration failed.
- **Click Types:** Single, double, or triple clicks with the left, right, or middle button.
- **Safety Limits:** Max CPS cap, Max Clicks auto-stop, and optional jitter (random ± variation per interval). `0` means off/unlimited.
- **Persistent Settings:** Everything autosaves to `config.json` as you edit (no save button needed) and on window close.
- **Threaded Execution:** The clicking engine runs in a background thread, keeping the `customtkinter` UI responsive at all times.

## 🛠 Tech Stack

- **Python 3.x**
- **CustomTkinter:** For a modern, themed graphical user interface.
- **Pynput:** For low-level, high-speed mouse control (never `pyautogui.click()`, which has a forced delay).
- **PyAutoGUI:** For pointer movement and position capture only.
- **Keyboard:** For global hotkey registration.

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

## 📖 Usage

1. Launch `autoclicker.py`.
2. **Set Interval:** Enter minutes, seconds, and milliseconds — they are added together (e.g., `0`, `1`, `500` = 1.5s). Watch the `Total` readout for the effective rate.
3. **Click Type:** Choose **Single**, **Double**, or **Triple** click, and the mouse button.
4. **Pointer (Optional):**
   - Check the **Freeze Pointer** box.
   - Click the **Pick Location** button and move your mouse to the desired spot. The app will capture and save those coordinates after 3 seconds.
5. **Limits (Optional):** Set **Max CPS** to cap speed, **Max Clicks** to auto-stop, or enable **Jitter** for randomized timing.
6. **Start:** Click the **Start** button or press the **Hotkey** (Default: `F8`) to begin. The indicator turns green.
7. **Stop:** Click the **Stop** button, press the **Hotkey** again, or hit **Emergency Stop** (Default: `F9`) to halt instantly.

Settings save automatically as you change them — including on window close — so your setup is restored next launch.

## ⚙️ Settings (`config.json`)

`hotkey`, `emergency_stop_hotkey`, `click_type`, `click_button`, `freeze_pointer`, `freeze_x`, `freeze_y`, `click_rate_min`, `click_rate_sec`, `click_rate_ms`, `jitter_enabled`, `jitter_range_ms`, `max_cps`, `max_clicks`

## 📂 Project Structure

- `autoclicker.py`: Main entry point.
- `ui.py`: GUI implementation using `customtkinter` (two-column scrollable layout, autosave, clicking indicator).
- `click_engine.py`: Core logic for high-precision clicking and timing (interruptible hybrid wait, hotkey handling).
- `config_manager.py`: Persistence layer for loading/saving configurations (atomic writes, migration).
- `config.json`: Automatically generated file to store your settings.

## ⚖️ License
[Specify License, e.g., MIT]
