import tkinter as tk


class AffichageEcran():
    def __init__(self, master):
        # Le conteneur principal (root)
        self.master = master
        self.master.title(
            "Copropriété Monica - Analyse de l'historique du relevé général des dépenses")
        self.master.geometry("800x500")

        # Frame principale
        self.main_frame = tk.Frame(master, bg="lightblue")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Crée une sous-section par méthode
        self.creer_zone_titre()
        self.creer_zone_boutons()

    def creer_zone_titre(self):
        """Créer une frame contenant le titre"""
        self.frame_titre = tk.Frame(
            self.main_frame, bg="white", relief="groove", bd=2)
        self.frame_titre.pack(fill="x", pady=5)
        self.label_titre = tk.Label(
            self.frame_titre, text="Bienvenue !", font=("Arial", 14))
        self.label_titre.pack(padx=10, pady=5)

    def creer_zone_boutons(self):
        """Créer une frame contenant les boutons"""
        self.frame_boutons = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.frame_boutons.pack(pady=10)

        self.btn_ajouter = tk.Button(
            self.frame_boutons, text="Ajouter", command=self.ajouter_message)
        self.btn_ajouter.pack(side="left", padx=5)

        self.btn_effacer = tk.Button(
            self.frame_boutons, text="Effacer", command=self.effacer_widgets)
        self.btn_effacer.pack(side="left", padx=5)

    def ajouter_message(self):
        """Exemple d’ajout dynamique d’un widget"""
        label = tk.Label(self.main_frame, text="Nouveau message", bg="yellow")
        label.pack(pady=2)
        # Tu pourrais garder une liste de widgets créés ici
        # self.widgets.append(label)

    def effacer_widgets(self):
        """Supprime tout le contenu de la main_frame sauf les zones fixes"""
        for w in self.main_frame.winfo_children():
            if w not in (self.frame_titre, self.frame_boutons):
                w.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    cadre = AffichageEcran(root)
    root.mainloop()
