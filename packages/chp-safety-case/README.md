# chp-safety-case

The portable **`.chpsafety` Safety Case** bundle format and its **offline verifier** — part of
the [Capability Host Protocol](https://capabilityhostprotocol.com) runtime-assurance work.

A Safety Case is the artifact you hand to a security reviewer, an auditor, or a customer to answer
*"what was this AI agent authorized and technically able to do, and did the controls hold?"* — a
file, not a screenshot. This package **verifies one anywhere, with no network and no trust in the
producer**: it recomputes every artifact digest (tamper-evidence) and checks the Ed25519 signature
over the manifest. Deliberately minimal — **stdlib + `cryptography` only**, no `chp-core`, no mesh.

## Install

```bash
pipx install chp-safety-case      # or: pip install chp-safety-case
```

## Verify a bundle

```bash
chp-safety-case verify case.chpsafety
```

```json
{
  "manifest_valid": true,     // every file matches its recorded sha256; no unsigned files present
  "signature_valid": true,    // the Ed25519 signature over the manifest checks out
  "signer_trusted": false,    // true only when you pass the signer's key via --trusted-key
  "integrity_valid": true,    // manifest_valid AND signature_valid
  "errors": []
}
```

Exit codes: `0` ok, `2` integrity failed, `3` `--require-trusted-signer` set and the signer wasn't
trusted. Pin a signer you trust:

```bash
chp-safety-case verify case.chpsafety --trusted-key my-node=signer.pub.hex --require-trusted-signer
```

## As a library

```python
from chp_safety_case import verify_safety_case_bundle

r = verify_safety_case_bundle("case.chpsafety")
assert r.integrity_valid        # tamper-evident: any edit to any artifact breaks this
```

## What's in a bundle

A `.chpsafety` file is a zip of `case.json` (the Safety Case), its evidence artifacts, a
`manifest.json` (sha256 of every file), and a `signature.json` (Ed25519 over the manifest). The
verifier trusts none of the producer's own booleans — it recomputes the digests and checks the
signature itself.

## License

Apache-2.0.
