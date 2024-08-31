import tkinter as tk

from ui import Ui

if __name__ == '__main__':
    root = tk.Tk()
    app = Ui(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
