from tkinter import ttk
import tkinter as tk
from src.core.context import context as ctxt

print("Module accueil chargé avec succès.")


class AccueilPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ttk.Label(
            self,
            text=f"Bienvenue dans l'application {ctxt.nom_court}",
            style="Accueil.TLabel")  # police, taille, style
        # Application du style Accueil.Tframe à l'écran
        self.configure(style="Accueil.TFrame")
        # NE PAS UTILISER pack. Frame géré en cours de traitement par "place" incompatible avec "pack"
        # Centrer dans le frame
        self.label.place(relx=0.5, rely=0.5, anchor="center")
