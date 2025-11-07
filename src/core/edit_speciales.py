import tkinter as tk
from tkinter import ttk
import sqlite3
from src.core.context import context as ctxt


def creer_vue_base():
    """Crée une vue complète sans filtre."""
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
    Exemple : filtres = {'typ': '441', 'exercice': '2024'}
    """
    conn = sqlite3.connect(ctxt.path_bdd)
    cur = conn.cursor()

    # Construire la clause WHERE dynamiquement selon les filtres fournis
    conditions = []
    params = {}

    for cle, valeur in filtres.items():
        conditions.append(f"{cle} = :{cle}")
        params[cle] = valeur

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    sql = f"""
        SELECT *
        FROM vue_editions_speciales
        {where_clause}
        ORDER BY bat || batrub || typ
    """

    cur.execute(sql, params)
    resultats = cur.fetchall()
    conn.close()
    return resultats


def afficher_dans_frame():
    creer_vue_base()
    filtres = {
        'typ': '441',
        'exercice': '2024',
        'base_rep': 'CCG/9984'
    }
    lignes = selectionner_resultats(filtres)

    for ligne in lignes:
        ttk.Label(ctxt.ecran.pages["SelectionEnregistrementsPage"].fr_resultats,
                  text=str(ligne)).pack(anchor="w")


def compter_selection(filtre=None):
    conn = sqlite3.connect(ctxt.path_bdd)
    cur = conn.cursor()
    requete = "SELECT count(*) FROM vue_editions_speciales"
    params = ()
    if filtre:
        requete += " WHERE typ = ?"
        params = (filtre,)
    cur.execute(requete, params)
    count = cur.fetchone()[0]

    conn.close()
    return count


def valeurs_possibles_vues():
    """Retourne un dict {champ: [valeurs_uniques]} à partir de vue_editions_speciales."""
    conn = sqlite3.connect(ctxt.path_bdd)
    cur = conn.cursor()
    champs = ["exercice", "groupe", "batrub", "typ", "base_rep"]
    valeurs = {}
    for champ in champs:
        cur.execute(
            f"SELECT DISTINCT {champ} FROM vue_editions_speciales WHERE {champ} IS NOT NULL ORDER BY {champ}")
        valeurs[champ] = [r[0] for r in cur.fetchall()]
    conn.close()
    return valeurs


def filtrer_vues(filtres):
    """
    Utilise selectionner_resultats pour renvoyer les lignes filtrées
    (listes de tuples lisibles dans le Text de SelectionEnregistrementsPage).
    """
    try:
        return selectionner_resultats(filtres)
    except Exception as e:
        print("Erreur lors du filtrage :", e)
        return []
