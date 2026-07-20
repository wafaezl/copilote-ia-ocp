"""
Registre des outils disponibles sur le serveur MCP.

Ce fichier centralise la liste de tous les outils que les agents
peuvent utiliser : leur nom, la fonction Python reelle a executer,
une description (utile pour le LLM), et les parametres attendus.
"""

from src.mcp_server.tools import (
    load_dataset, profile_dataset, compute_kpis,
    detect_anomalies, clean_dataset, compare_periods,
    generate_choropleth_map, generate_time_series,
    generate_radar_chart, generate_waterfall_chart, generate_correlation_heatmap,
)


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
        "description": "Analyse les colonnes d'un dataset deja charge et detecte leur role (mesure, dimension, date, identifiant, geo, texte).",
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
    "detect_anomalies": {
        "fonction": detect_anomalies,
        "description": "Detecte les valeurs aberrantes (methode IQR) pour chaque colonne de type mesure.",
        "parametres": {
            "dataframe": "DataFrame - les donnees",
            "profil": "dict - le profil genere par profile_dataset",
        },
    },
    "clean_dataset": {
        "fonction": clean_dataset,
        "description": "Nettoie le dataset : supprime les doublons et traite les valeurs manquantes selon le role de chaque colonne.",
        "parametres": {
            "dataframe": "DataFrame - les donnees",
            "profil": "dict - le profil genere par profile_dataset",
        },
    },
    "compare_periods": {
        "fonction": compare_periods,
        "description": "Compare chaque mesure entre la periode la plus recente et la precedente (annee ou mois selon l'historique disponible).",
        "parametres": {
            "dataframe": "DataFrame - les donnees",
            "profil": "dict - le profil genere par profile_dataset",
        },
    },
    "generate_choropleth_map": {
        "fonction": generate_choropleth_map,
        "description": "Genere une carte mondiale (choroplethe) agregeant une mesure par pays. Necessite une colonne geographique.",
        "parametres": {
            "dataframe": "DataFrame - les donnees",
            "profil": "dict - le profil genere par profile_dataset",
        },
    },
    "generate_time_series": {
        "fonction": generate_time_series,
        "description": "Genere des courbes d'evolution mensuelle pour chaque mesure. Necessite une colonne date.",
        "parametres": {
            "dataframe": "DataFrame - les donnees",
            "profil": "dict - le profil genere par profile_dataset",
        },
    },
    "generate_radar_chart": {
        "fonction": generate_radar_chart,
        "description": "Genere un radar chart comparant toutes les mesures normalisees, pour une vue d'ensemble rapide.",
        "parametres": {
            "dataframe": "DataFrame - les donnees",
            "profil": "dict - le profil genere par profile_dataset",
        },
    },
    "generate_waterfall_chart": {
        "fonction": generate_waterfall_chart,
        "description": "Genere un graphique en cascade decomposant l'evolution d'UN SEUL KPI entre deux periodes.",
        "parametres": {
            "comparaisons": "dict - le resultat de compare_periods",
            "nom_kpi": "str - le KPI a decomposer",
        },
    },
    "generate_correlation_heatmap": {
        "fonction": generate_correlation_heatmap,
        "description": "Genere une heatmap montrant les correlations entre toutes les mesures numeriques.",
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