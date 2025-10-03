from sqlalchemy import create_engine, MetaData, update, inspect, text
from sqlalchemy.orm import Session
import variables_communes as vc
import src.modeles as modl
from src.utils import u_gen as u_gen, u_sql_1 as u_sql_1

print("Module actualiser_donnees chargé avec succès.")


def actualiser_donnees(l_sauf):
    # 1) Supprimer tables tampon_data, tampon_parametres
    u_sql_1.supprimer_toutes_tables(["tampon_data", "tampon_parametres"])

    # 2) Charger les données excel (source_active.xlsm) actualisées
    u_gen.traiter_classeur(vc.rep_source / "source_active.xlsm", l_sauf)


def copier_donnees(nom_source, nom_cible, correspondance_noms=None, correspondance_source_types=None, correspondance_cible_types=None):
    classe_source = u_sql_1.extraire_classe_depuis_nom_table(nom_source)
    classe_cible = u_sql_1.extraire_classe_depuis_nom_table(nom_cible)
    table_source = u_sql_1.extraire_table_depuis_nom_table(nom_source)
    table_cible = u_sql_1.extraire_table_depuis_nom_table(nom_cible)
    with Session(vc.engine) as session:
        if not (correspondance_noms and correspondance_source_types and correspondance_cible_types):
            try:
                data = session.query(classe_source).all()
                mappings = [
                    {c.name: getattr(obj, c.name)
                     for c in classe_source.__table__.columns}
                    for obj in session.query(classe_source).all()
                ]
                session.bulk_insert_mappings(classe_cible, mappings)
                session.commit()
                print(
                    f"{len(mappings)} lignes copiées de {classe_source} vers {classe_cible}.")
            except Exception as e:
                session.rollback()
                print(
                    f"Echec transfert de données de{classe_source} vers {classe_cible}.", e)
        else:
            select_parts = []
            cols_source = [col for col in correspondance_source_types.keys(
            ) if correspondance_source_types[col][3] == 0 and col != 'id']
            cols_cible = []
            for col_source in cols_source:
                col_cible = vc.nom_originel_nom_pep8[col_source]
                type_cible = correspondance_cible_types[col_cible][0].split("(")[
                    0].upper()
                if type_cible:
                    select_parts.append(
                        f"CAST([{col_source}] AS {type_cible})")
                else:
                    select_parts.append(col_source)
                cols_cible.append(col_cible)
            select_clause = ", ".join(select_parts)
            cols_cible_clause = ", ".join(cols_cible)
            # Construire la requête complète
            sql = f"""
            INSERT INTO {table_cible} ({cols_cible_clause})
            SELECT {select_clause}
            FROM {table_source};
            """
            # print("Requête générée :")
            # print(sql)
            result = session.execute(text(sql))
            print(f"{result} lignes copiées de {classe_source} vers {classe_cible}.")
        session.commit()
        pass


def peupler_donnees_courantes_bdd():
    u_sql_1.mettre_a_jour_metadata()
    u_sql_1.vider_table("t_data")
    u_sql_1.vider_table("t_parametres")
    copier_donnees("tampon_data", "t_data",
                   vc.nom_originel_nom_pep8, vc.tampon_data_types, vc.t_data_types)
    copier_donnees("t_agregation", "t_data")
    copier_donnees("tampon_parametres", "t_parametres")
