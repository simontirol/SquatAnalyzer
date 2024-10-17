# main.py
from squat_app import SquatApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    root.title("SquatAnalyzer")
    app = SquatApp(root)
    root.mainloop()
