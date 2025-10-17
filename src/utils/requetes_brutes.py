import sys
import sqlite3
import variables_communes as vc
from src.utils import u_sql_1 as u_sql_1

sys.stdout.reconfigure(encoding='utf-8')


def formater_julien(table):
    u_sql_1.convertir_colonne_en_date_julien(table, "debut_periode")
    u_sql_1.convertir_colonne_en_date_julien(table, "fin_periode")
    u_sql_1.convertir_colonne_en_date_julien(table, "date_a")


def controle_recherche_groupe():
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()

    sql = """SELECT id, cle, groupe
        FROM t_base_data
        ORDER BY cle;"""
    cur.execute(sql)
    lignes = cur.fetchall()


if __name__ == "__main__":
    # table = "t_agregation"
    # formater_julien(table)
    # table = "t_base_data"
    # formater_julien(table)
    controle_recherche_groupe()
