import tkinter as tk
from tkinter import messagebox
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

print("Module activation_ecran chargé avec succès.")


def activer_ecran():
    noms_pages = {'!accueilpage': 'page_accueil', '!generalpage': 'page_general', '!miseajourpage': 'page_miseajour_page', '!editionpage': 'page_edition',
                  '!qualitebasepage': 'page_qualitebase', '!selectionenregistrementspage': 'page_selectionenregistrements', '!affichagepage': 'page_affichage'}
    for P in (ap, gp, map, ep,
              qbp, afp, sep):
        # On instancie chaque page dans le frame fr_centre.
        page = P(ctxt.ecran.fr_centre)  # type: ignore
        # Attention les noms des pages ne répondent pas à la norme PEP8. Ex: l'instance de AccueilPage est stockée sous le nom "AccueilPage" au lieu de "accueil_page".
        # ctxt.ecran.pages[P.__name__] = page  # type: ignore
        ctxt.ecran.pages[noms_pages[page._name]] = page  # type: ignore
    ctxt.ecran.afficher_page("page_accueil")  # type: ignore

    creer_menu(ctxt.ecran.menubar)  # type: ignore


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
    menubar.add_cascade(label="Sélection enregistrements", menu=menu_v5)

    menu_v6 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Affichage", menu=menu_v6)

    # on garde les index de chaque item pour pouvoir les (dés)activer
    menu_v1.add_command(
        label="Fermer projet", command=lambda: executer_action("Fermeture du projet...", "10"))
    menu_v1.add_command(
        label="Bidon", command=lambda: bidon)
    menu_v1.add_separator()
    menu_v1.add_command(
        label="Choix3", command=lambda: executer_action("Choix3", 3))

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


def executer_action(message, index_menu):
    match index_menu:
        case "10":
            ctxt.ecran.afficher_page("page_general")  # type: ignore
            ctxt.ecran.quit()  # type: ignore
        case "20":
            ctxt.ecran.afficher_page("page_miseajour")  # type: ignore
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
            ctxt.ecran.afficher_page("page_qualitebase")  # type: ignore
            sy.afficher_table()
        case "50":
            ctxt.ecran.afficher_page(  # type: ignore
                "page_selectionenregistrements")  # type: ignore
        case "60":
            ctxt.ecran.afficher_page("page_affichage")  # type: ignore
            ctxt.ecran.afficher_choix_palettes_polices()  # type: ignore

            # type: ignore
            # page = ctxt.ecran.pages["SelectionEnregistrementsPage"]
            # page.pack(fill="both", expand=True)
            # La page "SelectionEnregistrementsPage" est instanciée dans ctxt.ecran.pages à l'exécution de activer_ecran() (main.py)
            # ctxt.ecran.afficher_page(  # type: ignore
            #    "SelectionEnregistrementsPage")  # type: ignore
            # e_s.afficher_dans_frame()
            # sep.creer_vue_base()
            # sep.afficher_vue(ctxt.ecran.label_statut_2.config(  # type: ignore
            # type: ignore
            #    text=f"Nombre d'enregistrements : {e_s.compter_selection()}"))
        case _:
            messagebox.showinfo("Action", f"Tu as sélectionné : {message}")


def bidon(self):
    messagebox.showinfo("Action", "bidon...")
