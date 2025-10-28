from sqlalchemy import Table, MetaData, Column, Integer, PrimaryKeyConstraint
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.automap import automap_base
import sqlite3
import hashlib
from sqlalchemy import create_engine, MetaData, update, text, Table, select, func, String, inspect
from sqlalchemy.orm import Session, declarative_base, mapper, class_mapper, sessionmaker
import variables_path as vc


print("Module u_sql_1 chargé avec succès.")


def supprimer_table(nom_table):
    with vc.engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {nom_table}"))
        conn.commit()


def supprimer_toutes_tables(l_tables=None, l_excepte=None):
    """
    Supprime les tables SQLite contenues dans l_tables à l'exception de celles contenues dans l_excepte
    Si l_tables est None, supprime toutes les tables de la base à l'exception de celles contenues dans l_excepte
    """
    with vc.engine.connect() as conn:
        l_excepte = [] if l_excepte is None else l_excepte
        l_tot_tables = lister_tables()
        l_tot_tables = [
            table for table in l_tot_tables if table not in l_excepte]
        if l_tables:  # si une liste de tables est fournie
            for table_name in l_tables:
                # sqlite_xxx sont des tables système
                if table_name in l_tot_tables and not table_name.startswith("sqlite_"):
                    conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                    # print(f"Table {table_name} supprimée.")
                else:
                    print(f"Table {table_name} non trouvée.")
        else:  # Si aucune liste -> supprimer toutes les tables autres que celles contenues dans l_excepte
            for table_name in l_tot_tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                print(f"Table {table_name} supprimée.")
        conn.commit()


def lister_tables():
    with vc.engine.connect() as conn:
        result = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"))
        tables = [row[0] for row in result.fetchall()]
    return tables


def supprimer_colonne_toutes_tables(nom_colonne):
    conn = sqlite3.connect(vc.REP_BDD)
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
    conn = sqlite3.connect(vc.REP_BDD)
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
    conn = sqlite3.connect(vc.REP_BDD)
    cursor = conn.cursor()

    # Récupération des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    tables = [item for item in tables if item.startswith("t_")]
    conn.close()

    for table in tables:
        conn = sqlite3.connect(vc.REP_BDD)
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
    conn = sqlite3.connect(vc.REP_BDD)
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
    cls = extraire_model_cls(nom_table)
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
        l_lignes_doublons = session.execute(stmt_all).fetchall()

    return {"lignes": l_lignes_doublons, "nb_doublons": len(l_lignes_doublons)}


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
    print(f"Schéma général de {vc.REP_BDD} - Tables : {tables}")

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


def cloner_table(db_path, source_table, new_table):
    """
    Clone une table SQLite (structure, données, index, triggers).

    :param db_path: chemin vers la base SQLite (ex: "ma_base.db")
    :param source_table: nom de la table existante à copier
    :param new_table: nom de la nouvelle table
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # --- 1) Récupérer la structure de la table ---
        cursor.execute("""
            SELECT sql 
            FROM sqlite_master 
            WHERE type='table' AND name=?;
        """, (source_table,))
        create_sql = cursor.fetchone()

        if not create_sql or not create_sql[0]:
            raise ValueError(f"Table {source_table} introuvable.")

        # Adapter le CREATE TABLE
        create_new = create_sql[0].replace(source_table, new_table, 1)
        print(f"▶ Création structure:\n{create_new}")
        cursor.execute(create_new)

        # --- 2) Copier les données ---
        cursor.execute(
            f"INSERT INTO {new_table} SELECT * FROM {source_table};")
        print("✅ Données copiées.")

        # --- 3) Recréer les index ---
        cursor.execute("""
            SELECT sql 
            FROM sqlite_master 
            WHERE type='index' AND tbl_name=? AND sql IS NOT NULL;
        """, (source_table,))
        for (index_sql,) in cursor.fetchall():
            new_index_sql = index_sql.replace(source_table, new_table, 1)
            print(f"▶ Création index:\n{new_index_sql}")
            cursor.execute(new_index_sql)

        # --- 4) Recréer les triggers ---
        cursor.execute("""
            SELECT sql 
            FROM sqlite_master 
            WHERE type='trigger' AND tbl_name=?;
        """, (source_table,))
        for (trigger_sql,) in cursor.fetchall():
            new_trigger_sql = trigger_sql.replace(source_table, new_table, 1)
            print(f"▶ Création trigger:\n{new_trigger_sql}")
            cursor.execute(new_trigger_sql)

        conn.commit()
        print(f"🎉 Table '{source_table}' clonée en '{new_table}'.")

    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur : {e}")
    finally:
        conn.close()


def run_sql_sequence(db_path, sql_statements):
    """
    Exécute une séquence de requêtes SQL dans une transaction atomique.

    :param db_path: chemin vers la base SQLite (ex: "ma_base.db")
    :param sql_statements: liste de requêtes SQL (strings)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Commence une transaction explicite
        conn.execute("BEGIN")

        for sql in sql_statements:
            print(f"▶ Exécution: {sql}")
            cursor.execute(sql)

        # Validation si tout est OK
        conn.commit()
        print("✅ Toutes les requêtes ont été exécutées avec succès.")
    except Exception as e:
        # Annulation si une erreur survient
        conn.rollback()
        print(f"❌ Erreur rencontrée: {e}")
    finally:
        conn.close()


def convertir_colonne_en_date_julien(nom_table, nom_colonne):
    ancienne_table = nom_table
    col = nom_colonne
    sql_statements1 = [
        f"ALTER TABLE {ancienne_table} ADD COLUMN date_julien REAL;",
        f"UPDATE {ancienne_table} SET date_julien = julianday({col});",
        f"ALTER TABLE {ancienne_table} DROP COLUMN {col};",
    ]
    sql_statements2 = [
        f"DROP TABLE {ancienne_table};",
        f"ALTER TABLE nouvelle_table RENAME TO {ancienne_table};",
        f"ALTER TABLE {ancienne_table} RENAME COLUMN date_julien TO {col};"
    ]

    run_sql_sequence(vc.REP_BDD, sql_statements1)
    cloner_table(vc.REP_BDD, ancienne_table, "nouvelle_table")
    run_sql_sequence(vc.REP_BDD, sql_statements2)


def introspecter_table_non_mappee(nom_table):
    # Conteneur de métadonnées
    metadata = MetaData()

    # Réflection de la table existante
    table = Table(nom_table, metadata, autoload_with=vc.engine)

    # Liste des noms de colonnes
    colonnes = [c.name for c in table.columns]
    print(colonnes)


def extraire_table_depuis_nom_table(nom_table):
    mettre_a_jour_metadata()
    metadata = vc.Base.metadata
    # Récupérer la table par son nom
    return metadata.tables[nom_table]


def vider_table(nom_table):
    conn = sqlite3.connect(vc.REP_BDD)
    conn.execute(f"DELETE FROM {nom_table};")
    conn.commit()
    conn.close()


def mettre_a_jour_mappers(classname_for_table=None):
    """
    Reconstruit un nouvel automap Base et met à jour les mappers
    en fonction de l'état actuel de la base de données.

    Args:
        engine : l'engine SQLAlchemy connecté à ta BDD
        classname_for_table : fonction optionnelle pour transformer 
                              les noms de table en noms de classes
    Returns:
        Base : un nouveau Base automap avec registry.mappers à jour
    """
    Base = automap_base()
    Base.prepare(autoload_with=vc.engine,
                 classname_for_table=classname_for_table)
    return Base


def extraire_classe_depuis_nom_table(nom_table):
    Base = mettre_a_jour_mappers()
    for mapper in Base.registry.mappers:
        if mapper.local_table.name == nom_table:
            return mapper.class_
    return None


def mettre_a_jour_metadata():
    metadata = vc.Base.metadata  # celui attaché à ton declarative_base()
    metadata.reflect(bind=vc.engine)


def attach_all_tables():
    """
    Inscrit dans Base toutes les tables de la base de données.
    Pour chaque table non encore mappée, on crée dynamiquement une classe ORM.

    :param Base: ton declarative_base()
    :param engine: SQLAlchemy engine
    :return: dict {nom_table: classe ORM}
    """
    insp = inspect(vc.engine)
    metadata = vc.Base.metadata
    mapped_classes = {}

    # toutes les tables dans la BDD
    all_tables = insp.get_table_names()

    for table_name in all_tables:
        # Vérifier si la table est déjà mappée
        if table_name in metadata.tables:
            continue

        # Réfléchir la table
        table = Table(table_name, metadata, autoload_with=vc.engine)

        # Nom de classe : CamelCase à partir du nom de table
        class_name = "".join([part.capitalize()
                             for part in table_name.split("_")])

        # Création dynamique de la classe
        cls = type(class_name, (vc.Base,), {"__table__": table})

        mapped_classes[table_name] = cls

    return mapped_classes


def check_engine(engine, check_tables: bool = True):
    """
    Vérifie que l'engine SQLAlchemy fonctionne correctement.

    - Teste une connexion avec SELECT 1
    - Si check_tables=True, liste aussi les tables présentes
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connexion réussie à la base de données.")
    except Exception as e:
        print("❌ Erreur de connexion :", e)
        return False

    if check_tables:
        try:
            insp = inspect(engine)
            tables = insp.get_table_names()
            if tables:
                print("📋 Tables trouvées :", tables)
            else:
                print("⚠️ Aucun table trouvée dans la base.")
        except Exception as e:
            print("❌ Impossible de récupérer la liste des tables :", e)
            return False

    return True


def identifier_colonnes(nom_table):
    mettre_a_jour_metadata()
    table = extraire_table_depuis_nom_table(nom_table)
    if table is not None:
        req = f"PRAGMA table_info({nom_table});"
        with vc.engine.connect() as conn:
            result = conn.execute(text(req))
            cols = result.fetchall()
            colonnes = {col[1]: [col[2], col[3], col[4], col[5]]
                        for col in cols}
            return colonnes
        return []


def attach_table_to_base_with_pk(table_name, class_name=None, pk_columns=None):
    """
    Rattache (mappe) une table existante à vc.Base en créant dynamiquement une classe ORM.
    Si la table n'a pas de PK, on peut :
      - fournir pk_columns=['col1', 'col2'], ou
      - laisser pk_columns=None et accepter l'utilisation de rowid (SQLite uniquement).
    Retourne la classe créée.
    """
    metadata = vc.Base.metadata
    if class_name is None:
        class_name = "".join(part.capitalize()
                             for part in table_name.split("_"))

    try:
        table = Table(table_name, metadata, autoload_with=vc.engine)
    except NoSuchTableError:
        raise ValueError(f"La table '{table_name}' n'existe pas dans la base.")

    # si la table a déjà une PK, on peut mapper directement
    if not any(col.primary_key for col in table.columns):
        # Option 1 : pk_columns fournis par l'utilisateur
        if pk_columns:
            missing = [c for c in pk_columns if c not in table.c]
            if missing:
                raise ValueError(
                    f"Colonnes PK demandées introuvables dans la table : {missing}")
            table.append_constraint(PrimaryKeyConstraint(
                *[table.c[c] for c in pk_columns]))

        # Option 2 : SQLite -> utiliser rowid comme clé primaire (mappage seulement, pas de DDL)
        elif vc.engine.dialect.name == "sqlite":
            # ajouter une colonne 'rowid' au Table (mappée au pseudo-colonne sqlite)
            if "rowid" not in table.c:
                table.append_column(Column("rowid", Integer, primary_key=True))
            else:
                # si pour quelque raison rowid existait, on marque comme pk
                table.c["rowid"].primary_key = True

        # Option 3 : autre SGBD ou refus de créer PK implicite
        else:
            raise ValueError(
                f"La table '{table_name}' n'a pas de clé primaire. "
                "Fournis pk_columns=['col1', ...] ou mappe en SQLAlchemy Core (Table) sans ORM."
            )

    # Création dynamique de la classe ORM rattachée à la table (et enregistrement dans Base)
    cls = type(class_name, (vc.Base,), {"__table__": table})
    return cls


def creer_colonnes(nom_table, d_noms_colonnes):
    """
    Crée dans nom_table les colonnes listées dans d_noms_colonne si elles n'existent pas déjà.
    d_noms_colonne : dict {nom_colonne: type_sql}
    """
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()

    # Vérifie que la table existe
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nom_table,))
    if not cur.fetchone():
        print(f"⚠️ Table '{nom_table}' introuvable.")
        conn.close()
        return

    # Colonnes existantes
    cur.execute(f"PRAGMA table_info({nom_table})")
    colonnes_existantes = [row[1] for row in cur.fetchall()]

    for nom_col, type_col in d_noms_colonnes.items():
        if nom_col not in colonnes_existantes:
            print(f"➕ Création de la colonne '{nom_col}' ({type_col})...")
            cur.execute(
                f'ALTER TABLE {nom_table} ADD COLUMN "{nom_col}" {type_col}')
        else:
            print(f"✅ Colonne '{nom_col}' existe déjà, rien à faire.")

    conn.commit()
    conn.close()


def nb_lig(table):
    conn = sqlite3.connect(vc.REP_BDD)
    try:
        cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
        return str(cur.fetchone()[0])
    except sqlite3.OperationalError as e:
        if "no such table" in str(e).lower():
            return f"Table '{table}' absente"
        return f"Erreur SQL: {e}"
    finally:
        conn.close()


def nb_avec_colonne_vide(table, nom_colonne):
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.execute(f"""
        SELECT COUNT(*) 
        FROM {table}
        WHERE {nom_colonne} IS NULL OR LENGTH(TRIM({nom_colonne})) = 0
    """)
    return cur.fetchone()[0]


def compter_par_exercice():
    """
    Retourne un dictionnaire {exercice: nombre_de_lignes} pour t_base_data.
    """
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()
    cur.execute("""
        SELECT exercice, COUNT(*) 
        FROM t_base_data
        GROUP BY exercice
    """)
    result = cur.fetchall()
    conn.close()
    # Construire le dictionnaire
    return {str(exercice): count for exercice, count in result}


# print(lister_tables())
if __name__ == "__main__":
    print(nb_avec_colonne_vide("t_base_data", "groupe"))
