import sqlite3
import hashlib
from sqlalchemy import create_engine, MetaData, update, text, Table, select, func, String, inspect
from sqlalchemy.orm import Session, declarative_base, mapper, class_mapper, sessionmaker
import variables_communes as vc
from src import modeles as modl

print("Module u_sql chargé avec succès.")


def supprimer_table(nom_table):
    with vc.engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {nom_table}"))
        conn.commit()


def supprimer_toutes_tables():
    with vc.engine.connect() as conn:
        conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = conn.fetchall()
        for table in tables:
            supprimer_table(table[0])
        conn.commit()


def supprimer_colonne_toutes_tables(nom_colonne):
    conn = sqlite3.connect(vc.rep_bdd)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [t[0] for t in cursor.fetchall()]

    for nom_table in tables:
        cursor.execute(
            f"""ALTER TABLE {nom_table} DROP COLUMN {nom_colonne};""")
    conn.commit()
    conn.close()


def renommer_colonne_pk_toutes_tables(ancien_nom, nouveau_nom):
    conn = sqlite3.connect(vc.rep_bdd)
    cursor = conn.cursor()
    # Etablir la liste des tables
    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [t[0] for t in cursor.fetchall()]

    for nom_table in tables:
        cursor.execute(
            f"ALTER TABLE {nom_table} RENAME COLUMN {ancien_nom} TO {nouveau_nom};")
    conn.commit()
    conn.close()


def migrate_add_pk():
    conn = sqlite3.connect(vc.rep_bdd)
    cursor = conn.cursor()

    # Récupération des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    tables = [item for item in tables if item.startswith("t_")]
    conn.close()

    for table in tables:
        conn = sqlite3.connect(vc.rep_bdd)
        cursor = conn.cursor()
        # On récupère la définition de la table
        cursor.execute(f"PRAGMA table_info({table});")
        cols_info = cursor.fetchall()  # (cid, name, type, notnull, dflt_value, pk)
        pk_cols = [c for c in cols_info if c[5] > 0]

        # Si déjà une PK → on passe
        if pk_cols:
            continue

        # Liste colonnes existantes
        col_names = [c[1] for c in cols_info]
        col_defs = [f"{c[1]} {c[2]}" for c in cols_info]

        # Nouvelle table : ajout pk en première colonne
        new_table = f"new_{table}"
        new_schema = ", ".join(
            ["pk INTEGER PRIMARY KEY AUTOINCREMENT"] + col_defs)
        cursor.execute(f"CREATE TABLE {new_table} ({new_schema});")

        # Copie des données
        cols_str = ", ".join(col_names)
        cursor.execute(
            f"INSERT INTO {new_table} ({cols_str}) SELECT {cols_str} FROM {table};")

        # Remplacement
        cursor.execute(f"DROP TABLE {table};")
        cursor.execute(f"ALTER TABLE {new_table} RENAME TO {table};")

        conn.commit()
        conn.close()


def renommer_une_colonne(nom_table, ancien_nom, nouveau_nom):
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()
    succes = True
    try:
        req = f'ALTER TABLE {nom_table} RENAME COLUMN "{ancien_nom}" TO {nouveau_nom}'
        cur.execute(req)
        conn.commit()
    except sqlite3.Error as e:
        succes = False
    conn.close()
    return succes


def renommer_toutes_colonnes_toutes_tables():
    succes = True
    nom_table = None
    for nom_table in list(vc.d_tables_colonnes.keys()):
        for ancien_nom in list(vc.d_tables_colonnes[nom_table]):
            nouveau_nom = vc.d_tables_colonnes[nom_table][ancien_nom]
            if nouveau_nom:
                res = renommer_une_colonne(
                    nom_table, ancien_nom, nouveau_nom)
                succes = False if not res else True


def raz_colonne(nom_table, nom_colonne):
    sessionlocal = sessionmaker(vc.engine)
    cls = get_class_from_table_name(nom_table)
    col_obj = getattr(cls, nom_colonne)
    # Mettre toute la colonne ma_colonne à la valeur vide ""
    with sessionlocal() as session:
        session.execute(
            update(cls).values({col_obj: ""}))
        session.commit()


def lister_doublons(nom_table, nom_colonne):
    # Sous-requête qui liste uniquement les clés en doublon
    metadata = MetaData()
    metadata.reflect(bind=vc.engine)
    Nom_table = metadata.tables[nom_table]

    doublons_subq = (
        select(Nom_table.c.cle)
        .group_by(Nom_table.c.cle)
        .having(func.count() > 1)
        .subquery()
    )

    # Requête finale qui renvoie toutes les lignes dont la clé est en doublon
    stmt_all = select(Nom_table).where(
        Nom_table.c.cle.in_(select(doublons_subq.c.cle)))

    sessionlocal = sessionmaker(vc.engine)
    with sessionlocal() as session:
        lignes_doublons = session.execute(stmt_all).fetchall()

    return lignes_doublons


def creer_classes_mappees():
    """
    Cette procédure est là pour mémoire car l'utilisation de sqlacodegen a permis de créer et mémoriser les tables mappées.
    """
    #  1. Base ORM
    Base = declarative_base()

    # 2. Récupérer le schéma existant
    metadata = MetaData()
    metadata.reflect(bind=vc.engine)

    # 3. Générer dynamiquement les classes pour chaque table
    classes = {}

    for table_name, table in metadata.tables.items():
        # Crée une classe vide associée à la table
        cls = type(
            # Dans la cas d'une approche par introspection, ce paramètre correspond au nom de la classe (ex: "Users" pour table "users")
            table_name.capitalize(),
            (Base,),
            {"__table__": table}
        )
        classes[table_name] = cls
    return classes


def extraire_schema():
    """_summary_
    """
    # Crée un inspecteur
    inspector = inspect(vc.engine)

    # Récupérer toutes les tables
    tables = inspector.get_table_names()
    print(f"Schéma général de {vc.rep_bdd} - Tables : {tables}")

    # Détails sur une table spécifique
    for table_name in tables:
        print(f"\n--- Schéma de {table_name} ---")
        columns = inspector.get_columns(table_name)
        for col in columns:
            print(
                f"{col['name']} ({col['type']}) nullable={col['nullable']} default={col.get('default')}")

        # Clés primaires
        print("PK :", inspector.get_pk_constraint(table_name))

        # Index
        print("Index :", inspector.get_indexes(table_name))

        # Contraintes uniques
        print("Uniques :", inspector.get_unique_constraints(table_name))

        # Clés étrangères
        print("FK :", inspector.get_foreign_keys(table_name))


def visualisation_orm_des_tables(classes):
    Session = sessionmaker(bind=vc.engine)
    session = Session()
    for nom_classe in list(classes.keys()):
        classe = classes[nom_classe]
        for ligne in session.query(classe).all():
            print(ligne.__dict__)


def structure_bdd(classes):
    Session = sessionmaker(bind=vc.engine)
    session = Session()
    struct_bdd = {}
    for nom_classe in list(classes.keys()):
        struct_classe = []
        for column in classes[nom_classe].__table__.columns:
            struct_classe.append({"nom": column.name, "type": column.type,
                                 "nullable": column.nullable, "primary_key": column.primary_key})
            print(column.name, column.type, column.nullable, column.primary_key)
        struct_bdd[nom_classe] = struct_classe
    return struct_bdd


def formater_batrubtyp(nom_table):
    sessionlocal = sessionmaker(vc.engine)

    stmt1 = f"UPDATE {nom_table} SET bat = printf('%03d', CAST(bat AS INT));"
    stmt2 = f"UPDATE {nom_table} SET rub = printf('%02d', CAST(rub AS INT));"
    stmt3 = f"UPDATE {nom_table} SET typ = printf('%03d', CAST(typ AS INT));"
    with sessionlocal() as session:
        session.execute(text(stmt1))
        session.execute(text(stmt2))
        session.execute(text(stmt3))
        session.commit()


def formater_champ(nom_table, nom_champ):
    nom_col = nom_champ
    model_cls = extraire_model_cls(nom_table)
    col = getattr(model_cls, nom_col)
    sessionlocal = sessionmaker(vc.engine)
    stmt = (
        update(model_cls)
        .values({nom_col: func.lpad(col, 6, "0")})
    )
    with sessionlocal() as session:
        session.execute(stmt)
        session.commit()

    stmt = f"UPDATE {nom_table} SET date = substr(replace(date, '.0', ''), 1, 2) || '.' || substr(replace(date, '.0', ''), 3, 2) || '.' || substr(replace(date, '.0', ''), 5, 2);"
    with sessionlocal() as session:
        session.execute(text(stmt))
        session.commit()


def remplacer_null_par_vide(nom_table):
    """
    Remplace toutes les valeurs NULL de chaque colonne listée dans l_cols
    par "" si la colonne est de type texte, sinon par 0.
    """
    model_cls = extraire_model_cls(
        nom_table)  # Classe modèle correspondant à nom_table
    # Liste des colonnes de la table
    l_cols = [c.name for c in model_cls.__table__.columns]
    # Session active
    sessionlocal = sessionmaker(vc.engine)
    with sessionlocal() as session:
        for nom_col in l_cols:
            col = getattr(model_cls, nom_col)
            default_value = "" if isinstance(col.type, String) else 0
            stmt = (
                update(model_cls)
                .where(col.is_(None))
                .values({nom_col: default_value})
            )
            session.execute(stmt)
        session.commit()


def creer_lexique_cles(nom_table):
    raz_colonne(nom_table, "cle")
    sessionlocal = sessionmaker(vc.engine)
    select_sql = f"SELECT id, {vc.ccc} AS concat_val FROM {nom_table}"
    update_sql = f"UPDATE {nom_table} SET cle = :cle WHERE id = :id"

    with sessionlocal() as session:
        # Récupérer toutes les lignes (chaque row contient 2 colonnes : id, concat_val)
        rows = session.execute(text(select_sql)).fetchall()
        # session.commit()
        if not rows:
            print("Aucune ligne trouvée.")
        else:
            params = []
            controle = []
            for id, concat_val in rows:
                # cast en str par sécurité si concat_val n'est pas déjà une chaine
                digest = hashlib.sha256(
                    str(concat_val).encode("utf-8")).hexdigest()
                params.append({"cle": digest, "id": id})
                controle.append({"cle": digest, "id": id, "ligne": concat_val})
            # Exécute un executemany (passer une liste de mappings)
            session.execute(text(update_sql), params)
            session.commit()
            print(f"Controle ----> {len(controle)} ligne: {controle}")

    # Création de la table "t_lexique_cles" à partir des deux colonnes cle et groupe de "t_originel_completee"
    with vc.engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE t_lexique_cles AS
            SELECT cle, groupe
            FROM t_originel_completee;
        """))
        conn.commit()


def extraire_model_cls(nom_cls):
    # Extraction de la classe mappée
    Base = modl.Base
    model_cls = None
    for mapper in Base.registry.mappers:
        if mapper.local_table.name == nom_cls:
            model_cls = mapper.class_
            break
    return model_cls


def get_class_from_table_name(table_name):
    for cls in modl.Base.registry.mappers:
        if cls.local_table.name == table_name:
            return cls.class_
    return None
