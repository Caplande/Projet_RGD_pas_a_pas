import sys
import os
import tkinter as tk
from tkinter import messagebox
from src.utils import u_gen as u_gen
from src.utils import reinitialiser_bdd as rb

print("Module menu chargé avec succès.")


class MonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Copropriété Monica - Analyse de l'historique RGD")
        self.creer_menu()

    def creer_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        self.menu_v1 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Application", menu=self.menu_v1)

        # on garde les index de chaque item pour pouvoir les (dés)activer
        self.menu_v1.add_command(
            label="Fermer projet", command=lambda: self.executer_action("Fermeture du projet...", 0))
        self.menu_v1.add_command(
            label="Bidon", command=lambda: self.bidon)
        self.menu_v1.add_separator()
        self.menu_v1.add_command(
            label="Choix3", command=lambda: self.executer_action("Choix3", 3))

    def executer_action(self, message, index_menu):
        if index_menu == 0:
            u_gen.fermer_projet()
        else:
            messagebox.showinfo("Action", f"Tu as sélectionné : {message}")
        # Désactive temporairement le menu cliqué
        self.menu_v1.entryconfig(index_menu, state="disabled")
        # Optionnel : le réactiver après quelques secondes
        self.root.after(3000, lambda: self.menu_v1.entryconfig(
            index_menu, state="normal"))

    def bidon(self):
        messagebox.showinfo("Action", "bidon...")


if __name__ == "__main__":
    # --- Lancement
    root = tk.Tk()
    app = MonApp(root)
    root.mainloop()
