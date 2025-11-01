import tkinter as tk
from tkinter import ttk
from src.ui.theme_global import definir_theme_global


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

    # --- Widgets de démonstration ---
    frame_principal = ttk.Frame(root, padding=20)
    frame_principal.pack(fill="both", expand=True)

    titre = ttk.Label(
        frame_principal, text="Interface harmonisée", style="Titre.TLabel")
    titre.pack(pady=10)

    label = ttk.Label(frame_principal, text="Ceci est un label normal.")
    label.pack(pady=5)

    entry = ttk.Entry(frame_principal)
    entry.pack(pady=5, fill="x")

    bouton = ttk.Button(frame_principal, text="Valider")
    bouton.pack(pady=15)

    cadre = ttk.Frame(frame_principal, style="Cadre.TFrame", padding=10)
    cadre.pack(fill="both", expand=True, pady=10)

    ttk.Label(cadre, text="Cadre stylé").pack()

    root.mainloop()


if __name__ == "__main__":
    main()
