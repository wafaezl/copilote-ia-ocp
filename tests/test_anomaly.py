"""
Test isole de la detection d'anomalies (IQR), avant de l'integrer
au serveur MCP.
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.profiler import profiler_dataset
from src.core.anomaly import detecter_anomalies

# Chargement direct pour ce test isole
df = pd.read_csv("data/raw/exemple_production.csv")
profil = profiler_dataset(df)

resultat = detecter_anomalies(df, profil)

if not resultat["success"]:
    print("Echec :", resultat["erreur"])
    exit()

print("=== Anomalies detectees (methode IQR) ===\n")
for nom_col, infos in resultat["anomalies"].items():
    print(f"- {nom_col} :")
    print(f"    Anomalies detectees : {infos['nb_anomalies']} ({infos['pct_anomalies']}%)")
    print(f"    Limites normales : [{infos['borne_basse']}, {infos['borne_haute']}]")
    print(f"    Exemples de valeurs aberrantes : {infos['exemples']}\n")