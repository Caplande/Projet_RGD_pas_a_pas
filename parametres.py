import locale

print("Module parametres chargé avec succès.")

# Mettre la locale française pour les noms de mois/jours
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

MODE_DEBUG = True
VERSION = "1.0.0"

# Ensemble de couleurs harmonieux
# Option 1
PALETTE_MODERNE = {
    "fond": "#f5f6fa",          # gris très clair
    "accent": "#4078c0",        # bleu moyen
    "texte": "#2c3e50",         # gris anthracite
    "fond_cadre": "#eaecef",    # gris doux
    "fond_bouton": "#d5d8dc",   # gris clair
    "hover_bouton": "#b0bec5",  # gris bleuté au survol
    "erreur": "#e74c3c",        # rouge vif pour signaler
    "valide": "#27ae60",        # vert apaisant
}
# Option 2
PALETTE_CLAIRE = {
    "fond": "#fffaf0",          # ivoire
    "accent": "#e67e22",        # orange doux
    "texte": "#3b3b3b",         # gris foncé
    "fond_cadre": "#fcefe3",    # beige clair
    "fond_bouton": "#f9d7a0",   # sable
    "hover_bouton": "#f0b974",  # plus chaud au survol
    "erreur": "#f44747",        # rouge doux pour signaler
    "valide": "#4ec9b0",        # vert bleuté apaisant
}
# Option 3
PALETTE_SOMBRE = {
    "fond": "#1e1e1e",          # gris très foncé (fond général)
    "accent": "#569cd6",        # bleu doux pour les éléments actifs
    "texte": "#d4d4d4",         # gris clair pour le texte
    "fond_cadre": "#252526",    # léger contraste avec le fond
    "fond_bouton": "#2d2d30",   # ton moyen pour boutons
    "hover_bouton": "#3e3e42",  # un peu plus clair au survol
    "erreur": "#f44747",        # rouge doux pour signaler
    "valide": "#4ec9b0",        # vert bleuté apaisant
}
