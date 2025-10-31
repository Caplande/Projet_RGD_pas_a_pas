import sqlite3
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style, init
import src.core.variables_metier_path as vc


def actualiser_controle():
    init(autoreset=True)

    conn = sqlite3.connect(vc.REP_BDD)

    df_e = pd.read_sql_query(
        "SELECT indicateur, valeur FROM t_parametres", conn)
    # print(df_e)
    df_b = pd.read_sql_query()
    rows = []
    for _, row in df.iterrows():
        if str(row["Excel"]) == str(row["BDD"]):
            color = Fore.GREEN
        else:
            color = Fore.RED

        rows.append([
            color + str(row["parametre"]) + Style.RESET_ALL,
            color + str(row["Excel"]) + Style.RESET_ALL,
            color + str(row["BDD"]) + Style.RESET_ALL,
        ])

    print(tabulate(rows, headers=[
          "Paramètre", "Excel", "BDD"], tablefmt="fancy_grid", showindex=False))


if __name__ == "__main__":
    actualiser_controle()
