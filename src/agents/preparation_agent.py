"""
Agent Preparation : deuxieme agent LLM du pipeline.

Cet agent dispose de deux outils : profile_dataset (analyse les roles
des colonnes) et clean_dataset (nettoie le dataset). clean_dataset a
besoin du profil deja genere - le code garde donc en memoire le profil
obtenu par profile_dataset pour le reutiliser si clean_dataset est
appele ensuite.
"""

import json
import pandas as pd
from src.llm.groq_client import get_llm_client, get_default_model
from src.mcp_server.server import appeler_outil


NOM_AGENT = "agent_preparation"

SYSTEM_PROMPT = """Tu es l'Agent Preparation d'un systeme d'analyse de donnees.
Ta mission est d'analyser la structure d'un dataset deja charge (roles des
colonnes) et de le nettoyer si necessaire (doublons, valeurs manquantes).
Tu disposes de deux outils :
- profile_dataset : analyse les roles de chaque colonne (a utiliser en premier)
- clean_dataset : nettoie le dataset (doublons, valeurs manquantes) - necessite
  que profile_dataset ait deja ete appele
Utilise les outils necessaires selon la mission - ne devine jamais
la structure ou l'etat de proprete sans les avoir reellement verifies."""


OUTILS_GROQ = [
    {
        "type": "function",
        "function": {
            "name": "profile_dataset",
            "description": (
                "Analyse le dataset actuellement charge et detecte le role "
                "de chaque colonne (mesure, dimension, date, identifiant, texte)."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clean_dataset",
            "description": (
                "Nettoie le dataset : supprime les doublons et traite les valeurs "
                "manquantes selon le role de chaque colonne. Necessite que "
                "profile_dataset ait deja ete appele avant."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def executer_agent_preparation(mission: str, dataframe: pd.DataFrame) -> dict:
    """
    Lance l'Agent Preparation sur un DataFrame deja charge.

    Retourne un dictionnaire avec :
        - texte : la reponse finale en langage naturel
        - profil : le profil genere par profile_dataset (ou None)
    """
    client = get_llm_client()
    modele = get_default_model()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mission},
    ]

    profil_obtenu = None  # sera rempli des que profile_dataset reussit

    # Boucle avec plusieurs iterations, car profile_dataset puis clean_dataset
    # peuvent necessiter deux allers-retours avec le LLM
    for _ in range(4):
        reponse = client.chat.completions.create(
            model=modele,
            messages=messages,
            tools=OUTILS_GROQ,
        )

        message = reponse.choices[0].message

        if not message.tool_calls:
            return {"texte": message.content, "profil": profil_obtenu}

        messages.append(message)

        for appel in message.tool_calls:
            nom_outil = appel.function.name
            arguments_llm = json.loads(appel.function.arguments) if appel.function.arguments else {}
            arguments_llm = arguments_llm if isinstance(arguments_llm, dict) else {}

            print(f"[Agent Preparation] Le LLM demande d'appeler : {nom_outil}()")

            # --- clean_dataset a besoin du profil deja obtenu ---
            if nom_outil == "clean_dataset":
                if profil_obtenu is None:
                    resume_pour_llm = {
                        "success": False,
                        "erreur": "Impossible d'appeler clean_dataset avant profile_dataset.",
                    }
                    messages.append({
                        "role": "tool",
                        "tool_call_id": appel.id,
                        "content": json.dumps(resume_pour_llm),
                    })
                    continue

                resultat = appeler_outil(
                    nom_agent=NOM_AGENT,
                    nom_outil=nom_outil,
                    dataframe=dataframe,
                    profil=profil_obtenu,
                )
            else:
                resultat = appeler_outil(
                    nom_agent=NOM_AGENT,
                    nom_outil=nom_outil,
                    dataframe=dataframe,
                    **arguments_llm,
                )

            if resultat.get("success"):
                if nom_outil == "profile_dataset":
                    profil_obtenu = resultat["profil"]
                    resume_pour_llm = {"success": True, "resume_texte": resultat["resume_texte"]}
                elif nom_outil == "clean_dataset":
                    resume_pour_llm = {"success": True, "rapport": resultat["rapport"]}
                else:
                    resume_pour_llm = resultat
            else:
                resume_pour_llm = resultat

            messages.append({
                "role": "tool",
                "tool_call_id": appel.id,
                "content": json.dumps(resume_pour_llm),
            })

    # Si on atteint la limite d'iterations, on force une reponse finale
    reponse_finale = client.chat.completions.create(model=modele, messages=messages)
    return {"texte": reponse_finale.choices[0].message.content, "profil": profil_obtenu}