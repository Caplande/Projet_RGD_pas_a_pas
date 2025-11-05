# Importer context suppose, au premier appel l'exécution du module complet (donc l'instanciation de AppContext).
# Lors des autres appels, on récupère juste l'instance déjà créée.
from src.core.context import context as ctxt
from src.ui.app_ui import AppUi as AppUi
from src.ui.activation_ecran import activer_ecran as activer_ecran

if __name__ == "__main__":
    # instanciation de la base de données et connexion
    # conn = ctxt.db.connect()
    # print("Connexion établie sur :", ctxt.path_bdd)

    # Active le menu principal et lance l'interface
    """Point d'entrée pour l'interface."""
    app = AppUi(ctxt)  # Instance de tk.Tk()
    # Pour pouvoir accéder à l'interface depuis le contexte global
    ctxt.set_ecran(app)
    activer_ecran()
    app.mainloop()
