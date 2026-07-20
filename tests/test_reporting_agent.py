"""
Test de l'Agent Redaction, avec verification anti-hallucination
et validation humaine.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.server import appeler_outil
from src.agents.reporting_agent import executer_agent_reporting

# --- Preparer les donnees necessaires ---
df = appeler_outil(nom_agent="agent_ingestion", nom_outil="load_dataset",
                    chemin_fichier="data/raw/exemple_production.csv")["dataframe"]

profil = appeler_outil(nom_agent="agent_preparation", nom_outil="profile_dataset",
                        dataframe=df)["profil"]

kpis = appeler_outil(nom_agent="agent_kpi", nom_outil="compute_kpis",
                      dataframe=df, profil=profil)["kpis"]

anomalies = appeler_outil(nom_agent="agent_kpi", nom_outil="detect_anomalies",
                           dataframe=df, profil=profil)["anomalies"]

comparaisons = appeler_outil(nom_agent="agent_kpi", nom_outil="compare_periods",
                              dataframe=df, profil=profil)["comparaisons"]

# --- Lancer l'Agent Redaction ---
resultat = executer_agent_reporting(kpis, anomalies, comparaisons)

print("\n=== Resultat final ===")
print(f"Valide par un humain : {resultat['valide_par_humain']}")
print(f"\nTexte final :\n{resultat['texte_final']}")