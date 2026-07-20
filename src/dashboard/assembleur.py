"""
Assemblage de tous les graphiques generes en un seul dashboard HTML.
"""

from datetime import datetime


def assembler_dashboard(graphiques_html: dict, titre: str = "Dashboard - Analyse decisionnelle") -> str:
    """
    Assemble plusieurs graphiques Plotly (deja en HTML) en une seule
    page HTML complete, avec une mise en page verticale simple.

    Parametres :
        graphiques_html (dict) : {nom_outil: html_du_graphique}
        titre (str)             : titre affiche en haut du dashboard

    Retourne le HTML complet de la page (string).
    """
    date_generation = datetime.now().strftime("%d/%m/%Y a %H:%M")

    noms_lisibles = {
        "generate_choropleth_map": "Carte mondiale",
        "generate_time_series": "Evolution dans le temps",
        "generate_radar_chart": "Vue d'ensemble (radar)",
        "generate_waterfall_chart": "Decomposition de l'evolution",
        "generate_correlation_heatmap": "Correlations entre mesures",
    }

    sections_html = ""
    for nom_outil, html_graphique in graphiques_html.items():
        titre_section = noms_lisibles.get(nom_outil, nom_outil)
        sections_html += f"""
        <div class="section-graphique">
            <h2>{titre_section}</h2>
            {html_graphique}
        </div>
        """

    page_complete = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>{titre}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #F5F6FA;
                margin: 0;
                padding: 20px;
            }}
            .en-tete {{
                background-color: #1F6F4E;
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .en-tete h1 {{
                margin: 0;
            }}
            .en-tete p {{
                margin: 5px 0 0 0;
                opacity: 0.9;
            }}
            .section-graphique {{
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .section-graphique h2 {{
                margin-top: 0;
                color: #333;
                font-size: 18px;
                border-bottom: 2px solid #1F6F4E;
                padding-bottom: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="en-tete">
            <h1>{titre}</h1>
            <p>Genere le {date_generation}</p>
        </div>
        {sections_html}
    </body>
    </html>
    """

    return page_complete

def assembler_rapport_complet(graphiques_html: dict, commentaire: str,
                                verification: dict, titre: str = "Rapport d'analyse") -> str:
    """
    Assemble le dashboard complet (graphiques + commentaire + badge de
    verification) en une seule page HTML finale.
    """
    from datetime import datetime
    date_generation = datetime.now().strftime("%d/%m/%Y a %H:%M")

    noms_lisibles = {
        "generate_choropleth_map": "Carte mondiale",
        "generate_time_series": "Evolution dans le temps",
        "generate_radar_chart": "Vue d'ensemble (radar)",
        "generate_waterfall_chart": "Decomposition de l'evolution",
        "generate_correlation_heatmap": "Correlations entre mesures",
    }

    couleurs_verdict = {
        "verifie": "#2ECC71",
        "partiel": "#F39C12",
        "non_verifie": "#E74C3C",
    }
    couleur_badge = couleurs_verdict.get(verification["verdict"], "#95A5A6")

    commentaire_html = commentaire.replace("\n", "<br>")

    sections_graphiques = ""
    for nom_outil, html_graphique in graphiques_html.items():
        titre_section = noms_lisibles.get(nom_outil, nom_outil)
        sections_graphiques += f"""
        <div class="section-graphique">
            <h2>{titre_section}</h2>
            {html_graphique}
        </div>
        """

    page_complete = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>{titre}</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #F5F6FA; margin: 0; padding: 20px; }}
            .en-tete {{ background-color: #1F6F4E; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .en-tete h1 {{ margin: 0; }}
            .en-tete p {{ margin: 5px 0 0 0; opacity: 0.9; }}
            .section-commentaire {{ background-color: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; color: white; font-size: 12px; font-weight: bold; background-color: {couleur_badge}; margin-bottom: 10px; }}
            .section-graphique {{ background-color: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .section-graphique h2 {{ margin-top: 0; color: #333; font-size: 18px; border-bottom: 2px solid #1F6F4E; padding-bottom: 8px; }}
        </style>
    </head>
    <body>
        <div class="en-tete">
            <h1>{titre}</h1>
            <p>Genere le {date_generation}</p>
        </div>
        <div class="section-commentaire">
            <span class="badge">Verdict : {verification['verdict'].upper()} ({verification['nb_nombres_verifies']}/{verification['nb_nombres_cites']} chiffres verifies)</span>
            <h2>Commentaire d'analyse</h2>
            <p>{commentaire_html}</p>
        </div>
        {sections_graphiques}
    </body>
    </html>
    """

    return page_complete