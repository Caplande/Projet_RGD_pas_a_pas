from sqlalchemy import create_engine, MetaData, update, inspect, text
from sqlalchemy.orm import Session
import variables_communes as vc
import src.utils.modeles as modl
from src.utils import u_gen as u_gen, u_sql_1 as u_sql_1, u_sql_2 as u_sql_2

print("Module actualiser_donnees chargé avec succès.")


def actualiser_donnees():
    # 1) Supprimer toutes les tables
    # Supprime toutes les tables excepté t_lexique_cles et t_agregation
    u_sql_1.supprimer_toutes_tables(l_tables=["tampon_data", "tampon_parametres"]
                                    )
    # 2) Convertir les feuilles data et Parametres
    # 2.1) Convertir les données Excel en tables SQLite
    # ex tac = {"nom_fichier": "rgd_originel_completee_modifiee.xlsx", "feuilles": ["F_roc_modifiee"]}
    l_noms_tables = u_gen.traiter_classeur(
        vc.REP_SOURCE / "source_active.xlsm", l_sauf=["F_agregation"])
    # 2.2) Norme PEP8: Normer les noms des colonnes de tampon_data (les noms des colonnes de toutes les autres tables ont été normés à partir de Excel)
    u_sql_2.normer_noms_colonnes()
    # 2.3) Normer les types des colonnes de tampon_data (les types des colonnes de toutes les autres tables ont été normés à partir de Excel)
    u_sql_2.normer_types_colonnes(l_tables=l_noms_tables)
    # 2.4) Ajouter 'id' en clé primaire
    u_sql_2.adjoindre_pk(l_tables=l_noms_tables)

    u_sql_2.formater_bat_rub_typ(["tampon_data"])
