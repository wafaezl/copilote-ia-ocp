"""
Test du premier vrai agent LLM : l'Agent Ingestion.
Cette fois, c'est le LLM qui decide d'appeler load_dataset,
pas nous.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.ingestion_agent import executer_agent_ingestion

mission = (
    "Charge le fichier data/raw/exemple_production.csv "
    "et dis-moi combien de lignes et colonnes il contient."
)

reponse = executer_agent_ingestion(mission)

print("\n=== Reponse finale de l'Agent Ingestion ===")
print(reponse)