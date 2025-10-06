from archives import initialiser_bdd
from src.utils import u_sql_1
from src.utils import reinitialiser_bdd as ad  # ,essai
import variables_communes as vc
from src.utils import reinitialiser_bdd as rb

# Initialiser la base de données
rb.reinitialiser_bdd()


# u_sql_1.introspecter_table_non_mappee("tampon_data")

# ad.peupler_donnees_courantes_bdd()

# print(u_sql.attach_all_tables())

# print(u_sql.extraire_classe_depuis_nom_table("tampon_parametres"))
# u_sql.attach_table_to_base_with_pk("tampon_parametres")
# print(u_sql.extraire_classe_depuis_nom_table("tampon_parametres"))
