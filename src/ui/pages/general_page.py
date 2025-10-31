from tkinter import ttk
import tkinter as tk

print("Module general_page chargé avec succès.")


class GeneralPage(tk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        label = ttk.Label(parent, text="Menu général de l'application")
        label.pack(padx=20, pady=20)
