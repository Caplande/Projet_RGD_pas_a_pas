import sys
import os
import tkinter as tk
from tkinter import messagebox
from src.utils import u_gen as u_gen
from src.utils import reinitialiser_bdd as rb, actualiser_donnees as ad, synoptique as sy


print("Module menu chargé avec succès.")


class MonMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Copropriété Monica - Analyse de l'historique RGD")
        self.root.geometry("800x600")
        self.creer_menu()

    def creer_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        self.menu_v1 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Général", menu=self.menu_v1)

        self.menu_v2 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Mise à jour", menu=self.menu_v2)

        self.menu_v3 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edition", menu=self.menu_v3)

        self.menu_v4 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Qualité de la base", menu=self.menu_v4)

        # on garde les index de chaque item pour pouvoir les (dés)activer
        self.menu_v1.add_command(
            label="Fermer projet", command=lambda: self.executer_action("Fermeture du projet...", "10"))
        self.menu_v1.add_command(
            label="Bidon", command=lambda: self.bidon)
        self.menu_v1.add_separator()
        self.menu_v1.add_command(
            label="Choix3", command=lambda: self.executer_action("Choix3", 3))

        self.menu_v2.add_command(
            label="Actualiser données", command=lambda: self.executer_action("Actualiser données...", "20"))
        self.menu_v2.add_separator()
        self.menu_v2.add_command(
            label="Réinitialiser à situation 2024", command=lambda: self.executer_action("Réinitialiser à situation 2024...", "21"))

        self.menu_v3.add_command(
            label="Document intégral par typ", command=lambda: self.executer_action("Document intégral par typ...", "30"))
        self.menu_v3.add_command(
            label="Document intégral par groupe", command=lambda: self.executer_action("Document intégral par groupe...", "31"))
        self.menu_v3.add_separator()
        self.menu_v3.add_command(
            label="Document partiel par typ", command=lambda: self.executer_action("Document partiel par typ...", "32"))
        self.menu_v3.add_command(
            label="Document partiel par groupe", command=lambda: self.executer_action("Actualiser données...", "33"))

        self.menu_v4.add_command(
            label="Statistiques de la base", command=lambda: self.executer_action("Statistiques de la base...", "40"))

    def executer_action(self, message, index_menu):
        match index_menu:
            case "10":
                u_gen.fermer_projet()
            case "20":
                ad.actualiser_bdd('actualiser_bdd_executer')
            case "21":
                rb.reinitialiser_bdd('reinitialiser_bdd_executer')
            case "30":
                rb.reinitialiser_bdd()
            case "31":
                rb.reinitialiser_bdd()
            case "32":
                rb.reinitialiser_bdd()
            case "33":
                rb.reinitialiser_bdd()
            case "40":
                sy.afficher_table()
            case _:
                messagebox.showinfo("Action", f"Tu as sélectionné : {message}")

    def bidon(self):
        messagebox.showinfo("Action", "bidon...")


if __name__ == "__main__":
    # --- Lancement
    root = tk.Tk()
    app = MonMenu(root)
    root.mainloop()
