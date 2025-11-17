import tkinter as tk

root = tk.Tk()
root.geometry("300x200")

# 1. Le FRAME PARENT (le fond à masquer) - Avec un fond GRIS pour visualisation
parent_frame = tk.Frame(root, bg='lightgray')
# Note : Nous retirons padx/pady ici et ajoutons un petit espace entre les frames
parent_frame.pack(fill='both', expand=True, padx=5, pady=5)

# 2. Le SOUS-FRAME (Le recouvreur) - SANS BORDURE NI MARGE INTERNE, packé EN PREMIER
# Le sub_frame a la couleur bleue.
sub_frame = tk.Frame(parent_frame, bg='lightblue', bd=0)  # bd=0 est important
sub_frame.pack(side='top', fill='both', expand=True,
               padx=0, pady=0)  # padx/pady=0 est crucial

# 3. Le LABEL (L'élément masqué) - packé APRES
initial_label = tk.Label(
    parent_frame, text="Label derrière le sous-frame", bg='yellow')
initial_label.pack(pady=20)

# Contenu du Sous-frame
content_label = tk.Label(
    sub_frame, text="Recouvrement ZÉRO Marge!", bg='lightblue')
content_label.pack(expand=True)

root.mainloop()
