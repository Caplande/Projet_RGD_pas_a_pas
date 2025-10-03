from sqlalchemy import create_engine, MetaData, update, inspect, text
from sqlalchemy.orm import Session
import variables_communes as vc
import src.modeles as modl
from src.utils import u_gen as u_gen, u_sql_1 as u_sql_1, u_sql_2 as u_sql_2

print("Module actualiser_donnees chargé avec succès.")


def actualiser_donnees(l_sauf):
    # 1) Supprimer tables tampon_data, tampon_parametres
    u_sql_1.supprimer_toutes_tables(["tampon_data", "tampon_parametres"])

    # 2) Charger les données excel (source_active.xlsm) actualisées
    u_gen.traiter_classeur(vc.rep_source / "source_active.xlsm", l_sauf)


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
