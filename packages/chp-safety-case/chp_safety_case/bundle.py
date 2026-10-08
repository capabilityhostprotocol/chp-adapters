"""The portable `.chpsafety` Safety Case bundle: build + offline verify.

A bundle is a zip of `case.json` + named artifacts + a `manifest.json` (sha256 of every
file) + a `signature.json` (Ed25519 over the manifest). Verification recomputes every
digest (tamper-evidence), checks the signature, and — given trusted keys — whether the
signer is one you trust. Stdlib + `cryptography` only: it verifies offline, with no network
and no trust in the producer.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(data: bytes) -> str:
    return "sha256:" + sha256(data).hexdigest()


@dataclass(frozen=True)
class BundleVerification:
    manifest_valid: bool
    signature_valid: bool
    signer_trusted: bool
    errors: tuple[str, ...]

    @property
    def integrity_valid(self) -> bool:
        return self.manifest_valid and self.signature_valid


def build_safety_case_bundle(
    destination: str | Path,
    *,
    case: dict,
    artifacts: dict[str, bytes],
    signer: Ed25519PrivateKey,
    key_id: str,
) -> Path:
    destination = Path(destination)
    files: dict[str, bytes] = {"case.json": _canonical_json(case)}
    for name, data in artifacts.items():
        if name in {"manifest.json", "signature.json", "case.json"}:
            raise ValueError(f"reserved bundle path: {name}")
        if name.startswith("/") or ".." in Path(name).parts:
            raise ValueError(f"unsafe bundle path: {name}")
        files[name] = data

    manifest = {
        "format": "chp-safety-case/v0.1",
        "files": {name: _sha256(data) for name, data in sorted(files.items())},
    }
    manifest_bytes = _canonical_json(manifest)
    signature = signer.sign(manifest_bytes)
    public = signer.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    signature_doc = {
        "algorithm": "ed25519",
        "key_id": key_id,
        "public_key_b64": base64.b64encode(public).decode("ascii"),
        "signature_b64": base64.b64encode(signature).decode("ascii"),
    }

    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as zf:
        for name, data in sorted(files.items()):
            zf.writestr(name, data)
        zf.writestr("manifest.json", manifest_bytes)
        zf.writestr("signature.json", _canonical_json(signature_doc))
    return destination


def verify_safety_case_bundle(
    bundle: str | Path,
    *,
    trusted_public_keys: dict[str, bytes] | None = None,
) -> BundleVerification:
    errors: list[str] = []
    manifest_valid = True
    signature_valid = False
    signer_trusted = False
    trusted_public_keys = trusted_public_keys or {}

    try:
        with ZipFile(bundle, "r") as zf:
            names = set(zf.namelist())
            if not {"case.json", "manifest.json", "signature.json"}.issubset(names):
                return BundleVerification(False, False, False, ("missing required bundle file",))
            manifest_bytes = zf.read("manifest.json")
            manifest = json.loads(manifest_bytes)
            sigdoc = json.loads(zf.read("signature.json"))

            expected_files = manifest.get("files", {})
            for name, expected in expected_files.items():
                if name not in names:
                    manifest_valid = False
                    errors.append(f"missing: {name}")
                    continue
                actual = _sha256(zf.read(name))
                if actual != expected:
                    manifest_valid = False
                    errors.append(f"digest mismatch: {name}")

            signed_names = set(expected_files) | {"manifest.json", "signature.json"}
            unexpected = names - signed_names
            if unexpected:
                manifest_valid = False
                errors.append("unsigned files present: " + ",".join(sorted(unexpected)))

            public_raw = base64.b64decode(sigdoc["public_key_b64"])
            signature = base64.b64decode(sigdoc["signature_b64"])
            try:
                Ed25519PublicKey.from_public_bytes(public_raw).verify(signature, manifest_bytes)
                signature_valid = True
            except Exception:
                errors.append("signature invalid")

            key_id = sigdoc.get("key_id", "")
            trusted = trusted_public_keys.get(key_id)
            signer_trusted = trusted == public_raw if trusted is not None else False
            if trusted is not None and not signer_trusted:
                errors.append("signer key does not match trusted key")
    except Exception as exc:
        errors.append(f"bundle parse failure: {exc}")
        return BundleVerification(False, False, False, tuple(errors))

    return BundleVerification(manifest_valid, signature_valid, signer_trusted, tuple(errors))
