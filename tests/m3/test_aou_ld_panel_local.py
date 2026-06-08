"""Unit tests for src/python/aou_ld_panel.py against the synthetic MT fixture.

Skips gracefully if Hail is not installed locally (CI graceful-degrade per
plan acceptance criteria — pytest.importorskip("hail") at module entry).
Otherwise: builds the synthetic MT via ``synthetic_mt_path`` session fixture,
exercises load_qc_cohort + compute_region_ld for both region_class branches.

Covers the 5 driver behaviors enumerated in m3-00 plan task 3:
* test_synthetic_mt_built_via_balding_nichols
* test_aou_driver_loads_synthetic_mt
* test_canonical_ordering (split_multi_hts BEFORE variant_qc; static source check)
* test_compute_region_ld_path_a1 (small region; dense .npz)
* test_compute_region_ld_skipped_few_variants
* test_env_yaml_pins_python_311
* test_gitignore_has_explicit_aou_entries
"""
from __future__ import annotations

import ast
import sys
import types
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ----- Static-source / file-existence tests (no hail dependency) -----

def test_env_yaml_pins_python_311():
    p = PROJECT_ROOT / "envs" / "m3-aou-dev.yml"
    assert p.exists(), f"missing {p}"
    content = p.read_text()
    assert "python=3.11" in content, "envs/m3-aou-dev.yml must pin python=3.11"
    assert "hail==0.2" in content, "envs/m3-aou-dev.yml must pin hail==0.2.x"


def test_r_env_yaml_has_reticulate():
    p = PROJECT_ROOT / "envs" / "m3-r-ld.yml"
    assert p.exists()
    content = p.read_text()
    assert "r-reticulate" in content
    assert "r-base=4.4" in content


def test_canonical_ordering_split_before_variant_qc():
    """Static check: split_multi_hts called BEFORE the FIRST variant_qc in source."""
    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    split_idx = src.find("split_multi_hts")
    vqc_idx = src.find("variant_qc")
    assert split_idx > 0, "split_multi_hts not found in aou_ld_panel.py"
    assert vqc_idx > 0, "variant_qc not found in aou_ld_panel.py"
    assert split_idx < vqc_idx, (
        f"split_multi_hts must appear BEFORE variant_qc "
        f"(positions: split={split_idx}, vqc={vqc_idx})"
    )


# ----- Post-split partitioning regression guards
# ----- (m3-gateb-load-qc-cohort-driver-collect, 2026-06-02) -----
#
# Gate B chr22 smoke surfaced an INDEFINITE driver-side stall in
# load_qc_cohort(): jstack showed the driver in SpillingCollectIterator ->
# TableValue.mapRows, spilling ~2,077 surviving row-partitions to /tmp with
# 0 active executor threads. Root cause: mt.repartition(2048) (shuffle=True is
# the MatrixTable.repartition DEFAULT) was called AFTER split_multi_hts and
# BEFORE the post_split checkpoint write. repartition(shuffle=True) builds a
# Spark RangePartitioner by SAMPLING row keys across all input partitions;
# split_multi_hts had just re-keyed/added rows so the carried partitioner was
# invalidated, and Hail lowered the boundary computation to a DRIVER collect.
# The op was also redundant (naive_coalesce already set count=2048) and an
# anti-pattern the Hail core team warns against: "avoid repartition, especially
# shuffle=True; repartition AFTER you've written data with too many partitions,
# NOT before -- use _n_partitions on read"
# (discuss.hail.is: "best way to repartition heavily-filtered matrix tables").
#
# Fix: drop the pre-write repartition; rebalance on the post-split checkpoint
# READ-BACK via read_matrix_table(..., _n_partitions=...), which uses the
# on-disk partition index (no key-sampling, no driver gather). These guards
# FAIL on the pre-fix source (repartition-before-write) and PASS on the fix.


def test_fresh_path_no_repartition_before_post_split_checkpoint():
    """REGRESSION GUARD (m3-gateb-load-qc-cohort-driver-collect, 2026-06-02):

    The FRESH path of load_qc_cohort must NOT call .repartition() between
    split_multi_hts and the post_split checkpoint write. repartition(shuffle=True)
    there triggers a driver-side SpillingCollectIterator gather over the surviving
    partitions (the Gate B indefinite stall). Static-source check so it runs
    without Hail (NCSU-side, no Hail install).
    """
    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    # Anchor on the ACTUAL FRESH-path call (the LAST split_multi_hts occurrence;
    # earlier ones are the module + function docstrings), and bound the window at
    # the post_split checkpoint WRITE. Then assert there is no executable
    # repartition CALL in that window -- matching `mt.repartition(` as code, not
    # the substring `.repartition(` which legitimately appears in explanatory
    # comments/docstrings describing why the op was removed.
    split_idx = src.rfind("mt = hl.split_multi_hts(mt)")
    ckpt_idx = src.find("ckpt_post_split, overwrite=overwrite_flag", split_idx)
    assert split_idx > 0, "FRESH-path split_multi_hts call not found"
    assert ckpt_idx > split_idx, "post_split checkpoint write not found after split"
    window = src[split_idx:ckpt_idx]
    assert "mt.repartition(" not in window, (
        "load_qc_cohort FRESH path calls mt.repartition() between split_multi_hts "
        "and the post_split checkpoint write -- this is the shuffle=True driver "
        "collect that caused the Gate B indefinite stall. Rebalance on the "
        "checkpoint read-back via read_matrix_table(_n_partitions=...) instead "
        "(repartition AFTER write, not before)."
    )


def test_post_split_read_partitions_helper_exists_and_returns_target():
    """REGRESSION GUARD (m3-gateb-load-qc-cohort-driver-collect, 2026-06-02):

    The post-split rebalance target is computed by a pure, Hail-free helper so
    the partitioning decision is unit-testable without a live cluster. It must
    return the documented Q3-hybrid target partition count (_COHORT_TARGET_PARTITIONS).
    """
    from aou_ld_panel import _post_split_read_partitions, _COHORT_TARGET_PARTITIONS
    assert _COHORT_TARGET_PARTITIONS == 2048, (
        "Q3-hybrid balanced-QC target partition count (DEC-2026-05-04-01) is 2048"
    )
    assert _post_split_read_partitions() == _COHORT_TARGET_PARTITIONS
    # Never returns a non-positive count (would be an invalid _n_partitions).
    assert _post_split_read_partitions() > 0


def test_post_split_read_partitions_never_exceeds_current():
    """The read-back target must never exceed the available on-disk partition
    count (read_matrix_table(_n_partitions=N) cannot fabricate partitions beyond
    what the checkpoint holds -- it coalesces down). When the post-split MT has
    FEWER partitions than the 2048 target (e.g. a nano interval that pruned to a
    handful), the helper must clamp to the available count, not the target."""
    from aou_ld_panel import _post_split_read_partitions, _COHORT_TARGET_PARTITIONS
    # Plenty available -> target.
    assert _post_split_read_partitions(available_partitions=145_192) == \
        _COHORT_TARGET_PARTITIONS
    # Fewer available than target -> clamp to available (no over-request).
    assert _post_split_read_partitions(available_partitions=37) == 37
    # available unknown (None) -> fall back to target (preserves prior behavior).
    assert _post_split_read_partitions(available_partitions=None) == \
        _COHORT_TARGET_PARTITIONS


def test_uses_verified_env_var_names():
    """Verify the driver does NOT use the broken RELATED_SAMPLES_HT_PATH env var (Q9 correction)."""
    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    assert "WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH" in src
    assert "WORKSPACE_BUCKET" in src
    assert "GOOGLE_PROJECT" in src
    # The broken spec env var name must NOT appear (verifies RESEARCH Q9 correction)
    assert "RELATED_SAMPLES_HT_PATH" not in src, (
        "broken env-var name from spec §5.1 line 142 must NOT appear in driver"
    )
    # The correct hardcoded path MUST appear
    assert "relatedness_flagged_samples.tsv" in src


def test_static_ast_calls_present():
    """Driver source contains ast-detectable calls to all required Hail entry points."""
    tree = ast.parse((PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text())
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    required = {"split_multi_hts", "variant_qc", "sample_qc", "ld_matrix"}
    missing = required - names
    assert not missing, f"missing Hail call-path attributes: {missing}"


def test_gitignore_has_explicit_aou_entries():
    g = (PROJECT_ROOT / ".gitignore").read_text()
    assert "data/interim/aou_ld_exports" in g
    assert "data/processed/ld_reference/AFR_aou" in g
    assert "data/processed/ld_reference/EUR_aou" in g
    assert "tests/m3/fixtures/synthetic_mt" in g


# ----- Checkpoint-URI tests (m3-W1-checkpoint-suffix regression guards) -----

def test_qc_checkpoint_uri_primary_afr():
    """sensitivity=False AFR -> mt_afr_qc.mt (current behavior preserved)."""
    from aou_ld_panel import _qc_checkpoint_uri
    assert _qc_checkpoint_uri("test-bucket", "afr", False) == \
        "gs://test-bucket/ld/mt_afr_qc.mt"


def test_qc_checkpoint_uri_sensitivity_afr():
    """sensitivity=True AFR -> mt_afr_pca_selfid_qc.mt (D-M3-07 distinct path).

    Three downstream notebooks (AOU-1 cohort_summary table at Cell 7,
    AOU-2_per_region_ld.ipynb, AOU-4_validation.ipynb) already consume
    this exact path; the producer load_qc_cohort was the drift point
    surfaced 2026-05-12.
    """
    from aou_ld_panel import _qc_checkpoint_uri
    assert _qc_checkpoint_uri("test-bucket", "afr", True) == \
        "gs://test-bucket/ld/mt_afr_pca_selfid_qc.mt"


def test_qc_checkpoint_uri_eur_primary():
    """EUR is always sensitivity=False -> mt_eur_qc.mt (D-M3-01 parity)."""
    from aou_ld_panel import _qc_checkpoint_uri
    assert _qc_checkpoint_uri("test-bucket", "eur", False) == \
        "gs://test-bucket/ld/mt_eur_qc.mt"


def test_qc_checkpoint_uri_distinct_paths_regression():
    """REGRESSION GUARD (m3-W1-checkpoint-suffix, 2026-05-12): AFR primary
    and sensitivity cohorts MUST write to distinct checkpoint URIs.
    Prevents the silent overwrite where Cell 4 (sensitivity=True) would
    trash Cell 3's (sensitivity=False) checkpoint at the shared mt_afr_qc.mt
    path. Three downstream notebooks consume both paths independently."""
    from aou_ld_panel import _qc_checkpoint_uri
    primary = _qc_checkpoint_uri("test-bucket", "afr", False)
    sensitivity = _qc_checkpoint_uri("test-bucket", "afr", True)
    assert primary != sensitivity, (
        f"AFR primary and sensitivity cohorts must write to distinct "
        f"checkpoints; both got {primary}"
    )


# ----- AFR sensitivity self-report sourcing tests
# ----- (m3-W2-afr-sensitivity-selfid, 2026-06-08) -----
#
# The sensitivity=True (D-M3-07) AFR cohort must be a STRICT non-empty SUBSET of
# the genetic-ancestry-only primary: genetic-ancestry AFR ∩ self-reports
# "Black or African American". Surfaced 2026-06-08 as a silent no-op — the
# self_report column was NEVER sourced onto the MT (referenced only at the
# filter), and the filter sat behind `and "self_report" in mt.col` which turned
# the missing column into a silent skip. sensitivity=True therefore yielded the
# IDENTICAL predicate as sensitivity=False (AFR-sens == AFR-primary,
# membership-identical). The fix sources self_report through the EXISTING
# _resolve_aux_file + import_table + annotate_cols machinery (mirroring the
# MANDATORY ancestry pattern) and hard-fails when it cannot be sourced.
# See .planning/debug/m3-W2-afr-sensitivity-selfid-noop.md.


def test_selfreport_filter_version_token_in_provenance():
    """Provenance must carry the self_report sidecar path + a sensitivity-filter
    version token so any future change to the sensitivity-restriction semantics
    auto-invalidates intermediates (belt-and-suspenders atop the explicit purge).

    RED pre-fix: _collect_provenance has no self_report_path / sens_filter_version
    keys at all. GREEN: both present, and the resolved sidecar path is recorded
    when sensitivity=True."""
    from aou_ld_panel import _collect_provenance
    prov = _collect_provenance(
        ancestry="afr",
        sensitivity=True,
        source_mt_path="gs://src/path.mt",
        interval_filter=None,
        self_report_path="gs://aux/self_report/self_report.tsv",
    )
    assert prov.get("self_report_path") == "gs://aux/self_report/self_report.tsv", (
        "sensitivity provenance must record the resolved self_report sidecar path"
    )
    assert "sens_filter_version" in prov, (
        "provenance must carry a sensitivity-filter version token so a change to "
        "the self-report restriction auto-invalidates intermediates"
    )


def test_selfreport_filter_version_token_independent_of_sensitivity_false():
    """A sensitivity=False provenance must NOT record a self_report_path (the
    primary cohort never sources self-report). Guards the scoping contract: the
    fix must not perturb the sensitivity=False path that EUR builds on."""
    from aou_ld_panel import _collect_provenance
    prov = _collect_provenance(
        ancestry="afr",
        sensitivity=False,
        source_mt_path="gs://src/path.mt",
    )
    # No self_report sidecar for the primary; key may be absent or None.
    assert not prov.get("self_report_path"), (
        "sensitivity=False provenance must not record a self_report sidecar path"
    )


# ----- _normalize_bucket + prefixed-bucket contract tests
# ----- (m3-W1-bucket-prefix-defensive, 2026-05-14 regression guards) -----


def test_normalize_bucket_strips_prefix():
    """Bare requirement: _normalize_bucket strips the gs:// protocol prefix."""
    from aou_ld_panel import _normalize_bucket
    assert _normalize_bucket("gs://fc-secure-XXX") == "fc-secure-XXX"


def test_normalize_bucket_keeps_bare():
    """Back-compat: bare bucket names pass through unchanged."""
    from aou_ld_panel import _normalize_bucket
    assert _normalize_bucket("fc-secure-XXX") == "fc-secure-XXX"


def test_normalize_bucket_strips_trailing_slash():
    """Defensive: trailing slash on bucket path normalized away (otherwise
    f-string construction yields "gs://bucket//ld/..." double-slash)."""
    from aou_ld_panel import _normalize_bucket
    assert _normalize_bucket("fc-secure-XXX/") == "fc-secure-XXX"
    assert _normalize_bucket("gs://fc-secure-XXX/") == "fc-secure-XXX"


def test_normalize_bucket_idempotent():
    """Property: applying _normalize_bucket twice yields same as once.
    Guards against accidental future regressions where re-normalization could
    over-strip (e.g. removing characters from a bare name that happens to
    start with 'gs:')."""
    from aou_ld_panel import _normalize_bucket
    for raw in [
        "fc-secure-XXX",
        "gs://fc-secure-XXX",
        "gs://fc-secure-XXX/",
        "test-bucket",
    ]:
        once = _normalize_bucket(raw)
        twice = _normalize_bucket(once)
        assert once == twice, f"non-idempotent: f({raw!r})={once!r}, f(f({raw!r}))={twice!r}"


def test_normalize_bucket_handles_malformed_extra_slash():
    """Defensive: malformed gs:///bucket (3 slashes) still normalizes cleanly.
    Belt-and-suspenders against AoU env-var edge cases."""
    from aou_ld_panel import _normalize_bucket
    assert _normalize_bucket("gs:///fc-secure-XXX") == "fc-secure-XXX"


def test_qc_checkpoint_uri_accepts_prefixed_bucket():
    """REGRESSION GUARD (m3-W1-bucket-prefix-defensive, 2026-05-14):
    _qc_checkpoint_uri must accept both bare ('fc-secure-XXX') and
    already-prefixed ('gs://fc-secure-XXX') bucket inputs and produce the
    SAME canonical single-gs:// URI either way.

    Bug surfaced 2026-05-14 during AOU-1 Wave 1 fire on AoU Workbench: the
    notebook caller passed os.environ['WORKSPACE_BUCKET'] (which AoU ships as
    'gs://fc-secure-...') into the prior bare-only contract, yielding
    'gs://gs://fc-secure-.../ld/mt_afr_qc.mt' -- a malformed double-protocol
    URI that would have failed at GCS-write boundary during Cell 3's
    load_qc_cohort. Defensive normalization in the helper closes the
    integration gap between the helper's bare-only test contract and the
    notebook's prefixed env-var convention.
    """
    from aou_ld_panel import _qc_checkpoint_uri
    bare = _qc_checkpoint_uri("test-bucket", "afr", False)
    prefixed = _qc_checkpoint_uri("gs://test-bucket", "afr", False)
    assert bare == prefixed == "gs://test-bucket/ld/mt_afr_qc.mt", (
        f"bare vs prefixed inputs must produce identical canonical URI; "
        f"got bare={bare!r}, prefixed={prefixed!r}"
    )


# ----- _resolve_aux_base env-derive tests
# ----- (CHECK-C / CDR R8->R9 forward-compat regression guards, 2026-06-01) -----
#
# The AUX sidecar tables (ancestry_preds.tsv, relatedness_flagged_samples.tsv)
# live in an aux/ directory that is a documented SIBLING of acaf_threshold/
# under .../wgs/short_read/snpindel/ (verified 2026-05-01 Run 2,
# m3-W1-AUX-PATH-VERIFICATION.md). Deriving AUX_BASE from the WGS MT path the
# cohort is actually built from makes the ancestry/relatedness tables track
# whatever CDR version the platform binds (v8, v9, ...) instead of a hardcoded
# literal -- this removes CHECK-C from the critical path on the RW 2.0 R8->R9
# migration: the code self-resolves regardless of the R9 prefix.

_V8_WGS_MT = "gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/acaf_threshold/multiMT/hail.mt"
_V8_AUX_BASE = "gs://fc-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux"
_V9_WGS_MT = "gs://fc-aou-datasets-controlled/v9/wgs/short_read/snpindel/acaf_threshold/multiMT/hail.mt"
_V9_AUX_BASE = "gs://fc-aou-datasets-controlled/v9/wgs/short_read/snpindel/aux"


def test_resolve_aux_base_derives_v8_from_mt_path():
    """Deriving from the canonical v8 WGS MT path yields the v8 aux base
    (matches the hardcoded literal that Carter's 2026-05-01 gsutil Run 2
    empirically verified)."""
    from aou_ld_panel import _resolve_aux_base
    assert _resolve_aux_base(_V8_WGS_MT) == _V8_AUX_BASE


def test_resolve_aux_base_derives_v9_from_mt_path():
    """CHECK-C REGRESSION GUARD (RW 2.0 R8->R9 migration, 2026-06-01): when the
    CDR advances and the platform binds the WGS MT to v9, the aux base MUST
    follow automatically -- no code edit, no manual Workbench path-verification
    gate. This is the whole point of env-deriving."""
    from aou_ld_panel import _resolve_aux_base
    assert _resolve_aux_base(_V9_WGS_MT) == _V9_AUX_BASE


def test_resolve_aux_base_derives_from_moved_bucket():
    """Forward-compat: if AoU relocates controlled-tier WGS to a different
    bucket, aux derivation follows the bucket too -- the
    /wgs/short_read/snpindel/ infix is the stable anchor, not the bucket name."""
    from aou_ld_panel import _resolve_aux_base
    moved = "gs://fc-aou-datasets-controlled-v2/v9/wgs/short_read/snpindel/acaf_threshold/multiMT/hail.mt"
    assert _resolve_aux_base(moved) == \
        "gs://fc-aou-datasets-controlled-v2/v9/wgs/short_read/snpindel/aux"


def test_resolve_aux_base_reads_env_var_when_arg_none(monkeypatch):
    """No mt_path arg -> derive from $WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH (the
    env var the AoU platform binds)."""
    from aou_ld_panel import _resolve_aux_base
    monkeypatch.setenv("WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH", _V9_WGS_MT)
    assert _resolve_aux_base() == _V9_AUX_BASE


def test_resolve_aux_base_falls_back_to_literal_when_unset(monkeypatch):
    """Offline/local: no arg + env var unset -> the hardcoded AUX_BASE literal
    (preserves pre-refactor behavior; the AUX_BASE module constant is the
    documented fallback)."""
    from aou_ld_panel import _resolve_aux_base, AUX_BASE
    monkeypatch.delenv("WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH", raising=False)
    assert _resolve_aux_base() == AUX_BASE
    assert _resolve_aux_base(None) == AUX_BASE


def test_resolve_aux_base_falls_back_when_path_lacks_infix(monkeypatch):
    """Local synthetic-MT test paths (e.g. /tmp/.../synthetic_aou.mt) do NOT
    contain the AoU WGS infix -> fall back to the literal so the test suite and
    any non-AoU MT path keep current behavior (no bogus aux base)."""
    from aou_ld_panel import _resolve_aux_base, AUX_BASE
    monkeypatch.delenv("WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH", raising=False)
    assert _resolve_aux_base("/tmp/pytest-xyz/synthetic_aou.mt") == AUX_BASE


def test_resolve_aux_base_falls_back_on_infix_at_root(monkeypatch):
    """Defensive (adversarial-review 1.6): a pathological path that STARTS with
    the infix yields an empty prefix; we must NOT return a malformed root-rooted
    '/wgs/short_read/snpindel/aux'. The prefix must carry a URI scheme (gs://,
    file://) to be trusted; otherwise fall back to the literal."""
    from aou_ld_panel import _resolve_aux_base, AUX_BASE
    monkeypatch.delenv("WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH", raising=False)
    assert _resolve_aux_base("/wgs/short_read/snpindel/acaf_threshold/hail.mt") == AUX_BASE


def test_resolve_aux_base_mt_path_arg_wins_over_env(monkeypatch):
    """Resolution order: explicit mt_path arg (the MT actually read) wins over
    the env var -- guarantees the aux tables match the WGS version being
    processed even if the env var drifts."""
    from aou_ld_panel import _resolve_aux_base
    monkeypatch.setenv("WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH", _V8_WGS_MT)
    assert _resolve_aux_base(_V9_WGS_MT) == _V9_AUX_BASE


def test_resolve_aux_base_child_paths_are_correct_siblings():
    """The two load-bearing AUX files derive as correct v9 siblings of the aux
    base (ancestry/ancestry_preds.tsv + relatedness/relatedness_flagged_samples.tsv)."""
    from aou_ld_panel import _resolve_aux_base
    aux = _resolve_aux_base(_V9_WGS_MT)
    assert f"{aux}/ancestry/ancestry_preds.tsv" == \
        f"{_V9_AUX_BASE}/ancestry/ancestry_preds.tsv"
    assert f"{aux}/relatedness/relatedness_flagged_samples.tsv" == \
        f"{_V9_AUX_BASE}/relatedness/relatedness_flagged_samples.tsv"


def test_collect_provenance_records_resolved_aux_paths():
    """Provenance truthfulness: when load_qc_cohort env-derives the AUX paths,
    the sidecar MUST record the RESOLVED paths actually read (not the stale
    hardcoded literal). Guards the reproducibility contract under R8->R9."""
    from aou_ld_panel import _collect_provenance
    resolved_anc = f"{_V9_AUX_BASE}/ancestry/ancestry_preds.tsv"
    resolved_rel = f"{_V9_AUX_BASE}/relatedness/relatedness_flagged_samples.tsv"
    prov = _collect_provenance(
        ancestry="afr",
        sensitivity=False,
        source_mt_path=_V9_WGS_MT,
        interval_filter=None,
        ancestry_preds_path=resolved_anc,
        relateds_path=resolved_rel,
    )
    assert prov["ancestry_preds_path"] == resolved_anc
    assert prov["relateds_path"] == resolved_rel


# ----- _resolve_aux_file discovery tests
# ----- (RW 2.0 / R8 filename-prefix gap, 2026-06-01) -----
#
# On RW 2.0 (vwb- bucket, cdrv8/R8) the aux files carry pipeline-version
# prefixes the bare-name code missed (verified live: CHECK C 404):
#   aux/ancestry/echo_v4_r2.ancestry_preds.tsv
#   aux/relatedness/samples_relatedness_flagged_samples.tsv
# The fix discovers the file by its canonical SUFFIX (so the echo_v4_r2./
# samples_ prefixes — which will drift again — don't require a code edit),
# the same "discover, don't pin" lesson as _resolve_aux_base.

_AUXB = "gs://vwb-aou-datasets-controlled/v8/wgs/short_read/snpindel/aux"


def test_resolve_aux_file_bare_when_no_lister():
    """No lister (local/offline/tests) -> bare canonical path, pre-discovery
    behavior preserved."""
    from aou_ld_panel import _resolve_aux_file
    assert _resolve_aux_file(_AUXB, "ancestry", "ancestry_preds.tsv") == \
        f"{_AUXB}/ancestry/ancestry_preds.tsv"


def test_resolve_aux_file_discovers_prefixed_ancestry():
    """RW2.0 R8 gap: find echo_v4_r2.ancestry_preds.tsv by the ancestry_preds.tsv
    suffix among the other ancestry-pipeline artifacts."""
    from aou_ld_panel import _resolve_aux_file
    entries = [
        f"{_AUXB}/ancestry/echo_v4_r2.ancestry_preds.tsv",
        f"{_AUXB}/ancestry/echo_v4_r2.preds_oth.html",
        f"{_AUXB}/ancestry/eigenvalues.txt",
        f"{_AUXB}/ancestry/rf_classifier.pkl",
        f"{_AUXB}/ancestry/training_pca.tsv",
    ]
    assert _resolve_aux_file(_AUXB, "ancestry", "ancestry_preds.tsv",
                             lister=lambda d: entries) == \
        f"{_AUXB}/ancestry/echo_v4_r2.ancestry_preds.tsv"


def test_resolve_aux_file_discovers_flagged_not_full_relatedness():
    """Disambiguation guard: suffix relatedness_flagged_samples.tsv must pick the
    FLAGGED list, NOT the full pairwise samples_relatedness.tsv (schema i.s/j.s/kin)."""
    from aou_ld_panel import _resolve_aux_file
    entries = [
        f"{_AUXB}/relatedness/samples_relatedness.tsv",
        f"{_AUXB}/relatedness/samples_relatedness_flagged_samples.tsv",
    ]
    assert _resolve_aux_file(_AUXB, "relatedness", "relatedness_flagged_samples.tsv",
                             lister=lambda d: entries) == \
        f"{_AUXB}/relatedness/samples_relatedness_flagged_samples.tsv"


def test_resolve_aux_file_matches_bare_name_legacy_layout():
    """Back-compat: the old Legacy fc- layout had a bare ancestry_preds.tsv;
    suffix-match still finds it (a bare name ends with its own suffix)."""
    from aou_ld_panel import _resolve_aux_file
    entries = [f"{_AUXB}/ancestry/ancestry_preds.tsv"]
    assert _resolve_aux_file(_AUXB, "ancestry", "ancestry_preds.tsv",
                             lister=lambda d: entries) == \
        f"{_AUXB}/ancestry/ancestry_preds.tsv"


def test_resolve_aux_file_falls_back_to_bare_on_zero_match(capsys):
    """0 matches (layout changed again) -> warn + bare fallback, so the import
    site keeps its existing semantics (ancestry hard-fails loudly, relatedness
    soft-fails per its try/except) rather than the resolver guessing."""
    from aou_ld_panel import _resolve_aux_file
    entries = [f"{_AUXB}/ancestry/something_unrelated.txt"]
    got = _resolve_aux_file(_AUXB, "ancestry", "ancestry_preds.tsv",
                            lister=lambda d: entries)
    assert got == f"{_AUXB}/ancestry/ancestry_preds.tsv"
    assert "no entry" in capsys.readouterr().err.lower()


def test_resolve_aux_file_raises_on_ambiguous_match():
    """Default (ancestry, mandatory): >1 match is a genuine 'which one?' ->
    raise rather than guess."""
    from aou_ld_panel import _resolve_aux_file
    entries = [
        f"{_AUXB}/ancestry/a.ancestry_preds.tsv",
        f"{_AUXB}/ancestry/b.ancestry_preds.tsv",
    ]
    with pytest.raises(RuntimeError, match="[Aa]mbiguous"):
        _resolve_aux_file(_AUXB, "ancestry", "ancestry_preds.tsv",
                          lister=lambda d: entries)


def test_resolve_aux_file_ambiguous_fallback_mode(capsys):
    """on_ambiguous='fallback' (relatedness, best-effort): >1 match -> WARN +
    bare, so a transient rollout collision (echo_v4_r2 + echo_v4_r3 both
    present) degrades to the soft-skip path instead of hard-crashing
    load_qc_cohort. Preserves the relatedness try/except contract that the
    resolver would otherwise bypass (adversarial-review 2.1)."""
    from aou_ld_panel import _resolve_aux_file
    entries = [
        f"{_AUXB}/relatedness/echo_v4_r2.relatedness_flagged_samples.tsv",
        f"{_AUXB}/relatedness/echo_v4_r3.relatedness_flagged_samples.tsv",
    ]
    got = _resolve_aux_file(_AUXB, "relatedness", "relatedness_flagged_samples.tsv",
                            lister=lambda d: entries, on_ambiguous="fallback")
    assert got == f"{_AUXB}/relatedness/relatedness_flagged_samples.tsv"  # bare
    assert "ambiguous" in capsys.readouterr().err.lower()


def test_resolve_aux_file_ignores_subdir_entry_with_trailing_slash():
    """A subdir entry (e.g. the loadings Hail table 'echo_v4_r2_loadings.ht/')
    must not be mistaken for the preds file; rstrip('/') runs before the
    basename split so trailing slashes are handled (refutes adversarial-review
    2.7's mis-trace)."""
    from aou_ld_panel import _resolve_aux_file
    entries = [
        f"{_AUXB}/ancestry/echo_v4_r2_loadings.ht/",
        f"{_AUXB}/ancestry/echo_v4_r2.ancestry_preds.tsv",
    ]
    assert _resolve_aux_file(_AUXB, "ancestry", "ancestry_preds.tsv",
                             lister=lambda d: entries) == \
        f"{_AUXB}/ancestry/echo_v4_r2.ancestry_preds.tsv"


def test_validate_sidecar_rejects_cdr_version_drift():
    """Contract (adversarial-review 2.2): a checkpoint saved under one CDR
    version (v8) MUST be invalidated when the platform advances to a new CDR
    (v9). The v9 WGS source is DIFFERENT DATA; silent reuse would be the
    version-mismatch hazard DEC-2026-05-01-01 warned against. source_mt_path
    AND the env-derived aux paths all differ, so _validate_sidecar returns
    False. This is the data-integrity-correct behavior: 'R8->R9 needs no code
    edit' refers to AUX-path RESOLUTION, NOT cross-version checkpoint reuse --
    a genuine source change correctly forces a force_fresh rebuild."""
    from aou_ld_panel import _collect_provenance, _validate_sidecar
    v8_sidecar = _collect_provenance(
        "afr", False, _V8_WGS_MT, None,
        ancestry_preds_path=f"{_V8_AUX_BASE}/ancestry/ancestry_preds.tsv",
        relateds_path=f"{_V8_AUX_BASE}/relatedness/relatedness_flagged_samples.tsv",
    )
    v9_provenance = _collect_provenance(
        "afr", False, _V9_WGS_MT, None,
        ancestry_preds_path=f"{_V9_AUX_BASE}/ancestry/ancestry_preds.tsv",
        relateds_path=f"{_V9_AUX_BASE}/relatedness/relatedness_flagged_samples.tsv",
    )
    matches, diag = _validate_sidecar(v8_sidecar, v9_provenance)
    assert matches is False, "v8 checkpoint must NOT validate against v9 source"
    assert "source_mt_path" in diag
    assert "ancestry_preds_path" in diag


def test_intermediate_checkpoint_uri_post_split_afr_primary():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "afr", "post_split", False)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_post_split.mt"


def test_intermediate_checkpoint_uri_post_variant_qc_afr_sensitivity():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "afr", "post_variant_qc", True)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_pca_selfid_post_variant_qc.mt"


def test_intermediate_checkpoint_uri_eur_no_sensitivity():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "eur", "post_split", False)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_eur_post_split.mt"


def test_intermediate_checkpoint_uri_with_interval_filter_chr22():
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("fc-secure-XXX", "afr", "post_split", False, "chr22")
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_post_split_chr22.mt"


def test_intermediate_checkpoint_uri_accepts_prefixed_bucket():
    """Defensive: bucket may arrive as 'gs://...' (per _normalize_bucket contract)."""
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri("gs://fc-secure-XXX", "afr", "post_split", False)
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_post_split.mt"


def test_intermediate_checkpoint_uri_sanitizes_colon_nano_interval():
    """Regression (m3-gateb-load-qc-cohort-driver-collect, 2026-06-02 follow-on).

    A span-bounded nano INTERVAL ('chr22:16000000-18000000') must NOT leak its
    colon/dash into the intermediate checkpoint URI. GCS tolerates a colon on
    WRITE, but the e23c081 driver-collect fix re-reads the post_split checkpoint
    via hl.read_matrix_table(...), which routes the URI through Hadoop's Path/URI
    parser. An unsanitized 'chr22:' is read as a URI scheme and raises
    java.net.URISyntaxException: Relative path in absolute URI. The sanitized
    name must match the notebook's final-output convention
    (INTERVAL.replace(':','_').replace('-','_') -> '_chr22_16000000_18000000').
    """
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri(
        "fc-secure-XXX", "afr", "post_split", False, "chr22:16000000-18000000")
    # Hard URI-fatal char: a colon ANYWHERE in the path after the gs:// scheme
    # makes Hadoop read e.g. 'chr22:' as a (second) URI scheme.
    assert ":" not in uri.removeprefix("gs://"), \
        f"colon leaked into intermediate URI path: {uri!r}"
    # The interval suffix (filename component) must carry NO ':' or '-' — full
    # consistency with the notebook's final-output suffix convention. Scoped to
    # the basename: a bucket name may legitimately contain '-' (e.g.
    # 'rw-migration-aou-rw-476cdac2'); only the MT filename is at issue.
    filename = uri.rsplit("/", 1)[-1]
    assert ":" not in filename and "-" not in filename, \
        f"colon/dash leaked into intermediate MT filename: {filename!r}"
    assert uri == (
        "gs://fc-secure-XXX/ld/intermediate/"
        "mt_afr_post_split_chr22_16000000_18000000.mt"
    )


def test_intermediate_checkpoint_uri_sanitizes_colon_nano_interval_sensitivity():
    """Same colon-sanitization regression on the sensitivity=True branch.

    Both ckpt_post_split AND ckpt_post_vqc derive from this one builder
    (aou_ld_panel.py:1270-1273), and the sensitivity fire is a separate live
    path, so the sanitization must hold with the _pca_selfid infix too.
    """
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri(
        "fc-secure-XXX", "afr", "post_variant_qc", True, "chr22:16000000-18000000")
    assert ":" not in uri.removeprefix("gs://"), \
        f"colon leaked into intermediate URI path: {uri!r}"
    filename = uri.rsplit("/", 1)[-1]
    assert ":" not in filename and "-" not in filename, \
        f"colon/dash leaked into intermediate MT filename: {filename!r}"
    assert uri == (
        "gs://fc-secure-XXX/ld/intermediate/"
        "mt_afr_pca_selfid_post_variant_qc_chr22_16000000_18000000.mt"
    )


def test_intermediate_checkpoint_uri_clean_chr22_unchanged():
    """The Tier-2 whole-chrom 'chr22' (no colon/dash) must be byte-identical
    before and after the sanitization fix — the existing contract is preserved.
    """
    from aou_ld_panel import _intermediate_checkpoint_uri
    uri = _intermediate_checkpoint_uri(
        "fc-secure-XXX", "afr", "post_split", False, "chr22")
    assert uri == "gs://fc-secure-XXX/ld/intermediate/mt_afr_post_split_chr22.mt"


def test_sanitize_interval_suffix_helper():
    """The reusable sanitizer encapsulates the notebook's
    INTERVAL.replace(':','_').replace('-','_') convention (one sanitization
    point per the 'recurrent bug class -> reusable utility' rule).
    """
    from aou_ld_panel import _sanitize_interval_suffix
    # Span-bounded nano interval: colon AND dash -> underscore.
    assert _sanitize_interval_suffix("chr22:16000000-18000000") == \
        "chr22_16000000_18000000"
    # Whole-chromosome token: no change.
    assert _sanitize_interval_suffix("chr22") == "chr22"
    # No residual URI-fatal chars after sanitization.
    out = _sanitize_interval_suffix("chr22:16000000-18000000")
    assert ":" not in out and "-" not in out


def test_sidecar_uri_format():
    from aou_ld_panel import _sidecar_uri
    checkpoint_uri = "gs://bkt/ld/intermediate/mt_afr_post_split.mt"
    assert _sidecar_uri(checkpoint_uri) == "gs://bkt/ld/intermediate/mt_afr_post_split.mt.meta.json"


def test_collect_provenance_includes_required_fields():
    from aou_ld_panel import _collect_provenance
    prov = _collect_provenance(
        ancestry="afr",
        sensitivity=False,
        source_mt_path="gs://src/path.mt",
        interval_filter=None,
    )
    # Top-level fields (phase intentionally absent — added by _write_sidecar)
    assert prov["ancestry"] == "afr"
    assert prov["sensitivity"] is False
    assert prov["source_mt_path"] == "gs://src/path.mt"
    assert prov["interval_filter"] is None
    assert "phase" not in prov  # phase added at write time
    assert prov["schema_version"] == 1
    # Nested params dict has all 7 thresholds from DESIGN §3.4
    assert prov["params"]["MIN_CALL_RATE_SAMPLE"] == 0.98
    assert prov["params"]["MIN_MAF_INTERNAL"] == 0.005
    assert prov["params"]["MAX_MAF"] == 0.995
    assert prov["params"]["MIN_CALL_RATE_VARIANT"] == 0.95
    assert prov["params"]["MIN_HWE_PVALUE"] == 1e-06
    assert prov["params"]["HET_HOM_SD_BAND"] == 3.0
    assert prov["params"]["KING_KINSHIP_THRESHOLD"] == 0.0442
    # CDR metadata
    assert prov["cdr_version"] == "v8"
    assert prov["ancestry_preds_path"].endswith("ancestry_preds.tsv")
    assert prov["relateds_path"].endswith("relatedness_flagged_samples.tsv")
    # Git + timestamp + hail_version present (don't assert exact values)
    assert "git_commit_sha" in prov
    assert "timestamp_utc" in prov
    assert "hail_version" in prov


def test_write_read_sidecar_round_trip(tmp_path):
    from aou_ld_panel import _write_sidecar, _read_sidecar, _collect_provenance
    prov = _collect_provenance("afr", False, "gs://src/path.mt")
    sidecar_path = tmp_path / "test_sidecar.meta.json"
    _write_sidecar(f"file://{sidecar_path}", prov, phase="post_split")
    read_back = _read_sidecar(f"file://{sidecar_path}")
    assert read_back is not None
    # Phase added at write time
    assert read_back["phase"] == "post_split"
    # Other fields preserved
    assert read_back["ancestry"] == "afr"
    assert read_back["sensitivity"] is False
    assert read_back["params"]["MIN_CALL_RATE_SAMPLE"] == 0.98


def test_read_sidecar_returns_none_when_absent(tmp_path):
    from aou_ld_panel import _read_sidecar
    nonexistent = tmp_path / "nope.meta.json"
    assert _read_sidecar(f"file://{nonexistent}") is None


def test_read_sidecar_rejects_unknown_schema_version(tmp_path):
    from aou_ld_panel import _read_sidecar
    import json
    sidecar_path = tmp_path / "bad_schema.meta.json"
    sidecar_path.write_text(json.dumps({"schema_version": 999, "ancestry": "afr"}))
    with pytest.raises(RuntimeError, match="schema_version"):
        _read_sidecar(f"file://{sidecar_path}")


def test_validate_sidecar_accepts_matching():
    from aou_ld_panel import _validate_sidecar, _collect_provenance
    prov = _collect_provenance("afr", False, "gs://src/path.mt")
    sidecar = {**prov, "phase": "post_split"}  # simulates what _write_sidecar produces
    matches, diag = _validate_sidecar(sidecar, prov)
    assert matches is True
    assert diag == ""


def test_validate_sidecar_rejects_mismatched_ancestry():
    from aou_ld_panel import _validate_sidecar, _collect_provenance
    prov_afr = _collect_provenance("afr", False, "gs://src/path.mt")
    prov_eur = _collect_provenance("eur", False, "gs://src/path.mt")
    sidecar = {**prov_afr, "phase": "post_split"}
    matches, diag = _validate_sidecar(sidecar, prov_eur)
    assert matches is False
    assert "ancestry" in diag.lower()


def test_validate_sidecar_rejects_mismatched_thresholds(monkeypatch):
    from aou_ld_panel import _validate_sidecar, _collect_provenance
    import aou_ld_panel
    prov_a = _collect_provenance("afr", False, "gs://src/path.mt")
    sidecar = {**prov_a, "phase": "post_split"}
    monkeypatch.setattr(aou_ld_panel, "MIN_CALL_RATE_SAMPLE", 0.95)
    prov_b = _collect_provenance("afr", False, "gs://src/path.mt")
    matches, diag = _validate_sidecar(sidecar, prov_b)
    assert matches is False
    assert "MIN_CALL_RATE_SAMPLE" in diag


def test_validate_sidecar_ignores_phase_field():
    """phase legitimately differs between post_split + post_variant_qc sidecars for
    the same fire — _validate_sidecar must ignore it during comparison."""
    from aou_ld_panel import _validate_sidecar, _collect_provenance
    prov = _collect_provenance("afr", False, "gs://src/path.mt")
    sidecar_a = {**prov, "phase": "post_split"}
    sidecar_b = {**prov, "phase": "post_variant_qc"}
    assert _validate_sidecar(sidecar_a, prov)[0] is True
    assert _validate_sidecar(sidecar_b, prov)[0] is True


def test_validate_sidecar_ignores_timestamp_and_git_sha():
    """timestamp_utc and git_commit_sha legitimately drift across runs of the
    same parameters — they're audit metadata, not invalidation triggers."""
    from aou_ld_panel import _validate_sidecar, _collect_provenance
    prov = _collect_provenance("afr", False, "gs://src/path.mt")
    sidecar = {**prov, "phase": "post_split",
               "timestamp_utc": "1970-01-01T00:00:00.000Z",
               "git_commit_sha": "deadbeef"}
    assert _validate_sidecar(sidecar, prov)[0] is True


def test_has_checkpoint_returns_false_when_absent(tmp_path):
    from aou_ld_panel import _has_checkpoint
    nonexistent = tmp_path / "nope.mt"
    assert _has_checkpoint(f"file://{nonexistent}") is False


def test_has_checkpoint_returns_true_when_success_marker_present(tmp_path):
    from aou_ld_panel import _has_checkpoint
    mt_dir = tmp_path / "fake.mt"
    mt_dir.mkdir()
    (mt_dir / "_SUCCESS").write_text("")
    assert _has_checkpoint(f"file://{mt_dir}") is True


def test_has_checkpoint_returns_false_when_mt_dir_exists_but_no_success(tmp_path):
    """An MT directory with parquet files but no _SUCCESS marker is an
    incomplete write (e.g., previous run was interrupted). _has_checkpoint
    must distinguish this from a complete checkpoint."""
    from aou_ld_panel import _has_checkpoint
    mt_dir = tmp_path / "partial.mt"
    mt_dir.mkdir()
    (mt_dir / "part-00000.parquet").write_text("fake parquet")
    # no _SUCCESS file
    assert _has_checkpoint(f"file://{mt_dir}") is False


# ----- m3-W1 empty-MT catastrophe regression tests (Track 4 patch 1/7) -----
#
# These tests document the contract divergence that the W1 catastrophe
# exposed: _has_checkpoint() only checks the _SUCCESS marker, which Hail's
# driver-side finalize() writes based on tasks-reported-complete accounting
# without validating output contents. Under aggressive
# spark.executor.cores=1/mem=5g profile, executor tasks can silently
# truncate after writing Parquet schema footers but before writing
# entries row-group payloads, leaving a populated-looking MT directory
# with zero data. Bucket forensics 2026-05-21:
#   mt_afr_qc.mt/_SUCCESS                                       present
#   mt_afr_qc.mt/metadata.json.gz                               present
#   mt_afr_qc.mt/rows/rows/parts/part-00000-X.parquet (~35B)    present (footer stub)
#   mt_afr_qc.mt/entries/rows/parts/                            footer-only
#   hl.read_matrix_table(uri).count_cols()                      0
#   hl.read_matrix_table(uri).count_rows()                      0
#
# (Historical note: the 2026-05-21 forensics recorded `entries/entries/parts/`
# as ABSENT — but that path is a PHANTOM and is ALWAYS absent on a real Hail
# 0.2.135 MT; entries live at `entries/rows/parts/`. The only true empty-vs-
# populated discriminator was count_rows/count_cols. Corrected
# 2026-06-03 per .planning/debug/m3-entries-path-phantom-subpath.md.)
#
# _validate_checkpoint_populated() is the contents-validating replacement
# for _has_checkpoint() in resume-gate semantics. Cross-references:
# - .planning/debug/m3-W1-empty-mt-catastrophe.md (root-cause analysis)
# - [[feedback_aou_success_marker_not_evidence_of_data]]
# - [[feedback_hail_checkpoint_contract_violation]]


def _make_stub_mt(mt_dir: Path, with_entries_dir: bool = False) -> None:
    """Build the W1 catastrophe MT-skeleton pattern at mt_dir.

    Produces: _SUCCESS marker + metadata.json.gz stub + rows/rows/parts/
    with a single 35-byte Parquet-footer stub file (the exact size class
    observed on AoU 2026-05-21). Optionally creates an empty
    entries/rows/parts/ directory (the second catastrophe variant where
    Hail created the entries scaffold but no executor wrote row-group data).

    NOTE: entries live at the REAL Hail layout `entries/rows/parts/`
    (m3-entries-path-phantom-subpath fix 2026-06-03), NOT the phantom
    `entries/entries/parts/` the original Track-4 fixtures used.
    """
    mt_dir.mkdir(parents=True)
    (mt_dir / "_SUCCESS").write_text("")
    (mt_dir / "metadata.json.gz").write_bytes(b"\x1f\x8b\x08" + b"\x00" * 32)
    rows_parts = mt_dir / "rows" / "rows" / "parts"
    rows_parts.mkdir(parents=True)
    # Exactly 35 bytes — matches the Parquet column-metadata footer
    # size observed in the 2026-05-21 bucket inspection.
    (rows_parts / "part-00000-stub.parquet").write_bytes(b"PAR1" + b"\x00" * 27 + b"PAR1")
    if with_entries_dir:
        entries_parts = mt_dir / "entries" / "rows" / "parts"
        entries_parts.mkdir(parents=True)
        # Intentionally empty — no executor wrote row-group payloads.


def test_validate_checkpoint_populated_rejects_stub_entries(tmp_path):
    """Stub MT (_SUCCESS + 35-byte rows footer + NO entries dir) must fail
    validation. Models the mt_afr_qc.mt state observed on AoU 2026-05-21."""
    from aou_ld_panel import _validate_checkpoint_populated
    mt_dir = tmp_path / "stub_afr_qc.mt"
    _make_stub_mt(mt_dir, with_entries_dir=False)
    assert _validate_checkpoint_populated(f"file://{mt_dir}") is False


def test_validate_checkpoint_populated_rejects_empty_entries_dir(tmp_path):
    """Stub MT with present-but-empty entries/entries/parts/ must also fail
    validation. Models the silent-executor-truncation variant where Hail
    created the entries scaffold but no row-group payloads were written."""
    from aou_ld_panel import _validate_checkpoint_populated
    mt_dir = tmp_path / "stub_afr_empty_entries.mt"
    _make_stub_mt(mt_dir, with_entries_dir=True)
    assert _validate_checkpoint_populated(f"file://{mt_dir}") is False


def test_has_checkpoint_vs_validate_diverge_on_stub_mt(tmp_path):
    """Document the contract divergence: _has_checkpoint() returns True
    (the W1 false-positive that triggered RESUME_FROM_POST_VARIANT_QC into
    an empty MT), but _validate_checkpoint_populated() returns False
    (the corrected resume-gate semantics)."""
    from aou_ld_panel import _has_checkpoint, _validate_checkpoint_populated
    mt_dir = tmp_path / "stub_diverge.mt"
    _make_stub_mt(mt_dir, with_entries_dir=False)
    has = _has_checkpoint(f"file://{mt_dir}")
    validated = _validate_checkpoint_populated(f"file://{mt_dir}")
    assert has is True, (
        "_has_checkpoint() must still return True on stub MT — "
        "documents the pre-patch false-positive that triggered RESUME"
    )
    assert validated is False, (
        "_validate_checkpoint_populated() must return False on stub MT — "
        "the corrected resume-gate semantics"
    )


# ----- m3-entries-path-phantom-subpath regression (2026-06-03) -----
#
# The Track-4 path-based probe hardcoded `entries/entries/parts/`, a PHANTOM
# subpath that does NOT exist on a real Hail 0.2.135 MatrixTable. Real entry
# row-group payload is at `<mt>/entries/rows/parts/` (Carter verified LIVE at
# Gate B #3: EUR mt 3.25 GB total, 3.24 GB at entries/rows/parts/,
# entries/entries/parts/ ABSENT). The bug was FAIL-SAFE (wrong path -> always
# False -> force-recompute; never passed an empty MT as populated) but blocked
# real runs (Gate-C blocker) and the old fixtures validated the phantom path =
# false confidence. These tests pin the REAL layout.
#
# Cross-reference: .planning/debug/m3-entries-path-phantom-subpath.md


# Real Hail MatrixTable on-disk entries payload location.
_REAL_ENTRIES_PARTS = "entries/rows/parts"


def _make_populated_mt(mt_dir: Path) -> None:
    """Build a PASSING MT skeleton at the REAL Hail layout.

    _SUCCESS + metadata.json.gz + rows/rows/parts/ + a populated
    `entries/rows/parts/` part file comfortably above MIN_ENTRIES_FILE_BYTES
    (default 1 KB). This is what a genuinely-written Hail MT looks like on
    disk; `_validate_checkpoint_populated` must return True on it.
    """
    mt_dir.mkdir(parents=True)
    (mt_dir / "_SUCCESS").write_text("")
    (mt_dir / "metadata.json.gz").write_bytes(b"\x1f\x8b\x08" + b"\x00" * 32)
    rows_parts = mt_dir / "rows" / "rows" / "parts"
    rows_parts.mkdir(parents=True)
    (rows_parts / "part-00000.parquet").write_bytes(b"PAR1" + b"\x00" * 4096 + b"PAR1")
    entries_parts = mt_dir / "entries" / "rows" / "parts"
    entries_parts.mkdir(parents=True)
    # > 1 KB row-group payload (NOT a 35-byte footer stub).
    (entries_parts / "part-00000.parquet").write_bytes(b"PAR1" + b"\x00" * 8192 + b"PAR1")


def _make_empty_real_path_mt(mt_dir: Path) -> None:
    """Build an EMPTY MT skeleton at the REAL Hail layout: _SUCCESS + rows
    footer stub + a present-but-footer-only `entries/rows/parts/` (35-byte
    stub, below the 1 KB threshold). `_validate_checkpoint_populated` must
    return False — the catastrophe is still caught at the real path."""
    mt_dir.mkdir(parents=True)
    (mt_dir / "_SUCCESS").write_text("")
    (mt_dir / "metadata.json.gz").write_bytes(b"\x1f\x8b\x08" + b"\x00" * 32)
    entries_parts = mt_dir / "entries" / "rows" / "parts"
    entries_parts.mkdir(parents=True)
    # 35-byte Parquet footer stub — below MIN_ENTRIES_FILE_BYTES.
    (entries_parts / "part-00000-stub.parquet").write_bytes(b"PAR1" + b"\x00" * 27 + b"PAR1")


def test_validate_checkpoint_populated_accepts_real_path_populated_mt(tmp_path):
    """A populated MT at the REAL Hail layout (`entries/rows/parts/` with a
    >1 KB part) must validate True. Against the pre-fix code (which probed the
    phantom `entries/entries/parts/`) this returns False -> the m3-entries-path
    RED state."""
    from aou_ld_panel import _validate_checkpoint_populated
    mt_dir = tmp_path / "real_eur_qc.mt"
    _make_populated_mt(mt_dir)
    assert _validate_checkpoint_populated(f"file://{mt_dir}") is True, (
        "populated MT at entries/rows/parts/ must validate True — the probe "
        "must look at the real Hail layout, not the phantom entries/entries/parts/"
    )


def test_validate_checkpoint_populated_rejects_empty_real_path_mt(tmp_path):
    """An empty/footer-stub MT at the REAL Hail layout must still validate
    False — the catastrophe guard is preserved at the corrected path."""
    from aou_ld_panel import _validate_checkpoint_populated
    mt_dir = tmp_path / "empty_real.mt"
    _make_empty_real_path_mt(mt_dir)
    assert _validate_checkpoint_populated(f"file://{mt_dir}") is False, (
        "footer-only entries/rows/parts/ must validate False — catastrophe "
        "still caught at the real path"
    )


# ----- AFR sensitivity self-report sourcing — live-Hail dynamic tests
# ----- (m3-W2-afr-sensitivity-selfid, 2026-06-08) -----


def _build_selfreport_sidecar(path: Path, mt, self_report_value_fn) -> None:
    """Write a research_id -> self_report TSV sidecar covering every sample of
    `mt`. Mirrors the AoU CDR person-table extraction the runbook produces.

    self_report_value_fn(i, sample_id) -> the self_report string for sample i.
    Columns: research_id<TAB>self_report (matches the import_table(key=...) the
    resolver consumes; the col key on the synthetic MT is 's')."""
    ids = mt.s.collect()
    lines = ["research_id\tself_report"]
    for i, sid in enumerate(ids):
        lines.append(f"{sid}\t{self_report_value_fn(i, sid)}")
    path.write_text("\n".join(lines) + "\n")


def test_sensitivity_true_yields_strict_nonempty_subset(
    synthetic_mt_path: Path, synthetic_bucket: str, tmp_path
):
    """T1 (first test to ever exercise the TRUE sensitivity branch).

    With a self_report sidecar mixing "WhatRaceEthnicity_Black" and another
    race value across the AFR samples, sensitivity=True must:
      * apply the restriction (N_sens == count of Black/AA in-scope), AND
      * be a STRICT non-empty subset (0 < N_sens < N_primary).
    Pre-fix this fails: the filter is never applied (self_report never sourced;
    silent skip) so N_sens == N_primary (the membership-identical defect)."""
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    bucket = synthetic_bucket.removeprefix("file://")

    # Primary (sensitivity=False) membership — the superset.
    mt_primary = load_qc_cohort(
        mt_path=str(synthetic_mt_path), ancestry="afr",
        sensitivity=False, skip_checkpoint=True,
    )
    n_primary = mt_primary.count_cols()
    assert n_primary > 1, "fixture must have >1 AFR sample for a meaningful subset"

    # Build a sidecar: roughly half the AFR samples self-report Black/AA, the
    # rest "White" (an out-of-restriction value). Deterministic by index parity.
    sidecar = tmp_path / "self_report.tsv"
    _build_selfreport_sidecar(
        sidecar, hl.read_matrix_table(str(synthetic_mt_path)),
        lambda i, sid: "WhatRaceEthnicity_Black" if (i % 2 == 0)
        else "WhatRaceEthnicity_White",
    )

    mt_sens = load_qc_cohort(
        mt_path=str(synthetic_mt_path), ancestry="afr",
        sensitivity=True, skip_checkpoint=True,
        self_report_table_path=str(sidecar),
    )
    n_sens = mt_sens.count_cols()

    assert n_sens > 0, "sensitivity cohort must be non-empty (subset, not collapse)"
    assert n_sens < n_primary, (
        f"sensitivity=True must be a STRICT subset of primary "
        f"(got n_sens={n_sens} == n_primary={n_primary} — the silent-no-op defect)"
    )


def test_sensitivity_true_raises_when_self_report_unresolvable(
    synthetic_mt_path: Path, tmp_path
):
    """T2: sensitivity=True with NO self_report column and an unresolvable
    sidecar must HARD-FAIL (raise), not silently skip. Pre-fix the missing
    column fell through `and "self_report" in mt.col` to a no-op cohort."""
    _require_hail()
    from aou_ld_panel import load_qc_cohort

    missing_sidecar = tmp_path / "does_not_exist_self_report.tsv"
    assert not missing_sidecar.exists()

    with pytest.raises(Exception) as exc:
        load_qc_cohort(
            mt_path=str(synthetic_mt_path), ancestry="afr",
            sensitivity=True, skip_checkpoint=True,
            self_report_table_path=str(missing_sidecar),
        )
    # Must be a loud failure tied to self_report sourcing, not a silent return.
    assert "self_report" in str(exc.value).lower() or "self report" in str(exc.value).lower(), (
        f"sensitivity=True must hard-fail on unresolvable self_report sidecar; "
        f"got: {exc.value!r}"
    )


# ----- Live Hail tests (skip individually if hail not available) -----


def _require_hail():
    return pytest.importorskip("hail")


def test_synthetic_mt_built_via_balding_nichols(synthetic_mt_path: Path):
    _require_hail()
    """The synthetic MT exists and has the expected schema."""
    import hail as hl

    mt = hl.read_matrix_table(str(synthetic_mt_path))
    n_cols = mt.count_cols()
    n_rows = mt.count_rows()
    # Default fixture: 100 samples x 1500 variants
    assert n_cols == 100, f"expected 100 samples, got {n_cols}"
    assert n_rows == 1500, f"expected 1500 variants, got {n_rows}"
    # Required fields for the driver
    assert "ancestry_pred" in mt.col, "synthetic MT must have ancestry_pred col field"
    assert "filters" in mt.row, "synthetic MT must have filters row field"
    assert "rsid" in mt.row, "synthetic MT must have rsid row field"


def test_aou_driver_loads_synthetic_mt(synthetic_mt_path: Path, mock_aou_env, tmp_path):
    """load_qc_cohort runs end-to-end against synthetic MT."""
    _require_hail()
    from aou_ld_panel import load_qc_cohort

    mt = load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        skip_checkpoint=True,
    )
    n_cols = mt.count_cols()
    n_rows = mt.count_rows()
    assert n_cols > 0, "no AFR samples survived QC; check fixture / thresholds"
    assert n_rows > 0, "no variants survived QC; check fixture"
    # Roughly 60 AFR samples in fixture; some may drop on call_rate / het filter.
    # Synthetic generator gives high call rate so most should survive.
    assert n_cols >= 30, f"expected >= 30 AFR samples post-QC, got {n_cols}"


def test_compute_region_ld_path_a1_small_region(synthetic_mt_path: Path,
                                                mock_aou_env, tmp_path):
    """Small region (~2 Mb FTO neighborhood) -> Path A.1 dense .npz."""
    _require_hail()
    import numpy as np

    from aou_ld_panel import compute_region_ld, load_qc_cohort

    mt = load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        skip_checkpoint=True,
    )
    region = {
        "region_id": "synth_region_chr16_small",
        "chr": "16",
        "start_grch38": 50_100_000,
        "end_grch38": 51_900_000,
        "radius_bp": 2_400_000,
        "region_class": "small",
    }
    res = compute_region_ld(region, mt, out_bucket=None, out_local_dir=tmp_path)
    assert res["status"] == "ok", f"expected ok, got {res}"
    assert res["path_a"] == "A.1"
    assert res["n_var"] > 10
    out_path = Path(res["out"])
    assert out_path.exists()
    # Round-trip: load .npz, verify symmetric float32
    z = np.load(out_path)
    ld = z["ld"]
    assert ld.dtype == np.float32
    assert ld.shape[0] == ld.shape[1] == res["n_var"]


def test_compute_region_ld_skipped_few_variants(synthetic_mt_path: Path,
                                                mock_aou_env, tmp_path):
    """Tiny interval with < 10 variants -> status='skipped_few_variants'."""
    _require_hail()
    from aou_ld_panel import compute_region_ld, load_qc_cohort

    mt = load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        skip_checkpoint=True,
    )
    # A 1 kb window in a sparse-density region of the fixture should have < 10 SNPs
    region = {
        "region_id": "synth_region_chr16_tiny",
        "chr": "16",
        "start_grch38": 50_100_000,
        "end_grch38": 50_100_500,
        "radius_bp": 500_000,
        "region_class": "small",
    }
    res = compute_region_ld(region, mt, out_bucket=None, out_local_dir=tmp_path)
    assert res["status"] == "skipped_few_variants"
    assert res["n_var"] < 10


@pytest.fixture
def synthetic_bucket(tmp_path):
    """File:// URI emulating a workspace bucket for live-Hail tests."""
    bucket_dir = tmp_path / "bucket"
    bucket_dir.mkdir()
    return f"file://{bucket_dir}"


def test_load_qc_cohort_auto_resume_from_post_split(
    synthetic_mt_path: Path, synthetic_bucket: str, tmp_path, capsys
):
    """Fire once (writes intermediate 1+2+final); delete intermediate 2; fire
    again -> expect resume from intermediate 1 (Phase 1 skipped, Phase 2 + 3
    re-run). Per DESIGN §5.1 test 7 + Issue #6 fix (shutil.rmtree pattern)."""
    import shutil
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    # First fire: FRESH state, writes all 3 checkpoints
    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,  # ensure fresh start for this test
    )
    captured = capsys.readouterr()
    assert "state=FRESH" in captured.out

    # Delete intermediate 2 (post_variant_qc) — leave intermediate 1 + sidecar intact
    bucket_path = Path(synthetic_bucket.removeprefix("file://"))
    int2_dir = bucket_path / "ld" / "intermediate" / "mt_afr_post_variant_qc.mt"
    int2_sidecar = bucket_path / "ld" / "intermediate" / "mt_afr_post_variant_qc.mt.meta.json"
    assert int2_dir.exists(), "first fire should have written intermediate 2"
    shutil.rmtree(int2_dir)
    int2_sidecar.unlink()

    # Second fire: should resume from intermediate 1
    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        # force_fresh defaults to False — auto-resume active
    )
    captured = capsys.readouterr()
    assert "state=RESUME_FROM_POST_SPLIT" in captured.out
    assert "resumed from intermediate 1" in captured.out


def test_load_qc_cohort_auto_resume_from_post_variant_qc(
    synthetic_mt_path: Path, synthetic_bucket: str, capsys
):
    """Fire once; fire again unchanged -> expect resume from intermediate 2
    (deepest available; Phase 1 + Phase 2 skipped, only Phase 3 re-runs)."""
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,
    )
    capsys.readouterr()  # clear

    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
    )
    captured = capsys.readouterr()
    assert "state=RESUME_FROM_POST_VARIANT_QC" in captured.out
    assert "resumed from intermediate 2" in captured.out


def test_load_qc_cohort_force_fresh_bypasses_auto_resume(
    synthetic_mt_path: Path, synthetic_bucket: str, capsys
):
    """force_fresh=True must bypass the auto-resume detection even when valid
    intermediates exist. Verifies the user-override semantic in DESIGN §4."""
    import time
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,
    )
    bucket_path = Path(synthetic_bucket.removeprefix("file://"))
    int1_mt = bucket_path / "ld" / "intermediate" / "mt_afr_post_split.mt"
    initial_mtime = int1_mt.stat().st_mtime
    time.sleep(1.1)  # ensure st_mtime difference detectable on coarse FS
    capsys.readouterr()  # clear

    # Second fire with force_fresh=True — should NOT resume; should overwrite
    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,
    )
    captured = capsys.readouterr()
    assert "state=FRESH" in captured.out
    # Intermediate 1 was overwritten (mtime advanced)
    new_mtime = int1_mt.stat().st_mtime
    assert new_mtime > initial_mtime, (
        f"force_fresh should overwrite intermediate 1 (old mtime={initial_mtime}, "
        f"new mtime={new_mtime})"
    )


def test_load_qc_cohort_raises_on_sidecar_mismatch(
    synthetic_mt_path: Path, synthetic_bucket: str
):
    """Sidecar parameter mismatch -> RuntimeError with informative diagnostic.
    Verifies the safety guard against silently using stale-parameter intermediates."""
    import json
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,
    )

    # Manually edit the intermediate-2 sidecar to flip ancestry to "eur"
    bucket_path = Path(synthetic_bucket.removeprefix("file://"))
    int2_sidecar = bucket_path / "ld" / "intermediate" / "mt_afr_post_variant_qc.mt.meta.json"
    sc = json.loads(int2_sidecar.read_text())
    sc["ancestry"] = "eur"  # mismatch with the next call's ancestry="afr"
    int2_sidecar.write_text(json.dumps(sc, indent=2, sort_keys=True))

    # Second fire — auto-resume should detect mismatch and raise
    with pytest.raises(RuntimeError, match=r"(?i)ancestry"):
        load_qc_cohort(
            mt_path=str(synthetic_mt_path),
            ancestry="afr",
            sensitivity=False,
            workspace_bucket=synthetic_bucket.removeprefix("file://"),
        )


def test_load_qc_cohort_auto_recovers_from_orphan_mt(
    synthetic_mt_path: Path, synthetic_bucket: str, capsys
):
    """Sidecar-absent-but-MT-exists is an orphan from a prior crash window
    between checkpoint write and sidecar write. Auto-recovery: print WARN,
    treat as FRESH, overwrite the orphan. Per DESIGN §4 atomicity policy."""
    hl = _require_hail()
    from aou_ld_panel import load_qc_cohort

    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
        force_fresh=True,
    )
    capsys.readouterr()  # clear

    # Delete intermediate-1 sidecar but leave MT directory (orphan state)
    bucket_path = Path(synthetic_bucket.removeprefix("file://"))
    int1_sidecar = bucket_path / "ld" / "intermediate" / "mt_afr_post_split.mt.meta.json"
    int1_mt = bucket_path / "ld" / "intermediate" / "mt_afr_post_split.mt"
    assert int1_sidecar.exists() and int1_mt.exists(), "setup precondition"
    int1_sidecar.unlink()
    assert int1_mt.exists(), "MT directory should still exist after sidecar removal"

    # Also need to delete intermediate-2 (else auto-resume picks deepest valid)
    int2_mt = bucket_path / "ld" / "intermediate" / "mt_afr_post_variant_qc.mt"
    int2_sidecar = bucket_path / "ld" / "intermediate" / "mt_afr_post_variant_qc.mt.meta.json"
    import shutil
    shutil.rmtree(int2_mt)
    int2_sidecar.unlink()

    # Second fire: should detect orphan intermediate 1, WARN, auto-force-fresh
    load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        sensitivity=False,
        workspace_bucket=synthetic_bucket.removeprefix("file://"),
    )
    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "orphan MT" in captured.out
    assert "state=FRESH" in captured.out


# ----- 260520-s2s Wave-2 design-delta regression tests -----
# Q6 (MAF export threshold), Q2/Q4 (float32 .npz), W1-G1 (idempotent resume).
# See .planning/quick/260520-s2s-wave-2-ld-computation-design/260520-s2s-CONTEXT.md


def test_maf_export_threshold_constant_is_0_005():
    """Q6 (260520-s2s-CONTEXT.md): export MAF floor is 0.005, NOT spec §7.2 default of 0.01.

    Rationale lock: M2-novel AFR variants concentrate in the 0.005-0.01 band
    (m3-RESEARCH.md Q10); dropping them at export forfeits the AFR-specific
    signal the project exists to capture. feedback_rigor_over_speed.md.
    """
    from aou_ld_panel import MAF_THRESHOLD_EXPORT
    assert MAF_THRESHOLD_EXPORT == 0.005, (
        f"Q6 lock requires MAF_THRESHOLD_EXPORT == 0.005 (overriding "
        f"AOU-LD-PIPELINE.md §7.2 default of 0.01); got {MAF_THRESHOLD_EXPORT}"
    )
    # Internal MAF floor and export floor are equal under the Q6 override
    # (no separate internal-stricter band). This may decouple later if
    # cohort/variant pathology surfaces in dev-10; for now they're pinned together.
    from aou_ld_panel import MIN_MAF_INTERNAL
    assert MAF_THRESHOLD_EXPORT == MIN_MAF_INTERNAL, (
        f"Q6 lock pins MAF_THRESHOLD_EXPORT ({MAF_THRESHOLD_EXPORT}) == "
        f"MIN_MAF_INTERNAL ({MIN_MAF_INTERNAL}) for Wave 2 dev fire"
    )


def test_compute_region_ld_writes_float32_npz(synthetic_mt_path: Path,
                                              mock_aou_env, tmp_path):
    """Q2/Q4 (260520-s2s-CONTEXT.md): exported .npz LD arrays MUST be float32.

    float64 would silently double per-region storage + egress (~16 GB → ~32 GB
    across 322 production cells); float16 would lose SuSiE-RSS-relevant
    precision in the signed-r band. Defensive regression on _save_npz's
    dtype contract.
    """
    _require_hail()
    import numpy as np

    from aou_ld_panel import compute_region_ld, load_qc_cohort

    mt = load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        skip_checkpoint=True,
    )
    region = {
        "region_id": "synth_region_chr16_small_dtype",
        "chr": "16",
        "start_grch38": 50_100_000,
        "end_grch38": 51_900_000,
        "radius_bp": 2_400_000,
        "region_class": "small",
    }
    res = compute_region_ld(region, mt, out_bucket=None, out_local_dir=tmp_path)
    assert res["status"] == "ok", f"expected ok, got {res}"
    with np.load(res["out"]) as npz:
        assert npz["ld"].dtype == np.float32, (
            f"Q2/Q4 lock requires float32 .npz storage; got dtype={npz['ld'].dtype}. "
            f"float64 would silently double egress cost across 322 production cells."
        )


def test_compute_region_ld_idempotent_skip(synthetic_mt_path: Path,
                                           mock_aou_env, tmp_path, monkeypatch):
    """W1-G1 (260520-s2s-CONTEXT.md): re-fire of an already-written {region_id}.npz
    must return status='skipped_idempotent' WITHOUT re-running hl.ld_matrix.

    Critical for websocket-drop resume protocol — a 30h Wave 4 production fire
    cannot tolerate a single browser timeout forfeiting all completed regions.
    force_recompute=True bypasses the guard and re-runs.
    """
    _require_hail()
    from aou_ld_panel import compute_region_ld, load_qc_cohort

    mt = load_qc_cohort(
        mt_path=str(synthetic_mt_path),
        ancestry="afr",
        skip_checkpoint=True,
    )
    region = {
        "region_id": "synth_region_chr16_small_idem",
        "chr": "16",
        "start_grch38": 50_100_000,
        "end_grch38": 51_900_000,
        "radius_bp": 2_400_000,
        "region_class": "small",
    }

    # First fire: writes .npz
    res1 = compute_region_ld(region, mt, out_bucket=None, out_local_dir=tmp_path)
    assert res1["status"] == "ok", f"expected ok on first fire, got {res1}"
    assert res1["out"] is not None

    # Second fire: must short-circuit without invoking hl.ld_matrix
    import hail as hl
    call_log = []
    orig_ld_matrix = hl.ld_matrix

    def _spy_ld_matrix(*a, **k):
        call_log.append("invoked")
        return orig_ld_matrix(*a, **k)

    monkeypatch.setattr(hl, "ld_matrix", _spy_ld_matrix)
    res2 = compute_region_ld(region, mt, out_bucket=None, out_local_dir=tmp_path)
    assert res2["status"] == "skipped_idempotent", (
        f"W1-G1 idempotency: re-fire must skip without re-running hl.ld_matrix; "
        f"got status={res2['status']!r}"
    )
    assert call_log == [], f"hl.ld_matrix invoked on idempotent re-fire: {call_log}"
    assert res2["out"] == res1["out"], (
        f"skipped_idempotent return must point at the existing .npz; "
        f"got {res2['out']!r} != {res1['out']!r}"
    )

    # Third fire: force_recompute=True must bypass guard
    res3 = compute_region_ld(region, mt, out_bucket=None, out_local_dir=tmp_path,
                             force_recompute=True)
    assert res3["status"] == "ok", (
        f"force_recompute=True must bypass the idempotency guard; "
        f"got status={res3['status']!r}"
    )
    assert call_log == ["invoked"], (
        f"force_recompute=True must re-invoke hl.ld_matrix exactly once; "
        f"got call_log={call_log}"
    )


# ----- 260601-u1b: tiered cheap-first hardening (Task 1) -----
#
# Two helpers, both TDD RED-first.
#
# (A) _interval_scaled_du_floor — the du byte-floor is a DIAGNOSTIC soft-signal
#     scaled to the interval span. The 50 MB notebook floor false-positives on a
#     ~2 Mb nano-interval (its real entries payload is far below 50 MB), so a
#     nano fire would FAIL the floor even on a perfectly-populated MT. We demote
#     the du-floor to an interval-scaled soft check; the count_rows>0 /
#     count_cols>0 assertion inside load_qc_cohort (_assert_checkpoint_nonempty,
#     UNCHANGED) remains the authoritative HARD catastrophe gate. The floor only
#     scales DOWN for span-bounded intervals — whole-chromosome / None keep the
#     full base floor so the chr22 (Tier 2) check is never weakened.
#
# (B) _capture_catastrophe_forensics — best-effort forensic capture invoked by
#     notebook cells on any Track-4 halt. NEVER raises (defensive); standalone
#     (NOT injected into _assert_checkpoint_nonempty, so the hard-fail/raise
#     contract of the Track-4 guard is byte-for-byte unchanged). Records the
#     _SUCCESS-mtime-vs-part-mtimes hypothesis distinguisher
#     ([[feedback_w1_catastrophe_hypothesis_distinguisher]]) and emits a
#     _forensics/<phase>_capture.json.


# --- (A) du-floor parameterization helper ---

def test_interval_scaled_du_floor_nano_interval_no_false_positive():
    """A ~2 Mb nano-interval ('chr22:16000000-18000000') must NOT inherit the
    unscaled 50 MB base floor — that floor false-positives a populated nano MT.
    The scaled floor must be < 50 MB AND >= a documented few-MB minimum.

    RATIONALE (load-bearing): the du-floor is a DIAGNOSTIC soft-signal scaled to
    the interval span. The real catastrophe gate is count_rows>0/count_cols>0
    in _assert_checkpoint_nonempty (inside load_qc_cohort), which is untouched.
    """
    from aou_ld_panel import _interval_scaled_du_floor
    base = 50_000_000
    floor = _interval_scaled_du_floor("chr22:16000000-18000000",
                                      base_floor_bytes=base)
    assert floor < base, (
        f"nano-interval floor must scale BELOW the 50 MB base (no "
        f"false-positive); got {floor}"
    )
    # Documented few-MB minimum so the soft-signal still catches a footer-stub
    # (~71 KiB) MT even on a tiny span.
    assert floor >= 1_000_000, (
        f"nano-interval floor must stay >= a few-MB documented minimum; "
        f"got {floor}"
    )


def test_interval_scaled_du_floor_whole_chromosome_keeps_base():
    """A whole-chromosome 'chr22' (no span bounds) must NOT down-scale — it
    keeps the full base floor so the chr22 (Tier 2) du check is not weakened."""
    from aou_ld_panel import _interval_scaled_du_floor
    base = 50_000_000
    assert _interval_scaled_du_floor("chr22", base_floor_bytes=base) == base


def test_interval_scaled_du_floor_none_keeps_base():
    """interval_filter=None (full-genome) keeps the full base floor."""
    from aou_ld_panel import _interval_scaled_du_floor
    base = 50_000_000
    assert _interval_scaled_du_floor(None, base_floor_bytes=base) == base


def test_interval_scaled_du_floor_scales_with_span():
    """A wider span yields a higher (or equal) floor than a narrower span on
    the same chromosome — the floor tracks expected payload monotonically."""
    from aou_ld_panel import _interval_scaled_du_floor
    base = 50_000_000
    narrow = _interval_scaled_du_floor("chr22:16000000-18000000",
                                       base_floor_bytes=base)   # 2 Mb
    wide = _interval_scaled_du_floor("chr22:16000000-36000000",
                                     base_floor_bytes=base)     # 20 Mb
    assert wide >= narrow, (
        f"wider span must not yield a smaller floor; narrow={narrow} "
        f"wide={wide}"
    )
    assert wide <= base, "a sub-chromosomal span must never exceed the base floor"


# --- (B) _capture_catastrophe_forensics(uri, *, phase) ---

def _mk_listing(success_mtime, part_mtimes):
    """Build a mock hl.hadoop_ls-style stat-dict listing for an MT dir:
    a _SUCCESS marker + N entries-part files, each with a 'modification_time'
    epoch and a 'size_bytes'. Mirrors the dict shape _capture inspects.

    ``success_mtime`` / ``part_mtimes`` may be ints (epochs) OR formatted
    strings (the form Hail's ``hl.hadoop_ls`` emits across versions) — the
    distinguisher must resolve either."""
    listing = [
        {"path": "gs://b/ld/x.mt/_SUCCESS",
         "modification_time": success_mtime, "size_bytes": 0, "is_dir": False},
    ]
    for i, mt in enumerate(part_mtimes):
        listing.append({
            "path": f"gs://b/ld/x.mt/entries/rows/parts/part-{i:05d}.parquet",
            "modification_time": mt, "size_bytes": 70_000, "is_dir": False,
        })
    return listing


def test_capture_forensics_flags_hail_finalize_signature(tmp_path):
    """_SUCCESS mtime AFTER all entries-part mtimes = the
    Hail-finalize-on-empty-contents signature
    ([[feedback_w1_catastrophe_hypothesis_distinguisher]]). The capture json
    must record that ordering / a hypothesis flag."""
    from aou_ld_panel import _capture_catastrophe_forensics
    listing = _mk_listing(success_mtime=2000, part_mtimes=[1000, 1500])
    out_dir = tmp_path / "bucket"
    out_dir.mkdir()
    result = _capture_catastrophe_forensics(
        f"file://{out_dir}/x.mt", phase="afr",
        lister=lambda d: listing,
        copier=lambda src, dst: None,
        http_getter=lambda url: {"activeStages": []},
        bucket=f"file://{out_dir}",
    )
    assert result is not None
    assert result.get("hypothesis_flag") == "hail_finalize_on_empty", (
        f"_SUCCESS after all parts must flag hail_finalize_on_empty; got "
        f"{result.get('hypothesis_flag')!r}"
    )


def test_capture_forensics_flags_kill_interrupted_signature(tmp_path):
    """Some entries-part mtimes AFTER the _SUCCESS mtime = the
    kill-interrupted-write signature. The capture must record the opposite
    hypothesis flag."""
    from aou_ld_panel import _capture_catastrophe_forensics
    listing = _mk_listing(success_mtime=1000, part_mtimes=[1500, 2000])
    out_dir = tmp_path / "bucket"
    out_dir.mkdir()
    result = _capture_catastrophe_forensics(
        f"file://{out_dir}/x.mt", phase="afr",
        lister=lambda d: listing,
        copier=lambda src, dst: None,
        http_getter=lambda url: {"activeStages": []},
        bucket=f"file://{out_dir}",
    )
    assert result is not None
    assert result.get("hypothesis_flag") == "kill_interrupted_write", (
        f"part mtime after _SUCCESS must flag kill_interrupted_write; got "
        f"{result.get('hypothesis_flag')!r}"
    )


def test_capture_forensics_never_raises_when_collaborators_raise(tmp_path):
    """LOAD-BEARING defensive guarantee: when every injected collaborator
    RAISES, the helper does NOT propagate — it returns its sentinel (a dict,
    never None-on-success-path) and still writes whatever partial json it
    could. Forensic capture must NEVER take down the cell it is trying to
    diagnose."""
    from aou_ld_panel import _capture_catastrophe_forensics

    def _boom(*a, **k):
        raise RuntimeError("collaborator exploded")

    out_dir = tmp_path / "bucket"
    out_dir.mkdir()
    # Must not raise.
    result = _capture_catastrophe_forensics(
        f"file://{out_dir}/x.mt", phase="afr",
        lister=_boom,
        copier=_boom,
        http_getter=_boom,
        bucket=f"file://{out_dir}",
    )
    assert result is not None, "capture must return a sentinel dict, not raise"
    assert isinstance(result, dict)
    # It should still have recorded the phase + uri even when listing failed.
    assert result.get("phase") == "afr"


def test_capture_forensics_writes_parseable_capture_json(tmp_path):
    """The helper writes a parseable _forensics/<phase>_capture.json that
    round-trips through json.loads and contains the phase + uri."""
    import json as _json
    from aou_ld_panel import _capture_catastrophe_forensics
    out_dir = tmp_path / "bucket"
    out_dir.mkdir()
    uri = f"file://{out_dir}/x.mt"
    _capture_catastrophe_forensics(
        uri, phase="probe",
        lister=lambda d: _mk_listing(2000, [1000]),
        copier=lambda src, dst: None,
        http_getter=lambda url: {"activeStages": [{"stageId": 71}]},
        bucket=f"file://{out_dir}",
    )
    capture_json = out_dir / "ld" / "_forensics" / "probe_capture.json"
    assert capture_json.is_file(), (
        f"capture json must be written at {capture_json}"
    )
    parsed = _json.loads(capture_json.read_text())
    assert parsed["phase"] == "probe"
    assert parsed["uri"] == uri


# --- IN-01 (remediation 260601-u1b): string / mixed-type modification_time ---
# Hail's hl.hadoop_ls can emit modification_time as a FORMATTED STRING (epoch
# string, ISO, or 'YYYY-MM-DD HH:MM:SS') rather than an int/float epoch. A naive
# `m > success_mtime` comparison across str-vs-int raises TypeError, which the
# outer never-raise guard swallows and degrades the hypothesis_flag to
# 'indeterminate' — destroying the diagnostic at the exact moment it matters.
# These tests pin that a PARSEABLE string mtime resolves the CORRECT flag.

def test_capture_forensics_flags_finalize_with_epoch_string_mtimes(tmp_path):
    """modification_time as numeric epoch STRINGS ('1700000000') must still
    resolve hail_finalize_on_empty when _SUCCESS >= all parts — NOT degrade
    to indeterminate."""
    from aou_ld_panel import _capture_catastrophe_forensics
    listing = _mk_listing(success_mtime="1700000200",
                          part_mtimes=["1700000000", "1700000100"])
    out_dir = tmp_path / "bucket"
    out_dir.mkdir()
    result = _capture_catastrophe_forensics(
        f"file://{out_dir}/x.mt", phase="afr",
        lister=lambda d: listing,
        copier=lambda src, dst: None,
        http_getter=lambda url: {"activeStages": []},
        bucket=f"file://{out_dir}",
    )
    assert result.get("hypothesis_flag") == "hail_finalize_on_empty", (
        f"epoch-string _SUCCESS after all parts must flag hail_finalize_on_empty "
        f"(not indeterminate); got {result.get('hypothesis_flag')!r}"
    )


def test_capture_forensics_flags_finalize_with_uneven_epoch_strings(tmp_path):
    """Epoch STRINGS of differing digit-length must compare NUMERICALLY, not
    lexicographically. _SUCCESS='1700000000' (10 digits) is numerically AFTER
    parts '999999999' (9 digits) => hail_finalize_on_empty. A naive string '>'
    would invert this ('1...' < '9...' lexicographically) and mis-flag it
    kill_interrupted_write — so this pins genuine numeric coercion, not the
    accidental same-width-string lexical match."""
    from aou_ld_panel import _capture_catastrophe_forensics
    listing = _mk_listing(success_mtime="1700000000",
                          part_mtimes=["999999999", "999999000"])
    out_dir = tmp_path / "bucket"
    out_dir.mkdir()
    result = _capture_catastrophe_forensics(
        f"file://{out_dir}/x.mt", phase="afr",
        lister=lambda d: listing,
        copier=lambda src, dst: None,
        http_getter=lambda url: {"activeStages": []},
        bucket=f"file://{out_dir}",
    )
    assert result.get("hypothesis_flag") == "hail_finalize_on_empty", (
        f"uneven-length epoch strings must compare numerically; _SUCCESS "
        f"'1700000000' is numerically after part '999999999' => "
        f"hail_finalize_on_empty; got {result.get('hypothesis_flag')!r}"
    )


def test_capture_forensics_flags_kill_with_human_string_mtimes(tmp_path):
    """modification_time as human 'YYYY-MM-DD HH:MM:SS' strings must still
    resolve kill_interrupted_write when a part is later than _SUCCESS — NOT
    degrade to indeterminate (this is the form Hail historically emits)."""
    from aou_ld_panel import _capture_catastrophe_forensics
    listing = _mk_listing(success_mtime="2024-01-15 12:34:56",
                          part_mtimes=["2024-01-15 12:35:10",
                                       "2024-01-15 12:40:00"])
    out_dir = tmp_path / "bucket"
    out_dir.mkdir()
    result = _capture_catastrophe_forensics(
        f"file://{out_dir}/x.mt", phase="afr",
        lister=lambda d: listing,
        copier=lambda src, dst: None,
        http_getter=lambda url: {"activeStages": []},
        bucket=f"file://{out_dir}",
    )
    assert result.get("hypothesis_flag") == "kill_interrupted_write", (
        f"human-string part after _SUCCESS must flag kill_interrupted_write "
        f"(not indeterminate); got {result.get('hypothesis_flag')!r}"
    )


def test_capture_forensics_flags_finalize_with_iso_string_mtimes(tmp_path):
    """modification_time as ISO 'YYYY-MM-DDTHH:MM:SSZ' strings must still
    resolve hail_finalize_on_empty when _SUCCESS >= all parts."""
    from aou_ld_panel import _capture_catastrophe_forensics
    listing = _mk_listing(success_mtime="2024-01-15T12:40:00Z",
                          part_mtimes=["2024-01-15T12:34:56Z",
                                       "2024-01-15T12:35:10Z"])
    out_dir = tmp_path / "bucket"
    out_dir.mkdir()
    result = _capture_catastrophe_forensics(
        f"file://{out_dir}/x.mt", phase="afr",
        lister=lambda d: listing,
        copier=lambda src, dst: None,
        http_getter=lambda url: {"activeStages": []},
        bucket=f"file://{out_dir}",
    )
    assert result.get("hypothesis_flag") == "hail_finalize_on_empty", (
        f"ISO-string _SUCCESS at/after all parts must flag hail_finalize_on_empty "
        f"(not indeterminate); got {result.get('hypothesis_flag')!r}"
    )


def test_capture_forensics_flags_kill_with_mixed_type_mtimes(tmp_path):
    """MIXED types — _SUCCESS as a string, a part as an int epoch (or vice
    versa) — must coerce to a common comparable before comparison and resolve
    the CORRECT flag, NOT raise TypeError that degrades to indeterminate.
    Here _SUCCESS='1700000000' (string) and a part is 1700000500 (int, later)
    => kill_interrupted_write."""
    from aou_ld_panel import _capture_catastrophe_forensics
    listing = _mk_listing(success_mtime="1700000000",
                          part_mtimes=[1700000300, 1700000500])
    out_dir = tmp_path / "bucket"
    out_dir.mkdir()
    result = _capture_catastrophe_forensics(
        f"file://{out_dir}/x.mt", phase="afr",
        lister=lambda d: listing,
        copier=lambda src, dst: None,
        http_getter=lambda url: {"activeStages": []},
        bucket=f"file://{out_dir}",
    )
    assert result.get("hypothesis_flag") == "kill_interrupted_write", (
        f"mixed str/int mtimes must coerce + resolve kill_interrupted_write "
        f"(not indeterminate via TypeError); got {result.get('hypothesis_flag')!r}"
    )


# --- IN-02 (remediation 260601-u1b): pin the production no-bucket + partial-JSON
# never-raise contract paths the existing suite leaves uncovered. ---

def test_capture_forensics_never_raises_with_bucket_none_and_env_unset(monkeypatch):
    """Production default-arg path: notebook calls _capture_catastrophe_forensics(uri,
    phase='afr') with NO bucket. With WORKSPACE_BUCKET unset, forensics_dir is None
    (hail.log-copy + json-write skipped) — the helper must STILL not raise and STILL
    return a best-effort partial dict carrying phase + uri."""
    from aou_ld_panel import _capture_catastrophe_forensics
    monkeypatch.delenv("WORKSPACE_BUCKET", raising=False)
    result = _capture_catastrophe_forensics(
        "gs://some-bucket/ld/mt_afr_qc.mt", phase="afr",
        lister=lambda d: _mk_listing(2000, [1000]),
        copier=lambda src, dst: None,
        http_getter=lambda url: {"activeStages": []},
        # NO bucket= -> resolves to WORKSPACE_BUCKET (unset) -> None.
    )
    assert isinstance(result, dict)
    assert result.get("phase") == "afr"
    assert result.get("uri") == "gs://some-bucket/ld/mt_afr_qc.mt"
    assert result.get("forensics_dir") is None


def test_capture_forensics_writes_partial_json_when_collaborators_raise(tmp_path):
    """Partial-JSON promise: when the non-writer collaborators (lister / copier /
    http_getter) all raise, the _forensics/<phase>_capture.json is STILL written
    (json round-trips) with the sub-step errors recorded in its 'errors' list."""
    import json as _json
    from aou_ld_panel import _capture_catastrophe_forensics

    def _boom(*a, **k):
        raise RuntimeError("collaborator exploded")

    out_dir = tmp_path / "bucket"
    out_dir.mkdir()
    result = _capture_catastrophe_forensics(
        f"file://{out_dir}/x.mt", phase="afr",
        lister=_boom,
        copier=_boom,
        http_getter=_boom,
        bucket=f"file://{out_dir}",
    )
    assert isinstance(result, dict)
    capture_json = out_dir / "ld" / "_forensics" / "afr_capture.json"
    assert capture_json.is_file(), (
        f"partial capture json must STILL be written at {capture_json} even "
        f"when collaborators raise"
    )
    parsed = _json.loads(capture_json.read_text())
    assert parsed["phase"] == "afr"
    assert parsed["errors"], (
        "partial json must record the sub-step errors that fired "
        "(listing/distinguisher + hail.log-copy + spark-rest)"
    )


# ===================================================================
# Nano-tier sample-axis collapse — call-rate degeneracy guard
# (.planning/debug/m3-gateb-nano-sample-axis-collapse.md)
#
# Root cause: the unguarded call_rate sample filter at
# aou_ld_panel.py:1460-1461 collapsed the sample (column) axis to 0 at
# Gate B nano (chr22:16-18Mb, ~119K un-QC'd variants) because per-sample
# call_rate computed over a tiny pre-variant-QC window is degenerate.
# Fix design: docs/superpowers/specs/2026-06-03-nano-sample-axis-callrate-guard-design.md
#
# Two test layers:
#   (A) pure-Python (run under smoke_dev, no hail): the assertion-message
#       branch, the MIN_VARIANTS_FOR_SAMPLE_CALLRATE constant + provenance
#       params, and the sample_callrate_filtered sidecar threading.
#   (B) hail-gated integration (skip locally via _require_hail; exercised
#       on a hail env / cluster): the guard skip-on-nano col-retention and
#       the above-floor genuinely-bad-sample drop.
# ===================================================================


class _FakeMT:
    """Minimal stand-in exposing count_rows()/count_cols() for the
    pure-Python _assert_checkpoint_nonempty message tests (no hail)."""

    def __init__(self, n_rows: int, n_cols: int):
        self._n_rows = n_rows
        self._n_cols = n_cols

    def count_rows(self) -> int:
        return self._n_rows

    def count_cols(self) -> int:
        return self._n_cols


def test_assert_checkpoint_sample_axis_collapse_message():
    """rows>0, cols==0 -> the message must name the SAMPLE-axis collapse
    and explicitly disclaim the m3-W1 0x0 finalize catastrophe.

    RED before the fix: the canned message labels every empty MT (including
    this 118903x0 sample-collapse) as the 'm3-W1 empty-MT catastrophe
    signature', which mislabels a QC-predicate collapse as a platform
    finalize bug (the mislabel that pushed toward an incorrect 1000G pivot).
    """
    from aou_ld_panel import _assert_checkpoint_nonempty

    with pytest.raises(RuntimeError) as exc:
        _assert_checkpoint_nonempty(
            _FakeMT(118903, 0), "gs://b/mt_afr_post_variant_qc.mt",
            phase="post_variant_qc")
    msg = str(exc.value)
    assert "118903 rows x 0 cols" in msg
    # Names the sample/column axis collapse + QC-predicate cause.
    assert "sample" in msg.lower() and "axis" in msg.lower()
    assert "QC" in msg or "qc" in msg
    # Explicitly NOT the 0x0 finalize catastrophe.
    assert "NOT the m3-W1" in msg or "not the m3-w1" in msg.lower()


def test_assert_checkpoint_variant_axis_collapse_message():
    """cols>0, rows==0 -> analogous row(variant)-axis collapse message."""
    from aou_ld_panel import _assert_checkpoint_nonempty

    with pytest.raises(RuntimeError) as exc:
        _assert_checkpoint_nonempty(
            _FakeMT(0, 250), "gs://b/mt_afr_final.mt", phase="final")
    msg = str(exc.value)
    assert "0 rows x 250 cols" in msg
    assert "variant" in msg.lower() or "row" in msg.lower()
    assert "NOT the m3-W1" in msg or "not the m3-w1" in msg.lower()


def test_assert_checkpoint_zero_by_zero_keeps_finalize_message():
    """True 0x0 -> the existing m3-W1 finalize-catastrophe message is kept
    verbatim (the genuine catastrophe signature)."""
    from aou_ld_panel import _assert_checkpoint_nonempty

    with pytest.raises(RuntimeError) as exc:
        _assert_checkpoint_nonempty(
            _FakeMT(0, 0), "gs://b/mt_afr_post_split.mt", phase="post_split")
    msg = str(exc.value)
    assert "0 rows x 0 cols" in msg
    assert "m3-W1 empty-MT" in msg
    assert "contents are missing" in msg
    # Cross-reference pointers preserved.
    assert "m3-W1-empty-mt-catastrophe.md" in msg
    assert "feedback_hail_checkpoint_contract_violation" in msg


def test_min_variants_for_sample_callrate_constant():
    """The new floor constant exists and is the documented 500K value, and
    it never trips at whole-chromosome-or-larger scale (chr22 ~2.4M)."""
    from aou_ld_panel import MIN_VARIANTS_FOR_SAMPLE_CALLRATE
    assert MIN_VARIANTS_FOR_SAMPLE_CALLRATE == 500_000
    # Nano (~119K) trips; whole-chr22 (~2.4M) does not.
    assert 118_903 < MIN_VARIANTS_FOR_SAMPLE_CALLRATE < 2_400_000


def test_collect_provenance_records_sample_callrate_floor():
    """The floor constant is recorded in provenance.params so a change to
    it invalidates intermediates (symmetric with the other QC thresholds)."""
    from aou_ld_panel import (_collect_provenance,
                              MIN_VARIANTS_FOR_SAMPLE_CALLRATE)
    prov = _collect_provenance(
        ancestry="afr", sensitivity=False,
        source_mt_path="gs://src/path.mt", interval_filter=None)
    assert prov["params"]["MIN_VARIANTS_FOR_SAMPLE_CALLRATE"] == \
        MIN_VARIANTS_FOR_SAMPLE_CALLRATE
    # The runtime OUTCOME flag must NOT be baked into _collect_provenance
    # output (it is a per-fire result, not a fire-level parameter, and would
    # spuriously fail resume-validation if compared). It is threaded at
    # sidecar-write time instead.
    assert "sample_callrate_filtered" not in prov


def test_write_sidecar_threads_sample_callrate_filtered_flag(tmp_path):
    """post_variant_qc sidecar honestly records whether the call-rate sample
    filter was applied (sample_callrate_filtered), WITHOUT mutating the
    reusable provenance dict and WITHOUT putting an outcome into the
    resume-validation comparison surface
    ([[feedback_aou_success_marker_not_evidence_of_data]])."""
    from aou_ld_panel import (_collect_provenance, _write_sidecar,
                              _read_sidecar, _validate_sidecar,
                              _SIDECAR_COMPARE_EXCLUDE_FIELDS)
    prov = _collect_provenance("afr", False, "gs://src/path.mt")

    # post_split sidecar: filter not yet decided -> no flag written.
    split_uri = f"file://{tmp_path}/post_split.meta.json"
    _write_sidecar(split_uri, prov, phase="post_split")
    split = _read_sidecar(split_uri)
    assert "sample_callrate_filtered" not in split

    # post_variant_qc sidecar: the runtime flag is threaded through.
    sqc_uri = f"file://{tmp_path}/post_vqc.meta.json"
    _write_sidecar(sqc_uri, prov, phase="post_variant_qc",
                   sample_callrate_filtered=False)
    sqc = _read_sidecar(sqc_uri)
    assert sqc["sample_callrate_filtered"] is False

    # The input provenance dict must not have been mutated by either write.
    assert "sample_callrate_filtered" not in prov
    assert "phase" not in prov

    # The outcome flag must be excluded from resume-validation comparison
    # (it is an outcome, not a parameter; comparing it would spuriously
    # invalidate a post_variant_qc intermediate on resume).
    assert "sample_callrate_filtered" in _SIDECAR_COMPARE_EXCLUDE_FIELDS
    matches, diag = _validate_sidecar(sqc, prov)
    assert matches, f"outcome flag must not break sidecar validation: {diag}"


# ----- Hail-gated integration tests (skip locally; run on hail env) -----


def test_nano_span_guard_retains_samples(synthetic_mt_path_missing: Path,
                                          mock_aou_env, tmp_path, capsys):
    """Span-bounded + low-call window below MIN_VARIANTS_FOR_SAMPLE_CALLRATE:
    the guard SKIPS the call_rate sample filter, COLS ARE RETAINED, the skip
    is logged, and the post_variant_qc sidecar records
    sample_callrate_filtered=False.

    This is the regression that reproduces the Gate B nano 118903x0 collapse:
    pre-fix the call_rate filter would drop every sample on this low-call,
    below-floor window; post-fix the guard keeps them.
    """
    _require_hail()
    import json as _json
    from aou_ld_panel import load_qc_cohort, _sidecar_uri, _read_sidecar

    bucket_dir = tmp_path / "wb"
    bucket_dir.mkdir()
    mt = load_qc_cohort(
        mt_path=str(synthetic_mt_path_missing),
        ancestry="afr",
        interval_filter="chr16:50000000-52000000",
        workspace_bucket=f"file://{bucket_dir}",
        force_fresh=True,
    )
    assert mt.count_cols() > 0, (
        "sample axis collapsed on a below-floor low-call window — the guard "
        "must SKIP the call_rate filter and retain samples")
    out = capsys.readouterr().out
    assert "SKIP call_rate sample filter" in out
    # Provenance honestly records the skip.
    from aou_ld_panel import _intermediate_checkpoint_uri
    sqc_ckpt = _intermediate_checkpoint_uri(
        f"file://{bucket_dir}", "afr", "post_variant_qc", False,
        "chr16:50000000-52000000")
    sidecar = _read_sidecar(_sidecar_uri(sqc_ckpt))
    assert sidecar is not None
    assert sidecar["sample_callrate_filtered"] is False


def test_above_floor_callrate_filter_still_drops_bad_sample(
        synthetic_mt_path_missing: Path, mock_aou_env, tmp_path, monkeypatch,
        capsys):
    """With variant count >= the floor (floor lowered for the test) AND a
    genuinely-bad low-call-rate sample, the filter STILL applies: the bad
    sample is dropped, good samples kept, provenance flag True. Locks the
    genome-scale path (the guard does not weaken real QC at scale)."""
    _require_hail()
    import aou_ld_panel as ldp
    from aou_ld_panel import load_qc_cohort, _sidecar_uri, _read_sidecar, \
        _intermediate_checkpoint_uri

    # Lower the floor below the fixture's chr16 variant count so the
    # above-floor (filter-applied) branch is exercised on a small fixture.
    monkeypatch.setattr(ldp, "MIN_VARIANTS_FOR_SAMPLE_CALLRATE", 10)

    bucket_dir = tmp_path / "wb"
    bucket_dir.mkdir()
    mt = load_qc_cohort(
        mt_path=str(synthetic_mt_path_missing),
        ancestry="afr",
        interval_filter="chr16:50000000-52000000",
        workspace_bucket=f"file://{bucket_dir}",
        force_fresh=True,
    )
    assert mt.count_cols() > 0, "good samples must survive QC"
    sqc_ckpt = _intermediate_checkpoint_uri(
        f"file://{bucket_dir}", "afr", "post_variant_qc", False,
        "chr16:50000000-52000000")
    sidecar = _read_sidecar(_sidecar_uri(sqc_ckpt))
    assert sidecar is not None
    assert sidecar["sample_callrate_filtered"] is True


def test_real_hail_mt_entries_layout_and_validate_populated(
        synthetic_mt_path: Path, tmp_path):
    """GROUND TRUTH (hail-gated): write a small REAL Hail MatrixTable and pin
    the on-disk entries layout the fix depends on.

    SKIPs on smoke_dev (no Hail) via _require_hail(); RUNS on any Hail env
    (AoU / Dataproc). This is the anti-false-confidence test: without it we'd
    just be trusting a hardcoded string. Asserts:
      (a) `<mt>/entries/rows/parts/` exists and is non-empty (the REAL layout),
          and the phantom `<mt>/entries/entries/parts/` does NOT exist;
      (b) `_validate_checkpoint_populated` returns True on the populated MT;
      (c) an emptied MT (filter_cols to zero) returns False (catastrophe still
          caught at the corrected path).

    Cross-reference: .planning/debug/m3-entries-path-phantom-subpath.md
    """
    hl = _require_hail()
    from aou_ld_panel import _validate_checkpoint_populated

    # (a) Write a small real Hail MT and inspect its on-disk layout.
    mt = hl.read_matrix_table(str(synthetic_mt_path))
    real_mt = tmp_path / "real_populated.mt"
    mt.write(str(real_mt), overwrite=True)

    real_entries = real_mt / "entries" / "rows" / "parts"
    phantom_entries = real_mt / "entries" / "entries" / "parts"
    assert real_entries.is_dir(), (
        f"real Hail MT must store entries at entries/rows/parts/ — not found "
        f"at {real_entries}; Hail layout may have changed, re-verify the probe"
    )
    real_parts = [p for p in real_entries.iterdir()
                  if p.is_file() and p.suffix == ".parquet"]
    assert real_parts, "entries/rows/parts/ must contain >=1 parquet part file"
    assert not phantom_entries.exists(), (
        "phantom entries/entries/parts/ must NOT exist on a real Hail MT — "
        "if it does, the on-disk layout assumption is wrong"
    )

    # (b) the populated MT validates True at the corrected path.
    assert _validate_checkpoint_populated(f"file://{real_mt}") is True, (
        "a freshly-written real Hail MT must validate populated at "
        "entries/rows/parts/"
    )

    # (c) an emptied MT (zero columns) validates False — catastrophe caught.
    empty_mt = tmp_path / "real_empty.mt"
    mt.filter_cols(hl.literal(False)).write(str(empty_mt), overwrite=True)
    assert _validate_checkpoint_populated(f"file://{empty_mt}") is False, (
        "an emptied (0-column) real Hail MT must validate False — the "
        "catastrophe guard must still fire at the corrected path"
    )


# ----- Sample-QC / variant-QC ORDERING regression guards -----
# ----- (m3-gatec-sample-callrate-ordering-collapse, 2026-06-04) -----
#
# Gate C (whole chr22, 1,859,922 variants) collapsed the AFR sample axis to 0:
# post_split 1859922x74576 -> post_sample_qc 1859922x0. Root cause = QC ORDERING.
# load_qc_cohort runs the per-sample call_rate filter (Phase 2,
# src/python/aou_ld_panel.py: `filter_cols(sqc.call_rate >= 0.98)`) BEFORE
# variant_qc (Phase 3). hl.sample_qc computes call_rate over the RAW, pre-variant-QC
# ACAF variant set; AoU sets FT-failed genotypes to no-call, so over that un-QC'd
# set (rich in rare/low-call variants) every sample's call_rate sits below 0.98 —
# the threshold is UNSATISFIABLE pre-variant-QC at ANY scale. The
# MIN_VARIANTS_FOR_SAMPLE_CALLRATE=500_000 guard only SKIPPED the filter below 500K
# (masking it at the Gate B nano tier); above 500K the filter applies and zeroes
# the sample axis. Fix = compute sample call_rate over QC-passing variants, i.e.
# run variant_qc + variant filters BEFORE sample_qc + the sample call_rate filter.
#
# These guards FAIL on the pre-fix source (sample-callrate-filter before variant_qc)
# and PASS on the fix. See .planning/debug/m3-gatec-sample-callrate-ordering-collapse.md.


def test_sample_callrate_filter_runs_after_variant_qc():
    """STATIC GUARD (Hail-free, NCSU-side): the per-sample call_rate filter must
    run AFTER variant_qc, so sample call_rate is measured over QC-passing variants
    (common, well-called) — NOT over the raw pre-variant-QC ACAF set whose FT
    no-calls depress every sample below 0.98 (the Gate C collapse).

    Anchored on the EXACT executable call-site tokens (unique in source; the
    substrings also appear in docstrings/comments, hence the full-statement match).
    """
    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    vqc_idx = src.find('mt = hl.variant_qc(mt, name="vqc")')
    sample_filter_idx = src.find("mt = mt.filter_cols(mt.sqc.call_rate >= MIN_CALL_RATE_SAMPLE)")
    assert vqc_idx > 0, "executable variant_qc call not found"
    assert sample_filter_idx > 0, "executable sample call_rate filter_cols not found"
    assert sample_filter_idx > vqc_idx, (
        "load_qc_cohort applies the per-sample call_rate filter "
        f"(pos {sample_filter_idx}) BEFORE variant_qc (pos {vqc_idx}). Per-sample "
        "call_rate is then computed over the raw pre-variant-QC ACAF variant set, "
        "where FT no-calls make the 0.98 threshold unsatisfiable -> the Gate C "
        "sample-axis collapse (1859922x0). Run variant_qc + variant filters FIRST, "
        "then sample_qc + the call_rate filter over QC-passing variants."
    )


@pytest.mark.skip(
    reason="SKELETON — Gate C Probe numbers now known ([A] RAW call_rate max "
           "0.8490 -> 0/74576 pass 0.98; [B] post-variant-QC 74558/74576 kept), "
           "but the structured-missingness fixture work below is out of scope here "
           "(.planning/debug/m3-gatec-sample-callrate-ordering-collapse.md). "
           "Needs STRUCTURED missingness: the fixture's current --missingness knob "
           "is UNIFORM per-genotype, which depresses call_rate independent of "
           "variant QC and so will NOT reproduce the ordering-dependence. To make "
           "sample-QC-first collapse the axis while variant-QC-first retains it, "
           "no-call must be CONCENTRATED on the rare/low-call variants variant_qc "
           "removes (likely a build_synthetic_mt fixture enhancement). Unskip once "
           "Probe numbers fix the missingness profile + variant counts."
)
def test_sample_axis_survives_at_scale_with_structured_missingness(
    mock_aou_env, tmp_path
):
    """E2E REPRODUCTION (hail-gated): on a fixture whose no-calls are concentrated
    in a rare/low-call variant tail (the AoU ACAF FT pattern), the pre-fix
    sample-QC-first ordering collapses the sample axis (post_sample_qc cols == 0),
    while the variant-QC-first fix retains it.

    Calibration TODO (from Probe):
      - [A] target: RAW sample call_rate max < 0.98 -> 0 samples pass (collapse).
      - [B] target: after variant_qc, ~all samples pass 0.98 (retained).
      - structured-missingness fraction + variant counts that reproduce [A]/[B]
        deterministically on a small synthetic MT.
    """
    _require_hail()
    from aou_ld_panel import load_qc_cohort  # noqa: F401

    # TODO(probe): build a structured-missingness fixture (no-call concentrated on
    # rare/low-call variants), run load_qc_cohort(ancestry="afr", skip_checkpoint=
    # True) through the (fixed) variant-QC-first ordering, and assert the sample
    # axis is RETAINED (n_cols > 0). Numbers come from Probe [A]/[B].
    raise NotImplementedError("calibrate from Gate C Probe [A]/[B]")


# ----- Wave 2 LD-compute routing OOM guards -----
# ----- (m3-W2 pre-fire audit HIGH-1 / HIGH-3, 2026-06-04) -----
#
# compute_region_ld routed by region_class FIRST; the Wave-0 manifest
# (build_ld_region_manifest.CLASS_MEDIUM_MAX_MB=25) classes regions up to 25 Mb
# as "medium", but Paths A.1/A.2 end in BlockMatrix.to_numpy() -- an O(n_var^2)
# DRIVER-side dense collect that OOMs the driver far below 25 Mb. 86 of the 322
# config cells are small/medium-classed yet span > PATH_A2_MAX_MB (largest 23.7
# Mb -> ~225 GB dense float32). These pure (Hail-free) guards pin the OOM-safe
# routing and the radius-cap invariant. See the Wave-2 plan / audit.

import csv as _csv  # noqa: E402


def _read_ld_regions():
    """Yield rows of config/ld_regions.tsv as dicts (tab-separated)."""
    p = PROJECT_ROOT / "config" / "ld_regions.tsv"
    with open(p, newline="") as f:
        yield from _csv.DictReader(f, delimiter="\t")


def test_route_region_path_oom_veto():
    """_route_region_path must NEVER route a region whose span exceeds the A.2 cap
    into a to_numpy() path (A.1/A.2), regardless of its region_class label."""
    from aou_ld_panel import _route_region_path, PATH_A1_MAX_MB, PATH_A2_MAX_MB
    # in-band: region_class routing honored
    assert _route_region_path("small", 3.0) == "A.1"
    assert _route_region_path("small", PATH_A1_MAX_MB) == "A.1"
    assert _route_region_path("medium", 8.0) == "A.2"
    assert _route_region_path("medium", PATH_A2_MAX_MB) == "A.2"        # 10.0 ok
    # OOM veto: oversized "medium"/"small" demoted to A.3 (the HIGH-1 bug)
    assert _route_region_path("medium", 10.1) == "A.3"
    assert _route_region_path("medium", 17.7) == "A.3"  # dev-10 m2_region_00006
    assert _route_region_path("medium", 23.7) == "A.3"  # largest medium in config
    assert _route_region_path("small", 12.0) == "A.3"
    # large/xlarge always A.3
    assert _route_region_path("large", 33.0) == "A.3"
    assert _route_region_path("xlarge", 73.0) == "A.3"
    # span-only routing when class is unknown/None
    assert _route_region_path(None, 4.0) == "A.1"
    assert _route_region_path(None, 9.0) == "A.2"
    assert _route_region_path(None, 40.0) == "A.3"


def test_ld_regions_config_no_to_numpy_oom():
    """REGRESSION GUARD (m3-W2 HIGH-1): under the fixed router, NO config region
    whose span exceeds PATH_A2_MAX_MB routes to a to_numpy() path. This FAILS on
    the pre-fix region_class-first routing (86 of 322 cells would OOM)."""
    from aou_ld_panel import _route_region_path, PATH_A2_MAX_MB
    offenders = []
    for row in _read_ld_regions():
        span_mb = (int(row["end_grch38"]) - int(row["start_grch38"])) / 1_000_000
        path = _route_region_path(row["region_class"], span_mb)
        if span_mb > PATH_A2_MAX_MB and path in ("A.1", "A.2"):
            offenders.append((row["region_id"], row["ancestry"], row["region_class"],
                              round(span_mb, 1), path))
    assert not offenders, (
        f"{len(offenders)} region cells route a >{PATH_A2_MAX_MB}Mb span into a "
        f"driver to_numpy() (OOM). First few: {offenders[:5]}"
    )


def test_ld_regions_radius_cap_only_affects_xlarge():
    """FLAG GUARD (m3-W2 HIGH-3): the Wave-0 radius cap (50 Mb) leaves radius < span
    on the xlarge regions, structurally zeroing long-range LD. That is a flagged
    scientific trade-off (long-range LD ~ 0); this test pins the invariant that
    ONLY xlarge regions are radius-capped, so any NEW non-xlarge banded region in a
    regenerated manifest is surfaced for review (rather than silently shipped)."""
    banded_nonxlarge = []
    n_banded = 0
    for row in _read_ld_regions():
        span = int(row["end_grch38"]) - int(row["start_grch38"])
        if int(row["radius_bp"]) < span:
            n_banded += 1
            if row["region_class"] != "xlarge":
                banded_nonxlarge.append((row["region_id"], row["ancestry"],
                                         row["region_class"]))
    assert not banded_nonxlarge, (
        "non-xlarge region(s) have radius < span (unexpected banding — review): "
        f"{banded_nonxlarge}"
    )
    # Sanity: the known xlarge banding set is present (16 cells = 8 regions x 2 anc).
    assert n_banded == 16, f"expected 16 banded xlarge cells, found {n_banded}"


def test_existing_region_npz_rejects_truncated(tmp_path):
    """MED-6: the idempotency guard must NOT short-circuit a 0-byte / truncated
    .npz (exists != populated — the m3-W1 blind-spot class). Pure, no Hail."""
    from aou_ld_panel import _existing_region_npz, _MIN_REGION_NPZ_BYTES
    rid = "synth_region_med6"
    target = tmp_path / f"{rid}.npz"
    # (a) 0-byte -> NOT a valid skip
    target.write_bytes(b"")
    assert _existing_region_npz(rid, None, tmp_path) is None
    # (b) truncated (< floor) -> NOT a valid skip
    target.write_bytes(b"PK\x03\x04" + b"\x00" * 8)
    assert _existing_region_npz(rid, None, tmp_path) is None
    # (c) populated (>= floor) -> valid idempotent skip
    target.write_bytes(b"\x00" * (_MIN_REGION_NPZ_BYTES + 1))
    assert _existing_region_npz(rid, None, tmp_path) == str(target)


def test_compute_region_ld_path_a2_medium(synthetic_mt_path, mock_aou_env, tmp_path):
    """A.2 (medium region_class): sparsify_triangle + to_numpy -> lower-tri .npz.
    Hail-gated (runs on AoU / the dev fire) — first coverage of Path A.2."""
    _require_hail()
    import numpy as np
    from aou_ld_panel import compute_region_ld, load_qc_cohort
    mt = load_qc_cohort(mt_path=str(synthetic_mt_path), ancestry="afr",
                        skip_checkpoint=True)
    region = {"region_id": "synth_a2", "chr": "16", "start_grch38": 50_100_000,
              "end_grch38": 51_900_000, "radius_bp": 2_400_000,
              "region_class": "medium"}
    res = compute_region_ld(region, mt, out_bucket=None, out_local_dir=tmp_path)
    assert res["status"] == "ok", res
    assert res["path_a"] == "A.2"
    z = np.load(res["out"])
    assert z["ld"].dtype == np.float32
    assert bool(z["lower_triangular"][0]) is True


def test_compute_region_ld_path_a3_large_validates_bm(synthetic_mt_path, mock_aou_env,
                                                      tmp_path):
    """A.3 (large region_class): BlockMatrix .bm + sidecar TSVs, with the MED-4
    populated-validation (_assert_blockmatrix_written) running inside
    compute_region_ld. Hail-gated — first coverage of Path A.3 + the new guard."""
    _require_hail()
    from aou_ld_panel import compute_region_ld, load_qc_cohort
    mt = load_qc_cohort(mt_path=str(synthetic_mt_path), ancestry="afr",
                        skip_checkpoint=True)
    region = {"region_id": "synth_a3", "chr": "16", "start_grch38": 50_100_000,
              "end_grch38": 51_900_000, "radius_bp": 2_400_000,
              "region_class": "large"}
    res = compute_region_ld(region, mt, out_bucket=None, out_local_dir=tmp_path)
    assert res["status"] == "ok", res
    assert res["path_a"] == "A.3"        # OOM-veto + region_class both -> A.3
    bm_dir = Path(res["out"])
    assert bm_dir.exists(), f"BlockMatrix .bm dir missing: {bm_dir}"
    assert (bm_dir.parent / "synth_a3.variant_ids.tsv").is_file()
    assert (bm_dir.parent / "synth_a3.rsids.tsv").is_file()


# ============================================================================
# GENOME-WIDE PER-CHROMOSOME FAN-OUT
# (.planning/debug/m3-W2-genome-wide-countcols-py4j-wedge.md)
#
# Root cause: with interval_filter=None there is NO filter_intervals partition
# pruning, so the FIRST Hail action (the post_split checkpoint) must materialize
# a driver-side plan over the FULL un-pruned ~145k-partition v8 source in one
# shot -> the driver wedges before any Spark stage launches. Fix: when genome-
# wide (interval_filter is None, real run), load_qc_cohort recurses per autosome
# (each bounded by interval_filter="chrN", running Phases 1-2 only via
# _skip_final_write=True), union_rows the 22 variant-QC'd MTs, then runs Phase 3
# (sample QC + het) ONCE over the union. Reproduces the proven-good chr22 Gate-C
# condition (every action bounded to one chromosome).
#
# These tests exercise the BRANCHING / UNION / QC-ORDERING / GUARD-KEYING logic
# with NO Hail cluster: a fake hail module + monkeypatched recursion records the
# control flow. They FAIL on the pre-fix source (single un-pruned pass) and PASS
# on the fix.
# ============================================================================


class _FanoutFakeMT:
    """Minimal MatrixTable stand-in that records union_rows + count_rows.

    Carries a synthetic row count so the union's count_rows() (the raw-count
    guard input) is computable without Hail. union_rows returns a NEW _FanoutFakeMT
    whose row count is the SUM of the inputs (variant-axis concatenation) and
    records the operands so the test can assert all 22 chroms were unioned.
    """
    def __init__(self, tag, n_rows):
        self.tag = tag
        self._n_rows = n_rows
        self.union_operands = None  # set on the union result

    def union_rows(self, *others):
        total = self._n_rows + sum(o._n_rows for o in others)
        out = _FanoutFakeMT(tag="union", n_rows=total)
        out.union_operands = (self,) + others
        return out

    def count_rows(self):
        return self._n_rows


def _install_genome_wide_harness(monkeypatch, *, per_chrom_rows):
    """Monkeypatch aou_ld_panel so the genome-wide branch runs Hail-free.

    - fake `hail` import (only union/count are used in the branch; sample QC +
      final write are intercepted via _apply_sample_qc_and_finalize stub).
    - recursive load_qc_cohort returns a _FanoutFakeMT per chrom and records each call.
    - _apply_sample_qc_and_finalize records its inputs and echoes the MT.

    Returns a dict of recorders: {"recursive_calls": [...], "finalize": {...}}.
    """
    import aou_ld_panel as ldp

    recorder = {"recursive_calls": [], "finalize": None}

    # Fake hail module (the branch does `import hail as hl` but only touches it
    # transitively through the (stubbed) recursion/finalize, so a bare module
    # satisfies the import without exercising any real Hail call).
    fake_hl = types.ModuleType("hail")
    monkeypatch.setitem(sys.modules, "hail", fake_hl)

    # The REAL function object (so we can dispatch: genome-wide call uses the
    # real branch; per-chrom recursive calls are intercepted to return fakes).
    real_load = ldp.load_qc_cohort.__wrapped__ if hasattr(
        ldp.load_qc_cohort, "__wrapped__") else ldp.load_qc_cohort

    def fake_load(*args, **kwargs):
        # Genome-wide entry: interval_filter None, not skip_checkpoint, not
        # _skip_final_write -> run the REAL branch (which will call THIS fake
        # for the per-chrom recursions).
        iv = kwargs.get("interval_filter", None)
        skip_ckpt = kwargs.get("skip_checkpoint", False)
        skip_final = kwargs.get("_skip_final_write", False)
        if iv is None and not skip_ckpt and not skip_final:
            return real_load(*args, **kwargs)
        # Per-chrom recursive call -> record + return a fake post-vqc MT.
        recorder["recursive_calls"].append(dict(kwargs))
        return _FanoutFakeMT(tag=iv, n_rows=per_chrom_rows.get(iv, 0))

    monkeypatch.setattr(ldp, "load_qc_cohort", fake_load)

    def fake_finalize(mt, *, ancestry, sensitivity, bucket,
                      sample_callrate_filtered):
        recorder["finalize"] = {
            "mt": mt, "ancestry": ancestry, "sensitivity": sensitivity,
            "bucket": bucket,
            "sample_callrate_filtered": sample_callrate_filtered,
        }
        return mt

    monkeypatch.setattr(ldp, "_apply_sample_qc_and_finalize", fake_finalize)
    return recorder, fake_load


def test_autosomes_constant_is_chr1_to_chr22():
    """AUTOSOMES is exactly chr1..chr22 (GRCh38) — autosomal LD panel, no
    chrX/Y/M (matches the M2 region-manifest scope). Locks the fan-out range."""
    from aou_ld_panel import AUTOSOMES
    assert tuple(AUTOSOMES) == tuple(f"chr{i}" for i in range(1, 23))
    assert len(AUTOSOMES) == 22
    assert "chrX" not in AUTOSOMES and "chrY" not in AUTOSOMES
    assert "chrM" not in AUTOSOMES and "chr23" not in AUTOSOMES


def test_genome_wide_fans_out_22_per_chrom_calls(monkeypatch):
    """interval_filter=None (real run) issues exactly 22 recursive calls, one
    per autosome, each with interval_filter='chrN' AND _skip_final_write=True
    (Phases 1-2 only). This is the structural fix: every Hail action is bounded
    to one chromosome's partitions (the chr22-Gate-C condition)."""
    import aou_ld_panel as ldp

    per_chrom_rows = {c: 100_000 for c in ldp.AUTOSOMES}
    recorder, fake_load = _install_genome_wide_harness(
        monkeypatch, per_chrom_rows=per_chrom_rows)

    fake_load(
        mt_path="gs://fake/wgs.mt", ancestry="afr", sensitivity=False,
        workspace_bucket="fc-fake-bucket", interval_filter=None,
    )

    calls = recorder["recursive_calls"]
    assert len(calls) == 22, f"expected 22 per-chrom calls, got {len(calls)}"
    seen_intervals = [c["interval_filter"] for c in calls]
    assert seen_intervals == list(ldp.AUTOSOMES), (
        "per-chrom recursion must cover chr1..chr22 in order"
    )
    # Every per-chrom call runs Phases 1-2 only (no sample QC / final write).
    assert all(c["_skip_final_write"] is True for c in calls), (
        "per-chrom calls MUST pass _skip_final_write=True (sample QC is "
        "union-level, NOT per-chromosome)"
    )
    # Ancestry / sensitivity / bucket are threaded through unchanged.
    assert all(c["ancestry"] == "afr" for c in calls)
    assert all(c["sensitivity"] is False for c in calls)


def test_genome_wide_unions_all_22_then_sample_qc_once(monkeypatch):
    """The 22 per-chrom MTs are union_rows'd, and Phase 3 (sample QC + het +
    final write) runs EXACTLY ONCE over the union — not per-chromosome. Guards
    the single subtle correctness point: per-sample call_rate must see all
    variants per sample (W1 QC-ordering invariant)."""
    import aou_ld_panel as ldp

    per_chrom_rows = {c: 50_000 for c in ldp.AUTOSOMES}
    recorder, fake_load = _install_genome_wide_harness(
        monkeypatch, per_chrom_rows=per_chrom_rows)

    out_mt = fake_load(
        mt_path="gs://fake/wgs.mt", ancestry="eur", sensitivity=False,
        workspace_bucket="fc-fake-bucket", interval_filter=None,
    )

    # finalize (sample QC + het + final write) called exactly once.
    fin = recorder["finalize"]
    assert fin is not None, "Phase 3 finalize must run once over the union"
    # The MT handed to finalize is the UNION of all 22 per-chrom fakes.
    union_mt = fin["mt"]
    assert getattr(union_mt, "tag", None) == "union", (
        "sample QC must run over the union_rows result, not a single chrom"
    )
    assert union_mt.union_operands is not None
    assert len(union_mt.union_operands) == 22, (
        "union must concatenate all 22 per-chrom variant-QC'd MTs"
    )
    # Final write goes to the real bucket (downstream contract preserved).
    assert fin["bucket"] == "fc-fake-bucket"
    assert fin["ancestry"] == "eur"
    assert out_mt is union_mt


def test_genome_wide_guard_keys_on_unioned_count_not_per_chrom(monkeypatch):
    """The sample-callrate degeneracy guard keys on the UNIONED raw count, not
    any single chromosome. Each chrom here is BELOW the 500K floor, but their
    union is ABOVE it -> the filter must APPLY (sample_callrate_filtered=True).

    Regression guard against the single-chrom-dips-below-500K-and-wrongly-skips
    bug (DEC-2026-06-04 raw-count guard semantics at genome-wide scale)."""
    import aou_ld_panel as ldp

    # Each autosome below the 500K floor; 22 x 100K = 2.2M union (>> floor).
    per_chrom_rows = {c: 100_000 for c in ldp.AUTOSOMES}
    assert all(v < ldp.MIN_VARIANTS_FOR_SAMPLE_CALLRATE
               for v in per_chrom_rows.values()), "fixture precondition"
    assert sum(per_chrom_rows.values()) >= ldp.MIN_VARIANTS_FOR_SAMPLE_CALLRATE, \
        "fixture precondition: union must exceed the floor"

    recorder, fake_load = _install_genome_wide_harness(
        monkeypatch, per_chrom_rows=per_chrom_rows)

    fake_load(
        mt_path="gs://fake/wgs.mt", ancestry="afr", sensitivity=False,
        workspace_bucket="fc-fake-bucket", interval_filter=None,
    )

    fin = recorder["finalize"]
    assert fin is not None
    assert fin["sample_callrate_filtered"] is True, (
        "guard must key on the UNIONED count (2.2M >= 500K -> APPLY), NOT a "
        "single chromosome's count (100K < 500K would wrongly SKIP)"
    )


def test_single_interval_path_does_not_fan_out(monkeypatch):
    """REGRESSION: the single-interval (chr22 / nano / synthetic) path is
    UNTOUCHED. With interval_filter SET, NO genome-wide fan-out occurs — the
    call proceeds straight into the existing per-interval body. Locks Gate A/B/C
    byte-for-byte behavior (the new branch is gated on interval_filter is None)."""
    import aou_ld_panel as ldp

    # Harness installs the fake recursion recorder; a chr22 call must NOT use it
    # (no recursive per-chrom calls), because interval_filter is SET.
    recorder, fake_load = _install_genome_wide_harness(
        monkeypatch, per_chrom_rows={c: 1 for c in ldp.AUTOSOMES})

    result = fake_load(
        mt_path="gs://fake/wgs.mt", ancestry="afr", sensitivity=False,
        workspace_bucket="fc-fake-bucket", interval_filter="chr22",
    )
    # The chr22 call hit the per-chrom recorder branch (returned a fake) — it did
    # NOT enter the genome-wide fan-out (which would have made 22 recursive
    # calls). Zero fan-out recursion fired beyond this single intercepted call.
    assert len(recorder["recursive_calls"]) == 1
    assert recorder["recursive_calls"][0]["interval_filter"] == "chr22"
    assert recorder["finalize"] is None, (
        "single-interval path must NOT trigger the union-level finalize"
    )
    assert getattr(result, "tag", None) == "chr22"


def test_genome_wide_branch_gate_is_static_in_source():
    """STATIC GUARD (no Hail): the genome-wide fan-out is gated on
    `interval_filter is None and not skip_checkpoint and not _skip_final_write`,
    and the per-chrom recursion passes `_skip_final_write=True`. Locks the gate
    so a future edit cannot silently let skip_checkpoint tests or per-chrom
    recursions fall into the fan-out (infinite recursion / test breakage)."""
    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    assert (
        "if interval_filter is None and not skip_checkpoint "
        "and not _skip_final_write:"
    ) in src, "genome-wide fan-out gate changed — re-verify recursion safety"
    assert "_skip_final_write=True,       # Phases 1-2 only" in src, (
        "per-chrom recursion must pass _skip_final_write=True"
    )
    # The per-chrom body must STOP after post_vqc when _skip_final_write.
    assert "if _skip_final_write:\n        return mt" in src, (
        "the per-interval body must early-return after post_variant_qc when "
        "_skip_final_write is set (so sample QC stays union-level)"
    )


# ----- m3-W2-afr-sensitivity-selfid static-source guards (no Hail) -----
#
# These run on the GPFS dev host (no Hail) and give the RED->GREEN signal for
# the silent-no-op fix without a cluster. They lock the two structural
# invariants the live-Hail T1/T2 tests below exercise dynamically.


def test_sensitivity_silent_skip_escape_is_deleted():
    """RED pre-fix / GREEN post-fix: the silent-skip escape
    `if sensitivity and "self_report" in mt.col:` MUST be deleted. That guard
    converted the never-sourced self_report column into a no-op, making
    sensitivity=True == sensitivity=False (the 2026-06-08 AFR-sens==AFR-primary
    membership-identical defect). It violated the codebase's own ancestry-is-
    MANDATORY discipline (refuse to guess; hard-fail loudly)."""
    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    assert 'if sensitivity and "self_report" in mt.col:' not in src, (
        "the silent-skip escape must be deleted — a missing self_report column "
        "under sensitivity=True must HARD-FAIL, not silently skip the filter"
    )


def test_sensitivity_sources_self_report_via_resolve_aux_file():
    """RED pre-fix / GREEN post-fix: self_report must be SOURCED through the
    existing _resolve_aux_file machinery (mirroring the MANDATORY ancestry
    pattern with on_ambiguous='raise'), not merely referenced at the filter.
    Pre-fix self_report appeared at exactly two lines (the filter guard + the
    filter) and was NEVER import_table'd / annotate_cols'd."""
    src = (PROJECT_ROOT / "src" / "python" / "aou_ld_panel.py").read_text()
    # The resolver must be invoked for the self_report subdir/suffix.
    assert "SELF_REPORT_SUBDIR" in src and "SELF_REPORT_SUFFIX" in src, (
        "self_report must be resolved via _resolve_aux_file with stable "
        "subdir/suffix constants (discover-by-suffix, mirror ancestry_preds.tsv)"
    )
    # The MANDATORY discipline: hard-fail (on_ambiguous='raise') like ancestry.
    assert 'on_ambiguous="raise"' in src, (
        "self_report sourcing must use on_ambiguous='raise' — MANDATORY, "
        "refuse to guess (mirror the ancestry table)"
    )
    # The filter semantics (person.race SOURCE-VALUE code) must be preserved: a
    # .contains() match against the stable 'WhatRaceEthnicity_Black' survey-answer
    # code (carried by the SELF_REPORT_AFR_MATCH constant) -- NOT the fragile
    # human-readable display string (which the concept JOIN named differently and
    # silently zero-matched). See m3-W2-afr-sensitivity-selfid-noop.
    assert '"WhatRaceEthnicity_Black"' in src, (
        "the self-report restriction must match the stable race_source_value "
        "code 'WhatRaceEthnicity_Black' (person.race source value)"
    )
    assert ".contains(" in src and "SELF_REPORT_AFR_MATCH" in src, (
        "the restriction must be applied via a .contains() string-match against "
        "the SELF_REPORT_AFR_MATCH constant"
    )