"""M2 Wave 3 — CPASSOC (Zhu 2015) 3 stratum runs.

Plan: m2-03-cpassoc-3-strata-PLAN.md.

Decisions:
  D-M2-04 — Python reimplementation of Zhu 2015 SHom + SHet using the M2
            LDSC bivariate-intercept matrix (Wave 1) as the cohort-correlation
            matrix R.
  D-M2-Q6 — _MIN_PER_STRATUM = 3 (Carter-locked); below-floor strata
            cascade-skip per D-M2-06 (the Wave 2 MTAG residcov sidecar
            does NOT exist for skipped strata, so this rule fails-closed
            in the canonical case; the cascade-skip guard at the top of
            the shell traps the upstream sentinel and emits its own
            skipped_strata.tsv).
  D-M2-06 — Strict ancestry match; per-trait skips inherit from Wave 2.
  Q7      — Per-stratum R is constructed as a PSD-preserving principal
            submatrix of the full ~26x26 matrix (eigvalsh probe enforces
            the invariant inside run_cpassoc._slice_R_for_trait_order).

Pitfalls:
  Pitfall 7 — CRITICAL: CPASSOC consumes the SAME trait order as MTAG
              (residcov.trait_order.json sidecar from Wave 2). This
              guarantees the downstream Class 1 novelty join (Wave 5)
              operates on a consistent K-trait basis. The Snakemake rule's
              input dependency on the Wave 2 sidecar makes this
              alignment-by-construction.
  Pitfall 8 — Snakemake 7.32.4 requires Python 3.11; production fire uses
              /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake.

Cascade-skip contract (D-M2-Q6):
  When Wave 2 MTAG records a stratum below floor, it emits
    data/processed/mtag/{stratum}/skipped_strata.tsv
  AND skips the residcov.trait_order.json + residcov.txt. This rule's
  shell prelude detects the upstream sentinel and emits its own
  skipped_strata.tsv mirror to data/processed/cpassoc/{stratum}/
  rather than failing, then short-circuits with empty results files.

Per Wave 2 outcomes (m2-02-mtag-3-strata-SUMMARY.md): EUR K=8, AFR K=6,
TRANS K=7 — all three strata clear the _MIN_PER_STRATUM=3 floor; no
cascade skips expected during M2.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project-root + src/python discovery (matches m2_mtag.smk pattern).
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

# ---------------------------------------------------------------------------
# Path constants — same conventions as m2_mtag.smk for cross-rule consistency.
# ---------------------------------------------------------------------------
_MATRIX = "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
# CPASSOC consumes the Wave 2 augmented sumstats (P/FRQ/INFO columns are
# tolerated; only SNP/A1/A2/Z/N are read). This guarantees CPASSOC and MTAG
# operate on the same per-trait variant set.
_MUNGED_DIR = "data/processed/mtag/munged_for_mtag"
_MTAG_DIR = "data/processed/mtag"
_CPASSOC_DIR = "data/processed/cpassoc"

STRATA = ("EUR", "AFR", "TRANS")


# ---------------------------------------------------------------------------
# rule m2_cpassoc_run — per-stratum CPASSOC fire (Zhu 2015 SHom + SHet).
# ---------------------------------------------------------------------------

rule m2_cpassoc_run:
    """Per-stratum CPASSOC fire using the M2 LDSC matrix as R.

    Consumes the Wave 2 MTAG sidecar (residcov.trait_order.json) to align
    trait order with MTAG (CRITICAL — downstream Class 1 novelty join
    requires this; Pitfall 7 contract).

    The Q7 PSD-preserving principal-submatrix slice + eigvalsh probe is
    implemented inside run_cpassoc._slice_R_for_trait_order; if PSD is
    violated (numerical drift), that helper raises ValueError and the
    rule fails-fast.

    Output: per-locus TSV with columns chr, pos, rsid, A1, A2, n_traits,
    SHom_stat, SHom_p, SHet_stat, SHet_p, contributing_traits. Expected
    row count at HM3 SNP density = ~1M post-intersection across K traits.

    Wall: ~10-30 min on local compute per stratum (matrix-vector ops are
    cheap; the bottleneck is the per-trait sumstats join + 1000G EUR bim
    load for chr+pos resolution).

    Cascade-skip: if upstream Wave 2 emitted skipped_strata.tsv for this
    stratum, the shell prelude mirrors that sentinel to the cpassoc dir
    and short-circuits.
    """
    input:
        matrix=_MATRIX,
        sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
    output:
        results=f"{_CPASSOC_DIR}/{{stratum}}/cpassoc_results.tsv",
        log=f"{_CPASSOC_DIR}/{{stratum}}/cpassoc_run.log",
    params:
        munged_dir=_MUNGED_DIR,
        mtag_dir=_MTAG_DIR,
        cpassoc_dir=_CPASSOC_DIR,
    conda:
        "../../../envs/m2-cpassoc.yml"
    resources:
        mem_mb=16000,
        runtime=120,  # 2 hr ceiling; expected 10-30 min per stratum
    threads: 4
    shell:
        r"""
        set -euo pipefail
        mkdir -p {params.cpassoc_dir}/{wildcards.stratum}

        # D-M2-Q6 cascade-skip guard: if upstream MTAG emitted
        # skipped_strata.tsv for this stratum, mirror it to the cpassoc
        # output dir and short-circuit (empty results + log).
        UPSTREAM_SKIP="{params.mtag_dir}/{wildcards.stratum}/skipped_strata.tsv"
        if [ -f "$UPSTREAM_SKIP" ]; then
            cp "$UPSTREAM_SKIP" "{params.cpassoc_dir}/{wildcards.stratum}/skipped_strata.tsv"
            echo "SKIPPED — upstream MTAG was below _MIN_PER_STRATUM=3 floor (D-M2-Q6 cascade)" \
                > {output.log}
            # Touch results with header-only sentinel for downstream consumers.
            printf "chr\tpos\trsid\tA1\tA2\tn_traits\tSHom_stat\tSHom_p\tSHet_stat\tSHet_p\tcontributing_traits\n" \
                > {output.results}
            exit 0
        fi

        # Normal path: invoke run_cpassoc.py orchestrator.
        # Q7 PSD probe + eigvalsh assertion are inside the helper.
        # Pitfall 7: --mtag-sidecar enforces same trait order as MTAG.
        python src/python/run_cpassoc.py \
            --stratum {wildcards.stratum} \
            --matrix {input.matrix} \
            --mtag-sidecar {input.sidecar} \
            --munged-dir {params.munged_dir} \
            --out {output.results} \
            2>&1 | tee {output.log}

        # Fail-fast invariant: results file must be non-empty.
        test -s {output.results}
        """


# ---------------------------------------------------------------------------
# rule m2_cpassoc_all_strata — aggregator for the 3 strata fires.
# ---------------------------------------------------------------------------

rule m2_cpassoc_all_strata:
    """Aggregator: fire CPASSOC for all 3 strata (EUR, AFR, TRANS).

    Per Wave 2 outcomes all 3 strata cleared the _MIN_PER_STRATUM=3 floor
    (EUR=8, AFR=6, TRANS=7), so all 3 cpassoc_results.tsv files are
    expected to land. If a future M2 re-fire or M5 catalog refresh
    triggers a stratum-skip cascade from Wave 2, this aggregator will
    still succeed because m2_cpassoc_run handles the cascade gracefully
    and emits the header-only sentinel + skipped_strata.tsv mirror.
    """
    input:
        expand(
            f"{_CPASSOC_DIR}/{{stratum}}/cpassoc_results.tsv",
            stratum=STRATA,
        ),
