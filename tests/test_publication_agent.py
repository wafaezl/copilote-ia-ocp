"""
Test de bout en bout : Ingestion -> Preparation -> KPI -> Dashboard ->
Redaction -> Publication.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.server import appeler_outil
from src.agents.dashboard_agent import executer_agent_dashboard
from src.agents.reporting_agent import generer_commentaire
from src.core.validator import verifier_texte
from src.agents.publication_agent import executer_agent_publication

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

mission_dashboard = (
    f"Genere les graphiques pertinents. Les KPIs disponibles pour "
    f"generate_waterfall_chart sont exactement : {list(kpis.keys())}."
)
resultat_dashboard = executer_agent_dashboard(mission_dashboard, dataframe=df, profil=profil,
                                                kpis=kpis, comparaisons=comparaisons)

commentaire = generer_commentaire(kpis, anomalies, comparaisons)
verification = verifier_texte(commentaire, kpis=kpis, anomalies=anomalies, comparaisons=comparaisons)

print(f"Verdict verification : {verification['verdict']}")

resultat_publication = executer_agent_publication(
    dataframe=df,
    graphiques_html=resultat_dashboard["graphiques"],
    commentaire=commentaire,
    verification=verification,
    kpis=kpis,
)

print("\nPipeline complet termine.")