"""chp-safety-case — the portable `.chpsafety` Safety Case bundle format + offline verifier.

Verify a CHP Safety Case anywhere, with no network and no trust in the producer:

    from chp_safety_case import verify_safety_case_bundle
    result = verify_safety_case_bundle("case.chpsafety")
    assert result.integrity_valid        # manifest digests + Ed25519 signature check out

Or on the command line:  ``chp-safety-case verify case.chpsafety``.
"""
from .bundle import (
    BundleVerification,
    build_safety_case_bundle,
    verify_safety_case_bundle,
)

__all__ = [
    "BundleVerification",
    "build_safety_case_bundle",
    "verify_safety_case_bundle",
]
__version__ = "0.1.0"
