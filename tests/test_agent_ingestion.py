"""
Premier agent de test (Etape A, sans MCP) :
1. Charge un fichier CSV
2. Le profile automatiquement (role de chaque colonne)
3. Envoie ce profil a Groq pour generer un resume en langage naturel
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.llm.groq_client import get_llm_client, get_default_model
from src.core.profiler import profiler_dataset, resumer_profil

# --- 1. Chargement du fichier CSV ---
CHEMIN_FICHIER = "data/raw/exemple_production.csv"

df = pd.read_csv(CHEMIN_FICHIER)
print(f"Fichier charge : {len(df)} lignes, {len(df.columns)} colonnes.\n")

# --- 2. Profilage automatique ---
profil = profiler_dataset(df)
resume_texte = resumer_profil(profil)

print("=== Profil detecte ===")
print(resume_texte, "\n")

# --- 3. Resume en langage naturel via Groq ---
client = get_llm_client()

reponse = client.chat.completions.create(
    model=get_default_model(),
    messages=[
        {
            "role": "system",
            "content": "Tu es un assistant d'analyse de donnees. Reponds en francais, en 3 phrases maximum.",
        },
        {
            "role": "user",
            "content": (
                f"Voici le profil automatique d'un jeu de donnees :\n{resume_texte}\n\n"
                "Explique en langage simple ce que semble contenir ce jeu de donnees, "
                "et quel type d'analyse serait pertinent."
            ),
        },
    ],
)

print("=== Commentaire genere par le LLM ===")
print(reponse.choices[0].message.content)