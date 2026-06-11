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
    5. mt = hl.variant_qc(mt, name='vqc'); MAF/HWE/call_rate
    6. mt = hl.sample_qc(mt, name='sqc'); call_rate >= 0.98 over QC-passing
       variants + het
    7. mt = filter_rows hl.len(mt.filters) == 0  (drop AoU-flagged variants)
       # variant_qc precedes sample_qc so per-sample call_rate is computed over
       # QC-passing variants (m3-gatec-sample-callrate-ordering-collapse).
    8. mt = mt.checkpoint(_qc_checkpoint_uri(bucket, ancestry, sensitivity))
       # path: gs://${WORKSPACE_BUCKET}/ld/mt_{ancestry}[_pca_selfid]_qc.mt
    9. for region: hl.ld_matrix(..., radius=region.radius_bp)

Verified env vars (RESEARCH Q9):
    WORKSPACE_BUCKET                   - workspace egress staging (AoU-set)
    GOOGLE_PROJECT                     - billing (AoU-set)
    WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH - AoU-provided ACAF MT path (AoU-set)

Auxiliary paths (ancestry_preds.tsv + relatedness_flagged_samples.tsv):
    ENV-DERIVED at runtime from the WGS MT path the cohort is built from, via
    _resolve_aux_base() (DEC-2026-06-01). The aux/ dir is a documented SIBLING
    of acaf_threshold/ under .../wgs/short_read/snpindel/, so the tables track
    whatever CDR version the platform binds (v8, v9, ...) with no code edit --
    this closes the manual Workbench AUX-path-verification gate (CHECK C) on
    the RW 2.0 R8->R9 migration. The hardcoded
    gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux/ literal
    (CDR_VERSION below) is now the OFFLINE/LOCAL FALLBACK only, used when no
    AoU WGS path is present (synthetic-MT tests, offline imports). The v8 layout
    was empirically VERIFIED 2026-05-01 (Run 2, m3-W1-AUX-PATH-VERIFICATION.md;
    v7->v8 per DEC-2026-05-01-01). A genuine CDR-source change correctly
    invalidates stale checkpoints (force_fresh rebuild); env-derivation is about
    path RESOLUTION, not cross-version checkpoint reuse.

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
#
# These module constants are now the OFFLINE/LOCAL FALLBACK only. At runtime
# inside the Workbench, load_qc_cohort derives the AUX base from the WGS MT
# path it is actually reading via _resolve_aux_base() — so the ancestry /
# relatedness tables track whatever CDR version the platform binds (v8, v9,
# ...) without a code edit. The constants are used when no AoU WGS path is
# available (local synthetic-MT tests, offline imports) and as the documented
# pin value recorded in provenance. (DEC-2026-06-01: env-derive AUX base —
# closes CHECK-C as a manual gate; see [[feedback_extract_reusable_utilities]].)
CDR_VERSION = "v8"
AUX_BASE = f"gs://fc-aou-datasets-controlled/{CDR_VERSION}/wgs/short_read/snpindel/aux"
RELATED_SAMPLES_PATH = f"{AUX_BASE}/relatedness/relatedness_flagged_samples.tsv"
ANCESTRY_PREDS_PATH = f"{AUX_BASE}/ancestry/ancestry_preds.tsv"  # VERIFIED 2026-05-01 via AoU Workbench v8 AUX path check (Run 2)

# AFR sensitivity (D-M3-07) self-reported-race sidecar. UNLIKE ancestry_preds /
# relatedness_flagged_samples (AoU-shipped genomic aux files under aux/), AoU
# self-reported race lives in the CDR `person` table and is NOT shipped as an
# aux TSV. The runbook extracts it via BigQuery (person.race source value ->
# research_id, self_report) and stages it under aux/self_report/ so the SAME
# _resolve_aux_file discover-by-suffix machinery (mirroring ancestry_preds.tsv)
# resolves it. The self-report restriction is MANDATORY for the sensitivity
# cohort -> on_ambiguous="raise" + hard-fail when unresolvable (the ancestry
# discipline), never a silent skip. See
# .planning/debug/m3-W2-afr-sensitivity-selfid-noop.md.
SELF_REPORT_FIELD = "self_report"
SELF_REPORT_SUBDIR = "self_report"
SELF_REPORT_SUFFIX = "self_report.tsv"
SELF_REPORT_PATH = f"{AUX_BASE}/{SELF_REPORT_SUBDIR}/{SELF_REPORT_SUFFIX}"
# person.race SOURCE-VALUE CODE the AFR sensitivity cohort restricts to (string
# .contains match). We match the stable AoU survey answer CODE
# (`race_source_value`), NOT the human-readable display string: a live
# C2024Q3R9 `GROUP BY race_source_value` (2026-06-08) showed the Black answer is
# coded 'WhatRaceEthnicity_Black' (99,788), and the display string
# "Black or African American" is only produced by a fragile concept-name JOIN
# (race_source_concept_id -> concept.concept_name) that AoU often names
# "Black, African American, or African" instead -> COALESCE falls back to the
# code -> the old display-string match silently matched ZERO. The code is
# release-stable and empirically confirmed; the extractor emits race_source_value
# verbatim so producer/consumer agree. See
# .planning/debug/m3-W2-afr-sensitivity-selfid-noop.md.
SELF_REPORT_AFR_MATCH = "WhatRaceEthnicity_Black"
# Bump on ANY change to the sensitivity-restriction semantics (match string,
# coverage policy, sourcing). Threaded into provenance so a change auto-
# invalidates intermediates (belt-and-suspenders atop the runbook purge).
# v2 (2026-06-08): match the race_source_value code, not the display string.
SENS_FILTER_VERSION = "2"
# Defense in depth: require self_report non-null for ~all in-scope samples, else
# the sidecar is malformed / mis-keyed and the cohort would silently shrink.
MIN_SELF_REPORT_COVERAGE = 0.95

# Stable infix in every AoU controlled-tier WGS path; the aux/ directory is a
# documented sibling of acaf_threshold/ under it (verified 2026-05-01 Run 2;
# m3-W1-AUX-PATH-VERIFICATION.md).
_WGS_PATH_INFIX = "/wgs/short_read/snpindel/"


def _resolve_aux_base(mt_path: str | None = None) -> str:
    """Derive the AoU controlled-tier AUX base from the WGS ACAF MatrixTable
    path, so the ancestry/relatedness sidecar tables track whatever CDR
    version the platform binds (v8, v9, ...) instead of a hardcoded literal.

    The aux/ directory is a documented SIBLING of acaf_threshold/ under
    ``.../wgs/short_read/snpindel/`` (empirically verified 2026-05-01 Run 2;
    see m3-W1-AUX-PATH-VERIFICATION.md). We split the WGS MT path on that
    stable infix and rebuild ``<prefix>/wgs/short_read/snpindel/aux``.

    Resolution order:
      1. explicit ``mt_path`` arg — the WGS MT ``load_qc_cohort`` actually reads
      2. ``$WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH`` — the env var AoU binds
      3. the hardcoded ``AUX_BASE`` literal — offline/local/tests (pre-refactor
         behavior preserved)

    Falls back to ``AUX_BASE`` whenever the source path is absent or does not
    contain the AoU WGS infix (e.g. local synthetic-MT test paths). This makes
    the v7→v8→v9 CDR transition a no-op for this code path and removes the
    manual Workbench AUX-path-verification gate (CHECK C) from the critical
    path on the RW 2.0 R8→R9 migration.
    """
    candidate = mt_path or os.environ.get("WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH")
    if candidate and _WGS_PATH_INFIX in candidate:
        prefix = candidate.split(_WGS_PATH_INFIX, 1)[0]
        # Guard: the prefix must carry a URI scheme (gs://, file://). A
        # pathological path that starts with the infix yields an empty prefix
        # and would build a malformed root-rooted '/wgs/.../aux'; fall back to
        # the literal in that case rather than return a broken path.
        if "://" in prefix:
            return f"{prefix}{_WGS_PATH_INFIX}aux"
    return AUX_BASE


def _hail_hadoop_lister(dirpath: str) -> list[str]:
    """Production directory lister: Hail ``hadoop_ls`` over a gs:// dir.

    Uses the AoU Spark/Hadoop GCS connector (requester-pays project already
    configured in the Workbench), so it lists the same controlled-tier bucket
    the cohort reads from. Returns full entry paths.
    """
    import hail as hl
    return [entry["path"] for entry in hl.hadoop_ls(dirpath)]


def _resolve_aux_file(aux_base: str, subdir: str, suffix: str,
                      lister=None, *, on_ambiguous: str = "raise") -> str:
    """Resolve a specific AUX table inside ``aux/<subdir>/`` by its canonical
    SUFFIX, robust to the pipeline-version filename prefix AoU prepends.

    On RW 2.0 / cdrv8-R8 the files carry prefixes the bare-name code missed
    (verified live 2026-06-01 via a CHECK-C 404):
        aux/ancestry/echo_v4_r2.ancestry_preds.tsv
        aux/relatedness/samples_relatedness_flagged_samples.tsv
    Those prefixes (``echo_v4_r2.``, ``samples_``) are pipeline-version strings
    that will drift again, so we DISCOVER the file by the stable suffix
    (``ancestry_preds.tsv`` / ``relatedness_flagged_samples.tsv``) instead of
    pinning the prefix — the same "discover, don't pin" posture as
    ``_resolve_aux_base`` (DEC-2026-06-01).

    Args:
        aux_base: the env-derived AUX base (``_resolve_aux_base``).
        subdir: ``"ancestry"`` or ``"relatedness"``.
        suffix: the bare canonical filename to match on (endswith).
        lister: callable(dir) -> list[str] of entry paths (full gs:// paths in
            production via ``_hail_hadoop_lister``; injected in tests). The
            basename is extracted (``rstrip('/')`` first, so subdir entries like
            ``echo_v4_r2_loadings.ht/`` are handled). If ``None``
            (local/offline/tests) returns the bare ``<aux_base>/<subdir>/<suffix>``
            (pre-discovery behavior preserved).
        on_ambiguous: behavior when >1 entry matches the suffix. ``"raise"``
            (default; used for the MANDATORY ancestry table — refuse to guess)
            vs ``"fallback"`` (used for the BEST-EFFORT relatedness table —
            WARN + bare, so a transient rollout collision degrades to the
            soft-skip path the import-site try/except already handles, rather
            than hard-crashing the cohort load).

    Resolution:
        1 match  -> the discovered (possibly prefixed) path.
        0 matches -> WARN + bare fallback. The import site keeps its existing
            semantics: ancestry hard-fails loudly, relatedness soft-fails via
            its try/except — the resolver does not guess.
        >1 matches -> RuntimeError (on_ambiguous="raise") or WARN+bare
            (on_ambiguous="fallback").
    """
    bare = f"{aux_base}/{subdir}/{suffix}"
    if lister is None:
        return bare
    dirpath = f"{aux_base}/{subdir}"
    matches = sorted(
        e for e in lister(dirpath)
        if e.rstrip("/").rsplit("/", 1)[-1].endswith(suffix)
    )
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        msg = (f"Ambiguous AUX file: {len(matches)} entries under {dirpath} "
               f"end with {suffix!r}: {matches}.")
        if on_ambiguous == "fallback":
            print(f"[load_qc_cohort] WARN: {msg} Falling back to bare {bare} "
                  f"(best-effort table; anti_join may be skipped).",
                  file=sys.stderr)
            return bare
        raise RuntimeError(f"{msg} Refusing to guess.")
    print(f"[load_qc_cohort] WARN: no entry under {dirpath} ends with "
          f"{suffix!r}; falling back to bare {bare}", file=sys.stderr)
    return bare


# Sample QC thresholds (AOU-LD-PIPELINE.md §3.1)
MIN_CALL_RATE_SAMPLE = 0.98
HET_HOM_SD_BAND = 3.0

# Raw (pre-variant-QC) in-scope variant count below which the per-sample
# call_rate sample filter is SKIPPED as a nano-smoke convenience
# (.planning/debug/m3-gateb-nano-sample-axis-collapse.md). After the
# variant-QC-before-sample-QC reorder (m3-gatec-sample-callrate-ordering-
# collapse, 2026-06-04), sqc.call_rate is measured over the QC-passing clean
# variant set, so the 0.98 threshold is satisfiable at every real tier; this
# guard NO LONGER masks the ordering bug (the reorder fixed that). It now
# keys on the RAW interval size purely to decide "real tier vs nano smoke
# window": at nano scale a 2 Mb window has too few QC-passing variants for a
# meaningful per-sample call_rate, so the filter is skipped to keep the nano
# smoke tier a clean PASS. Derivation: nano density ~59.5K variants/Mb (Gate B
# nano chr22:16-18Mb = ~119K over 2 Mb); whole-chr22 raw ~1.86M. 500K is ~4x
# the nano count and ~4x below the smallest real tier (chr22-full), so it
# NEVER trips at whole-chromosome-or-larger scale (genome-wide QC thresholds
# untouched) and ALWAYS trips at nano. The guard is captured on the RAW count
# BEFORE variant_qc and persisted to the post_variant_qc sidecar so a resume
# applies the same decision. Mirrors the het filter's `stdev > 0` degeneracy
# guard.
MIN_VARIANTS_FOR_SAMPLE_CALLRATE = 500_000

# GRCh38 autosomes (chr1..chr22). The LD panel is AUTOSOMAL per the M2 region
# manifest scope (no chrX/Y/M). Used by the genome-wide per-chromosome fan-out
# in load_qc_cohort (interval_filter=None): every Hail action is bounded to one
# chromosome's partition set -- the exact condition under which the chr22 Gate-C
# run passed -- so the driver never has to materialize the un-pruned whole-genome
# plan over the ~145k-partition v8 source in one shot (the genome-wide first-
# action wedge; .planning/debug/m3-W2-genome-wide-countcols-py4j-wedge.md).
AUTOSOMES = tuple(f"chr{i}" for i in range(1, 23))

# Variant QC thresholds (AOU-LD-PIPELINE.md §4)
MIN_MAF_INTERNAL = 0.005
MAX_MAF = 0.995  # 1 - MIN_MAF_INTERNAL
MIN_CALL_RATE_VARIANT = 0.95
MIN_HWE_PVALUE = 1e-6

# Cohort partition target for the balanced-QC phase (DEC-2026-05-04-01 "Q3
# hybrid" remediation for the v8 ~145k-partition explosion). naive_coalesce
# reduces the source MT to this count cheaply (no shuffle). The post-split
# REBALANCE to this target is then done on the checkpoint READ-BACK via
# read_matrix_table(_n_partitions=...), NOT via a pre-write mt.repartition()
# -- repartition(shuffle=True) before a write builds a RangePartitioner by
# sampling keys across all input partitions and routes through a driver-side
# SpillingCollectIterator gather (the m3-gateb-load-qc-cohort-driver-collect
# indefinite stall, 2026-06-02). The Hail core team's guidance is explicit:
# repartition AFTER you've written data with too many partitions, not before
# (discuss.hail.is "best way to repartition heavily-filtered matrix tables").
_COHORT_TARGET_PARTITIONS = 2048

# Export MAF floor (Q6 lock, 260520-s2s-CONTEXT.md): 0.005 overrides
# AOU-LD-PIPELINE.md §7.2 default of 0.01. Rationale: M2-novel AFR variants
# concentrate in the 0.005-0.01 band (m3-RESEARCH.md Q10); dropping them at
# export forfeits the AFR-specific signal the project exists to capture.
# feedback_rigor_over_speed.md.
#
# Pinned equal to MIN_MAF_INTERNAL for the Wave 2 dev fire; may decouple later
# if cohort/variant pathology surfaces in dev-10 (RESEARCH Q10 halt check
# applies: if a dev-10 region shows > 50% variant-drop at 0.005 vs 0.01,
# halt at Carter checkpoint).
MAF_THRESHOLD_EXPORT = 0.005

# Region-class -> Path-A branch thresholds (RESEARCH Q5)
PATH_A1_MAX_MB = 5     # to_numpy direct
PATH_A2_MAX_MB = 10    # sparsify_triangle + to_numpy
# > 10 Mb -> Path A.3 (BlockMatrix write to bucket; densify NCSU-side)


def _route_region_path(region_class: "str | None", span_mb: float) -> str:
    """Select the Path-A export branch for a region, with an OOM safety veto.

    region_class is the Wave-0 pinned routing label (D-M3-09); span_mb is the
    region span and the true OOM determinant. Paths A.1/A.2 end in
    ``BlockMatrix.to_numpy()`` -- an O(n_var**2) DRIVER-side dense collect -- so a
    large-span region routed there OOMs the driver.

    m3-W2 pre-fire audit (2026-06-04) HIGH-1: the Wave-0 manifest
    (build_ld_region_manifest.CLASS_MEDIUM_MAX_MB=25) classes regions up to 25 Mb
    as "medium", but to_numpy OOMs the driver far below that (a ~24 Mb region at
    AFR density is a ~200+ GB dense float32; 86 of the 322 config cells are
    small/medium-classed yet span > PATH_A2_MAX_MB). So region_class ALONE must
    not route into to_numpy. This applies the region_class routing, then a HARD
    span veto: any A.1/A.2 whose span exceeds PATH_A2_MAX_MB is demoted to A.3
    (BlockMatrix streaming write, never densified on the driver).

    Returns one of "A.1", "A.2", "A.3".
    """
    if region_class == "small" or span_mb <= PATH_A1_MAX_MB:
        path_a = "A.1"
    elif region_class == "medium" or span_mb <= PATH_A2_MAX_MB:
        path_a = "A.2"
    else:
        path_a = "A.3"
    # OOM safety veto: never to_numpy() a region whose span exceeds the A.2 cap.
    if path_a in ("A.1", "A.2") and span_mb > PATH_A2_MAX_MB:
        path_a = "A.3"
    return path_a

# Skip threshold (matches AOU-LD-PIPELINE.md §5.1 line 186)
MIN_VARIANTS_PER_REGION = 10

# Minimum byte size for an existing region .npz to be trusted as a completed
# idempotent result (m3-W2 audit MED-6). The idempotency guard must NOT skip a
# 0-byte / truncated .npz left by a websocket-drop mid-write -- that is the same
# "exists != populated" blind spot as the m3-W1 empty-MT catastrophe
# ([[feedback_aou_success_marker_not_evidence_of_data]]). A real LD .npz for the
# >=10-variant floor is comfortably > 256 B; a partial write is 0 / a few bytes.
_MIN_REGION_NPZ_BYTES = 256


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


def _sanitize_interval_suffix(interval_filter: str) -> str:
    """Sanitize an INTERVAL token into a filesystem/URI-safe path suffix.

    Replaces ``:`` and ``-`` with ``_`` so a span-bounded GRCh38 interval
    (``"chr22:16000000-18000000"``) becomes a path-safe token
    (``"chr22_16000000_18000000"``). A bare whole-chromosome token
    (``"chr22"``) passes through unchanged.

    WHY (m3-gateb-load-qc-cohort-driver-collect, 2026-06-02 follow-on): GCS
    tolerates a colon on the checkpoint WRITE, but the post-write read-back
    ``hl.read_matrix_table(...)`` routes the URI through Hadoop's Path/URI
    parser, which reads ``"chr22:"`` as a URI *scheme* and raises
    ``java.net.URISyntaxException: Relative path in absolute URI``. The
    Tier-2 ``"chr22"`` default (no colon) never exercised the path.

    This is the single sanitization point for INTERVAL-derived suffixes; it
    encapsulates the same ``.replace(":", "_").replace("-", "_")`` convention
    the AOU-1 smoke notebook applies to its final-output ``_suffix`` (so the
    intermediate checkpoint name matches the final cohort MT naming).

    Examples:
        >>> _sanitize_interval_suffix("chr22")
        'chr22'
        >>> _sanitize_interval_suffix("chr22:16000000-18000000")
        'chr22_16000000_18000000'
    """
    return interval_filter.replace(":", "_").replace("-", "_")


def _intermediate_checkpoint_uri(bucket: str, ancestry: str, phase: str,
                                  sensitivity: bool,
                                  interval_filter: str | None = None) -> str:
    """Construct an intermediate-checkpoint URI inside /ld/intermediate/.

    Args:
        bucket: Workspace bucket (bare-name or gs://-prefixed; normalized
            via :func:`_normalize_bucket`).
        ancestry: "afr" or "eur".
        phase: "post_split" or "post_variant_qc".
        sensitivity: When True, appends "_pca_selfid" before phase suffix
            (matches the existing _qc_checkpoint_uri convention).
        interval_filter: When set (e.g., "chr22" for smoke, or a span-bounded
            nano interval like "chr22:16000000-18000000"), appends a
            URI-safe "_{interval}" to the URI for path-level isolation
            between smoke and production paths. The interval is sanitized via
            :func:`_sanitize_interval_suffix` (``:`` and ``-`` -> ``_``) so the
            colon does not break the post-write read-back's Hadoop URI parse
            (m3-gateb-load-qc-cohort-driver-collect, 2026-06-02 follow-on).
            Defense in depth alongside sidecar-level mismatch detection.
            Per DESIGN §3.3.

    Examples:
        >>> _intermediate_checkpoint_uri("bkt", "afr", "post_split", False)
        'gs://bkt/ld/intermediate/mt_afr_post_split.mt'
        >>> _intermediate_checkpoint_uri("bkt", "afr", "post_split", True, "chr22")
        'gs://bkt/ld/intermediate/mt_afr_pca_selfid_post_split_chr22.mt'
        >>> _intermediate_checkpoint_uri("bkt", "afr", "post_split", False,
        ...                              "chr22:16000000-18000000")
        'gs://bkt/ld/intermediate/mt_afr_post_split_chr22_16000000_18000000.mt'
    """
    sens_suffix = "_pca_selfid" if sensitivity else ""
    interval_suffix = (
        f"_{_sanitize_interval_suffix(interval_filter)}" if interval_filter else ""
    )
    return (
        f"gs://{_normalize_bucket(bucket)}/ld/intermediate/"
        f"mt_{ancestry}{sens_suffix}_{phase}{interval_suffix}.mt"
    )


def _sidecar_uri(checkpoint_uri: str) -> str:
    """Sidecar JSON path is the checkpoint URI + '.meta.json'.

    Hail MT checkpoints are directories (containing _SUCCESS + parquet
    parts); the sidecar lives as a sibling JSON file at the same parent
    level. The '.meta.json' extension is chosen to avoid colliding with
    any Hail/Spark-managed files inside the MT directory tree.
    """
    return checkpoint_uri + ".meta.json"


def _collect_provenance(ancestry: str, sensitivity: bool,
                         source_mt_path: str,
                         interval_filter: str | None = None,
                         ancestry_preds_path: str | None = None,
                         relateds_path: str | None = None,
                         self_report_path: str | None = None) -> dict:
    """Collect provenance metadata for sidecar write.

    Builds the JSON-serializable dict that becomes the sidecar contents.
    DOES NOT include 'phase' field — that is added by _write_sidecar at
    write time so the same provenance dict can be written to both
    post_split and post_variant_qc sidecars.

    Per DESIGN §3.4: conservative semantics — all QC parameters are
    captured regardless of which phase consumes them. Any parameter
    change invalidates ALL intermediates for the same (ancestry,
    sensitivity, interval_filter) tuple.
    """
    import datetime
    import subprocess

    # Best-effort: capture git SHA. Falls back to "unknown" if not a git
    # checkout (e.g., tests in tmp_path that don't preserve git context).
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(Path(__file__).parent.parent.parent),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        sha = "unknown"

    # Best-effort: capture hail version. Falls back if hail not importable.
    try:
        import hail as hl
        hv = hl.__version__
    except ImportError:
        hv = "unknown"

    return {
        "ancestry": ancestry,
        "sensitivity": sensitivity,
        "interval_filter": interval_filter,
        "source_mt_path": source_mt_path,
        "params": {
            "MIN_CALL_RATE_SAMPLE": MIN_CALL_RATE_SAMPLE,
            "MIN_MAF_INTERNAL": MIN_MAF_INTERNAL,
            "MAX_MAF": MAX_MAF,
            "MIN_CALL_RATE_VARIANT": MIN_CALL_RATE_VARIANT,
            "MIN_HWE_PVALUE": MIN_HWE_PVALUE,
            "HET_HOM_SD_BAND": HET_HOM_SD_BAND,
            "KING_KINSHIP_THRESHOLD": KING_KINSHIP_THRESHOLD,
            # Nano-degeneracy floor for the call_rate sample filter. A change
            # to it alters which cohorts are call-rate-QC'd, so it invalidates
            # intermediates symmetric with the other QC thresholds. The
            # RUNTIME OUTCOME of the guard (whether the filter actually ran on
            # this fire) is a per-fire result, NOT a parameter -- it is
            # threaded separately into the post_variant_qc sidecar via
            # _write_sidecar(sample_callrate_filtered=...) so it does not
            # participate in resume-validation comparison.
            "MIN_VARIANTS_FOR_SAMPLE_CALLRATE": MIN_VARIANTS_FOR_SAMPLE_CALLRATE,
        },
        # Record the RESOLVED paths actually read (env-derived under R9), not
        # the hardcoded literal — provenance reproducibility contract. Falls
        # back to the module constants for callers that don't pass overrides.
        "ancestry_preds_path": ancestry_preds_path or ANCESTRY_PREDS_PATH,
        "relateds_path": relateds_path or RELATED_SAMPLES_PATH,
        # AFR sensitivity self-report sidecar + restriction version. Recorded
        # ONLY for the sensitivity cohort (None on the primary, so the primary
        # provenance is byte-stable -- the EUR/AFR-primary builds are
        # unaffected). A change to SENS_FILTER_VERSION (or the resolved
        # self_report_path) flips the sidecar -> auto-invalidates the
        # sensitivity intermediates on the next fire.
        "self_report_path": (self_report_path or SELF_REPORT_PATH) if sensitivity else None,
        "sens_filter_version": SENS_FILTER_VERSION if sensitivity else None,
        "cdr_version": CDR_VERSION,
        "git_commit_sha": sha,
        "hail_version": hv,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "schema_version": 1,
    }


def _open_sidecar(uri: str, mode: str):
    """Open a sidecar URI, dispatching by scheme.

    - 'file://' URIs use plain Python open() so local-FS tests don't
      require Hail to be importable.
    - All other URIs (gs://, s3://, etc.) defer to hl.hadoop_open for
      unified distributed-FS handling in production AoU Dataproc.

    Returns the open file handle (caller must close it via context
    manager).
    """
    if uri.startswith("file://"):
        local_path = uri[len("file://"):]
        return open(local_path, mode)
    import hail as hl
    return hl.hadoop_open(uri, mode)


def _write_sidecar(uri: str, provenance: dict, phase: str,
                   sample_callrate_filtered: bool | None = None) -> None:
    """Write provenance JSON sidecar at uri.

    Adds 'phase' field to a copy of provenance before serialization so
    the input dict is not mutated (caller may reuse it for the next
    phase's sidecar in the same load_qc_cohort fire).

    Order matters: callers MUST invoke this AFTER the matching
    mt.checkpoint() returns successfully. Per DESIGN §4 atomicity policy:
    a crash window between checkpoint write and sidecar write leaves an
    orphan MT; next fire detects sidecar absence and auto-force-fresh's.

    Args:
        uri: Sidecar URI. Local-FS tests pass "file:///path/to/sidecar.meta.json";
            production AoU passes "gs://bucket/ld/intermediate/mt_*.mt.meta.json".
        provenance: Output of _collect_provenance (does NOT include 'phase').
        phase: One of {"post_split", "post_variant_qc"}.
        sample_callrate_filtered: The raw-count guard DECISION (will the
            call_rate sample filter be applied), recorded on the post_variant_qc
            sidecar so a resume restores it. Excluded from resume-validation
            comparison. True if the filter will be applied (raw in-scope variant
            count >= MIN_VARIANTS_FOR_SAMPLE_CALLRATE), False if skipped (raw
            count below the threshold -- nano smoke tier). Recorded ONLY for the
            post_variant_qc sidecar (the phase where the raw-count decision is
            made); None for post_split (the decision has not been made yet) so
            no flag is written. It is EXCLUDED from resume-validation comparison
            (_SIDECAR_COMPARE_EXCLUDE_FIELDS) because it is an outcome, not a
            parameter. See
            .planning/debug/m3-gateb-nano-sample-axis-collapse.md +
            [[feedback_aou_success_marker_not_evidence_of_data]].
    """
    payload = {**provenance, "phase": phase}
    if sample_callrate_filtered is not None:
        payload["sample_callrate_filtered"] = sample_callrate_filtered
    with _open_sidecar(uri, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def _read_sidecar(uri: str) -> dict | None:
    """Read provenance JSON sidecar at uri.

    Returns:
        Parsed dict on success, None if the sidecar file does not exist.

    Raises:
        RuntimeError: if the sidecar exists but has malformed JSON or
            an unknown schema_version. Loud failure is intentional —
            silently treating bad sidecars as schema_version=1 risks
            using stale-format metadata.
    """
    try:
        with _open_sidecar(uri, "r") as f:
            content = f.read()
    except (FileNotFoundError, OSError):
        return None
    # hail.hadoop_open also raises generic exceptions on missing GCS objects;
    # broad-catch path-existence failures and return None.
    if not content:
        return None
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Sidecar at {uri} is malformed JSON: {e}")
    sv = parsed.get("schema_version")
    if sv != 1:
        raise RuntimeError(
            f"Sidecar at {uri} has unknown schema_version={sv!r}; "
            f"expected 1. Refusing to interpret as known schema."
        )
    return parsed


# Fields that legitimately differ between sidecar and current call.
# Excluded from _validate_sidecar comparison.
_SIDECAR_COMPARE_EXCLUDE_FIELDS = frozenset({
    "phase",            # phase is per-sidecar; not a fire-level parameter
    "timestamp_utc",    # write time; drifts across runs of same params
    "git_commit_sha",   # audit metadata; non-breaking code changes ok
    "hail_version",     # build-environment; ok to drift across runs
    # Per-fire OUTCOME of the nano-degeneracy guard (whether the call_rate
    # sample filter will run), recorded ONLY in the post_variant_qc
    # sidecar. It is a result, not an input parameter, so it must not
    # participate in resume-validation comparison -- comparing it would
    # spuriously invalidate a post_variant_qc intermediate. See
    # .planning/debug/m3-gateb-nano-sample-axis-collapse.md +
    # [[feedback_aou_success_marker_not_evidence_of_data]].
    "sample_callrate_filtered",
})


def _validate_sidecar(sidecar: dict, provenance: dict) -> tuple[bool, str]:
    """Compare sidecar against current provenance dict.

    Returns:
        (True, "") if all relevant fields match.
        (False, diagnostic_str) if any relevant field differs. The
        diagnostic enumerates the mismatched field names + values for
        each side (sidecar vs current).

    Comparison rules per DESIGN §3.4 + v2 CHANGELOG:
        - All top-level fields are compared EXCEPT those in
          _SIDECAR_COMPARE_EXCLUDE_FIELDS (phase, timestamp_utc,
          git_commit_sha, hail_version).
        - 'params' dict is compared element-by-element. Any threshold
          difference is a mismatch.

    Conservative semantics: ANY divergence outside the excluded set
    invalidates the intermediate. Caller passes force_fresh=True to
    override.
    """
    mismatches = []
    # Top-level fields
    sidecar_keys = set(sidecar.keys()) - _SIDECAR_COMPARE_EXCLUDE_FIELDS
    provenance_keys = set(provenance.keys()) - _SIDECAR_COMPARE_EXCLUDE_FIELDS
    for k in sorted(sidecar_keys | provenance_keys):
        if k == "params":
            continue  # handled separately below
        sv = sidecar.get(k, "<absent>")
        pv = provenance.get(k, "<absent>")
        if sv != pv:
            mismatches.append(f"  {k}: sidecar={sv!r} current={pv!r}")
    # Params dict
    sidecar_params = sidecar.get("params", {})
    provenance_params = provenance.get("params", {})
    for k in sorted(set(sidecar_params.keys()) | set(provenance_params.keys())):
        sv = sidecar_params.get(k, "<absent>")
        pv = provenance_params.get(k, "<absent>")
        if sv != pv:
            mismatches.append(f"  params.{k}: sidecar={sv!r} current={pv!r}")
    if not mismatches:
        return True, ""
    diag = (
        f"mismatch on {len(mismatches)} field(s):\n"
        + "\n".join(mismatches)
    )
    return False, diag


def _has_checkpoint(uri: str) -> bool:
    """Check for {uri}/_SUCCESS marker (definitive completion signal).

    Hail's mt.checkpoint() writes parquet files into the MT directory
    and finalizes with an atomic _SUCCESS marker. Existence of the
    _SUCCESS marker is the definitive "this checkpoint was written
    successfully" signal — partial writes (interrupted, crashed) leave
    parquet shards but no _SUCCESS.

    GCS object existence is strongly consistent (Google's 2020
    consistency model upgrade — read-after-write on individual objects).
    False-negative due to list-operation eventual-consistency edge cases
    would result in redundant work (re-firing a completed phase), not
    corruption.

    Scheme dispatch: 'file://' uses pathlib for local-FS tests without
    a Hail dependency; all other schemes defer to hl.hadoop_is_file.

    WARNING: _has_checkpoint() only verifies the _SUCCESS marker exists.
    The m3-W1 empty-MT catastrophe (2026-05-21) proved this is NOT
    sufficient evidence of populated data — Hail's driver-side finalize()
    writes _SUCCESS on tasks-reported-complete accounting WITHOUT
    validating output contents. For resume-gate decisions, use
    :func:`_validate_checkpoint_populated` instead.
    """
    success_marker_uri = f"{uri}/_SUCCESS"
    if uri.startswith("file://"):
        local_path = Path(success_marker_uri[len("file://"):])
        return local_path.is_file()
    try:
        import hail as hl
        return hl.hadoop_is_file(success_marker_uri)
    except Exception:
        # Defensive: any filesystem error during the existence check
        # is treated as "checkpoint not present" — safer to redo work
        # than to assume a checkpoint that may not actually exist.
        return False


# Minimum entries-file byte size that constitutes "populated" content.
# The m3-W1 catastrophe bucket forensics 2026-05-21 observed 35-byte
# Parquet column-metadata footer stubs in rows/rows/parts/ (zero
# row-group payload). A populated Hail MT partition file is at least
# tens of KB even for tiny test fixtures. 1 KB cleanly discriminates
# footer-only stubs from real partition contents.
MIN_ENTRIES_FILE_BYTES = 1024


def _validate_checkpoint_populated(uri: str, *,
                                    min_entries_bytes: int = MIN_ENTRIES_FILE_BYTES
                                    ) -> bool:
    """Strict resume-gate: _SUCCESS + non-empty entries/ row-group payload.

    Contents-validating replacement for :func:`_has_checkpoint`. Defends
    against the m3-W1 empty-MT catastrophe class
    (.planning/debug/m3-W1-empty-mt-catastrophe.md), where Hail's
    driver-side ``finalize()`` writes ``_SUCCESS`` on tasks-reported-
    complete accounting WITHOUT validating that executor tasks actually
    wrote row-group payloads. Under aggressive
    ``spark.executor.cores=1/mem=5g`` profile (necessary for v8
    partition-explosion OOM remediation), executor tasks can silently
    truncate after writing Parquet schema footers — producing an MT
    directory with ``_SUCCESS`` + 35-byte rows-stubs + footer-only
    ``entries/rows/parts/`` (the 2026-05-21 catastrophe signature; the
    only true empty-vs-populated discriminator was count_rows/count_cols,
    NOT a "missing entries dir" — see m3-entries-path-phantom-subpath).

    NOTE (m3-entries-path-phantom-subpath, 2026-06-03): real Hail 0.2.135
    stores entry row-group payload at ``entries/rows/parts/`` — NOT the
    phantom ``entries/entries/parts/`` the original Track-4 probe used.

    Validation steps:
      1. ``_has_checkpoint(uri)`` — ``_SUCCESS`` must exist.
      2. ``{uri}/entries/rows/parts/`` directory must exist.
      3. At least one file in ``entries/rows/parts/`` must exceed
         ``min_entries_bytes`` (default 1 KB; filters footer stubs).

    Scheme dispatch mirrors :func:`_has_checkpoint`: ``file://`` uses
    pathlib for local-FS tests without a Hail dependency; all other
    schemes defer to ``hl.hadoop_ls``. Defensive ``try/except``: any
    filesystem error during validation returns False — safer to redo
    work than to assume a populated checkpoint that may not exist.

    Used by :func:`load_qc_cohort`'s auto-resume state machine
    (DESIGN §3.5) as the canonical resume-gate. Any new code path that
    needs to decide "is this MT real?" must use this helper, not
    :func:`_has_checkpoint`.

    Cross-references:
      - [[feedback_aou_success_marker_not_evidence_of_data]]
      - [[feedback_hail_checkpoint_contract_violation]]

    Args:
        uri: MT directory URI. ``file://`` for tests; ``gs://`` in production.
        min_entries_bytes: Threshold below which an entries-part file is
            considered a stub. Keyword-only; default
            :data:`MIN_ENTRIES_FILE_BYTES`.

    Returns:
        True iff _SUCCESS + entries-dir + ≥1 populated entries-part.
    """
    if not _has_checkpoint(uri):
        return False
    entries_dir_uri = f"{uri}/entries/rows/parts"
    if uri.startswith("file://"):
        entries_dir = Path(entries_dir_uri[len("file://"):])
        if not entries_dir.is_dir():
            return False
        try:
            for entry in entries_dir.iterdir():
                if entry.is_file() and entry.stat().st_size > min_entries_bytes:
                    return True
        except OSError:
            return False
        return False
    try:
        import hail as hl
        # hl.hadoop_ls returns a list of stat-dicts with 'path' and
        # 'size_bytes' keys; FileNotFoundError if the dir is absent.
        listing = hl.hadoop_ls(entries_dir_uri)
        for entry in listing:
            size = entry.get("size_bytes", entry.get("size", 0))
            if size and size > min_entries_bytes:
                return True
        return False
    except Exception:
        # Defensive: filesystem error, missing entries dir, or hail not
        # importable all yield "not populated" — safer to redo work
        # than to resume from a potentially empty checkpoint.
        return False


# Sentinel marker written into a FINAL cohort MT directory ONLY after the MT has
# passed _assert_checkpoint_nonempty. Closes the m3-W2 empty-final window
# (.planning/debug/resolved/m3-W2-afr-sens-empty-final-merge.md): Hail's
# mt.checkpoint() writes the canonical _SUCCESS on driver-side task accounting
# BEFORE our post-write validation runs, so a driver kill in the
# checkpoint->assert window (the 2026-06-10 H1 catastrophe — a stray browser
# navigation killed the finalize flush) leaves a lying _SUCCESS over 0-byte
# contents. A canonical _VALIDATED marker is written only AFTER the non-empty
# assertion passes, so the trustworthy-final contract is "_SUCCESS + _VALIDATED",
# NOT _SUCCESS alone. See [[feedback_aou_success_marker_not_evidence_of_data]].
VALIDATED_MARKER = "_VALIDATED"


def _has_marker(uri: str, marker: str) -> bool:
    """True iff ``{uri}/{marker}`` exists. Scheme dispatch mirrors
    :func:`_has_checkpoint`: ``file://`` uses pathlib (no Hail dependency for
    local tests); all other schemes defer to ``hl.hadoop_is_file``. Any
    filesystem error is treated as absent (safer to redo than to trust)."""
    marker_uri = f"{uri}/{marker}"
    if uri.startswith("file://"):
        return Path(marker_uri[len("file://"):]).is_file()
    try:
        import hail as hl
        return hl.hadoop_is_file(marker_uri)
    except Exception:
        return False


def _write_validated_marker(uri: str) -> None:
    """Write the ``{uri}/_VALIDATED`` sentinel (idempotent, empty file).

    Call ONLY after a final MT has passed :func:`_assert_checkpoint_nonempty`
    (see :data:`VALIDATED_MARKER`) — a present marker is the producer's stamp
    that the canonical contents were validated non-empty at write time. Scheme
    dispatch mirrors :func:`_has_marker`."""
    marker_uri = f"{uri}/{VALIDATED_MARKER}"
    if uri.startswith("file://"):
        Path(marker_uri[len("file://"):]).write_text("")
        return
    import hail as hl
    with hl.hadoop_open(marker_uri, "w") as f:
        f.write("")


def _final_is_trustworthy(uri: str) -> bool:
    """Consumer / resume gate for a FINAL cohort MT (mt_{ancestry}_qc.mt etc.).

    CONTENTS are the sole source of truth: returns
    :func:`_validate_checkpoint_populated` (the m3-W1 empty-MT catastrophe guard
    applied to the final). The ``_VALIDATED`` sentinel is producer-side
    DOCUMENTATION only (a canonical ``_SUCCESS`` *without* ``_VALIDATED`` flags a
    final that never passed post-write validation) and is deliberately **NOT** a
    trust fast-path: a stale ``_VALIDATED`` can survive a
    ``mt.checkpoint(overwrite=True)`` re-fire that is then killed mid-write, so
    trusting the marker alone would vouch for re-emptied contents — exactly the
    re-fire failure mode this project hit. Back-compat: the three already-banked
    cohorts carry no ``_VALIDATED`` and validate True via contents. The m3-W2
    empty-final signature (``_SUCCESS`` over 0-byte / footer-stub entries) returns
    False, so consumers reject a bad final instead of silently consuming it.

    NB: consumers must CALL this before reading a final — wiring it into the
    AOU-2 / AOU-4 notebook readers (raise on False) is the remaining phase-2 step
    (.planning/phases/m3-aou-afr-ld-panel-build/DURABLE-FIX-DESIGN-atomic-final-write.md)."""
    return _validate_checkpoint_populated(uri)


def read_final_cohort_mt(uri: str):
    """Gate-then-read a FINAL cohort MT (mt_afr_qc.mt / mt_eur_qc.mt /
    mt_afr_pca_selfid_qc.mt). Closes the read-side hole the m3-W2 empty-final
    catastrophe (2026-06-10) exposed: hl.read_matrix_table trusts _SUCCESS
    directly, so a lying _SUCCESS over 0-byte contents (driver killed mid
    finalize-flush) would propagate silently into LD compute. Call
    _final_is_trustworthy(uri) (CONTENTS-only) FIRST and RAISE on False, so
    the reject runs before any Hail read.
    See DURABLE-FIX-DESIGN-atomic-final-write.md +
    [[feedback_aou_success_marker_not_evidence_of_data]]."""
    if not _final_is_trustworthy(uri):
        raise RuntimeError(
            f"REFUSING to read untrustworthy final cohort MT: {uri}\n"
            f"_final_is_trustworthy() returned False — _SUCCESS is present but "
            f"the contents are empty/footer-stub (the m3-W2 empty-final "
            f"catastrophe class: a driver killed mid finalize-flush leaves a "
            f"lying _SUCCESS over 0-byte entries).\n"
            f"RECOVERY: re-finalize via force_fresh=False from the still-intact "
            f"22 per-chrom intermediates (a finalize-only re-drive, minutes not "
            f"hours — do NOT force_fresh=True). "
            f"See DURABLE-FIX-DESIGN-atomic-final-write.md."
        )
    import hail as hl
    return hl.read_matrix_table(uri)


def _post_split_read_partitions(available_partitions: int | None = None,
                                *,
                                target: int = _COHORT_TARGET_PARTITIONS) -> int:
    """Target partition count for the post-split checkpoint READ-BACK.

    Pure (Hail-free) so the partitioning decision is unit-testable without a
    live cluster. Replaces the pre-write ``mt.repartition(2048)`` that caused
    the m3-gateb-load-qc-cohort-driver-collect indefinite driver stall
    (2026-06-02): ``repartition(shuffle=True)`` before a write builds a
    RangePartitioner by sampling keys across all input partitions and routes
    through a driver-side ``SpillingCollectIterator`` gather. Rebalancing
    on the checkpoint read-back via ``read_matrix_table(_n_partitions=...)``
    uses the on-disk partition index instead — no key sampling, no driver
    collect (the Hail-team-recommended "repartition after write, not before").

    ``read_matrix_table(_n_partitions=N)`` coalesces DOWN to ``N``; it cannot
    fabricate more partitions than the checkpoint physically holds. So when the
    post-split MT has fewer partitions than ``target`` (e.g. a nano interval
    that pruned to a handful), clamp to what is available rather than
    over-requesting.

    Args:
        available_partitions: On-disk partition count of the post-split
            checkpoint, when known (``mt.n_partitions()`` is a cheap metadata
            read). ``None`` -> use ``target`` unconditionally (preserves the
            prior fixed-2048 behavior when the count is not threaded in).
        target: Desired balanced-QC partition count (default
            ``_COHORT_TARGET_PARTITIONS``).

    Returns:
        A positive partition count to pass as ``_n_partitions`` on read-back:
        ``min(target, available_partitions)`` when available is known,
        else ``target``.
    """
    if available_partitions is None:
        return target
    return max(1, min(target, int(available_partitions)))


def _assert_checkpoint_nonempty(mt: "hl.MatrixTable", uri: str,
                                 *, phase: str) -> None:
    """Raise loudly if a just-checkpointed MT is empty.

    Post-write contents validation — defense against the m3-W1 empty-MT
    catastrophe (2026-05-21). Hail's ``mt.checkpoint()`` writes the
    ``_SUCCESS`` marker on driver-side tasks-reported-complete accounting
    WITHOUT validating output contents. Under
    ``spark.executor.cores=1/mem=5g``, executor tasks can silently
    truncate after writing Parquet schema footers, leaving an MT
    skeleton that returns ``count_rows()=0 + count_cols()=0`` on read-back.

    Cell 7 of the W1 monolithic run would have caught this 36h earlier
    via ``mt_afr_selfid.count_rows()`` — this assertion builds that check
    INSIDE :func:`load_qc_cohort` so EVERY MT write self-validates,
    not just the final one that Cell 7 happens to query.

    Calls ``mt.count_rows()`` + ``mt.count_cols()`` (eager Hail actions —
    each forces a Spark job, so cost is ~10-30 sec on the populated path
    and the entire pipeline cost on the empty path which fails fast).
    On AoU production fires this adds ~3 Spark jobs per cohort = ~1-2
    min total overhead — trivial against the 60+ h monolithic-run cost,
    and exactly what would have caught the 2026-05-21 catastrophe
    BEFORE Cell 4 fired the next ancestry on top of an empty MT.

    Raises:
        RuntimeError: if ``count_rows() == 0`` or ``count_cols() == 0``,
            with the phase name, URI, and a pointer to the catastrophe
            debug document. Caller (``load_qc_cohort``) propagates the
            error up so the notebook cell halts before any downstream
            cohort defines on top of empty cohort.

    Cross-references:
      - .planning/debug/m3-W1-empty-mt-catastrophe.md
      - [[feedback_hail_checkpoint_contract_violation]]
      - [[feedback_aou_success_marker_not_evidence_of_data]]
    """
    n_rows = mt.count_rows()
    n_cols = mt.count_cols()
    if n_rows == 0 or n_cols == 0:
        head = (f"checkpoint at {uri} (phase={phase}) returned empty MT: "
                f"{n_rows} rows x {n_cols} cols. ")
        xref = (f"See .planning/debug/m3-W1-empty-mt-catastrophe.md + "
                f"[[feedback_hail_checkpoint_contract_violation]] + "
                f"[[feedback_aou_success_marker_not_evidence_of_data]].")
        if n_rows > 0 and n_cols == 0:
            # Sample (column) axis collapsed while variant rows survived: a QC
            # predicate dropped every sample (e.g. the call_rate sample filter
            # on a degenerate small span). This is NOT the m3-W1 finalize
            # catastrophe (which is 0x0).
            # See .planning/debug/m3-gateb-nano-sample-axis-collapse.md.
            raise RuntimeError(
                head +
                "sample (column) axis collapsed during "
                f"{phase} — every sample dropped by a QC predicate; check "
                "sample-QC filters / degeneracy guards. This is NOT the "
                "m3-W1 finalize catastrophe (which is 0x0). " + xref
            )
        if n_cols > 0 and n_rows == 0:
            # Variant (row) axis collapsed while samples survived: a QC
            # predicate dropped every variant. NOT the m3-W1 finalize
            # catastrophe (which is 0x0).
            raise RuntimeError(
                head +
                "variant (row) axis collapsed during "
                f"{phase} — every variant dropped by a QC predicate; check "
                "variant-QC filters / interval scope. This is NOT the "
                "m3-W1 finalize catastrophe (which is 0x0). " + xref
            )
        # True 0x0: the m3-W1 empty-MT finalize catastrophe signature.
        raise RuntimeError(
            head +
            "Hail's mt.checkpoint() wrote _SUCCESS but contents are missing "
            "— the m3-W1 empty-MT catastrophe signature. See "
            ".planning/debug/m3-W1-empty-mt-catastrophe.md + "
            "[[feedback_hail_checkpoint_contract_violation]]."
        )


# Documented minimum du soft-floor for ANY span (260601-u1b). Even a ~2 Mb
# nano-interval populated MT carries a few MB of entries row-group payload, so a
# floor below ~1 MB would never fire; a floor at a few MB still catches the
# m3-W1 footer-stub signature (~71 KiB total) while NOT false-positiving a
# legitimately small nano cohort. This is the soft-signal minimum, NOT a hard
# gate — _assert_checkpoint_nonempty's count_rows>0/count_cols>0 is the gate.
MIN_DU_FLOOR_BYTES = 2_000_000  # 2 MB

# Approximate GRCh38 chromosome lengths (bp) for du-floor span scaling. Only the
# chromosomes the LD panel touches need exact values; an unknown contig falls
# back to chr1's length (largest) so scaling is conservative (never over-floors).
# Source: GRCh38 primary assembly (rounded to the nearest 1e3); used ONLY to
# scale a DIAGNOSTIC soft-floor, so megabase-level rounding is immaterial.
_GRCH38_CHROM_LEN_BP = {
    "chr1": 248_956_422, "chr2": 242_193_529, "chr3": 198_295_559,
    "chr4": 190_214_555, "chr5": 181_538_259, "chr6": 170_805_979,
    "chr7": 159_345_973, "chr8": 145_138_636, "chr9": 138_394_717,
    "chr10": 133_797_422, "chr11": 135_086_622, "chr12": 133_275_309,
    "chr13": 114_364_328, "chr14": 107_043_718, "chr15": 101_991_189,
    "chr16": 90_338_345, "chr17": 83_257_441, "chr18": 80_373_285,
    "chr19": 58_617_616, "chr20": 64_444_167, "chr21": 46_709_983,
    "chr22": 50_818_468, "chrX": 156_040_895, "chrY": 57_227_415,
}
_DEFAULT_CHROM_LEN_BP = _GRCH38_CHROM_LEN_BP["chr1"]


def _interval_scaled_du_floor(interval_filter: str | None, *,
                              base_floor_bytes: int) -> int:
    """Return an interval-span-scaled du byte-floor (DIAGNOSTIC soft-signal).

    The notebook du-floor (historically a hardcoded 50 MB) is a SOFT diagnostic
    signal, NOT the catastrophe gate. The authoritative gate is
    :func:`_assert_checkpoint_nonempty`'s ``count_rows()>0 / count_cols()>0``
    assertion inside :func:`load_qc_cohort`, which is UNCHANGED by this helper.

    The 50 MB floor false-positives on a ~2 Mb nano-interval: a perfectly
    populated nano cohort carries only a few MB of ``entries/rows/parts/``
    payload, so the unscaled floor would FAIL a healthy nano fire and mask the
    real signal. This helper scales the floor DOWN for span-bounded intervals so
    a Tier-1 nano fire gets a proportionate floor, while NOT weakening the
    Tier-2 chr22 / full-genome check.

    Scaling policy:
      * ``interval_filter`` is ``None`` (full-genome) or a bare whole-chromosome
        token (``"chr22"`` — no ``:start-end`` span) → return ``base_floor_bytes``
        unchanged (NO down-scaling; the chr22-tier check stays at full strength).
      * a span-bounded interval (``"chr22:16000000-18000000"``) → scale by the
        span fraction of the chromosome:
        ``base_floor_bytes * span_bp / chrom_len_bp``, floored at
        :data:`MIN_DU_FLOOR_BYTES` (a few MB) and capped at ``base_floor_bytes``.

    The floor scales monotonically with span (wider span → larger floor) and
    never exceeds ``base_floor_bytes`` for a sub-chromosomal interval. Pure
    function — no I/O, fully unit-testable.

    Args:
        interval_filter: ``None``, a whole-chromosome token (``"chr22"``), or a
            span-bounded GRCh38 locus interval (``"chr22:16000000-18000000"``).
        base_floor_bytes: the full-genome / whole-chromosome floor the notebook
            passes in (the per-tier policy still lives in the notebook).

    Returns:
        An integer byte floor, in ``[MIN_DU_FLOOR_BYTES, base_floor_bytes]`` for
        a span-bounded interval, or exactly ``base_floor_bytes`` otherwise.
    """
    if not interval_filter or ":" not in interval_filter:
        # full-genome (None) or whole-chromosome ('chr22') — no down-scaling.
        return base_floor_bytes
    chrom, _, span = interval_filter.partition(":")
    try:
        start_s, _, end_s = span.partition("-")
        start_bp = int(start_s)
        end_bp = int(end_s)
        span_bp = max(0, end_bp - start_bp)
    except (ValueError, TypeError):
        # Unparseable span — fall back to the full base floor (conservative;
        # never under-floors on a malformed interval string).
        return base_floor_bytes
    chrom_len = _GRCH38_CHROM_LEN_BP.get(chrom, _DEFAULT_CHROM_LEN_BP)
    if chrom_len <= 0 or span_bp <= 0:
        return base_floor_bytes
    scaled = int(base_floor_bytes * span_bp / chrom_len)
    # Clamp into [MIN_DU_FLOOR_BYTES, base_floor_bytes].
    scaled = max(MIN_DU_FLOOR_BYTES, min(scaled, base_floor_bytes))
    return scaled


def _hail_hadoop_copy(src: str, dst: str) -> None:
    """Production file copier: Hail ``hadoop_copy`` (used for the hail.log
    preserve in :func:`_capture_catastrophe_forensics`). Injected in tests."""
    import hail as hl
    hl.hadoop_copy(src, dst)


def _spark_rest_active_stages(url: str) -> dict:
    """Production Spark-REST getter: GET ``<url>`` and parse JSON (best-effort
    active-stages snapshot). Injected in tests so no network is touched."""
    import json as _json
    import urllib.request
    with urllib.request.urlopen(url, timeout=5) as resp:  # nosec B310 - local Spark UI
        return _json.loads(resp.read().decode("utf-8"))


def _coerce_mtime(value) -> "float | None":
    """Normalize an ``hl.hadoop_ls`` ``modification_time`` to a comparable float.

    Hail's ``hadoop_ls`` does NOT guarantee an integer/float epoch for
    ``modification_time`` across versions/backends — historically it has been
    emitted as a formatted datetime STRING (e.g. ``'2026-05-21 14:03:22'``), and
    the production stat lister passes whatever Hail returns straight through.
    A naive numeric ``>`` comparison then either (a) raises ``TypeError`` on a
    mixed str/int pair — swallowed by the never-raise guard and silently
    degrading ``hypothesis_flag`` to ``'indeterminate'`` — or (b) compares
    same-format strings LEXICOGRAPHICALLY, which inverts across digit-length /
    date / format boundaries. Either way the W1-catastrophe distinguisher (the
    single mechanism the ``$2,140``-class re-fire decision hinges on) loses its
    value at the exact moment it matters (IN-01, remediation 260601-u1b).

    This normalizer is used on BOTH sides of the comparison so the flag decision
    is always on a common float scale. It NEVER raises (every parse is guarded);
    an uncoercible value returns ``None`` so it is dropped from the comparable
    set — and if nothing is comparable, ``'indeterminate'`` remains the honest
    answer, but a PARSEABLE string must NOT degrade.

    Accepts:
      * ``int`` / ``float`` epochs (returned verbatim as float);
      * numeric-as-string epochs (``'1700000000'``, including differing
        digit-lengths — compared numerically, not lexically);
      * common formatted timestamp strings: ``'YYYY-MM-DD HH:MM:SS'`` (the
        historical Hail form), ISO ``'YYYY-MM-DDTHH:MM:SS'``, a trailing ``Z``,
        and a ``.%f`` microsecond fraction.

    Returns:
        A ``float`` epoch (seconds) if coercible; otherwise ``None``.
    """
    try:
        if isinstance(value, bool):
            # bool is an int subclass; an mtime is never a bool, so reject it
            # rather than coerce True->1.0 / False->0.0.
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return None
            try:
                return float(s)  # numeric-as-string epoch (any digit-length)
            except ValueError:
                pass
            from datetime import datetime
            # Allow a trailing 'Z' (UTC designator) on ISO-like strings.
            s_norm = s[:-1] if s.endswith("Z") else s
            for fmt in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%f",
            ):
                try:
                    return datetime.strptime(s_norm, fmt).timestamp()
                except ValueError:
                    continue
    except Exception:  # noqa: BLE001 - the coercer must NEVER raise
        return None
    return None


def _capture_catastrophe_forensics(
    uri: str,
    *,
    phase: str,
    lister=None,
    copier=None,
    http_getter=None,
    bucket: str | None = None,
    log_path: str = "/tmp/hail.log",
    spark_rest_url: str = "http://localhost:4040/api/v1/applications",
    now=None,
    writer=None,
) -> dict:
    """Best-effort forensic capture at ANY Track-4 halt — NEVER raises.

    STANDALONE helper invoked by notebook cells on an ``AssertionError`` /
    ``RuntimeError`` from the Track-4 guards. It is DELIBERATELY NOT injected
    into :func:`_assert_checkpoint_nonempty`: keeping it standalone means the
    Track-4 guard's hard-fail/raise contract (``count_rows>0`` / ``count_cols>0``
    → ``RuntimeError``) is byte-for-byte unchanged. The notebook pattern is::

        try:
            _assert_checkpoint_nonempty(mt, uri, phase='afr')
            ... du soft-floor ...
        except Exception:
            _capture_catastrophe_forensics(uri, phase='afr')
            raise   # re-raise AFTER capture so the cell still halts loudly

    LOAD-BEARING DEFENSIVE GUARANTEE: forensic capture must NEVER take down the
    cell it is diagnosing. Every sub-step is wrapped in ``try/except``; on total
    failure the helper still returns a sentinel dict (carrying at least ``phase``
    + ``uri``) and never propagates. The caller's ``raise`` is what halts the
    cell — not this helper.

    Captures the hypothesis-distinguisher data
    ([[feedback_w1_catastrophe_hypothesis_distinguisher]]):

      (a) ``_SUCCESS`` mtime vs ``entries/rows/parts/`` part mtimes →
          ``hypothesis_flag``:
            * ``"hail_finalize_on_empty"`` — ``_SUCCESS`` mtime is at/after ALL
              part mtimes (Hail wrote ``_SUCCESS`` on driver-side task accounting
              after the executor writes; the debug-doc theory);
            * ``"kill_interrupted_write"`` — at least one part mtime is AFTER the
              ``_SUCCESS`` mtime (writes continued past the marker; Carter's
              kill-as-culprit theory);
            * ``"indeterminate"`` — listing/mtimes unavailable.
      (b) the MT directory listing + entries-part sizes;
      (c) copy ``/tmp/hail.log`` → ``<bucket>/ld/_forensics/<phase>_hail.log``;
      (d) a Spark-REST active-stages snapshot (best-effort HTTP/JSON);
      (e) a ``<bucket>/ld/_forensics/<phase>_capture.json`` with the gathered
          facts (json round-trippable; contains ``phase`` + ``uri``).

    Testability: side-effecting collaborators are injected as keyword params
    with production defaults (mirrors the existing ``lister=lambda d: entries``
    idiom). ``file://`` URIs are handled for the json-write path so tests run
    with no Hail / no network.

    Args:
        uri: the halted MT directory URI (``gs://`` in prod; ``file://`` in tests).
        phase: the cohort/phase label (``"afr"`` / ``"eur"`` / ``"probe"`` / ...);
            names the forensic artifacts.
        lister: ``callable(dir) -> list[stat-dict]``. Production default
            :func:`_hail_hadoop_lister`-style (``hl.hadoop_ls`` stat dicts with
            ``path`` + ``modification_time`` + ``size_bytes``). Injected in tests.
        copier: ``callable(src, dst) -> None`` for the hail.log preserve.
            Production default :func:`_hail_hadoop_copy`. Injected in tests.
        http_getter: ``callable(url) -> dict`` for the Spark-REST snapshot.
            Production default :func:`_spark_rest_active_stages`. Injected.
        bucket: forensic-artifact destination root (defaults to the parent of
            ``uri``'s ``/ld/...`` segment, else ``$WORKSPACE_BUCKET``). Artifacts
            land under ``<bucket>/ld/_forensics/``.
        log_path: hail.log source path (default ``/tmp/hail.log``).
        spark_rest_url: Spark REST applications endpoint (default localhost:4040).
        now: ``callable() -> float`` epoch source (defaults to ``time.time``).
        writer: ``callable(dest_uri, text) -> None`` json writer (defaults to a
            ``file://`` pathlib writer for ``file://`` dests, else
            ``hl.hadoop_open``). Injected in tests if desired.

    Returns:
        A dict of gathered forensic facts (always contains ``phase`` + ``uri``);
        NEVER ``None``, NEVER raises.
    """
    if now is None:
        now = time.time
    if lister is None:
        lister = _hail_hadoop_lister_stat
    if copier is None:
        copier = _hail_hadoop_copy
    if http_getter is None:
        http_getter = _spark_rest_active_stages

    capture: dict = {
        "phase": phase,
        "uri": uri,
        "captured_at": None,
        "hypothesis_flag": "indeterminate",
        "success_mtime": None,
        "entries_part_mtimes": [],
        "entries_part_sizes": [],
        "mt_listing": [],
        "hail_log_copied_to": None,
        "spark_active_stages": None,
        "errors": [],
    }
    try:
        capture["captured_at"] = now()
    except Exception as exc:  # noqa: BLE001 - never propagate from capture
        capture["errors"].append(f"now(): {exc!r}")

    # Resolve the forensics destination root.
    if bucket is None:
        try:
            bucket = os.environ.get("WORKSPACE_BUCKET")
        except Exception as exc:  # noqa: BLE001
            capture["errors"].append(f"bucket-resolve: {exc!r}")
    forensics_dir = f"{(bucket or '').rstrip('/')}/ld/_forensics" if bucket else None
    capture["forensics_dir"] = forensics_dir

    # (a)+(b): listing + _SUCCESS-mtime-vs-part-mtimes hypothesis distinguisher.
    try:
        entries_parts_dir = f"{uri.rstrip('/')}/entries/rows/parts"
        listing = lister(uri.rstrip("/"))
        capture["mt_listing"] = [e.get("path") for e in listing
                                 if isinstance(e, dict)]
        # _SUCCESS mtime
        success_mtime = None
        for e in listing:
            if isinstance(e, dict) and str(e.get("path", "")).rstrip("/").endswith("_SUCCESS"):
                success_mtime = e.get("modification_time")
                break
        # entries-part mtimes/sizes
        try:
            entries = lister(entries_parts_dir)
        except Exception:
            entries = [e for e in listing
                       if isinstance(e, dict)
                       and "/entries/rows/parts" in str(e.get("path", ""))]
        part_mtimes = [e.get("modification_time") for e in entries
                       if isinstance(e, dict) and not e.get("is_dir", False)
                       and "modification_time" in e]
        part_sizes = [e.get("size_bytes", e.get("size")) for e in entries
                      if isinstance(e, dict) and not e.get("is_dir", False)]
        # Store the RAW mtimes/sizes verbatim in the JSON (so a human can always
        # resolve the hypothesis manually); coercion below is ONLY for the flag.
        capture["success_mtime"] = success_mtime
        capture["entries_part_mtimes"] = part_mtimes
        capture["entries_part_sizes"] = part_sizes
        # Distinguisher: any part written AFTER _SUCCESS => kill-interrupted;
        # else _SUCCESS at/after all parts => hail-finalize-on-empty.
        # Coerce BOTH sides to a common float scale first (IN-01): Hail may emit
        # modification_time as an int/float epoch OR a formatted string; a naive
        # str-vs-int '>' raises TypeError (-> degrades to 'indeterminate') and a
        # same-width-string '>' compares lexicographically (inverts across
        # digit-length / date boundaries). A pair where EITHER side is
        # uncoercible is skipped; if nothing is comparable, 'indeterminate' is
        # the honest answer — but a parseable string must NOT degrade.
        success_cmp = _coerce_mtime(success_mtime)
        usable = [c for c in (_coerce_mtime(m) for m in part_mtimes)
                  if c is not None]
        if success_cmp is not None and usable:
            if any(c > success_cmp for c in usable):
                capture["hypothesis_flag"] = "kill_interrupted_write"
            else:
                capture["hypothesis_flag"] = "hail_finalize_on_empty"
        else:
            capture["hypothesis_flag"] = "indeterminate"
    except Exception as exc:  # noqa: BLE001 - never propagate
        capture["errors"].append(f"listing/distinguisher: {exc!r}")

    # (c): preserve /tmp/hail.log to the forensics dir (best-effort).
    if forensics_dir:
        try:
            dst = f"{forensics_dir}/{phase}_hail.log"
            copier(log_path, dst)
            capture["hail_log_copied_to"] = dst
        except Exception as exc:  # noqa: BLE001
            capture["errors"].append(f"hail.log-copy: {exc!r}")

    # (d): Spark-REST active-stages snapshot (best-effort).
    try:
        capture["spark_active_stages"] = http_getter(spark_rest_url)
    except Exception as exc:  # noqa: BLE001
        capture["errors"].append(f"spark-rest: {exc!r}")

    # (e): write the capture json (best-effort).
    if forensics_dir:
        try:
            capture_json_uri = f"{forensics_dir}/{phase}_capture.json"
            payload = json.dumps(capture, indent=2, default=str)
            if writer is not None:
                writer(capture_json_uri, payload)
            elif capture_json_uri.startswith("file://"):
                p = Path(capture_json_uri[len("file://"):])
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(payload)
            else:
                import hail as hl
                with hl.hadoop_open(capture_json_uri, "w") as fh:
                    fh.write(payload)
            capture["capture_json_uri"] = capture_json_uri
        except Exception as exc:  # noqa: BLE001
            capture["errors"].append(f"capture-json-write: {exc!r}")

    return capture


def _hail_hadoop_lister_stat(dirpath: str) -> list[dict]:
    """Production stat-dict lister: Hail ``hadoop_ls`` returning the FULL stat
    dicts (``path`` + ``modification_time`` + ``size_bytes`` + ``is_dir``), as
    :func:`_capture_catastrophe_forensics` needs the mtimes/sizes, not just
    paths (so it cannot reuse the path-only :func:`_hail_hadoop_lister`)."""
    import hail as hl
    return list(hl.hadoop_ls(dirpath))


def load_qc_cohort(mt_path: str, ancestry: str, sensitivity: bool = False,
                   ancestry_table_path: str | None = None,
                   relateds_table_path: str | None = None,
                   self_report_table_path: str | None = None,
                   workspace_bucket: str | None = None,
                   skip_checkpoint: bool = False,
                   *,
                   force_fresh: bool = False,
                   interval_filter: str | None = None,
                   _skip_final_write: bool = False,
                   ) -> "hl.MatrixTable":
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
        self_report_table_path: Override the self-report sidecar path used ONLY
            when sensitivity=True (tests, or an explicit staged sidecar). When
            None, production resolves SELF_REPORT_SUFFIX under aux/self_report/
            via _resolve_aux_file (discover-by-suffix, mirroring ancestry_preds).
            The self-report restriction is MANDATORY for the sensitivity cohort:
            if it cannot be sourced, load_qc_cohort RAISES (no silent skip).
            Ignored when sensitivity=False (the primary cohort never sources it).
        workspace_bucket: Override $WORKSPACE_BUCKET; if None and not
            skip_checkpoint, reads from env.
        skip_checkpoint: Skip the gs:// checkpoint write (used by tests
            against synthetic MT — no real bucket available).
        force_fresh: When True, bypass auto-resume checks; overwrite any
            existing intermediates. Default False (auto-resume active).
            Per DESIGN §3.5 + §4.
        interval_filter: When set (e.g., "chr22"), filter source MT to
            this interval right after read_matrix_table. Used by smoke
            tests for path-isolated execution; produces URI-suffixed
            intermediates. Default None.

            When None AND not skip_checkpoint (the GENOME-WIDE production
            fire), load_qc_cohort FANS OUT per autosome: it recurses 22
            times with interval_filter="chrN" and _skip_final_write=True
            (running Phases 1-2 only), then ``union_rows`` the 22 per-chrom
            variant-QC'd MTs and runs Phase 3 (sample QC + het) ONCE over the
            union before the final cohort checkpoint. This bounds every Hail
            action to a single chromosome's partition set -- the condition
            under which chr22 Gate-C passed -- instead of materializing the
            un-pruned whole-genome plan over the ~145k-partition v8 source on
            the first action (the genome-wide first-action wedge;
            .planning/debug/m3-W2-genome-wide-countcols-py4j-wedge.md). Per-
            chrom intermediates are path-isolated via _intermediate_checkpoint_uri
            so the loop is RESTARTABLE (a websocket-drop after chrK resumes at
            chrK+1). Per DESIGN §3.5.
        _skip_final_write: PRIVATE. When True, stop after the post_variant_qc
            checkpoint (end of Phase 2) and RETURN the variant-QC'd MT WITHOUT
            running Phase 3 (sample QC + het) or the final cohort write. Used
            ONLY by the genome-wide per-chromosome fan-out: sample QC and the
            het +/-3SD band MUST be computed once over the full unioned cohort
            (per-sample call_rate needs all variants per sample; the het band
            must be centered on the whole cohort), NOT per-chromosome -- so the
            per-chrom calls chunk Phases 1-2 only. Not part of the public API.

    Returns:
        QC-filtered ``hl.MatrixTable`` ready for per-region LD computation.
        When ``_skip_final_write`` is True, the returned MT is the
        post-variant-QC (Phase 2) MT (sample QC NOT yet applied).
    """
    import hail as hl

    if ancestry not in SUPPORTED_ANCESTRIES:
        raise ValueError(
            f"ancestry={ancestry!r} not supported in M3; the manifest "
            f"emits {sorted(SUPPORTED_ANCESTRIES)}. Documented AoU pred "
            f"labels are {sorted(ANCESTRY_VALUES)} but routing here only "
            f"covers AFR/EUR (D-M3-02)."
        )

    # ------------------------------------------------------------------
    # GENOME-WIDE PER-CHROMOSOME FAN-OUT (interval_filter is None, real run).
    #
    # Root cause of the genome-wide first-action wedge: with interval_filter
    # None there is NO filter_intervals partition pruning, so naive_coalesce +
    # split_multi_hts must build (and the first checkpoint must materialize) a
    # driver-side plan over the FULL un-pruned ~145k-partition v8 source in one
    # shot -- the driver wedges in that pre-task plan phase (stage=0, no
    # executors, flat CPU). chr22 Gate-C never hit this because filter_intervals
    # bounded every action to chr22's partitions first. So: GENERALIZE the
    # proven-good chr22 condition to all 22 autosomes -- recurse per-autosome
    # (each call bounded by interval_filter="chrN"), run Phases 1-2 only
    # (_skip_final_write=True), then union_rows the per-chrom variant-QC'd MTs
    # and run Phase 3 (sample QC + het) ONCE over the union below.
    #
    # Gated on `interval_filter is None and not skip_checkpoint` so:
    #   * the chr22 / nano / synthetic SINGLE-INTERVAL paths (interval_filter
    #     SET) are byte-identical -- they fall straight through to the existing
    #     per-interval body, untouched;
    #   * the local synthetic-MT tests (skip_checkpoint=True, interval_filter
    #     None) ALSO fall through unchanged -- they run the single in-memory
    #     pass, no fan-out (no bucket to write per-chrom intermediates to).
    # See .planning/debug/m3-W2-genome-wide-countcols-py4j-wedge.md.
    # ------------------------------------------------------------------
    if interval_filter is None and not skip_checkpoint and not _skip_final_write:
        import hail as hl  # local: graceful offline import (mirrors body below)

        print(f"[load_qc_cohort] GENOME-WIDE fan-out: {len(AUTOSOMES)} autosomes "
              f"(chr1..chr22) ancestry={ancestry} sensitivity={sensitivity}; "
              f"each chrom bounded to its own partition set (restartable per chrom)")
        per_chrom_mts = []
        for idx, chrom in enumerate(AUTOSOMES, start=1):
            print(f"[load_qc_cohort] genome-wide {idx}/{len(AUTOSOMES)}: {chrom}")
            mt_c = load_qc_cohort(
                mt_path=mt_path,
                ancestry=ancestry,
                sensitivity=sensitivity,
                ancestry_table_path=ancestry_table_path,
                relateds_table_path=relateds_table_path,
                self_report_table_path=self_report_table_path,
                workspace_bucket=workspace_bucket,
                skip_checkpoint=skip_checkpoint,
                force_fresh=force_fresh,
                interval_filter=chrom,        # bounds every action to one chrom
                _skip_final_write=True,       # Phases 1-2 only; return post-vqc MT
            )
            per_chrom_mts.append(mt_c)

        # Variant-axis union of the 22 disjoint per-chrom MTs. union_rows is a
        # metadata-level concatenation (identical col-keys/samples + identical
        # post-split_multi_hts/variant_qc row schema across all 22, since each is
        # built from the same source over the same ancestry/relateds filter) --
        # no shuffle, no driver collect.
        mt = per_chrom_mts[0].union_rows(*per_chrom_mts[1:])

        # The raw-count sample-callrate guard keys on the UNIONED raw count, NOT
        # any single chromosome (one chrom may dip below MIN_VARIANTS_FOR_SAMPLE_
        # CALLRATE and wrongly skip the genome-wide filter). The union of 22
        # variant-QC'd autosomes is far above 500K, so this resolves to APPLY at
        # genome-wide scale -- preserving today's chr22-Gate-C semantics. One
        # bounded count over the already-balanced, checkpointed union.
        _n_var_union = mt.count_rows()
        sample_callrate_filtered = _n_var_union >= MIN_VARIANTS_FOR_SAMPLE_CALLRATE

        # Phase 3 (sample QC + het) ONCE over the union, then the UNCHANGED final
        # cohort checkpoint (same _qc_checkpoint_uri downstream AOU-2/AOU-4/
        # cohort_summary already read). bucket resolved here for the final write.
        bucket = workspace_bucket or os.environ.get("WORKSPACE_BUCKET")
        if not bucket:
            raise RuntimeError("WORKSPACE_BUCKET not set; cannot checkpoint")
        mt = _apply_sample_qc_and_finalize(
            mt, ancestry=ancestry, sensitivity=sensitivity, bucket=bucket,
            sample_callrate_filtered=sample_callrate_filtered)
        return mt

    # Env-derive the AUX base from the WGS MT being read so the ancestry /
    # relatedness tables track the platform-bound CDR version (v8/v9/...), then
    # DISCOVER each table by its canonical suffix so pipeline-version filename
    # prefixes (echo_v4_r2./samples_) need no code edit either. Explicit
    # overrides (tests) still win via the `or`. The lister is active only on
    # real runs; skip_checkpoint (tests/local, no real bucket) -> bare names.
    # (DEC-2026-06-01: env-derive base + suffix-discover filename.)
    aux_base = _resolve_aux_base(mt_path)
    aux_lister = None if skip_checkpoint else _hail_hadoop_lister
    # Ancestry is MANDATORY -> on_ambiguous="raise" (hard-fail, don't guess).
    # Relatedness is BEST-EFFORT (import wrapped in try/except below) ->
    # on_ambiguous="fallback" so a transient rollout collision degrades to the
    # soft-skip path instead of hard-crashing the cohort load.
    anc_path = ancestry_table_path or _resolve_aux_file(
        aux_base, "ancestry", "ancestry_preds.tsv", lister=aux_lister)
    rel_path = relateds_table_path or _resolve_aux_file(
        aux_base, "relatedness", "relatedness_flagged_samples.tsv",
        lister=aux_lister, on_ambiguous="fallback")
    # AFR sensitivity self-report sidecar (D-M3-07). Resolved ONLY when
    # sensitivity=True so the primary cohort's resolution + provenance are
    # unchanged (EUR / AFR-primary stay byte-equivalent). MANDATORY discipline,
    # like ancestry: on_ambiguous="raise" -> hard-fail, refuse to guess. An
    # explicit override (tests / staged sidecar) still wins via the `or`.
    self_report_path = None
    if sensitivity:
        self_report_path = self_report_table_path or _resolve_aux_file(
            aux_base, SELF_REPORT_SUBDIR, SELF_REPORT_SUFFIX,
            lister=aux_lister, on_ambiguous="raise")

    # Resilience refactor: compute intermediate-checkpoint URIs + auto-resume
    # state machine (DESIGN §3.5).
    state = "FRESH"
    auto_fresh = False
    ckpt_post_split = None
    ckpt_post_vqc = None
    provenance = None
    if not skip_checkpoint:
        bucket = workspace_bucket or os.environ.get("WORKSPACE_BUCKET")
        if not bucket:
            raise RuntimeError("WORKSPACE_BUCKET not set; cannot checkpoint")
        ckpt_post_split = _intermediate_checkpoint_uri(
            bucket, ancestry, "post_split", sensitivity, interval_filter)
        ckpt_post_vqc = _intermediate_checkpoint_uri(
            bucket, ancestry, "post_variant_qc", sensitivity, interval_filter)
        provenance = _collect_provenance(
            ancestry, sensitivity, mt_path, interval_filter,
            ancestry_preds_path=anc_path, relateds_path=rel_path,
            self_report_path=self_report_path)

        if not force_fresh:
            # Check deepest intermediate first (post_variant_qc) — if it's
            # present with valid sidecar AND populated entries, we skip
            # both Phase 1 and Phase 2 (variant QC).
            #
            # _validate_checkpoint_populated() is the contents-validating
            # resume-gate (m3-W1 empty-MT catastrophe defense). A stub MT
            # with _SUCCESS present but zero entries falls through to the
            # explicit catastrophe-pattern branch below, then to
            # auto_fresh recovery.
            if _validate_checkpoint_populated(ckpt_post_vqc):
                sidecar = _read_sidecar(_sidecar_uri(ckpt_post_vqc))
                if sidecar is None:
                    # Orphan: MT present but sidecar absent (crash window between
                    # the two writes in a prior fire). Auto-recover.
                    print(f"[load_qc_cohort] WARN: orphan MT at {ckpt_post_vqc} "
                          f"(sidecar absent); auto-force-fresh recovery")
                    auto_fresh = True
                else:
                    matches, diag = _validate_sidecar(sidecar, provenance)
                    if matches:
                        state = "RESUME_FROM_POST_VARIANT_QC"
                    else:
                        raise RuntimeError(
                            f"Stale intermediate at {ckpt_post_vqc}: {diag}\n"
                            f"Use force_fresh=True to overwrite, or fix the "
                            f"parameter mismatch."
                        )
            elif _has_checkpoint(ckpt_post_vqc):
                # m3-W1 catastrophe pattern: _SUCCESS present but entries
                # absent or stub-only. The prior fire produced an empty
                # MT skeleton; do NOT resume from it. Auto-force-fresh
                # recovery so Phase 1 + Phase 2 (variant QC) re-run from source.
                # See [[feedback_aou_success_marker_not_evidence_of_data]].
                print(f"[load_qc_cohort] WARN: empty-MT catastrophe pattern "
                      f"at {ckpt_post_vqc} (_SUCCESS present but entries/ "
                      f"absent or stub-only); auto-force-fresh recovery")
                auto_fresh = True
            elif _validate_checkpoint_populated(ckpt_post_split):
                sidecar = _read_sidecar(_sidecar_uri(ckpt_post_split))
                if sidecar is None:
                    print(f"[load_qc_cohort] WARN: orphan MT at {ckpt_post_split} "
                          f"(sidecar absent); auto-force-fresh recovery")
                    auto_fresh = True
                else:
                    matches, diag = _validate_sidecar(sidecar, provenance)
                    if matches:
                        state = "RESUME_FROM_POST_SPLIT"
                    else:
                        raise RuntimeError(
                            f"Stale intermediate at {ckpt_post_split}: {diag}\n"
                            f"Use force_fresh=True to overwrite, or fix the "
                            f"parameter mismatch."
                        )
            elif _has_checkpoint(ckpt_post_split):
                # Same catastrophe-pattern guard for the shallow intermediate.
                print(f"[load_qc_cohort] WARN: empty-MT catastrophe pattern "
                      f"at {ckpt_post_split} (_SUCCESS present but entries/ "
                      f"absent or stub-only); auto-force-fresh recovery")
                auto_fresh = True

    # Effective overwrite flag for intermediate writes
    overwrite_flag = force_fresh or auto_fresh
    print(f"[load_qc_cohort] state={state} ancestry={ancestry} "
          f"sensitivity={sensitivity} interval_filter={interval_filter}")

    # Guard decision for the Phase 3 sample-callrate filter. Initialized here
    # (before any state branch) so the RESUME_FROM_POST_VARIANT_QC branch can
    # restore it from the resumed sidecar; FRESH / RESUME_FROM_POST_SPLIT set it
    # from the raw variant count in the Phase 2 (variant QC) block below.
    sample_callrate_filtered = None

    # Phase 1: read + filter + split (former steps 1-6)
    if state == "FRESH":
        # Step 1: load the AoU MT (or local synthetic MT)
        mt = hl.read_matrix_table(mt_path)

        # Apply interval filter for smoke tests (no-op for production fires)
        if interval_filter is not None:
            mt = hl.filter_intervals(
                mt,
                [hl.parse_locus_interval(interval_filter, reference_genome="GRCh38")],
            )

        # Step 2: cohort filter on ancestry_pred
        if ANCESTRY_FIELD in mt.col:
            mt = mt.filter_cols(mt[ANCESTRY_FIELD] == ancestry)
        else:
            anc_ht = hl.import_table(anc_path, key="research_id",
                                     types={"research_id": hl.tstr})
            mt = mt.annotate_cols(**{ANCESTRY_FIELD: anc_ht[mt.s][ANCESTRY_FIELD]})
            mt = mt.filter_cols(mt[ANCESTRY_FIELD] == ancestry)

        # Step 3: anti-join against flagged-relateds
        try:
            rel_ht = hl.import_table(rel_path, key="sample_id",
                                     types={"sample_id": hl.tstr})
            mt = mt.anti_join_cols(rel_ht)
        except Exception as e:
            print(f"WARN: relateds table unavailable ({rel_path}): {e}; "
                  f"skipping anti_join", file=sys.stderr)

        # Step 4: AFR sensitivity (D-M3-07) self-report restriction.
        #
        # The sensitivity cohort = genetic-ancestry AFR ∩ self-reports
        # "Black or African American" — a STRICT non-empty subset of the
        # primary. self_report is NOT a column on the AoU WGS MT (it lives in
        # the CDR person table, BigQuery-only); it must be SOURCED here through
        # the same _resolve_aux_file + import_table + annotate_cols machinery as
        # ancestry, then filtered. MANDATORY discipline (mirror ancestry): if it
        # cannot be sourced -> RAISE. NO silent skip — the silent skip was the
        # 2026-06-08 root cause that made AFR-sens == AFR-primary (membership-
        # identical no-op). See
        # .planning/debug/m3-W2-afr-sensitivity-selfid-noop.md.
        if sensitivity:
            if self_report_path is None:
                # Defensive: the resolver above sets self_report_path whenever
                # sensitivity=True. If it is None here the wiring regressed.
                raise RuntimeError(
                    "sensitivity=True but self_report sidecar was not resolved; "
                    "refusing to build a cohort without the MANDATORY "
                    "self-report restriction (would silently == the primary "
                    "cohort). See m3-W2-afr-sensitivity-selfid-noop."
                )
            # Source self_report onto the cols if the MT does not already carry
            # it (it never does in production; a test fixture may pre-annotate
            # it as a col field, mirroring how ancestry_pred is pre-annotated on
            # the synthetic MT). import_table HARD-FAILS loudly if the sidecar
            # path is unresolvable — that is the intended MANDATORY behavior.
            if SELF_REPORT_FIELD not in mt.col:
                try:
                    sr_ht = hl.import_table(
                        self_report_path, key="research_id",
                        types={"research_id": hl.tstr})
                except Exception as e:
                    raise RuntimeError(
                        f"sensitivity=True self-report sidecar could not be "
                        f"sourced ({self_report_path}): {e}. The AFR sensitivity "
                        f"cohort REQUIRES self-reported race (D-M3-07); refusing "
                        f"to silently fall back to the primary cohort. Stage the "
                        f"sidecar (see runbook) and re-fire."
                    ) from e
                mt = mt.annotate_cols(
                    **{SELF_REPORT_FIELD: sr_ht[mt.s][SELF_REPORT_FIELD]})

            # Defense in depth (1/2): self_report must be non-null for ~all
            # in-scope (already ancestry+relateds-filtered) samples. Low coverage
            # => malformed / mis-keyed sidecar (e.g. research_id type/format
            # drift) that would silently shrink the cohort. Fail loudly.
            n_in_scope = mt.count_cols()
            if n_in_scope == 0:
                raise RuntimeError(
                    "sensitivity=True: zero AFR samples in scope BEFORE the "
                    "self-report filter — upstream ancestry/relateds filtering "
                    "collapsed the cohort; aborting (not a self-report issue)."
                )
            n_covered = mt.aggregate_cols(
                hl.agg.count_where(hl.is_defined(mt[SELF_REPORT_FIELD])))
            coverage = n_covered / n_in_scope
            if coverage < MIN_SELF_REPORT_COVERAGE:
                raise RuntimeError(
                    f"sensitivity=True self-report coverage {coverage:.4f} "
                    f"({n_covered}/{n_in_scope}) below "
                    f"MIN_SELF_REPORT_COVERAGE={MIN_SELF_REPORT_COVERAGE}: the "
                    f"sidecar ({self_report_path}) is malformed or mis-keyed "
                    f"(research_id mismatch). Refusing to build a silently-"
                    f"truncated cohort."
                )

            # Apply the restriction (person.race source value string-match).
            mt = mt.filter_cols(
                mt[SELF_REPORT_FIELD].contains(SELF_REPORT_AFR_MATCH))

            # Defense in depth (2/2): the result must be a PROPER non-empty
            # SUBSET (0 < N_post < N_pre). An empty cohort (bad match string /
            # empty sidecar) or a no-shrink (== primary, the original defect)
            # both fail here loudly rather than shipping a degenerate cohort.
            n_post = mt.count_cols()
            if not (0 < n_post < n_in_scope):
                raise RuntimeError(
                    f"sensitivity=True self-report filter did not yield a proper "
                    f"non-empty subset: N_pre={n_in_scope} N_post={n_post} "
                    f"(expected 0 < N_post < N_pre). N_post==0 => bad match "
                    f"string / empty sidecar; N_post==N_pre => the silent-no-op "
                    f"defect (every in-scope sample matched). "
                    f"See m3-W2-afr-sensitivity-selfid-noop."
                )
            print(f"[load_qc_cohort] sensitivity self-report filter applied: "
                  f"{n_in_scope} -> {n_post} samples (match="
                  f"{SELF_REPORT_AFR_MATCH!r}, ver={SENS_FILTER_VERSION})")

        # Step 5: naive_coalesce (cheap upstream coalesce; DEC-2026-05-04-01).
        # No shuffle -> reduces the ~145k-partition source toward the target
        # without a driver gather. The balanced-QC REBALANCE to the target is
        # deferred to the post-split checkpoint read-back below (NOT a pre-write
        # repartition -- see m3-gateb-load-qc-cohort-driver-collect, 2026-06-02).
        mt = mt.naive_coalesce(_COHORT_TARGET_PARTITIONS)

        # Step 6: split_multi_hts BEFORE variant_qc (canonical ordering)
        mt = hl.split_multi_hts(mt)

        # Intermediate 1 checkpoint + sidecar (DESIGN §3.5 atomicity policy:
        # checkpoint write FIRST, then sidecar write).
        if not skip_checkpoint:
            mt = mt.checkpoint(ckpt_post_split, overwrite=overwrite_flag)
            _assert_checkpoint_nonempty(mt, ckpt_post_split, phase="post_split")
            _write_sidecar(_sidecar_uri(ckpt_post_split), provenance, phase="post_split")
            print(f"[load_qc_cohort] wrote intermediate 1: {ckpt_post_split}")
            # Q3-hybrid balanced-QC rebalance, done the Hail-recommended way:
            # repartition AFTER the write by RE-READING the checkpoint with a
            # target partition count. read_matrix_table(_n_partitions=...) uses
            # the on-disk partition index (no key sampling, no driver collect),
            # unlike the removed pre-write mt.repartition(shuffle=True) that
            # caused the Gate B indefinite SpillingCollectIterator driver stall.
            mt = hl.read_matrix_table(
                ckpt_post_split,
                _n_partitions=_post_split_read_partitions(mt.n_partitions()),
            )
    elif state == "RESUME_FROM_POST_SPLIT":
        # Resume also rebalances on read so Phase 2 runs over balanced partitions
        # (the post_split checkpoint carries the naive_coalesce'd, possibly
        # uneven, partition sizes). Same driver-collect-free read-back path.
        mt = hl.read_matrix_table(
            ckpt_post_split,
            _n_partitions=_post_split_read_partitions(),
        )
        print(f"[load_qc_cohort] resumed from intermediate 1: {ckpt_post_split}")
    elif state == "RESUME_FROM_POST_VARIANT_QC":
        mt = hl.read_matrix_table(ckpt_post_vqc)
        print(f"[load_qc_cohort] resumed from intermediate 2: {ckpt_post_vqc}")
        # Restore the raw-count guard DECISION from the resumed sidecar so the
        # Phase 3 sample-callrate filter applies (or skips) exactly as the
        # producing fire decided, without re-reading source for the raw count.
        _resumed_sc = _read_sidecar(_sidecar_uri(ckpt_post_vqc))
        sample_callrate_filtered = (_resumed_sc or {}).get("sample_callrate_filtered", True)

    # Phase 2: variant QC (was Phase 3) — MOVED AHEAD of sample QC so per-sample
    # call_rate is computed over QC-passing (common, well-called) variants, not
    # the raw pre-variant-QC ACAF set. Computing call_rate pre-variant-QC made the
    # 0.98 sample threshold unsatisfiable at ALL scales (Gate C whole-chr22
    # collapse 1859922x74576 -> 1859922x0; probe [A] max call_rate 0.8490).
    # variant-QC-first lifts call_rate to mean 0.9975 (probe [B], 74558/74576 kept).
    # See .planning/debug/m3-gatec-sample-callrate-ordering-collapse.md.
    if state in ("FRESH", "RESUME_FROM_POST_SPLIT"):
        # Capture the RAW (pre-variant-QC) in-scope variant count for the sample-
        # callrate degeneracy guard. The guard keys on RAW interval size (the
        # honest "real tier vs nano smoke window" discriminator), NOT the post-
        # variant-QC count, so the validated MIN_VARIANTS_FOR_SAMPLE_CALLRATE=500K
        # threshold keeps its meaning after the reorder (DEC-2026-06-04). nano
        # (raw <500K) SKIPs; whole-chromosome+ (raw >=500K) APPLIES over the clean
        # variants. The decision is persisted to the post_variant_qc sidecar so a
        # RESUME_FROM_POST_VARIANT_QC fire applies the same guard without re-reading
        # source.
        _n_var_raw = mt.count_rows()
        sample_callrate_filtered = _n_var_raw >= MIN_VARIANTS_FOR_SAMPLE_CALLRATE

        # variant_qc + MAF/HWE/call_rate filters
        mt = hl.variant_qc(mt, name="vqc")
        mt = mt.filter_rows(
            (mt.vqc.AF[1] >= MIN_MAF_INTERNAL) &
            (mt.vqc.AF[1] <= MAX_MAF) &
            (mt.vqc.call_rate >= MIN_CALL_RATE_VARIANT) &
            (mt.vqc.p_value_hwe >= MIN_HWE_PVALUE)
        )
        # Drop AoU-flagged variants (filters non-empty)
        if "filters" in mt.row:
            mt = mt.filter_rows(hl.len(mt.filters) == 0)

        # Intermediate 2 checkpoint (post_variant_qc) + sidecar. The raw-count
        # guard DECISION is persisted (sample_callrate_filtered); it is a non-
        # compared sidecar field (resume-safe).
        if not skip_checkpoint:
            mt = mt.checkpoint(ckpt_post_vqc, overwrite=overwrite_flag)
            _assert_checkpoint_nonempty(mt, ckpt_post_vqc, phase="post_variant_qc")
            _write_sidecar(_sidecar_uri(ckpt_post_vqc), provenance,
                           phase="post_variant_qc",
                           sample_callrate_filtered=sample_callrate_filtered)
            print(f"[load_qc_cohort] wrote intermediate 2: {ckpt_post_vqc}")

    # GENOME-WIDE FAN-OUT boundary: a per-chromosome recursion stops HERE, after
    # the post_variant_qc checkpoint, and returns the variant-QC'd MT. Phase 3
    # (sample QC + het) and the final write run ONCE over the UNIONED cohort in
    # the genome-wide caller above -- NOT per-chromosome (per-sample call_rate
    # needs all variants per sample; the het band must center on the whole
    # cohort). _skip_final_write is only ever True on those internal recursive
    # calls. See .planning/debug/m3-W2-genome-wide-countcols-py4j-wedge.md.
    if _skip_final_write:
        return mt

    # Phase 3: sample QC (was Phase 2) + final cohort checkpoint. Shared with the
    # genome-wide union path via _apply_sample_qc_and_finalize so both code paths
    # run IDENTICAL sample-QC / het / final-write logic (no drift).
    return _apply_sample_qc_and_finalize(
        mt, ancestry=ancestry, sensitivity=sensitivity,
        bucket=(bucket if not skip_checkpoint else None),
        sample_callrate_filtered=sample_callrate_filtered)


def _apply_sample_qc_and_finalize(mt: "hl.MatrixTable", *, ancestry: str,
                                  sensitivity: bool, bucket: str | None,
                                  sample_callrate_filtered: bool | None
                                  ) -> "hl.MatrixTable":
    """Phase 3 (sample QC + het +/-3SD) and the final cohort checkpoint.

    Extracted so the single-interval path (load_qc_cohort body) and the
    genome-wide per-chromosome UNION path run byte-identical sample-QC / het /
    final-write logic. variant_qc has ALREADY been applied upstream (per the
    W1 QC-ordering fix: variant_qc BEFORE sample_qc, so per-sample call_rate is
    measured over QC-passing variants -- do NOT reintroduce the sample-axis
    collapse). sample QC and the het band are correctly computed ONCE over the
    full (single-interval or unioned-genome) cohort here.

    Args:
        mt: post-variant-QC MatrixTable (sample QC not yet applied).
        ancestry/sensitivity: select the final checkpoint URI.
        bucket: workspace bucket for the final write; None => skip the write
            (local synthetic-MT tests, no real bucket).
        sample_callrate_filtered: raw-count guard decision (APPLY vs SKIP the
            >=0.98 per-sample call_rate filter). None => defensive APPLY
            (reached only on RESUME_FROM_POST_VARIANT_QC where the producing
            fire's decision is restored from the sidecar).
    """
    import hail as hl

    # call_rate is measured over the post-variant-QC clean variant set, so the
    # 0.98 threshold is satisfiable.
    if sample_callrate_filtered is None:
        # Defensive default: APPLY (production-correct; only nano smoke skips).
        sample_callrate_filtered = True
    mt = hl.sample_qc(mt, name="sqc")
    if sample_callrate_filtered:
        mt = mt.filter_cols(mt.sqc.call_rate >= MIN_CALL_RATE_SAMPLE)
    else:
        cr = mt.aggregate_cols(hl.agg.stats(mt.sqc.call_rate))
        print(f"[load_qc_cohort] SKIP call_rate sample filter — raw in-scope "
              f"variant count < {MIN_VARIANTS_FOR_SAMPLE_CALLRATE} (nano-tier "
              f"degeneracy guard); call_rate mean={cr.mean:.4f} max={cr.max:.4f}. "
              f"Sample-QC thresholds validated at whole-chromosome+ tier.")

    # het +/-3SD within ancestry-filtered cohort, guarded against stdev<=0
    het_stats = mt.aggregate_cols(hl.agg.stats(mt.sqc.r_het_hom_var))
    if het_stats.stdev is not None and het_stats.stdev > 0:
        lo = het_stats.mean - HET_HOM_SD_BAND * het_stats.stdev
        hi = het_stats.mean + HET_HOM_SD_BAND * het_stats.stdev
        mt = mt.filter_cols((mt.sqc.r_het_hom_var >= lo) &
                            (mt.sqc.r_het_hom_var <= hi))

    # Final checkpoint to workspace bucket (UNCHANGED URI -- downstream AOU-2 /
    # AOU-4 / cohort_summary read this exact path; producer/consumer contract
    # preserved for both the single-interval and genome-wide union paths).
    if bucket is not None:
        ckpt = _qc_checkpoint_uri(bucket, ancestry, sensitivity)
        mt = mt.checkpoint(ckpt, overwrite=True)
        _assert_checkpoint_nonempty(mt, ckpt, phase="final")
        # Atomic-final-write contract: stamp _VALIDATED ONLY after the non-empty
        # assertion passes, so a canonical _SUCCESS WITHOUT _VALIDATED documents a
        # final that never passed post-write validation (the m3-W2 H1 driver kill
        # died between the _SUCCESS-writing checkpoint() and this assert). The
        # marker is documentation; _final_is_trustworthy() gates on CONTENTS, not
        # the marker (a stale marker must never vouch for re-emptied contents).
        _write_validated_marker(ckpt)
        print(f"[load_qc_cohort] wrote final: {ckpt}")

    return mt


def _existing_region_npz(region_id: str, out_bucket: str | None,
                         out_local_dir: Path | None) -> str | None:
    """Return path/URI to an existing ``{region_id}.npz``, or None.

    Used by :func:`compute_region_ld`'s W1-G1 idempotency guard
    (260520-s2s-CONTEXT.md). Critical for websocket-drop resume protocol —
    a 30h Wave 4 production fire cannot tolerate a single browser timeout
    forfeiting all completed regions.

    Checks in priority order:

      1. ``{out_bucket}/{region_id}.npz`` (production GCS write target).
         Uses ``hl.hadoop_is_file`` for ``gs://`` URIs; falls back to local
         path check for ``file://`` or bare-path buckets.
      2. ``{out_local_dir or /tmp}/{region_id}.npz`` (local-test write target).

    For Path A.3 (BlockMatrix .bm directory), idempotency would require
    checking ``{out_bucket}/bm/{region_id}.bm/_SUCCESS`` — DEFERRED to a
    follow-up quick task; dev-10 has only 2 Path A.3 regions and Wave 2
    manual re-fire skipping is acceptable for those (re-firing a completed
    .bm write is wasteful but not incorrect since BlockMatrix.write accepts
    overwrite=True).
    """
    # GCS / Hadoop-style bucket check. MED-6: validate the file is populated
    # (size >= _MIN_REGION_NPZ_BYTES), not merely present — a 0-byte / truncated
    # .npz from a websocket-drop mid-write must NOT short-circuit as "done".
    if out_bucket is not None:
        candidate = f"{out_bucket}/{region_id}.npz"
        if candidate.startswith("gs://"):
            try:
                import hail as hl
                if hl.hadoop_is_file(candidate):
                    size = int(hl.hadoop_stat(candidate)["size_bytes"])
                    if size >= _MIN_REGION_NPZ_BYTES:
                        return candidate
                    print(f"WARN: existing {candidate} is {size} B "
                          f"(< {_MIN_REGION_NPZ_BYTES} B floor) — treating as a "
                          f"truncated/corrupt write; will recompute (m3-W2 MED-6).",
                          file=sys.stderr)
            except Exception:
                # Defensive: any filesystem/Hail error treated as "not present"
                # — safer to redo work than to assume a checkpoint that may
                # not actually exist.
                pass
        elif candidate.startswith("file://"):
            local_candidate = Path(candidate[len("file://"):])
            if local_candidate.is_file() and \
                    local_candidate.stat().st_size >= _MIN_REGION_NPZ_BYTES:
                return candidate
    # Local-dir fallback (matches _save_npz's local_path convention)
    local = (out_local_dir or Path("/tmp")) / f"{region_id}.npz"
    if local.is_file() and local.stat().st_size >= _MIN_REGION_NPZ_BYTES:
        return str(local)
    return None


def compute_region_ld(region_row: dict, mt_source: "hl.MatrixTable",
                      out_bucket: str | None = None,
                      out_local_dir: Path | None = None,
                      *,
                      force_recompute: bool = False) -> dict:
    """Compute per-region LD matrix.

    Path-A branching per region_class (RESEARCH Q5):
        small (<= 5 Mb)        -> Path A.1: to_numpy + np.savez_compressed
        medium (5 - 10 Mb)     -> Path A.2: sparsify_triangle + to_numpy + savez
        large/xlarge (> 10 Mb) -> Path A.3: BlockMatrix.write(gs://) for NCSU densification

    Returns a dict with keys: region_id, status, n_var, path_a, out (path/uri).

    Skip threshold: regions with n_var < MIN_VARIANTS_PER_REGION return
    status='skipped_few_variants' (matches AOU-LD-PIPELINE.md §5.1 line 187).

    Idempotency (W1-G1, 260520-s2s-CONTEXT.md):
        If ``{region_id}.npz`` already exists at the target location
        (out_bucket or out_local_dir) and ``force_recompute`` is False
        (default), short-circuit and return ``status='skipped_idempotent'``
        without invoking ``hl.ld_matrix``. Critical for websocket-drop
        resume protocol on the 322-cell Wave 4 production fire. Pass
        ``force_recompute=True`` to bypass the guard for a single region.

    Export MAF (Q6, 260520-s2s-CONTEXT.md):
        Variant pre-filter at ``load_qc_cohort`` enforces MAF ≥ MIN_MAF_INTERNAL
        (= MAF_THRESHOLD_EXPORT = 0.005); exported .npz preserves this band
        rather than tightening to spec §7.2's 0.01 default. See
        :data:`MAF_THRESHOLD_EXPORT`.
    """
    import hail as hl
    import numpy as np

    rid = region_row["region_id"]

    # W1-G1 idempotency guard (260520-s2s-CONTEXT.md): if {region_id}.npz
    # already exists at the target location and force_recompute is False,
    # short-circuit without invoking hl.ld_matrix.
    if not force_recompute:
        existing_npz = _existing_region_npz(rid, out_bucket, out_local_dir)
        if existing_npz is not None:
            return {
                "region_id": rid,
                "status": "skipped_idempotent",
                "n_var": None,
                "path_a": None,
                "out": existing_npz,
            }

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

    # hl.ld_matrix returns a BlockMatrix of Pearson correlations on n_alt_alleles dosages.
    # radius_bp is the per-region radius (span + 500 kb) emitted by the Wave-0
    # reformatter, CAPPED at 50 Mb (build_ld_region_manifest.RADIUS_HARD_CAP_BP).
    # m3-W2 audit HIGH-3 (ACCEPTED trade-off, Carter 2026-06-04): for the 16 xlarge
    # cells (span > 50 Mb) radius < span, so hl.ld_matrix structurally zeroes
    # variant pairs > 50 Mb apart -> long-range LD is banded out. This is accepted:
    # full-radius LD over a ~100 Mb region is computationally intractable
    # (O(n_var^2) ~ 10^12 entries) and long-range LD ~ 0 at > 50 Mb anyway.
    # Downstream (SuSiE-RSS / ld_npz_to_rds.R) must treat xlarge-region LD as
    # 50-Mb-banded. The invariant "only xlarge cells are radius-capped" is pinned
    # by tests::test_ld_regions_radius_cap_only_affects_xlarge, so a new banded
    # region in a regenerated manifest surfaces for review. See WAVE-2-PLAN.md HIGH-3.
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
    path_a = _route_region_path(region_class, span_mb)
    # Observability: log when the OOM veto demoted a small/medium-classed region
    # to A.3 by span (m3-W2 audit HIGH-1) — otherwise the path choice is silent.
    if path_a == "A.3" and region_class in ("small", "medium") and span_mb > PATH_A2_MAX_MB:
        print(f"[compute_region_ld] OOM-veto (m3-W2 HIGH-1): region_class="
              f"{region_class!r} but span {span_mb:.1f} Mb > {PATH_A2_MAX_MB} Mb "
              f"-> A.3 BlockMatrix write (avoids an O(n_var^2) driver to_numpy OOM).")

    if path_a == "A.1":
        ld_np = ld_bm.to_numpy().astype("float32")
        out_uri = _save_npz(rid, ld_np, variant_ids, rsids, out_bucket, out_local_dir)
    elif path_a == "A.2":
        # Sparsify lower triangle in place; result is still a BlockMatrix
        ld_bm_lt = ld_bm.sparsify_triangle(lower=True)
        ld_np = ld_bm_lt.to_numpy().astype("float32")
        out_uri = _save_npz(rid, ld_np, variant_ids, rsids, out_bucket, out_local_dir,
                            lower_triangular=True)
    else:
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
            # MED-4: validate the .bm is populated (read-back shape), not merely
            # that write() returned. m3-W1 wrote a success marker on empty
            # contents; Path A.3 had no analogous catastrophe guard.
            _assert_blockmatrix_written(str(local_path), n_var, rid)
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
            _assert_blockmatrix_written(bm_uri, n_var, rid)  # MED-4
            # Upload sidecar TSVs to the same gs://.../bm/ prefix so the
            # NCSU-side gsutil cp -r picks them up alongside the .bm dir.
            # MED-5: a swallowed upload failure would ship an orphan .bm that
            # bm_to_npz.py cannot ingest (the CR-003 failure) — discovered only
            # post-egress. Fail loudly so the region is re-fired instead of
            # silently returning status=ok.
            for sidecar_name, payload in (
                (f"{rid}.variant_ids.tsv", variant_ids),
                (f"{rid}.rsids.tsv", rsids),
            ):
                local_tmp = Path("/tmp") / sidecar_name
                np.savetxt(str(local_tmp), np.array(payload, dtype=object), fmt="%s")
                uploaded = _upload_to_gcs(
                    local_path=local_tmp,
                    out_bucket=out_bucket,
                    blob_subpath=f"bm/{sidecar_name}",
                )
                if uploaded is None:
                    raise RuntimeError(
                        f"Path A.3 sidecar upload FAILED for {sidecar_name} "
                        f"(region {rid}); refusing status=ok with an orphan .bm "
                        f"that bm_to_npz.py cannot ingest (m3-W2 MED-5). Re-fire "
                        f"the region."
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


def _assert_blockmatrix_written(uri: str, n_var: int, region_id: str) -> None:
    """Validate a Path-A.3 BlockMatrix write produced a populated matrix.

    m3-W2 audit MED-4: ``BlockMatrix.write`` returning is NOT proof of populated
    contents — the m3-W1 empty-MT catastrophe wrote a success marker on empty
    contents, and Path A.3 had no analogous guard. Re-reads the BlockMatrix
    metadata and asserts its shape is the expected ``(n_var, n_var)``; a read
    failure or shape mismatch means the ``.bm`` is empty/corrupt. ``read`` is lazy
    (metadata only) so this is cheap. Mirrors :func:`_assert_checkpoint_nonempty`
    for the MT path. See [[feedback_aou_success_marker_not_evidence_of_data]].
    """
    import hail as hl
    try:
        nr, nc = hl.linalg.BlockMatrix.read(uri).shape
    except Exception as e:
        raise RuntimeError(
            f"Path A.3 BlockMatrix at {uri} (region {region_id}) is unreadable "
            f"after write — empty/corrupt .bm (m3-W1-class catastrophe): {e}"
        )
    if nr != n_var or nc != n_var:
        raise RuntimeError(
            f"Path A.3 BlockMatrix at {uri} (region {region_id}) has shape "
            f"({nr}, {nc}); expected ({n_var}, {n_var}) — empty/corrupt write "
            f"(m3-W2 MED-4)."
        )


def _save_npz(region_id: str, ld_np: "np.ndarray", variant_ids: list,
              rsids: list, out_bucket: str | None, out_local_dir: Path | None,
              lower_triangular: bool = False) -> str:
    """Save dense LD as .npz (locally + optionally upload to GCS bucket).

    Q2/Q4 lock (260520-s2s-CONTEXT.md): asserts ld_np is float32 — float64
    would silently double per-region storage + egress (~16 GB → ~32 GB
    across 322 production cells); float16 would lose SuSiE-RSS-relevant
    precision in the signed-r band. Path A.1/A.2 callers already cast via
    ``.astype("float32")`` (defensive assertion traps a future regression
    where the cast is dropped).
    """
    import numpy as np

    assert ld_np.dtype == np.float32, (
        f"Q2/Q4 lock (260520-s2s): LD array must be float32 before .npz write; "
        f"got dtype={ld_np.dtype} for region_id={region_id!r}. "
        f"float64 doubles egress; float16 loses SuSiE-RSS precision."
    )

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
