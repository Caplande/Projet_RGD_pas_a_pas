from tkinter import ttk
import tkinter as tk

print("Module edition chargé avec succès.")


class EditionPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ttk.Label(
            self, text="Menu édition", style="TLabel")
        self.label.pack(expand=True, padx=20, pady=20)
        self.configure(style="TFrame")
