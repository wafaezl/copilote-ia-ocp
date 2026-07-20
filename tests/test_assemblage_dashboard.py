"""
Test de l'assemblage : execute le pipeline complet jusqu'au Tableau de bord,
puis assemble tous les graphiques en une seule page.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.server import appeler_outil
from src.agents.dashboard_agent import executer_agent_dashboard
from src.dashboard.assembleur import assembler_dashboard

# --- Preparer toutes les donnees necessaires ---
df = appeler_outil(nom_agent="agent_ingestion", nom_outil="load_dataset",
                    chemin_fichier="data/raw/exemple_production.csv")["dataframe"]

profil = appeler_outil(nom_agent="agent_preparation", nom_outil="profile_dataset",
                        dataframe=df)["profil"]

kpis = appeler_outil(nom_agent="agent_kpi", nom_outil="compute_kpis",
                      dataframe=df, profil=profil)["kpis"]

comparaisons = appeler_outil(nom_agent="agent_kpi", nom_outil="compare_periods",
                              dataframe=df, profil=profil)["comparaisons"]

# --- Lancer l'Agent Dashboard ---
mission = (
    f"Genere les graphiques pertinents. Les KPIs disponibles pour "
    f"generate_waterfall_chart sont exactement : {list(kpis.keys())}."
)
resultat = executer_agent_dashboard(mission, dataframe=df, profil=profil,
                                     kpis=kpis, comparaisons=comparaisons)

print(f"Graphiques generes : {list(resultat['graphiques'].keys())}\n")

# --- Assembler en un seul dashboard ---
dashboard_final = assembler_dashboard(
    resultat["graphiques"],
    titre="Copilote IA - Dashboard OCP (donnees de test)"
)

os.makedirs("runs", exist_ok=True)
with open("runs/dashboard.html", "w", encoding="utf-8") as f:
    f.write(dashboard_final)

print("Dashboard complet sauvegarde dans runs/dashboard.html")