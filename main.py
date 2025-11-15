# Importer context suppose, au premier appel l'exécution du module complet (donc l'instanciation de AppContext).
# Lors des autres appels, on récupère juste l'instance déjà créée.
import types
from src.core.context import context as ctxt
from src.ui.app_ui import AppUi as AppUi
from src.ui.activation_ecran import activer_ecran as activer_ecran
from src.utils.u_sql_3 import WidgetTreeManager

if __name__ == "__main__":
    # Active le menu principal et lance l'interface
    """Point d'entrée pour l'interface."""
    app = AppUi()  # Instance de tk.Tk()
    # Pour pouvoir accéder à l'interface depuis le contexte global
    # L'instance singleton de AppUi est stockée dans le singleton ctxt sous le nom d'attribut: 'ecran'
    ctxt.set_ecran(app)
    ctxt.wtm = WidgetTreeManager(ctxt.ecran)
    activer_ecran()

    app.mainloop()
