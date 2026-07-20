"""
Agent Redaction : sixieme agent du pipeline.

Redige un commentaire d'analyse en francais a partir des KPIs, anomalies
et comparaisons de periodes deja calcules. Deux garde-fous appliques :

1. Verification anti-hallucination : chaque nombre cite est controle
   contre les vraies valeurs calculees (src/core/validator.py).
2. Human-in-the-loop : le texte doit etre valide (ou modifie) par un
   humain avant d'etre considere comme final.
"""

from src.llm.groq_client import get_llm_client, get_default_model
from src.core.validator import verifier_texte


NOM_AGENT = "agent_reporting"

SYSTEM_PROMPT = """Tu es l'Agent Redaction d'un systeme d'analyse de donnees.
Ta mission est de rediger un commentaire d'analyse clair et concis en francais,
a partir des indicateurs (KPIs), anomalies et comparaisons de periodes fournis.

Regles strictes :
- Cite UNIQUEMENT des chiffres qui apparaissent explicitement dans les donnees fournies.
- N'invente JAMAIS un chiffre, un pourcentage ou une tendance qui n'est pas dans les donnees.
- Reste factuelle : decris ce qui est observe, sans exagerer les resultats.
- Structure ta reponse en 3 parties courtes : indicateurs cles, anomalies a surveiller,
  evolution par rapport a la periode precedente."""


def generer_commentaire(kpis: dict, anomalies: dict, comparaisons: dict) -> str:
    """
    Genere le commentaire d'analyse via le LLM, a partir des resultats
    deja calcules (pas d'appel d'outil ici : simple generation de texte).
    """
    client = get_llm_client()
    modele = get_default_model()

    contexte = f"""
Voici les resultats calcules pour ce dataset :

KPIs : {kpis}

Anomalies detectees : {anomalies}

Comparaison de periodes : {comparaisons}

Redige le commentaire d'analyse en respectant les regles donnees.
"""

    reponse = client.chat.completions.create(
        model=modele,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": contexte},
        ],
    )

    return reponse.choices[0].message.content


def executer_agent_reporting(kpis: dict, anomalies: dict, comparaisons: dict,
                               validation_humaine: bool = True) -> dict:
    """
    Lance l'Agent Redaction complet :
        1. Genere le commentaire
        2. Verifie les chiffres cites (anti-hallucination)
        3. Demande une validation humaine avant de considerer le texte final
           (sauf si validation_humaine=False, utile pour des tests automatises)

    Retourne :
        - texte_final : le commentaire (valide ou modifie par l'humain)
        - verification : le resultat de la verification anti-hallucination
        - valide_par_humain : bool
    """
    texte_genere = generer_commentaire(kpis, anomalies, comparaisons)

    verification = verifier_texte(texte_genere, kpis=kpis, anomalies=anomalies,
                                    comparaisons=comparaisons)

    print("\n=== Commentaire genere ===")
    print(texte_genere)
    print(f"\n=== Verification anti-hallucination ===")
    print(f"Verdict : {verification['verdict'].upper()}")
    print(f"Nombres cites : {verification['nb_nombres_cites']}, "
          f"verifies : {verification['nb_nombres_verifies']}")
    if verification["nombres_non_trouves"]:
        print(f"Nombres suspects (non retrouves) : {verification['nombres_non_trouves']}")

    texte_final = texte_genere
    valide_par_humain = False

    if validation_humaine:
        print("\n=== Validation humaine requise ===")
        reponse = input("Valider ce texte tel quel ? (o = oui / n = reecrire manuellement) : ").strip().lower()

        if reponse == "o":
            valide_par_humain = True
        else:
            print("Entrez le texte corrige (terminez par une ligne vide) :")
            lignes = []
            while True:
                ligne = input()
                if ligne == "":
                    break
                lignes.append(ligne)
            texte_final = "\n".join(lignes)
            valide_par_humain = True

    return {
        "texte_final": texte_final,
        "verification": verification,
        "valide_par_humain": valide_par_humain,
    }