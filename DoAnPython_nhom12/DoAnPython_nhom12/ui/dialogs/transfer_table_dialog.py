import tkinter as tk

class TransferTableDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Chuyển bàn")
        self.geometry("300x200")