"""Integration test: negative controls should NOT flip tier under bootstrap.

HLA and pigmentation loci are expected to show ancestry-specific effects
that would NOT survive matched-N bootstrap — they should remain in their
pre-bootstrap tier (not flip from non-Tier-A to Tier A under bootstrap).

References:
    - CP#1(c): Phase 4 must not flip HLA/pigmentation tiers under bootstrap
    - Phase 2 negative controls: HLA, cosmetic, blood group sets
"""
import pytest


@pytest.mark.phase4
@pytest.mark.xfail(reason="Wave 0 stub — implementation in later plan")
def test_hla_pigmentation_no_tier_flip():
    """Verify HLA and pigmentation loci do not flip to Tier A under bootstrap.

    Integration test: run bootstrap on known negative-control regions and
    confirm they remain non-Tier-A (or remain unchanged if already non-A).
    """
    raise NotImplementedError("Negative control integration test pending Plan 04-05")
