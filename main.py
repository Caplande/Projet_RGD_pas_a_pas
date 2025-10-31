# app_context est l'instance singleton de AppContext. NE DOIT ËTRE IMPORTEE NULLE PART AILLEURS QUE DANS main.py
from src.core.context import app_context
# launch_ui lance l'ouverture de la fenetre de l'application
from src.ui.app_ui import launch_ui

if __name__ == "__main__":
    # instanciation de la base de données et connexion
    conn = app_context.db.connect()
    print("Connexion établie sur :", app_context.db_path)

    # Active le menu principal et lance l'interface
    launch_ui(app_context)  # Active le menu principal et lance l'interface
