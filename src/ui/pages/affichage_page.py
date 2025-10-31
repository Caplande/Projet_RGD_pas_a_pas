from tkinter import ttk
import tkinter as tk

print("Module affichage chargé avec succès.")


class AffichagePage(tk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.label = ttk.Label(
            self, text="Paramétrer les couleurs des widgets d'affichage")
        self.label.pack(padx=20, pady=20)
