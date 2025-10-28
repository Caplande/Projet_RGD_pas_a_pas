import variables_path as vc
import src.utils.modeles as modl
from src.utils import u_gen as u_gen, u_sql_1 as u_sql_1
from sqlalchemy import create_engine, MetaData, update, inspect

print("Module initialiser_bdd chargé avec succès.")

if False:
    # 1) Supprimer toutes les tables
    u_sql_1.supprimer_toutes_tables()

    # 2) Importer les feuilles et les transformer en tables dans bdd.sqlite
    u_gen.traiter_classeur(vc.REP_SOURCE / "source_active.xlsm")
    u_gen.traiter_classeur(vc.REP_SOURCE / "lexiques.xlsx", ["Noms_champs"])
    u_gen.traiter_classeur(
        vc.REP_SOURCE / "RGD_Originel_completee.xlsx", ["Dates"])

    # 3) Renommer les colonnes des tables importées
    u_sql_1.renommer_toutes_colonnes_toutes_tables()

    # 4) Ajouter une clef primaire (pk) à toutes les tables
    u_sql_1.migrate_add_pk()

    # 5) Supprimer colonne "id" de toutes les tables
    u_sql_1.supprimer_colonne_toutes_tables("id")

    # 6) Renommer la colonne "pk" de toutes les tables en "id"
    u_sql_1.renommer_colonne_pk_toutes_tables("pk", "id")

    # 7) Création des classes mappées
    # L'opération est réalisée avec la commande bash:
    # sqlacodegen sqlite:///bdd/bdd.sqlite > src/modeles.py
    # qui crée le fichier src/modeles.py
    # Cette opération est à re-exécuter à chaque modification de structure d'une des tables de bdd.

    # 8) Formater les colonnes bat, rub, typ, date
    u_sql_1.formater_batrubtyp("t_originel_completee")
    u_sql_1.formater_champ("t_originel_completee", "date")

    # 9) Remplacer les valeurs Null par "" dans la table t_originel_completee

    # **********************A EFFACER *********************
    u_gen.traiter_classeur(
        vc.REP_SOURCE / "RGD_Originel_completee.xlsx", ["Dates"])
    # ******************************************************

    # Suppression des valeurs NULL dans la table "t_originel_completee"
    u_sql_1.remplacer_null_par_vide("t_originel_completee")

    # 10) Initialisation de la table "t_lexique_cles"
    u_sql_1.supprimer_table("t_lexique_cles")
    u_sql_1.creer_lexique_cles("t_originel_completee")
    doublons = u_sql_1.lister_doublons("t_originel_completee", "cle")
    print(
        f"Nombre de cle doublons: {len(doublons)} \n Liste des doublons: {doublons}\n\n")
