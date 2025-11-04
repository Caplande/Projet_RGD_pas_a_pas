# app_context est l'instance singleton de AppContext. NE DOIT ËTRE IMPORTEE NULLE PART AILLEURS QUE DANS main.py.
# Dans les autres modules, faire: from src.core.context import context
from src.core.context import context as ctxt
# launch_ui lance l'ouverture de la fenetre de l'application
from src.ui.app_ui import launch_ui

if __name__ == "__main__":
    # instanciation de la base de données et connexion
    conn = ctxt.db.connect()
    print("Connexion établie sur :", ctxt.path_bdd)

    # Active le menu principal et lance l'interface
    launch_ui(ctxt)  # Active le menu principal et lance l'interface
