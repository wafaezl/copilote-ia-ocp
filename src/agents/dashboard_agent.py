"""
Agent Tableau de bord : quatrieme agent LLM du pipeline.

Cet agent genere jusqu'a 5 types de graphiques, choisis par le LLM
selon leur pertinence pour le dataset :
- generate_choropleth_map : carte mondiale (necessite colonne geo)
- generate_time_series : evolution mensuelle (necessite colonne date)
- generate_radar_chart : vue d'ensemble normalisee des mesures
- generate_waterfall_chart : decomposition de l'evolution d'un KPI
- generate_correlation_heatmap : correlations entre mesures
"""

import json
import pandas as pd
from src.llm.groq_client import get_llm_client, get_default_model
from src.mcp_server.server import appeler_outil


NOM_AGENT = "agent_dashboard"

SYSTEM_PROMPT = """Tu es l'Agent Tableau de bord. Tu disposes de 5 types de graphiques :
- generate_choropleth_map : carte mondiale par pays (utile seulement si une colonne pays existe)
- generate_time_series : evolution mensuelle des mesures (utile si une colonne date existe)
- generate_radar_chart : vue d'ensemble normalisee de toutes les mesures
- generate_waterfall_chart : decomposition de l'evolution d'UN KPI precis - utilise UNIQUEMENT
  les noms de KPI donnes explicitement dans la mission, jamais un nom invente
- generate_correlation_heatmap : correlations entre les mesures

Essaie chaque graphique UNE SEULE FOIS. Si generate_choropleth_map echoue (pas de
colonne geographique), n'insiste pas, passe directement aux autres graphiques.
N'appelle jamais un outil deja reussi."""

OUTILS_GROQ = [
    {
        "type": "function",
        "function": {
            "name": "generate_choropleth_map",
            "description": "Genere une carte mondiale par pays.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_time_series",
            "description": "Genere l'evolution mensuelle des mesures.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_radar_chart",
            "description": "Genere un radar chart des mesures normalisees.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_waterfall_chart",
            "description": "Genere un graphique en cascade pour UN KPI precis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom_kpi": {"type": "string", "description": "Nom exact du KPI a decomposer."},
                },
                "required": ["nom_kpi"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_correlation_heatmap",
            "description": "Genere une heatmap des correlations.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def executer_agent_dashboard(mission: str, dataframe: pd.DataFrame, profil: dict,
                               kpis: dict, comparaisons: dict) -> dict:
    client = get_llm_client()
    modele = get_default_model()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mission},
    ]

    graphiques_html = {}
    outils_deja_reussis = set()
    echecs_par_outil = {}   # <-- AJOUT : compte les echecs par outil

    for _ in range(8):
        reponse = client.chat.completions.create(
            model=modele,
            messages=messages,
            tools=OUTILS_GROQ,
        )

        message = reponse.choices[0].message

        if not message.tool_calls:
            return {"texte": message.content, "graphiques": graphiques_html}

        messages.append(message)

        for appel in message.tool_calls:
            nom_outil = appel.function.name
            arguments_llm = json.loads(appel.function.arguments) if appel.function.arguments else {}
            arguments_llm = arguments_llm if isinstance(arguments_llm, dict) else {}

            if nom_outil in outils_deja_reussis:
                messages.append({
                    "role": "tool", "tool_call_id": appel.id,
                    "content": json.dumps({"success": True, "info": f"{nom_outil} deja genere."}),
                })
                continue

            # --- AJOUT : bloque apres 2 echecs sur le meme outil ---
            if echecs_par_outil.get(nom_outil, 0) >= 2 and nom_outil != "generate_waterfall_chart":
                messages.append({
                    "role": "tool", "tool_call_id": appel.id,
                    "content": json.dumps({
                        "success": False,
                        "erreur": f"{nom_outil} a deja echoue plusieurs fois, abandonne definitivement.",
                    }),
                })
                continue

            print(f"[Agent Dashboard] Le LLM demande d'appeler : {nom_outil}({arguments_llm})")

            if nom_outil in ("generate_choropleth_map", "generate_radar_chart",
                              "generate_correlation_heatmap", "generate_time_series"):
                resultat = appeler_outil(nom_agent=NOM_AGENT, nom_outil=nom_outil,
                                          dataframe=dataframe, profil=profil)
            elif nom_outil == "generate_waterfall_chart":
                resultat = appeler_outil(nom_agent=NOM_AGENT, nom_outil=nom_outil,
                                          comparaisons=comparaisons, **arguments_llm)
            else:
                resultat = {"success": False, "erreur": f"Outil inconnu : {nom_outil}"}

            if resultat.get("success"):
                graphiques_html[nom_outil] = resultat["html"]
                outils_deja_reussis.add(nom_outil)
                resume_pour_llm = {"success": True, "message": f"Graphique {nom_outil} genere avec succes."}
            else:
                echecs_par_outil[nom_outil] = echecs_par_outil.get(nom_outil, 0) + 1
                resume_pour_llm = resultat

            messages.append({
                "role": "tool", "tool_call_id": appel.id,
                "content": json.dumps(resume_pour_llm),
            })

    reponse_finale = client.chat.completions.create(model=modele, messages=messages)
    return {"texte": reponse_finale.choices[0].message.content, "graphiques": graphiques_html}