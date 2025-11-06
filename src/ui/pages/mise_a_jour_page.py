from tkinter import ttk
import tkinter as tk

print("Module mise_a_jour chargé avec succès.")


class MiseAJourPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ttk.Label(
            self, text="Menu de mise à jour", style="TLabel")
        self.label.pack(expand=True, padx=20, pady=20)
        self.configure(style="TFrame")
