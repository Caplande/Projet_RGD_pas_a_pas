# %pip install sqlalchemy

from pathlib import Path
from sqlalchemy import create_engine, MetaData, inspect, __version__  # type: ignore

print("Module variables_communes chargé avec succès.")


REP_DEFAUT = Path.cwd()
print(f"VC_1 ---> Répertoire par défaut {REP_DEFAUT}")

REP_SOURCE = REP_DEFAUT / "sources"
print(f"VC_2 ---> Répertoire source {REP_SOURCE}")

REP_BDD = REP_DEFAUT / "data" / "bdd.sqlite"

print(f"VC_3 ---> Version SQLAlchemy {__version__}")


try:
    DATABASE_URL = f"sqlite:///{REP_BDD.resolve()}"
    engine = create_engine(DATABASE_URL)
    print(f"VC_4 ---> Création de engine réussie")

except Exception as e:
    print(f"VC_4 ---> Erreur lors de la création de l'engine : {e}")
    print(f"VC_4 ---> Erreur lors de la création de Base : {e}")
