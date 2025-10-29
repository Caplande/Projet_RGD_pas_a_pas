import parametres  # locale et palettes
# app_context est l'instance singleton de AppContext
from src.core.context import app_context
# launch_ui lance l'ouverture de la fenetre de l'application
from src.ui.app_ui import launch_ui

if __name__ == "__main__":
    conn = app_context.db.connect()
    print("Connexion établie sur :", app_context.db_path)
    launch_ui(app_context)  # Active le menu principal et lance l'interface
