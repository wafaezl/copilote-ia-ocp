"""
Registre des outils disponibles sur le serveur MCP.

Ce fichier centralise la liste de tous les outils que les agents
peuvent utiliser : leur nom, la fonction Python reelle a executer,
une description (utile pour le LLM), et les parametres attendus.

Pour ajouter un nouvel outil plus tard (ex: detect_anomalies,
compare_periods...), il suffira de l'importer et de l'ajouter
au dictionnaire OUTILS_DISPONIBLES ci-dessous.
"""

from src.mcp_server.tools import load_dataset, profile_dataset, compute_kpis


OUTILS_DISPONIBLES = {
    "load_dataset": {
        "fonction": load_dataset,
        "description": "Charge un fichier CSV et retourne ses informations de base (nombre de lignes, colonnes).",
        "parametres": {
            "chemin_fichier": "str - chemin vers le fichier CSV a charger",
        },
    },
    "profile_dataset": {
        "fonction": profile_dataset,
        "description": "Analyse les colonnes d'un dataset deja charge et detecte leur role (mesure, dimension, date, identifiant, texte).",
        "parametres": {
            "dataframe": "DataFrame - les donnees deja chargees par load_dataset",
        },
    },
    "compute_kpis": {
        "fonction": compute_kpis,
        "description": "Calcule des indicateurs de base (total, moyenne, min, max) pour chaque colonne identifiee comme mesure.",
        "parametres": {
            "dataframe": "DataFrame - les donnees",
            "profil": "dict - le profil genere par profile_dataset",
        },
    },
}


def obtenir_outil(nom_outil: str):
    """
    Retourne les informations d'un outil du registre, ou None
    si l'outil demande n'existe pas.
    """
    return OUTILS_DISPONIBLES.get(nom_outil)


def lister_outils() -> list:
    """
    Retourne la liste des noms de tous les outils disponibles.
    Utile pour le serveur ou pour du debogage.
    """
    return list(OUTILS_DISPONIBLES.keys())