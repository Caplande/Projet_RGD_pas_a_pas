from tkinter import ttk
import tkinter as tk

print("Module qualite_base_page chargé avec succès.")


class QualiteBasePage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = ttk.Label(self, text="Menu de qualité de la base")
        self.label.pack(padx=20, pady=20)
