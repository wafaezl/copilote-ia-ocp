"""
Test du pipeline complet avec les 3 VRAIS agents LLM enchaines :
Agent Ingestion -> Agent Preparation -> Agent KPI.

Chaque agent est reellement pilote par Llama (pas d'appel direct
aux outils comme dans les tests precedents).
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.ingestion_agent import executer_agent_ingestion
from src.agents.preparation_agent import executer_agent_preparation
from src.agents.kpi_agent import executer_agent_kpi

print("=" * 60)
print("ETAPE 1 : Agent Ingestion")
print("=" * 60)

mission_ingestion = (
    "Charge le fichier data/raw/exemple_production.csv "
    "et dis-moi combien de lignes et colonnes il contient."
)
resultat_ingestion = executer_agent_ingestion(mission_ingestion)

print(resultat_ingestion["texte"])

if resultat_ingestion["dataframe"] is None:
    print("Echec : aucun DataFrame recupere. Arret du pipeline.")
    exit()

df = resultat_ingestion["dataframe"]

print("\n" + "=" * 60)
print("ETAPE 2 : Agent Preparation")
print("=" * 60)

mission_preparation = "Analyse la structure de ce dataset et dis-moi le role de chaque colonne."
resultat_preparation = executer_agent_preparation(mission_preparation, dataframe=df)

print(resultat_preparation["texte"])

if resultat_preparation["profil"] is None:
    print("Echec : aucun profil recupere. Arret du pipeline.")
    exit()

profil = resultat_preparation["profil"]

print("\n" + "=" * 60)
print("ETAPE 3 : Agent KPI")
print("=" * 60)

mission_kpi = (
    "Calcule les indicateurs cles de ce dataset, signale s'il y a des valeurs "
    "aberrantes a surveiller, et indique l'evolution par rapport a la periode precedente."
)
reponse_kpi = executer_agent_kpi(mission_kpi, dataframe=df, profil=profil)

print(reponse_kpi)

print("\n" + "=" * 60)
print("PIPELINE COMPLET TERMINE - 3 agents LLM enchaines avec succes")
print("=" * 60)