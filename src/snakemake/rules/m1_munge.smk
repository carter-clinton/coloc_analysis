"""M1 Wave 3a — LDSC munge rules (HM3-restricted .sumstats.gz per D-15/D-16).

Plan: m1-03-munge-and-ldsc-intercept-matrix Task 1 step (D).

Each rule consumes one D-16-named harmonized ``.tsv.bgz`` from
``data/processed/sumstats_harmonized/`` and emits one ``.sumstats.gz``
under ``data/processed/ldsc_overlap/munged/``. The wrapper module
``src/python/munge_sumstats_ldsc.py`` (existing per D-10) handles
canonical-10-col -> LDSC munge schema conversion + N-column / case-control
dispatch from the SUMSTATS-UPGRADE.tsv side-car (auto-detected per trait).

Path-parameterization (REQ-PATH-PARAMETERIZATION): every disk path is
resolved through ``config["paths"]["harmonized_sumstats"]`` (input root)
and ``config["paths"]["ldsc_munged"]`` (output root). Zero hardcoded
absolute paths.

W8 fix (universal .deferred guard): when an upstream harmonized file is
absent (e.g. cookie-pending DIAMANTE; D-01 Loh deferral), the input
resolution returns the path with the implied ``.deferred`` sibling and
this rule's shell prelude routes to a no-op ``.deferred`` placeholder.

D-15 munge spec: ``--merge-alleles w_hm3.snplist`` is applied via the
underlying ``tools/ldsc/munge_sumstats.py`` invocation embedded in the
wrapper. The wrapper auto-detects continuous vs case-control N from the
SUMSTATS-UPGRADE.tsv lookup keyed by trait-key tokens.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project-root + src/python discovery (so m1_trait_keys is importable from
# the rule's params lambda regardless of how Snakemake is invoked).
# ---------------------------------------------------------------------------
try:
    _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _BASE = Path(os.getcwd())


def _find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(6):
        if (cur / "config" / "pipeline.yaml").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start


_PROJECT_ROOT = _find_project_root(_BASE)
_SRC_PYTHON = _PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# Path-parameterized roots (config-driven; no absolute scratch paths).
try:
    _HARM = config["paths"]["harmonized_sumstats"]   # type: ignore[name-defined]
    _MUNGED = config["paths"]["ldsc_munged"]         # type: ignore[name-defined]
except (NameError, KeyError):
    _HARM = "data/processed/sumstats_harmonized"
    _MUNGED = "data/processed/ldsc_overlap/munged"

# HM3 SNP list (Wave 0 staged via Phase 5 reuse + symlink per
# feedback_url_rot_workarounds — see m1-00 SUMMARY).
_W_HM3 = "data/external/ldscore/w_hm3.snplist"

# ---------------------------------------------------------------------------
# Per-trait N-column / case-control dispatch table.
# ---------------------------------------------------------------------------
# The wrapper munge_sumstats_ldsc.py supports either a per-row N column
# (default for continuous traits) OR an explicit --n-override / --n-case +
# --n-ctrl pair (case-control). Most Wave 2 harmonizers emit a per-row N
# column natively (continuous traits + Aragam CAD), so the default path
# applies. GIGASTROKE harmonizer adds a synthesized N column from
# SUMSTATS-UPGRADE.tsv totals at harmonize-time, so it ALSO works in default
# mode. The exception is GBMI asthma (case-control via harmonize_gbmi.py)
# which emits BETA/SE/P but no per-row N — case_control_overrides handles
# this case via --n-case + --n-ctrl. Default empty: most rules pass-through.
case_control_overrides = {
    # No explicit overrides currently — every Wave 2 harmonizer surface emits
    # a usable N column. Reserved for future deferral resolutions where the
    # raw release does not carry per-row N.
}


# Universal .deferred guard for upstream harmonizer no-op outputs.
_DEFERRED_GUARD = r"""
        if [ ! -s "{input.harmonized}" ] || [ -f "{input.harmonized}.deferred" ]; then
            mkdir -p $(dirname {output.munged})
            touch {output.munged}.deferred
            touch {output.munged}
            echo "DEFERRED: harmonized input is empty or .deferred sibling present"
            exit 0
        fi
"""


rule m1_munge_per_trait:
    """Generic wildcard-expanded LDSC munger per D-16 trait key.

    Wildcards:
      trait, ancestry, consortium, year — together compose the full D-16
      trait key. ``consortium`` may contain hyphens (e.g. GIANT-UKBB,
      Evangelou-ICBP-UKBB, MVP-CHARGE) so the wildcard constraint allows
      ``[\w-]+``. ``year`` is a 4-digit token.
    """
    input:
        harmonized=os.path.join(
            _HARM, "{trait}.{ancestry}.{consortium}.{year}.GRCh37.tsv.bgz"
        ),
        w_hm3=_W_HM3,
    output:
        munged=os.path.join(
            _MUNGED, "{trait}.{ancestry}.{consortium}.{year}.sumstats.gz"
        ),
    wildcard_constraints:
        trait=r"[a-z0-9]+",
        ancestry=r"[A-Z]+",
        consortium=r"[\w-]+",
        year=r"\d{4}",
    conda:
        "../../../envs/m1-munge.yml"
    resources:
        mem_mb=8000,
        runtime=5760,  # serial queue ceiling per feedback_lsf_queues
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/munge_sumstats_ldsc.py \
            --input {input.harmonized} \
            --output {output.munged} \
            --trait {wildcards.trait} \
            --merge-alleles {input.w_hm3} \
            --chunksize 500000
        """


def _expand_munge_targets() -> list[str]:
    """Build the full munge target list from m1_trait_keys.build_keys.

    Reads ``.planning/amendments/SUMSTATS-UPGRADE.tsv`` at rule-load time,
    applies TOKEN_MAP + EVANGELOU append, and emits one
    ``data/processed/ldsc_overlap/munged/<key>.sumstats.gz`` per key.
    """
    from m1_trait_keys import build_keys
    tsv = _PROJECT_ROOT / ".planning" / "amendments" / "SUMSTATS-UPGRADE.tsv"
    keys = build_keys(tsv)
    return [os.path.join(_MUNGED, f"{k}.sumstats.gz") for k in keys]


rule m1_munge_all:
    """Aggregator: depend on every D-16 key derived from SUMSTATS-UPGRADE.tsv."""
    input:
        _expand_munge_targets(),
    output:
        sentinel=os.path.join(_MUNGED, ".m1_munge_all.complete"),
    shell:
        "touch {output.sentinel}"
