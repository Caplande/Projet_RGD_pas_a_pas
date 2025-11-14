from tkinter import ttk
import tkinter as tk
from src.core.context import context as ctxt

print("Module mise_a_jour chargé avec succès.")

if False:
    class MiseAJourPage(ttk.Frame):
        def __init__(self, parent):
            super().__init__(parent)

            self.label = ttk.Label(
                self,
                text="Menu de mise à jour",
                style="Accueil.TLabel")  # police, taille, style
            self.avancement = ttk.Label(
                self,
                style="Avancement.TLabel"
            )
            # Application du style Accueil.Tframe à l'écran
            self.configure(style="Accueil.TFrame")
            # NE PAS UTILISER pack. Frame géré en cours de traitement par "place" incompatible avec "pack"
            # Centrer dans le frame
            self.label.place(relx=0.5, rely=0.5, anchor="center")
            self.avancement.place(relx=0.5, rely=0.7, anchor="center")
            # Mise à jour de la barre d'état
            ctxt.ecran.maj_barre_etat()  # type: ignore


class MiseAJourPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.label = ttk.Label(
            self,
            text="Menu de mise à jour",
            style="Accueil.TLabel")  # police, taille, style
        self.avancement = ttk.Label(
            self,
            text="Avancement....",
            style="Avancement.TLabel"
        )
        self.label.pack()
        self.avancement.pack()
        # Application du style Accueil.Tframe à l'écran
        self.configure(style="Accueil.TFrame")

        ctxt.ecran.maj_barre_etat()  # type: ignore
