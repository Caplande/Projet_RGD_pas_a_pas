import sys
import os
import tkinter as tk
from tkinter import messagebox
from src.utils import u_gen as u_gen

print("Module menu chargé avec succès.")


def action(message):
    messagebox.showinfo("Action", f"Tu as choisi : {message}")


def menu():
    root = tk.Tk()
    root.title("Copropriété Monica - Menu principal")
    root.geometry("400x250")

    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # === Onglet Application ===
    app_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Application", menu=app_menu)
    app_menu.add_command(label="Fermer le projet",
                         command=lambda: u_gen.fermer_projet(root))
    app_menu.add_command(label="Reinitialiser le projet",
                         command=lambda: u_gen.fermer_projet(root))

    # === Onglet V1 ===
    v1_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="V1", menu=v1_menu)
    v1_sub = tk.Menu(v1_menu, tearoff=0)
    v1_menu.add_cascade(label="V1_Choix1", menu=v1_sub)
    v1_sub.add_command(label="Sous-choix 1.1",
                       command=lambda: messagebox.showinfo("Choix", "V1 → 1.1"))
    v1_sub.add_command(label="Sous-choix 1.2",
                       command=lambda: messagebox.showinfo("Choix", "V1 → 1.2"))
    v1_menu.add_command(
        label="V1_Choix2", command=lambda: messagebox.showinfo("Choix", "V1 → Choix2"))

    # === Onglet V2 ===
    v2_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="V2", menu=v2_menu)
    v2_menu.add_command(
        label="V2_Choix1", command=lambda: messagebox.showinfo("Choix", "V2 → Choix1"))
    v2_menu.add_command(
        label="V2_Choix2", command=lambda: messagebox.showinfo("Choix", "V2 → Choix2"))

    # Raccourci clavier Ctrl+Q pour fermer
    root.bind("<Control-q>", lambda event: u_gen.fermer_projet(root))

    root.mainloop()


menu()
