from balise.registry import Status
from balise.semantic import EngineResult, verify_quotes


def test_fabricated_quotes_are_dropped_and_disclosed():
    corpus = ("[page: https://x.example/politique]\n"
              "Nous recueillons votre nom et votre courriel pour traiter "
              "vos commandes. Vous pouvez retirer votre consentement.")
    result = EngineResult(
        Status.PARTIAL,
        "Policy covers purposes but not third parties.",
        "La politique couvre les fins mais pas les tiers.",
        ["Nous recueillons votre nom et votre courriel",
         "Vos données sont vendues à des partenaires"])   # fabricated
    verified = verify_quotes(result, corpus)
    assert verified.evidence == ["Nous recueillons votre nom et votre courriel"]
    assert "1 quote(s)" in verified.reasoning
    assert "1 citation(s)" in verified.reasoning_fr
    assert verified.status is Status.PARTIAL


def test_real_quotes_survive_typographic_and_case_differences():
    corpus = "L’entreprise conserve les renseignements  pendant cinq ans."
    result = EngineResult(
        Status.MET, "r", "r",
        ["l'entreprise conserve les renseignements pendant cinq ans"])
    verified = verify_quotes(result, corpus)
    assert verified.evidence == result.evidence
    assert verified.reasoning == "r"          # nothing dropped, nothing added
