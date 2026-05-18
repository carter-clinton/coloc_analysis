"""aou_ld_panel.py -- Hail driver for the M3 AoU AFR/EUR LD panel build.

Runs INSIDE the AoU Researcher Workbench (Terra-hosted Dataproc/Hail) AND
locally against the synthetic MT fixture at tests/m3/fixtures/synthetic_mt/
(D-M3-06 dev mirror).

Pipeline ordering (canonical; corrected per RESEARCH.md against
AOU-LD-PIPELINE.md §5.1 spec inversion):

    1. mt = hl.read_matrix_table(WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH)
    2. mt = filter_cols by ancestry (ancestry_pred == 'afr' | 'eur')
    3. mt = anti_join_cols against relateds (KING >= 0.0442 flagged samples)
    4. mt = hl.split_multi_hts(mt)              # canonical ordering
    5. mt = hl.sample_qc(mt, name='sqc'); call_rate >= 0.98
    6. mt = hl.variant_qc(mt, name='vqc'); MAF/HWE/call_rate
    7. mt = filter_rows hl.len(mt.filters) == 0  (drop AoU-flagged variants)
    8. mt = mt.checkpoint(_qc_checkpoint_uri(bucket, ancestry, sensitivity))
       # path: gs://${WORKSPACE_BUCKET}/ld/mt_{ancestry}[_pca_selfid]_qc.mt
    9. for region: hl.ld_matrix(..., radius=region.radius_bp)

Verified env vars (RESEARCH Q9):
    WORKSPACE_BUCKET                   - workspace egress staging (AoU-set)
    GOOGLE_PROJECT                     - billing (AoU-set)
    WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH - AoU-provided ACAF MT path (AoU-set)

Hardcoded auxiliary paths (NOT env vars; pin to CDR version):
    gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/
        relatedness/relatedness_flagged_samples.tsv
        ancestry/ancestry_preds.tsv (VERIFIED 2026-05-01 against CDR v8
            via AoU Workbench AUX path check; see Run 2 in
            m3-W1-AUX-PATH-VERIFICATION.md. Initial v7 verification
            2026-04-30 superseded by v8 adoption — O2 trigger fired
            because workspace WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH
            defaulted to v8 once Workbench bound to v8 dataset.
            v7 paths still resolve but v8 is canonical going forward
            per DEC-2026-05-01-01.)

Bucket access note:
    The AoU controlled-tier AUX bucket is requester-pays. Hail's GCS
    connector handles this transparently via Spark conf (Dataproc-set
    on AoU). For interactive shell `gsutil` commands inside the
    Workbench, use `gsutil -u "$GOOGLE_PROJECT" ...`.

Per-region branching (RESEARCH Q5):
    region_class == 'small'   -> Path A.1: to_numpy + savez_compressed
    region_class == 'medium'  -> Path A.2: sparsify_triangle + to_numpy + savez
    region_class == 'large'/'xlarge' -> Path A.3: BlockMatrix.write to bucket
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # avoid hail import at module load time (graceful local import)
    import hail as hl
    import numpy as np

# Verified against AoU CDR v8 docs (2026-05-01; per DEC-2026-05-01-01 v7→v8
# adoption). ANCESTRY_FIELD column name preserved between v7 and v8 per the
# v8 ancestry_preds.tsv header inspection (Run 2 in
# m3-W1-AUX-PATH-VERIFICATION.md). Reverify at submission.
ANCESTRY_FIELD = "ancestry_pred"
# Documented AoU ancestry_pred label space (CDRv7 docs reference; for column
# annotation only). The M3 manifest only emits AFR/EUR rows per D-M3-02.
ANCESTRY_VALUES = {"afr", "amr", "eas", "eur", "sas", "mid", "oth"}
# WR-007 (2026-05-01): runtime-supported ancestries for the LD-panel build.
# Tightened from ANCESTRY_VALUES to match the M2 manifest scope (D-M3-02);
# any other label (mid/oth/etc.) would run a no-op QC chain and waste
# cluster-hours producing a checkpoint nobody can use downstream.
SUPPORTED_ANCESTRIES = {"afr", "eur"}

# KING third-degree-or-closer threshold (D-M3-07 conservative pin)
KING_KINSHIP_THRESHOLD = 0.0442

# AoU CDR version pin (DEC-2026-05-01-01: v7→v8 adoption; O2 trigger fired
# 2026-05-01 because Workbench bound WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH to v8
# by default and v8 ancestry_preds.tsv has ~+69% participants over v7).
# v7 paths still resolve but v8 is canonical going forward.
CDR_VERSION = "v8"
AUX_BASE = f"gs://fc-aou-datasets-controlled/{CDR_VERSION}/wgs/short_read/snpindel/aux"
RELATED_SAMPLES_PATH = f"{AUX_BASE}/relatedness/relatedness_flagged_samples.tsv"
RELATEDNESS_FULL_PATH = f"{AUX_BASE}/relatedness/relatedness.tsv"
ANCESTRY_PREDS_PATH = f"{AUX_BASE}/ancestry/ancestry_preds.tsv"  # VERIFIED 2026-05-01 via AoU Workbench v8 AUX path check (Run 2)

# Sample QC thresholds (AOU-LD-PIPELINE.md §3.1)
MIN_CALL_RATE_SAMPLE = 0.98
HET_HOM_SD_BAND = 3.0

# Variant QC thresholds (AOU-LD-PIPELINE.md §4)
MIN_MAF_INTERNAL = 0.005
MAX_MAF = 0.995  # 1 - MIN_MAF_INTERNAL
MIN_CALL_RATE_VARIANT = 0.95
MIN_HWE_PVALUE = 1e-6

# Region-class -> Path-A branch thresholds (RESEARCH Q5)
PATH_A1_MAX_MB = 5     # to_numpy direct
PATH_A2_MAX_MB = 10    # sparsify_triangle + to_numpy
# > 10 Mb -> Path A.3 (BlockMatrix write to bucket; densify NCSU-side)

# Skip threshold (matches AOU-LD-PIPELINE.md §5.1 line 186)
MIN_VARIANTS_PER_REGION = 10


def _require_env(name: str) -> str:
    """Read AoU env var; raise RuntimeError with a helpful message if missing."""
    v = os.environ.get(name)
    if v is None:
        raise RuntimeError(
            f"AoU env var ${name} is not set. This driver runs (a) inside "
            f"the AoU Researcher Workbench where AoU sets it automatically, "
            f"or (b) locally with the mock_aou_env pytest fixture. Neither "
            f"applies right now."
        )
    return v


def init_hail(default_reference: str = "GRCh38",
              log_path: str = "/tmp/hail.log",
              spark_conf: dict | None = None) -> None:
    """Wrap hl.init(...) with AoU-friendly defaults.

    Idempotent: if hail is already initialized, no-op.
    """
    import hail as hl

    try:
        # If already initialized, hl.current_backend() returns the running backend.
        hl.current_backend()
        return
    except Exception:
        pass
    init_kwargs = {
        "default_reference": default_reference,
        "log": log_path,
        "quiet": True,
    }
    if spark_conf is not None:
        init_kwargs["spark_conf"] = spark_conf
    hl.init(**init_kwargs)


def _normalize_bucket(bucket: str) -> str:
    """Normalize a bucket reference to bare-name form.

    AoU's ``$WORKSPACE_BUCKET`` env var includes the ``gs://`` protocol prefix
    (e.g. ``gs://fc-secure-XXX``); local tests, CLI flag inputs, and other
    call sites historically pass bare bucket names. URI builders in this
    module assume bare form so they can unambiguously prepend the protocol.
    This helper makes callers tolerant of either input form: strips an
    optional ``gs://`` prefix and any leading/trailing slashes. Pure function;
    no validation (callers handle empty-input cases on their own).

    Closes the producer/consumer drift at the helper boundary surfaced
    2026-05-14 during AOU-1 Wave 1 fire on AoU Workbench (quick task
    260514-m3-W1-bucket-prefix-defensive), where the AOU-1 notebook caller
    pattern ``_qc_checkpoint_uri(os.environ['WORKSPACE_BUCKET'], ...)``
    produced malformed ``gs://gs://fc-secure-.../ld/mt_*.mt`` URIs under the
    prior bare-only contract.

    Examples:
        >>> _normalize_bucket("gs://fc-secure-XXX")
        'fc-secure-XXX'
        >>> _normalize_bucket("fc-secure-XXX")
        'fc-secure-XXX'
        >>> _normalize_bucket("gs://fc-secure-XXX/")
        'fc-secure-XXX'
        >>> _normalize_bucket(_normalize_bucket("gs://x"))
        'x'
    """
    return bucket.removeprefix("gs://").strip("/")


def _qc_checkpoint_uri(bucket: str, ancestry: str, sensitivity: bool) -> str:
    """Construct the QC-cohort checkpoint URI.

    Per W1 must_have (D-M3-07 sensitivity branch), sensitivity=True AFR
    cohorts MUST write to a distinct path from the primary AFR cohort --
    otherwise the sensitivity fire silently overwrites the primary
    checkpoint at the shared mt_afr_qc.mt URI. Three downstream notebooks
    (AOU-1 cohort_summary table, AOU-2 per-region LD, AOU-4 validation)
    already expect the mt_afr_pca_selfid_qc.mt path; this helper closes
    the consumer/producer drift surfaced 2026-05-12 during the AOU-1
    notebook fire.

    Accepts ``bucket`` in either bare-name form (``"fc-secure-XXX"``) or
    already-prefixed URI form (``"gs://fc-secure-XXX"``). Normalizes via
    :func:`_normalize_bucket` before construction (defensive boundary
    closure added 2026-05-14 by quick 260514-m3-W1-bucket-prefix-defensive
    after the prior bare-only contract produced ``gs://gs://...`` malformed
    URIs from the AoU notebook caller).
    """
    suffix = "_pca_selfid_qc" if sensitivity else "_qc"
    return f"gs://{_normalize_bucket(bucket)}/ld/mt_{ancestry}{suffix}.mt"


def _intermediate_checkpoint_uri(bucket: str, ancestry: str, phase: str,
                                  sensitivity: bool,
                                  interval_filter: str | None = None) -> str:
    """Construct an intermediate-checkpoint URI inside /ld/intermediate/.

    Args:
        bucket: Workspace bucket (bare-name or gs://-prefixed; normalized
            via :func:`_normalize_bucket`).
        ancestry: "afr" or "eur".
        phase: "post_split" or "post_sample_qc".
        sensitivity: When True, appends "_pca_selfid" before phase suffix
            (matches the existing _qc_checkpoint_uri convention).
        interval_filter: When set (e.g., "chr22" for smoke), appends
            "_{interval}" to the URI for path-level isolation between
            smoke and production paths. Defense in depth alongside
            sidecar-level mismatch detection. Per DESIGN §3.3.

    Examples:
        >>> _intermediate_checkpoint_uri("bkt", "afr", "post_split", False)
        'gs://bkt/ld/intermediate/mt_afr_post_split.mt'
        >>> _intermediate_checkpoint_uri("bkt", "afr", "post_split", True, "chr22")
        'gs://bkt/ld/intermediate/mt_afr_pca_selfid_post_split_chr22.mt'
    """
    sens_suffix = "_pca_selfid" if sensitivity else ""
    interval_suffix = f"_{interval_filter}" if interval_filter else ""
    return (
        f"gs://{_normalize_bucket(bucket)}/ld/intermediate/"
        f"mt_{ancestry}{sens_suffix}_{phase}{interval_suffix}.mt"
    )


def load_qc_cohort(mt_path: str, ancestry: str, sensitivity: bool = False,
                   ancestry_table_path: str | None = None,
                   relateds_table_path: str | None = None,
                   workspace_bucket: str | None = None,
                   skip_checkpoint: bool = False) -> "hl.MatrixTable":
    """Load + cohort-define + QC-filter the AoU AFR/EUR cohort.

    Implements the canonical ordering per RESEARCH.md (split_multi_hts BEFORE
    variant_qc; corrects spec §5.1 inversion).

    Args:
        mt_path: Path to the AoU MatrixTable (typically
            ``$WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH`` inside AoU; locally points
            at the synthetic MT fixture).
        ancestry: "afr" or "eur" (lowercase, matches ancestry_pred values).
        sensitivity: If True, additionally restrict to samples self-reporting
            Black or African American (AOU-LD-PIPELINE.md §3.2 sensitivity).
        ancestry_table_path: Override ANCESTRY_PREDS_PATH (mostly used by
            tests; production reads from the AoU-hardcoded path).
        relateds_table_path: Override RELATED_SAMPLES_PATH (tests only).
        workspace_bucket: Override $WORKSPACE_BUCKET; if None and not
            skip_checkpoint, reads from env.
        skip_checkpoint: Skip the gs:// checkpoint write (used by tests
            against synthetic MT — no real bucket available).

    Returns:
        QC-filtered ``hl.MatrixTable`` ready for per-region LD computation.
    """
    import hail as hl

    if ancestry not in SUPPORTED_ANCESTRIES:
        raise ValueError(
            f"ancestry={ancestry!r} not supported in M3; the manifest "
            f"emits {sorted(SUPPORTED_ANCESTRIES)}. Documented AoU pred "
            f"labels are {sorted(ANCESTRY_VALUES)} but routing here only "
            f"covers AFR/EUR (D-M3-02)."
        )
    anc_path = ancestry_table_path or ANCESTRY_PREDS_PATH
    rel_path = relateds_table_path or RELATED_SAMPLES_PATH

    # Step 1: load the AoU MT (or local synthetic MT)
    mt = hl.read_matrix_table(mt_path)

    # Step 2: cohort filter on ancestry_pred. The AoU ancestry predictions
    # arrive as a TSV (not a Hail Table); use hl.import_table with the
    # research_id key. For local synthetic MT testing, the ancestry field
    # may already be annotated on cols — detect and short-circuit.
    if ANCESTRY_FIELD in mt.col:
        # synthetic / pre-annotated path
        mt = mt.filter_cols(mt[ANCESTRY_FIELD] == ancestry)
    else:
        anc_ht = hl.import_table(anc_path, key="research_id",
                                 types={"research_id": hl.tstr})
        mt = mt.annotate_cols(**{ANCESTRY_FIELD: anc_ht[mt.s][ANCESTRY_FIELD]})
        mt = mt.filter_cols(mt[ANCESTRY_FIELD] == ancestry)

    # Step 3: anti-join against AoU's flagged-relateds TSV (KING >= 0.0442
    # third-degree pruning). For tests, the rel_path may be missing or
    # synthetic; tolerate that.
    try:
        rel_ht = hl.import_table(rel_path, key="sample_id",
                                 types={"sample_id": hl.tstr})
        mt = mt.anti_join_cols(rel_ht)
    except Exception as e:
        print(f"WARN: relateds table unavailable ({rel_path}): {e}; "
              f"skipping anti_join", file=sys.stderr)

    # Optional sensitivity: self-reported Black or African American.
    if sensitivity and "self_report" in mt.col:
        mt = mt.filter_cols(mt.self_report.contains("Black or African American"))

    # m3-W2 OOM remediation (DEC-2026-05-04-01): naive_coalesce post-ancestry.
    # Reduces row-partition count (~290,384 v8 partitions -> 2048) before the
    # three downstream materialization stages (split_multi_hts, sample_qc,
    # aggregate_cols for het_stats) so Hail RegionPool memory pressure stays
    # within executor headroom. Receipt: m3-W2-forensics/2026-05-04-stage8-regionpool-oom/.
    mt = mt.naive_coalesce(2048)

    # Step 4: split_multi_hts BEFORE variant_qc (canonical ordering).
    mt = hl.split_multi_hts(mt)

    # Step 5: sample_qc + call_rate >= 0.98
    mt = hl.sample_qc(mt, name="sqc")
    mt = mt.filter_cols(mt.sqc.call_rate >= MIN_CALL_RATE_SAMPLE)

    # Step 6: heterozygosity ±3 SD (computed within the ancestry-filtered cohort)
    het_stats = mt.aggregate_cols(hl.agg.stats(mt.sqc.r_het_hom_var))
    if het_stats.stdev is not None and het_stats.stdev > 0:
        lo = het_stats.mean - HET_HOM_SD_BAND * het_stats.stdev
        hi = het_stats.mean + HET_HOM_SD_BAND * het_stats.stdev
        mt = mt.filter_cols((mt.sqc.r_het_hom_var >= lo) &
                            (mt.sqc.r_het_hom_var <= hi))

    # Step 7: variant_qc + MAF/HWE/call_rate
    mt = hl.variant_qc(mt, name="vqc")
    mt = mt.filter_rows(
        (mt.vqc.AF[1] >= MIN_MAF_INTERNAL) &
        (mt.vqc.AF[1] <= MAX_MAF) &
        (mt.vqc.call_rate >= MIN_CALL_RATE_VARIANT) &
        (mt.vqc.p_value_hwe >= MIN_HWE_PVALUE)
    )

    # Step 8: drop AoU-flagged variants (filters non-empty)
    if "filters" in mt.row:
        mt = mt.filter_rows(hl.len(mt.filters) == 0)

    # Step 9: checkpoint to workspace bucket so per-region loops don't
    # recompute the QC chain. Skip for synthetic-MT tests.
    if not skip_checkpoint:
        bucket = workspace_bucket or os.environ.get("WORKSPACE_BUCKET")
        if not bucket:
            raise RuntimeError("WORKSPACE_BUCKET not set; cannot checkpoint")
        ckpt = _qc_checkpoint_uri(bucket, ancestry, sensitivity)
        mt = mt.checkpoint(ckpt, overwrite=True)
    return mt


def compute_region_ld(region_row: dict, mt_source: "hl.MatrixTable",
                      out_bucket: str | None = None,
                      out_local_dir: Path | None = None) -> dict:
    """Compute per-region LD matrix.

    Path-A branching per region_class (RESEARCH Q5):
        small (<= 5 Mb)        -> Path A.1: to_numpy + np.savez_compressed
        medium (5 - 10 Mb)     -> Path A.2: sparsify_triangle + to_numpy + savez
        large/xlarge (> 10 Mb) -> Path A.3: BlockMatrix.write(gs://) for NCSU densification

    Returns a dict with keys: region_id, status, n_var, path_a, out (path/uri).

    Skip threshold: regions with n_var < MIN_VARIANTS_PER_REGION return
    status='skipped_few_variants' (matches AOU-LD-PIPELINE.md §5.1 line 187).
    """
    import hail as hl
    import numpy as np

    rid = region_row["region_id"]
    chrom = str(region_row["chr"])
    if not chrom.startswith("chr"):
        chrom = f"chr{chrom}"
    start_b38 = int(region_row["start_grch38"])
    end_b38 = int(region_row["end_grch38"])
    radius_bp = int(region_row["radius_bp"])
    region_class = region_row["region_class"]

    interval = hl.parse_locus_interval(
        f"{chrom}:{start_b38}-{end_b38}", reference_genome="GRCh38",
    )
    mt_r = hl.filter_intervals(mt_source, [interval])
    n_var = mt_r.count_rows()
    if n_var < MIN_VARIANTS_PER_REGION:
        return {"region_id": rid, "status": "skipped_few_variants", "n_var": n_var,
                "path_a": "skip", "out": None}

    # hl.ld_matrix returns a BlockMatrix of Pearson correlations on n_alt_alleles dosages
    ld_bm = hl.ld_matrix(
        mt_r.GT.n_alt_alleles(),
        mt_r.locus,
        radius=radius_bp,
    )
    # CR-002 fix (2026-05-01): collect variant_ids and rsids in a SINGLE
    # aggregate_rows traversal to guarantee row-order alignment between the
    # two sidecar vectors. Both come from the same MT row pass; row order
    # within an aggregate_rows call is implicitly the MT key (locus,
    # alleles), which matches hl.ld_matrix's row indexing (also keyed by
    # locus). Two separate aggregate_rows calls are deterministic in
    # current Hail but the contract is "no row order guarantee" — coupling
    # them in one struct collect closes the silent-misalignment hole.
    has_rsid = "rsid" in mt_r.row
    if has_rsid:
        aligned = mt_r.aggregate_rows(
            hl.agg.collect(
                hl.struct(
                    vid=hl.str(mt_r.locus) + ":" + mt_r.alleles[0] + ":" + mt_r.alleles[1],
                    rsid=hl.coalesce(mt_r.rsid, hl.str("")),
                )
            )
        )
    else:
        aligned = mt_r.aggregate_rows(
            hl.agg.collect(
                hl.struct(
                    vid=hl.str(mt_r.locus) + ":" + mt_r.alleles[0] + ":" + mt_r.alleles[1],
                    rsid=hl.str(""),
                )
            )
        )
    variant_ids = [a.vid for a in aligned]
    rsids = [a.rsid if a.rsid is not None else "" for a in aligned]
    # IR-003 defensive assertion: variant_ids/rsids row count must equal n_var
    # (the BlockMatrix row count). A divergence here means hl.ld_matrix and
    # aggregate_rows traversed mt_r with inconsistent row sets — should not
    # happen, but the .npz consumers assume strict 1:1 alignment.
    assert len(variant_ids) == n_var, (
        f"variant_ids count {len(variant_ids)} != n_var {n_var} for region {rid}"
    )
    assert len(rsids) == n_var, (
        f"rsids count {len(rsids)} != n_var {n_var} for region {rid}"
    )

    span_mb = (end_b38 - start_b38) / 1_000_000
    if region_class == "small" or span_mb <= PATH_A1_MAX_MB:
        path_a = "A.1"
        ld_np = ld_bm.to_numpy().astype("float32")
        out_uri = _save_npz(rid, ld_np, variant_ids, rsids, out_bucket, out_local_dir)
    elif region_class == "medium" or span_mb <= PATH_A2_MAX_MB:
        path_a = "A.2"
        # Sparsify lower triangle in place; result is still a BlockMatrix
        ld_bm_lt = ld_bm.sparsify_triangle(lower=True)
        ld_np = ld_bm_lt.to_numpy().astype("float32")
        out_uri = _save_npz(rid, ld_np, variant_ids, rsids, out_bucket, out_local_dir,
                            lower_triangular=True)
    else:
        path_a = "A.3"
        # Never densify on driver for large/xlarge regions.
        # CR-003 fix (2026-05-01): emit variant_ids.tsv + rsids.tsv sidecars
        # alongside the BlockMatrix write so bm_to_npz.py (Wave 3 NCSU-side
        # converter) can ingest the BlockMatrix directory. Without these
        # sidecars, conversion fails with "sidecar TSV missing" — blocking
        # the dev-fire HLA + 8p23 stress regions and Wave 4 production for
        # the 36 large/xlarge regions.
        if out_bucket is None:
            # Local-test path: write to a temp local dir
            local_path = (out_local_dir or Path("/tmp")) / "bm" / f"{rid}.bm"
            local_path.parent.mkdir(parents=True, exist_ok=True)
            ld_bm.write(str(local_path), overwrite=True)
            # Sidecars beside the .bm directory (matches bm_to_npz.py CLI)
            sidecar_dir = local_path.parent
            np.savetxt(
                str(sidecar_dir / f"{rid}.variant_ids.tsv"),
                np.array(variant_ids, dtype=object),
                fmt="%s",
            )
            np.savetxt(
                str(sidecar_dir / f"{rid}.rsids.tsv"),
                np.array(rsids, dtype=object),
                fmt="%s",
            )
            out_uri = str(local_path)
        else:
            bm_uri = f"{out_bucket}/bm/{rid}.bm"
            ld_bm.write(bm_uri, overwrite=True)
            # Upload sidecar TSVs to the same gs://.../bm/ prefix so the
            # NCSU-side gsutil cp -r picks them up alongside the .bm dir.
            for sidecar_name, payload in (
                (f"{rid}.variant_ids.tsv", variant_ids),
                (f"{rid}.rsids.tsv", rsids),
            ):
                local_tmp = Path("/tmp") / sidecar_name
                np.savetxt(str(local_tmp), np.array(payload, dtype=object), fmt="%s")
                _upload_to_gcs(
                    local_path=local_tmp,
                    out_bucket=out_bucket,
                    blob_subpath=f"bm/{sidecar_name}",
                )
            out_uri = bm_uri

    return {
        "region_id": rid, "status": "ok", "n_var": n_var,
        "path_a": path_a, "out": out_uri,
    }


def _upload_to_gcs(local_path: Path, out_bucket: str, blob_subpath: str) -> str | None:
    """Upload a local file to ``{out_bucket}/{blob_subpath}``.

    out_bucket is "gs://bucket/prefix"; blob_subpath is appended after the
    optional prefix (e.g., "bm/m2_region_00120.variant_ids.tsv"). Returns
    the gs:// URI on success; None on failure (warning printed to stderr).

    Centralises the GCS upload code shared between Path A.1/A.2 (.npz) and
    Path A.3 (BlockMatrix sidecar TSVs) per CR-003 refactor.
    """
    try:
        from google.cloud import storage  # noqa: WPS433 -- lazy import (test envs lack google-cloud-storage)

        assert out_bucket.startswith("gs://")
        stripped = out_bucket[len("gs://"):]
        bucket_name, _, prefix = stripped.partition("/")
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob_path = f"{prefix}/{blob_subpath}" if prefix else blob_subpath
        bucket.blob(blob_path).upload_from_filename(str(local_path))
        return f"{out_bucket}/{blob_subpath}"
    except Exception as e:
        print(
            f"WARN: GCS upload failed ({out_bucket}/{blob_subpath}): {e}",
            file=sys.stderr,
        )
        return None


def _save_npz(region_id: str, ld_np: "np.ndarray", variant_ids: list,
              rsids: list, out_bucket: str | None, out_local_dir: Path | None,
              lower_triangular: bool = False) -> str:
    """Save dense LD as .npz (locally + optionally upload to GCS bucket)."""
    import numpy as np

    out_local_dir = out_local_dir or Path("/tmp")
    out_local_dir.mkdir(parents=True, exist_ok=True)
    local_path = out_local_dir / f"{region_id}.npz"
    np.savez_compressed(
        local_path,
        ld=ld_np,
        variant_ids=np.array(variant_ids),
        rsids=np.array(rsids),
        lower_triangular=np.array([lower_triangular]),
    )
    if out_bucket is not None:
        uri = _upload_to_gcs(
            local_path=local_path,
            out_bucket=out_bucket,
            blob_subpath=f"{region_id}.npz",
        )
        if uri is not None:
            return uri
    return str(local_path)


def _read_manifest(manifest_path: Path) -> list[dict]:
    """Read config/ld_regions.tsv (or _dev.tsv) -> list of dicts."""
    import pandas as pd

    df = pd.read_csv(manifest_path, sep="\t")
    return df.to_dict(orient="records")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path,
                        help="Region manifest TSV (config/ld_regions{,_dev}.tsv)")
    parser.add_argument("--ancestry", required=True, choices=["afr", "eur"])
    parser.add_argument("--mt-path", default=None,
                        help="Override $WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH")
    parser.add_argument("--out-bucket", default=None,
                        help="GCS bucket prefix; defaults to gs://${WORKSPACE_BUCKET}/ld/{ANCESTRY}_aou")
    parser.add_argument("--out-local-dir", type=Path, default=None,
                        help="Local scratch dir for .npz before upload")
    parser.add_argument("--log", default=None, help="Output run log TSV")
    parser.add_argument("--sensitivity", action="store_true",
                        help="Use AFR self-report sensitivity cohort (D-M3-07)")
    parser.add_argument("--skip-checkpoint", action="store_true",
                        help="Skip gs:// checkpoint (synthetic MT testing only)")
    args = parser.parse_args(argv)

    init_hail()
    mt_path = args.mt_path or _require_env("WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH")
    out_bucket = args.out_bucket
    if out_bucket is None and not args.skip_checkpoint:
        # Defensive: AoU's $WORKSPACE_BUCKET is prefixed (gs://fc-secure-...);
        # some local CLI uses pass bare. Normalize before prepending protocol
        # (closes the gs://gs:// double-prefix bug pattern surfaced 2026-05-14;
        # see _normalize_bucket docstring + quick 260514-m3-W1-bucket-prefix-defensive).
        ws = _normalize_bucket(_require_env("WORKSPACE_BUCKET"))
        anc_upper = args.ancestry.upper()
        out_bucket = f"gs://{ws}/ld/{anc_upper}_aou"

    mt = load_qc_cohort(
        mt_path=mt_path, ancestry=args.ancestry, sensitivity=args.sensitivity,
        skip_checkpoint=args.skip_checkpoint,
    )
    regions = _read_manifest(args.manifest)
    # Filter to ancestry of interest (manifest carries AFR + EUR rows)
    regions = [r for r in regions if str(r.get("ancestry", "")).lower() == args.ancestry]

    results = []
    for r in regions:
        t0 = time.time()
        try:
            res = compute_region_ld(r, mt, out_bucket=out_bucket,
                                    out_local_dir=args.out_local_dir)
        except Exception as e:
            res = {"region_id": r["region_id"], "status": f"error: {e}",
                   "n_var": -1, "path_a": "error", "out": None}
        res["wall_seconds"] = round(time.time() - t0, 1)
        results.append(res)
        print(json.dumps(res), flush=True)

    if args.log:
        import pandas as pd
        pd.DataFrame(results).to_csv(args.log, sep="\t", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
