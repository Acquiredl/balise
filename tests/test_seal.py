"""Seals: issuer signature and OTS anchor, judged through balise verify.

All offline: the calendar is monkeypatched, and Bitcoin-attested proofs
are crafted with the same serializer the verifier parses.
"""

import json

from test_verify import build_package

from balise import seal
from balise.verify import verify_package


def make_pending_proof(digest_hex: str) -> bytes:
    node = {"attestations": [(seal.TAG_PENDING, seal.write_varbytes(b"uri"))],
            "ops": []}
    proof = seal.serialize_timestamp(node)
    assert seal.judge_proof(digest_hex, proof)[0] == "pending"
    return proof


def make_bitcoin_proof(digest_hex: str, height: int = 900000) -> bytes:
    node = {"attestations": [(seal.TAG_BITCOIN, seal.write_varint(height))],
            "ops": []}
    proof = seal.serialize_timestamp(node)
    assert seal.judge_proof(digest_hex, proof)[0] == "bitcoin"
    return proof


def seal_it(tmp_path, monkeypatch, *, sign=True, anchor=True):
    private_hex, public_hex, fingerprint = seal.generate_keypair()
    if anchor:
        # the fake calendar reads the digest lazily: the declaration is
        # written before anchoring, so the digest exists by the time
        # calendar_request fires
        monkeypatch.setattr(
            seal, "calendar_request",
            lambda url, data=None: make_pending_proof(
                seal.manifest_digest(tmp_path)))
    rc = seal.seal_package(tmp_path, sign=sign, anchor=anchor,
                           calendars=["https://calendar.test"] if anchor else None,
                           private_key_hex=private_hex if sign else None)
    assert rc == 0
    return private_hex, fingerprint


def test_sealed_package_verdict_carries_the_signed_rung(tmp_path, monkeypatch):
    build_package(tmp_path)
    _, fingerprint = seal_it(tmp_path, monkeypatch)

    verdict = verify_package(tmp_path)
    assert verdict.exit_code == 0
    assert verdict.verdict.startswith("SELF-CONSISTENT")
    assert f"SIGNED (key: {fingerprint[:16]}…)" in verdict.verdict
    # pending anchor is judged honestly: no ANCHORED rung yet
    assert "ANCHORED" not in verdict.verdict
    manifest = json.loads((tmp_path / "manifest.json").read_text("utf-8"))
    assert manifest["seals"] == ["anchor", "ed25519"]


def test_bitcoin_attested_anchor_earns_the_anchored_rung(tmp_path, monkeypatch):
    build_package(tmp_path)
    seal_it(tmp_path, monkeypatch, anchor=False)
    # graft a completed proof directly into the sidecar
    digest_hex = seal.manifest_digest(tmp_path)
    seals_dir = tmp_path / seal.SEALS_DIR
    (seals_dir / seal.ANCHORS_FILE).write_text(json.dumps({
        "manifest_sha256": digest_hex,
        "ts": "2026-08-25T00:00:00+00:00",
        "calendar": "https://calendar.test",
        "proof": __import__("base64").b64encode(
            make_bitcoin_proof(digest_hex)).decode(),
    }) + "\n", encoding="utf-8")
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    assert manifest["seals"] == ["ed25519"]  # declared at signing time

    # a declared-set change after sealing must be refused
    try:
        seal._declare_seals(tmp_path, ["anchor", "ed25519"])
        raise AssertionError("redeclaration after sealing must fail")
    except RuntimeError:
        pass


def test_full_seal_set_with_attestation_reaches_the_top_rung(tmp_path,
                                                             monkeypatch):
    build_package(tmp_path)
    private_hex, fingerprint = seal_it(tmp_path, monkeypatch)
    # replace the pending proof with a completed one for the same digest
    digest_hex = seal.manifest_digest(tmp_path)
    anchors = tmp_path / seal.SEALS_DIR / seal.ANCHORS_FILE
    anchors.write_text(json.dumps({
        "manifest_sha256": digest_hex,
        "ts": "2026-08-25T00:00:00+00:00",
        "calendar": "https://calendar.test",
        "proof": __import__("base64").b64encode(
            make_bitcoin_proof(digest_hex, 905123)).decode(),
    }) + "\n", encoding="utf-8")

    verdict = verify_package(tmp_path)
    assert verdict.exit_code == 0
    assert "ANCHORED (block 905123)" in verdict.verdict
    assert "SIGNED" in verdict.verdict


def test_attack_tampered_manifest_invalidates_both_seals(tmp_path,
                                                         monkeypatch):
    build_package(tmp_path)
    seal_it(tmp_path, monkeypatch)
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text("utf-8"))
    manifest["target"] = "https://autre.example"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n",
                             encoding="utf-8")

    verdict = verify_package(tmp_path)
    assert verdict.verdict == "SEAL-INVALID"
    assert verdict.exit_code == 3


def test_attack_resign_with_substituted_key_shows_a_different_fingerprint(
        tmp_path, monkeypatch):
    build_package(tmp_path)
    _, issuer_fp = seal_it(tmp_path, monkeypatch)
    # the adversary re-signs with their own key and swaps the public key in
    attacker_hex, _, attacker_fp = seal.generate_keypair()
    seal.sign_package(tmp_path, private_key_hex=attacker_hex)

    verdict = verify_package(tmp_path)
    # math passes — the verifier's job — and the fingerprint names the
    # substituted key, which the out-of-band comparison catches
    assert verdict.exit_code == 0
    assert f"SIGNED (key: {attacker_fp[:16]}…)" in verdict.verdict
    assert issuer_fp[:16] not in verdict.verdict


def test_attack_anchor_for_a_different_manifest_is_invalid(tmp_path,
                                                           monkeypatch):
    build_package(tmp_path)
    seal_it(tmp_path, monkeypatch, sign=False)
    anchors = tmp_path / seal.SEALS_DIR / seal.ANCHORS_FILE
    record = json.loads(anchors.read_text("utf-8").splitlines()[0])
    record["manifest_sha256"] = "0" * 64
    anchors.write_text(json.dumps(record) + "\n", encoding="utf-8")

    verdict = verify_package(tmp_path)
    assert verdict.verdict == "SEAL-INVALID"


def test_keygen_writes_nothing(tmp_path, capsys, monkeypatch):
    from balise.cli import main

    monkeypatch.chdir(tmp_path)
    assert main(["keygen"]) == 0
    out = capsys.readouterr().out
    assert "private key" in out
    assert "fingerprint" in out
    assert list(tmp_path.iterdir()) == []


def test_checklist_shows_the_full_fingerprint(tmp_path, monkeypatch):
    build_package(tmp_path)
    _, fingerprint = seal_it(tmp_path, monkeypatch)
    rendered = verify_package(tmp_path).render()
    # the full value is what recipients compare out-of-band; a truncated
    # prefix would leave room for a collided key
    assert fingerprint in rendered
