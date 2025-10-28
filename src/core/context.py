from sqlalchemy import create_engine, MetaData, inspect, __version__  # type: ignore
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import registry, declarative_base
import tkinter as tk


composantes_bdd = {
    "feuilles_roc": {"nom_fichier": "rgd_originel_completee_modifiee.xlsm", "feuilles": ["F_roc_modifiee", "F_parametres", "F_agregation"]},
    "feuilles_lexiques": {"nom_fichier": "lexiques.xlsx", "feuilles": ["F_definition_cles_repartitions", "F_lexique_batrub", "F_lexique_bat", "F_lexique_rub", "F_lexique_typ",
                          "F_liste_groupes", "F_liste_group_a_etudier"]},
    "feuilles_source_active": {"nom_fichier": "source_active.xlsm", "feuilles": ["data", "F_parametres"]}
}

composantes_bdd_initialisation = {
    "feuilles_roc": {"nom_fichier": "rgd_originel_completee_modifiee.xlsm", "feuilles": ["F_roc_modifiee", "F_parametres", "F_agregation"]},
    "feuilles_lexiques": {"nom_fichier": "lexiques.xlsx", "feuilles": ["F_definition_cles_repartitions", "F_lexique_batrub", "F_lexique_bat", "F_lexique_rub", "F_lexique_typ",
                          "F_liste_groupes", "F_liste_group_a_etudier"]}}

composantes_bdd_actualisation = {
    "feuilles_roc": {"nom_fichier": "source_active.xlsm", "feuilles": ["data", "F_parametres"]},
}

l_tables_source = ["t_agregation", "t_definition_cles_repartitions", "t_lexique_batrub", "t_lexique_bat", "t_lexique_rub", "t_lexique_typ", "t_liste_groupes", "t_liste_groupes_a_etudier",
                   "t_roc_modifiee", "t_parametres"]
mapping_tampon_data = {"id": "id", "Type d'appel": "type_appel", 'Libelle': 'libelle1', 'Debut de periode': 'debut_periode', 'Fin de periode': 'fin_periode', 'Periode Cloturee': 'periode_cloturee',
                       'Numéro du batiment': 'bat', 'Nom du batiment': 'bat_tit', 'Numéro de la rubrique': 'rub', 'Nom de la rubrique': 'rub_tit', 'Num type charge': 'typ',
                       'Nom du type de charge': 'typ_tit', 'Date': 'date_a', 'Libelle.1': 'libelle', 'Reference': 'reference', 'Montant à repartir': 'montant', 'Nom du fournisseur': 'nom_fournisseur',
                       "exercice": "exercice"}

lexique_colonnes_types = {'id': 'INTEGER', 'exercice': 'TEXT (4)', 'type_appel': 'TEXT (2)', 'libelle1': 'TEXT', 'periode_cloturee': 'TEXT (1)', 'bat': 'TEXT (3)', 'bat_tit': 'TEXT (50)', 'rub': 'TEXT (2)', 'rub_tit': 'TEXT (50)',
                          'typ': 'TEXT (3)', 'typ_tit': 'TEXT (50)', 'batrub': 'TEXT (6)', 'libelle': 'TEXT (50)', 'reference': 'TEXT (50)', 'montant': 'FLOAT', 'nom_fournisseur': 'TEXT (50)',
                          'debut_periode': 'REAL', 'fin_periode': 'REAL', 'date_a': 'REAL', 'indicateur': 'TEXT (50)', 'valeur': 'TEXT (50)', 'bat_tit_yp': 'TEXT (50)',
                          'rub_tit_yp': 'TEXT (50)', "typ_tit_yp": 'TEXT (50)', 'batrub_tit_yp': 'TEXT (50)', 'entites': 'TEXT (30)', 'rgpt_entites': 'TEXT (30)', 'groupe': 'TEXT (30)'}

composantes_cle = ["exercice", "bat", "rub", "typ", "date_a",
                   "libelle", "reference", "nom_fournisseur", "montant", "rang_doublon"]

colonnes_t_base_data = {'id': 'INTEGER', 'type_appel': 'TEXT (2)', 'exercice': 'TEXT (4)',
                        'periode_cloturee': 'TEXT (1)', 'bat': 'TEXT (3)', 'bat_tit': 'TEXT (50)', 'rub': 'TEXT (2)', 'rub_tit': 'TEXT (50)', 'typ': 'TEXT (3)',
                        'typ_tit': 'TEXT (50)', 'date_a': 'REAL', 'libelle': 'TEXT (50)', 'reference': 'TEXT (50)', 'montant': 'FLOAT', 'nom_fournisseur': 'TEXT (50)',
                        'rang_doublon': 'INTEGER', 'groupe': 'TEXT (30)', 'cle': 'TEXT'}

# Colonnes composantes de la cle
ccc = "bat  ||  rub  ||  typ  ||  date  ||  libelle  ||  reference  ||  montant  ||  nom_fournisseur || rang_doublon"
# ccc_v = "{bat} , {rub} , {typ} , {date} , {libelle} , {reference} , {montant} , {nom_fournisseur} , {rang_doublon}"

if __name__ == '__main__':
    root = tk.Tk()
    cadre = AffichageEcran(root)
    root.mainloop()
