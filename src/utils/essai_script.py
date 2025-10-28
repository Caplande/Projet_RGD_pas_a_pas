import tkinter as tk
from tkinter import ttk


class Application:
    def __init__(self):
        # --- Fenêtre principale ---
        self.root = tk.Tk()
        self.root.title("Application Tkinter dynamique")
        self.root.geometry("500x300")

        # --- Conteneur principal ---
        self.container = tk.Frame(self.root, bg="lightgray")
        self.container.pack(fill="both", expand=True)

        # Dictionnaire pour stocker les sous-frames actives
        self.frames = {}

        # Création initiale de la frame principale
        self.afficher_frame(AccueilFrame)

    # --- Méthode pour afficher une frame donnée ---
    def afficher_frame(self, frame_class):
        # Si une frame est déjà affichée → on la détruit
        for frame in self.container.winfo_children():
            frame.destroy()

        # Crée et affiche la nouvelle frame
        frame = frame_class(self.container, self)
        frame.pack(fill="both", expand=True)
        self.frames[frame_class.__name__] = frame

    # --- Méthode pour lancer l'application ---
    def run(self):
        self.root.mainloop()


# === Frame 1 : Accueil ===
class AccueilFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="lightblue")

        tk.Label(self, text="Bienvenue dans l'application !",
                 bg="lightblue", font=("Arial", 14)).pack(pady=20)
        ttk.Button(self, text="Aller vers l'écran 2",
                   command=lambda: controller.afficher_frame(DeuxiemeFrame)).pack(pady=10)


# === Frame 2 : Deuxième écran ===
class DeuxiemeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="lightgreen")

        tk.Label(self, text="Écran 2 : contenu différent",
                 bg="lightgreen", font=("Arial", 14)).pack(pady=20)
        ttk.Button(self, text="Retour à l'accueil",
                   command=lambda: controller.afficher_frame(AccueilFrame)).pack(pady=10)


# --- Exécution ---
if __name__ == "__main__":
    app = Application()
    app.run()
