"""
Test de l'Agent Orchestrateur : lance le pipeline complet en UN SEUL
appel, au lieu d'enchainer manuellement les 6 agents comme avant.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.orchestrator_agent import executer_pipeline_complet

resultat = executer_pipeline_complet(
    chemin_fichier="data/raw/exemple_production.csv",
    validation_humaine=True,
)

print("\n=== ETAT FINAL DU PIPELINE ===")
for nom_etape, infos in resultat["etapes"].items():
    print(f"{nom_etape} : {infos}")

if resultat["success"]:
    print(f"\nRapport final disponible : {resultat['chemin_rapport_final']}")