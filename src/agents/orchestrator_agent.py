"""
Agent Orchestrateur : septieme et dernier agent du pipeline.

Ne prend aucune decision metier lui-meme - son role est de piloter
l'enchainement complet des 6 autres agents, de gerer les erreurs a
chaque etape, et de retourner un etat complet de l'execution.

Contrairement aux autres agents, celui-ci n'est PAS pilote par un LLM :
l'enchainement des etapes est fixe et connu a l'avance (Ingestion ->
Preparation -> KPI -> Dashboard -> Redaction -> Publication), donc un
simple code Python deterministe suffit - pas besoin de "decision" IA
pour savoir quel agent vient apres lequel.
"""

from src.mcp_server.server import appeler_outil
from src.agents.dashboard_agent import executer_agent_dashboard
from src.agents.reporting_agent import executer_agent_reporting
from src.agents.publication_agent import executer_agent_publication


def executer_pipeline_complet(chemin_fichier: str, validation_humaine: bool = True) -> dict:
    """
    Execute le pipeline complet de bout en bout, en gerant les erreurs
    a chaque etape.

    Retourne un etat complet avec le statut de chaque etape et les
    artefacts produits (ou un message d'erreur si une etape echoue).
    """
    etat = {
        "etapes": {},
        "success": False,
    }

    # --- ETAPE 1 : Ingestion ---
    print("=" * 60)
    print("ETAPE 1/6 : Ingestion")
    print("=" * 60)

    resultat_ingestion = appeler_outil(
        nom_agent="agent_ingestion", nom_outil="load_dataset",
        chemin_fichier=chemin_fichier,
    )
    if not resultat_ingestion.get("success"):
        etat["etapes"]["ingestion"] = {"success": False, "erreur": resultat_ingestion.get("erreur")}
        etat["erreur_bloquante"] = f"Echec a l'ingestion : {resultat_ingestion.get('erreur')}"
        return etat

    df = resultat_ingestion["dataframe"]
    etat["etapes"]["ingestion"] = {"success": True, "nb_lignes": resultat_ingestion["nb_lignes"]}
    print(f"OK - {resultat_ingestion['nb_lignes']} lignes chargees.\n")

    # --- ETAPE 2 : Preparation (profilage + nettoyage) ---
    print("=" * 60)
    print("ETAPE 2/6 : Preparation")
    print("=" * 60)

    resultat_profil = appeler_outil(nom_agent="agent_preparation", nom_outil="profile_dataset", dataframe=df)
    if not resultat_profil.get("success"):
        etat["etapes"]["preparation"] = {"success": False, "erreur": resultat_profil.get("erreur")}
        etat["erreur_bloquante"] = f"Echec au profilage : {resultat_profil.get('erreur')}"
        return etat

    profil = resultat_profil["profil"]

    resultat_nettoyage = appeler_outil(nom_agent="agent_preparation", nom_outil="clean_dataset",
                                         dataframe=df, profil=profil)
    if resultat_nettoyage.get("success"):
        df = resultat_nettoyage["dataframe_propre"]

    etat["etapes"]["preparation"] = {"success": True}
    print("OK - dataset profile et nettoye.\n")

    # --- ETAPE 3 : KPI (indicateurs, anomalies, comparaison de periodes) ---
    print("=" * 60)
    print("ETAPE 3/6 : KPI")
    print("=" * 60)

    resultat_kpis = appeler_outil(nom_agent="agent_kpi", nom_outil="compute_kpis", dataframe=df, profil=profil)
    if not resultat_kpis.get("success"):
        etat["etapes"]["kpi"] = {"success": False, "erreur": resultat_kpis.get("erreur")}
        etat["erreur_bloquante"] = f"Echec au calcul des KPIs : {resultat_kpis.get('erreur')}"
        return etat
    kpis = resultat_kpis["kpis"]

    resultat_anomalies = appeler_outil(nom_agent="agent_kpi", nom_outil="detect_anomalies",
                                         dataframe=df, profil=profil)
    anomalies = resultat_anomalies.get("anomalies", {})

    resultat_comparaisons = appeler_outil(nom_agent="agent_kpi", nom_outil="compare_periods",
                                            dataframe=df, profil=profil)
    comparaisons = resultat_comparaisons.get("comparaisons", {})

    etat["etapes"]["kpi"] = {"success": True, "nb_kpis": len(kpis)}
    print(f"OK - {len(kpis)} KPIs calcules.\n")

    # --- ETAPE 4 : Tableau de bord (agent LLM) ---
    print("=" * 60)
    print("ETAPE 4/6 : Tableau de bord")
    print("=" * 60)

    mission_dashboard = (
        f"Genere les graphiques pertinents. Les KPIs disponibles pour "
        f"generate_waterfall_chart sont exactement : {list(kpis.keys())}."
    )
    resultat_dashboard = executer_agent_dashboard(
        mission_dashboard, dataframe=df, profil=profil, kpis=kpis, comparaisons=comparaisons,
    )
    graphiques_html = resultat_dashboard["graphiques"]

    etat["etapes"]["dashboard"] = {"success": True, "nb_graphiques": len(graphiques_html)}
    print(f"OK - {len(graphiques_html)} graphiques generes.\n")

    # --- ETAPE 5 : Redaction (agent LLM + verification + validation humaine) ---
    print("=" * 60)
    print("ETAPE 5/6 : Redaction")
    print("=" * 60)

    resultat_redaction = executer_agent_reporting(
        kpis, anomalies, comparaisons, validation_humaine=validation_humaine,
    )

    etat["etapes"]["redaction"] = {
        "success": True,
        "verdict": resultat_redaction["verification"]["verdict"],
        "valide_par_humain": resultat_redaction["valide_par_humain"],
    }
    print(f"OK - verdict : {resultat_redaction['verification']['verdict']}.\n")

    # --- ETAPE 6 : Publication ---
    print("=" * 60)
    print("ETAPE 6/6 : Publication")
    print("=" * 60)

    resultat_publication = executer_agent_publication(
        dataframe=df,
        graphiques_html=graphiques_html,
        commentaire=resultat_redaction["texte_final"],
        verification=resultat_redaction["verification"],
        kpis=kpis,
    )

    etat["etapes"]["publication"] = {"success": True, "chemin_rapport": resultat_publication["chemin_rapport"]}
    print(f"OK - rapport final : {resultat_publication['chemin_rapport']}\n")

    # --- Bilan final ---
    etat["success"] = True
    etat["chemin_rapport_final"] = resultat_publication["chemin_rapport"]
    etat["chemin_export_donnees"] = resultat_publication["chemin_export_donnees"]
    etat["chemin_export_kpis"] = resultat_publication["chemin_export_kpis"]

    print("=" * 60)
    print("PIPELINE COMPLET TERMINE AVEC SUCCES")
    print("=" * 60)

    return etat