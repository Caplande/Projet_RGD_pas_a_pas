from src.utils import initialiser_bdd, u_sql_1
from src.utils import actualiser_donnees as ad  # ,essai
import variables_communes as vc

# Initialiser la base de données
# Pour initialiser la base de données, enlever la condition False en tête du module initialiser_bdd.py.
# Vérifier au préalable car j'ai fait de nombreuses modifications.

# Actualiser les données
# ad.actualiser_donnees("F_agregation")
# u_sql.introspecter_table_non_mappee("tampon_data")

ad.peupler_donnees_courantes_bdd()

# print(u_sql.attach_all_tables())

# print(u_sql.extraire_classe_depuis_nom_table("tampon_parametres"))
print(vc.Base.metadata.tables)
# u_sql.attach_table_to_base_with_pk("tampon_parametres")
# print(u_sql.extraire_classe_depuis_nom_table("tampon_parametres"))
