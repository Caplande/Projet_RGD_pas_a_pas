
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import text, inspect
import sqlite3
import src.core.variables_metier_path as vc

sys.stdout.reconfigure(encoding='utf-8')

DATABASE_URL = Path.cwd()
print(f"VC_1 ---> Répertoire par défaut {DATABASE_URL}")
REP_BDD = DATABASE_URL / "bdd" / "bdd.sqlite"

conn = sqlite3.connect(REP_BDD)
cur = conn.cursor()
sql = 'INSERT INTO t_base_data (type_appel, libelle1, debut_periode, fin_periode, periode_cloturee, bat, bat_tit, rub, rub_tit, typ, typ_tit, date_a, libelle, reference, montant, nom_fournisseur) SELECT type_appel AS type_appel, libelle1 AS libelle1, debut_periode AS debut_periode, fin_periode AS fin_periode, periode_cloturee AS periode_cloturee, bat AS bat, bat_tit AS bat_tit, rub AS rub, rub_tit AS rub_tit, typ AS typ, typ_tit AS typ_tit, date_a AS date_a, libelle AS libelle, reference AS reference, montant AS montant, nom_fournisseur AS nom_fournisseur FROM t_agregation;'

try:
    cur.execute(sql)   # ou conn.executescript(sql) si plusieurs statements
    conn.commit()
    print("OK")
except Exception as e:
    print("Erreur sqlite:", e)
