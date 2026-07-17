"""
Agent KPI : troisieme agent du MVP.

Cet agent dispose de DEUX outils (compute_kpis et detect_anomalies).
Le LLM peut choisir d'appeler l'un, l'autre, ou les deux successivement,
selon la mission qu'on lui donne.

Comme pour l'Agent Preparation : dataframe et profil sont des objets
Python complexes, donc injectes par le code, jamais inventes par le LLM.
"""

import json
import pandas as pd
from src.llm.groq_client import get_llm_client, get_default_model
from src.mcp_server.server import appeler_outil


NOM_AGENT = "agent_kpi"

SYSTEM_PROMPT = """Tu es l'Agent KPI d'un systeme d'analyse de donnees.
Ta mission est de calculer les indicateurs cles (KPIs) du dataset, de
detecter les eventuelles valeurs aberrantes (anomalies), et de comparer
les periodes pour identifier les evolutions (hausse/baisse).
Tu disposes de trois outils :
- compute_kpis : calcule total, moyenne, min, max pour chaque mesure
- detect_anomalies : detecte les valeurs aberrantes (methode IQR)
- compare_periods : compare la periode actuelle a la precedente
Utilise les outils necessaires selon la mission donnee - ne devine
jamais des chiffres sans les avoir reellement calcules."""


OUTILS_GROQ = [
    {
        "type": "function",
        "function": {
            "name": "compute_kpis",
            "description": "Calcule total, moyenne, min et max pour chaque colonne de type mesure.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_anomalies",
            "description": "Detecte les valeurs aberrantes (methode IQR) pour chaque colonne de type mesure.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_periods",
            "description": "Compare chaque mesure entre la periode la plus recente et la precedente, et calcule le pourcentage d'evolution.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

def executer_agent_kpi(mission: str, dataframe: pd.DataFrame, profil: dict, max_iterations: int = 5) -> str:
    client = get_llm_client()
    modele = get_default_model()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mission},
    ]

    outils_deja_appeles = set()

    for iteration in range(max_iterations):
        reponse = client.chat.completions.create(
            model=modele,
            messages=messages,
            tools=OUTILS_GROQ,
        )

        message = reponse.choices[0].message

        if not message.tool_calls:
            return message.content

        messages.append(message)

        for appel in message.tool_calls:
            nom_outil = appel.function.name

            # --- Evite de rappeler un outil deja execute avec succes ---
            if nom_outil in outils_deja_appeles:
                messages.append({
                    "role": "tool",
                    "tool_call_id": appel.id,
                    "content": json.dumps({
                        "success": True,
                        "info": f"Resultat deja obtenu precedemment pour {nom_outil}, ne pas rappeler.",
                    }),
                })
                continue

            arguments_llm = json.loads(appel.function.arguments) if appel.function.arguments else {}
            arguments_llm = arguments_llm if isinstance(arguments_llm, dict) else {}

            print(f"[Agent KPI] Le LLM demande d'appeler : {nom_outil}()")

            resultat = appeler_outil(
                nom_agent=NOM_AGENT,
                nom_outil=nom_outil,
                dataframe=dataframe,
                profil=profil,
                **arguments_llm,
            )

            if resultat.get("success"):
                outils_deja_appeles.add(nom_outil)
                if nom_outil == "compute_kpis":
                    resume_pour_llm = {"success": True, "kpis": resultat["kpis"]}
                elif nom_outil == "detect_anomalies":
                    resume_pour_llm = {"success": True, "anomalies": resultat["anomalies"]}
                elif nom_outil == "compare_periods":
                    resume_pour_llm = {"success": True, "comparaisons": resultat["comparaisons"]}
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
    return reponse_finale.choices[0].message.content