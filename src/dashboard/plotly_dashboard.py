"""
Moteur de generation de graphiques Plotly.

Types de graphiques : carte choroplethe, series temporelles, radar chart,
waterfall chart, heatmap de correlations - types differents de ceux
utilises dans les deux projets ENSAO deja etudies.
"""

import plotly.graph_objects as go
import pandas as pd


def generer_carte_choroplethe(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Genere une carte choroplethe mondiale, agregeant la premiere mesure
    disponible par pays (colonne de role 'geo').
    """
    try:
        colonne_geo = None
        for nom, infos in profil["colonnes"].items():
            if infos["role"] == "geo":
                colonne_geo = nom
                break

        if colonne_geo is None:
            return {
                "success": False,
                "erreur": "Aucune colonne geographique (pays) detectee dans ce dataset.",
            }

        colonnes_mesures = [n for n, i in profil["colonnes"].items() if i["role"] == "mesure"]
        if not colonnes_mesures:
            return {"success": False, "erreur": "Aucune mesure disponible pour la carte."}

        mesure_choisie = colonnes_mesures[0]
        agregation = dataframe.groupby(colonne_geo)[mesure_choisie].sum().reset_index()

        fig = go.Figure(go.Choropleth(
            locations=agregation[colonne_geo],
            locationmode="country names",
            z=agregation[mesure_choisie],
            colorscale="Greens",
            colorbar_title=mesure_choisie,
        ))
        fig.update_layout(
            title=f"{mesure_choisie} par pays",
            geo={"showframe": False, "showcoastlines": True},
            template="plotly_white",
        )

        return {"success": True, "html": fig.to_html(full_html=False, include_plotlyjs="cdn")}

    except Exception as e:
        return {"success": False, "erreur": f"Erreur lors de la generation de la carte : {str(e)}"}


def generer_series_temporelles(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Genere un graphique de series temporelles (courbes) pour chaque
    mesure, agregee par mois.
    """
    try:
        colonne_date = None
        for nom, infos in profil["colonnes"].items():
            if infos["role"] == "date":
                colonne_date = nom
                break

        if colonne_date is None:
            return {"success": False, "erreur": "Aucune colonne date detectee pour les series temporelles."}

        colonnes_mesures = [n for n, i in profil["colonnes"].items() if i["role"] == "mesure"]
        if not colonnes_mesures:
            return {"success": False, "erreur": "Aucune mesure disponible."}

        df = dataframe.copy()
        df[colonne_date] = pd.to_datetime(df[colonne_date], errors="coerce")
        df = df.dropna(subset=[colonne_date]).set_index(colonne_date)

        df_mensuel = df[colonnes_mesures].resample("ME").mean()

        fig = go.Figure()
        for col in colonnes_mesures:
            fig.add_trace(go.Scatter(x=df_mensuel.index, y=df_mensuel[col], mode="lines", name=col))

        fig.update_layout(
            title="Evolution des mesures dans le temps (moyenne mensuelle)",
            xaxis_title="Date",
            yaxis_title="Valeur",
            template="plotly_white",
        )

        return {"success": True, "html": fig.to_html(full_html=False, include_plotlyjs="cdn")}

    except Exception as e:
        return {"success": False, "erreur": f"Erreur lors de la generation des series temporelles : {str(e)}"}


def generer_radar_chart(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Genere un radar chart (graphique en araignee) comparant toutes les
    mesures normalisees (0-100) sur un seul coup d'oeil.
    """
    try:
        colonnes_mesures = [
            nom for nom, infos in profil["colonnes"].items()
            if infos["role"] == "mesure"
        ]

        if len(colonnes_mesures) < 3:
            return {"success": False, "erreur": "Au moins 3 mesures necessaires pour un radar chart."}

        valeurs_normalisees = []
        for col in colonnes_mesures:
            serie = dataframe[col]
            min_v, max_v = serie.min(), serie.max()
            moyenne = serie.mean()
            if max_v == min_v:
                valeurs_normalisees.append(50)
            else:
                valeurs_normalisees.append(round((moyenne - min_v) / (max_v - min_v) * 100, 2))

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=valeurs_normalisees + [valeurs_normalisees[0]],
            theta=colonnes_mesures + [colonnes_mesures[0]],
            fill="toself",
            name="Position moyenne (normalisee)",
        ))
        fig.update_layout(
            title="Vue d'ensemble des mesures (radar, valeurs normalisees 0-100)",
            polar={"radialaxis": {"visible": True, "range": [0, 100]}},
            template="plotly_white",
        )

        return {"success": True, "html": fig.to_html(full_html=False, include_plotlyjs="cdn")}

    except Exception as e:
        return {"success": False, "erreur": f"Erreur lors de la generation du radar chart : {str(e)}"}


def generer_waterfall_chart(comparaisons: dict, nom_kpi: str) -> dict:
    """
    Genere un graphique en cascade (waterfall) montrant la decomposition
    de l'evolution d'UN SEUL KPI entre la periode precedente et actuelle.
    """
    try:
        if nom_kpi not in comparaisons:
            return {
                "success": False,
                "erreur": f"KPI '{nom_kpi}' introuvable. Noms valides : {list(comparaisons.keys())}",
            }

        infos = comparaisons[nom_kpi]
        valeur_precedente = infos["valeur_precedente"]
        valeur_actuelle = infos["valeur_actuelle"]
        variation = round(valeur_actuelle - valeur_precedente, 2)

        fig = go.Figure(go.Waterfall(
            name=nom_kpi,
            orientation="v",
            measure=["absolute", "relative", "total"],
            x=[f"Periode precedente ({infos['periode_precedente']})",
               "Variation",
               f"Periode actuelle ({infos['periode_actuelle']})"],
            y=[valeur_precedente, variation, valeur_actuelle],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#E74C3C"}},
            increasing={"marker": {"color": "#2ECC71"}},
            totals={"marker": {"color": "#3498DB"}},
        ))
        fig.update_layout(
            title=f"Decomposition de l'evolution : {nom_kpi}",
            template="plotly_white",
        )

        return {"success": True, "html": fig.to_html(full_html=False, include_plotlyjs="cdn")}

    except Exception as e:
        return {"success": False, "erreur": f"Erreur lors de la generation du waterfall : {str(e)}"}


def generer_heatmap_correlation(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Genere une heatmap montrant les correlations entre toutes les mesures.
    """
    try:
        colonnes_mesures = [
            nom for nom, infos in profil["colonnes"].items()
            if infos["role"] == "mesure"
        ]

        if len(colonnes_mesures) < 2:
            return {"success": False, "erreur": "Au moins 2 mesures necessaires pour une heatmap de correlation."}

        matrice_correlation = dataframe[colonnes_mesures].corr().round(2)

        fig = go.Figure(go.Heatmap(
            z=matrice_correlation.values,
            x=matrice_correlation.columns.tolist(),
            y=matrice_correlation.columns.tolist(),
            colorscale="RdBu",
            zmid=0,
            text=matrice_correlation.values,
            texttemplate="%{text}",
        ))
        fig.update_layout(
            title="Correlation entre les mesures",
            template="plotly_white",
        )

        return {"success": True, "html": fig.to_html(full_html=False, include_plotlyjs="cdn")}

    except Exception as e:
        return {"success": False, "erreur": f"Erreur lors de la generation de la heatmap : {str(e)}"}