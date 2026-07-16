"""
Agent Preparation : deuxieme agent LLM du pipeline.

Difference avec l'Agent Ingestion : cet agent ne charge pas un fichier
depuis un chemin donne par le LLM. Il recoit un DataFrame DEJA CHARGE
(transmis par le code, pas par le LLM) et demande au LLM de decider
d'appeler profile_dataset dessus.

Pourquoi cette difference : un DataFrame ne peut pas etre "invente"
par le LLM sous forme de texte/JSON - c'est un objet Python complexe.
Le LLM decide donc juste QUAND appeler l'outil, mais les vraies donnees
sont injectees par le code au moment de l'execution.
"""

import json
import pandas as pd
from src.llm.groq_client import get_llm_client, get_default_model
from src.mcp_server.server import appeler_outil


NOM_AGENT = "agent_preparation"

SYSTEM_PROMPT = """Tu es l'Agent Preparation d'un systeme d'analyse de donnees.
Ta mission est d'analyser la structure d'un dataset deja charge : quels sont
les roles de ses colonnes (mesure, dimension, date, identifiant, texte),
et s'il y a des valeurs manquantes a signaler.
Tu dois utiliser l'outil profile_dataset pour obtenir cette analyse -
ne devine jamais la structure sans l'avoir reellement profile."""


# Le parametre "dataframe" n'est PAS demande au LLM : il n'a aucun moyen
# de le fournir lui-meme. On declare donc l'outil sans parametres visibles
# pour le LLM ; le vrai DataFrame sera injecte par le code au moment
# de l'execution (voir plus bas).
OUTILS_GROQ = [
    {
        "type": "function",
        "function": {
            "name": "profile_dataset",
            "description": (
                "Analyse le dataset actuellement charge et detecte le role "
                "de chaque colonne (mesure, dimension, date, identifiant, texte)."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]


def executer_agent_preparation(mission: str, dataframe: pd.DataFrame) -> str:
    """
    Lance l'Agent Preparation sur un DataFrame deja charge.

    Parametres :
        mission (str)          : la consigne donnee a l'agent
        dataframe (DataFrame)  : les donnees deja chargees (par l'Agent Ingestion)
    """
    client = get_llm_client()
    modele = get_default_model()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mission},
    ]

    reponse = client.chat.completions.create(
        model=modele,
        messages=messages,
        tools=OUTILS_GROQ,
    )

    message = reponse.choices[0].message

    if message.tool_calls:
        messages.append(message)

        for appel in message.tool_calls:
            nom_outil = appel.function.name
            arguments_llm = json.loads(appel.function.arguments)  # normalement vide ici

            print(f"[Agent Preparation] Le LLM demande d'appeler : {nom_outil}()")

            # --- Injection du vrai DataFrame par le code, pas par le LLM ---
            resultat = appeler_outil(
                nom_agent=NOM_AGENT,
                nom_outil=nom_outil,
                dataframe=dataframe,
                **arguments_llm,
            )

            if resultat.get("success"):
                # On transmet le profil (structure legere) mais PAS le DataFrame
                resume_pour_llm = {
                    "success": True,
                    "resume_texte": resultat["resume_texte"],
                }
            else:
                resume_pour_llm = resultat

            messages.append({
                "role": "tool",
                "tool_call_id": appel.id,
                "content": json.dumps(resume_pour_llm),
            })

        reponse_finale = client.chat.completions.create(
            model=modele,
            messages=messages,
        )
        return reponse_finale.choices[0].message.content

    return message.content