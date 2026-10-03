# Autoclicker Application

## Introduction
The Autoclicker Application is a GUI-based tool designed to automate mouse clicking at user-defined intervals. Perfect for a wide range of repetitive tasks, this application offers customizable click rates down to the millisecond and allows for easy toggling on or off via a user-specified hotkey. Built with simplicity and efficiency in mind, our Autoclicker is ideal for gaming, data entry, and any scenario requiring consistent mouse clicks.

## Features
- **GUI for Easy Configuration**: Set your click rate using a simple graphical interface.
- **Customizable Click Rate**: Define click intervals in minutes, seconds, and milliseconds.
- **Hotkey Support**: Start or stop the autoclicker with a hotkey of your choosing.
- **Click Freeze**: Freeze the pointer in 1 location to click, can be toggled on or off in the GUI.
- **Click Recording**: Record the position and click of the mouse pointer.
- **Future Expansion**: I'am committed to adding more features, such as click position settings and proper click recording.

## Installation
To use the Autoclicker Application, you'll need Python installed on your system. Clone the repository or download the source code, then install the required dependencies listed below.

### Dependencies
- `tkinter` for the GUI.
- `threading` for concurrent operations.
- `pyautogui` for simulating mouse clicks.
- `keyboard` for hotkey functionality.
- `pynput` for click recording

Run the following command to install the necessary Python packages:
`pip install pyautogui keyboard pynput`

## Usage
After installing the dependencies, launch the application by running the script:

`python autoclicker.py`

OR

Click on Autoclicker.exe in `\dist`

Set the desired click rate in the GUI, and use the start/stop buttons or the specified hotkey to control the autoclicker.
