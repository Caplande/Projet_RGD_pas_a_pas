from pathlib import Path
import tkinter as tk
import parametres as config
import src.core.variables_metier_path as paths
from .data import Database  # ta classe qui gère SQLite


print("Module context chargé avec succès.")


class AppContext:
    """Contexte global de l'application :
    - chemins
    - connexion à la base
    - configuration partagée
    """

    def __init__(self):
        # Racine du projet (un cran au-dessus de /src)
        # self.root_dir = Path(__file__).resolve().parents[2]
        paths.REP_DEFAUT
        # Constantes descriptives de l'application
        self.mode_debug = getattr(config, "MODE_DEBUG", False)
        self.version = getattr(config, "VERSION", "xxx.x.x")
        self.nom_application = getattr(
            config, "NOM_APPLICATION", "a déterminer")
        self.palettes = getattr(config, "PALETTES", {})
        # Dossiers structurants
        self.paths = {
            # "sources": self.root_dir / "sources",
            # "resultats": self.root_dir / "resultats",
            # "data": self.root_dir / "data",
            "sources": paths.REP_SOURCE,
            "resultats": paths.REP_RESULTATS,
            "data": paths.REP_DATA
        }

        # Fichier de base de données
        # self.db_path = self.paths["data"] / "bdd.sqlite"
        self.db_path = paths.REP_BDD

        # Instance de base de données
        self.db = Database(self.db_path)


# Singleton : une seule instance réutilisable partout. Créée au moment de l'importation du module context.py depuis main.py
app_context = AppContext()

if __name__ == '__main__':
    liste_attributs = [attr for attr in dir(
        app_context) if not attr.startswith("__")]
    print(liste_attributs)
