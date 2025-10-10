from src.utils import u_sql_1, u_gen
from src.utils import reinitialiser_bdd as ad  # ,essai
import variables_communes as vc
from src.utils import reinitialiser_bdd as rb  # , menu as mn
from src.utils import actualiser_donnees as ad
import os

# Initialiser la base de données
rb.reinitialiser_bdd(rb.reinitialiser_bdd_executer)

# Actualiser données avec la plus récente importation de données B&D
# ad.actualiser_donnees()
