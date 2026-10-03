# Autoclicker

A lightweight, cross-platform Python desktop application designed to automate mouse clicks at a customizable rate. This tool is ideal for repetitive tasks, testing, or any scenario where consistent mouse interaction is required.

## 🚀 Features

- **Customizable Click Rate:** Set intervals using minutes, seconds, and milliseconds.
- **Click Types:** Support for both single and double clicks.
- **Hotkey Toggling:** Start and stop the autoclicker instantly using a configurable hotkey (Default: `F8`).
- **Pointer Freeze:** Option to lock the mouse cursor at a specific position during automated clicking.
- **Click Recording:** Record mouse click positions and types to be used for automation (feature in development).
- **Threaded Execution:** Runs the clicking logic in a background thread to ensure the GUI remains responsive.

## 🛠 Tech Stack

- **Python 3.x**
- **Tkinter:** For the graphical user interface.
- **PyAutoGUI:** For high-level mouse simulation.
- **Keyboard:** For global hotkey registration.
- **Pynput:** For low-level mouse event listening (recording).

## 📋 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-repo/Autoclicker.git
   cd Autoclicker
   ```

2. **Install dependencies:**
   ```bash
   pip install pyautogui keyboard pynput
   ```

3. **Run the application:**
   ```bash
   python autoclicker.py
   ```

## 📖 Usage

1. Launch `autoclicker.py`.
2. Enter your desired click interval in the **Click Rate** fields.
3. Choose your **Click Type** (Single or Double) from the Settings menu.
4. (Optional) Check **Freeze Pointer** if you want the mouse to stay on a specific spot.
5. Click **Start** or press `F8` to begin.
6. Click **Stop** or press `F8` again to halt the operation.

## 📂 Project Structure

- `autoclicker.py`: Main entry point and application logic.
- `autoclicker.spec`: Configuration for PyInstaller executables.
- `docs/`: Project documentation.
- `build/` / `dist/`: Compiled output folders.

## ⚖️ License
[Specify License, e.g., MIT]
