import sys
import os
import pandas as pd
import re
from datetime import datetime
import variables_communes as vc
from src.utils import u_sql_1 as u_sql_1, u_sql_2 as u_sql_2
import tkinter as tk
from tkinter import messagebox

print("Module data chargé avec succès.")


def convertir_feuilles_en_table(classeur, nom_feuille):
    """
    Convertit une feuille en table dans la base de données.
    Toutes les feuilles du type F_* sont converties en tables du nom de t_*.
    Les feuilles data et parametres sont converties en tables tampon_data et tampon_parametres.
    """
    try:
        # Charger une feuille spécifique depuis Excel
        df = pd.read_excel(classeur, sheet_name=nom_feuille)

        # Transformer la feuille en table SQL
        try:
            nom_table = "tampon_" + nom_feuille.lower() if nom_feuille in [
                "data", "Parametres"] else "t_" + nom_feuille.lower()[2:]
            df.to_sql(nom_table, con=vc.engine, index=True,
                      index_label='id', if_exists="replace")
            return nom_table
        except Exception as e:
            print(
                "Erreur lors de la création de la table pour la feuille:", nom_feuille, e)
            raise
            return None
    except Exception as e:
        print("Erreur lors du chargement de la feuille:", nom_feuille, e)
        raise
        return None


def diff_entre_deux_listes(l1, moins_l2):
    return [x for x in l1 if x not in moins_l2]


def calculer_clef_ligne(ligne):
    import hashlib
    # Concaténer tous les champs de la ligne en une seule chaîne de caractères
    concat_str = ''.join(str(getattr(ligne, col))
                         for col in ligne.__table__.columns.keys())
    # Calculer le hachage SHA256 de la chaîne concaténée
    sha256_hash = hashlib.sha256(concat_str.encode()).hexdigest()
    return sha256_hash


def purifier_sql(sql: str) -> str:
    if sql is None:
        return None
    # 1. Supprimer les caractères de contrôle (ASCII 0-31, 127)
    sql = re.sub(r'[\x00-\x1F\x7F]', ' ', sql)
    # 2. Supprimer ou normaliser les retours ligne/tabs
    # compresse tous les blancs (\n, \t, etc.) en un seul espace
    sql = re.sub(r'\s+', ' ', sql)
    # 3. Supprimer espaces inutiles en début/fin
    return sql.strip()


def fermer_projet(root=None):
    """
    Ferme proprement l'application Tkinter.
    """
    if messagebox.askokcancel("Quitter", "Fermer le projet ?"):
        try:
            if root is not None:
                root.quit()
                root.destroy()
            # Force la terminaison du processus
            os._exit(0)
        except Exception as e:
            print(f"Erreur à la fermeture : {e}")
            os._exit(1)


def traiter_classeur(classeur, l_sauf=None):
    """
    Traite un classeur en effectuant des opérations spécifiques.

    Args:
        classeur (classeur): Le classeur à traiter.
    """
    l_sauf = l_sauf if l_sauf is not None else []
    # Lister les feuilles
    l_feuilles = pd.ExcelFile(classeur).sheet_names
    l_feuilles = [feuille for feuille in l_feuilles if (feuille.startswith(
        "F_") or feuille in ["data"]) and (feuille not in l_sauf)]
    l_noms_tables = []
    try:
        for nom_feuille in l_feuilles:
            # Effectuer des opérations spécifiques sur chaque feuille
            l_noms_tables.append(
                convertir_feuilles_en_table(classeur, nom_feuille))
        return l_noms_tables
    except Exception as e:
        return None
