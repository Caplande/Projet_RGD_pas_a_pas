import os
import tkinter as tk
from tkinter import ttk
import sqlite3
import variables_communes as vc
from src.utils import u_sql_2 as u_sql_2, u_sql_3 as u_sql_3

# --- Configuration de la Base de Données ---
CHEMIN_BDD = vc.rep_bdd
NOM_TABLE = 't_base_data'
NOM_TABLE_GROUPES = 't_liste_groupes'  # Nouvelle table de référence
COLONNE_A_EDITER = 'groupe'
COLONNE_IDENTIFIANT_UNIQUE = 'cle'


class GroupeValorisationApp:

    def __init__(self, master):
        self.master = master
        master.title("Valorisation Manuelle du Groupe (Autocomplétion Stable)")

        # Dictionnaire de configuration des largeurs
        self.largeurs_colonnes = {
            COLONNE_IDENTIFIANT_UNIQUE: 0, 'exercice': 60, 'batrub': 60, 'typ': 50,
            'typ_tit': 100, 'libelle': 300, 'reference': 120, 'nom_fournisseur': 200,
            'montant': 70, COLONNE_A_EDITER: 150,
        }

        self.groupes_valides = self._recuperer_groupes_valides()

        self.requete_select = f"""
            SELECT 
                {COLONNE_IDENTIFIANT_UNIQUE}, exercice, batrub, typ, typ_tit, libelle, reference, nom_fournisseur,montant, {COLONNE_A_EDITER} 
            FROM 
                {NOM_TABLE} 
            WHERE 
                {COLONNE_A_EDITER} IS NULL OR {COLONNE_A_EDITER} = ''
            ORDER BY 
                exercice, libelle, typ_tit, nom_fournisseur
        """

        self.requete_count = f"""
            SELECT COUNT(*) 
            FROM {NOM_TABLE} 
            WHERE {COLONNE_A_EDITER} IS NULL OR {COLONNE_A_EDITER} = ''
        """

        # Variables d'état pour la gestion de l'édition
        self.current_editor = None
        self.suggestion_window = None

        self._creer_widgets()
        self.charger_donnees()
        self.update_bandeau_status()

    # ----------------------------------------------------------------------
    # --- Méthodes de Données (BDD) ---
    # ----------------------------------------------------------------------

    def _recuperer_groupes_valides(self):
        # (Méthode inchangée - lit les groupes valides)
        conn = None
        try:
            conn = sqlite3.connect(CHEMIN_BDD)
            cur = conn.cursor()
            cur.execute(
                f"SELECT groupe FROM {NOM_TABLE_GROUPES} ORDER BY groupe")
            return [row[0] for row in cur.fetchall()]
        except sqlite3.Error as e:
            print(
                f"❌ Erreur SQLite lors de la récupération des groupes valides : {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_groupe_in_db(self, cle_value, new_groupe_value):
        # (Méthode inchangée - mise à jour BDD)
        conn = None
        try:
            conn = sqlite3.connect(CHEMIN_BDD)
            cur = conn.cursor()

            requete_update = f"UPDATE {NOM_TABLE} SET {COLONNE_A_EDITER} = ? WHERE {COLONNE_IDENTIFIANT_UNIQUE} = ?"
            cur.execute(requete_update, (new_groupe_value, cle_value))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur de mise à jour SQLite : {e}")
            return False
        finally:
            if conn:
                conn.close()

    def compter_lignes_restantes(self):
        # (Méthode inchangée - comptage des lignes)
        conn = None
        try:
            conn = sqlite3.connect(CHEMIN_BDD)
            cur = conn.cursor()
            cur.execute(self.requete_count)
            return cur.fetchone()[0]
        except sqlite3.Error as e:
            print(f"❌ Erreur SQLite lors du comptage des lignes : {e}")
            return -1
        finally:
            if conn:
                conn.close()

    # ----------------------------------------------------------------------
    # --- Gestion de l'Interface Utilisateur (GUI) ---
    # ----------------------------------------------------------------------

    def update_bandeau_status(self):
        # (Méthode inchangée - mise à jour du bandeau)
        lignes_restantes = self.compter_lignes_restantes()

        if lignes_restantes == 0:
            texte_status = "🎉 Tous les enregistrements ont été valorisés !"
            self.bandeau_status.config(bg="#E0F8E0", fg="black")
        elif lignes_restantes == -1:
            texte_status = "⚠️ Erreur de connexion à la base de données pour le comptage."
            self.bandeau_status.config(bg="#FFD0D0", fg="black")
        else:
            texte_status = f"📊 {lignes_restantes} lignes restantes à valoriser (sans groupe)."
            self.bandeau_status.config(bg="#FFFFD0", fg="black")

        self.bandeau_status.config(text=texte_status)

    def _creer_widgets(self):
        # (Méthode inchangée - création Treeview et bandeau)
        frame_table = ttk.Frame(self.master)
        frame_table.pack(padx=10, pady=(10, 0), fill='both', expand=True)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical")
        scrollbar.pack(side='right', fill='y')

        self.tree = ttk.Treeview(frame_table, columns=(
        ), yscrollcommand=scrollbar.set, selectmode="browse")
        self.tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        self.tree.bind("<Double-1>", self.edition_cellule)

        self.bandeau_status = tk.Label(
            self.master,
            text="Initialisation...",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Arial', 10)
        )
        self.bandeau_status.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

    def charger_donnees(self):
        # (Méthode inchangée - chargement des données)
        conn = None
        try:
            conn = sqlite3.connect(CHEMIN_BDD)
            cur = conn.cursor()

            cur.execute(self.requete_select)
            lignes = cur.fetchall()
            noms_colonnes = [description[0] for description in cur.description]

            self.tree.delete(*self.tree.get_children())

            self.tree["columns"] = noms_colonnes
            self.tree.heading("#0", text="", anchor='w')
            self.tree.column("#0", width=0, stretch=tk.NO)

            for col_name in noms_colonnes:
                width = self.largeurs_colonnes.get(col_name, 80)
                self.tree.heading(
                    col_name, text=col_name.capitalize().replace('_', ' '), anchor='w')
                self.tree.column(col_name, width=width,
                                 anchor='w', stretch=tk.NO)

            for ligne in lignes:
                self.tree.insert("", "end", values=ligne)

        except sqlite3.Error as e:
            print(f"❌ Erreur SQLite lors du chargement des données : {e}")
        finally:
            if conn:
                conn.close()

    def _detruire_suggestion_listbox(self):
        """Détruit la fenêtre de suggestion si elle existe."""
        if self.suggestion_window is not None:
            self.suggestion_window.destroy()
            self.suggestion_window = None

    def _creer_suggestion_listbox(self, x, y, width):
        """Crée la fenêtre flottante contenant la Listbox de suggestions."""
        self._detruire_suggestion_listbox()  # Détruit l'ancienne si elle existe

        # Le Listbox sera contenu dans une Frame ou Toplevel pour être placé facilement
        self.suggestion_window = tk.Frame(self.tree, bd=1, relief="solid")

        self.listbox_suggestions = tk.Listbox(
            self.suggestion_window,
            selectmode=tk.SINGLE,
            height=10,
            width=width,
            exportselection=False  # Important pour ne pas interférer avec le focus Entry
        )
        self.listbox_suggestions.pack(fill='both', expand=True)

        # Positionnement de la Listbox juste en dessous de l'Entry
        self.suggestion_window.place(
            x=x, y=y + 22, width=width, height=200, anchor='nw')

        # Événements pour la Listbox
        self.listbox_suggestions.bind(
            '<<ListboxSelect>>', self._sauvegarder_avec_listbox)
        self.listbox_suggestions.bind(
            '<Return>', self._sauvegarder_avec_listbox)
        self.listbox_suggestions.bind(
            '<Double-1>', self._sauvegarder_avec_listbox)

    def _mettre_a_jour_suggestions(self, event):
        """Filtre et affiche les suggestions dans la Listbox en fonction de la saisie Entry."""

        current_input = self.current_editor.get().lower()

        # Si aucune saisie, on affiche tous les groupes
        if not current_input:
            filtered_list = self.groupes_valides
        else:
            filtered_list = [
                groupe for groupe in self.groupes_valides
                if groupe.lower().startswith(current_input)
            ]

        # Si aucune fenêtre de suggestion n’existe encore, la créer
        if self.suggestion_window is None:
            self._creer_suggestion_listbox(
                self.current_editor.winfo_x(),
                self.current_editor.winfo_y(),
                self.current_editor.winfo_width()
            )

        # Mettre à jour la liste
        self.listbox_suggestions.delete(0, tk.END)
        for item in filtered_list:
            self.listbox_suggestions.insert(tk.END, item)

        # Si aucune correspondance, cacher la liste
        if not filtered_list:
            self._detruire_suggestion_listbox()

    def _sauvegarder_avec_entry(self, event):
        """Sauvegarde si on valide l'Entry sans avoir utilisé la Listbox."""
        new_value = self.current_editor.get().strip()

        # Sauvegarde uniquement si la valeur saisie est valide
        if new_value and new_value in self.groupes_valides:
            self._sauvegarder_et_nettoyer(new_value)
        else:
            # Si la saisie est invalide ou vide, on ferme juste l'éditeur
            self._sauvegarder_et_nettoyer(None)

    def _sauvegarder_avec_listbox(self, event):
        """Sauvegarde après sélection dans la Listbox."""

        try:
            selection_index = self.listbox_suggestions.curselection()[0]
            new_value = self.listbox_suggestions.get(selection_index)
            self._sauvegarder_et_nettoyer(new_value)
        except IndexError:
            # Rien n'était sélectionné dans la Listbox, on ignore
            pass

    def _sauvegarder_et_nettoyer(self, new_value=None):
        """Logic commune de sauvegarde et de destruction des widgets."""

        if self.current_editor is None:
            return

        # Récupération des données nécessaires (stockées dans l'Entry)
        item_id = self.current_editor.item_id
        cle_value = self.current_editor.cle_value

        if new_value and new_value in self.groupes_valides:
            if self.update_groupe_in_db(cle_value, new_value):
                self.tree.delete(item_id)
                print(
                    f"✅ Ligne {cle_value} mise à jour avec groupe '{new_value}' et retirée de la vue.")
                self.update_bandeau_status()

        # Nettoyage des widgets d'édition
        self._detruire_suggestion_listbox()
        self.current_editor.destroy()
        self.current_editor = None

    def edition_cellule(self, event):
        """Gère le double-clic pour créer l'Entry et la Listbox de suggestion."""

        # Détruire toute édition précédente si elle est active
        if self.current_editor is not None:
            self._sauvegarder_et_nettoyer(self.current_editor.get().strip())

        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)

        if not item_id:
            return

        try:
            index_colonne_groupe = self.tree["columns"].index(COLONNE_A_EDITER)
        except ValueError:
            return

        id_positionnel_attendu = f"#{index_colonne_groupe + 1}"

        if column_id != id_positionnel_attendu:
            return

        bbox = self.tree.bbox(item_id, column_id)
        if not bbox:
            return
        x, y, width, height = bbox

        current_values = self.tree.item(item_id, 'values')
        col_index_groupe = index_colonne_groupe
        current_text = current_values[col_index_groupe]

        cle_col_index = self.tree["columns"].index(COLONNE_IDENTIFIANT_UNIQUE)
        cle_value = current_values[cle_col_index]

        # 1. CRÉATION DU ENTRY EDITOR
        var_groupe = tk.StringVar(value=current_text)

        editor = ttk.Entry(self.tree, textvariable=var_groupe)
        editor.place(x=x, y=y, width=width, height=height, anchor='nw')
        editor.focus_set()

        # Stocker les identifiants nécessaires pour la sauvegarde
        editor.item_id = item_id
        editor.cle_value = cle_value
        self.current_editor = editor

        # 2. CRÉATION DU LISTBOX DE SUGGESTIONS
        self._creer_suggestion_listbox(x, y, width)

        # 3. LIAISONS D'ÉVÉNEMENTS
        # Filtrage en temps réel
        editor.bind('<KeyRelease>', self._mettre_a_jour_suggestions)
        # Valider la saisie (si elle correspond à un groupe)
        editor.bind('<Return>', self._sauvegarder_avec_entry)
        # Annuler
        editor.bind('<Escape>', lambda e: self._sauvegarder_et_nettoyer(None))
        # Valider à la perte de focus
        editor.bind('<FocusOut>', self._sauvegarder_avec_entry)

# --- Lancement de l'exécution ---


def saisie_manuelle():
    root = tk.Tk()
    app = GroupeValorisationApp(root)
    root.mainloop()


def saisie_automatique():
    import sqlite3


# --- Configuration de la Base de Données ---
NOM_TABLE_DATA = 't_base_data'
NOM_TABLE_CRITERES = 't_criteres_groupe'
COLONNE_A_EDITER = 'groupe'


def mise_a_jour_groupe_par_criteres(table_data, table_criteres, colonne_groupe):
    """
    Met à jour la colonne 'groupe' de la table_data en utilisant les conditions 
    définies dans la table_criteres.

    Args:
        CHEMIN_BDD (str): Chemin vers le fichier SQLite.
        table_data (str): Nom de la table à mettre à jour (ex: t_base_data).
        table_criteres (str): Nom de la table contenant les critères (ex: criteres_groupe).
        colonne_groupe (str): Nom de la colonne à mettre à jour (ex: groupe).
    """
    conn = None
    try:
        conn = sqlite3.connect(CHEMIN_BDD)
        cur = conn.cursor()

        # 1. Lire tous les critères et les noms de groupe
        print(f"1. Lecture des critères depuis la table '{table_criteres}'...")
        cur.execute(
            f"SELECT nom_groupe, condition FROM {table_criteres} ORDER BY rowid")
        criteres = cur.fetchall()

        if not criteres:
            print("⚠️ Aucune règle trouvée dans la table de critères. Opération annulée.")
            return

        total_lignes_modifiees = 0

        # 2. Itérer sur chaque critère et exécuter la requête UPDATE
        for nom_groupe, condition_texte in criteres:
            if not condition_texte or not nom_groupe:
                print(
                    f"   ! Ignoré : Règle incomplète (Groupe: {nom_groupe}, Condition: {condition_texte})")
                continue

            # Construire la requête UPDATE dynamique.
            # On utilise f-string car la condition est une chaîne de caractères SQL.
            # ATTENTION : Cette méthode est sensible aux injections SQL si les données de
            # 'condition' ne sont pas fiables. Ici, on suppose qu'elles sont gérées.

            requete_update = f"""
                UPDATE {table_data} 
                SET {colonne_groupe} = '{nom_groupe}' 
                WHERE ({colonne_groupe} IS NULL OR {colonne_groupe} = '') 
                AND ({condition_texte})
            """

            # Note: La clause "WHERE groupe IS NULL OR groupe = ''" garantit
            # que seules les lignes non valorisées sont traitées.

            try:
                cur.execute(requete_update)
                lignes_modifiees = cur.rowcount
                total_lignes_modifiees += lignes_modifiees

                print(
                    f"   - ✅ Mise à jour : Groupe '{nom_groupe}' ({lignes_modifiees} lignes modifiées)")

            except sqlite3.Error as e:
                # Si une condition SQL est mal formée, elle sera capturée ici.
                print(f"   - ❌ ERREUR SQL pour la règle '{nom_groupe}' : {e}")
                print(f"     Requête défaillante : {requete_update.strip()}")

        # 3. Validation des modifications (Commit)
        conn.commit()
        print(
            f"\nFIN DU TRAITEMENT : {total_lignes_modifiees} lignes mises à jour au total.")
        u_sql_3.maj_t_lexique_cles()

    except sqlite3.Error as e:
        print(f"❌ Erreur générale de connexion/exécution : {e}")
        if conn:
            conn.rollback()  # Annuler toutes les transactions en cas d'erreur
    finally:
        if conn:
            conn.close()
        print(
            f"""Nombre de lignes dont le groupe n'est pas valorisé: {u_sql_2.compter_lignes("t_base_data", cdtn="groupe IS NULL OR groupe = ''")}""")

# ----------------------------------------------------------------------
# --- Bloc de Test et Initialisation (Démo) ---
# ----------------------------------------------------------------------


if __name__ == '__main__':
    print("\n--- Début de la Mise à Jour ---")
    mise_a_jour_groupe_par_criteres(
        NOM_TABLE_DATA,
        NOM_TABLE_CRITERES,
        COLONNE_A_EDITER
    )
