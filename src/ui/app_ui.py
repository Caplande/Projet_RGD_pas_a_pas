import tkinter as tk
from tkinter import ttk
from .menu import build_menu
from src.ui.menu import build_menu
from src.ui.pages.accueil import AccueilPage
import parametres as config

print("Module app_ui chargé avec succès.")


class AppUi(tk.Tk):
    """Fenêtre principale de l'application."""

    def __init__(self, context):
        super().__init__()
        self.context = context

        self.title(f"Mon application - version {context.version}")
        self.geometry("1200x800")
        self.configure(bg="white")

        # Menu principal
        self.config(menu=build_menu(self, context))

        # Contenu de base
        self.label_status = tk.Label(
            self,
            text=f"Base connectée : {context.db_path.name}",
            bg="white",
            fg="gray"
        )
        self.label_status.pack(pady=10)

        # Gestion de la fermeture
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Ferme proprement l'application."""
        print("Fermeture de la connexion à la base…")
        self.context.db.close()
        self.destroy()


def launch_ui(context):
    """Point d'entrée pour l'interface."""
    app = AppUi(context)  # Instance de tk.Tk()
    app.mainloop()

# --- Fonctions utilitaires de couleurs---


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def interpolate_color(color1, color2, t):
    """Mélange deux couleurs selon t ∈ [0,1]."""
    c1, c2 = hex_to_rgb(color1), hex_to_rgb(color2)
    return rgb_to_hex(tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))


def appliquer_palette(widget, palette):
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
        appliquer_palette(enfant, palette)


def styliser_ttk(palette):
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


def appliquer_theme(root, palette):
    root.configure(bg=palette["fond"])
    styliser_ttk(palette)
    appliquer_palette(root, palette)

# --- Transition douce ---


def transition_theme(root, start_palette, end_palette, steps=20, delay=20):
    """Fait un fondu de start_palette vers end_palette."""
    for i in range(steps + 1):
        t = i / steps
        interm = {k: interpolate_color(start_palette[k], end_palette[k], t)
                  for k in start_palette}
        root.after(i * delay, lambda p=interm: appliquer_theme(root, p))

# --- Interface ---


def main():
    root = tk.Tk()
    root.title("Bascule avec fondu")

    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20)

    tk.Label(frame, text="Mode clair / sombre").pack(pady=10)
    ttk.Entry(frame).pack(fill="x", pady=5)
    ttk.Combobox(frame, values=["Option 1", "Option 2"]).pack(fill="x", pady=5)
    bouton_theme = ttk.Button(frame, text="Changer de thème")
    bouton_theme.pack(pady=15)

    # État
    theme_actuel = {"palette": config.PALETTE_SOMBRE}
    appliquer_theme(root, theme_actuel["palette"])

    def toggle_theme():
        if theme_actuel["palette"] == config.PALETTE_SOMBRE:
            next_palette = config.PALETTE_CLAIRE
        else:
            next_palette = config.PALETTE_SOMBRE
        transition_theme(root, theme_actuel["palette"], next_palette)
        theme_actuel["palette"] = next_palette

    bouton_theme.configure(command=toggle_theme)
    root.mainloop()


if __name__ == "__main__":
    main()
