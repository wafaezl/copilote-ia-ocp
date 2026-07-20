"""
Profileur de donnees : detecte automatiquement le role de chaque colonne
(mesure, dimension, date, identifiant, texte), sans configuration manuelle.
Inspire de l'approche des rapports MCP-BI etudies.
"""

import pandas as pd


def profiler_dataset(df: pd.DataFrame) -> dict:
    """
    Analyse chaque colonne du DataFrame et retourne un profil structure :
    role, type, cardinalite, valeurs manquantes.
    """
    profil = {
        "nb_lignes": len(df),
        "nb_colonnes": len(df.columns),
        "colonnes": {}
    }

    for col in df.columns:
        serie = df[col]
        cardinalite = serie.nunique()
        taux_manquant = serie.isna().mean() * 100

        role = _detecter_role(col, serie, cardinalite, len(df))

        profil["colonnes"][col] = {
            "role": role,
            "type_pandas": str(serie.dtype),
            "cardinalite": int(cardinalite),
            "pct_manquant": round(taux_manquant, 1),
        }

    return profil


def _detecter_role(nom_colonne: str, serie: pd.Series, cardinalite: int, nb_lignes: int) -> str:
    nom_lower = nom_colonne.lower()

    if "date" in nom_lower or "annee" in nom_lower or "year" in nom_lower:
        return "date"

    if pd.api.types.is_datetime64_any_dtype(serie):
        return "date"

    if "id" in nom_lower or "rank" in nom_lower or nom_lower.endswith("_id"):
        return "identifiant"

    if pd.api.types.is_numeric_dtype(serie):
        if cardinalite <= 10 and cardinalite / max(nb_lignes, 1) < 0.05:
            return "dimension"
        return "mesure"

    # --- NOUVEAU : test geographique avant dimension/texte ---
    if _looks_like_geo(serie):
        return "geo"

    if cardinalite <= 100:
        return "dimension"

    return "texte"

def resumer_profil(profil: dict) -> str:
    """Genere un resume en texte brut du profil, exploitable par un LLM."""

    lignes = [
        f"Le jeu de donnees contient {profil['nb_lignes']} lignes et "
        f"{profil['nb_colonnes']} colonnes."
    ]

    for nom_col, infos in profil["colonnes"].items():
        lignes.append(
            f"- '{nom_col}' : role={infos['role']}, "
            f"type={infos['type_pandas']}, "
            f"valeurs distinctes={infos['cardinalite']}, "
            f"manquant={infos['pct_manquant']}%"
        )

    return "\n".join(lignes)

# Referentiel simplifie de noms de pays (en anglais), pour la detection geographique
PAYS_REFERENTIEL = {
    "afghanistan", "albania", "algeria", "argentina", "armenia", "australia",
    "austria", "azerbaijan", "bahrain", "bangladesh", "belarus", "belgium",
    "brazil", "bulgaria", "cambodia", "cameroon", "canada", "chile", "china",
    "colombia", "croatia", "cuba", "cyprus", "czech republic", "denmark",
    "ecuador", "egypt", "estonia", "ethiopia", "finland", "france", "georgia",
    "germany", "ghana", "greece", "hungary", "iceland", "india", "indonesia",
    "iran", "iraq", "ireland", "israel", "italy", "jamaica", "japan", "jordan",
    "kazakhstan", "kenya", "kuwait", "latvia", "lebanon", "libya", "lithuania",
    "luxembourg", "malaysia", "mexico", "moldova", "monaco", "morocco",
    "netherlands", "new zealand", "nigeria", "norway", "oman", "pakistan",
    "panama", "peru", "philippines", "poland", "portugal", "qatar", "romania",
    "russia", "saudi arabia", "senegal", "serbia", "singapore", "slovakia",
    "slovenia", "south africa", "south korea", "spain", "sri lanka", "sudan",
    "sweden", "switzerland", "syria", "taiwan", "thailand", "tunisia",
    "turkey", "ukraine", "united arab emirates", "united kingdom",
    "united states", "uruguay", "venezuela", "vietnam", "yemen", "zimbabwe",
    "morocco", "maroc",
}


def _looks_like_geo(serie: pd.Series, seuil: float = 0.5) -> bool:
    """
    Verifie si une colonne texte contient majoritairement des noms de pays
    reconnus, pour la classer en role 'geo'.
    """
    valeurs_uniques = serie.dropna().astype(str).str.lower().str.strip().unique()
    if len(valeurs_uniques) == 0:
        return False
    nb_matchs = sum(1 for v in valeurs_uniques if v in PAYS_REFERENTIEL)
    return (nb_matchs / len(valeurs_uniques)) >= seuil