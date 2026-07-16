"""
Nettoyage des donnees : gere les valeurs manquantes, les doublons,
et les incoherences de types, en s'appuyant sur le profil deja genere
par profiler.py.

Principe : les regles de nettoyage s'adaptent au role de chaque colonne
(mesure, dimension, date...), sans configuration manuelle prealable.
"""

import pandas as pd


def nettoyer_dataset(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Applique un nettoyage adapte au role de chaque colonne.

    Regles appliquees :
        - Doublons : lignes entierement identiques -> supprimees
        - Mesures (valeurs manquantes) : remplacees par la mediane
        - Dimensions (valeurs manquantes) : remplacees par "Inconnu"
        - Dates (valeurs manquantes) : lignes supprimees (une date
          manquante rend la ligne difficile a exploiter pour les KPIs)

    Retourne :
        - dataframe_propre : le DataFrame nettoye
        - rapport : resume des operations effectuees (utile pour la tracabilite)
    """
    try:
        df = dataframe.copy()
        rapport = {
            "lignes_avant": len(df),
            "operations": [],
        }

        # --- 1. Suppression des doublons ---
        nb_avant = len(df)
        df = df.drop_duplicates()
        nb_supprimes = nb_avant - len(df)
        if nb_supprimes > 0:
            rapport["operations"].append(
                f"{nb_supprimes} ligne(s) dupliquee(s) supprimee(s)."
            )

        # --- 2. Traitement colonne par colonne, selon le role detecte ---
        for nom_col, infos in profil["colonnes"].items():
            if nom_col not in df.columns:
                continue

            nb_manquants = df[nom_col].isna().sum()
            if nb_manquants == 0:
                continue  # rien a faire pour cette colonne

            role = infos["role"]

            if role == "mesure":
                mediane = df[nom_col].median()
                df[nom_col] = df[nom_col].fillna(mediane)
                rapport["operations"].append(
                    f"'{nom_col}' (mesure) : {nb_manquants} valeur(s) manquante(s) "
                    f"remplacee(s) par la mediane ({round(mediane, 2)})."
                )

            elif role == "dimension":
                df[nom_col] = df[nom_col].fillna("Inconnu")
                rapport["operations"].append(
                    f"'{nom_col}' (dimension) : {nb_manquants} valeur(s) manquante(s) "
                    f"remplacee(s) par 'Inconnu'."
                )

            elif role == "date":
                nb_avant_date = len(df)
                df = df.dropna(subset=[nom_col])
                rapport["operations"].append(
                    f"'{nom_col}' (date) : {nb_avant_date - len(df)} ligne(s) "
                    f"supprimee(s) car date manquante."
                )

            else:
                # identifiant / texte : on laisse tel quel, juste signale
                rapport["operations"].append(
                    f"'{nom_col}' ({role}) : {nb_manquants} valeur(s) manquante(s) "
                    f"laissee(s) telle(s) quelle(s) (role non traite automatiquement)."
                )

        rapport["lignes_apres"] = len(df)
        rapport["taux_conservation"] = round(len(df) / rapport["lignes_avant"] * 100, 2) \
            if rapport["lignes_avant"] > 0 else 0

    except Exception as e:
        return {
            "success": False,
            "erreur": f"Erreur lors du nettoyage : {str(e)}",
        }

    return {
        "success": True,
        "dataframe_propre": df,
        "rapport": rapport,
    }