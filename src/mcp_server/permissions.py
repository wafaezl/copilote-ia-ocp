"""
Table des permissions du serveur MCP.

Definit precisement quel agent a le droit d'appeler quel outil.
Principe applique : moindre privilege - un agent ne peut utiliser
que les outils strictement necessaires a son role.

Toute tentative d'appel a un outil non autorise doit etre refusee
par le serveur (voir server.py).
"""

# Table des permissions : nom de l'agent -> liste des outils autorises
PERMISSIONS = {
    "agent_ingestion": ["load_dataset"],
    "agent_preparation": ["profile_dataset", "clean_dataset"],
    "agent_kpi": ["compute_kpis", "detect_anomalies", "compare_periods"],
    "agent_dashboard": [
        "generate_choropleth_map", "generate_time_series",
        "generate_radar_chart", "generate_waterfall_chart", "generate_correlation_heatmap",
    ],
}


def est_autorise(nom_agent: str, nom_outil: str) -> bool:
    """
    Verifie si un agent a le droit d'appeler un outil precis.

    Retourne True si autorise, False sinon (y compris si l'agent
    n'existe pas dans la table des permissions).
    """
    outils_autorises = PERMISSIONS.get(nom_agent, [])
    return nom_outil in outils_autorises


def lister_permissions(nom_agent: str) -> list:
    """
    Retourne la liste des outils autorises pour un agent donne.
    Utile pour du debogage ou pour afficher les droits d'un agent.
    """
    return PERMISSIONS.get(nom_agent, [])