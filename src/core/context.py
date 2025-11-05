from pathlib import Path
import tkinter as tk
import parametres as config
import src.core.variables_metier_path as vmp
import src.core.variables_metier as vm
from src.core.data import Database  # ta classe qui gère SQLite
from colorama import Fore, Style

print("Module context chargé avec succès.")


class AppContext:
    """Contexte global de l'application :
    - chemins
    - connexion à la base
    - configuration partagée
    """
    nb_instances = 0  # Attribut de classe pour le singleton

    def __init__(self):
        # *******************
        AppContext.nb_instances += 1
        if AppContext.nb_instances > 1:
            print(
                Fore.RED + f"Nb instances AppUi = {AppContext.nb_instances}" + Style.RESET_ALL)
        # *******************
        # Constantes descriptives de l'application
        self.mode_debug = getattr(config, "MODE_DEBUG", False)
        self.version = getattr(config, "VERSION", "xxx.x.x")
        self.nom_application = getattr(
            config, "NOM_APPLICATION", "a déterminer")
        self.nom_court = getattr(
            config, "NOM_COURT", "a déterminer")
        self.palettes = getattr(config, "PALETTES", {})
        self.polices = getattr(config, "POLICES", {})
        self.palette = getattr(config, "PALETTE", {})
        self.police = getattr(config, "POLICE", {})

        # Dossiers structurants
        self.dir_defaut = vmp.REP_DEFAUT
        self.dir_sources = vmp.REP_SOURCE
        self.dir_resultats = vmp.REP_RESULTATS
        self.dir_data = vmp.REP_DATA  # répertoire bdd.sqlite
        self.dir_resultats = vmp.REP_RESULTATS

        # Fichier de base de données
        # self.db_path = self.paths["data"] / "bdd.sqlite"
        self.path_bdd = vmp.REP_BDD

        # Création de l'instance de base de données et de toutes les fonctionnalités qui lui sont attachées
        self.db = Database()

        # Accès SQLITE à la base de données via SQLAlchemy
        self.engine = vmp.ENGINE

        # Variables métier partagées
        self.vm_composantes_bdd = vm.composantes_bdd
        self.vm_composantes_bdd_initialisation = vm.composantes_bdd_initialisation
        self.vm_composantes_bdd_actualisation = vm.composantes_bdd_actualisation
        self.vm_l_tables_source = vm.l_tables_source
        self.vm_mapping_tampon_data = vm.mapping_tampon_data
        self.vm_lexique_colonnes_types = vm.lexique_colonnes_types
        self.vm_composantes_cle = vm.composantes_cle
        self.vm_colonnes_t_base_data = vm.colonnes_t_base_data
        self.vm_ccc = vm.ccc

        # Référence à la fenêtre principale de l'application (AppUi)
        self.ecran = None

    def set_ecran(self, ecran):
        self.ecran = ecran


# Singleton : une seule instance réutilisable partout. Créée au moment de l'importation du module context.py depuis main.py
app_context = AppContext()
context = app_context

if __name__ == '__main__':
    liste_attributs = [attr for attr in dir(
        app_context) if not attr.startswith("__")]
    print(liste_attributs)
