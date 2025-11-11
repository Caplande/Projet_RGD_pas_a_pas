from tkinter import ttk
import tkinter as tk
# from src.ui.app_ui import ecran

print("Module affichage chargé avec succès.")


class AffichagePage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ttk.Label(
            self, text="Paramétrer les couleurs des widgets d'affichage", style="TLabel")
        self.label.pack(expand=True, padx=20, pady=20)
        self.configure(style="TFrame")
