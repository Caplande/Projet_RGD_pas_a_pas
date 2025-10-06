from sqlalchemy import create_engine, MetaData, update, inspect, text
from sqlalchemy.orm import Session
import variables_communes as vc

from src.utils import u_gen as u_gen, u_sql_1 as u_sql_1, u_sql_2 as u_sql_2

print("Module reinitialiser_bdd chargé avec succès.")


def reinitialiser_bdd():
    # 1) Supprimer toutes les tables
    u_sql_1.supprimer_toutes_tables()

    # 2) Initialiser les tables fondatrices
    for feuilles, tac in vc.composantes_bdd.items():  # tac = tâches à accomplir
        # 2.1) Convertir les données Excel en tables SQLite
        # ex tac = {"nom_fichier": "rgd_originel_completee_modifiee.xlsx", "feuilles": ["F_roc_modifiee"]}
        noms_tables = u_gen.traiter_classeur(
            vc.rep_source / tac["nom_fichier"])
    # 2.2) Norme PEP8: Normer les noms des colonnes de tampon_data (les noms des colonnes de toutes les autres tables ont été normés à partir de Excel)
    u_sql_2.normer_noms_colonnes()
    # 2.3) Normer les types des colonnes de tampon_data (les types des colonnes de toutes les autres tables ont été normés à partir de Excel)
    u_sql_2.normer_types_colonnes()
    # 2.4) Ajouter 'id' en clé primaire
    u_sql_2.adjoindre_pk()
    # 2.5) Créer la table t_lexique_cles
    u_sql_2.creer_table_lexique_cles()
    if False:
        # 2) Charger les données excel (rgd_originel_completee_modifiee.xlsx)
        # Contient la feuille (1): F_roc_modifee
        u_gen.traiter_classeur(
            vc.rep_source / "rgd_originel_completee_modifiee.xlsx")

        # 3) Charger les données excel (lexiques.xlsx)
        # Contient les feuilles (7): F_lexique_batrub, F_lexique_bat,
        # F_lexique_rub, F_lexique_typ, F_definition_cles_repartitions,
        # F_liste_groupes, F_liste_group_a_etudier
        u_gen.traiter_classeur(vc.rep_source / "lexiques.xlsx",
                               ["Nom champs", "Règles de nommage (PEP8)", "Classe vs Table"])

        # 4) Charger les données excel (source_active.xlsm) actualisées
        # Contient les feuilles (3): data, F_Agregation, Parametres
        u_gen.traiter_classeur(vc.rep_source / "source_active.xlsm")


def peupler_donnees_courantes_bdd():
    u_sql_1.mettre_a_jour_metadata()
    u_sql_1.vider_table("t_data")
    u_sql_1.vider_table("t_parametres")
    u_sql_2.copier_donnees_sql(
        "t_agregation", "t_data", vc.mapping_t_agregation)
    u_sql_2.copier_donnees_sql("tampon_data", "t_data",
                               vc.mapping_tampon_t_data, vc.t_data_types)
    u_sql_2.copier_donnees_sql("tampon_parametres", "t_parametres",
                               vc.mapping_tampon_t_parametres, vc.t_parametres_types)
