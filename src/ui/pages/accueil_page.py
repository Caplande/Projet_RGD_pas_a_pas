from tkinter import ttk
import tkinter as tk
from src.core.context import context as ctxt
import parametres as config

print("Module accueil chargé avec succès.")


class AccueilPage(ttk.Frame):
    nb_instances = 0

    def __init__(self, parent):
        super().__init__(parent)
        AccueilPage.nb_instances += 1
        if AccueilPage.nb_instances > 1:
            print(
                f"******************** AccueilPage.nb_instances = {AccueilPage.nb_instances} ********************")
            breakpoint()
        self.label = ttk.Label(
            self,
            text=config.BIENVENUE,
            style="Accueil.TLabel")  # police, taille, style
        # Application du style Accueil.Tframe à l'écran
        self.configure(style="Accueil.TFrame")
        # NE PAS UTILISER pack. Frame géré en cours de traitement par "place" incompatible avec "pack"
        # Centrer dans le frame
        # self.label.place(relx=0.5, rely=0.5, anchor="center")
        ctxt.set_widget_names(self.label, "label")

        # Mise à jour de la barre d'état
        ctxt.ecran.maj_barre_etat()  # type: ignore
