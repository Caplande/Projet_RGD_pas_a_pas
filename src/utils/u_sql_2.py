import sys
import sqlite3
import hashlib
from sqlalchemy import MetaData, delete, inspect, Table, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.ext.automap import automap_base
import pandas as pd
import variables_communes as vc
from src.utils import u_gen as u_gen

print("Module u_sql_2 chargé avec succès.")

sys.stdout.reconfigure(encoding='utf-8')


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
    conn = sqlite3.connect(vc.rep_bdd)
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

    conn = sqlite3.connect(vc.rep_bdd)
    conn.execute(sql)

    # Suppression de la table source
    conn.execute(f"DROP TABLE IF EXISTS {table_src};")
    conn.commit()


def normer_noms_colonnes():
    """
    Norme les noms des colonnes de la table data dans la table "tampon_data"
    """

    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()

    # Récupérer la structure de la table tampon_data
    cur.execute(f"PRAGMA table_info(tampon_data);")
    columns_info = cur.fetchall()

    # Colonnes existantes : [(nom, type)]
    cols = [(c[1]) for c in columns_info]

    # Créer une nouvelle liste de colonnes normalisées
    new_cols = []
    for name in cols:
        new_cols.append(vc.mapping_tampon_t_data[name])

    for old, new in zip(cols, new_cols):
        # les anciens noms non conformes doivent être entourés de guillemets doubles
        cur.execute(f'ALTER TABLE tampon_data RENAME COLUMN "{old}" TO {new};')

    conn.commit()
    conn.close()

    print(f"✅ Noms des colonnes normalisés dans data'.")


def normer_types_colonnes(dry_run=False):
    """
    Normalise les types de colonnes de toutes les tables SQLite selon le lexique fourni.
    Si dry_run=True, affiche les modifications sans toucher à la base.
    """
    lexique = vc.lexique_colonnes_types

    conn = sqlite3.connect(vc.rep_bdd)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"🔍 {len(tables)} tables détectées dans la base.")

    for table in tables:
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


def adjoindre_pk():
    """
    Pour chaque table de l_tables_source :
      - ajoute une colonne 'id' si elle n'existe pas
      - crée une clé primaire sur 'id' si la table n'en a pas déjà
      - conserve les types et contraintes des autres colonnes
    """
    conn = sqlite3.connect(vc.rep_bdd)
    cursor = conn.cursor()

    for table in vc.l_tables_source:
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


def remplacer_nulls_toutes_tables():
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()

    # Récupérer la liste des tables (hors tables système SQLite)
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cur.fetchall()]

    for table in tables:
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


def creer_table_lexique_cles():
    # Eliminer toutes les valeurs Null de toutes les table de la bdd
    remplacer_nulls_toutes_tables()
    # Formater les colonnes bat,rub,typ de t_roc_modifiee
    formater_bat_rub_typ(["t_roc_modifiee"])
    if not table_existe("t_lexique_cles"):
        # Création de la table t_lexique_cles
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS t_lexique_cles (
            cle TEXT PRIMARY KEY,
            groupe TEXT
        )
        """)

        # Récupération des données sources
        cols = ", ".join(vc.composantes_cle + ['groupe'])
        cursor.execute(f"SELECT {cols} FROM t_roc_modifiee")
        rows = cursor.fetchall()

        # Insertion dans t_lexique_cles
        for row in rows:
            *vals, groupe = row
            # Concaténation des valeurs composant la clé
            concat = ''.join(str(v) if v is not None else '' for v in vals)
            cle = hashlib.sha256(concat.encode('utf-8')).hexdigest()

            cursor.execute("""
            INSERT OR IGNORE INTO t_lexique_cles (cle, groupe)
            VALUES (?, ?)
            """, (cle, groupe))

        conn.commit()
        conn.close()
        print("✅ Table 't_lexique_cles' créée avec succès.")
    else:
        print("✅ Table 't_lexique_cles' a été conservée")


def formater_bat_rub_typ(l_toutes_tables):
    conn = sqlite3.connect(vc.rep_bdd)
    cursor = conn.cursor()
    for table in l_toutes_tables:
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
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?;",
        (nom_table,)
    )
    return cur.fetchone() is not None


if __name__ == "__main__":
    conn = sqlite3.connect(vc.rep_bdd)
    cursor = conn.cursor()
    nom_table = "tampon_data"
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (nom_table,))
    table_existe = cursor.fetchone()

    if not table_existe:
        print(
            f"⚠️  La table '{nom_table}' n'existe pas dans la base {vc.rep_bdd}")
        conn.close()

    normer_noms_colonnes("nom_table")
