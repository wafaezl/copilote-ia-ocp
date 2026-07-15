"""
Test de l'outil detect_anomalies, integre au serveur MCP.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.server import appeler_outil, afficher_journal

# --- Chargement + profilage (comme avant) ---
resultat_chargement = appeler_outil(
    nom_agent="agent_ingestion",
    nom_outil="load_dataset",
    chemin_fichier="data/raw/exemple_production.csv",
)
df = resultat_chargement["dataframe"]

resultat_profil = appeler_outil(
    nom_agent="agent_preparation",
    nom_outil="profile_dataset",
    dataframe=df,
)
profil = resultat_profil["profil"]

# --- Nouveau : detection d'anomalies via le serveur MCP ---
resultat_anomalies = appeler_outil(
    nom_agent="agent_kpi",
    nom_outil="detect_anomalies",
    dataframe=df,
    profil=profil,
)

if not resultat_anomalies["success"]:
    print("Echec :", resultat_anomalies["erreur"])
    exit()

print("=== Anomalies detectees via MCP ===\n")
for nom_col, infos in resultat_anomalies["anomalies"].items():
    print(f"- {nom_col} : {infos['nb_anomalies']} anomalies ({infos['pct_anomalies']}%)")

# --- Verification de securite : un agent NON autorise ---
print("\n--- Test de refus ---")
resultat_refuse = appeler_outil(
    nom_agent="agent_ingestion",   # n'a pas le droit
    nom_outil="detect_anomalies",
    dataframe=df,
    profil=profil,
)
print("Resultat :", resultat_refuse)

print("\n--- Journal ---")
afficher_journal()