import sqlite3
import json
import re
from datetime import datetime
import tkinter as tk
import variables_path as vc
from src.utils import u_sql_1 as u_sql_1


def convertir_date(date_texte):
    dt = datetime.strptime(date_texte, "%Y-%m-%d %H:%M:%S")
    # format "jour semaine jour mois année"
    resultat = dt.strftime("%A %d %B %Y")
    return resultat


def copier_table_avec_structure_et_donnees(source, cible):
    conn = sqlite3.connect(vc.REP_BDD)
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
    conn = sqlite3.connect(vc.REP_BDD)
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
    conn = sqlite3.connect(vc.REP_BDD)
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
    conn = sqlite3.connect(vc.REP_BDD)
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


def analyse_couple_typ_groupe():
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()

    cur.executescript(f"""
        DROP VIEW IF EXISTS v_t_base_data;

        CREATE VIEW v_t_base_data AS
        SELECT
            b.typ,
            b.id,
            b.batrub,
            lbr.batrub_tit_yp,
            b.typ_tit,
            b.libelle,
            b.nom_fournisseur,
            b.groupe
        FROM t_base_data AS b
        LEFT JOIN t_lexique_bat AS lb ON b.bat = lb.bat
        LEFT JOIN t_lexique_batrub AS lbr ON b.batrub = lbr.batrub
        LEFT JOIN t_lexique_typ AS lt ON b.typ = lt.typ
        ORDER BY b.batrub || b.typ;
        """)


def creer_vue(nom_vue='v_t_base_data', cdtn='1=1'):
    """
    Donner à cdtn la valeur: 1=1 pour avoir tous les enregistrements
    Autre exemplepour cdtn: groupe = 'Honoraires Syndic'
    """
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()

    # Il faut adapter cdtn à la syntaxe SQLITE
    cdtn = cdtn if cdtn == '1=1' else 'b.' + cdtn

    cur.execute(f"""
        DROP VIEW IF EXISTS {nom_vue};""")

    sql = f"""
        CREATE VIEW {nom_vue} AS
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
        WHERE {cdtn} 
        ORDER BY b.bat || b.batrub || b.typ;
    """
    cur.execute(sql)

    conn.commit()
    conn.close()


def maj_t_lexique_cles_old():
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS t_lexique_cles;             
                      
        CREATE TABLE t_lexique_cles AS
        SELECT DISTINCT cle, groupe
        FROM t_base_data;
        
        CREATE INDEX id ON t_lexique_cles(cle, groupe);
        """)

    conn.commit()
    conn.close()


def extraire_un_parametre(indicateur):
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()

    # Utiliser '?' comme placeholder pour la valeur
    sql = """SELECT valeur
             FROM t_parametres
             WHERE indicateur = ?
          """

    # Passer la variable 'indicateur' comme un tuple séparé
    # C'est la MÉTHODE SÛRE et RECOMMANDÉE
    cur.execute(sql, (indicateur,))
    row = cur.fetchone()
    # Complétez la fonction (par exemple, cur.fetchone() pour récupérer le résultat)
    conn.close()
    return row[0]


class AffichageEcran():
    def __init__(self, master):
        # Le conteneur principal (root)
        self.master = master
        self.master.title("Exemple Application modulaire")
        self.master.geometry("600x400")

        # Frame principale
        self.main_frame = tk.Frame(master, bg="lightblue")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Crée une sous-section par méthode
        self.creer_zone_titre()
        self.creer_zone_boutons()

    def creer_zone_titre(self):
        """Créer une frame contenant le titre"""
        self.frame_titre = tk.Frame(
            self.main_frame, bg="white", relief="groove", bd=2)
        self.frame_titre.pack(fill="x", pady=5)
        self.label_titre = tk.Label(
            self.frame_titre, text="Bienvenue !", font=("Arial", 14))
        self.label_titre.pack(padx=10, pady=5)

    def creer_zone_boutons(self):
        """Créer une frame contenant les boutons"""
        self.frame_boutons = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.frame_boutons.pack(pady=10)

        self.btn_ajouter = tk.Button(
            self.frame_boutons, text="Ajouter", command=self.ajouter_message)
        self.btn_ajouter.pack(side="left", padx=5)

        self.btn_effacer = tk.Button(
            self.frame_boutons, text="Effacer", command=self.effacer_widgets)
        self.btn_effacer.pack(side="left", padx=5)

    def ajouter_message(self):
        """Exemple d’ajout dynamique d’un widget"""
        label = tk.Label(self.main_frame, text="Nouveau message", bg="yellow")
        label.pack(pady=2)
        # Tu pourrais garder une liste de widgets créés ici
        # self.widgets.append(label)

    def effacer_widgets(self):
        """Supprime tout le contenu de la main_frame sauf les zones fixes"""
        for w in self.main_frame.winfo_children():
            if w not in (self.frame_titre, self.frame_boutons):
                w.destroy()


# Lancement de l’application
if __name__ == "__main__":
    root = tk.Tk()
    app = AffichageEcran(root)
    root.mainloop()


if __name__ == "__main__":
    # maj_etat_bdd()
    # get_date_importation_site()
    # copier_table_avec_structure_et_donnees(
    #    "t_lexique_cles", "t_lexique_cles_ante")
    # comparer_tables("t_lexique_cles", "t_lexique_cles_init_temp", "id")
    # maj_t_lexique_cles()
    # nettoyer_colonne('t_base_data', 'nom_fournisseur')
    # creer_vue(cdtn='groupe="Honoraires Syndic"')
    # analyse_couple_typ_groupe()
    # maj_t_lexique_cles()
    # print(extraire_un_parametre("I_001")[0])
    print("Globals :", list(globals().keys()))
    pass
