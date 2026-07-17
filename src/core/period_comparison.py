"""
Comparaison automatique de periodes.

Logique : si le dataset couvre beaucoup d'annees differentes, la
comparaison se fait par ANNEE (plus pertinent sur un historique long).
Sinon (peu d'annees), la comparaison se fait par MOIS (plus fin,
adapte a un suivi rapproche).

Fonctionnalite differenciante du projet : aucun des deux projets ENSAO
etudies ne propose cette comparaison automatique.
"""

import pandas as pd


SEUIL_NB_ANNEES = 3  # a partir de ce nombre d'annees distinctes, on compare par annee


def comparer_periodes(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Compare chaque mesure entre la periode la plus recente et la
    periode precedente. Choisit automatiquement la granularite
    (mois ou annee) selon le nombre d'annees distinctes presentes.
    """
    try:
        colonne_date = None
        for nom_col, infos in profil["colonnes"].items():
            if infos["role"] == "date":
                colonne_date = nom_col
                break

        if colonne_date is None:
            return {
                "success": False,
                "erreur": "Aucune colonne de type 'date' detectee dans le profil.",
            }

        df = dataframe.copy()
        df[colonne_date] = pd.to_datetime(df[colonne_date], errors="coerce")
        df = df.dropna(subset=[colonne_date])

        if df.empty:
            return {
                "success": False,
                "erreur": "Aucune date valide apres conversion.",
            }

        # --- Determiner la granularite selon le nombre d'annees distinctes ---
        nb_annees_distinctes = df[colonne_date].dt.year.nunique()

        if nb_annees_distinctes >= SEUIL_NB_ANNEES:
            code_pandas, nom_granularite = "Y", "annee"
        else:
            code_pandas, nom_granularite = "M", "mois"

        resultat = _comparer_par_granularite(df, profil, colonne_date, code_pandas, nom_granularite)

        if resultat["success"]:
            return resultat

        # --- Repli : si la granularite choisie n'a pas assez de periodes,
        #     on tente l'autre granularite avant d'abandonner ---
        granularite_repli = ("M", "mois") if code_pandas == "Y" else ("Y", "annee")
        resultat_repli = _comparer_par_granularite(df, profil, colonne_date, *granularite_repli)

        if resultat_repli["success"]:
            return resultat_repli

        return {
            "success": False,
            "erreur": "Pas assez de mois NI d'annees distincts pour effectuer "
                      "une comparaison de periodes.",
        }

    except Exception as e:
        return {
            "success": False,
            "erreur": f"Erreur lors de la comparaison de periodes : {str(e)}",
        }


def _comparer_par_granularite(df: pd.DataFrame, profil: dict, colonne_date: str,
                                code_pandas: str, nom_granularite: str) -> dict:
    """
    Fonction interne : effectue la comparaison pour une granularite donnee
    (mois ou annee). Retourne success=False si pas assez de periodes
    distinctes pour cette granularite precise.
    """
    df = df.copy()
    df["_periode"] = df[colonne_date].dt.to_period(code_pandas)

    periodes_disponibles = sorted(df["_periode"].unique())

    if len(periodes_disponibles) < 2:
        return {"success": False}

    periode_actuelle = periodes_disponibles[-1]
    periode_precedente = periodes_disponibles[-2]

    comparaisons = {}

    for nom_col, infos in profil["colonnes"].items():
        if infos["role"] != "mesure":
            continue

        moyenne_actuelle = df.loc[df["_periode"] == periode_actuelle, nom_col].mean()
        moyenne_precedente = df.loc[df["_periode"] == periode_precedente, nom_col].mean()

        if pd.isna(moyenne_actuelle) or pd.isna(moyenne_precedente):
            continue

        if moyenne_precedente == 0:
            evolution_pct = None
        else:
            evolution_pct = round(
                (moyenne_actuelle - moyenne_precedente) / abs(moyenne_precedente) * 100, 2
            )

        if evolution_pct is None:
            tendance = "indeterminee"
        elif evolution_pct > 1:
            tendance = "hausse"
        elif evolution_pct < -1:
            tendance = "baisse"
        else:
            tendance = "stable"

        comparaisons[nom_col] = {
            "granularite": nom_granularite,
            "periode_actuelle": str(periode_actuelle),
            "periode_precedente": str(periode_precedente),
            "valeur_actuelle": round(float(moyenne_actuelle), 2),
            "valeur_precedente": round(float(moyenne_precedente), 2),
            "evolution_pct": evolution_pct,
            "tendance": tendance,
        }

    if not comparaisons:
        return {"success": False}

    return {
        "success": True,
        "comparaisons": comparaisons,
    }