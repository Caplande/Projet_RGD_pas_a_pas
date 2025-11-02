import tkinter as tk
from tkinter import ttk
from src.ui.theme_global import definir_theme_global
from src.ui.pages.accueil_page import AccueilPage


"""
# --- Données du projet ---
PALETTE_MODERNE = {
    "fond": "#f5f6fa",       # gris clair
    "fond_cadre": "#e1e4eb",  # gris un peu plus soutenu
    "accent": "#4078c0",     # bleu moyen
    "texte": "#2c3e50"       # gris anthracite
}

POLICES_MODERNES = {
    "normale": ("Segoe UI", 10),
    "titre": ("Segoe UI", 14, "bold"),
    "bouton": ("Segoe UI", 10, "bold")
}
"""

# --- Application principale ---


def main():
    root = tk.Tk()
    root.title("Démo thème global")
    root.geometry("600x400")

    # Appliquer le thème global
    style = definir_theme_global()

    # Création d'un Frame central pour accueillir les pages
    fr_centre = ttk.Frame(root)
    fr_centre.pack(side="top", fill="both", expand=True)

    fr_statut = ttk.Frame(root, height=30, style="BarreEtat.TFrame")
    fr_statut.pack(side="bottom", fill="x")
    """
    label_statut = ttk.Label(
        fr_statut,
        text="Base connectée : exemple.db",
        anchor="w", style="LabelBarreEtat.TFrame"
    )
    label_statut.pack(side="left", padx=10)
    """
    accueil_page = AccueilPage(
        fr_centre, {"nom_application": "abcd des carottes et des navets"})
    accueil_page.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
