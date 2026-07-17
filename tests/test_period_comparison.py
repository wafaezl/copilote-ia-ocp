"""
Test de la comparaison de periodes, avec repli automatique
mois -> annee si necessaire.
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.profiler import profiler_dataset
from src.core.period_comparison import comparer_periodes

df = pd.read_csv("data/raw/exemple_production.csv")
profil = profiler_dataset(df)

resultat = comparer_periodes(df, profil)

if not resultat["success"]:
    print("Echec :", resultat["erreur"])
    exit()

# On recupere la granularite depuis le premier resultat (identique pour tous)
premiere_mesure = next(iter(resultat["comparaisons"].values()))
print(f"=== Comparaison de periodes (granularite : {premiere_mesure['granularite']}) ===\n")

for nom_col, infos in resultat["comparaisons"].items():
    signe = "+" if infos["tendance"] == "hausse" else ("-" if infos["tendance"] == "baisse" else "=")
    print(f"{nom_col} :")
    print(f"    {infos['periode_precedente']} -> {infos['periode_actuelle']}")
    print(f"    {infos['valeur_precedente']} -> {infos['valeur_actuelle']} "
          f"({signe}{infos['evolution_pct']}%) [{infos['tendance']}]\n")