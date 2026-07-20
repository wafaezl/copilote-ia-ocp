"""
Moteur de generation de graphiques Plotly.

Types de graphiques choisis volontairement DIFFERENTS de ceux utilises
dans les deux projets ENSAO deja etudies (qui utilisent barres, lignes,
camemberts, cartes choroplèthes, nuages de points, histogrammes) :

    - Boxplot : visualise directement les quartiles et bornes IQR
      utilises par notre detection d'anomalies (anomaly.py)
    - Graphique d'evolution : visualise les resultats de compare_periods
    - Jauge (gauge) : indicateur visuel d'un KPI par rapport a un seuil
"""

import plotly.graph_objects as go
import pandas as pd


def generer_boxplot(dataframe: pd.DataFrame, profil: dict) -> dict:
    """
    Genere un boxplot (boite a moustaches) pour chaque colonne de type
    mesure. Montre visuellement les quartiles (Q1, mediane, Q3) et les
    valeurs aberrantes - lien direct avec la methode IQR de anomaly.py.
    """
    try:
        colonnes_mesures = [
            nom for nom, infos in profil["colonnes"].items()
            if infos["role"] == "mesure"
        ]

        if not colonnes_mesures:
            return {"success": False, "erreur": "Aucune colonne de type mesure pour le boxplot."}

        fig = go.Figure()
        for nom_col in colonnes_mesures:
            fig.add_trace(go.Box(y=dataframe[nom_col], name=nom_col, boxmean=True))

        fig.update_layout(
            title="Distribution des mesures (boxplot) - bornes IQR visibles",
            yaxis_title="Valeur",
            template="plotly_white",
        )

        return {"success": True, "html": fig.to_html(full_html=False, include_plotlyjs="cdn")}

    except Exception as e:
        return {"success": False, "erreur": f"Erreur lors de la generation du boxplot : {str(e)}"}


def generer_graphique_evolution(comparaisons: dict) -> dict:
    """
    Genere un graphique en barres groupees comparant la periode
    precedente et la periode actuelle, pour chaque mesure.

    Utilise un axe Y secondaire pour les mesures dont l'echelle est
    tres differente des autres (ex: Volume vs prix), pour eviter
    qu'une mesure a grande echelle n'ecrase visuellement les autres.
    """
    try:
        if not comparaisons:
            return {"success": False, "erreur": "Aucune comparaison de periodes disponible."}

        noms_mesures = list(comparaisons.keys())
        valeurs_actuelles = {m: comparaisons[m]["valeur_actuelle"] for m in noms_mesures}

        toutes_valeurs = list(valeurs_actuelles.values())
        mediane_globale = pd.Series(toutes_valeurs).median()

        mesures_grande_echelle = [
            m for m in noms_mesures
            if mediane_globale > 0 and abs(valeurs_actuelles[m]) > 10 * mediane_globale
        ]
        mesures_echelle_normale = [m for m in noms_mesures if m not in mesures_grande_echelle]

        fig = go.Figure()

        if mesures_echelle_normale:
            fig.add_trace(go.Bar(
                name="Periode precedente",
                x=mesures_echelle_normale,
                y=[comparaisons[m]["valeur_precedente"] for m in mesures_echelle_normale],
                marker_color="#BDC3C7",
                yaxis="y1",
            ))
            fig.add_trace(go.Bar(
                name="Periode actuelle",
                x=mesures_echelle_normale,
                y=[comparaisons[m]["valeur_actuelle"] for m in mesures_echelle_normale],
                marker_color=[
                    "#2ECC71" if comparaisons[m]["tendance"] == "hausse"
                    else "#E74C3C" if comparaisons[m]["tendance"] == "baisse"
                    else "#95A5A6"
                    for m in mesures_echelle_normale
                ],
                yaxis="y1",
            ))

        if mesures_grande_echelle:
            fig.add_trace(go.Bar(
                name="Periode precedente (echelle secondaire)",
                x=mesures_grande_echelle,
                y=[comparaisons[m]["valeur_precedente"] for m in mesures_grande_echelle],
                marker_color="#7F8C8D",
                yaxis="y2",
            ))
            fig.add_trace(go.Bar(
                name="Periode actuelle (echelle secondaire)",
                x=mesures_grande_echelle,
                y=[comparaisons[m]["valeur_actuelle"] for m in mesures_grande_echelle],
                marker_color=[
                    "#27AE60" if comparaisons[m]["tendance"] == "hausse"
                    else "#C0392B" if comparaisons[m]["tendance"] == "baisse"
                    else "#7F8C8D"
                    for m in mesures_grande_echelle
                ],
                yaxis="y2",
            ))

        granularite = next(iter(comparaisons.values()))["granularite"]

        layout_config = {
            "title": f"Evolution par {granularite} : periode precedente vs actuelle",
            "barmode": "group",
            "template": "plotly_white",
            "yaxis": {"title": "Valeur (echelle normale)"},
        }

        if mesures_grande_echelle:
            layout_config["yaxis2"] = {
                "title": "Valeur (echelle secondaire)",
                "overlaying": "y",
                "side": "right",
            }

        fig.update_layout(**layout_config)

        return {"success": True, "html": fig.to_html(full_html=False, include_plotlyjs="cdn")}

    except Exception as e:
        return {"success": False, "erreur": f"Erreur lors de la generation du graphique d'evolution : {str(e)}"}


def generer_jauge_kpi(valeur: float, seuil: float, nom_kpi: str, sens_positif: str = "haut") -> dict:
    """
    Genere une jauge (gauge chart) pour un KPI precis, comparee a un seuil.
    """
    try:
        if sens_positif == "haut":
            couleur_barre = "#2ECC71" if valeur >= seuil else "#E74C3C"
        else:
            couleur_barre = "#2ECC71" if valeur <= seuil else "#E74C3C"

        valeur_max = max(valeur, seuil) * 1.3

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=valeur,
            delta={"reference": seuil},
            title={"text": nom_kpi},
            gauge={
                "axis": {"range": [0, valeur_max]},
                "bar": {"color": couleur_barre},
                "threshold": {
                    "line": {"color": "black", "width": 3},
                    "thickness": 0.8,
                    "value": seuil,
                },
            },
        ))
        fig.update_layout(template="plotly_white")

        return {"success": True, "html": fig.to_html(full_html=False, include_plotlyjs="cdn")}

    except Exception as e:
        return {"success": False, "erreur": f"Erreur lors de la generation de la jauge : {str(e)}"}