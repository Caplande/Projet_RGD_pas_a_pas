import sqlite3
import json
import variables_communes as vc
from src.utils import u_sql_1 as u_sql_1, u_gen as u_gen


def maj_etat_bdd():
    creer_table_etat_bdd_vide()
    alimenter_etat_bdd()


def creer_table_etat_bdd_vide():
    conn = sqlite3.connect(vc.rep_bdd)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS t_etat_bdd (
            intitule TEXT(30),
            valeur TEXT
        );
    """)
    u_sql_1.vider_table("t_etat_bdd")
    conn.close()


def alimenter_etat_bdd():
    conn = sqlite3.connect(vc.rep_bdd)
    donnees = [
        ("Date dernière mise à jour", get_date_importation_site()),
        ("Nombre de lignes t_base_data", u_sql_1.nb_lig("t_base_data")),
        ("Nombre de lignes t_base_data_ante", u_sql_1.nb_lig("t_base_data_ante")),
        ("Nombre de lignes t_roc_modifiee", u_sql_1.nb_lig("t_roc_modifiee")),
        ("Nombre de lignes t_agregation", u_sql_1.nb_lig("t_agregation")),
        ("Nombre de lignes tampon_data", u_sql_1.nb_lig("tampon_data")),
        ("Nombre de doublons dans t_base_data",
         u_sql_1.lister_doublons("t_base_data", "cle")["nb_doublons"]),
        ("Nombre de lignes sans groupe dans t_base_data",
         u_sql_1.nb_avec_colonne_vide("t_base_data", "groupe")),
        ("Nombre de lignes par exercice dans t_base_data",
         json.dumps(u_sql_1.compter_par_exercice()))
    ]

    conn.executemany(
        "INSERT INTO t_etat_bdd (intitule, valeur) VALUES (?, ?)", donnees)
    conn.commit()
    conn.close()
    print(f"✅ La table des indicateurs t_etat_bdd a été mise à jour")


def get_date_importation_site():
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT valeur 
            FROM t_parametres 
            WHERE indicateur = 'Date importation site'
            LIMIT 1
        """)
        row = cur.fetchone()
        return u_gen.convertir_date(row[0]) if row else None
    except Exception as e:
        print("❌ Erreur pendant la lecture :", e)
        return None
    finally:
        conn.close()


if __name__ == "__main__":
    maj_etat_bdd()
    # get_date_importation_site()
