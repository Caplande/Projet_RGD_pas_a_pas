from sqlalchemy import create_engine, MetaData, update, inspect, text
from sqlalchemy.orm import Session
import tkinter as tk
from tkinter import messagebox
import variables_communes as vc
from src.utils import u_gen as u_gen, u_sql_1 as u_sql_1, u_sql_2 as u_sql_2

print("Module reinitialiser_bdd chargé avec succès.")


def reinitialiser_bdd_executer():
    # 1) Supprimer toutes les tables
    # Supprime toutes les tables
    u_sql_1.supprimer_toutes_tables()

    # 2) Initialiser les tables fondatrices
    # 2.1) Convertir les données Excel en tables SQLite
    # ex tac = {"nom_fichier": "rgd_originel_completee_modifiee.xlsm", "feuilles": ["F_roc_modifiee"]}
    for famille, fac in vc.composantes_bdd_initialisation.items():  # fac feuilles à convertir
        nom_classeur = fac["nom_fichier"]
        u_gen.traiter_classeur(vc.rep_source / nom_classeur)
    # 2.2) Recensement des tables nécessaires à l'initialisation
    u_sql_2.verifier_tables_existent(vc.l_tables_source)
    # 2.3) Normer les types des colonnes de toutes les tables
    for nom_table in vc.l_tables_source:
        u_sql_2.modifier_types_colonnes(nom_table)
    # 2.4) Normer les valeurs bat, rub, typ de l'ensemble des tables
    u_sql_2.formater_bat_rub_typ(vc.l_tables_source)
    # 2.5) Eliminer toutes les valeurs Null de toutes les tables de la bdd
    u_sql_2.remplacer_nulls_toutes_tables()
    # 2.6) Ajouter PK à chacune des tables de la BDD
    u_sql_2.adjoindre_pk()
    # 2.7) Fusionner dans t_base_data (table à créer) les deux tables t_roc_modifiee et t_agregation
    u_sql_2.creer_peupler_table_fusion(
        table_source1="t_agregation", table_source2="t_roc_modifiee")
    # 2.8) Créer la table t_lexique_cles et mettre à jour colonne cle de t_base_data
    #      Après exécution de cette procédure, les colonnes cle et groupe de t_lexique_cles et t_base_data
    #      sont à jour des groupes identifiés dans t_roc_modifiee
    u_sql_2.maj_cle_et_creer_lexique()
    # 2.9) Traiter les doublons dans t_base_data en numérotant la colonne rang_doublon
    u_sql_2.numeroter_doublons_par_cle()
    # 2.10) Recalcul de la cle pour supprimer les doublons
    u_sql_2.maj_cle_et_creer_lexique()
    print(
        f"Il reste {u_sql_1.lister_doublons("t_base_data", "cle")['nb_doublons']} doublon(s) dans t_base_data")


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
    # u_sql_2.adjoindre_pk()
    # u_sql_2.creer_peupler_table_fusion(
    #    table_source1="t_agregation", table_source2="t_roc_modifiee")
    # u_sql_2.maj_cle_et_creer_lexique()
