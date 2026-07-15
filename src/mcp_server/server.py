"""
Serveur MCP (version simplifiee, sans reseau pour l'instant).

C'est le point de passage unique entre les agents et les outils :
il verifie les permissions, execute l'outil demande via le registre,
et journalise chaque appel pour la tracabilite.
"""

from src.mcp_server.registry import obtenir_outil
from src.mcp_server.permissions import est_autorise


# Journal simple en memoire (liste de tous les appels effectues)
JOURNAL_APPELS = []


def appeler_outil(nom_agent: str, nom_outil: str, **parametres) -> dict:
    """
    Point d'entree principal du serveur MCP.

    Etapes :
        1. Verifie que l'outil existe dans le registre
        2. Verifie que l'agent a le droit de l'appeler
        3. Execute l'outil avec les parametres fournis
        4. Journalise l'appel (succes ou echec)
        5. Retourne le resultat

    Parametres :
        nom_agent (str)   : le nom de l'agent qui fait la demande
        nom_outil (str)   : le nom de l'outil a executer
        **parametres      : les arguments a transmettre a l'outil

    Retourne un dictionnaire toujours de la forme :
        {"success": bool, ... resultat ou erreur ...}
    """

    # --- 1. L'outil existe-t-il dans le registre ? ---
    outil = obtenir_outil(nom_outil)
    if outil is None:
        resultat = {
            "success": False,
            "erreur": f"Outil '{nom_outil}' introuvable dans le registre.",
        }
        _journaliser(nom_agent, nom_outil, parametres, resultat)
        return resultat

    # --- 2. L'agent a-t-il la permission d'utiliser cet outil ? ---
    if not est_autorise(nom_agent, nom_outil):
        resultat = {
            "success": False,
            "erreur": f"Acces refuse : l'agent '{nom_agent}' n'est pas autorise "
                      f"a utiliser l'outil '{nom_outil}'.",
        }
        _journaliser(nom_agent, nom_outil, parametres, resultat)
        return resultat

    # --- 3. Execution de l'outil ---
    fonction = outil["fonction"]
    try:
        resultat = fonction(**parametres)
    except Exception as e:
        resultat = {
            "success": False,
            "erreur": f"Erreur pendant l'execution de '{nom_outil}' : {str(e)}",
        }

    # --- 4. Journalisation ---
    _journaliser(nom_agent, nom_outil, parametres, resultat)

    # --- 5. Retour du resultat ---
    return resultat


def _journaliser(nom_agent: str, nom_outil: str, parametres: dict, resultat: dict):
    """
    Enregistre chaque appel dans le journal en memoire.
    Ne stocke pas le DataFrame complet dans les parametres/resultat
    (trop volumineux), juste une trace lisible.
    """
    entree = {
        "agent": nom_agent,
        "outil": nom_outil,
        "parametres": list(parametres.keys()),  # juste les noms, pas les DataFrames entiers
        "succes": resultat.get("success", False),
        "erreur": resultat.get("erreur"),
    }
    JOURNAL_APPELS.append(entree)


def afficher_journal():
    """Affiche tous les appels effectues depuis le demarrage du serveur."""
    for i, entree in enumerate(JOURNAL_APPELS, start=1):
        statut = "OK" if entree["succes"] else "ECHEC"
        print(f"{i}. [{statut}] agent={entree['agent']} outil={entree['outil']} "
              f"parametres={entree['parametres']}"
              + (f" | erreur={entree['erreur']}" if entree['erreur'] else ""))