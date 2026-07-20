import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.server import appeler_outil
from src.agents.dashboard_agent import executer_agent_dashboard

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
    f"Genere les graphiques pertinents pour visualiser ces resultats. "
    f"Les KPIs disponibles pour generate_waterfall_chart sont exactement : {list(kpis.keys())}. "
    f"N'utilise JAMAIS d'autres noms que ceux-ci."
)
resultat = executer_agent_dashboard(mission, dataframe=df, profil=profil,
                                     kpis=kpis, comparaisons=comparaisons)

print(resultat["texte"])
print(f"\nGraphiques generes : {list(resultat['graphiques'].keys())}")

# Sauvegarde pour verification visuelle
os.makedirs("runs", exist_ok=True)
for nom, html in resultat["graphiques"].items():
    with open(f"runs/{nom}.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  -> runs/{nom}.html")