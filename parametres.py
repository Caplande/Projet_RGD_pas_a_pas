import locale
import importlib
yaml = importlib.import_module("yaml", "yaml")


print("Module parametres chargé avec succès.")

# Mettre la locale française pour les noms de mois/jours
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
print(f"Locale définie sur : {locale.getlocale(locale.LC_TIME)}")


def extraire_themes():
    """Extrait les thèmes disponibles depuis le fichier parametres.yaml"""
    with open("parametres.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        palettes = config.get("PALETTES", {})
        polices = config.get("POLICES", {})
    return palettes, polices


MODE_DEBUG = True
VERSION = "1.0.0"
NOM_APPLICATION = "Copropriété Monica - Exploitation du relevé général des dépenses"
NOM_COURT = "Exploitation du RGD Monica"

# Configuration du theme en vigueur
theme_en_vigueur = {"palette": "palette_moderne", "police": "police_moderne_1"}
palettes, polices = extraire_themes()
PALETTE = palettes.get(theme_en_vigueur["palette"], {})
POLICE = polices.get(theme_en_vigueur["police"], {})
