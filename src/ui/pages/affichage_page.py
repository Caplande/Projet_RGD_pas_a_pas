from tkinter import ttk
import tkinter as tk

print("Module affichage chargé avec succès.")


class AffichagePage(tk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        label = ttk.Label(
            parent, text="Paramétrer les couleurs des widgets d'affichage")
