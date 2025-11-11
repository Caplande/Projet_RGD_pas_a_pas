import yaml
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import parametres as config
from .theme_global import definir_theme_global
from src.core.context import context as ctxt
from colorama import Fore, Style
from src.utils import u_sql_3 as u_sql_3
print("Module app_ui chargé avec succès.")

ecran = None


class AppUi(tk.Tk):
    nb_instances = 0

    def __init__(self):
        # *******************
        AppUi.nb_instances += 1
        if AppUi.nb_instances > 1:
            print(
                Fore.RED + f"Nb instances AppUi = {AppUi.nb_instances}" + Style.RESET_ALL)
        # *******************
        super().__init__()

        self.geometry("1200x800")
        self.title(
            f"{ctxt.nom_application} (version:{ctxt.version})")
        # Les styles
        # Appliquer le thème global
        # Affecte le thème global TFrame à tous les frames, TLabel à tous les labels etc...
        style = definir_theme_global()

        # Création de la racine du menu principal
        self.menubar = tk.Menu(self)
        self.configure(menu=self.menubar)

        # Création d'un Frame central pour accueillir les pages
        self.fr_centre = ttk.Frame(self)
        self.fr_centre.pack(side="top", fill="both", expand=True)

        # Affichage initial: frame de statut: fr_statut et page d'accueil: AccueilPage
        # Affichage de la barre de statut fr_statut
        self.fr_statut = ttk.Frame(
            self, height=25, style="FondBarreEtat.TFrame")
        # Empêcher le redimensionnement automatique
        self.fr_statut.pack_propagate(False)
        self.fr_statut.pack(side="bottom", fill="x")
        self.label_statut_1 = ttk.Label(
            self.fr_statut,
            text=f"Base connectée : {Path(ctxt.path_bdd).name}",
            anchor="w", style="LabelBarreEtat.TLabel"
        )
        self.label_statut_2 = ttk.Label(
            self.fr_statut, anchor="w", style="LabelBarreEtat.TLabel"
        )

        # **********************************************************
        # self.after(2000, lambda: style.configure(
        #    "TLabel", background="yellow"))
        # **********************************************************

        self.label_statut_1.pack(side="left", padx=10)
        self.label_statut_2.pack(side="left", padx=10)

        # **********************************************************
        u_sql_3.appliquer_couleur_jaune_fond(self.fr_centre)
        u_sql_3.appliquer_couleur_bleu_fond(self.fr_statut)
        u_sql_3.appliquer_couleur_vert_fond(self.label_statut_1)
        u_sql_3.appliquer_couleur_orange_fond(self.label_statut_2)
        # **********************************************************

        # Dictionnaire des pages initialisé depuis AppUi mais rempli depuis activation_ecran.py (pour éviter référence circulaires)
        self.pages = {}
        # **********************************************************
        # self.after(2000, lambda: (print("Changement de style"),
        #           style.configure("LabelBarreEtat.TLabel", font=("Arial", 40, "bold"))))
        # **********************************************************
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def afficher_page(self, nom_page):
        # Voir ci-dessus: self.pages est rempli depuis activation_ecran.py
        for p in self.pages.values():
            p.pack_forget()
        page = self.pages[nom_page]
        page.pack(fill="both", expand=True)

    def on_close(self):
        """Ferme proprement l'application."""
        print("Fermeture de la connexion à la base…")
        ctxt.db.close()
        self.destroy()

    def lister_palettes_polices(self):
        with open("parametres.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Accéder au niveau "application" -> "themes"
        palettes = data["PALETTES"]
        polices = data["POLICES"]

        # Créer une liste de choix à partir des clés
        l_palettes = list(palettes.keys())
        l_polices = list(polices.keys())
        print(l_palettes)
        print(l_polices)

    def afficher_choix_palettes_polices(self, event=None):
        def get_theme_selection(event=None):
            palette = bx_palette.get()
            police = bx_police.get()
            print(f"Palette: {palette}, Police: {police}")
            return palette, police

        # --- Frame theme ---
        # ******************************************************
        # self.fr_centre.configure(style="Visualiser.TFrame")
        style = ttk.Style()
        style.configure("Jaune.TFrame", background="yellow")
        self.fr_centre.configure(style="Jaune.TFrame")
        # ******************************************************
        fr_theme = ttk.Frame(ctxt.ecran.pages['page_affichage'], borderwidth=2,  # type: ignore
                             relief="groove", padding=5)
        fr_theme.pack(side="top", anchor="nw", padx=5, pady=5)
        # *******************************************************
        # fr_theme.configure(style="Jaune.TFrame")
        ctxt.ecran.pages['page_affichage'].configure(
            style="Jaune.TFrame")  # type: ignore
        # *******************************************************
        # --- Combobox Palette ---
        ttk.Label(fr_theme, text="Palette:").grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        bx_palette = ttk.Combobox(
            fr_theme, values=["Clair", "Sombre", "Automne", "Bleu pastel"])
        bx_palette.current(0)
        bx_palette.grid(row=0, column=1, padx=5, pady=2)

        # --- Combobox Police ---
        ttk.Label(fr_theme, text="Police:").grid(
            row=1, column=0, sticky="w", padx=5, pady=2)
        bx_police = ttk.Combobox(
            fr_theme, values=["Arial", "Calibri", "Times New Roman", "Courier"])
        bx_police.current(0)
        bx_police.grid(row=1, column=1, padx=5, pady=2)

        # --- Lier les changements à la fonction ---
        bx_palette.bind("<<ComboboxSelected>>", get_theme_selection)
        bx_police.bind("<<ComboboxSelected>>", get_theme_selection)


if __name__ == "__main__":
    app = AppUi()
    app.mainloop()
