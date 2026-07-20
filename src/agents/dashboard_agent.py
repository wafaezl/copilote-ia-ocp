"""
Agent Tableau de bord : quatrieme agent LLM du pipeline.

Cet agent genere 3 types de graphiques :
- generate_boxplot : automatique, sur toutes les mesures (pas de choix du LLM)
- generate_evolution_chart : automatique, a partir de compare_periods
- generate_gauge : ICI le LLM apporte un vrai jugement - il choisit QUEL
  KPI merite une jauge et QUEL seuil est pertinent, mais ne fournit
  jamais la valeur reelle (recuperee depuis les KPIs deja calcules,
  pour eviter toute hallucination de chiffre).
"""

import json
import pandas as pd
from src.llm.groq_client import get_llm_client, get_default_model
from src.mcp_server.server import appeler_outil


NOM_AGENT = "agent_dashboard"

SYSTEM_PROMPT = """Tu es l'Agent Tableau de bord. Genere les 3 graphiques disponibles :
generate_boxplot, generate_evolution_chart, et generate_gauge.

Pour generate_gauge : choisis un KPI important parmi ceux reellement disponibles
et un seuil raisonnable. Si le nom du KPI est rejete comme introuvable, le message
d'erreur te donnera la liste exacte des noms valides - reessaie IMMEDIATEMENT avec
un de ces noms exacts, ne jamais abandonner."""


OUTILS_GROQ = [
    {
        "type": "function",
        "function": {
            "name": "generate_boxplot",
            "description": "Genere un boxplot pour toutes les colonnes de type mesure.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_evolution_chart",
            "description": "Genere le graphique d'evolution entre la periode precedente et actuelle.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_gauge",
            "description": "Genere une jauge pour un KPI precis, avec un seuil de reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom_kpi": {
                        "type": "string",
                        "description": "Nom exact du KPI a afficher (doit correspondre a une colonne des KPIs deja calcules).",
                    },
                    "seuil": {
                        "type": "number",
                        "description": "Seuil de reference propose pour ce KPI.",
                    },
                    "sens_positif": {
                        "type": "string",
                        "enum": ["haut", "bas"],
                        "description": "'haut' si depasser le seuil est bon, 'bas' si depasser le seuil est mauvais.",
                    },
                },
                "required": ["nom_kpi", "seuil", "sens_positif"],
            },
        },
    },
]


def executer_agent_dashboard(mission: str, dataframe: pd.DataFrame, profil: dict,
                               kpis: dict, comparaisons: dict) -> dict:
    """
    Lance l'Agent Tableau de bord.

    Retourne un dictionnaire avec :
        - texte : la reponse finale en langage naturel
        - graphiques : dict {nom_outil: html_du_graphique}
    """
    client = get_llm_client()
    modele = get_default_model()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mission},
    ]

    graphiques_html = {}
    outils_deja_reussis = set()

    for _ in range(6):
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

            if nom_outil in outils_deja_reussis and nom_outil != "generate_gauge":
                messages.append({
                    "role": "tool",
                    "tool_call_id": appel.id,
                    "content": json.dumps({
                        "success": True,
                        "info": f"{nom_outil} deja genere precedemment, ne pas rappeler.",
                    }),
                })
                continue

            print(f"[Agent Dashboard] Le LLM demande d'appeler : {nom_outil}({arguments_llm})")

            if nom_outil == "generate_boxplot":
                resultat = appeler_outil(nom_agent=NOM_AGENT, nom_outil=nom_outil,
                                          dataframe=dataframe, profil=profil)
            elif nom_outil == "generate_evolution_chart":
                resultat = appeler_outil(nom_agent=NOM_AGENT, nom_outil=nom_outil,
                                          comparaisons=comparaisons)
            elif nom_outil == "generate_gauge":
                resultat = appeler_outil(nom_agent=NOM_AGENT, nom_outil=nom_outil,
                                          kpis=kpis, **arguments_llm)
            else:
                resultat = {"success": False, "erreur": f"Outil inconnu : {nom_outil}"}

            if resultat.get("success"):
                graphiques_html[nom_outil] = resultat["html"]
                outils_deja_reussis.add(nom_outil)
                resume_pour_llm = {"success": True, "message": f"Graphique {nom_outil} genere avec succes."}
            else:
                resume_pour_llm = resultat

            messages.append({
                "role": "tool",
                "tool_call_id": appel.id,
                "content": json.dumps(resume_pour_llm),
            })

    reponse_finale = client.chat.completions.create(model=modele, messages=messages)
    return {"texte": reponse_finale.choices[0].message.content, "graphiques": graphiques_html}