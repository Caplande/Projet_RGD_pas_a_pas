from tkinter import ttk
import tkinter as tk

print("Module edition chargé avec succès.")


class EditionPage(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.label = ttk.Label(self, text="Menu d'édition")
        self.label.pack(padx=20, pady=20)
