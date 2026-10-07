# CHP Capability Adapters

Open-source ([Apache-2.0](./LICENSE)) capability adapters for the **[Capability Host Protocol](https://capabilityhostprotocol.com)** — the protocol that makes agent and tool execution visible, replayable, and governable. Each adapter adds governed capabilities to a CHP host ([`chp-core`](https://github.com/capabilityhostprotocol/chp-core)); every invocation is evidence-wrapped and runs through the protocol's gate pipeline.

This repository holds the **publicly released** adapters. It is a curated subset of the broader CHP adapter ecosystem — the generic, reusable governance/safety capabilities. It is published from the project's governed development flow; issues and discussion for all published packages live on [`chp-core`](https://github.com/capabilityhostprotocol/chp-core/issues).

## Packages

| Package | PyPI | What it adds |
|---|---|---|
| **chp-adapter-safety** | [`chp-adapter-safety`](https://pypi.org/project/chp-adapter-safety/) | Risk assessment + prompt-injection scanning, and **hardware-attested (W4) witness** attest/verify (TPM quote + EK-chain to a pinned manufacturer root) plus producer-independent **containment** verification. |
| **chp-adapter-audit** | [`chp-adapter-audit`](https://pypi.org/project/chp-adapter-audit/) | Queryable audit log over a host's evidence store: invocation query/stats, Merkle store-head inclusion proofs, cross-host witness countersignature, and **OCSF 1.3.0** export of governed decisions for SIEM/auditor interop. |

```bash
pip install chp-adapter-safety     # or: chp-adapter-audit
```

Then register on a host:

```python
from chp_core import LocalCapabilityHost, register_adapter
from chp_adapter_safety import SafetyAdapter

host = LocalCapabilityHost()
register_adapter(host, SafetyAdapter())
```

## Releases

Published to PyPI via **GitHub Actions OIDC Trusted Publishing** (no tokens). A release is a tag of the
form `<package>-v<version>` (e.g. `chp-adapter-safety-v0.57.2`); `.github/workflows/publish.yml` builds
that package and publishes it from the `release` environment. Each PyPI project trusts this repo +
workflow + environment as its publisher.

## License

Apache-2.0. See [LICENSE](./LICENSE) and each package's `NOTICE`.
