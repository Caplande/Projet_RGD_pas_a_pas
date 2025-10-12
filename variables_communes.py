# %pip install sqlalchemy

from pathlib import Path
from sqlalchemy import create_engine, MetaData, inspect, __version__  # type: ignore
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import registry, declarative_base
# from src.utils import modeles as modls
import locale

print("Module variables_communes chargé avec succès.")

rep_defaut = Path.cwd()
print(f"VC_1 ---> Répertoire par défaut {rep_defaut}")

rep_source = rep_defaut / "sources"

rep_bdd = rep_defaut / "bdd" / "bdd.sqlite"

print(f"VC_2 ---> Version SQLAlchemy {__version__}")

# Mettre la locale française pour les noms de mois/jours
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

try:
    DATABASE_URL = "sqlite:///./bdd/bdd.sqlite"
    engine = create_engine(DATABASE_URL)
    print(f"VC_3 ---> Création de engine réussie")

except Exception as e:
    print(f"VC_3 ---> Erreur lors de la création de l'engine : {e}")
    print(f"VC_4 ---> Erreur lors de la création de Base : {e}")

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
if False:
    d_feuille_table = {'data': 't_base_data', 'Parametres': 't_parametres', 'F_RGD_Originel_completee': 't_originel_completee',
                       'F_definition_cles_repartitions': 't_cles_repartition', 'F_lexique_batrub': 't_lexique_batrub',
                       'F_lexique_bat': 't_lexique_bat', 'F_lexique_rub': 't_lexique_rub', 'F_lexique_typ': 't_lexique_typ',
                       'F_liste_groupes': 't_liste_groupes', 'F_liste_group_a_etudier': 't_groupes_a_etudier_par_facture',
                       'F_agregation': 't_agregation'}

    d_tables_colonnes = {"t_base_data": {"Type d'appel": "type_appel", "cle": "cle", "Exercice": "exercice", "Libelle": "libelle1", "Debut de periode": "debut_periode", "Fin de periode": "fin_periode",
                                         "Periode Cloturee": "periode_cloturee", "Numéro du batiment": "bat", "BAT": "bat", "Nom du batiment": "bat_tit", "RUB": "rub",
                                         "Numéro de la rubrique": "rub", "Nom de la rubrique": "rub_tit", "Num type charge": "typ", "TYP": "typ", "Nom du type de charge": "typ_tit", "BATRUBTYP": "batrubtyp",
                                         "BATRUB": "batrub", "Date": "date", "Libelle.1": "libelle", "Reference": "reference", "Montant à repartir": "montant_a_repartir",
                                         "Nom du fournisseur": "nom_fournisseur"},
                         "t_parametres": {"Indicateur": "indicateur", "Valeur": "valeur"},
                         "t_Originel_completee": {"Exercice": "exercice", "Periode Cloturee": "periode_cloturee", "BAT": "bat", "RUB": "rub", "TYP": "typ", "Nom du type de charge": "typ_tit",
                                                  "BATRUBTYP": "batrubtyp", "BATRUB": "batrub", "Date": "\"date\"", "Libelle1": "libelle", "Reference": "reference", "Montant1": "montant1",
                                                  "Nom du fournisseur": "nom_fournisseur", "Rang_doublon": "rang_doublon", "Groupe": "groupe", "Montant": "montant"}
                         }

    nom_originel_nom_pep8 = {"id": "id", "Type d'appel": "type_appel", "Libelle": "libelle1", "Debut de periode": "debut_periode", "Fin de periode": "fin_periode",
                             "Periode Cloturee": "periode_cloturee", "Numéro du batiment": "bat", "Nom du batiment": "bat_tit", "Numéro de la rubrique": "rub",
                             "Nom de la rubrique": "rub_tit", "Num type charge": "typ", "Nom du type de charge": "typ_tit", "Date": "date_a", "Libelle.1": "libelle",
                             "Reference": "reference", "Montant à repartir": "montant", "Nom du fournisseur": "nom_fournisseur"}

    mapping_t_agregation = {"type_appel": "type_appel", "libelle1": "libelle1", "debut_periode": "debut_periode", "fin_periode": "fin_periode",
                            "periode_cloturee": "periode_cloturee", "bat": "bat", "bat_tit": "bat_tit", "rub": "rub", "rub_tit": "rub_tit", "typ": "typ",
                            "typ_tit": "typ_tit", "date_a": "date_a", "libelle": "libelle", "reference": "reference", "montant": "montant", "nom_fournisseur": "nom_fournisseur"}

    mapping_tampon_t_base_data = {"Type d'appel": "type_appel", "Libelle": "libelle1", "Debut de periode": "debut_periode", "Fin de periode": "fin_periode",
                                  "Periode Cloturee": "periode_cloturee", "Numéro du batiment": "bat", "Nom du batiment": "bat_tit", "Numéro de la rubrique": "rub",
                                  "Nom de la rubrique": "rub_tit", "Num type charge": "typ", "Nom du type de charge": "typ_tit", "Date": "date_a", "Libelle.1": "libelle",
                                  "Reference": "reference", "Montant à repartir": "montant", "Nom du fournisseur": "nom_fournisseur"}

    mapping_tampon_t_parametres = {
        "Indicateur": "indicateur", "Valeur": "valeur"}

    t_base_data_types = {'type_appel': 'TEXT (2)', 'libelle1': 'TEXT', 'periode_cloturee': 'TEXT', 'bat': 'TEXT (3)', 'bat_tit': 'TEXT (50)', 'rub': 'TEXT (2)', 'rub_tit': 'TEXT (50)',
                         'typ': 'TEXT (3)', 'typ_tit': 'TEXT (50)', 'libelle': 'TEXT (50)', 'reference': 'TEXT (50)', 'montant': 'FLOAT', 'nom_fournisseur': 'TEXT (50)',
                         'debut_periode': 'REAL', 'fin_periode': 'REAL', 'date_a': 'REAL'}

    t_parametres_types = {'indicateur': 'TEXT (50)', 'valeur': 'TEXT (50)'}

# Colonnes composantes de la cle
ccc = "bat  ||  rub  ||  typ  ||  date  ||  libelle  ||  reference  ||  montant  ||  nom_fournisseur || rang_doublon"
# ccc_v = "{bat} , {rub} , {typ} , {date} , {libelle} , {reference} , {montant} , {nom_fournisseur} , {rang_doublon}"
