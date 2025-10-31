import locale

print("Module parametres chargé avec succès.")

# Mettre la locale française pour les noms de mois/jours
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
print(f"Locale définie sur : {locale.getlocale(locale.LC_TIME)}")

MODE_DEBUG = True
VERSION = "1.0.0"
NOM_APPLICATION = "Copropriété Monica - Exploitation du relevé général des dépenses"

# Ensemble de couleurs harmonieux
PALETTES = {
    "palette_moderne": {
        "fond": "#f5f6fa",          # gris très clair
        "accent": "#4078c0",        # bleu moyen
        "texte": "#2c3e50",         # gris anthracite
        "fond_cadre": "#eaecef",    # gris doux
        "fond_bouton": "#d5d8dc",   # gris clair
        "hover_bouton": "#b0bec5",  # gris bleuté au survol
        "erreur": "#e74c3c",        # rouge vif pour signaler
        "valide": "#27ae60",        # vert apaisant
    },

    "palette_claire": {
        "fond": "#fffaf0",          # ivoire
        "accent": "#e67e22",        # orange doux
        "texte": "#3b3b3b",         # gris foncé
        "fond_cadre": "#fcefe3",    # beige clair
        "fond_bouton": "#f9d7a0",   # sable
        "hover_bouton": "#f0b974",  # plus chaud au survol
        "erreur": "#f44747",        # rouge doux pour signaler
        "valide": "#4ec9b0",        # vert bleuté apaisant
    },

    "palette_sombre": {
        "fond": "#1e1e1e",          # gris très foncé (fond général)
        "accent": "#569cd6",        # bleu doux pour les éléments actifs
        "texte": "#d4d4d4",         # gris clair pour le texte
        "fond_cadre": "#252526",    # léger contraste avec le fond
        "fond_bouton": "#2d2d30",   # ton moyen pour boutons
        "hover_bouton": "#3e3e42",  # un peu plus clair au survol
        "erreur": "#f44747",        # rouge doux pour signaler
        "valide": "#4ec9b0",        # vert bleuté apaisant
    },
    "palette_bleue_pastel": {
        "fond": "#f2f7fb",          # bleu très clair, presque blanc
        "accent": "#7daed3",        # bleu pastel principal
        "texte": "#2e3a46",         # gris bleuté foncé pour la lisibilité
        "fond_cadre": "#e1edf6",    # bleu très pâle pour les zones encadrées
        "fond_bouton": "#c9def0",   # bleu-gris léger
        "hover_bouton": "#b3d2eb",  # un ton au-dessus pour le survol
        "erreur": "#e57373",        # rouge rosé adouci
        "valide": "#81c784",        # vert pastel harmonieux
    },
    "palette_mauve_pastel": {
        "fond": "#f8f4fa",          # mauve très clair, presque blanc
        "accent": "#b79ad4",        # mauve pastel principal
        "texte": "#332f3b",         # gris violacé foncé pour le contraste
        "fond_cadre": "#ece3f3",    # lavande pâle pour les encadrés
        "fond_bouton": "#d9c7e6",   # mauve clair pour les boutons
        "hover_bouton": "#c8b0dc",  # légèrement plus soutenu au survol
        "erreur": "#e57373",        # rouge rosé, toujours doux
        "valide": "#81c784",        # vert tendre qui s’accorde bien au mauve
    }
}
