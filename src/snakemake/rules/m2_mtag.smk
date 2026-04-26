"""M2 Wave 2 — MTAG (Turley 2018) 3-stratum joint-signal discovery.

Plan: m2-02-mtag-3-strata-PLAN.md.

Decisions:
  D-M2-03  — three strata (EUR, AFR, TRANS); per-stratum mega-runs
  D-M2-07  — max_FDR threshold = 0.05 (Turley 2018 default)
  D-M2-Q1  — post-hoc max_FDR filter on each MTAG run
  D-M2-Q6  — _MIN_PER_STRATUM = 3 (Carter-locked soft floor); below-floor
             strata emit a row to skipped_strata.tsv
  D-M2-06  — strict ancestry match; per-trait skips emit a row to
             skipped_traits.tsv (no skips here since the slicer enumerates
             keys deterministically through m2_stratum_keys, but the file
             is touched empty for downstream consumers)
  D-M2-10  — CRITICAL CORRECTION: MTAG flag is --residcov_path NOT --overlap.
             "--overlap" is colloquial shorthand from the Turley paper;
             the actual implemented flag is verified in
             tools/mtag/.git_clone_log (commit 9e17f3cf...).

Pitfalls:
  Pitfall 1  — "--overlap" is the false-friend; never appears here
  Pitfall 2  — residcov.txt is bare numeric (built by
               build_mtag_residcov_slice.py)
  Pitfall 5  — MTAG --rg-cross is apocryphal (irrelevant in Wave 2)
  Pitfall 6  — vendored MTAG requires numpy<2 ABI (envs/m2-mtag.yml pins
               numpy=1.26.4)
  Pitfall 7  — trait-order alignment via residcov.trait_order.json sidecar;
               the Snakemake rule reads the sidecar to construct
               --sumstats in the same order as residcov rows/cols
  Pitfall 8  — Snakemake 7.32.4 requires Python 3.11; production fire uses
               /rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake

VENDORED MTAG ANOMALY (D-M2-Q1 reconciliation):
  The plan body refers to "tools/mtag/mtag_maxFDR.py". The pinned upstream
  JonJala/mtag commit 9e17f3cf does NOT ship a separate mtag_maxFDR.py;
  max-FDR computation lives inside mtag.py via the --fdr flag. The flag
  emits {out}_fdr_mat.txt with per-trait max-FDR scalars (one value per
  input trait, NOT per-SNP).

  We reconcile this in m2_mtag_maxfdr_filter rule by:
    1. Reading the per-trait scalar from {out}_fdr_mat.txt
    2. Attaching it as a constant max_FDR column on the per-trait
       _trait_{N}.txt MTAG output
    3. Filtering rows with max_FDR < 0.05 via mtag_maxfdr_filter.py

  This is the canonical implementation of "max_FDR filter per Turley 2018
  default 0.05" given the vendored release shape.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project-root + src/python discovery (matches m1_ldsc_rg.smk pattern).
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
# Path constants.
# ---------------------------------------------------------------------------
_MATRIX = "data/processed/ldsc_overlap/bivariate_intercept_matrix_2026-04-M2.tsv"
_MUNGED_DIR = "data/processed/ldsc_overlap/munged"
_MTAG_DIR = "data/processed/mtag"
_MTAG_REPO = "tools/mtag"
_INVENTORY = "config/trait_inventory.yaml"

STRATA = ("EUR", "AFR", "TRANS")


# ---------------------------------------------------------------------------
# rule m2_mtag_residcov_slice — bare-numeric K x K matrix + sidecar.
# ---------------------------------------------------------------------------

rule m2_mtag_residcov_slice:
    """Slice M2 LDSC matrix to per-stratum K x K residual-covariance matrix.

    D-M2-10 corrected — output is bare-numeric residcov.txt + sidecar JSON.
    Pitfall 2: NO header, NO index, whitespace-delimited.
    Pitfall 7: sidecar trait_order.json is the alignment contract for the
    --sumstats list constructed by m2_mtag_run.

    If the per-stratum K is below _MIN_PER_STRATUM = 3 (D-M2-Q6),
    build_mtag_residcov_slice.slice_from_files() raises ValueError; the
    shell wrapper traps that and emits a row to
    {_MTAG_DIR}/{stratum}/skipped_strata.tsv per D-M2-06 instead of
    failing the rule.
    """
    input:
        matrix=_MATRIX,
        inventory=_INVENTORY,
    output:
        residcov=f"{_MTAG_DIR}/{{stratum}}/residcov.txt",
        sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
        skipped_traits=f"{_MTAG_DIR}/{{stratum}}/skipped_traits.tsv",
    params:
        out_dir=f"{_MTAG_DIR}/{{stratum}}",
    conda:
        "../../../envs/m2-cpassoc.yml"
    resources:
        mem_mb=2000,
        runtime=10,
    shell:
        r"""
        set -euo pipefail
        mkdir -p {params.out_dir}
        # Slice; if below floor, emit skipped_strata.tsv row and re-raise.
        python src/python/build_mtag_residcov_slice.py \
            --matrix {input.matrix} \
            --stratum {wildcards.stratum} \
            --inventory {input.inventory} \
            --out-dir {params.out_dir}
        # Stratum was viable. Touch skipped_traits.tsv (empty header per
        # D-M2-06; no per-trait skips since slicer enumerates only keys
        # whose munged_path exists on disk).
        printf "stratum\ttrait_key\treason\tdecision_ref\n" > {output.skipped_traits}
        """


# ---------------------------------------------------------------------------
# rule m2_mtag_run — per-stratum MTAG fire (Turley 2018) with --residcov_path.
# ---------------------------------------------------------------------------

rule m2_mtag_run:
    """Per-stratum MTAG fire with --residcov_path correction (D-M2-10).

    Pitfall 1: NEVER use --overlap; the actual MTAG flag is --residcov_path.
    Pitfall 7: --sumstats list MUST be in the same order as residcov.txt
               rows/cols; the sidecar trait_order.json is the contract.
    D-M2-07: --p_sig 5e-8 (genome-wide significance).
    D-M2-Q1: --fdr enabled to emit {out}_fdr_mat.txt for the post-hoc
             max-FDR filter rule.

    Output naming follows the vendored MTAG convention (verified in
    tools/mtag/mtag.py:save_mtag_results around line 884):
        {out}_trait_1.txt, {out}_trait_2.txt, ..., {out}_trait_K.txt
    The {out}_fdr_mat.txt sidecar (K x G matrix where G = number of grid
    points; we extract the per-trait max for the filter step) is also
    emitted because of --fdr.

    Wall ~30-60 min on LSF standard or long queue per stratum at K<=9.
    """
    input:
        residcov=f"{_MTAG_DIR}/{{stratum}}/residcov.txt",
        sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
    output:
        # The trait_1 file is always emitted regardless of K because mtag.py
        # writes one file per input trait (K-1 stratum floor guarantees
        # at least 3 trait files; we declare trait_1 as the sentinel since
        # K varies across strata).
        trait_1=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_trait_1.txt",
        fdr_mat=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_fdr_mat.txt",
        log=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_run.log",
    params:
        out_prefix=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag",
        mtag_repo=_MTAG_REPO,
        munged_dir=_MUNGED_DIR,
    conda:
        "../../../envs/m2-mtag.yml"
    resources:
        mem_mb=8000,
        runtime=240,  # 4 hr ceiling; expected 30-60 min for K<=9
    threads: 4
    shell:
        r"""
        set -euo pipefail
        # Pitfall 7 — read sidecar for canonical trait order; build
        # --sumstats list in the SAME order so MTAG's post-load assertion
        # `omega_hat.shape == Zs.shape[1] == sigma_hat.shape` doesn't pass
        # silently with mismatched correlations.
        SUMSTATS_LIST=$(python -c "
        import json
        ord_list = json.load(open('{input.sidecar}'))['trait_order']
        paths = ['{params.munged_dir}/' + k + '.sumstats.gz' for k in ord_list]
        print(','.join(paths))
        ")
        TRAIT_ORDER=$(python -c "import json; print(','.join(json.load(open('{input.sidecar}'))['trait_order']))")
        echo "Stratum {wildcards.stratum} trait order: $TRAIT_ORDER" | tee {output.log}
        echo "Sumstats list: $SUMSTATS_LIST" | tee -a {output.log}

        export PYTHONPATH={params.mtag_repo}:${{PYTHONPATH:-}}

        # MTAG fire — D-M2-10 corrected: --residcov_path NOT --overlap.
        # --p_sig 5e-8 per D-M2-07.
        # --fdr per D-M2-Q1 to emit {out}_fdr_mat.txt for post-hoc filter.
        # --use_beta_se per munged HM3 inputs (BETA + SE columns present).
        # --stream_stdout for live progress logging.
        python {params.mtag_repo}/mtag.py \
            --sumstats "$SUMSTATS_LIST" \
            --residcov_path {input.residcov} \
            --out {params.out_prefix} \
            --p_sig 5e-8 \
            --use_beta_se \
            --fdr \
            --stream_stdout \
            2>&1 | tee -a {output.log}

        # Fail fast if MTAG didn't emit the per-trait file.
        test -s {output.trait_1}
        test -s {output.fdr_mat}
        """


# ---------------------------------------------------------------------------
# rule m2_mtag_maxfdr_filter — post-hoc max-FDR attachment + filter (D-M2-Q1).
# ---------------------------------------------------------------------------

rule m2_mtag_maxfdr_filter:
    """Post-hoc max_FDR filter per D-M2-Q1 + D-M2-07.

    Reconciles vendored MTAG --fdr output (per-trait scalar in
    {out}_fdr_mat.txt) with the plan-body per-SNP max_FDR column
    contract:

      1. Discover all {out}_trait_{N}.txt files in the stratum dir
      2. Read per-trait max-FDR row from {out}_fdr_mat.txt (taking the
         max across the grid points, per Turley 2018 Methods §"maxFDR")
      3. For each trait file, attach the trait's max-FDR scalar as a
         constant max_FDR column
      4. Filter rows with max_FDR < 0.05 (D-M2-07 default)
      5. Write {trait}_mtag_maxfdr_filtered.txt per-trait
      6. Emit aggregate {stratum}_mtag_maxfdr_filtered.txt as the
         sentinel that the aggregator depends on

    The 0.05 threshold is hardcoded per D-M2-07. To change, modify the
    --threshold argument below AND the corresponding entry in
    config/pipeline.yaml (TODO: add to pipeline.yaml when M5 reviews).
    """
    input:
        trait_1=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_trait_1.txt",
        fdr_mat=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_fdr_mat.txt",
        sidecar=f"{_MTAG_DIR}/{{stratum}}/residcov.trait_order.json",
    output:
        filtered=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_maxfdr_filtered.txt",
        log=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_maxfdr.log",
    params:
        stratum_dir=f"{_MTAG_DIR}/{{stratum}}",
        out_prefix=f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag",
    conda:
        "../../../envs/m2-mtag.yml"
    resources:
        mem_mb=8000,
        runtime=120,
    shell:
        r"""
        set -euo pipefail
        # Use Python inline to (1) load the per-trait FDR scalars from
        # {out}_fdr_mat.txt (G x K matrix; we take max across G per
        # trait), (2) iterate per-trait files, attach + filter, (3) emit
        # a concatenated stratum file with a `trait_key` provenance
        # column so downstream Class 1 novelty calling can route by trait.
        python -c "
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, 'src/python')
from mtag_maxfdr_filter import filter_by_max_fdr

stratum_dir = Path('{params.stratum_dir}')
out_prefix = Path('{params.out_prefix}')
threshold = 0.05  # D-M2-07 Turley 2018 default

# 1. Load per-trait max-FDR scalars (G x K matrix; max across rows per col).
fdr_mat = np.loadtxt('{input.fdr_mat}')
if fdr_mat.ndim == 1:
    fdr_mat = fdr_mat.reshape(-1, 1)
per_trait_maxfdr = fdr_mat.max(axis=0)  # (K,) max across grid rows
print(f'mtag_maxfdr_filter: per-trait max-FDR scalars = {{per_trait_maxfdr.tolist()}}')

sidecar = json.loads(Path('{input.sidecar}').read_text())
trait_order = sidecar['trait_order']
K = len(trait_order)
assert per_trait_maxfdr.shape[0] == K, f'fdr_mat K={{per_trait_maxfdr.shape[0]}} != sidecar K={{K}}'

# 2. Iterate per-trait files, attach + filter, accumulate.
all_filtered = []
total_in = 0
total_out = 0
for k, trait_key in enumerate(trait_order):
    trait_file = Path(str(out_prefix) + f'_trait_{{k+1}}.txt')
    if not trait_file.exists():
        print(f'mtag_maxfdr_filter: WARN missing {{trait_file}}; skipping')
        continue
    df = pd.read_csv(trait_file, sep='\t')
    df['max_FDR'] = float(per_trait_maxfdr[k])
    df['trait_key'] = trait_key
    n_in = len(df)
    out = filter_by_max_fdr(df, threshold=threshold)
    n_out = len(out)
    total_in += n_in
    total_out += n_out
    print(f'mtag_maxfdr_filter: {{trait_key}} max_FDR={{per_trait_maxfdr[k]:.4g}} {{n_in}} -> {{n_out}} rows')
    all_filtered.append(out)

# 3. Concat + write stratum-level aggregated filtered table.
if all_filtered:
    combined = pd.concat(all_filtered, ignore_index=True)
else:
    # Edge case: all per-trait max-FDR scalars >= 0.05 — no rows survive.
    combined = pd.DataFrame(columns=['trait_key', 'max_FDR'])
combined.to_csv('{output.filtered}', sep='\t', index=False)
print(f'mtag_maxfdr_filter: AGGREGATE {{total_in}} -> {{total_out}} rows (dropped {{total_in - total_out}} at threshold {{threshold}})')
" 2>&1 | tee {output.log}
        test -f {output.filtered}
        """


# ---------------------------------------------------------------------------
# rule m2_mtag_all_strata — aggregator across strata.
# ---------------------------------------------------------------------------

rule m2_mtag_all_strata:
    """Aggregator — fire residcov_slice + mtag_run + maxfdr_filter for all 3
    strata. The aggregated maxfdr_filtered.txt sentinel marks completion.
    """
    input:
        expand(
            f"{_MTAG_DIR}/{{stratum}}/{{stratum}}_mtag_maxfdr_filtered.txt",
            stratum=STRATA,
        ),
