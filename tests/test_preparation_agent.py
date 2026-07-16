"""
Test de l'Agent Preparation. On simule d'abord l'etape precedente
(chargement du fichier) puisque cet agent a besoin d'un DataFrame deja pret.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.server import appeler_outil
from src.agents.preparation_agent import executer_agent_preparation

# --- Etape prealable : charger le fichier (comme le ferait l'Agent Ingestion) ---
resultat_chargement = appeler_outil(
    nom_agent="agent_ingestion",
    nom_outil="load_dataset",
    chemin_fichier="data/raw/exemple_production.csv",
)
df = resultat_chargement["dataframe"]

# --- Lancement de l'Agent Preparation ---
mission = "Analyse la structure de ce dataset et dis-moi le role de chaque colonne."

reponse = executer_agent_preparation(mission, dataframe=df)

print("\n=== Reponse finale de l'Agent Preparation ===")
print(reponse)