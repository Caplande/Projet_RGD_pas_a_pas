from tkinter import ttk
import tkinter as tk

print("Module selection_enregistrements_page chargé avec succès.")


class SelectionEnregistrementsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ttk.Label(
            self, text="Menu de sélection des enregistrements", style="TLabel")
        self.label.pack(expand=True, padx=20, pady=20)
        self.configure(style="TFrame")
