import tkinter as tk
from tkinter import ttk
from src.core.context import context as ctxt

# On définit une liste de zones communes à la plupart des widgets auxquelles on attribue la composante de la palette courante la plus pertinente.
# Ex fond est associé à l'attribut 'fond' de la palette courante.
# Même principe pour la police.


def definir_theme_global(root=None):
    """
    Crée et applique un thème ttk global qui s'appuie sur les variables PALETTES et POLICES du projet.
    LES PALETTES: Les différentes palettes proposées fournissent un ensemble de couleurs harmonieuses pour l'interface. 
    Chaque ensemble propose une couleur pour un contexte donné (soit un type d'objet, soit une situation donnée...)
    LES POLICES: Les différentes polices proposées fournissent des styles de texte adaptés à divers usages dans l'interface 
    selon le même type de fonctionnement que les palettes.
    UN THEME: Définit un ensemble de styles ttk alimentés par les valeurs des palettes et des polices sélectionnées.
    La règle d'appellation générale d'un style (ex:barre_etat.Tframe) permet d'appliqer ce style à tous les wdgets du même type (ici TFrame)
    Il est possible de définir des variantes (ex: LabelBarreEtat.TLabel) pour des usages spécifiques qui surchargent le style de base (ici TLabel).
    REMARQUE 1: Si les choix faits dans la sélection des couleurs/polices dans les palettes/polices sont harmonieux, alors, les thèmes s'appuyant 
                sur ces choix devraient également être harmonieux.
    REMARQUE 2: Que veut dire changer le thème en vigueur dans l'application ? Cela revient à changer la palette et la police en vigueur, 
                et à redéfinir les styles ttk. La méthode app_ui.definir_theme_global() doit être appelée pour appliquer ces changements.
    """

    style = ttk.Style()
    # base neutre, largement compatible. Autres thèmes pré-construits possibles: "clam", "alt", "default", "vista", "xpnative"
    style.theme_use("clam")

    # Construction des styles généraux. Chaque instruction style.configure(...) contribue à la construction du thème
    # Dans la logique ci-dessus, on précise, par type de widget, la partie du widget à traiter avec une des zones définies ci-dessus.
    # Si l'on veut que le widget soit traité de manière identique pour tous ses pairs
    style.configure("TFrame", background=zne_fond)
    style.configure("TLabel", background=zne_fond,
                    foreground=zne_texte, font=font_normale)
    style.configure("TButton",
                    background=zne_accent,
                    foreground="white",
                    font=font_bouton,
                    padding=(8, 4))
    style.map("TButton",
              background=[("active", _assombrir(zne_accent, 0.85))],
              relief=[("pressed", "sunken"), ("!pressed", "raised")])
    style.configure("TEntry",
                    fieldbackground="white",
                    foreground=zne_texte,
                    font=font_normale,
                    padding=3)

    # Construction des styles pour des widgets utilisés dans des conditions déterminées particulières.
    style.configure("FondBarreEtat.TFrame",
                    background=zne_fond_barre_etat,
                    relief="flat")
    style.configure("LabelBarreEtat.TLabel",
                    background=zne_fond_barre_etat,
                    foreground="white",
                    font=font_barre_etat)
    style.configure("Accueil.TFrame",
                    background=zne_fond,
                    borderwidth=2)
    style.configure("Accueil.TLabel",
                    font=("Helvetica", 16, "bold"),
                    foreground="#61926E")
    style.configure("Titre.TLabel",
                    font=font_titre,
                    foreground=zne_accent,
                    background=zne_fond)

    # Cadre structurant
    style.configure("Cadre.TFrame",
                    background=zne_fond_cadre,
                    relief="groove",
                    borderwidth=2)

    # Label d’erreur
    style.configure("Erreur.TLabel",
                    foreground=zne_erreur,
                    background=zne_fond,
                    font=font_normale)

    # Bouton secondaire (gris neutre)
    style.configure("Secondaire.TButton",
                    background=zne_secondaire,
                    foreground="white",
                    font=font_bouton)
    style.map("Secondaire.TButton",
              background=[("active", _assombrir(zne_secondaire, 0.85))])

    # Entrée désactivée (fond grisé)
    style.configure("Disabled.TEntry",
                    fieldbackground="#e0e0e0",
                    foreground="#7f8c8d",
                    font=font_normale)

    # Visualisation d'un cadre par remplissage d'une couleur repérable
    style.configure("Visualiser.TFrame",
                    fieldbackground="#082f13",
                    foreground="#f5f8f9",
                    font=font_normale)
    return style


def _assombrir(couleur_hex, facteur):
    """Assombrit une couleur hex (facteur entre 0 et 1)."""
    couleur_hex = couleur_hex.lstrip('#')
    r, g, b = tuple(int(couleur_hex[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = [int(x * facteur) for x in (r, g, b)]
    return f"#{r:02x}{g:02x}{b:02x}"


def get_palette(cle, defaut="#ffffff"):
    # Retourne la composante cle de l'ensemble de la palette active
    valeur = ctxt.palette.get(cle, defaut)
    if cle not in ctxt.palette:
        print(f"(défaut) {cle} = {defaut}")
    return valeur


def get_police(cle, defaut=("Segoe UI", 10)):
    # Retourne la composante cle de l'ensemble de la police active
    valeur = ctxt.police.get(cle, defaut)  # type: ignore
    if cle not in ctxt.police:
        print(f"(défaut) {cle} = {defaut}")
    return valeur


zne_fond = get_palette('fond', "#f0f0f0")
zne_accent = get_palette('accent', "#4078c0")
zne_texte = get_palette('texte', "#2c3e50")
zne_fond_cadre = get_palette('fond_cadre', "#999999")
zne_erreur = get_palette('erreur', "#ee2f2f")
zne_fond_barre_etat = get_palette('barre_etat', "#0B3D2E")
zne_secondaire = get_palette('secondaire', "#7f8c8d")
font_normale = get_police('texte', ("Segoe UI", 10))
font_titre = get_police('titre', ("Segoe UI", 12, "bold"))
font_bouton = get_police('bouton', font_normale)
font_barre_etat = get_police('barre_etat', ("Segoe UI", 9, "normal"))

zones = [nom for nom in globals() if nom.startswith("zne_")]
fonts = [nom for nom in globals() if nom.startswith("font_")]


if __name__ == "__main__":
    print(zones, fonts)
