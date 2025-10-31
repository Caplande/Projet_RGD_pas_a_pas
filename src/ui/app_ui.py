import tkinter as tk
from tkinter import ttk
from .menu import MonMenu
from src.ui.pages.accueil_page import AccueilPage
from src.ui.pages.general_page import GeneralPage
from src.ui.pages.mise_a_jour_page import MiseAJourPage
from src.ui.pages.edition_page import EditionPage
from src.ui.pages.qualite_base_page import QualiteBasePage
from src.ui.pages.affichage_page import AffichagePage


print("Module app_ui chargé avec succès.")


class AppUi(tk.Tk):
    """Fenêtre principale de l'application."""

    def __init__(self, context):
        super().__init__()
        self.context = context

        self.title(
            f"{context.nom_application} (version:{context.version})")
        self.geometry("1200x800")
        # self.configure(bg="white")
        # Ajout des widgets (menu,frames etc...) à l'intérieur de self (fenetre)
        # 1) Menu principal
        mon_menu = MonMenu(self, context)
        self.configure(menu=mon_menu.menubar)
        # 2) Pages
        self.pages = {}
        for P in (AccueilPage, GeneralPage, MiseAJourPage, EditionPage,
                  QualiteBasePage, AffichagePage):
            page = P(self, context)
            # Attention les noms des pages ne répondent pas à la norme PEP8. Ex: l'instance de AccueilPage est stockée sous le nom "AccueilPage" au lieu de "accueil_page".
            self.pages[P.__name__] = page
            page.place(relwidth=1, relheight=1)
        self.afficher_page("AccueilPage")
        # Contenu de base
        self.label_status = tk.Label(
            self,
            text=f"Base connectée : {context.db_path.name}",
            bg="white",
            fg="gray"
        )
        self.label_status.pack(pady=10)

        # Gestion de la fermeture de la fenetre gérée par la méthode on_close (à compléter éventuellement)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Ferme proprement l'application."""
        print("Fermeture de la connexion à la base…")
        self.context.db.close()
        self.destroy()

    def afficher_page(self, nom_page):
        """Affiche la page demandée"""
        page = self.pages[nom_page]
        page.lift()
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

    # --- Transition douce ---
    def changer_palette(self, context):
        frame = tk.Frame(self)
        frame.pack(padx=20, pady=20)

        tk.Label(frame, text="Mode clair / sombre").pack(pady=10)
        ttk.Entry(frame).pack(fill="x", pady=5)
        ttk.Combobox(frame, values=["Option 1", "Option 2"]).pack(
            fill="x", pady=5)
        bouton_theme = ttk.Button(frame, text="Changer de thème")
        bouton_theme.pack(pady=15)

        # État
        theme_actuel = {"palette": context.palettes["PALETTE_SOMBRE"]}
        self.appliquer_theme(theme_actuel["palette"])

        def toggle_theme():
            if theme_actuel["palette"] == context.palettes["PALETTE_SOMBRE"]:
                next_palette = context.palettes["PALETTE_CLAIRE"]
            else:
                next_palette = context.palettes["PALETTE_SOMBRE"]
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


def launch_ui(context):
    """Point d'entrée pour l'interface."""
    app = AppUi(context)  # Instance de tk.Tk()
    app.mainloop()

# --- Interface ---


if __name__ == "__main__":
    pass
