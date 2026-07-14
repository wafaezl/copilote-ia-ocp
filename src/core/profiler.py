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
    """Heuristique simple de detection du role d'une colonne."""

    nom_lower = nom_colonne.lower()

    # 1. Detection date : par nom ou par tentative de conversion
    if "date" in nom_lower or "annee" in nom_lower or "year" in nom_lower:
        return "date"

    if pd.api.types.is_datetime64_any_dtype(serie):
        return "date"

    # 2. Detection identifiant : forte cardinalite + nom evocateur
    if "id" in nom_lower or "rank" in nom_lower or nom_lower.endswith("_id"):
        return "identifiant"

    # 3. Colonnes numeriques
    if pd.api.types.is_numeric_dtype(serie):
        # Peu de valeurs distinctes -> plutot categoriel malgre le type numerique
        if cardinalite <= 10 and cardinalite / max(nb_lignes, 1) < 0.05:
            return "dimension"
        return "mesure"

    # 4. Colonnes textuelles / categorielles
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