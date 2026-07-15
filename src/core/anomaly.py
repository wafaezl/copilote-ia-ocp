"""
Detection d'anomalies (valeurs aberrantes) dans les colonnes de type mesure.

Methode utilisee : IQR (Interquartile Range / ecart interquartile).
Choix volontairement different du score z modifie (MAD) utilise dans
les deux projets ENSAO deja realises sur ce sujet.

Principe de l'IQR :
    - Q1 = 25e percentile, Q3 = 75e percentile
    - IQR = Q3 - Q1
    - Toute valeur en dehors de [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
      est consideree comme une anomalie (regle statistique standard).
"""

import pandas as pd


def detecter_anomalies(dataframe: pd.DataFrame, profil: dict, seuil_iqr: float = 1.5) -> dict:
    """
    Detecte les valeurs aberrantes pour chaque colonne de type "mesure".

    Parametres :
        dataframe (DataFrame) : les donnees
        profil (dict)         : le profil genere par profile_dataset
        seuil_iqr (float)     : multiplicateur de l'IQR (1.5 = standard,
                                 3.0 = plus tolerant, ne signale que les
                                 anomalies tres extremes)

    Retourne un dictionnaire avec, pour chaque mesure analysee :
        - nb_anomalies : nombre de valeurs hors limites
        - pct_anomalies : pourcentage par rapport au total
        - borne_basse / borne_haute : les limites calculees
        - exemples : quelques valeurs aberrantes trouvees (max 5)
    """
    try:
        resultats = {}

        for nom_col, infos in profil["colonnes"].items():
            if infos["role"] != "mesure":
                continue

            serie = dataframe[nom_col].dropna()

            q1 = serie.quantile(0.25)
            q3 = serie.quantile(0.75)
            iqr = q3 - q1

            borne_basse = q1 - seuil_iqr * iqr
            borne_haute = q3 + seuil_iqr * iqr

            anomalies = serie[(serie < borne_basse) | (serie > borne_haute)]

            resultats[nom_col] = {
                "nb_anomalies": int(len(anomalies)),
                "pct_anomalies": round(len(anomalies) / len(serie) * 100, 2) if len(serie) > 0 else 0,
                "borne_basse": round(float(borne_basse), 2),
                "borne_haute": round(float(borne_haute), 2),
                "exemples": [round(float(v), 2) for v in anomalies.head(5).tolist()],
            }

        if not resultats:
            return {
                "success": False,
                "erreur": "Aucune colonne de type 'mesure' disponible pour la detection d'anomalies.",
            }

    except Exception as e:
        return {
            "success": False,
            "erreur": f"Erreur lors de la detection d'anomalies : {str(e)}",
        }

    return {
        "success": True,
        "anomalies": resultats,
    }