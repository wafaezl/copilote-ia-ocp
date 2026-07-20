"""
Agent Publication : assemble le dashboard et le commentaire en un
rapport final, et exporte les donnees preparees pour Power BI.
"""

import os
from datetime import datetime
from src.dashboard.assembleur import assembler_rapport_complet


def executer_agent_publication(dataframe, graphiques_html: dict, commentaire: str,
                                 verification: dict, kpis: dict,
                                 dossier_sortie: str = "runs") -> dict:
    """
    Assemble tous les elements en un rapport final, et exporte les
    donnees pour Power BI.

    Retourne les chemins des fichiers produits.
    """
    os.makedirs(dossier_sortie, exist_ok=True)
    os.makedirs("data/exports", exist_ok=True)

    # --- 1. Rapport HTML complet ---
    rapport_html = assembler_rapport_complet(
        graphiques_html, commentaire, verification,
        titre="Copilote IA - Rapport d'analyse decisionnelle"
    )
    chemin_rapport = os.path.join(dossier_sortie, "rapport_final.html")
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(rapport_html)

    # --- 2. Export des donnees nettoyees pour Power BI ---
    horodatage = datetime.now().strftime("%Y%m%d_%H%M")
    chemin_export = f"data/exports/donnees_pour_powerbi_{horodatage}.csv"
    dataframe.to_csv(chemin_export, index=False)

    # --- 3. Export des KPIs en CSV (pratique pour Power BI aussi) ---
    import pandas as pd
    kpis_df = pd.DataFrame(kpis).T.reset_index().rename(columns={"index": "mesure"})
    chemin_export_kpis = f"data/exports/kpis_{horodatage}.csv"
    kpis_df.to_csv(chemin_export_kpis, index=False)

    print(f"Rapport final : {chemin_rapport}")
    print(f"Donnees exportees pour Power BI : {chemin_export}")
    print(f"KPIs exportes pour Power BI : {chemin_export_kpis}")

    return {
        "success": True,
        "chemin_rapport": chemin_rapport,
        "chemin_export_donnees": chemin_export,
        "chemin_export_kpis": chemin_export_kpis,
    }