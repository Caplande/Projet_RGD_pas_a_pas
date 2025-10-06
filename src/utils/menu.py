import tkinter as tk
from tkinter import messagebox

print("Module menu chargé avec succès.")


def action(message):
    messagebox.showinfo("Action", f"Tu as choisi : {message}")


# --- Fenêtre principale ---
root = tk.Tk()
root.title("Menu type Excel / VSC")
root.geometry("400x250")

# --- Barre de menus ---
menubar = tk.Menu(root)
root.config(menu=menubar)

# === Menu V1 ===
menu_v1 = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="V1", menu=menu_v1)

# V1_Choix1 avec sous-choix
menu_v1_choix1 = tk.Menu(menu_v1, tearoff=0)
menu_v1.add_cascade(label="V1_Choix1", menu=menu_v1_choix1)
menu_v1_choix1.add_command(label="Sous-choix 1.1",
                           command=lambda: action("V1 → Sous-choix 1.1"))
menu_v1_choix1.add_command(label="Sous-choix 1.2",
                           command=lambda: action("V1 → Sous-choix 1.2"))

# Autres choix
menu_v1.add_command(label="V1_Choix2", command=lambda: action("V1 → Choix2"))
menu_v1.add_separator()
menu_v1.add_command(label="Choix3", command=lambda: action("V1 → Choix3"))

# === Menu V2 ===
menu_v2 = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="V2", menu=menu_v2)

menu_v2.add_command(label="V2_Choix1", command=lambda: action("V2 → Choix1"))
menu_v2.add_command(label="V2_Choix2", command=lambda: action("V2 → Choix2"))

# --- Boucle principale ---
root.mainloop()
