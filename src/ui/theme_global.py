import tkinter as tk
from tkinter import ttk
from parametres import PALETTE, POLICE


def definir_theme_global():
    """Crée et applique un thème ttk global basé sur les variables PALETTES et POLICES du projet."""

    style = ttk.Style()
    style.theme_use("clam")  # base neutre, largement compatible

    """
    # --- Palette extraite du projet ---
    fond = palette.get("fond", "#f0f0f0")
    accent = palette.get("accent", "#4078c0")
    texte = palette.get("texte", "#2c3e50")
    fond_cadre = palette.get("fond_cadre", fond)

    # --- Polices issues du projet ---
    font_normale = polices.get("normale", ("Segoe UI", 10))
    font_titre = polices.get("titre", ("Segoe UI", 12, "bold"))
    font_bouton = polices.get("bouton", font_normale)
    """

    fond = get_palette('fond', "#f0f0f0")
    accent = get_palette('accent', "#4078c0")
    texte = get_palette('texte', "#2c3e50")
    fond_cadre = get_palette('fond_cadre', "#999999")
    erreur = get_palette('erreur', "#ee2f2f")
    fond_barre_etat = get_palette('barre_etat', "#0B3D2E")
    secondaire = get_palette('secondaire', "#7f8c8d")
    font_normale = get_police('texte', ("Segoe UI", 10))
    font_titre = get_police('titre', ("Segoe UI", 12, "bold"))
    font_bouton = get_police('bouton', font_normale)
    font_barre_etat = get_police('barre_etat', ("Segoe UI", 9, "normal"))
    # --- Styles de base ---
    # === Styles généraux ===
    style.configure("TFrame", background=fond)
    style.configure("TLabel", background=fond,
                    foreground=texte, font=font_normale)
    style.configure("TButton",
                    background=accent,
                    foreground="white",
                    font=font_bouton,
                    padding=(8, 4))
    style.map("TButton",
              background=[("active", _assombrir(accent, 0.85))],
              relief=[("pressed", "sunken"), ("!pressed", "raised")])
    style.configure("TEntry",
                    fieldbackground="white",
                    foreground=texte,
                    font=font_normale,
                    padding=3)

    # === Variantes ===
    # Label de titre
    style.configure("FondBarreEtat.TFrame",
                    background=fond_barre_etat,
                    relief="flat")
    style.configure("LabelBarreEtat.TLabel",
                    background=fond_barre_etat,
                    foreground="white",
                    font=font_barre_etat)
    style.configure("Accueil.TFrame",
                    background=fond,
                    borderwidth=2)
    style.configure("Accueil.TLabel",
                    font=("Helvetica", 16, "bold"),
                    foreground="#16073B")
    style.configure("Titre.TLabel",
                    font=font_titre,
                    foreground=accent,
                    background=fond)

    # Cadre structurant
    style.configure("Cadre.TFrame",
                    background=fond_cadre,
                    relief="groove",
                    borderwidth=2)

    # Label d’erreur
    style.configure("Erreur.TLabel",
                    foreground=erreur,
                    background=fond,
                    font=font_normale)

    # Bouton secondaire (gris neutre)
    style.configure("Secondaire.TButton",
                    background=secondaire,
                    foreground="white",
                    font=font_bouton)
    style.map("Secondaire.TButton",
              background=[("active", _assombrir(secondaire, 0.85))])

    # Entrée désactivée (fond grisé)
    style.configure("Disabled.TEntry",
                    fieldbackground="#e0e0e0",
                    foreground="#7f8c8d",
                    font=font_normale)

    return style


def _assombrir(couleur_hex, facteur):
    """Assombrit une couleur hex (facteur entre 0 et 1)."""
    couleur_hex = couleur_hex.lstrip('#')
    r, g, b = tuple(int(couleur_hex[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = [int(x * facteur) for x in (r, g, b)]
    return f"#{r:02x}{g:02x}{b:02x}"


def get_palette(cle, defaut="#ffffff"):
    valeur = PALETTE.get(cle, defaut)
    if cle not in PALETTE:
        print(f"(défaut) {cle} = {defaut}")
    return valeur


def get_police(cle, defaut=("Segoe UI", 10)):
    valeur = POLICE.get(cle, defaut)
    if cle not in POLICE:
        print(f"(défaut) {cle} = {defaut}")
    return valeur
