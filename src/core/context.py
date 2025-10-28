from sqlalchemy import create_engine, MetaData, inspect, __version__  # type: ignore
import tkinter as tk
import parametres
import variables_path
from src.core import data


from pathlib import Path
from .data import Database  # ta classe qui gère SQLite
# si variables_communes.py est à la racine
from ... import variables_communes as config


class AppContext:
    """Contexte global de l'application :
    - chemins
    - connexion à la base
    - configuration partagée
    """

    def __init__(self):
        # Racine du projet (un cran au-dessus de /src)
        self.root_dir = Path(__file__).resolve().parents[2]

        # Dossiers structurants
        self.paths = {
            "sources": self.root_dir / "sources",
            "resultats": self.root_dir / "resultats",
            "data": self.root_dir / "data",
        }

        # Fichier de base de données
        self.db_path = self.paths["data"] / "bdd.sqlite"

        # Instance de base de données
        self.db = Database(self.db_path)

        # Autres variables partagées (optionnelles)
        self.mode_debug = getattr(config, "MODE_DEBUG", False)
        self.version = getattr(config, "VERSION", "1.0.0")


# Singleton : une seule instance réutilisable partout
app_context = AppContext()

if __name__ == '__main__':
    root = tk.Tk()
    cadre = AffichageEcran(root)
    root.mainloop()
