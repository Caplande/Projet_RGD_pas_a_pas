from tkinter import ttk
import tkinter as tk
from parametres import NOM_APPLICATION, PALETTES
print("Module accueil chargé avec succès.")


class AccueilPage(tk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        label = ttk.Label(
            self, text=f"Bienvenue dans l'application {NOM_APPLICATION}")
        label.pack(padx=20, pady=20)
