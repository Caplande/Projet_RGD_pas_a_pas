import tkinter as tk
from tkinter import ttk
from src.core.context import context as ctxt
from src.core import edit_speciales as res


print("Module selection_enregistrements_page chargé avec succès.")


class SelectionEnregistrementsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style="TFrame")

        self.filtres = {}
        self.combos = {}
        self.champs = ["exercice", "groupe", "batrub", "typ", "base_rep"]

        # --- Zones principales ---
        self.fr_choix = ttk.Frame(self, style="TFrame")
        self.fr_choix.place(x=0, y=0, relwidth=1, height=40)

        self.fr_resultats = ttk.Frame(self, style="TFrame")
        self.fr_resultats.place(x=0, rely=0.1, relwidth=1, relheight=0.9)

        # --- Création des filtres ---
        self.creer_filtres(self.champs)

        # --- Bouton pour afficher ---
        bouton_afficher = ttk.Button(
            self.fr_choix, text="Afficher", command=self.afficher_resultats)
        bouton_afficher.pack(side="right", padx=10, pady=5)

        # --- Affichage initial ---
        self.after(0, self._ajuster_resultats)

    # ------------------------
    def creer_filtres(self, champs):
        """Crée les comboboxes dans fr_choix à partir des valeurs présentes dans la vue."""
        valeurs_possibles = res.valeurs_possibles_vues()

        for champ in champs:
            lbl = ttk.Label(
                self.fr_choix, text=champ.capitalize() + " :", style="TLabel")
            lbl.pack(side="left", padx=5)

            valeurs = [""] + valeurs_possibles.get(champ, [])

            combo = ttk.Combobox(
                self.fr_choix, values=valeurs, state="readonly", width=12
            )
            combo.set("")
            combo.pack(side="left", padx=3)
            combo.bind("<<ComboboxSelected>>", self._maj_filtre)

            self.combos[champ] = combo

    # ------------------------
    def _maj_filtre(self, event):
        """Met à jour le dictionnaire self.filtres selon les choix actuels."""
        for champ, combo in self.combos.items():
            val = combo.get()
            if val:
                self.filtres[champ] = val
            elif champ in self.filtres:
                del self.filtres[champ]

    # ------------------------
    def afficher_resultats(self):
        """Affiche les résultats filtrés dans fr_resultats."""
        self._maj_filtre(None)
        colonnes, lignes = res.filtrer_vues(self.filtres)

        # Nettoyer l’affichage précédent
        for widget in self.fr_resultats.winfo_children():
            widget.destroy()

        if not lignes:
            ttk.Label(self.fr_resultats,
                      text="Aucun résultat trouvé.",
                      style="TLabel").pack(pady=10)
            return

        # --- Scrollbars ---
        vsb = ttk.Scrollbar(self.fr_resultats, orient="vertical")
        hsb = ttk.Scrollbar(self.fr_resultats, orient="horizontal")

        # --- Treeview ---
        tree = ttk.Treeview(
            self.fr_resultats,
            columns=colonnes,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # --- Colonnes ---
        for col in colonnes:
            tree.heading(col, text=col, anchor="w",
                         command=lambda c=col: self._trier_colonne(tree, c, False))
            tree.column(col, width=120, anchor="w", stretch=True)

        for ligne in lignes:
            tree.insert("", "end", values=ligne)

        tree.pack(fill="both", expand=True)

        # Sauvegarde du tree pour référence (utile pour re-tri)
        self.tree = tree

        # Affichage du montant total de la sélection dans la barre de statut
        self.afficher_total_montant()

    # ------------------------
    def _trier_colonne(self, tree, col, descendante):
        """Trie les valeurs d’une colonne lors du clic sur l’en-tête."""
        donnees = [(tree.set(k, col), k) for k in tree.get_children("")]
        try:
            donnees.sort(key=lambda t: float(t[0])
                         if t[0].replace(".", "", 1).isdigit() else t[0],
                         reverse=descendante)
        except Exception:
            donnees.sort(key=lambda t: t[0], reverse=descendante)

        for index, (val, k) in enumerate(donnees):
            tree.move(k, "", index)

        tree.heading(col, command=lambda: self._trier_colonne(
            tree, col, not descendante))

    # ------------------------
    def _ajuster_resultats(self):
        """Affichage initial (avant sélection)."""
        for widget in self.fr_resultats.winfo_children():
            widget.destroy()
        ttk.Label(
            self.fr_resultats,
            text="Sélectionnez vos filtres puis cliquez sur Afficher.",
            style="TLabel"
        ).pack(pady=10)

    def afficher_total_montant(self):
        total = res.calcul_montant_total(self.filtres)
        ctxt.ecran.label_statut_2.configure(  # type: ignore
            text=f"Montant total : {total:.2f} €")
