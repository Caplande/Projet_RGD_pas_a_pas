import sys
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import declarative_base, Session

from sqlalchemy import text, inspect

sys.stdout.reconfigure(encoding='utf-8')


def check_engine(engine, check_tables: bool = True):
    """
    Vérifie que l'engine SQLAlchemy fonctionne correctement.

    - Teste une connexion avec SELECT 1
    - Si check_tables=True, liste aussi les tables présentes
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connexion réussie à la base de données.")
    except Exception as e:
        print("❌ Erreur de connexion :", e)
        return False

    if check_tables:
        try:
            insp = inspect(engine)
            tables = insp.get_table_names()
            if tables:
                print("📋 Tables trouvées :", tables)
            else:
                print("⚠️ Aucun table trouvée dans la base.")
        except Exception as e:
            print("❌ Impossible de récupérer la liste des tables :", e)
            return False

    return True


engine = create_engine("sqlite:///./bdd/bdd.sqlite")
check_engine(engine)
Base = declarative_base()

# --- Reflect pour récupérer un objet Table
metadata = MetaData()
tampon_data = Table("tampon_data", metadata, autoload_with=engine)

# --- Création dynamique d'une classe ORM mappée


class TamponData(Base):
    __table__ = tampon_data


# --- Vérification : la classe est bien enregistrée
print("Mappers dans Base :", [
      m.class_.__name__ for m in Base.registry.mappers])

# --- Utilisation avec ORM
with Session(engine) as session:
    rows = session.query(TamponData).all()
    for row in rows:
        print(row.id, row.nom)
