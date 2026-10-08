from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from .bundle import verify_safety_case_bundle


def _load_trusted_key(value: str) -> tuple[str, bytes]:
    key_id, path = value.split("=", 1)
    raw = Path(path).read_text(encoding="utf-8").strip()
    try:
        key = bytes.fromhex(raw)
    except ValueError:
        key = base64.b64decode(raw)
    if len(key) != 32:
        raise ValueError("Ed25519 public key must be 32 raw bytes")
    return key_id, key


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="chp-safety-case")
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify", help="Offline-verify a .chpsafety Safety Case bundle.")
    verify.add_argument("bundle")
    verify.add_argument("--trusted-key", action="append", default=[], metavar="KEY_ID=FILE",
                        help="A trusted Ed25519 public key (hex or base64, 32 raw bytes).")
    verify.add_argument("--require-trusted-signer", action="store_true",
                        help="Exit non-zero unless the signer matches a --trusted-key.")
    args = parser.parse_args(argv)

    trusted: dict[str, bytes] = {}
    for item in args.trusted_key:
        key_id, key = _load_trusted_key(item)
        trusted[key_id] = key

    result = verify_safety_case_bundle(args.bundle, trusted_public_keys=trusted)
    payload = {
        "manifest_valid": result.manifest_valid,
        "signature_valid": result.signature_valid,
        "signer_trusted": result.signer_trusted,
        "integrity_valid": result.integrity_valid,
        "errors": list(result.errors),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not result.integrity_valid:
        return 2
    if args.require_trusted_signer and not result.signer_trusted:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
