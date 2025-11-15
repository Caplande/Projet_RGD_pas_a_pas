import sqlite3
import json
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from src.core.context import context as ctxt
from src.utils import u_sql_1 as u_sql_1


def convertir_date(date_texte):
    dt = datetime.strptime(date_texte, "%Y-%m-%d %H:%M:%S")
    # format "jour semaine jour mois année"
    resultat = dt.strftime("%A %d %B %Y")
    return resultat


def copier_table_avec_structure_et_donnees(source, cible):
    conn = sqlite3.connect(ctxt.path_bdd)
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
    conn = sqlite3.connect(ctxt.path_bdd)
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
    conn = sqlite3.connect(ctxt.path_bdd)
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
    conn = sqlite3.connect(ctxt.path_bdd)
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
    conn = sqlite3.connect(ctxt.path_bdd)
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
    conn = sqlite3.connect(ctxt.path_bdd)
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
    conn = sqlite3.connect(ctxt.path_bdd)
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
    conn = sqlite3.connect(ctxt.path_bdd)
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


def appliquer_couleur_jaune_fond(mon_widget):
    style = ttk.Style()
    style.configure("Jaune.TFrame", background="yellow")
    mon_widget.configure(style="Jaune.TFrame")


def appliquer_couleur_bleu_fond(mon_widget):
    style = ttk.Style()
    style.configure("Bleu.TFrame", background="blue")
    mon_widget.configure(style="Bleu.TFrame")


def appliquer_couleur_vert_fond(mon_widget):
    style = ttk.Style()
    style.configure("Vert.TFrame", background="green")
    mon_widget.configure(style="Vert.TFrame")


def appliquer_couleur_orange_fond(mon_widget):
    style = ttk.Style()
    style.configure("Orange.TFrame", background="orange")
    mon_widget.configure(style="Orange.TFrame")


def hierarchie_widgets(widget):
    """
    Retourne un dictionnaire représentant la hiérarchie des widgets
    à partir du widget donné (souvent root).
    Clés : noms Tkinter des widgets
    Valeurs : sous-dictionnaires (même structure)
    """
    enfants = widget.winfo_children()
    return {
        str(widget): {
            child.winfo_name(): hierarchie_widgets(child)
            for child in enfants
        }
    }


def print_widget_tree(widget, indent=""):
    # Couleurs ANSI
    C_RESET = "\033[0m"
    C_CLS = "\033[96m"   # cyan clair pour la classe
    C_PATH = "\033[92m"   # vert pour le chemin
    C_MGR = "\033[93m"   # jaune pour le manager
    C_FORG = "\033[91m"   # rouge pour forgotten
    C_OK = "\033[92m"   # vert status

    cls = widget.winfo_class()
    path = str(widget)
    mgr = widget.winfo_manager()

    if mgr == "":
        status = f"{C_FORG}FORGOTTEN{C_RESET}"
        mgr_display = "none"
    else:
        status = f"{C_OK}active{C_RESET}"
        mgr_display = mgr

    print(
        f"{indent}"
        f"{C_CLS}{cls}{C_RESET} "
        f"{C_PATH}{path}{C_RESET}  "
        f"manager={C_MGR}{mgr_display}{C_RESET}  "
        f"status={status}"
    )

    for child in widget.winfo_children():
        print_widget_tree(child, indent + "    ")


class WidgetTreeManager:
    """ Cette classe permet de visualiser et/ou extraire une hiérarchie de widgets en termes de création,masquage,affichage
        pour les 3 systèmes de gestion:pack,grid,place
        3 fonctionnalités essentielles:
        Si wtm = WidgetTreeManager(widget_contenant)
        ---> root est la racine (ctxt.ecran)
        ---> Gestion récursive. Le manager parcourt widget_contenant, repère tous les enfants, petits enfants quel que soit leur geometry manager
             Peut les cacher, les retaurer en navigant grace au chemin absolu /fr_centre/label1..
        ---> On peut détecter les widgets créés plus tard par wtm.refresh()
        ---> On peut afficher n'importe quel widget wtm.show("/fr_centre/mon_label")
        ---> On peut recupérer un widget: lbl = wtm.get("/fr_centre/mon_label")
        ---> On peut cacher un ou plusieurs widgets: wtm.hide("/page1", "/page2", "/fr_centre/sidebar")
        ---> Représentation de la hiérarchie: wtm.print_tree_status()
        ---> Pack, Grid, Place tous pris en charge
        ---> Système auto-refresh basé sur les events Tkinter (Map/Unmap/Configure/Destroy)
        ---> Peut restaurer automatiquement les geometry managers d’origine
    """

    def __init__(self, widg_contenant):
        self.root = widg_contenant
        self.tree = {}   # path → {widget, manager, info}
        self._build_tree()
        self._bind_events()  # activation du refresh automatique

    # ============================================================
    # AUTO-REFRESH
    # ============================================================
    def _bind_events(self):
        """
        Active un système global d'écoute :
        - <Map>       : widget rendu visible
        - <Unmap>     : widget masqué
        - <Configure> : taille/geometry manager changé
        - <Destroy>   : widget détruit

        Le tree est ainsi toujours à jour sans appeler refresh().
        """
        root = self.root.winfo_toplevel()

        root.bind_all("<Map>", lambda e: self._build_tree(), add="+")
        root.bind_all("<Unmap>", lambda e: self._build_tree(), add="+")
        root.bind_all("<Configure>", lambda e: self._build_tree(), add="+")
        root.bind_all("<Destroy>", lambda e: self._build_tree(), add="+")

    # ============================================================
    # BUILD TREE
    # ============================================================
    def _build_tree(self):
        """Reconstruit totalement le tree."""
        self.tree.clear()

        def recurse(widget, path):
            # --- nom logique pour le chemin ---
            if widget in ctxt.widget_names:
                name = ctxt.widget_names[widget]
            else:
                name = widget.winfo_name()

            fullpath = f"{path}/{name}" if path else name

            # --- infos manager ---
            mgr = widget.winfo_manager()
            if mgr == "pack":
                info = widget.pack_info()
            elif mgr == "grid":
                info = widget.grid_info()
            elif mgr == "place":
                info = widget.place_info()
            else:
                info = {}

            self.tree[fullpath] = {
                "widget": widget,
                "manager": mgr,
                "info": info
            }

            for child in widget.winfo_children():
                recurse(child, fullpath)

        recurse(self.root, "")

    # ============================================================
    # INTERNAL TOOLS
    # ============================================================
    def _hide(self, widget):
        mgr = widget.winfo_manager()
        if mgr == "pack":
            widget.pack_forget()
        elif mgr == "grid":
            widget.grid_remove()
        elif mgr == "place":
            widget.place_forget()

    def _restore(self, widget, mgr, info):
        if mgr == "pack":
            widget.pack(**info)
        elif mgr == "grid":
            widget.grid(**info)
        elif mgr == "place":
            widget.place(**info)

    def _descendants(self, path):
        """Retourne tous les chemins descendants récursifs."""
        prefix = path + "/" if path else ""
        return [
            p for p in self.tree
            if p.startswith(prefix) and p != path
        ]

    # ============================================================
    # PUBLIC API
    # ============================================================
    def _resolve(self, p: str):
        """Trouve le chemin réel associé à p (nom exact, partiel ou segment)."""
        p = p.strip("/")
        if not p:
            return "" if "" in self.tree else None

        # 1) match exact
        if p in self.tree:
            return p

        # 2) match sur les segments
        for key in self.tree.keys():
            if p in key.split("/"):
                return key

        return None

    def show(self, path):
        """Affiche un widget + tous ses descendants."""
        self._build_tree()

        key = self._resolve(path)
        if key is None:
            raise KeyError(f"[WTM.show] Chemin non trouvé : {path}")

        # cacher tous les widgets
        for entry in self.tree.values():
            self._hide(entry["widget"])

        # restaurer la cible
        e = self.tree[key]
        self._restore(e["widget"], e["manager"], e["info"])

        # restaurer les descendants
        for child in self._descendants(key):
            e = self.tree[child]
            self._restore(e["widget"], e["manager"], e["info"])

    def hide(self, *paths):
        """Cache un ou plusieurs widgets + leurs descendants."""
        self._build_tree()

        for path in paths:
            key = self._resolve(path)
            if key is None:
                print(f"[WTM.hide] Chemin non trouvé : {path}")
                continue

            # cacher ce widget
            self._hide(self.tree[key]["widget"])

            # cacher tous les descendants
            for c in self._descendants(key):
                self._hide(self.tree[c]["widget"])

    def get(self, path):
        """Renvoie directement l’objet widget."""
        return self.tree[path.lstrip("/")]["widget"]

    # ============================================================
    # PRINT TREE (couleurs)
    # ============================================================
    def print_tree_status(self):
        """Affiche l'arbre avec couleurs + statut actif/inactif + geometry manager."""
        self._build_tree()

        COLOR = {
            "root": "\033[96m",
            "container": "\033[94m",
            "leaf": "\033[92m",
            "inactive": "\033[91m",
            "mgr": "\033[90m",
            "reset": "\033[0m",
        }

        def is_container(widget):
            return len(widget.winfo_children()) > 0

        def is_visible(widget):
            return widget.winfo_manager() != ""

        def indent(level):
            return "  " * level

        def rec(path, level):
            entry = self.tree[path]
            widget = entry["widget"]
            mgr = entry["manager"] or "none"

            # nom python si dispo
            if widget in getattr(ctxt, "widget_names", {}):
                name = ctxt.widget_names[widget]
            else:
                name = widget.winfo_name()

            # couleur du type
            if path == "":
                color = COLOR["root"]
            elif is_container(widget):
                color = COLOR["container"]
            else:
                color = COLOR["leaf"]

            # actif/inactif
            active = is_visible(widget)
            state_color = COLOR["leaf"] if active else COLOR["inactive"]
            state_txt = "actif" if active else "inactif"

            print(
                f"{indent(level)}"
                f"{color}{name}{COLOR['reset']} "
                f"{COLOR['mgr']}[{mgr}]{COLOR['reset']} "
                f"{state_color}({state_txt}){COLOR['reset']}"
            )

            # enfants directs
            prefix = path + "/" if path else ""
            children = [
                p for p in self.tree
                if p.startswith(prefix)
                and p.count("/") == path.count("/") + 1
                and p != path
            ]

            for c in sorted(children):
                rec(c, level + 1)
        # --- Création d'une racine virtuelle "" si elle n'existe pas ---
        if "" not in self.tree:
            # On trouve tous les vrais racines : chemins sans "/"
            real_roots = [p for p in self.tree if "/" not in p]

            # Stockage dans l'entrée racine
            self.tree[""] = {
                "widget": self.root,        # widget racine réel
                "manager": None,
                "visible": True,
                "children": real_roots,
            }

        rec("", 0)


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
