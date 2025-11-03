from pathlib import Path
import tkinter as tk
import parametres as config
import src.core.variables_metier_path as vmp
from src.core.data import Database  # ta classe qui gère SQLite


print("Module context chargé avec succès.")


class AppContext:
    """Contexte global de l'application :
    - chemins
    - connexion à la base
    - configuration partagée
    """

    def __init__(self):
        # Constantes descriptives de l'application
        self.mode_debug = getattr(config, "MODE_DEBUG", False)
        self.version = getattr(config, "VERSION", "xxx.x.x")
        self.nom_application = getattr(
            config, "NOM_APPLICATION", "a déterminer")
        self.nom_court = getattr(
            config, "NOM_COURT", "a déterminer")
        self.palettes = getattr(config, "PALETTES", {})
        self.polices = getattr(config, "POLICES", {})
        self.palette = getattr(config, "PALETTE", {})
        self.police = getattr(config, "POLICE", {})
        # Dossiers structurants
        self.paths = {
            "defaut": vmp.REP_DEFAUT,
            "sources": vmp.REP_SOURCE,
            "resultats": vmp.REP_RESULTATS,
            "data": vmp.REP_DATA  # répertoire bdd.sqlite
        }

        # Fichier de base de données
        # self.db_path = self.paths["data"] / "bdd.sqlite"
        self.rep_bdd = vmp.REP_BDD

        # Création de l'instance de base de données et de toutes les fonctionnalités qui lui sont attachées
        self.db = Database()

        # Accès SQLITE à la base de données via SQLAlchemy
        self.engine = vmp.ENGINE


# Singleton : une seule instance réutilisable partout. Créée au moment de l'importation du module context.py depuis main.py
app_context = AppContext()
context = app_context

if __name__ == '__main__':
    liste_attributs = [attr for attr in dir(
        app_context) if not attr.startswith("__")]
    print(liste_attributs)
