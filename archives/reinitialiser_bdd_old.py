from sqlalchemy import create_engine, MetaData, update, inspect, text
from sqlalchemy.orm import Session
import tkinter as tk
from tkinter import messagebox
import variables_communes as vc
from src.utils import u_gen as u_gen, u_sql_1 as u_sql_1, u_sql_2 as u_sql_2

print("Module reinitialiser_bdd chargé avec succès.")


def reinitialiser_bdd_executer():
    # 1) Supprimer toutes les tables
    # Supprime toutes les tables excepté t_lexique_cles et t_agregation
    u_sql_1.supprimer_toutes_tables(
        l_excepte=["t_lexique_cles", "t_agregation"])

    # 2) Initialiser les tables fondatrices
    for feuilles, tac in vc.composantes_bdd.items():  # tac = tâches à accomplir
        # 2.1) Convertir les données Excel en tables SQLite
        # ex tac = {"nom_fichier": "rgd_originel_completee_modifiee.xlsx", "feuilles": ["F_roc_modifiee"]}
        noms_tables = u_gen.traiter_classeur(
            vc.REP_SOURCE / tac["nom_fichier"])
    # 2.2) Norme PEP8: Normer les noms des colonnes de tampon_data (les noms des colonnes de toutes les autres tables ont été normés à partir de Excel)
    u_sql_2.normer_noms_colonnes()
    # 2.3) Normer les types des colonnes de tampon_data et tampon_parametres (les types des colonnes de toutes les autres tables ont été normés à partir de Excel)
    u_sql_2.normer_types_colonnes()
    # 2.4) Ajouter 'id' en clé primaire
    u_sql_2.adjoindre_pk()
    # 2.5) Créer la table t_lexique_cles
    u_sql_2.creer_table_lexique_cles()
    # 2.6) Composer la table t_base_data: fusion de t_agregation-tampon_data
    u_sql_2.creer_table_fusion(
        table_source1="t_agregation", table_source2="tampon_data", table_cible="t_base_data")
    # 2.7) Mettre à niveau t_base_data:Creer et valoriser une colonne exercice - supprimer les colonnes debut_periode et fin_periode -
    #                             creer et valoriser colonne cle - creer et valoriser colonne groupe - créer et valoriser
    #                             les colonnes bat_tit_yp, rub_tit_yp, typ_tit_yp
    u_sql_2.mettre_a_niveau_t_base_data()


def reinitialiser_bdd(methode, *args, **kwargs):
    """
    Demande confirmation avant d'exécuter une méthode.
    """
    reponse = messagebox.askquestion(
        "Confirmation",
        # f"Exécuter {methode.__name__} ?",
        "Re-initialiser la base à la situation de l'exercice 2024 ?",
        icon='warning'
    )
    if reponse == "yes":
        try:
            return methode(*args, **kwargs)
        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Erreur lors de l'exécution de {methode.__name__} : {e}")
    else:
        print(f"Exécution de {methode.__name__} annulée.")


if __name__ == "__main__":
    reinitialiser_bdd_executer()
