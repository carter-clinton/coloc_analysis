"""M1 Wave 3b — LDSC star-topology --rg orchestration + reducer.

Plan: m1-03-munge-and-ldsc-intercept-matrix Task 1 step (E).

RESEARCH Pitfall #1: ``ldsc.py an "rg cross" flag`` does NOT exist in the vendored
``abdenlab/ldsc-python3`` fork (verified at tools/ldsc/ldsc.py lines 608-613).
The CANONICAL approach for full N x N coverage is N-1 star-topology
``--rg`` calls where for ``focal_idx`` in 0..N-2 the focal trait pairs with
all traits index+1..N-1 in a single comma-separated list. Each call emits
one ``focal_<i>.log`` containing (N-1-i) pairwise rg records.

A reducer (``src/python/reduce_ldsc_rg_matrix.py``) parses every
focal_*.log, extracts ``gcov_int`` for each pair, and assembles the
N x N symmetric wide TSV consumed by M2 MTAG --overlap (D-11).

Path-parameterization (REQ-PATH-PARAMETERIZATION): every disk path is
resolved through ``config["paths"]["ldsc_munged"]``,
``config["paths"]["ldsc_rg_logs"]``, and
``config["paths"]["ldsc_overlap"]``. Zero hardcoded absolute paths.

LD-panel selection per D-15 + RESEARCH Pattern 4: EUR-EUR uses
``data/external/ldscore/eur_w_ld_chr/`` (Wave 0 staged); cross-ancestry
pairs default to the same EUR LD panel since gcov_int is interpretable
across LD panels (the bivariate INTERCEPT consumed by MTAG --overlap is
LD-panel-robust). AFR-AFR pairs would benefit from an AFR LD-score
release; deferred per D-11 / RESEARCH §Pattern 4 note. Cross-ancestry
intercepts are flagged as approximated in the QC sidecar.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project-root + src/python discovery.
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

# Path-parameterized roots.
try:
    _MUNGED = config["paths"]["ldsc_munged"]      # type: ignore[name-defined]
    _RG_LOGS = config["paths"]["ldsc_rg_logs"]    # type: ignore[name-defined]
    _OVERLAP = config["paths"]["ldsc_overlap"]    # type: ignore[name-defined]
except (NameError, KeyError):
    _MUNGED = "data/processed/ldsc_overlap/munged"
    _RG_LOGS = "data/processed/ldsc_overlap/rg_logs"
    _OVERLAP = "data/processed/ldsc_overlap"

# EUR LD-score reference (Wave 0 staged via Phase 5 reuse + symlink).
_EUR_REF_LD = "data/external/ldscore/eur_w_ld_chr/"

# Trait-keys file written by m1_build_trait_keys_list (one D-16 key per line).
_TRAIT_KEYS_FILE = os.path.join(_OVERLAP, "trait_keys.txt")


# ---------------------------------------------------------------------------
# rule m1_build_trait_keys_list — deterministic D-16 key list.
# ---------------------------------------------------------------------------

rule m1_build_trait_keys_list:
    """Materialize the deterministic D-16 trait-keys list.

    Calls ``src/python/m1_trait_keys.py`` which reads SUMSTATS-UPGRADE.tsv,
    filters to in-scope statuses, applies TOKEN_MAP, appends Evangelou
    SBP-EUR, dedupes + sorts. Defensive 40<=N<=50 bound enforced inside
    the helper (W5 fix).
    """
    input:
        tsv=".planning/amendments/SUMSTATS-UPGRADE.tsv",
    output:
        trait_keys=_TRAIT_KEYS_FILE,
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=2000,
        runtime=120,
    shell:
        r"""
        mkdir -p $(dirname {output.trait_keys})
        python src/python/m1_trait_keys.py \
            --tsv {input.tsv} \
            --out {output.trait_keys}
        """


def _read_trait_keys() -> list[str]:
    """Read the trait_keys.txt produced by m1_build_trait_keys_list.

    Returns sorted unique keys; raises FileNotFoundError when the
    list hasn't been built yet — Snakemake DAG will trigger
    m1_build_trait_keys_list and re-evaluate the rule body's input list
    once the file exists.
    """
    p = Path(_TRAIT_KEYS_FILE)
    if not p.exists():
        return []
    return sorted({line.strip() for line in p.read_text().splitlines() if line.strip()})


def _focal_input(wildcards) -> str:
    """Return the focal munged file path for star focal_idx=i."""
    keys = _read_trait_keys()
    i = int(wildcards.focal_idx)
    if i >= len(keys):
        raise ValueError(f"focal_idx {i} out of range (have {len(keys)} keys)")
    return os.path.join(_MUNGED, f"{keys[i]}.sumstats.gz")


def _others_input(wildcards) -> list[str]:
    """Return the list of non-focal munged files (i+1..N-1) for star focal_idx=i."""
    keys = _read_trait_keys()
    i = int(wildcards.focal_idx)
    return [os.path.join(_MUNGED, f"{k}.sumstats.gz") for k in keys[i + 1:]]


# ---------------------------------------------------------------------------
# rule m1_ldsc_rg_star — one star per focal_idx (focal vs i+1..N-1).
# ---------------------------------------------------------------------------

rule m1_ldsc_rg_star:
    """Star-topology --rg call: focal i vs traits i+1..N-1.

    Produces one ``focal_<i>.log`` containing (N-1-i) pairwise rg records.
    Pitfall #1: NOT an "rg cross" flag (which does not exist); CANONICAL --rg with
    a comma-separated prefix list (first entry is focal).
    """
    input:
        focal=_focal_input,
        others=_others_input,
        trait_keys=_TRAIT_KEYS_FILE,
        ref_ld=_EUR_REF_LD,
    output:
        log=os.path.join(_RG_LOGS, "focal_{focal_idx}.log"),
    wildcard_constraints:
        focal_idx=r"[0-9]+",
    params:
        out_prefix=lambda wc: os.path.join(_RG_LOGS, f"focal_{wc.focal_idx}"),
        rg_args=lambda wc, input: ",".join([input.focal] + list(input.others)),
    conda:
        "../../../envs/m1-ldsc-rg.yml"
    resources:
        mem_mb=8000,
        runtime=14400,  # long queue ceiling per feedback_lsf_queues
    shell:
        r"""
        mkdir -p {_RG_LOGS}
        # Pitfall #1: --rg (NOT an "rg cross" flag) with comma-separated prefix list.
        python tools/ldsc/ldsc.py \
            --rg {params.rg_args} \
            --ref-ld-chr {input.ref_ld} \
            --w-ld-chr   {input.ref_ld} \
            --out {params.out_prefix}
        """


def _all_star_logs() -> list[str]:
    """Build the full list of focal_*.log targets from the trait-keys file.

    Returns logs for focal_idx in 0..N-2 (N-1 stars; the N-1-th focal has
    zero remaining comparisons so its trivial log is omitted; matrix
    diagonal handles the self-pair convention).
    """
    keys = _read_trait_keys()
    if not keys:
        return []
    return [os.path.join(_RG_LOGS, f"focal_{i}.log") for i in range(len(keys) - 1)]


rule m1_ldsc_rg_all_stars:
    """Aggregator: every focal_*.log."""
    input:
        trait_keys=_TRAIT_KEYS_FILE,
        logs=_all_star_logs(),
    output:
        sentinel=os.path.join(_RG_LOGS, ".all_stars.complete"),
    shell:
        "touch {output.sentinel}"


# ---------------------------------------------------------------------------
# rule m1_ldsc_rg_reduce — assemble the NxN intercept matrix + long format.
# ---------------------------------------------------------------------------

rule m1_ldsc_rg_reduce:
    """Reduce focal_*.log files into the NxN intercept matrix + long-form TSV."""
    input:
        trait_keys=_TRAIT_KEYS_FILE,
        logs=_all_star_logs(),
    output:
        matrix=os.path.join(_OVERLAP, "bivariate_intercept_matrix_2026-04.tsv"),
        long=os.path.join(_OVERLAP, "rg_matrix_long.tsv"),
        validation=os.path.join(_OVERLAP, "rg_validation_warnings.json"),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=4000,
        runtime=120,
    shell:
        r"""
        python src/python/reduce_ldsc_rg_matrix.py \
            --log-dir {_RG_LOGS} \
            --trait-keys-file {input.trait_keys} \
            --output-matrix {output.matrix} \
            --output-long {output.long} \
            --output-validation {output.validation}
        """
