from sqlalchemy import create_engine, MetaData, update, inspect, text
from sqlalchemy.orm import Session
import variables_communes as vc
from src.utils import u_gen as u_gen, u_sql_1 as u_sql_1, u_sql_2 as u_sql_2, u_sql_3 as u_sql_3

print("Module actualiser_donnees chargé avec succès.")


def actualiser_bdd_executer():
    """ 2.1) Efface toutes les tables de la liste ["t_roc_modifiee","t_parametres"]
        2.2) Renomme t_base_data en t_base_data_ante
        2.3) Depuis source_active.xlsm crée les tables tampon_data et t_parametres.
        2.4) Norme tampon_data sur les noms de colonnes, les types, les valeurs Null, PK, les valeurs bat,rub,typ.
        2.5) Créer et calculer la colonne exercice dans tampon_data
        2.6) Merger tampon_data et t_agregation dans t_base_data (à creer)
        2.7) Créer colonne batrub
        2.8) Valorisaer la colonne groupe de t_base_data et traiter les doublons
        2.9) Mettre à jour la table des indicateurs maj_etat_bdd
"""

    # 2.1) Supprimer toutes les tables "t_roc_modifiee" et "t_parametres"
    u_sql_1.supprimer_toutes_tables(
        l_tables=["t_roc_modifiee", "t_parametres"])

    # 2.2) Renomme t_base_data en t_base_data_ante
    u_sql_2.renommer_table("t_base_data", "t_base_data_ante")

    # 2.3) Convertir les données Excel en tables SQLite
    # ex fac = {"nom_fichier": "source_active.xlsm", "feuilles": ["data",F_parametres"]}
    # Cette étape conduit à la création des tables tampon_data (feuille data) et t_parametres (feuille parametre)
    for famille, fac in vc.composantes_bdd_actualisation.items():  # fac feuilles à convertir
        nom_classeur = fac["nom_fichier"]
        u_gen.traiter_classeur(vc.rep_source / nom_classeur)
    # 2.4) Normer tampon_data
    # 2.4.1) Normer les noms de colonnes de tampon_data
    u_sql_2.normer_noms_colonnes()
    # 2.4.2) Normer types tampon_data
    u_sql_2.normer_types_colonnes(dry_run=False, l_tables=["tampon_data"])
    # 2.4.3) Normer valeurs Null
    u_sql_2.remplacer_nulls_toutes_tables(["tampon_data"])
    # 2.4.4) Adjoindre PK
    u_sql_2.promouvoir_ou_ajouter_id_en_pk("tampon_data")
    # 2.4.5) Normer valeurs bat,rub,typ
    u_sql_2.formater_bat_rub_typ(["tampon_data"])
    # 2.5) Ajouter une colonne exercice TEXT(4) à tampon_data, la calculer ensuite
    u_sql_2.ajouter_calculer_colonne_exercice_tampon_data()
    # 2.6) Merger tampon_data et t_agregation dans t_base_data (tablee à creer)
    u_sql_2.creer_peupler_table_fusion("t_agregation", "tampon_data")
    # 2.7) Créer et peupler la colonne batrub
    u_sql_2.ajouter_colonne_batrub()
    # 2.8) Valorisation de la colonne groupe de t_base_data
    # 2.8.1) Calcul de la colonne cle de la table t_base_data
    u_sql_2.maj_cle_sha256("t_base_data", vc.composantes_cle)
    # 2.8.2) Traiter les doublons dans t_base_data en numérotant la colonne rang_doublon
    u_sql_2.numeroter_doublons_par_cle()
    # 2.8.3) La colonne rang_doublon vient d'être valorisée, elle est composante du SHA256 de la cle. Il faut donc recalculer la cle
    u_sql_2.maj_cle_sha256("t_base_data", vc.composantes_cle)
    # 2.8.4) Affectation d'une valeur à la colonne groupe de t_base_data.
    #        A ce stade, t_lexique_cles est complet
    u_sql_2.maj_groupe_avec_lexique_cles("t_base_data")
    if False:
        # 2.8.5) Recalcul de la cle pour supprimer les doublons
        u_sql_2.maj_cle_et_creer_lexique()
        print(
            f"Il reste {u_sql_1.lister_doublons("t_base_data", "cle")['nb_doublons']} doublon(s) dans t_base_data")
        # 2.8) Mise à jour de la colonne groupe de t_base_data à partir de t_lexique_cles
        u_sql_2.maj_groupe_avec_lexique_cles("t_base_data")
    # 2.9) Mise à jour de la table des indicateurs
    u_sql_3.maj_etat_bdd()


if __name__ == "__main__":
    actualiser_bdd_executer()
