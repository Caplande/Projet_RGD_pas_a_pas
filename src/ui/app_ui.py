import tkinter as tk
from tkinter import ttk
from pathlib import Path
import parametres as config
from .theme_global import definir_theme_global
from src.core.context import context as ctxt
from colorama import Fore, Style

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

        # Dictionnaire des pages initialisé depuis AppUi mais rempli depuis activation_ecran.py (pour éviter référence circulaires)
        self.pages = {}
        # **********************************************************
        # self.after(2000, lambda: (print("Changement de style"),
        #           style.configure("LabelBarreEtat.TLabel", font=("Arial", 40, "bold"))))
        # **********************************************************
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def appliquer_style(self, frame, style_map):
        """Applique un style aux widgets d'un frame donné (simulateur d'héritage)."""
        for child in frame.winfo_children():
            cls = child.winfo_class()
            if isinstance(child, ttk.Label):
                child.configure(style=style_map.get("Label", "TLabel"))
            elif isinstance(child, ttk.Button):
                child.configure(style=style_map.get("Button", "TButton"))

    def afficher_page(self, nom_page):
        # Voir ci-dessus: self.pages est rempli depuis activation_ecran.py
        for p in self.pages.values():
            p.pack_forget()
        page = self.pages[nom_page]
        page.pack(fill="both", expand=True)

    # --- Fonctions utilitaires de couleurs---

    def hex_to_rgb(self, hex_code):
        hex_code = hex_code.lstrip("#")
        return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        return "#%02x%02x%02x" % rgb

    def interpolate_color(self, color1, color2, t):
        """Mélange deux couleurs selon t ∈ [0,1]."""
        c1, c2 = self.hex_to_rgb(color1), self.hex_to_rgb(color2)
        return self.rgb_to_hex(tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))

    def appliquer_palette(self, widget, palette):
        cls = widget.winfo_class().lower()
        if cls in ("frame", "toplevel", "labelframe"):
            widget.configure(bg=palette["fond_cadre"])
        elif cls == "label":
            widget.configure(bg=palette["fond_cadre"], fg=palette["texte"])
        elif cls == "button":
            widget.configure(bg=palette["fond_bouton"], fg=palette["texte"],
                             activebackground=palette["hover_bouton"])
        elif cls == "entry":
            widget.configure(bg=palette["fond_bouton"], fg=palette["texte"],
                             insertbackground=palette["texte"], relief="flat")
        elif cls == "text":
            widget.configure(bg=palette["fond_bouton"], fg=palette["texte"],
                             insertbackground=palette["texte"], relief="flat")
        for enfant in widget.winfo_children():
            self.appliquer_palette(enfant, palette)

    def styliser_ttk(self, palette):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=palette["fond_cadre"],
                        foreground=palette["texte"],
                        fieldbackground=palette["fond_bouton"])
        style.configure("TButton",
                        background=palette["fond_bouton"],
                        foreground=palette["texte"],
                        borderwidth=0, padding=6)
        style.map("TButton", background=[("active", palette["hover_bouton"])])
        style.configure("TEntry",
                        fieldbackground=palette["fond_bouton"],
                        foreground=palette["texte"])
        style.configure("TCombobox",
                        fieldbackground=palette["fond_bouton"],
                        foreground=palette["texte"],
                        arrowcolor=palette["texte"])

    def appliquer_theme(self, palette):
        self.configure(bg=palette["fond"])
        self.styliser_ttk(palette)
        self.appliquer_palette(self, palette)

    def on_close(self):
        """Ferme proprement l'application."""
        print("Fermeture de la connexion à la base…")
        ctxt.db.close()
        self.destroy()
    # --- Transition douce ---

    def changer_palette(self, ctxt):
        frame = tk.Frame(self)
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Mode clair / sombre").pack(pady=10)
        ttk.Entry(frame).pack(fill="x", pady=5)
        ttk.Combobox(frame, values=["Option 1", "Option 2"]).pack(
            fill="x", pady=5)
        bouton_theme = ttk.Button(frame, text="Changer de thème")
        bouton_theme.pack(pady=15)

        # État
        theme_actuel = {"palette": ctxt.palettes["PALETTE_SOMBRE"]}
        self.appliquer_theme(theme_actuel["palette"])

        def toggle_theme():
            if theme_actuel["palette"] == ctxt.palettes["PALETTE_SOMBRE"]:
                next_palette = ctxt.palettes["PALETTE_CLAIRE"]
            else:
                next_palette = ctxt.palettes["PALETTE_SOMBRE"]
            self.transition_theme(theme_actuel["palette"], next_palette)
            theme_actuel["palette"] = next_palette

    def transition_theme(self, start_palette, end_palette, steps=20, delay=20):
        """Fait un fondu de start_palette vers end_palette."""
        for i in range(steps + 1):
            t = i / steps
            interm = {k: self.interpolate_color(start_palette[k], end_palette[k], t)
                      for k in start_palette}
            self.after(
                i * delay, lambda p=interm: self.appliquer_theme(p))

    def toggle_theme(self, theme_actuel, theme_suivant):
        if theme_actuel["palette"] == config.PALETTE_SOMBRE:
            next_palette = config.PALETTE_CLAIRE
        else:
            next_palette = config.PALETTE_SOMBRE
        self.transition_theme(theme_actuel["palette"], next_palette)
        theme_actuel["palette"] = next_palette
