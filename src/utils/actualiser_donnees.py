from sqlalchemy import create_engine, MetaData, update, inspect, text
from sqlalchemy.orm import Session
import variables_communes as vc
import src.utils.modeles as modl
from src.utils import u_gen as u_gen, u_sql_1 as u_sql_1, u_sql_2 as u_sql_2

print("Module actualiser_donnees chargé avec succès.")


def actualiser_bdd_executer():
    """ 2.1) Efface toutes les tables de la liste ["t_roc_modifiee","t_parametres"]
        2.2) Renomme t_base_data en t_base_data_ante
        2.3) Depuis source_active.xlsm crée les tables tampon_data et t_parametres.
        2.4) Norme tampon_data sur les noms de colonnes, les types, les valeurs Null, PK, les valeurs bat,rub,typ.
        2.5) Merger tampon_data et t_agregation dans t_base_data (à creer)
"""

    # 2.1) Supprimer toutes les tables
    u_sql_1.supprimer_toutes_tables(
        l_tables=["t_roc_modifiee", "t_parametres"])

    # 2.2) Renomme t_base_data en t_base_data_ante
    u_sql_2.renommer_table("t_base_data", "t_base_data_ante")

    # 2.3) Convertir les données Excel en tables SQLite
    # ex fac = {"nom_fichier": "source_active.xlsm", "feuilles": ["data",F_parametres"]}
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

    # 2.5) Merger tampon_data et t_agregation dans t_base_data (à creer)
    u_sql_2.creer_peupler_table_fusion("t_agregation", "tampon_data")

    if False:
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
        # 2.8) Créer la table t_lexique_cles et mettre à jour colonne clé de t_base_data
        u_sql_2.maj_cle_et_creer_lexique()


if __name__ == "__main__":
    actualiser_bdd_executer()
