from tkinter import ttk
import tkinter as tk

print("Module general_page chargé avec succès.")


class GeneralPage(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.label = ttk.Label(self, text="Menu général de l'application")
        self.label.pack(padx=20, pady=20)
