"""Seals: outer commitments applied to the manifest's shipped bytes.

Two kinds, answering orthogonal questions. The **anchor** commits the
manifest hash to Bitcoin via OpenTimestamps (free public calendar
servers fold the digest into a Merkle tree whose root lands in a
Bitcoin transaction) and says *when*: this manifest existed before
block N. The **issuer signature** (Ed25519, detached, over the manifest
file's exact bytes) says *who*: the holder of this key issued it.
Neither replaces the other — a signature has no clock and can be redone
anytime by whoever holds the key, while nobody can anchor a forgery
into the past.

The seal declaration lives in the manifest and must be complete before
the first seal is applied: adding a kind later would rewrite the
manifest's bytes and orphan every existing seal. `seal_package` therefore
declares and applies in one act; `upgrade_anchors` only ever touches the
sidecar proof file.

Key custody is the issuer's job, not this module's: the private key is
prompted for at signing time, held in memory only, and never written
anywhere by this code. See docs/SIGNING.md.

The OpenTimestamps code implements the small subset of the OTS format
that calendar proofs use — anything outside it is refused by name,
never guessed. True Bitcoin verification would need the block headers;
what offline judgment provides is the proof's internal replay and the
attested block height, put in front of the operator.
"""

from __future__ import annotations

import base64
import getpass
import hashlib
import json
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

# --- OpenTimestamps: minimal proof subset ----------------------------------

DEFAULT_CALENDARS = [
    "https://a.pool.opentimestamps.org",
    "https://b.pool.opentimestamps.org",
    "https://a.pool.eternitywall.com",
    "https://ots.btc.catallaxy.com",
]

OP_SHA256, OP_APPEND, OP_PREPEND = 0x08, 0xF0, 0xF1
ATTESTATION_MARKER = 0x00
BRANCH_MARKER = 0xFF
TAG_BITCOIN = bytes.fromhex("0588960d73d71901")
TAG_PENDING = bytes.fromhex("83dfe30d2ef90c8e")
MAX_PROOF_BYTES = 8192  # generous; real calendar proofs are a few hundred
MAX_PROOF_DEPTH = 512   # ops nest one level each; real proofs stay under ~100


class ProofError(ValueError):
    """A proof this verifier cannot judge — malformed or outside the subset."""


class ProofReader:
    """Cursor over proof bytes; every read is bounds-checked."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def byte(self) -> int:
        return self.bytes(1)[0]

    def bytes(self, count: int) -> bytes:
        if self.pos + count > len(self.data):
            raise ProofError("truncated proof")
        chunk = self.data[self.pos:self.pos + count]
        self.pos += count
        return chunk

    def varint(self) -> int:
        # Unsigned, little-endian base 128; high bit means "more".
        value = shift = 0
        while True:
            byte = self.byte()
            value |= (byte & 0x7F) << shift
            if not byte & 0x80:
                return value
            shift += 7
            if shift > 63:
                raise ProofError("varint too large")

    def varbytes(self) -> bytes:
        length = self.varint()
        if length > MAX_PROOF_BYTES:
            raise ProofError("proof field too large")
        return self.bytes(length)


def write_varint(n: int) -> bytes:
    out = bytearray()
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def write_varbytes(b: bytes) -> bytes:
    return write_varint(len(b)) + b


def parse_timestamp(reader: ProofReader, depth: int = 0) -> dict:
    """One node of the proof tree: attestations that hold at the current
    digest, plus operations that each transform it and continue into a
    child node. Wire format: every element but the last is 0xff-prefixed.

    Depth is capped: each chained op nests one level, so without a cap a
    crafted proof a few KB long could exhaust the interpreter's recursion
    limit — a crash where a verdict belongs."""
    if depth > MAX_PROOF_DEPTH:
        raise ProofError(f"proof nests deeper than {MAX_PROOF_DEPTH} operations")
    node: dict = {"attestations": [], "ops": []}
    while True:
        tag = reader.byte()
        last = tag != BRANCH_MARKER
        if not last:
            tag = reader.byte()
        if tag == ATTESTATION_MARKER:
            node["attestations"].append(
                (bytes(reader.bytes(8)), bytes(reader.varbytes()))
            )
        elif tag in (OP_APPEND, OP_PREPEND):
            arg = bytes(reader.varbytes())
            node["ops"].append((tag, arg, parse_timestamp(reader, depth + 1)))
        elif tag == OP_SHA256:
            node["ops"].append((tag, None, parse_timestamp(reader, depth + 1)))
        else:
            raise ProofError(
                f"proof uses operation 0x{tag:02x}, "
                "which this verifier does not implement"
            )
        if last:
            return node


def serialize_timestamp(node: dict) -> bytes:
    elements = []
    for tag, payload in node["attestations"]:
        elements.append(bytes([ATTESTATION_MARKER]) + tag + write_varbytes(payload))
    for op, arg, child in node["ops"]:
        piece = bytes([op])
        if arg is not None:
            piece += write_varbytes(arg)
        elements.append(piece + serialize_timestamp(child))
    if not elements:
        raise ProofError("empty proof node")
    prefixed = [bytes([BRANCH_MARKER]) + e for e in elements[:-1]]
    return b"".join(prefixed) + elements[-1]


def replay_proof(digest: bytes, node: dict, results=None) -> list[dict]:
    """Walk the proof applying each operation to the digest; collect every
    attestation together with the digest it attests to and the node holding
    it (the node reference is what upgrade splices into)."""
    if results is None:
        results = []
    for tag, payload in node["attestations"]:
        results.append(
            {"tag": tag, "payload": payload, "digest": digest, "node": node}
        )
    for op, arg, child in node["ops"]:
        if op == OP_SHA256:
            next_digest = hashlib.sha256(digest).digest()
        elif op == OP_APPEND:
            next_digest = digest + arg
        else:  # OP_PREPEND
            next_digest = arg + digest
        replay_proof(next_digest, child, results)
    return results


def bitcoin_height(payload: bytes) -> int:
    reader = ProofReader(payload)
    height = reader.varint()
    if reader.pos != len(payload):
        raise ProofError("malformed Bitcoin attestation payload")
    return height


def judge_proof(digest_hex: str, proof_bytes: bytes):
    """Replay a proof from a digest. Returns ("bitcoin", height, root),
    ("pending", commitment_hex), or raises ProofError."""
    node = parse_timestamp(ProofReader(proof_bytes))
    results = replay_proof(bytes.fromhex(digest_hex), node)
    for r in results:
        if r["tag"] == TAG_BITCOIN:
            return ("bitcoin", bitcoin_height(r["payload"]), r["digest"])
    for r in results:
        if r["tag"] == TAG_PENDING:
            return ("pending", r["digest"].hex())
    raise ProofError("proof contains no attestation this verifier can judge")


def splice_continuation(proof_bytes: bytes, digest_hex: str,
                        continuation_bytes: bytes) -> bytes:
    """Graft a calendar's completion onto the stored proof: the node holding
    the pending attestation continues with the completion's operations."""
    node = parse_timestamp(ProofReader(proof_bytes))
    continuation = parse_timestamp(ProofReader(continuation_bytes))
    for r in replay_proof(bytes.fromhex(digest_hex), node):
        if r["tag"] == TAG_PENDING:
            spot = r["node"]
            spot["attestations"] = [a for a in spot["attestations"]
                                    if a[0] != TAG_PENDING]
            spot["attestations"].extend(continuation["attestations"])
            spot["ops"].extend(continuation["ops"])
            return serialize_timestamp(node)
    raise ProofError("stored proof has no pending attestation to upgrade")


def calendar_request(url: str, data: bytes | None = None) -> bytes:
    request = urllib.request.Request(
        url, data=data,
        headers={"Accept": "application/vnd.opentimestamps.v1",
                 "User-Agent": "balise"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read(MAX_PROOF_BYTES)


# --- Package sealing -------------------------------------------------------

SEALS_DIR = "seals"
ANCHORS_FILE = "anchors.jsonl"
SIGNATURE_FILE = "manifest.sig"
PUBLIC_KEY_FILE = "public-key.txt"


def manifest_digest(package: Path) -> str:
    """SHA-256 over manifest.json's exact shipped bytes — the package's
    single sealing surface."""
    return hashlib.sha256((package / "manifest.json").read_bytes()).hexdigest()


def key_fingerprint(public_key_bytes: bytes) -> str:
    return hashlib.sha256(public_key_bytes).hexdigest()


def generate_keypair() -> tuple[str, str, str]:
    """Returns (private_hex, public_hex, fingerprint). Nothing is written
    anywhere — the caller decides where the private key lives (a password
    manager, out of the writer's reach), and this module never sees it
    again except transiently at signing time."""
    private = Ed25519PrivateKey.generate()
    private_hex = private.private_bytes_raw().hex()
    public_bytes = private.public_key().public_bytes_raw()
    return private_hex, public_bytes.hex(), key_fingerprint(public_bytes)


def _declare_seals(package: Path, kinds: list[str]) -> None:
    """Write the declared seal set into the manifest — allowed only while
    no seal exists yet, because the first applied seal freezes the bytes."""
    manifest_path = package / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("seals") == kinds:
        return
    seals_dir = package / SEALS_DIR
    if seals_dir.is_dir() and any(seals_dir.iterdir()):
        raise RuntimeError(
            "seals already applied: the manifest's declared seal set is "
            "frozen by the first seal and cannot be changed — re-run the "
            "pipeline for a fresh package if a different set is needed")
    manifest["seals"] = kinds
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")


def anchor_package(package: Path, calendars: list[str] | None = None) -> int:
    """Submit the manifest digest to OTS calendars; store pending proofs
    in the seals sidecar. Returns the number of calendars that accepted."""
    digest_hex = manifest_digest(package)
    digest = bytes.fromhex(digest_hex)
    seals_dir = package / SEALS_DIR
    seals_dir.mkdir(exist_ok=True)
    written = 0
    for calendar in (calendars or DEFAULT_CALENDARS):
        url = calendar.rstrip("/")
        try:
            proof_bytes = calendar_request(url + "/digest", data=digest)
            judge_proof(digest_hex, proof_bytes)  # refuse to store what can't replay
        except (OSError, ProofError) as exc:
            print(f"warning: calendar {url}: {exc}")
            continue
        record = {
            "manifest_sha256": digest_hex,
            "ts": datetime.now(UTC).isoformat(),
            "calendar": url,
            "proof": base64.b64encode(proof_bytes).decode("ascii"),
        }
        with (seals_dir / ANCHORS_FILE).open("a", encoding="utf-8",
                                             newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True,
                                    separators=(",", ":")) + "\n")
        written += 1
        print(f"anchored manifest {digest_hex[:12]}… via {url}")
    return written


def upgrade_anchors(package: Path) -> int:
    """Complete pending proofs once Bitcoin has them. Touches only the
    seals sidecar — the manifest's bytes are frozen. Returns the number of
    proofs still pending."""
    anchors_path = package / SEALS_DIR / ANCHORS_FILE
    if not anchors_path.is_file():
        print("no anchors to upgrade — run `balise seal` first")
        return 0
    records = [json.loads(line) for line
               in anchors_path.read_text(encoding="utf-8").splitlines()
               if line.strip()]
    completed = set()
    pending = []
    for record in records:
        try:
            verdict = judge_proof(record["manifest_sha256"],
                                  base64.b64decode(record["proof"]))
        except (ProofError, KeyError, ValueError):
            continue  # verify reports these; upgrade just skips
        key = (record["manifest_sha256"], record["calendar"])
        if verdict[0] == "bitcoin":
            completed.add(key)
        else:
            pending.append((record, verdict[1]))

    still_pending = 0
    for record, commitment_hex in pending:
        key = (record["manifest_sha256"], record["calendar"])
        if key in completed:
            continue
        url = record["calendar"].rstrip("/")
        try:
            continuation = calendar_request(f"{url}/timestamp/{commitment_hex}")
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                print(f"still pending at {url} — Bitcoin confirmation "
                      "takes a few hours")
                still_pending += 1
            else:
                print(f"warning: calendar {url}: {exc}")
            continue
        except OSError as exc:
            print(f"warning: calendar {url}: {exc}")
            continue
        try:
            upgraded = splice_continuation(
                base64.b64decode(record["proof"]),
                record["manifest_sha256"], continuation)
        except ProofError as exc:
            print(f"warning: calendar {url} sent an unusable completion: {exc}")
            continue
        with anchors_path.open("a", encoding="utf-8",
                               newline="\n") as handle:
            handle.write(json.dumps({
                "manifest_sha256": record["manifest_sha256"],
                "ts": datetime.now(UTC).isoformat(),
                "calendar": url,
                "proof": base64.b64encode(upgraded).decode("ascii"),
            }, sort_keys=True, separators=(",", ":")) + "\n")
        completed.add(key)
        print(f"upgraded: manifest {record['manifest_sha256'][:12]}… now has "
              "a Bitcoin attestation")
    return still_pending


def sign_package(package: Path, private_key_hex: str | None = None) -> str:
    """Apply the issuer signature: detached Ed25519 over the manifest's
    exact shipped bytes. The private key is prompted for when not passed,
    lives in memory only, and is never written by this code. Returns the
    key fingerprint."""
    if private_key_hex is None:
        private_key_hex = getpass.getpass(
            "issuer private key (hex, from your password manager): ")
    try:
        private = Ed25519PrivateKey.from_private_bytes(
            bytes.fromhex(private_key_hex.strip()))
    except ValueError as exc:
        raise RuntimeError(f"not a valid Ed25519 private key: {exc}") from exc
    manifest_bytes = (package / "manifest.json").read_bytes()
    signature = private.sign(manifest_bytes)
    public_bytes = private.public_key().public_bytes_raw()
    seals_dir = package / SEALS_DIR
    seals_dir.mkdir(exist_ok=True)
    (seals_dir / SIGNATURE_FILE).write_bytes(signature)
    (seals_dir / PUBLIC_KEY_FILE).write_text(public_bytes.hex() + "\n",
                                             encoding="utf-8", newline="\n")
    return key_fingerprint(public_bytes)


def seal_package(package: str | Path, *, sign: bool = True,
                 anchor: bool = True,
                 calendars: list[str] | None = None,
                 private_key_hex: str | None = None) -> int:
    """The full sealing act, in the only safe order: declare every seal
    kind first (the declaration is part of the sealed bytes), then apply
    each seal to the frozen manifest."""
    package = Path(package)
    if not (package / "manifest.json").is_file():
        print("error: no manifest.json — seal a completed package")
        return 1
    kinds = ([] if not anchor else ["anchor"]) + ([] if not sign else ["ed25519"])
    if not kinds:
        print("error: nothing to apply (both seals disabled)")
        return 1
    try:
        _declare_seals(package, kinds)
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 1
    if anchor:
        if not anchor_package(package, calendars):
            print("error: no calendar accepted the digest — manifest not "
                  "anchored (the declaration stands; retry `balise seal`)")
            return 1
        print("anchor is pending — run `balise seal --upgrade` after a few "
              "hours to complete it")
    if sign:
        try:
            fingerprint = sign_package(package, private_key_hex)
        except RuntimeError as exc:
            print(f"error: {exc}")
            return 1
        print(f"signed (key: {fingerprint[:16]}…) — recipients compare this "
              "fingerprint against docs/SIGNING.md")
    return 0


# --- Seal judgment (used by verify) ----------------------------------------

def judge_signature(package: Path) -> tuple[str, str]:
    """Returns (state, detail): ("missing", why), ("invalid", why), or
    ("valid", fingerprint). The fingerprint names the key, never the
    keyholder — comparing it against an out-of-band channel is the
    recipient's job, not this code's."""
    seals_dir = package / SEALS_DIR
    sig_path = seals_dir / SIGNATURE_FILE
    key_path = seals_dir / PUBLIC_KEY_FILE
    if not sig_path.is_file() or not key_path.is_file():
        return ("missing", "signature or public key file absent")
    try:
        public_bytes = bytes.fromhex(
            key_path.read_text(encoding="utf-8").strip())
        public = Ed25519PublicKey.from_public_bytes(public_bytes)
        public.verify(sig_path.read_bytes(),
                      (package / "manifest.json").read_bytes())
    except InvalidSignature:
        return ("invalid", "signature does not verify over the manifest")
    except (OSError, ValueError) as exc:
        return ("invalid", f"unusable signature material: {exc}")
    return ("valid", key_fingerprint(public_bytes))


def judge_anchors(package: Path) -> tuple[str, str]:
    """Returns (state, detail): ("missing", why), ("invalid", why),
    ("pending", detail), or ("bitcoin", "block N")."""
    anchors_path = package / SEALS_DIR / ANCHORS_FILE
    if not anchors_path.is_file():
        return ("missing", "no anchors file")
    digest_hex = manifest_digest(package)
    best: tuple[str, str] | None = None
    for line in anchors_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            if record.get("manifest_sha256") != digest_hex:
                best = best or ("invalid",
                                "anchor commits a different manifest")
                continue
            verdict = judge_proof(digest_hex,
                                  base64.b64decode(record["proof"]))
        except (ValueError, KeyError, ProofError) as exc:
            best = best or ("invalid", f"unjudgeable proof: {exc}")
            continue
        if verdict[0] == "bitcoin":
            return ("bitcoin", f"block {verdict[1]}")
        best = ("pending", "submitted; Bitcoin attestation not yet grafted")
    return best or ("invalid", "no judgeable anchor records")
