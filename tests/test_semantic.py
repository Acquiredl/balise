from balise.registry import Status
from balise.semantic import EngineResult, _visible_text, verify_quotes


def test_corpus_preserves_form_control_semantics():
    html = ('<form><label>Téléphone'
            '<input type="tel" name="telephone" required></label>'
            '<input type="hidden" name="csrf" value="x">'
            '<textarea name="message" placeholder="Votre question"></textarea>'
            '</form><style>@media print { body { color: black } }</style>')
    text = _visible_text(html)
    assert "input name=telephone type=tel required" in text
    assert "textarea name=message placeholder=Votre question" in text
    assert "csrf" not in text          # hidden inputs are noise, dropped
    assert "@media" not in text       # styles still stripped


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
