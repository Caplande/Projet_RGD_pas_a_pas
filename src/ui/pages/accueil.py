from tkinter import ttk


class AccueilPage:
    def __init__(self, parent, context):
        label = ttk.Label(parent, text="Bienvenue dans l'application")
        label.pack(padx=20, pady=20)
