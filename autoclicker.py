import customtkinter as ctk
from ui import AutoclickerUI

if __name__ == "__main__":
    # Set appearance and theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Start the application
    app = AutoclickerUI()
    app.mainloop()
