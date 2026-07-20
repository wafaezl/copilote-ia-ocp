"""
Verification anti-hallucination : controle que chaque nombre cite dans
un texte genere par le LLM correspond bien a une valeur reellement
calculee (KPIs, anomalies, comparaisons de periodes).

Gere le format francais des nombres (espace = milliers, virgule = decimale).
"""

import re


def extraire_nombres(texte: str) -> list:
    """
    Extrait tous les nombres presents dans un texte, en gerant a la fois
    le format francais (espace = milliers, virgule = decimale) et le
    format anglais (virgule = milliers, point = decimale).
    """
    motif = r"-?\d[\d\s.,]*"
    trouves = re.findall(motif, texte)

    nombres = []
    for t in trouves:
        t = t.strip()
        if not t:
            continue

        t_nettoye = t.replace(" ", "")

        if "," in t_nettoye and "." in t_nettoye:
            t_nettoye = t_nettoye.replace(".", "").replace(",", ".")
        elif "," in t_nettoye:
            t_nettoye = t_nettoye.replace(",", ".")

        try:
            valeur = float(t_nettoye)
            nombres.append(valeur)
        except ValueError:
            continue

    return nombres


def collecter_valeurs_reelles(kpis: dict = None, anomalies: dict = None,
                                comparaisons: dict = None) -> set:
    """
    Rassemble toutes les vraies valeurs numeriques calculees par le
    systeme (KPIs, anomalies, comparaisons), pour servir de reference
    lors de la verification.
    """
    valeurs = set()

    if kpis:
        for infos in kpis.values():
            for cle in ("total", "moyenne", "min", "max"):
                if cle in infos:
                    valeurs.add(round(infos[cle], 1))
                    valeurs.add(round(infos[cle]))

    if anomalies:
        for infos in anomalies.values():
            for cle in ("nb_anomalies", "pct_anomalies", "borne_basse", "borne_haute"):
                if cle in infos:
                    valeurs.add(round(infos[cle], 1))
                    valeurs.add(round(infos[cle]))

    if comparaisons:
        for infos in comparaisons.values():
            for cle in ("valeur_actuelle", "valeur_precedente", "evolution_pct"):
                if infos.get(cle) is not None:
                    valeurs.add(round(infos[cle], 1))
                    valeurs.add(round(infos[cle]))

    return valeurs


def verifier_texte(texte: str, kpis: dict = None, anomalies: dict = None,
                     comparaisons: dict = None, tolerance: float = 0.5) -> dict:
    """
    Verifie que les nombres cites dans le texte correspondent a des
    valeurs reellement calculees, avec une tolerance pour les arrondis.
    """
    nombres_cites = extraire_nombres(texte)

    # Ignore les tres petits nombres ET les annees (2000-2099)
    nombres_cites = [
        n for n in nombres_cites
        if abs(n) >= 1 and not (2000 <= n <= 2099)
    ]

    if not nombres_cites:
        return {
            "verdict": "verifie",
            "nb_nombres_cites": 0,
            "nb_nombres_verifies": 0,
            "nombres_non_trouves": [],
        }

    valeurs_reelles = collecter_valeurs_reelles(kpis, anomalies, comparaisons)

    nombres_non_trouves = []
    nb_verifies = 0

    for nombre in nombres_cites:
        trouve = any(
            abs(nombre - reel) <= tolerance or abs(abs(nombre) - abs(reel)) <= tolerance
            for reel in valeurs_reelles
        )
        if trouve:
            nb_verifies += 1
        else:
            nombres_non_trouves.append(nombre)

    ratio = nb_verifies / len(nombres_cites)

    if ratio == 1.0:
        verdict = "verifie"
    elif ratio >= 0.5:
        verdict = "partiel"
    else:
        verdict = "non_verifie"

    return {
        "verdict": verdict,
        "nb_nombres_cites": len(nombres_cites),
        "nb_nombres_verifies": nb_verifies,
        "nombres_non_trouves": nombres_non_trouves,
    }