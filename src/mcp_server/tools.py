"""
Outils exposes par le serveur MCP.
Chaque fonction ici represente une action concrete qu'un agent
pourra demander au serveur d'executer.
"""

import pandas as pd
from src.core.profiler import profiler_dataset, resumer_profil
from src.core.anomaly import detecter_anomalies
from src.core.cleaner import nettoyer_dataset
from src.core.period_comparison import comparer_periodes
from src.dashboard.plotly_dashboard import (
    generer_carte_choroplethe, generer_series_temporelles,
    generer_radar_chart, generer_waterfall_chart, generer_heatmap_correlation,
)


def load_dataset(chemin_fichier: str) -> dict:
    """
    Charge un fichier CSV et retourne les donnees + quelques infos de base.
    """
    try:
        df = pd.read_csv(chemin_fichier)
    except FileNotFoundError:
        return {
            "success": False,
            "erreur": f"Fichier introuvable : {chemin_fichier}",
        }
    except Exception as e:
        return {
            "success": False,
            "erreur": f"Erreur lors du chargement : {str(e)}",
        }

    return {
        "success": True,
        "nb_lignes": len(df),
        "nb_colonnes": len(df.columns),
        "colonnes": list(df.columns),
        "dataframe": df,
    }


def profile_dataset(dataframe: pd.DataFrame) -> dict:
    """
    Profile un DataFrame deja charge : detecte le role de chaque colonne
    (mesure, dimension, date, identifiant, texte, geo).

    Reutilise directement le profiler deja construit et teste.
    """
    try:
        profil = profiler_dataset(dataframe)
        resume_texte = resumer_profil(profil)
    except Exception as e:
        return {
            "success": False,
            "erreur": f"Erreur lors du profilage : {str(e)}",
        }

    return {
        "success": True,
        "profil": profil,
        "resume_texte": resume_texte,
    }


def compute_kpis(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Calcule des KPIs de base a partir des colonnes detectees comme "mesure"
    dans le profil : total, moyenne, min, max pour chaque mesure.
    """
    try:
        kpis = {}

        for nom_col, infos in profil["colonnes"].items():
            if infos["role"] == "mesure":
                serie = dataframe[nom_col]
                kpis[nom_col] = {
                    "total": round(float(serie.sum()), 2),
                    "moyenne": round(float(serie.mean()), 2),
                    "min": round(float(serie.min()), 2),
                    "max": round(float(serie.max()), 2),
                }

        if not kpis:
            return {
                "success": False,
                "erreur": "Aucune colonne de type 'mesure' detectee dans le profil.",
            }

    except Exception as e:
        return {
            "success": False,
            "erreur": f"Erreur lors du calcul des KPIs : {str(e)}",
        }

    return {
        "success": True,
        "kpis": kpis,
    }


def detect_anomalies(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Detecte les valeurs aberrantes (methode IQR) pour chaque colonne
    de type mesure. Reutilise directement le moteur de src/core/anomaly.py.
    """
    try:
        resultat = detecter_anomalies(dataframe, profil)
    except Exception as e:
        return {
            "success": False,
            "erreur": f"Erreur lors de la detection d'anomalies : {str(e)}",
        }

    return resultat


def clean_dataset(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Nettoie le dataset (doublons, valeurs manquantes) selon le role
    de chaque colonne. Reutilise le moteur de src/core/cleaner.py.
    """
    try:
        resultat = nettoyer_dataset(dataframe, profil)
    except Exception as e:
        return {
            "success": False,
            "erreur": f"Erreur lors du nettoyage : {str(e)}",
        }
    return resultat


def compare_periods(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Compare chaque mesure entre la periode la plus recente et la
    periode precedente (annee ou mois, choisi automatiquement).
    Reutilise le moteur de src/core/period_comparison.py.
    """
    try:
        resultat = comparer_periodes(dataframe, profil)
    except Exception as e:
        return {
            "success": False,
            "erreur": f"Erreur lors de la comparaison de periodes : {str(e)}",
        }
    return resultat


def generate_choropleth_map(dataframe: pd.DataFrame, profil: dict) -> dict:
    """Genere une carte mondiale par pays (necessite une colonne geo)."""
    try:
        return generer_carte_choroplethe(dataframe, profil)
    except Exception as e:
        return {"success": False, "erreur": f"Erreur carte : {str(e)}"}


def generate_time_series(dataframe: pd.DataFrame, profil: dict) -> dict:
    """Genere l'evolution mensuelle des mesures (necessite une colonne date)."""
    try:
        return generer_series_temporelles(dataframe, profil)
    except Exception as e:
        return {"success": False, "erreur": f"Erreur series temporelles : {str(e)}"}


def generate_radar_chart(dataframe: pd.DataFrame, profil: dict) -> dict:
    """Genere un radar chart des mesures normalisees."""
    try:
        return generer_radar_chart(dataframe, profil)
    except Exception as e:
        return {"success": False, "erreur": f"Erreur radar : {str(e)}"}


def generate_waterfall_chart(comparaisons: dict, nom_kpi: str) -> dict:
    """Genere un graphique en cascade decomposant l'evolution d'UN KPI precis."""
    try:
        return generer_waterfall_chart(comparaisons, nom_kpi)
    except Exception as e:
        return {"success": False, "erreur": f"Erreur waterfall : {str(e)}"}


def generate_correlation_heatmap(dataframe: pd.DataFrame, profil: dict) -> dict:
    """Genere une heatmap des correlations entre les mesures."""
    try:
        return generer_heatmap_correlation(dataframe, profil)
    except Exception as e:
        return {"success": False, "erreur": f"Erreur heatmap : {str(e)}"}