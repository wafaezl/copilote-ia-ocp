"""
Test complet du serveur MCP : les 3 agents (simules) enchainent
load_dataset -> profile_dataset -> compute_kpis, via appeler_outil()
au lieu d'appeler les fonctions directement.

On teste aussi un cas de refus de permission, pour verifier
que la securite fonctionne.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.server import appeler_outil, afficher_journal

# --- Agent Ingestion : charge le fichier ---
resultat_chargement = appeler_outil(
    nom_agent="agent_ingestion",
    nom_outil="load_dataset",
    chemin_fichier="data/raw/exemple_production.csv",
)

if not resultat_chargement["success"]:
    print("Echec :", resultat_chargement["erreur"])
    exit()

print(f"[Agent Ingestion] OK - {resultat_chargement['nb_lignes']} lignes\n")
df = resultat_chargement["dataframe"]

# --- Agent Preparation : profile les donnees ---
resultat_profil = appeler_outil(
    nom_agent="agent_preparation",
    nom_outil="profile_dataset",
    dataframe=df,
)

if not resultat_profil["success"]:
    print("Echec :", resultat_profil["erreur"])
    exit()

print("[Agent Preparation] OK")
print(resultat_profil["resume_texte"], "\n")
profil = resultat_profil["profil"]

# --- Agent KPI : calcule les indicateurs ---
resultat_kpis = appeler_outil(
    nom_agent="agent_kpi",
    nom_outil="compute_kpis",
    dataframe=df,
    profil=profil,
)

if not resultat_kpis["success"]:
    print("Echec :", resultat_kpis["erreur"])
    exit()

print("[Agent KPI] OK")
for nom_kpi, valeurs in resultat_kpis["kpis"].items():
    print(f"- {nom_kpi} : {valeurs}")

# --- Test de securite : un agent qui tente un acces NON autorise ---
print("\n--- Test de refus de permission ---")
resultat_refuse = appeler_outil(
    nom_agent="agent_ingestion",
    nom_outil="compute_kpis",   # agent_ingestion n'a PAS le droit de faire ca
    dataframe=df,
    profil=profil,
)
print("Resultat :", resultat_refuse)

# --- Affichage du journal complet des appels ---
print("\n--- Journal des appels ---")
afficher_journal()