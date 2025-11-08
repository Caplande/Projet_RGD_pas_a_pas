import sqlite3
from src.core.context import context as ctxt


def creer_vue_base():
    """Crée ou recrée la vue complète 'vue_editions_speciales' sans filtre."""
    conn = sqlite3.connect(ctxt.path_bdd)
    cur = conn.cursor()

    cur.execute("DROP VIEW IF EXISTS vue_editions_speciales")

    cur.execute("""
        CREATE VIEW vue_editions_speciales AS
        SELECT
            lbr.base_rep,
            b.exercice,
            b.groupe,
            b.bat,
            lb.bat_tit_yp,
            b.batrub,
            lbr.batrub_tit_yp,
            b.typ,
            lt.typ_tit_yp,
            b.montant
        FROM t_base_data AS b
        LEFT JOIN t_lexique_bat AS lb ON b.bat = lb.bat
        LEFT JOIN t_lexique_batrub AS lbr ON b.batrub = lbr.batrub
        LEFT JOIN t_lexique_typ AS lt ON b.typ = lt.typ
        ORDER BY b.bat || b.batrub || b.typ
    """)

    conn.commit()
    conn.close()


def selectionner_resultats(filtres):
    """
    Récupère les enregistrements de la vue selon les filtres passés sous forme de dict.
    Retourne (colonnes, lignes)
    """
    conn = sqlite3.connect(ctxt.path_bdd)
    cur = conn.cursor()

    conditions = []
    params = {}

    for cle, valeur in filtres.items():
        if valeur:  # ignorer les filtres vides
            conditions.append(f"{cle} = :{cle}")
            params[cle] = valeur

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
        SELECT *
        FROM vue_editions_speciales
        {where_clause}
        ORDER BY bat || batrub || typ
    """

    cur.execute(sql, params)
    lignes = cur.fetchall()

    colonnes = [desc[0] for desc in cur.description]

    conn.close()
    return colonnes, lignes


def valeurs_possibles_vues():
    """Renvoie un dict {champ: [valeurs_distinctes]} pour alimenter les comboboxes."""
    conn = sqlite3.connect(ctxt.path_bdd)
    cur = conn.cursor()

    champs = ["exercice", "groupe", "batrub", "typ", "base_rep"]
    valeurs = {}

    for champ in champs:
        try:
            cur.execute(
                f"SELECT DISTINCT {champ} FROM vue_editions_speciales ORDER BY {champ}"
            )
            valeurs[champ] = [row[0]
                              for row in cur.fetchall() if row[0] is not None]
        except sqlite3.OperationalError:
            valeurs[champ] = []

    conn.close()
    return valeurs


def filtrer_vues(filtres):
    """Simplifie l’accès : renvoie directement les résultats filtrés."""
    return selectionner_resultats(filtres)


def calcul_montant_total(filtres):
    conn = sqlite3.connect(ctxt.path_bdd)
    cur = conn.cursor()

    conditions = []
    params = {}

    for cle, valeur in filtres.items():
        if valeur:  # ignorer les filtres vides
            conditions.append(f"{cle} = :{cle}")
            params[cle] = valeur

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
        SELECT SUM(montant)
        FROM vue_editions_speciales
        {where_clause}
        ORDER BY bat || batrub || typ
    """

    cur.execute(sql, params)
    total = cur.fetchone()[0]
    conn.close()
    return total
