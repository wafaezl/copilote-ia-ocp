"""
Test de l'Agent KPI. On prepare d'abord le DataFrame et le profil
(comme le feraient les agents precedents), puis on laisse le LLM
decider quels outils utiliser.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.server import appeler_outil
from src.agents.kpi_agent import executer_agent_kpi

# --- Etapes prealables : chargement + profilage ---
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

# --- Lancement de l'Agent KPI ---
mission = (
    "Calcule les indicateurs cles de ce dataset et signale s'il y a "
    "des valeurs aberrantes a surveiller."
)

reponse = executer_agent_kpi(mission, dataframe=df, profil=profil)

print("\n=== Reponse finale de l'Agent KPI ===")
print(reponse)