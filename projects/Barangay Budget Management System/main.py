# main.py - Application Launcher
import tkinter as tk
from app import BarangayBudgetSystemGUI
import sys

def main():
    # Create the main window
    root = tk.Tk()
    
    # Create the application
    app = BarangayBudgetSystemGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()