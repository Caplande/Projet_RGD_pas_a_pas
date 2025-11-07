import sqlite3
from tkinter import ttk
import tkinter as tk
from src.core.context import context as ctxt
from src.core import edit_speciales as es

print("Module selection_enregistrements_page chargé avec succès.")


class SelectionEnregistrementsPage(ttk.Frame):
    # Le parent est: fr_centre de AppUi
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

        # --- Création des filtres (comboboxes) ---
        self.creer_filtres(self.champs)

        # --- Bouton pour afficher ---
        bouton_afficher = ttk.Button(
            self.fr_choix, text="Afficher", command=self.afficher_resultats)
        bouton_afficher.pack(side="right", padx=10, pady=5)

        # --- Affichage initial ---
        self.after(0, self._ajuster_resultats)

    # ------------------------
    def creer_filtres(self, champs):
        """Crée les comboboxes dans fr_choix à partir des valeurs présentes dans vue_editions_speciales."""
        valeurs_possibles = es.valeurs_possibles_vues()
        for champ in champs:
            lbl = ttk.Label(
                self.fr_choix, text=champ.capitalize() + " :", style="TLabel")
            lbl.pack(side="left", padx=5)

            combo = ttk.Combobox(
                self.fr_choix,
                values=valeurs_possibles.get(champ, []),
                state="readonly",
                width=12
            )
            combo.pack(side="left", padx=3)
            combo.bind("<<ComboboxSelected>>", self._maj_filtre)

            self.combos[champ] = combo

    # ------------------------
    def _maj_filtre(self, event):
        """Met à jour le dictionnaire self.filtres en fonction des choix actuels."""
        for champ, combo in self.combos.items():
            val = combo.get()
            if val:
                self.filtres[champ] = val
            elif champ in self.filtres:
                del self.filtres[champ]

    # ------------------------
    def afficher_resultats(self):
        """Affiche les résultats filtrés dans fr_resultats avec en-têtes et barres de défilement."""
        self._maj_filtre(None)
        es.creer_vue_base()
        lignes = es.selectionner_resultats(self.filtres)

        # Nettoyer la zone d'affichage
        for widget in self.fr_resultats.winfo_children():
            widget.destroy()

        # Créer conteneur scrollable
        container = ttk.Frame(self.fr_resultats)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar_y = ttk.Scrollbar(
            container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(
            container, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set,
                         xscrollcommand=scrollbar_x.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        if not lignes:
            ttk.Label(scrollable_frame, text="Aucun enregistrement trouvé.").pack(
                anchor="w", padx=5, pady=5)
            return

        colonnes = [
            "base_rep", "exercice", "groupe", "bat", "bat_tit_yp",
            "batrub", "batrub_tit_yp", "typ", "typ_tit_yp", "montant"
        ]

        # En-têtes
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill="x", padx=5, pady=(5, 0))
        for col in colonnes:
            ttk.Label(header_frame, text=col, style="TLabel",
                      anchor="w", width=15).pack(side="left", padx=2)

        ttk.Separator(scrollable_frame, orient="horizontal").pack(
            fill="x", pady=3)

        # Données
        for ligne in lignes:
            row_frame = ttk.Frame(scrollable_frame)
            row_frame.pack(fill="x", padx=5)
            for valeur in ligne:
                ttk.Label(row_frame, text=str(valeur), anchor="w",
                          width=15).pack(side="left", padx=2)

    # ------------------------
    def _ajuster_resultats(self):
        """Affichage initial vide ou message par défaut."""
        for widget in self.fr_resultats.winfo_children():
            widget.destroy()
        lbl = ttk.Label(
            self.fr_resultats,
            text="Sélectionnez vos filtres puis cliquez sur Afficher.",
            style="TLabel"
        )
        lbl.pack(pady=10)
