import sqlite3
import json
import re
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


def maj_t_lexique_cles():
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()
    try:
        # comptage initial
        cur.execute("SELECT COUNT(*) FROM t_lexique_cles")
        nb_avant = cur.fetchone()[0]

        # raz complète
        cur.execute("DELETE FROM t_lexique_cles")

        # insertion depuis t_base_data
        cur.execute("""
            INSERT INTO t_lexique_cles (cle, groupe)
            SELECT DISTINCT cle, SUBSTR(COALESCE(groupe, ''), 1, 30)
            FROM t_base_data
            WHERE (cle IS NOT NULL AND TRIM(cle) <> '') AND (groupe IS NOT NULL AND TRIM(groupe) <> '')
        """)
        conn.commit()

        # comptage final
        cur.execute("SELECT COUNT(*) FROM t_lexique_cles")
        nb_apres = cur.fetchone()[0]

        nb_mises_a_jour = nb_apres - nb_avant

        print(
            f"t_lexique_cles: nombre de lignes mises à jour : {nb_mises_a_jour}")
        print(
            f"t_lexique_cles: total de lignes de t_lexique_cles : {nb_apres}")
    except Exception as e:
        print(f"⚠️ Erreur pendant la mise à jour : {e}")
    finally:
        conn.close()


def nettoyer_colonne(t_base_data, nom_colonne):
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()
    try:
        # récupération des valeurs distinctes
        cur.execute(
            f"SELECT DISTINCT {nom_colonne} FROM {t_base_data} WHERE {nom_colonne} IS NOT NULL")
        colonnes = cur.fetchall()

        print("🔍 Vérification des caractères invisibles...")
        anomalies = []
        for (nom,) in colonnes:
            if re.search(r'[\u00A0\u200B\u202F\r\n\t]', nom):
                anomalies.append(nom)

        if anomalies:
            print(
                f"⚠️ {len(anomalies)} valeurs contiennent des caractères invisibles :")
            for nom in anomalies:
                print(f"→ «{nom}»")
        else:
            print("✅ Aucune anomalie détectée.")

        # nettoyage sans changer la casse
        cur.execute(f"""
            UPDATE {t_base_data}
            SET {nom_colonne} = TRIM(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE({nom_colonne}, CHAR(160), ' '),  -- espace insécable
                            CHAR(9), ' '),   -- tabulation
                        CHAR(10), ' '),     -- saut de ligne
                    CHAR(13), ' '),        -- retour chariot
                '\u200B', ''               -- espace zéro largeur (attention : peut ne pas être interprété)
                )
            );
        """)

        conn.commit()

        print("🧹 Nettoyage effectué : caractères invisibles supprimés, espaces nettoyés.")
    except Exception as e:
        print(f"⚠️ Erreur pendant le nettoyage : {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    # maj_etat_bdd()
    # get_date_importation_site()
    # copier_table_avec_structure_et_donnees(
    #    "t_lexique_cles", "t_lexique_cles_ante")
    # comparer_tables("t_lexique_cles", "t_lexique_cles_init_temp", "id")
    # maj_t_lexique_cles()
    nettoyer_colonne('t_base_data', 'nom_fournisseur')
