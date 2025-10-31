from tkinter import ttk
import tkinter as tk

print("Module edition chargé avec succès.")


class EditionPage(tk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        label = ttk.Label(parent, text="Menu d'édition")
        label.pack(padx=20, pady=20)
