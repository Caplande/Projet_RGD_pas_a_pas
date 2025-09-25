import pandas as pd
import variables_communes as vc
from src.utils import u_sql as u_sql

print("Module u_gen chargé avec succès.")


def traiter_classeur(classeur, l_sauf=[None]):
    """
    Traite un classeur en effectuant des opérations spécifiques.

    Args:
        classeur (classeur): Le classeur à traiter.
    """
    # Lister les feuilles
    liste_feuilles = pd.ExcelFile(classeur).sheet_names
    liste_feuilles = diff_entre_deux_listes(liste_feuilles, l_sauf)

    try:
        for nom_feuille in liste_feuilles:
            # Effectuer des opérations spécifiques sur chaque feuille
            convertir_feuilles_en_table(classeur, nom_feuille)
    except Exception as e:
        pass


def convertir_feuilles_en_table(classeur, nom_feuille):
    """
    Convertit une feuille en table dans la base de données.
    """
    try:  # nom_feuille est-elle dans les clefs du dictionnaire vc.d_feuille_table ?
        # Charger une feuille spécifique depuis Excel
        df = pd.read_excel(classeur, sheet_name=nom_feuille)

        # Transformer la feuille en table SQL
        try:
            nom_table = vc.d_feuille_table[nom_feuille]
            df.to_sql(nom_table, con=vc.engine, index=True,
                      index_label='id', if_exists="replace")
        except:
            pass
    except Exception as e:
        pass


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
