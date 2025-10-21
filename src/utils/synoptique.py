import tkinter as tk
from tkinter import ttk
import sqlite3
import variables_communes as vc  # adapte si besoin
from src.utils import u_sql_1 as u_sql_1


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


def preparer_table_tree(parent):
    box = ttk.LabelFrame(parent, text="t_etat_bdd")
    box.pack(fill="both", expand=True, padx=8, pady=8)

    frame = ttk.Frame(box)
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame, show="headings")
    vs = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hs = ttk.Scrollbar(box, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)

    tree.pack(side="left", fill="both", expand=True)
    vs.pack(side="right", fill="y")
    hs.pack(fill="x")

    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM t_etat_bdd")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]

        tree["columns"] = cols
        for c in cols:
            tree.heading(c, text=c)          # en-tête
            tree.column(c, width=120, anchor="w")  # ajuste largeur au besoin

        for r in rows:
            tree.insert("", "end", values=r)
    finally:
        conn.close()

    # bouton rafraîchir (pratique)
    def refresh():
        for i in tree.get_children():
            tree.delete(i)
        conn2 = sqlite3.connect(vc.rep_bdd)
        cur2 = conn2.cursor()
        try:
            cur2.execute("SELECT * FROM t_etat_bdd")
            for r in cur2.fetchall():
                tree.insert("", "end", values=r)
        finally:
            conn2.close()

    btn = ttk.Button(box, text="Rafraîchir", command=refresh)
    btn.pack(pady=4)


def afficher_table():
    root = tk.Tk()
    root.title("Vue t_etat_bdd")
    preparer_table_tree(root)
    root.mainloop()


# Exemple d'utilisation
if __name__ == "__main__":
    afficher_table()
