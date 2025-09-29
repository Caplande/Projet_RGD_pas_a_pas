from src.utils import initialiser_bdd
from src.utils import actualiser_donnees as ad, u_sql  # ,essai
import variables_communes as vc

# Initialiser la base de données
# Pour initialiser la base de données, enlever la condition False en tête du module initialiser_bdd.py.
# Vérifier au préalable car j'ai fait de nombreuses modifications.

# Actualiser les données
# ad.actualiser_donnees("F_agregation")
# u_sql.introspecter_table_non_mappee("tampon_data")

# ad.mettre_en_forme_bdd()

print(u_sql.attach_all_tables())

# print(u_sql.extraire_classe_depuis_nom_table("tampon_parametres"))
