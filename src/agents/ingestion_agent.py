"""
Premier vrai agent IA du projet : l'Agent Ingestion.

Contrairement aux tests precedents ou TOI tu decidais d'appeler
load_dataset explicitement, ici c'est le LLM (Llama, via Groq) qui
recoit une mission et DECIDE lui-meme d'appeler cet outil.

Mecanisme utilise : tool-use / function-calling.
"""

import json
from src.llm.groq_client import get_llm_client, get_default_model
from src.mcp_server.server import appeler_outil


NOM_AGENT = "agent_ingestion"

SYSTEM_PROMPT = """Tu es l'Agent Ingestion d'un systeme d'analyse de donnees.
Ta mission est de charger un fichier de donnees et de rapporter clairement
ce qu'il contient (nombre de lignes, colonnes disponibles).
Tu dois utiliser l'outil load_dataset pour charger le fichier -
ne devine jamais son contenu sans l'avoir reellement charge."""


# Schema de l'outil, au format attendu par l'API Groq (tool-use).
# Pour l'instant defini manuellement, car le parametre est simple
# (une chaine de caracteres). On enrichira cette approche plus tard
# si des outils avec des parametres plus complexes doivent etre exposes.
OUTILS_GROQ = [
    {
        "type": "function",
        "function": {
            "name": "load_dataset",
            "description": "Charge un fichier CSV et retourne son nombre de lignes et de colonnes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chemin_fichier": {
                        "type": "string",
                        "description": "Chemin vers le fichier CSV a charger",
                    }
                },
                "required": ["chemin_fichier"],
            },
        },
    }
]


def executer_agent_ingestion(mission: str) -> str:
    """
    Lance l'Agent Ingestion sur une mission donnee.

    Boucle agentique :
        1. Envoie la mission + les outils disponibles au LLM
        2. Si le LLM demande un appel d'outil -> on l'execute via le serveur MCP
        3. On renvoie le resultat au LLM
        4. Le LLM formule sa reponse finale
    """
    client = get_llm_client()
    modele = get_default_model()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mission},
    ]

    # --- Premier appel : le LLM decide quoi faire ---
    reponse = client.chat.completions.create(
        model=modele,
        messages=messages,
        tools=OUTILS_GROQ,
    )

    message = reponse.choices[0].message

    # --- Le LLM a-t-il demande d'appeler un outil ? ---
    if message.tool_calls:
        messages.append(message)  # on garde la trace de sa decision

        for appel in message.tool_calls:
            nom_outil = appel.function.name
            arguments_llm = json.loads(appel.function.arguments) if appel.function.arguments else {}
            arguments_llm = arguments_llm if isinstance(arguments_llm, dict) else {}

            print(f"[Agent Ingestion] Le LLM demande d'appeler : {nom_outil}({arguments})")

            # --- Execution reelle via le serveur MCP (permissions verifiees) ---
            resultat = appeler_outil(nom_agent=NOM_AGENT, nom_outil=nom_outil, **arguments)

            # On ne renvoie pas le DataFrame complet au LLM (impossible a serialiser
            # et inutile) - juste un resume exploitable en texte.
            if resultat.get("success"):
                resume_pour_llm = {
                    "success": True,
                    "nb_lignes": resultat["nb_lignes"],
                    "nb_colonnes": resultat["nb_colonnes"],
                    "colonnes": resultat["colonnes"],
                }
            else:
                resume_pour_llm = resultat

            messages.append({
                "role": "tool",
                "tool_call_id": appel.id,
                "content": json.dumps(resume_pour_llm),
            })

        # --- Deuxieme appel : le LLM formule sa reponse finale avec le resultat ---
        reponse_finale = client.chat.completions.create(
            model=modele,
            messages=messages,
        )
        return reponse_finale.choices[0].message.content

    # Cas rare : le LLM repond directement sans appeler d'outil
    return message.content