import tkinter as tk
from tkinter import messagebox
from typing import dataclass_transform
from src.core.context import context as ctxt
from src.ui.pages.accueil_page import AccueilPage as ap
from src.ui.pages.general_page import GeneralPage as gp
from src.ui.pages.mise_a_jour_page import MiseAJourPage as map
from src.ui.pages.edition_page import EditionPage as ep
from src.ui.pages.qualite_base_page import QualiteBasePage as qbp
from src.ui.pages.affichage_page import AffichagePage as afp
from src.ui.pages.selection_enregistrements_page import SelectionEnregistrementsPage as sep
from src.core import actualiser_donnees as ad, edit_speciales as e_s, reinitialiser_bdd as rb, synoptique as sy
from src.core import resultats as res
from src.utils import u_sql_3 as u_sql_3

print("Module activation_ecran chargé avec succès.")


def activer_ecran():
    """
    Active l'écran principal :
    - construit l'UI si nécessaire
    - masque le contenu actuel
    - affiche la page d'accueil
    - trace l'état des widgets si mode debug activé
    """

    debug = getattr(ctxt, "debug_ui", False)

    # --- Construction UI ---
    if not ctxt.ecran.is_ui_built:
        if debug:
            print(">>> Construction de l’UI (ecran non construit)")
        ctxt.ecran.construire_ui()

    # --- Debug avant masquage ---
    if debug:
        print("\n************* AVANT HIDE *************")
        ctxt.wtm.print_tree_status()

    # --- Masquage du contenu principal ---
    ctxt.wtm.hide_contenu("tk/fr_centre")

    # --- Debug après masquage ---
    if debug:
        print("\n************* APRÈS HIDE *************")
        ctxt.wtm.print_tree_status()

    # --- Affichage page d’accueil ---
    if debug:
        print("\n>>> Affichage de la page_accueil via afficher_page()")

    ctxt.ecran.afficher_page("page_accueil")

    # --- Debug final ---
    if debug:
        print("\n************* APRÈS afficher_page *************")
        ctxt.wtm.print_tree_status()

        page_accueil = ctxt.ecran.pages["page_accueil"]
        print("→ Manager page_accueil :", page_accueil.winfo_manager())


def afficher_avancement(nom_page, msg):
    page = ctxt.ecran.pages[nom_page]   # type: ignore
    page.avancement.config(text=msg)


def creer_menu(menubar):
    menu_v1 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Général", menu=menu_v1)

    menu_v2 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Mise à jour", menu=menu_v2)

    menu_v3 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Edition", menu=menu_v3)

    menu_v4 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Qualité de la base", menu=menu_v4)

    menu_v5 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(
        label="Sélection enregistrements", menu=menu_v5)

    menu_v6 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Affichage", menu=menu_v6)

    # on garde les index de chaque item pour pouvoir les (dés)activer
    menu_v1.add_command(
        label="Fermer projet", command=lambda: executer_action("Fermeture du projet...", "10"))
    menu_v1.add_command(
        label="Bidon", command=lambda: bidon)
    menu_v1.add_separator()
    menu_v1.add_command(
        label="Choix3", command=lambda: executer_action("Choix3", "3"))

    menu_v2.add_command(
        label="Actualiser données", command=lambda: executer_action("Actualiser données...", "20"))
    menu_v2.add_separator()
    menu_v2.add_command(
        label="Réinitialiser à situation 2024", command=lambda: executer_action("Réinitialiser à situation 2024...", "21"))

    menu_v3.add_command(
        label="Document intégral par typ", command=lambda: executer_action("Document intégral par typ...", "30"))
    menu_v3.add_command(
        label="Document intégral par groupe", command=lambda: executer_action("Document intégral par groupe...", "31"))
    menu_v3.add_separator()
    menu_v3.add_command(
        label="Document partiel par typ", command=lambda: executer_action("Document partiel par typ...", "32"))
    menu_v3.add_command(
        label="Document partiel par groupe", command=lambda: executer_action("Document partiel par groupe...", "33"))

    menu_v4.add_command(
        label="Statistiques de la base", command=lambda: executer_action("Statistiques de la base...", "40"))

    menu_v5.add_command(
        label="Selection enregistrements", command=lambda: executer_action("Selection enregistrements...", "50"))

    menu_v6.add_command(
        label="Affichage", command=lambda: executer_action("Affichage...", "60"))

    def executer_action(message, index_menu: str):
        match index_menu:
            case "10":
                ctxt.ecran.afficher_page("page_general")  # type: ignore
                ctxt.ecran.quit()  # type: ignore
            case "20":
                ctxt.ecran.afficher_page("page_miseajour")  # type: ignore

                print("************************************************")
                # hierarchie = u_sql_3.hierarchie_widgets(ctxt.ecran)
                # print(f"hierarchie = {hierarchie}")
                print("************************************************")

                ctxt.ecran.pages["page_miseajour"].avancement.config(  # type: ignore
                    text='Actualisation démarrée')
                ad.actualiser_bdd(ad.actualiser_bdd_executer)
            case "21":
                ctxt.ecran.afficher_page("page_miseajour")  # type: ignore
                rb.reinitialiser_bdd(rb.reinitialiser_bdd_executer)
            case "30":
                ctxt.ecran.afficher_page("page_edition")  # type: ignore
                res.creer_pdf_pivot_hierarchique_vue_typ()
            case "31":
                ctxt.ecran.afficher_page("page_edition")  # type: ignore
                res.creer_pdf_pivot_hierarchique_vue_groupe()
            case "32":
                ctxt.ecran.afficher_page("page_edition")  # type: ignore
                res.ed_spec_par_typ()
            case "33":
                ctxt.ecran.afficher_page("page_edition")  # type: ignore
                res.ed_spec_par_groupe()
            case "40":
                ctxt.ecran.afficher_page(  # type: ignore
                    "page_qualitebase")  # type: ignore
                sy.afficher_table()
            case "50":
                ctxt.ecran.afficher_page(  # type: ignore
                    "page_selectionenregistrements")  # type: ignore
            case "60":
                ctxt.ecran.afficher_page("page_affichage")  # type: ignore
                # **********************************************************************
                # u_sql_3.appliquer_couleur_orange_fond(
                #     ctxt.ecran.pages["page_affichage"])  # type: ignore
                # **********************************************************************
                ctxt.ecran.changer_theme()  # type: ignore
            case _:
                messagebox.showinfo(
                    "Action", f"Tu as sélectionné : {message}")

    def bidon(self):
        messagebox.showinfo("Action", "bidon...")
