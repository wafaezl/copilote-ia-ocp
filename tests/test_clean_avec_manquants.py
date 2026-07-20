import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.server import appeler_outil

resultat_chargement = appeler_outil(
    nom_agent="agent_ingestion", nom_outil="load_dataset",
    chemin_fichier="data/raw/test_nettoyage.csv",
)
df = resultat_chargement["dataframe"]

resultat_profil = appeler_outil(
    nom_agent="agent_preparation", nom_outil="profile_dataset", dataframe=df,
)
profil = resultat_profil["profil"]

resultat_nettoyage = appeler_outil(
    nom_agent="agent_preparation", nom_outil="clean_dataset",
    dataframe=df, profil=profil,
)

print("=== Rapport de nettoyage ===")
print(f"Lignes avant : {resultat_nettoyage['rapport']['lignes_avant']}")
print(f"Lignes apres : {resultat_nettoyage['rapport']['lignes_apres']}\n")
for op in resultat_nettoyage["rapport"]["operations"]:
    print(f"- {op}")