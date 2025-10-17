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
    # u_sql_1.vider_table("t_etat_bdd")
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


def copier_table_avec_structure_et_donnees(source, cible):
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()
    try:
        # récupère la définition SQL de la table source
        cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (source,))
        create_sql = cur.fetchone()
        if not create_sql or not create_sql[0]:
            print(f"⚠️ Table source '{source}' introuvable.")
            return

        # recrée la définition en remplaçant le nom
        create_sql = create_sql[0].replace(source, cible, 1)

        # supprime la table cible si elle existe
        cur.execute(f"DROP TABLE IF EXISTS {cible}")

        # crée la nouvelle table avec même structure
        cur.execute(create_sql)

        # copie les données
        cur.execute(f"INSERT INTO {cible} SELECT * FROM {source}")

        conn.commit()
        print(
            f"✅ Table '{cible}' créée avec structure et données de '{source}'.")
    except Exception as e:
        print("⚠️ Erreur pendant la copie :", e)
    finally:
        conn.close()


def comparer_tables(table1, table2, id_col):
    """
    Compare le contenu de table1 et table2 et affiche les différences,
    en indiquant l'id de table1 et l'id de table2 pour chaque ligne.
    """
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()

    try:
        # Récupère les colonnes hors id pour vérifier schéma
        cur.execute(f"PRAGMA table_info({table1})")
        cols1 = [row[1] for row in cur.fetchall() if row[1] != id_col]
        cur.execute(f"PRAGMA table_info({table2})")
        cols2 = [row[1] for row in cur.fetchall() if row[1] != id_col]

        if cols1 != cols2:
            print(
                "⚠️ Les tables n'ont pas le même schéma ou ordre de colonnes (hors id).")
            print(f"{table1}: {cols1}")
            print(f"{table2}: {cols2}")
            return

        # Construit la condition de jointure sur toutes les colonnes hors id
        join_conditions = " AND ".join([f"t1.{c} = t2.{c}" for c in cols1])

        query = f"""
        -- lignes dans table1 mais pas table2
        SELECT t1.{id_col} AS id_table1, NULL AS id_table2, t1.*
        FROM {table1} t1
        LEFT JOIN {table2} t2 ON {join_conditions}
        WHERE t2.{id_col} IS NULL

        UNION ALL

        -- lignes dans table2 mais pas table1
        SELECT NULL AS id_table1, t2.{id_col} AS id_table2, t2.*
        FROM {table2} t2
        LEFT JOIN {table1} t1 ON {join_conditions}
        WHERE t1.{id_col} IS NULL
        """

        cur.execute(query)
        lignes = cur.fetchall()

        if not lignes:
            print("✅ Les deux tables ont exactement le même contenu.")
            return

        # Utilise la description du curseur pour obtenir les noms exacts des colonnes
        colonnes = [desc[0] for desc in cur.description]

        # Affichage en tableau
        largeurs = [max(len(str(val)) for val in [nom] + [lig[i]
                        for lig in lignes]) for i, nom in enumerate(colonnes)]
        entete = " | ".join(nom.ljust(largeurs[i])
                            for i, nom in enumerate(colonnes))
        print(entete)
        print("-" * len(entete))
        for lig in lignes:
            print(" | ".join(str(val).ljust(
                largeurs[i]) for i, val in enumerate(lig)))

    except Exception as e:
        print("⚠️ Erreur pendant la comparaison :", e)
    finally:
        conn.close()


if __name__ == "__main__":
    # maj_etat_bdd()
    # get_date_importation_site()
    copier_table_avec_structure_et_donnees(
        "t_lexique_cles", "t_lexique_cles_init_temp")
    # comparer_tables("t_lexique_cles", "t_lexique_cles_init_temp", "id")
