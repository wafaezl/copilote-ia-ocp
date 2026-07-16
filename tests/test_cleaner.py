"""
Test isole du nettoyage, avant integration complete au serveur MCP.
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.profiler import profiler_dataset
from src.core.cleaner import nettoyer_dataset

df = pd.read_csv("data/raw/exemple_production.csv")
profil = profiler_dataset(df)

resultat = nettoyer_dataset(df, profil)

if not resultat["success"]:
    print("Echec :", resultat["erreur"])
    exit()

print("=== Rapport de nettoyage ===")
print(f"Lignes avant : {resultat['rapport']['lignes_avant']}")
print(f"Lignes apres : {resultat['rapport']['lignes_apres']}")
print(f"Taux de conservation : {resultat['rapport']['taux_conservation']}%\n")

print("Operations effectuees :")
for operation in resultat["rapport"]["operations"]:
    print(f"- {operation}")

if not resultat["rapport"]["operations"]:
    print("(Aucune operation necessaire : donnees deja propres)")