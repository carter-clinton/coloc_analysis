"""The R4 arm table. Stage is owned by code, never by config (T-r4-W0b1-02)."""
from __future__ import annotations

CURRENT_SCRIPT = "src/legacy/region_analysis/scripts/run_susie_rss.R"
LEGACY_SCRIPT = "data/r4/legacy_code/run_susie_rss_3dd76df.R"
POLICY = "config/susie_policy.yaml"
POLICY_REPRO = "config/ta_r4/susie_policy_repro_iter100.yaml"
POLICY_L15 = "config/susie_policy_L15.yaml"


def _prod(ancestry, panel, validator_mode="real_ld"):
    return {
        "stage": "production",
        "ancestry": ancestry,
        "panel_source": panel,
        "panel_dir": panel,
        "route": "r4",
        "script": CURRENT_SCRIPT,
        "policy": POLICY,
        "validator_mode": validator_mode,
        "variant_catalog": "r4",
    }


def _repro(ancestry, panel, script, policy):
    return {
        "stage": "repro",
        "ancestry": ancestry,
        "panel_source": panel,
        "panel_dir": panel,
        "route": "legacy",
        "script": script,
        "policy": policy,
        "validator_mode": "legacy_any",
        "variant_catalog": "legacy",
    }


ARMS: dict[str, dict] = {
    "A3_1kg": _prod("EUR", "EUR_1kg_r4"),
    "A2_identity": _prod("EUR", "EUR_identity_r4", "identity_matched"),
    "A3_ukb": _prod("EUR", "EUR_ukb337k_r4"),
    "A3_ukb_isect": _prod("EUR", "EUR_ukb337k_isect_r4"),
    "A3_1kg_isect": _prod("EUR", "EUR_1kg_isect_r4"),
    "AFR661_A3": _prod("AFR", "AFR661_1kg_r4"),
    "AFR661_A2": _prod("AFR", "AFR661_identity_r4", "identity_matched"),
    "AFR504_A3": _prod("AFR", "AFR504_1kg_r4"),
    # Route C: current code, legacy semantics, effective max_iter 100.
    "repro_routeC": _repro(("EUR", "AFR"), "legacy_repro", CURRENT_SCRIPT, POLICY_REPRO),
    # Route L: the 3dd76df script; its max_iterations bug reproduces the effective 100.
    "repro_routeL": _repro(("EUR", "AFR"), "legacy_repro", LEGACY_SCRIPT, POLICY),
    "repro_k2d_routeC": _repro(("EUR", "AFR"), "k2d_identity", CURRENT_SCRIPT, POLICY_REPRO),
    "repro_k2d_routeL": _repro(("EUR", "AFR"), "k2d_identity", LEGACY_SCRIPT, POLICY),
    # L=15 fits for bmi/hypertension/stroke; asthma/t2d reuse the Route L L10 fits (W3b).
    "repro_sh2b3_r2": _repro(("EUR",), "legacy_repro", CURRENT_SCRIPT, POLICY_L15),
}


def arm_ancestries(arm: str) -> tuple[str, ...]:
    anc = ARMS[arm]["ancestry"]
    return (anc,) if isinstance(anc, str) else tuple(anc)


def arm_stage(arm: str) -> str:
    return ARMS[arm]["stage"]


def production_arms(ancestry: str | None = None) -> list[str]:
    return [
        a for a, r in ARMS.items()
        if r["stage"] == "production" and (ancestry is None or ancestry in arm_ancestries(a))
    ]
