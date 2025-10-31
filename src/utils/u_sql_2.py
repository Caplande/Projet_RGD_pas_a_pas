import re
import sys
import sqlite3
import hashlib
from sqlalchemy import MetaData, delete, inspect, Table, Column, Integer, String, Text, Float, REAL, create_engine
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional
import pandas as pd
import src.core.variables_metier_path as vc
from src.utils import u_sql_1 as u1

print("Module u_sql_2 chargé avec succès.")

sys.stdout.reconfigure(encoding='utf-8')  # type: ignore


def synoptique_1(engine, Base):
    insp = inspect(engine)
    metadata = maj_metadata()

    # Tables réelles dans SQLite
    tables_reelles = set(insp.get_table_names())

    # Classes mappées -> Tables Python
    classes_mappees = {
        mapper.class_.__name__: mapper.local_table
        for mapper in Base.registry.mappers
    }

    # Tables Python présentes dans metadata
    tables_python = metadata.tables

    # Ensemble global de tous les noms de tables
    tout = set(tables_reelles) | set(tables_python.keys()) | {
        t.name for t in classes_mappees.values()}

    lignes = []
    for nom_table in sorted(tout):
        # Classe associée
        classe_associee = next(
            (cls for cls, table in classes_mappees.items() if table.name == nom_table),
            None
        )
        # Objet Python Table
        table_python = tables_python.get(nom_table)

        # Détermination du statut
        if nom_table in tables_reelles and classe_associee is not None and table_python is not None:
            statut = "Complet ✅"
        elif nom_table not in tables_reelles:
            statut = "Table réelle absente ❌"
        elif classe_associee is None:
            statut = "Classe manquante ❌"
        elif table_python is None:
            statut = "Objet Python Table manquant ❌"
        else:
            statut = "Incohérence ⚠️"

        lignes.append({
            "Table réelle SQLite3": nom_table if nom_table in tables_reelles else None,
            "Classe mappée": classe_associee,
            "Objet Python Table": table_python,
            "Statut global": statut
        })

    df = pd.DataFrame(lignes)

    # Fonction de style pour coloriser
    def coloriser(val):
        if val is None or "❌" in str(val):
            return "background-color: #f8d7da; color: red; font-weight: bold;"
        elif "✅" in str(val):
            return "background-color: #d4edda; color: green; font-weight: bold;"
        elif "⚠️" in str(val):
            return "background-color: #fff3cd; color: orange; font-style: italic;"
        else:
            return "background-color: #888888; color: black;"  # par défaut

    # Application du style
    styled = df.style.map(coloriser)
    return styled


def synoptique(engine, Base):
    insp = inspect(engine)
    metadata = maj_metadata()

    # Tables réelles dans SQLite
    tables_reelles = set(insp.get_table_names())

    # Classes mappées -> Tables Python
    classes_mappees = {
        mapper.class_.__name__: mapper.local_table
        for mapper in Base.registry.mappers
    }

    # Tables Python présentes dans metadata
    tables_python = metadata.tables

    # Ensemble global de tous les noms de tables
    tout = set(tables_reelles) | set(tables_python.keys()) | {
        t.name for t in classes_mappees.values()}

    lignes = []
    for nom_table in sorted(tout):
        # Classe associée
        classe_associee = next(
            (cls for cls, table in classes_mappees.items() if table.name == nom_table),
            None
        )
        # Objet Python Table
        table_python = tables_python.get(nom_table)

        lignes.append({
            "Table réelle SQLite3": nom_table if nom_table in tables_reelles else None,
            "Classe mappée": classe_associee,
            "Objet Python Table": table_python
        })

    return pd.DataFrame(lignes)


def inventaire_dict(engine, Base):
    """
    Retourne un dict de la forme :
    {
        "Nom": {
            "classe_orm": <classe ou None>,
            "table_reelle": <nom table BDD ou None>,
            "table_python": <objet Table ou None>
        },
        ...
    }
    """
    insp = inspect(engine)

    # Tables réelles
    tables_reelles = set(insp.get_table_names())

    # Classes ORM mappées
    classes_mappees = {
        mapper.class_.__name__: mapper.class_
        for mapper in Base.registry.mappers
    }
    classes_vers_tables = {
        mapper.class_.__name__: mapper.local_table.name
        for mapper in Base.registry.mappers
    }

    # Tables Python (metadata)
    maj_metadata()
    tables_python = Base.metadata.tables

    # Fusion de tous les noms possibles
    noms = set(classes_mappees.keys()) | set(
        classes_vers_tables.values()) | tables_reelles | set(tables_python.keys())

    resultat = {}
    for nom in sorted(noms):
        resultat[nom] = {
            "classe_orm": classes_mappees.get(nom, None),
            "table_reelle": nom if nom in tables_reelles else None,
            "table_python": tables_python.get(nom, None),
        }

    return resultat


def inventaire_complet(engine, Base):
    """
    Retourne un DataFrame listant :
    - les classes ORM
    - les tables réelles en BDD
    - les objets Python Table
    - la correspondance Classe ↔ Table
    """
    insp = inspect(engine)

    # 1. Tables réelles en base
    tables_reelles = set(insp.get_table_names())

    # 2. Classes ORM mappées (Classe → Table)
    classes_mappees = {
        mapper.class_.__name__: mapper.local_table.name
        for mapper in Base.registry.mappers
    }

    # 3. Objets Python Table connus de metadata
    maj_metadata()
    tables_python = set(Base.metadata.tables.keys())

    # Fusion des noms possibles
    noms = set(classes_mappees.keys()) | set(
        classes_mappees.values()) | tables_reelles | tables_python

    rows = []
    for nom in sorted(noms):
        # Existence dans chaque monde
        est_classe = nom in classes_mappees.keys()
        est_table_reelle = nom in tables_reelles
        est_table_python = nom in tables_python

        # Correspondance éventuelle Classe ↔ Table
        correspondance = None
        if est_classe:
            correspondance = f"{nom} ↔ {classes_mappees[nom]}"

        rows.append({
            "Nom": nom,
            "Classe ORM": "✅" if est_classe else "❌",
            "Table réelle (BDD)": "✅" if est_table_reelle else "❌",
            "Objet Python Table": "✅" if est_table_python else "❌",
            "Correspondance": correspondance or "-"
        })

    return pd.DataFrame(rows)


def lister_tables_reelles():
    insp = inspect(vc.engine)
    # Tables réelles
    return set(insp.get_table_names())


def lister_classes_mappees(Base):
    return {
        mapper.class_.__name__: mapper.class_
        for mapper in Base.registry.mappers
    }


def lister_tables_python(Base):
    """Attention, ces tables python existent dès que la classe ORM est définie, même si elles ne sont pas encore créées en base."""
    return {
        mapper.class_.__name__: mapper.local_table.name
        for mapper in Base.registry.mappers
    }


def inventaire_1(engine, Base):
    """
    Liste l'état complet des classes mappées et des tables réelles.
    Retourne un dict {nom: etat}.
    """
    insp = inspect(engine)

    # Tables réelles en base
    tables_reelles = set(insp.get_table_names())

    # Classes ORM mappées
    classes_mappees = {
        mapper.class_.__name__: mapper.local_table.name
        for mapper in Base.registry.mappers
    }

    # Fusion des noms : classes + tables
    noms = set(tables_reelles) | set(
        classes_mappees.keys()) | set(classes_mappees.values())

    resultat = {}
    for nom in noms:
        est_classe = nom in classes_mappees or any(
            nom == table for table in classes_mappees.values())
        est_table = nom in tables_reelles

        if est_classe and est_table:
            etat = "Classe ORM + Table réelle"
        elif est_classe:
            etat = "Classe ORM seulement"
        elif est_table:
            etat = "Table réelle seulement"
        else:
            etat = "Inexistant"  # normalement impossible ici

        resultat[nom] = etat

    return resultat


def maj_metadata():
    global metadata
    metadata = MetaData()
    metadata.reflect(bind=vc.engine)
    print("Metadata mis à jour")
    return metadata


def vider_table(nom_table):
    if nom_table in lister_tables_reelles():
        table = metadata.tables[nom_table]
        with vc.engine.begin() as conn:
            conn.execute(delete(table))  # supprime toutes les lignes
        print(f"La table '{nom_table}' a été vidée.")
    else:
        print(f"La table '{nom_table}' n'existe pas.")


def supprimer_table(nom_table):
    global metadata
    maj_metadata()
    if nom_table in metadata.tables:
        table = metadata.tables[nom_table]
        table.drop(vc.engine, checkfirst=True)
        metadata = maj_metadata()
        print(f"La table '{nom_table}' a été supprimée.")
    else:
        print(f"La table '{nom_table}' n'existe pas.")


def a_une_pk(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name});")
    cols = cursor.fetchall()

    pk_cols = [col[1] for col in cols if col[5] > 0]  # col[5] = pk
    conn.close()

    if pk_cols:
        return True, pk_cols
    else:
        return False, []


def promouvoir_ou_ajouter_id_en_pk(table_name):
    conn = sqlite3.connect(vc.REP_BDD)
    cursor = conn.cursor()

    # Récupérer la structure de la table
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns_info = cursor.fetchall()

    # Colonnes existantes : [(nom, type)]
    cols = [(c[1], c[2]) for c in columns_info]
    col_names = [c[0] for c in cols]

    # Ajouter la colonne id si elle n’existe pas
    if "id" not in col_names:
        print(
            f"ℹ️  La table '{table_name}' n’a pas de colonne 'id' — elle sera ajoutée.")
        # on met id au début, mais c’est facultatif
        cols.insert(0, ("id", "INTEGER"))
        col_names.insert(0, "id")

    # 1. Renommer l'ancienne table
    cursor.execute(f"ALTER TABLE {table_name} RENAME TO {table_name}_old;")

    # 2. Recréer la nouvelle table avec id en PK
    cols_def = []
    for name, ctype in cols:
        if name == "id":
            cols_def.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        else:
            cols_def.append(f""""{name}" {ctype}""")
    create_sql = f"""CREATE TABLE {table_name} ({', '.join(cols_def)});"""
    cursor.execute(create_sql)

    # 3. Copier les données
    # Si id n'existait pas, on ne le copie pas (SQLite l'auto-remplira)
    if "id" in [c[0] for c in columns_info]:
        insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(col_names)})
            SELECT {', '.join(col_names)} FROM {table_name}_old;
        """
    else:
        cols_sans_id = [c for c in col_names if c != "id"]
        insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(cols_sans_id)})
            SELECT {', '.join(cols_sans_id)} FROM {table_name}_old;
        """
    cursor.execute(insert_sql)

    # 4. Supprimer l'ancienne table
    cursor.execute(f"DROP TABLE {table_name}_old;")

    conn.commit()
    conn.close()
    print(
        f"✅ Colonne 'id' présente et promue en PRIMARY KEY dans '{table_name}'.")


def creer_classes_manquantes():
    def classname_for_table(base, tablename, table):
        return ''.join(word.capitalize() for word in tablename.split('_'))

    # Base dynamique
    Base = automap_base()

    # Préparer l'automap AVANT d'accéder à Base.classes
    # surcharge de la fonction de nommage
    Base.prepare(autoload_with=vc.engine,
                 classname_for_table=classname_for_table)

    # Extraire les classes mappées
    print("Classes ORM disponibles :", list(Base.classes.keys()))

    # Les classes générées
    for cls_name in Base.classes.keys():
        print("Classe ORM existante :", cls_name)

    return Base


def style_negative(df, color="red", bold=True):
    """
    Applique un style aux valeurs négatives d'un DataFrame en évitant les erreurs de type.
    """
    def styler(val):
        if isinstance(val, (int, float)):  # uniquement si c'est un nombre
            if val < 0:
                style = f"color: {color};"
                if bold:
                    style += " font-weight: bold;"
                return style
        return ""

    return df.style.map(styler)


def lister_classes_tables(Base, format="chaine"):
    """
    Liste les classes ORM connues dans Base.registry.mappers.

    Args:
        Base : le declarative_base()
        format : "chaine", "tuple", ou "dict"
            - "chaine" : liste de str "Classe -> table"
            - "tuple"  : liste de tuples (Classe, table)
            - "dict"   : dict {table: Classe}
    """
    if format == "chaine":
        return [
            f"{mapper.class_.__name__} -> {mapper.class_.__table__.name}"
            for mapper in Base.registry.mappers
        ]
    elif format == "tuple":
        return [
            (mapper.class_.__name__, mapper.class_.__table__.name)
            for mapper in Base.registry.mappers
        ]
    elif format == "dict":
        return {
            mapper.class_.__table__.name: mapper.class_
            for mapper in Base.registry.mappers
        }
    else:
        raise ValueError(
            "Format inconnu. Utiliser 'chaine', 'tuple' ou 'dict'.")


def copier_donnees_sql(table_src, table_dst, mapping, conversions=None):
    """
    Copie les données d'une table source vers une table destination avec renommage et conversion.

    Args:
        conn : connexion sqlite3
        table_src (str) : nom de la table source
        table_dst (str) : nom de la table destination
        mapping (dict) : correspondance {col_dst: col_src}
        conversions (dict) : conversions optionnelles {col_dst: "TYPE"} pour CAST

    Exemple:
        mapping = {"identifiant": "id", "prenom": "nom", "age": "age"}
        conversions = {"age": "INTEGER"}
    """

    def cast_and_format(src_col, dest_col, dest_type):
        """Retourne l'expression SQL pour CAST + printf si besoin"""
        if dest_col == 'bat':
            return f"printf('%03d', CAST(\"{src_col}\" AS INTEGER)) AS {dest_col}"
        elif dest_col == 'rub':
            return f"printf('%02d', CAST(\"{src_col}\" AS INTEGER)) AS {dest_col}"
        elif 'REAL' in dest_type:
            return f'CAST("{src_col}" AS REAL) AS {dest_col}'
        elif 'TEXT' in dest_type:
            return f'CAST("{src_col}" AS TEXT) AS {dest_col}'
        elif 'FLOAT' in dest_type:
            return f'CAST("{src_col}" AS FLOAT) AS {dest_col}'
        else:
            return f'"{src_col}" AS {dest_col}'

    # génération des parties de la requête
    cols_dest = []
    cols_src = []
    if conversions:
        for src_col, dest_col in mapping.items():
            cols_dest.append(dest_col)
            cols_src.append(cast_and_format(
                src_col, dest_col, conversions[dest_col]))
    else:
        for src_col, dest_col in mapping.items():
            cols_dest.append(dest_col)
            cols_src.append(f'"{src_col}" AS {dest_col}')

    # construction finale
    sql = f"""
    INSERT INTO {table_dst} ({", ".join(cols_dest)})
    SELECT
        {",\n    ".join(cols_src)}
    FROM {table_src};
    """
    print(f"SQL avant purification: {sql}")
    sql = u_gen.purifier_sql(sql)
    print(f"SQL après purification: {sql}")

    conn = sqlite3.connect(vc.REP_BDD)
    conn.execute(sql)

    # Suppression de la table source
    conn.execute(f"DROP TABLE IF EXISTS {table_src};")
    conn.commit()


def normer_noms_colonnes():
    """
    Norme les noms des colonnes de la table data dans la table "tampon_data"
    """

    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()

    # Récupérer la structure de la table tampon_data
    cur.execute(f"PRAGMA table_info(tampon_data);")
    columns_info = cur.fetchall()

    # Colonnes existantes : [(nom, type)]
    cols = [(c[1]) for c in columns_info]

    # Créer une nouvelle liste de colonnes normalisées
    new_cols = []
    for name in cols:
        new_cols.append(vc.mapping_tampon_data[name])

    for old, new in zip(cols, new_cols):
        # les anciens noms non conformes doivent être entourés de guillemets doubles
        cur.execute(f'ALTER TABLE tampon_data RENAME COLUMN "{old}" TO {new};')

    conn.commit()
    conn.close()

    print(f"✅ Noms des colonnes normalisés dans tampon_data'.")


def normer_types_colonnes(dry_run=False, l_tables=None):
    """
    Normalise les types de colonnes de toutes les tables SQLite selon le lexique fourni.
    Si dry_run=True, affiche les modifications sans toucher à la base.
    """
    lexique = vc.lexique_colonnes_types

    conn = sqlite3.connect(vc.REP_BDD)
    cursor = conn.cursor()

    if not l_tables:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        l_tables = [row[0] for row in cursor.fetchall()]

        print(f"🔍 {len(l_tables)} l_tables détectées dans la base.")

    for table in l_tables:
        cursor.execute(f"PRAGMA table_info({table});")
        colonnes_info = cursor.fetchall()

        cols_def, cols_noms = [], []
        besoin_recreer = False
        changements = []

        for cid, nom, type_col, notnull, default, pk in colonnes_info:
            type_ref = lexique.get(nom, type_col)
            if type_ref != type_col:
                besoin_recreer = True
                changements.append((nom, type_col, type_ref))
            cols_def.append(f"{nom} {type_ref}")
            cols_noms.append(nom)

        if besoin_recreer:
            print(f"\n⚙️ Table {table} : types divergents détectés")
            for nom, avant, apres in changements:
                print(f"   - {nom}: {avant} → {apres}")

            if not dry_run:
                temp_table = f"{table}_old"
                try:
                    cursor.execute(
                        f"ALTER TABLE {table} RENAME TO {temp_table};")
                    cursor.execute(
                        f"CREATE TABLE {table} ({', '.join(cols_def)});")
                    cursor.execute(
                        f"INSERT INTO {table} ({', '.join(cols_noms)}) "
                        f"SELECT {', '.join(cols_noms)} FROM {temp_table};"
                    )
                    cursor.execute(f"DROP TABLE {temp_table};")
                    conn.commit()
                    print(f"✅ Table {table} normalisée.")
                except Exception as e:
                    print(f"❌ Erreur sur {table}: {e}")
                    conn.rollback()
            else:
                print("   (Simulation : aucune modification appliquée)")

    conn.close()
    print("\n🎯 Normalisation des types terminée.")


def adjoindre_pk(l_tables=None):
    """
    Pour chaque table de l_tables_source :
      - ajoute une colonne 'id' si elle n'existe pas
      - crée une clé primaire sur 'id' si la table n'en a pas déjà
      - conserve les types et contraintes des autres colonnes
    """
    l_tables = l_tables if l_tables else vc.l_tables_source
    conn = sqlite3.connect(vc.REP_BDD)
    cursor = conn.cursor()

    for table in l_tables:
        # --- structure initiale ---
        cursor.execute(f"PRAGMA table_info({table});")
        infos = cursor.fetchall()
        noms_cols = [col[1] for col in infos]
        pk_existante = any(col[5] for col in infos)

        # --- ajouter id si absent ---
        if "id" not in noms_cols:
            print(f"🆕 Ajout de la colonne 'id' dans {table}")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN id INTEGER;")

            # recharger infos après modification
            cursor.execute(f"PRAGMA table_info({table});")
            infos = cursor.fetchall()
            noms_cols = [col[1] for col in infos]

        # --- si pas encore de PK, la recréer proprement ---
        if not pk_existante:
            print(f"🔑 Création de la clé primaire sur 'id' dans {table}")

            # Renommer l’ancienne
            cursor.execute(f"ALTER TABLE {table} RENAME TO {table}_old;")

            # Liste des colonnes autres que id
            colonnes_autres = [col for col in infos if col[1] != "id"]

            # Construire la définition SQL des colonnes
            def fmt_col(col):
                nom, type_col, notnull, dflt_value = col[1], col[2], col[3], col[4]
                s = f"{nom} {type_col or ''}".strip()
                if notnull:
                    s += " NOT NULL"
                if dflt_value is not None:
                    s += f" DEFAULT {dflt_value}"
                return s

            colonnes_def = ", ".join(fmt_col(c) for c in colonnes_autres)

            # Recréer la table avec id comme PK
            cursor.execute(f"""
                CREATE TABLE {table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {colonnes_def}
                );
            """)

            # Copier les données
            noms_autres = ", ".join(c[1] for c in colonnes_autres)
            cursor.execute(f"""
                INSERT INTO {table} ({noms_autres})
                SELECT {noms_autres} FROM {table}_old;
            """)

            # Supprimer l’ancienne
            cursor.execute(f"DROP TABLE {table}_old;")

    conn.commit()


def remplacer_nulls_toutes_tables(l_tables=None):
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()

    if not l_tables:
        # Récupérer la liste des tables (hors tables système SQLite)
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        l_tables = [row[0] for row in cur.fetchall()]

    for table in l_tables:
        print(f"🔧 Table : {table}")
        # Récupérer les colonnes de la table
        cur.execute(f"PRAGMA table_info({table})")
        colonnes = [row[1] for row in cur.fetchall()]

        # Pour chaque colonne, remplacer les NULL par ""
        for col in colonnes:
            try:
                cur.execute(
                    f"UPDATE {table} SET {col} = '' WHERE {col} IS NULL")
            except Exception as e:
                print(f"⚠️  Colonne {col} ignorée ({e})")

    conn.commit()
    conn.close()
    print("✅ Tous les NULL ont été remplacés par des chaînes vides.")


def maj_cle_et_creer_lexique():
    """
    Si les colonnes composantes de la clé dans t_base_data existent, alors la colonne cle de t_base_data est peuplée.
    Les deux colonnes groupe et cle de t_base_data sont ensuite copiées dans les colonnes du même nom de t_lexique_cles
    Cet enchainenemnt signifie qu'il ne faut jamais mettre à jour directement t_lexique_cles mais passer par l'intermédiaire de t_base_data
    """
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()

    # récupération des noms de colonnes composant la clé
    colonnes_cle = vc.composantes_cle

    # Vérifier que les colonnes existent dans t_base_data
    cur.execute("PRAGMA table_info(t_base_data)")
    colonnes_existantes = [row[1] for row in cur.fetchall()]
    manquantes = [c for c in colonnes_cle if c not in colonnes_existantes]
    if manquantes:
        raise ValueError(
            f"Colonnes manquantes dans t_base_data : {manquantes}")

    # Récupérer les données pour calculer les SHA256
    cols_str = ", ".join(colonnes_cle)
    cur.execute(f"SELECT id, {cols_str} FROM t_base_data")
    lignes = cur.fetchall()

    for ligne in lignes:
        id_val = ligne[0]
        valeurs_concat = "".join("" if v is None else str(v)
                                 for v in ligne[1:])
        cle_sha = hashlib.sha256(valeurs_concat.encode("utf-8")).hexdigest()
        cur.execute("UPDATE t_base_data SET cle=? WHERE id=?",
                    (cle_sha, id_val))
    conn.commit()

    # Création (ou remplacement) et peuplement de t_lexique_cles
    cur.execute("""
        DROP TABLE IF EXISTS t_lexique_cles;""")
    cur.execute("""
        CREATE TABLE t_lexique_cles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cle TEXT,
            groupe TEXT(30),
            id_source INTEGER,
            libelle TEXT(50),
            montant FLOAT,
            date_a REAL
        );""")
    cur.execute("""
        INSERT INTO t_lexique_cles (cle, groupe, id_source,libelle,montant,date_a)
        SELECT cle, groupe, id, libelle,montant, date_a
        FROM t_base_data
        WHERE cle IS NOT NULL AND groupe IS NOT NULL;
        """)

    conn.commit()
    conn.close()

    print(
        f"✅ Table t_lexique_cles: colonne 'cle' mise à jour pour {len(lignes)} lignes.")


def formater_bat_rub_typ(l_tables):
    conn = sqlite3.connect(vc.REP_BDD)
    cursor = conn.cursor()
    for table in l_tables:
        # Vérifier que la table contient bien les colonnes à formater
        cursor.execute(f"PRAGMA table_info({table})")
        colonnes = [col[1] for col in cursor.fetchall()]

        for col, fmt in [('bat', '000'), ('rub', '00'), ('typ', '000')]:
            if col in colonnes:
                longueur = len(fmt)
                # Mettre à jour la colonne en la formatant à la bonne longueur avec des zéros à gauche
                cursor.execute(f"""
                    UPDATE {table}
                    SET {col} = printf('%0{longueur}d', CAST({col} AS INTEGER))
                    WHERE {col} IS NOT NULL AND TRIM({col}) <> '';
                """)
                print(
                    f"✅ Colonne '{col}' formatée dans la table '{table}' ({fmt})")
    conn.commit()


def table_existe(nom_table):
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?;",
        (nom_table,)
    )
    return cur.fetchone() is not None


class TableInexistanteError(Exception):
    """Erreur levée quand une table est absente de la base."""
    pass


def compter_lignes(nom_table, cdtn=None, annee=None):
    conn = sqlite3.connect(vc.REP_BDD)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nom_table,))
    existe = cursor.fetchone()
    if not existe:
        raise TableInexistanteError(
            f"La table '{nom_table}' n'existe pas dans la base de données.")

    requete = f"SELECT COUNT(*) FROM {nom_table}"
    clauses = []
    params = []

    if cdtn:
        clauses.append(cdtn)
    if annee is not None:
        clauses.append("strftime('%Y', ma_date) = ?")
        params.append(str(annee))

    if clauses:
        requete += " WHERE " + " AND ".join(clauses)

    cursor.execute(requete, tuple(params))
    nb_lignes = cursor.fetchone()[0]

    message = f"La table '{nom_table}' contient {nb_lignes} lignes"
    if cdtn:
        message += f" répondant à la condition: {cdtn}"
    if annee:
        message += f" pour l'exercice: {annee}"
    message += "."
    print(message)

    conn.close()
    return nb_lignes


def creer_peupler_table_fusion(table_source1, table_source2):
    """
    Création de la table t_base_data
    Copie dans t_base_data la totalité contenus de table_source1 et table_source2
    Toutes les colonnes de table_source1 et table_source2 doivent être présentes dans t_base_data
    Toutes les colonnes de t_base_data ne doivent pas être présentes dans table_source1 et table_source2
    Args:
        table_source1 (_type_): _description_
        table_source2 (_type_): _description_
        t_base_data (_type_): _description_

    Returns:
        _type_: _description_
    """
    conn = sqlite3.connect(vc.REP_BDD)
    cursor = conn.cursor()

    # 1. Supprimer si déjà existante
    cursor.execute("DROP TABLE IF EXISTS t_base_data")

    # 2. Créer la table cible selon le dictionnaire avec id en PK
    colonnes_def = ", ".join(
        [f"{col} {typ} PRIMARY KEY" if col == "id" else f"{col} {typ}"
         for col, typ in vc.colonnes_t_base_data.items()]
    )
    cursor.execute(f"CREATE TABLE t_base_data ({colonnes_def})")

    # 3. Fonction pour récupérer les colonnes d'une table

    def colonnes_table(table):
        cursor.execute(f"PRAGMA table_info({table})")
        return [row[1] for row in cursor.fetchall()]

    # 4. Identifier les types numériques
    types_numeriques = ("INT", "REAL", "FLOAT", "BIGINT")

    # 5. Copier les données depuis chaque table
    lignes_par_source = {}
    for table_source in [table_source1, table_source2]:
        cols_src = colonnes_table(table_source)
        colonnes_cibles = list(vc.colonnes_t_base_data.keys())

        select_expr = []
        # on retire 'id' des colonnes cibles
        colonnes_sans_id = [c for c in colonnes_cibles if c != "id"]

        select_expr = []
        for col in colonnes_sans_id:
            if col in cols_src:
                select_expr.append(col)
            else:
                type_col = vc.colonnes_t_base_data[col].upper()
                if any(t in type_col for t in types_numeriques):
                    select_expr.append(f"0 AS {col}")
                else:
                    select_expr.append(f"'' AS {col}")

        select_sql = f"SELECT {', '.join(select_expr)} FROM {table_source}"
        insert_sql = f"INSERT INTO t_base_data ({', '.join(colonnes_sans_id)}) {select_sql}"
        cursor.execute(insert_sql)

        # Compter les lignes copiées
        cursor.execute(f"SELECT COUNT(*) FROM {table_source}")
        lignes_par_source[table_source] = cursor.fetchone()[0]

    conn.commit()

    # 6. Vérification finale
    cursor.execute("SELECT COUNT(*) FROM t_base_data")
    total = cursor.fetchone()[0]

    print("✅ Table t_base_data créée et peuplée avec succès.")
    print(
        f" - {table_source1} : {lignes_par_source[table_source1]} lignes copiées")
    print(
        f" - {table_source2} : {lignes_par_source[table_source2]} lignes copiées")
    print(f" - Total final dans t_base_data : {total} lignes\n")

    return lignes_par_source, total


def maj_cle_sha256(nom_table, l_colonnes_composantes):
    """
    Met à jour la colonne 'cle' dans la table `nom_table`
    en calculant un SHA256 basé sur la concaténation des valeurs
    des colonnes listées dans `l_colonnes_composantes`.

    Args:
        nom_table (str): nom de la table à modifier.
        l_colonnes_composantes (list[str]): liste des noms de colonnes à concaténer.
        chemin_bdd (str): chemin du fichier SQLite.
    """
    if not l_colonnes_composantes:
        print("⚠️  Liste de colonnes vide — aucune mise à jour effectuée.")
        return

    try:
        conn = sqlite3.connect(vc.REP_BDD)
        cur = conn.cursor()

        # Vérifie si la colonne 'cle' existe, sinon la crée
        cur.execute(f"PRAGMA table_info({nom_table})")
        colonnes_existantes = [info[1] for info in cur.fetchall()]
        if "cle" not in colonnes_existantes:
            cur.execute(f"ALTER TABLE {nom_table} ADD COLUMN cle TEXT")

        # Concaténation SQL des colonnes
        expr_concat = " || '' || ".join(l_colonnes_composantes)

        # Récupère les lignes à traiter
        cur.execute(
            f"SELECT rowid, {expr_concat} AS concat_val FROM {nom_table}")
        lignes = cur.fetchall()

        nb_maj = 0
        for rowid, concat_val in lignes:
            if concat_val is None:
                concat_val = ""
            cle_sha = hashlib.sha256(concat_val.encode("utf-8")).hexdigest()
            cur.execute(
                f"UPDATE {nom_table} SET cle = ? WHERE rowid = ?", (cle_sha, rowid))
            nb_maj += 1

        conn.commit()
        print(f"✅ {nb_maj} clé(s) mise(s) à jour dans la table '{nom_table}'.")
    except Exception as e:
        print(
            f"❌ Échec de la mise à jour des clés SHA256 dans '{nom_table}': {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def maj_groupe_avec_lexique_cles(nom_table):
    """
    Met à jour la colonne 'groupe' de nom_table à partir de t_lexique_cles.
    La colonne 'groupe' est créée si elle n'existe pas.
    Les tables sont liées par la colonne 'cle'.
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

        # Vérifie la colonne 'groupe' et la crée si nécessaire
        cur.execute(f"PRAGMA table_info({nom_table})")
        colonnes_existantes = [row[1] for row in cur.fetchall()]
        if "groupe" not in colonnes_existantes:
            print("➕ Création de la colonne 'groupe'...")
            cur.execute(f'ALTER TABLE {nom_table} ADD COLUMN groupe TEXT')

        # Mise à jour via sous-requête
    cur.execute(f"""
        UPDATE {nom_table}
        SET groupe = (
            SELECT t_lc.groupe
            FROM t_lexique_cles t_lc
            -- Référence la colonne 'cle' de la ligne de la table en cours de MAJ
            WHERE t_lc.cle = {nom_table}.cle 
            )
            -- S'assure de n'exécuter la MAJ que si une correspondance existe
            WHERE EXISTS (
                SELECT 1 
                FROM t_lexique_cles t_lc_check 
                WHERE t_lc_check.cle = {nom_table}.cle
            )
        """)

    conn.commit()
    conn.close()
    print(f"🔄 Colonne 'groupe' mise à jour depuis t_lexique_cles.")


def mettre_a_niveau_t_base_data():
    """Il s'agit de creer une colonne exercice - supprimer les colonnes debut_periode et fin_periode - 
    creer et valoriser colonne clé - creer et valoriser colonne groupe - ajouter les colonnes bat_tit_yp, rub_tit_yp, typ_tit_yp
    """
    conn = sqlite3.connect(vc.REP_BDD)
    cursor = conn.cursor()

    # 1) Creer colonne exercice
    # Vérifie la présence de la colonne
    cursor.execute("PRAGMA table_info(t_base_data)")
    colonnes = [row[1] for row in cursor.fetchall()]

    if "exercice" not in colonnes:
        print("➕ Ajout de la colonne 'exercice'...")
        cursor.execute("ALTER TABLE t_base_data ADD COLUMN exercice TEXT(4)")
        conn.commit()
    else:
        print("⚠️ Colonne 'exercice' existe déjà, aucune modification effectuée.")
        sql = "UPDATE t_base_data SET exercice = strftime('%Y', debut_periode);"
        cursor.execute(sql)
        conn.commit()
    conn.close()
    print(f"✅ t_base_data: colonne exercice créée et valorisée.")

    # 2) Suppression colonnes debut_periode et fin_periode
    # supprimer_colonnes("t_base_data", ["debut_periode", "fin_periode"])

    # 3) Creer et valoriser colonne cle
    u1.creer_colonnes("t_base_data", {"cle": "TEXT"})
    u1
    maj_cle_sha256("t_base_data", vc.composantes_cle)

    # 4) Créer et valoriser colonne groupe
    maj_groupe_avec_lexique_cles("t_base_data")


def verifier_tables_existent(liste_tables):
    """
    Vérifie la présence de toutes les tables de liste_tables dans la base SQLite.
    Retourne un dictionnaire {nom_table: True/False}.
    """
    conn = sqlite3.connect(vc.REP_BDD)
    cursor = conn.cursor()

    resultat = {}
    for table in liste_tables:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    existe = cursor.fetchone() is not None
    resultat[table] = existe
    print(resultat)
    conn.close()
    manquantes = {table for table, res in resultat.items() if not res}
    if manquantes:
        print("Tables manquantes: ", f"\033[91m{manquantes}\033[0m")
    else:
        print("\033[92mAucune table manquante\033[0m")
    return resultat


def modifier_types_colonnes(nom_table):
    """
    Met à jour le type des colonnes de nom_table selon lexique_colonnes_types.
    Les colonnes non mentionnées dans le dictionnaire restent inchangées.
    """

    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()

    # Récupération du schéma actuel
    cur.execute(f"PRAGMA table_info({nom_table})")
    colonnes_info = cur.fetchall()
    if not colonnes_info:
        raise ValueError(f"La table {nom_table} n'existe pas.")

    # Nom et type actuel des colonnes
    colonnes_existantes = {col[1]: col[2] for col in colonnes_info}

    # Construction du nouveau schéma
    nouveau_schema = []
    for nom_col, type_col in colonnes_existantes.items():
        nouveau_type = vc.lexique_colonnes_types.get(nom_col, type_col)
        nouveau_schema.append(f'"{nom_col}" {nouveau_type}')

    colonnes_ordre = list(colonnes_existantes.keys())
    colonnes_jointes = ", ".join(colonnes_ordre)
    nouveau_schema_sql = ", ".join(nouveau_schema)

    # Création d'une table temporaire
    cur.execute(f'CREATE TABLE "{nom_table}_tmp" ({nouveau_schema_sql})')

    # Copie des données
    cur.execute(
        f'INSERT INTO "{nom_table}_tmp" ({colonnes_jointes}) SELECT {colonnes_jointes} FROM "{nom_table}"')

    # Suppression et renommage
    cur.execute(f'DROP TABLE "{nom_table}"')
    cur.execute(f'ALTER TABLE "{nom_table}_tmp" RENAME TO "{nom_table}"')

    conn.commit()
    conn.close()


def renommer_table(nom_old, nom_new):
    """
    Renomme une table SQLite de nom_old vers nom_new.
    Crée une erreur si la table d'origine n'existe pas ou si la nouvelle existe déjà.
    """
    conn = sqlite3.connect(vc.REP_BDD)
    cursor = conn.cursor()

    # Vérifie que la table d’origine existe
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nom_old,))
    if not cursor.fetchone():
        print(f"La table '{nom_old}' n'existe pas dans la base.")
        conn.close()
        return
    # Vérifie qu’il n’existe pas déjà une table avec le nouveau nom
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nom_new,))
    if cursor.fetchone():
        print(f"Une table '{nom_new}' existe déjà.")
        conn.close()
        return
    # Renommage
    cursor.execute(f"ALTER TABLE {nom_old} RENAME TO {nom_new};")
    conn.commit()
    conn.close()


def verifier_integrite_bdd():
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()
    cur.execute("PRAGMA integrity_check;")
    resultat = cur.fetchone()[0]
    conn.close()
    if resultat == "ok":
        print("Base saine.")
    else:
        print("Base corrompue :", resultat)


def generer_modeles(fichier_sortie):
    """
    Introspecte la base et génère un module Python contenant
    les classes SQLAlchemy correspondant aux tables existantes.
    """
    metadata = MetaData()
    metadata.reflect(bind=vc.engine)

    lignes = [
        "from sqlalchemy import Column, Integer, Text, Float, Boolean, Date, DateTime, Numeric",
        "from sqlalchemy.ext.declarative import declarative_base",
        "",
        "Base = declarative_base()",
        "",
    ]

    for nom_table, table in metadata.tables.items():
        class_name = "".join(part.capitalize()
                             for part in nom_table.split("_"))
        lignes.append(f"class {class_name}(Base):")
        lignes.append(f"    __tablename__ = '{nom_table}'")
        for colonne in table.columns:
            type_col = str(colonne.type)
            nullable = "" if colonne.nullable else ", nullable=False"
            primary_key = ", primary_key=True" if colonne.primary_key else ""
            lignes.append(
                f"    {colonne.name} = Column({type_col}{primary_key}{nullable})"
            )
        lignes.append("")  # ligne vide entre classes

    with open(fichier_sortie, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes))

    print(f"✅ Modèles générés dans {fichier_sortie}")


def numeroter_doublons_par_cle():
    """
    S'adresse à la table t_base_data
       Numérote les lignes de t_base_data par 'cle'.
    - Si plusieurs lignes ont la même cle : 1, 2, 3, ...
    - Si une seule ligne a cette cle : 1
    """
    conn = sqlite3.connect(vc.REP_BDD)
    conn.execute("UPDATE t_base_data SET rang_doublon = '';")

    # 1. Réinitialiser la colonne
    conn.execute("UPDATE t_base_data SET rang_doublon = 1;")

    # 2. Mettre à jour les doublons
    conn.execute("""
        WITH cles_doublons AS (
            SELECT cle
            FROM t_base_data
            GROUP BY cle
            HAVING COUNT(*) > 1
        ),
        numerotes AS (
            SELECT
                rowid AS rid,
                ROW_NUMBER() OVER (PARTITION BY cle ORDER BY rowid) AS rn
            FROM t_base_data
            WHERE cle IN (SELECT cle FROM cles_doublons)
        )
        UPDATE t_base_data
        SET rang_doublon = (
            SELECT rn FROM numerotes n WHERE n.rid = t_base_data.rowid
        )
        WHERE cle IN (SELECT cle FROM cles_doublons);
    """)

    conn.commit()
    conn.close()


def ajouter_calculer_colonne_exercice_tampon_data():
    conn = sqlite3.connect(vc.REP_BDD)
    conn.execute("""
    ALTER TABLE tampon_data
    ADD COLUMN exercice TEXT(4);
""")
    conn.execute("""
    UPDATE tampon_data
    SET exercice = SUBSTR(CAST(debut_periode AS TEXT), 1, 4)
    WHERE debut_periode IS NOT NULL
""")
    conn.commit()
    conn.close()


def ajouter_colonne_batrub():
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()
    try:
        # ajoute la colonne si elle n'existe pas déjà
        cur.execute("PRAGMA table_info(t_base_data)")
        colonnes = [row[1] for row in cur.fetchall()]
        if "batrub" not in colonnes:
            cur.execute("ALTER TABLE t_base_data ADD COLUMN batrub TEXT")

        # met à jour les valeurs
        cur.execute("""
            UPDATE t_base_data
            SET batrub = COALESCE(bat, '') || '-' || COALESCE(rub, '')
        """)
        conn.commit()
        print("✅ Colonne 'batrub' ajoutée à t_base_data et peuplée avec succès.")
    except Exception as e:
        print("⚠️ Erreur pendant l'opération :", e)
    finally:
        conn.close()


def correspondances():
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()
    sql = """SELECT COUNT(*) 
        FROM t_base_data tbd 
        WHERE EXISTS (
            SELECT 1 
            FROM t_lexique_cles tlc 
            WHERE tlc.cle = tbd.cle
        );"""
    cur.execute(sql)
    print(cur.fetchone()[0])
    conn.close()


def nettoyer_table(nom_table):
    conn = sqlite3.connect(vc.REP_BDD)
    cur = conn.cursor()

    # Récupérer les colonnes de type TEXT
    cur.execute(f"PRAGMA table_info({nom_table})")
    colonnes_text = [row[1]
                     for row in cur.fetchall() if row[2].upper() == "TEXT"]

    if not colonnes_text:
        print(f"⚠️ Aucune colonne TEXT trouvée dans {nom_table}.")
        conn.close()
        return

    nb_total = 0
    for col in colonnes_text:
        cur.execute(f"SELECT id, {col} FROM {nom_table}")
        lignes = cur.fetchall()
        for id_, val in lignes:
            if isinstance(val, str):
                # 1️⃣ Remplacer explicitement les espaces insécables (CHAR(160) ou \u00A0) par un espace normal
                val = val.replace('\u00A0', ' ').replace(chr(160), ' ')

                # 2️⃣ Supprimer les caractères invisibles et espaces multiples
                val_nettoyee = re.sub(r"[\s\u200B]+", " ", val.strip())

                if val_nettoyee != val:
                    cur.execute(
                        f"UPDATE {nom_table} SET {col}=? WHERE id=?",
                        (val_nettoyee, id_)
                    )
                    nb_total += 1

    conn.commit()
    conn.close()
    print(f"✅ {nb_total} valeurs nettoyées dans {nom_table}.")


# Exemple d'utilisation
if __name__ == "__main__":
    # numeroter_doublons_par_cle()
    # maj_cle_sha256("t_base_data", vc.composantes_cle)
    # maj_groupe_avec_lexique_cles("t_base_data")
    # ajouter_colonne_batrub()
    correspondances()
