from balise.registry import CHECKS, Mode, Tier, by_id, module_checks


def test_check_ids_are_unique():
    ids = [c.id for c in CHECKS]
    assert len(ids) == len(set(ids))


def test_every_check_has_a_legal_hook_and_titles():
    for check in CHECKS:
        assert check.legal_hook.strip(), check.id
        assert check.title_fr.strip(), check.id
        assert check.title_en.strip(), check.id


def test_contested_checks_are_never_statute_tier_without_note():
    for check in CHECKS:
        if check.contested:
            assert check.note.strip(), f"{check.id} contested but unexplained"


def test_module_split_matches_modes():
    for check in module_checks("A"):
        assert check.mode in (Mode.DETERMINISTIC, Mode.SEMANTIC)
    for check in module_checks("B"):
        assert check.mode is Mode.INTAKE


def test_no_72_hour_myth_encoded_anywhere():
    for check in CHECKS:
        for text in (check.title_fr, check.title_en, check.legal_hook):
            assert "72" not in text, f"{check.id}: 72-hour GDPR myth must not be encoded"


def test_by_id_round_trip():
    assert by_id("B6").tier is Tier.STATUTE
    assert by_id("A5").contested is True


def test_client_copy_covers_every_check():
    from balise.advice import CLIENT_COPY
    # exact two-way match: a check without copy silently vanishes from the
    # sommaire and exec opener; orphaned copy means a check was removed
    # without cleaning its owner-voice text
    assert set(CLIENT_COPY) == {c.id for c in CHECKS}
    for check in CHECKS:
        copy = CLIENT_COPY.get(check.id)
        assert copy is not None, f"{check.id} has no client copy"
        for fieldname in ("plain_fr", "plain_en", "risk_fr", "risk_en",
                          "action_fr", "action_en"):
            assert getattr(copy, fieldname).strip(), f"{check.id}.{fieldname} empty"
        assert copy.priority in (1, 2, 3), check.id
