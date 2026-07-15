"""
Test des 3 outils enchaines manuellement (sans encore le serveur MCP
ni les agents) : load_dataset -> profile_dataset -> compute_kpis.

Objectif : verifier que les 3 fonctions s'enchainent correctement
avant de les brancher au serveur MCP.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.tools import load_dataset, profile_dataset, compute_kpis

# --- 1. load_dataset ---
resultat_chargement = load_dataset("data/raw/exemple_production.csv")

if not resultat_chargement["success"]:
    print("Echec chargement :", resultat_chargement["erreur"])
    exit()

print(f"[load_dataset] OK - {resultat_chargement['nb_lignes']} lignes, "
      f"{resultat_chargement['nb_colonnes']} colonnes\n")

df = resultat_chargement["dataframe"]

# --- 2. profile_dataset ---
resultat_profil = profile_dataset(df)

if not resultat_profil["success"]:
    print("Echec profilage :", resultat_profil["erreur"])
    exit()

print("[profile_dataset] OK")
print(resultat_profil["resume_texte"], "\n")

profil = resultat_profil["profil"]

# --- 3. compute_kpis ---
resultat_kpis = compute_kpis(df, profil)

if not resultat_kpis["success"]:
    print("Echec calcul KPIs :", resultat_kpis["erreur"])
    exit()

print("[compute_kpis] OK")
for nom_kpi, valeurs in resultat_kpis["kpis"].items():
    print(f"- {nom_kpi} : total={valeurs['total']}, moyenne={valeurs['moyenne']}, "
          f"min={valeurs['min']}, max={valeurs['max']}")