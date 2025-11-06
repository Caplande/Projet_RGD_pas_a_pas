import tkinter as tk
from tkinter import ttk
import sqlite3
from src.core.context import context as ctxt


def creer_vue_base():
    conn = sqlite3.connect(ctxt.path_bdd)
    cur = conn.cursor()

    cur.execute("DROP VIEW IF EXISTS vue_editions_speciales")

    cur.execute("""
        CREATE VIEW vue_editions_speciales AS
        SELECT
            b.exercice,
            b.groupe,
            b.montant,
            b.bat,
            lb.bat_tit_yp,
            b.batrub,
            lbr.batrub_tit_yp,
            lbr.base_rep,
            b.typ,
            lt.typ_tit_yp
        FROM t_base_data AS b
        LEFT JOIN t_lexique_bat AS lb ON b.bat = lb.bat
        LEFT JOIN t_lexique_batrub AS lbr ON b.batrub = lbr.batrub
        LEFT JOIN t_lexique_typ AS lt ON b.typ = lt.typ
        ORDER BY b.bat || b.batrub || b.typ
    """)

    conn.commit()
    conn.close()


def afficher_vue(mon_frame, filtre_typ=None):
    for w in mon_frame.winfo_children():
        w.destroy()

    conn = sqlite3.connect(ctxt.path_bdd)
    cur = conn.cursor()

    requete = "SELECT * FROM vue_editions_speciales"
    params = ()

    if filtre_typ:
        requete += " WHERE typ = ?"
        params = (filtre_typ,)

    cur.execute(requete, params)
    rows = cur.fetchall()
    colonnes = [d[0] for d in cur.description]
    conn.close()

    tree = ttk.Treeview(mon_frame, columns=colonnes, show="headings")
    for col in colonnes:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="w")

    for row in rows:
        tree.insert("", "end", values=row)

    tree.pack(fill="both", expand=True)
