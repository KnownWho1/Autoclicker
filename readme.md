# Autoclicker Pro

## Introduction
Autoclicker Pro is a high-precision, modern Python desktop application designed for automating mouse clicks at customizable rates. Featuring a sleek dark-themed GUI and a high-performance clicking engine, it is ideal for repetitive tasks, gaming, testing, and any scenario requiring consistent, high-frequency mouse interaction.

## 🚀 Features

- **High-Precision Timing:** Supports fractional millisecond intervals (e.g., `0.002ms`) using a hybrid sleep/busy-wait loop to ensure maximum accuracy.
- **Modern GUI:** Built with `customtkinter` for a sleek, professional user experience.
- **Pick Location System:** Easily capture and save specific screen coordinates to use as a fixed clicking point.
- **Freeze Pointer:** Option to lock the mouse at a recorded location during automated clicking.
- **Hotkey Support:** Start and stop the autoclicker instantly using a configurable global hotkey (Default: `F8`).
- **Persistent Settings:** All your preferences (hotkey, click rate, freeze locations) are automatically saved to a local `config.json` file.
- **Threaded Execution:** The clicking engine runs in a background thread, keeping the `customtkinter` UI responsive at all times.

## 🛠 Tech Stack

- **Python 3.x**
- **CustomTkinter:** For a modern, themed graphical user interface.
- **Pynput:** For low-level, high-speed mouse control.
- **PyAutoGUI:** For high-level mouse interaction (movement and position).
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
2. **Set Interval:** Enter your desired rate in minutes, seconds, and milliseconds (e.g., `0`, `1`, `500`).
3. **Click Type:** Choose between **Single Click** and **Double Click**.
4. **Freeze Location (Optional):**
   - Check the **Freeze Pointer** box.
   - Click the **Pick Location** button and move your mouse to the desired spot. The app will capture and save those coordinates.
5. **Start:** Click the **Start** button or press the **Hotkey** (Default: `F8`) to begin.
6. **Stop:** Click the **Stop** button or press the **Hotkey** again to halt.

## 📂 Project Structure

- `autoclicker.py`: Main entry point.
- `ui.py`: Modern GUI implementation using `customtkinter`.
- `click_engine.py`: Core logic for high-precision clicking and timing.
- `config_manager.py`: Persistence layer for loading/saving configurations.
- `config.json`: Automatically generated file to store your settings.

## ⚖️ License
[Specify License, e.g., MIT]
