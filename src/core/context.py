from pathlib import Path
import tkinter as tk
import parametres as config
import variables_path as paths
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

        # Autres variables partagées (optionnelles)
        self.mode_debug = getattr(config, "MODE_DEBUG", False)
        self.version = getattr(config, "VERSION", "xxx.x.x")


# Singleton : une seule instance réutilisable partout
app_context = AppContext()

if __name__ == '__main__':
    liste_attributs = [attr for attr in dir(
        app_context) if not attr.startswith("__")]
    print(liste_attributs)
