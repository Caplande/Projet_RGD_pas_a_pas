from tkinter import ttk
import tkinter as tk
print("Module accueil chargé avec succès.")


class AccueilPage(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.bg = 'green'
        # self.configure(bg=self.bg)
        self.label = ttk.Label(
            self,
            text=f"Bienvenue dans l'application {context.nom_application}",
            font=("Helvetica", 16, "bold"),  # police, taille, style
        )
        self.label.pack(expand=True, padx=20, pady=20)
        self.label.configure(background=self.bg)

        # label.place(relx=0.5, rely=0.5, anchor="center")  # centré dans le frame
