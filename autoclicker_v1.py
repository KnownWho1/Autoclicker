"""
Autoclicker Application

This script provides a GUI application that allows users to 
automate mouse clicking at a specified rate.
Users can set the click rate in minutes, seconds, and milliseconds,
and start or stop the autoclicker.
Additionally, the application supports changing the hotkey used to toggle the autoclicker on or off.

Dependencies:
- tkinter: For the GUI.
- threading: To run the autoclicker in a separate thread.
- pyautogui: For simulating mouse clicks.
- keyboard: For registering and using a hotkey to toggle the autoclicker.

Usage:
Run this script to launch the autoclicker application. 
Set the desired click rate and use the GUI buttons or the specified 
hotkey to control the autoclicker.

Author: KnownWho
Version: 1.0
Last Updated: 25/02/2024
"""

import tkinter as tk
import threading
import time
import pyautogui
import keyboard

class AutoclickerApp:
    """
    A GUI application for an autoclicker that allows users to set 
    a click rate and start/stop the autoclicking
    with both a GUI button and a hotkey.
    """

    def __init__(self, master):
        """
        Initializes the AutoclickerApp with a master tkinter window, 
        sets up the GUI, and registers a hotkey for toggling autoclicking.

        :param master: The tkinter master window.
        """
        self.master = master
        master.title("Autoclicker")

        self.click_rate_minutes = tk.StringVar(value="0")  # Default click rate in minutes
        self.click_rate_seconds = tk.StringVar(value="0")  # Default click rate in seconds
        self.click_rate_ms = tk.StringVar(value="500")  # Default click rate in milliseconds
        self.hotkey = "F8"  # Default hotkey

        self.setup_gui()

        self.is_autoclicking = False
        self.autoclick_thread = None

        # Register hotkey for toggling the autoclicker.
        keyboard.add_hotkey(self.hotkey, self.on_hotkey_press)

    def setup_gui(self):
        """
        Sets up the graphical user interface for the autoclicker application,
          including input fields for click rate
        and buttons for starting/stopping autoclicking.
        """
        main_frame = tk.Frame(self.master)
        main_frame.pack(padx=10, pady=10)

        # Frame for setting the click rate.
        click_rate_frame = tk.Frame(main_frame)
        click_rate_frame.pack(pady=5)

        # Label and entry fields for click rate.
        self.label_click_rate = tk.Label(click_rate_frame, text="Click Rate (min, sec, ms):")
        self.label_click_rate.grid(row=0, column=0, padx=5, sticky=tk.W)

        self.click_rate_minutes_entry = tk.Entry(click_rate_frame,
                                                 textvariable=self.click_rate_minutes, width=5)
        self.click_rate_minutes_entry.grid(row=0, column=1, padx=5)

        self.click_rate_seconds_entry = tk.Entry(click_rate_frame,
                                                  textvariable=self.click_rate_seconds, width=5)
        self.click_rate_seconds_entry.grid(row=0, column=2, padx=5)

        self.click_rate_ms_entry = tk.Entry(click_rate_frame,
                                             textvariable=self.click_rate_ms, width=5)
        self.click_rate_ms_entry.grid(row=0, column=3, padx=5)

        # Button for applying the set click rate.
        time_apply_button = tk.Button(click_rate_frame, text="OK", command=self.apply_time)
        time_apply_button.grid(row=0, column=4, padx=5)

        # Frame and button for changing the hotkey.
        hotkey_frame = tk.Frame(main_frame)
        hotkey_frame.pack(pady=5)

        self.change_hotkey_button = tk.Button(hotkey_frame, text="Change Hotkey",
                                               command=self.change_hotkey)
        self.change_hotkey_button.grid(row=0, column=0, padx=5)

        self.hotkey_label = tk.Label(hotkey_frame, text="Hotkey: " + self.hotkey)
        self.hotkey_label.grid(row=0, column=1, padx=5)

        # Frame and buttons for starting/stopping autoclicking.
        action_frame = tk.Frame(main_frame)
        action_frame.pack(pady=5)

        self.start_button = tk.Button(action_frame, text="Start", command=self.toggle_autoclicker)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(action_frame, text="Stop", command=self.stop_autoclicker)
        self.stop_button.grid(row=0, column=1, padx=5)
        self.stop_button.config(state=tk.DISABLED) # Initially disable the stop button.

    def change_hotkey(self):
        """
        Temporarily disables the hotkey change button and captures a new 
        hotkey through a temporary entry widget.
        """
        # Temporarily disable the change hotkey button
        self.change_hotkey_button.config(state=tk.DISABLED)
        # Create a temporary entry widget for capturing the new hotkey
        temp_entry = tk.Entry(self.master)
        temp_entry.pack()

        # Focus on the new entry widget to capture the next key press
        temp_entry.focus_set()

        # Bind the key press event to a method that sets the new hotkey
        temp_entry.bind('<Key>', self.capture_new_hotkey)

    def capture_new_hotkey(self, event):
        """
        Captures the new hotkey from the temporary entry widget,
          updates the hotkey, and cleans up the temporary widget.

        :param event: The key event that triggered this callback.
        """
        # Use the event char or keysym as the new hotkey
        new_hotkey = event.keysym
        keyboard.remove_hotkey(self.hotkey)  # Remove the old hotkey
        self.hotkey = new_hotkey  # Set the new hotkey
        keyboard.add_hotkey(self.hotkey, self.on_hotkey_press)  # Register the new hotkey

        # Update the hotkey label
        self.hotkey_label.config(text="Hotkey: " + self.hotkey.capitalize())
        # Remove the temporary entry widget after setting the new hotkey
        event.widget.destroy()
        # Re-enable the change hotkey button
        self.change_hotkey_button.config(state=tk.NORMAL)


    def on_hotkey_press(self):
        """
        Toggles the autoclicker on or off in response to the hotkey press.
        """
        self.toggle_autoclicker()

    def toggle_autoclicker(self):
        """
        Toggles the state of the autoclicker, either starting or stopping
          the autoclick thread based on the current state.
        """
        self.is_autoclicking = not self.is_autoclicking
        if self.is_autoclicking:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.autoclick_thread = threading.Thread(target=self.autoclick)
            self.autoclick_thread.start()
        else:
            self.stop_autoclicker()

    def stop_autoclicker(self):
        """
        Stops the autoclicker and updates the GUI to reflect the stopped state.
        """
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.is_autoclicking = False

    def apply_time(self):
        """
        Applies the click rate settings from the GUI input fields, 
        converting the values to milliseconds.
        """
        try:
            minutes = int(self.click_rate_minutes.get())
            seconds = int(self.click_rate_seconds.get())
            milliseconds = int(self.click_rate_ms.get())
            self.click_rate_ms_total = (minutes * 60 * 1000) + (seconds * 1000) + milliseconds
        except ValueError:
            print("Invalid input for click rate.")
        finally:
            # Remove focus from the entry fields
            self.master.focus_set()  # Set focus to the main window

    def autoclick(self):
        """
        The main loop for autoclicking, which clicks at the interval
          specified by the user until stopped.
        """
        while self.is_autoclicking:
            try:
                # Calculate the click rate on each iteration to always use the latest values
                minutes = int(self.click_rate_minutes.get())
                seconds = int(self.click_rate_seconds.get())
                milliseconds = int(self.click_rate_ms.get())
                click_rate_ms_total = (minutes * 60 * 1000) + (seconds * 1000) + milliseconds
            except ValueError:
                click_rate_ms_total = 500  # Default to 500ms if there's an error in calculation

            pyautogui.click()
            time.sleep(click_rate_ms_total / 1000)


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoclickerApp(root)
    root.mainloop()
