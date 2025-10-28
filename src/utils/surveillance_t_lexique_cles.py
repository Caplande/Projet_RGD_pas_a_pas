import sqlite3
import tkinter as tk
from tkinter import messagebox
import variables_path as vc
from src.utils import u_sql_1 as u_sql_1, u_gen as u_gen


def creer_table_surveillance():
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()
    script = """
        CREATE TABLE t_signaux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cle TEXT,
            ancien_groupe TEXT,
            nouveau_groupe TEXT,
            date_modif TEXT
            );

            CREATE TRIGGER trg_update_groupe
            AFTER UPDATE OF groupe ON t_base_data
            FOR EACH ROW
            WHEN NEW.groupe <> OLD.groupe
            BEGIN
                INSERT INTO t_signaux(cle, ancien_groupe, nouveau_groupe, date_modif)
                VALUES (NEW.cle, OLD.groupe, NEW.groupe, datetime('now'));
            END;
    """
    cur.executescript(script)
    conn.commit()
    conn.close()


def controle_modif():
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM t_signaux").fetchall()
    if rows:
        messagebox.showinfo(
            "Info", f"{len(rows)} changements de groupe détectés.")
        # Vide t_signaux - Autres traitements envisageables
        cur.execute("DELETE FROM t_signaux")
        conn.commit()


if __name__ == '__main__':
    # creer_table_surveillance()
    root = tk.Tk()
    root.withdraw()  # cache la fenêtre principale si tu veux juste l’alerte
    controle_modif()
