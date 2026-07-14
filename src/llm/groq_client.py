"""
Connexion au LLM via l'API Groq.
Ce module centralise la création du client, pour que tous les futurs
agents utilisent la même configuration sans dupliquer le code.
"""

import os
from dotenv import load_dotenv
from groq import Groq

# Charge les variables du fichier .env (dont GROQ_API_KEY)
load_dotenv()

def get_llm_client():
    """Retourne un client Groq prêt à l'emploi."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY introuvable. Vérifie que ton fichier .env "
            "contient bien la ligne : GROQ_API_KEY=ta_cle_ici"
        )
    return Groq(api_key=api_key)

def get_default_model():
    """Nom du modèle utilisé par défaut."""
    return "llama-3.1-8b-instant"