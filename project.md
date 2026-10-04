# Autoclicker

A high-precision, modern Python desktop application for automating mouse clicks. 

## 🚀 Features

- **High-Precision Timing:** Supports fractional milliseconds (e.g., 0.002ms) using a hybrid sleep/busy-wait loop for maximum accuracy.
- **Modern GUI:** Built with `customtkinter` for a sleek, dark-themed interface.
- **Hotkey Support:** Configurable global hotkey for starting/stopping (Default: `F8`).
- **Pointer Freeze:** Option to lock the mouse at a specific coordinate.
- **Persistent Settings:** Automatically saves your preferences (hotkey, rate, etc.) to a local config file.
- **Threaded Execution:** Ensures the UI remains buttery smooth while the clicking engine runs in the background.

## 🛠 Tech Stack

- **Python 3.x**
- **CustomTkinter:** Modernized Tkinter widgets.
- **PyAutoGUI:** Mouse simulation.
- **Pynput:** Low-level mouse control.
- **Keyboard:** Hotkey registration.
- **Threading:** Concurrent execution.

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

## 📂 Project Structure

- `autoclicker.py`: Main entry point.
- `ui.py`: Main GUI implementation.
- `click_engine.py`: Core clicking logic and timing engine.
- `config_manager.py`: Configuration loading and saving.
- `config.json`: Persisted user settings.

## ⚖️ License
[Specify License, e.g., MIT]
