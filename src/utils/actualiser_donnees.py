import variables_communes as vc
import src.modeles as modl
from src.utils import u_gen as u_gen, u_sql as u_sql
from sqlalchemy import create_engine, MetaData, update, inspect

print("Module actualiser_donnees chargé avec succès.")

# 1) Supprimer tables tampon_data, tampon_parametres
u_sql.supprimer_toutes_tables(["tampon_data", "tampon_parametres"])

# 2) Charger les données excel (source_active.xlsm) actualisées
