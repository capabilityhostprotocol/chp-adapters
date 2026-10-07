# Quickstart — govern an agent, prove it, in ~5 minutes

The [Capability Host Protocol](https://capabilityhostprotocol.com) runs an agent's tool/capability
calls behind a governance pipeline and records every one as tamper-evident, SHA-256-chained evidence.
This walks you from `pip install` to a verified evidence chain, using only public packages.

## 1. Install

```bash
pip install 'chp-core[schema]' chp-adapter-safety chp-adapter-audit
```

- `chp-core` — the protocol + a local capability host (the `[schema]` extra turns on input-schema
  enforcement, so malformed or over-reaching calls are denied).
- `chp-adapter-safety` — governed safety capabilities (prompt-injection screening; hardware-attested
  witness verify/attest; containment checks).
- `chp-adapter-audit` — a queryable, verifiable audit log over the host's evidence store.

## 2. Run

Save [`examples/quickstart.py`](./examples/quickstart.py) and run it:

```bash
python quickstart.py
```

Expected output:

```
benign content   -> recommendation: allow
injection attempt-> recommendation: block | detected: True | categories: ['action_hijack', 'instruction_override']

evidence — governed invocations recorded: 2
            by capability: {'scan_injection': 2}
            evidence chain valid: True
```

## 3. What just happened

1. **Governed capability calls.** You screened untrusted content through a capability on a host — the
   benign text was allowed, the prompt-injection attempt was flagged and recommended `block`. The host
   evaluated each call through its pipeline (and, with `[schema]`, denies malformed input).
2. **Automatic evidence.** You didn't ask for logging — every invocation was recorded as evidence on
   an append-only, hash-chained store. `chp.adapters.audit.stats` queried it back.
3. **Verifiable, tamper-evident.** `verify_chain()` re-checked the SHA-256 chain for the run: any
   edit, reorder, or removal of a record breaks it. That's the "prove the controls held" half.

## Next

- Browse the [adapters](./packages) — each adds governed capabilities (http, filesystem, process, git,
  mlx, …); register any of them the same way.
- The safety adapter also does **hardware-attested (W4) witness** verification and producer-independent
  **containment** checks — the building blocks of a portable, offline-verifiable Safety Case.
- Learn more: **https://capabilityhostprotocol.com**

> Honest scope: CHP governs and evidences what an agent *does* — it is not a claim that a model is
> intrinsically safe, nor that it infers an agent's intent. It proves which controls were active and
> that the evidence verifies.
