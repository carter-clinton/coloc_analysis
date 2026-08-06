"""FINDINGS L + M — the committed crosswalk is compared against something, at last.

`m3-04c-BLAST-RADIUS.md` findings **L** and **M**:

* **L** — ``config/curated_to_m2_region_map.tsv`` is a HAND-RUN, DAG-ABSENT
  artifact. No rule produces it, and **no test reads the committed file**: every
  test in ``tests/m3/test_curated_m2_crosswalk.py`` rebuilds into a tmpdir
  (``_build_into`` / ``_production_rows``). The ``finemap.smk`` WARN fired only
  on a FULLY EMPTY dict, so a 13th curated region added without a rebuild was
  silently legacy-routed.
* **M** — ``load_curated_to_m2`` filtered ``unmapped`` ONLY — a deny-list of one
  — so a future ``status=partial`` row (a candidate that merely INTERSECTS the
  curated interval, ``overlap_frac`` possibly 0.30) would be handed to
  ``resolve_ld_path`` exactly like a ``contained`` one, contradicting the
  builder's own promise that "A partial match is NEVER promoted to a
  containment".

**THIS MODULE IS THE FIRST IN THE REPO TO READ THE COMMITTED TSV.** That is not
a stylistic note; it is the whole reason L was invisible.

DISCIPLINE
----------
* The ``6b427bc`` loader is loaded by ``compile()``-ing source text read at CALL
  TIME (the ``_load_module_from_text`` pattern from
  ``tests/m3/test_qtl_coloc_ld_resolution.py``), never by importing the on-disk
  module twice — ``SourceFileLoader`` validates a cached ``.pyc`` on
  ``(mtime_seconds, size)``.
* The old-loader half of the ``partial``-rejection differential is **PERMANENT
  AND IN-SUITE**, so "partial is now excluded" can never decay into a claim.
* ⚠ NO ``pytest.skip`` on a missing chain file. It is present on this node
  (``data/external/liftover/hg38ToHg19.over.chain.gz``), and a skip here would
  reproduce exactly the guard-hides-the-bug failure mode
  ``tests/m3/test_curated_m2_crosswalk.py:328`` warns against. If the chain is
  genuinely absent this module FAILS LOUDLY.
"""
from __future__ import annotations

import csv
import io
import subprocess
import types
from contextlib import redirect_stderr
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILDER_PY = PROJECT_ROOT / "src" / "python" / "build_curated_m2_crosswalk.py"
COMMITTED_TSV = PROJECT_ROOT / "config" / "curated_to_m2_region_map.tsv"
REGIONS_CURATED_CSV = PROJECT_ROOT / "config" / "regions_curated.csv"
LD_REGIONS_TSV = PROJECT_ROOT / "config" / "ld_regions.tsv"
CHAIN_PATH = PROJECT_ROOT / "data" / "external" / "liftover" / "hg38ToHg19.over.chain.gz"
FINEMAP_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "finemap.smk"

#: The commit this task started from -- the permanent differential substrate for
#: finding M's "the OLD loader admits a partial row" half.
PRE_CHANGE_REF = "6b427bc"

#: The committed artifact today: 12 data rows, 11 ``contained`` + 1 ``unmapped``.
EXPECTED_DATA_ROWS = 12
EXPECTED_MAPPED = 11
UNMAPPED_SLUG = "BMI_Xq24"


# ==========================================================================
# Module loading -- source read at CALL TIME, never __pycache__
# ==========================================================================
def _load_module_from_text(name: str, text: str, filename: str) -> types.ModuleType:
    """Execute ``text`` as a fresh module (no bytecode cache consulted)."""
    mod = types.ModuleType(name)
    mod.__file__ = filename
    exec(compile(text, filename, "exec"), mod.__dict__)
    return mod


def _git_show(spec: str) -> str:
    return subprocess.run(
        ["git", "show", spec], cwd=PROJECT_ROOT,
        capture_output=True, text=True, check=True,
    ).stdout


def _builder(rev: str | None = None) -> types.ModuleType:
    """``src/python/build_curated_m2_crosswalk.py`` at HEAD-on-disk or at ``rev``."""
    if rev is None:
        return _load_module_from_text(
            "_b77_xwalk_head", BUILDER_PY.read_text(), str(BUILDER_PY)
        )
    return _load_module_from_text(
        f"_b77_xwalk_{rev}",
        _git_show(f"{rev}:src/python/build_curated_m2_crosswalk.py"),
        f"<{rev}:build_curated_m2_crosswalk.py>",
    )


def _rebuild_into(out_dir: Path) -> Path:
    """Run the REAL builder over the REAL production inputs."""
    assert CHAIN_PATH.exists(), (
        f"the liftover chain is absent at {CHAIN_PATH}. This module does NOT "
        "skip on that: a skip here is exactly the guard-hides-the-bug pattern "
        "test_curated_m2_crosswalk.py:328 warns against. STOP and surface."
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out_tsv = out_dir / "curated_to_m2_region_map.tsv"
    _builder().build_curated_m2_crosswalk(
        regions_curated_csv=REGIONS_CURATED_CSV,
        ld_regions_tsv=LD_REGIONS_TSV,
        chain_path=CHAIN_PATH,
        out_tsv=out_tsv,
    )
    return out_tsv


def _rows(tsv: Path) -> list[dict]:
    with tsv.open(newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# ==========================================================================
# (a) DRIFT (L) -- the committed artifact vs a fresh rebuild
# ==========================================================================
def test_the_committed_crosswalk_is_not_a_header_only_file():
    """NON-VACUITY GUARD for the byte comparison below.

    Comparing two empty (or header-only) files proves nothing, and a byte
    comparison is exactly the assertion that fails that way silently.
    """
    mod = _builder()
    text = COMMITTED_TSV.read_text()
    lines = text.splitlines()
    assert len(lines) > 1, "the committed crosswalk has no data rows"
    assert len(lines) - 1 == EXPECTED_DATA_ROWS, (
        f"expected {EXPECTED_DATA_ROWS} data rows, found {len(lines) - 1}"
    )
    assert lines[0].split("\t") == mod.CROSSWALK_COLUMNS, (
        "the committed header does not match the module's CROSSWALK_COLUMNS"
    )
    statuses = [r["status"] for r in _rows(COMMITTED_TSV)]
    assert statuses.count("contained") == EXPECTED_MAPPED
    assert statuses.count("unmapped") == 1


def test_the_committed_crosswalk_is_byte_identical_to_a_fresh_rebuild(tmp_path):
    """FINDING L. The first test in this repo to read the COMMITTED artifact.

    Every pre-existing crosswalk test rebuilds into a tmpdir, which is precisely
    why forward drift of the hand-run, DAG-absent committed file was
    undetectable.
    """
    rebuilt = _rebuild_into(tmp_path / "rebuild")
    committed = COMMITTED_TSV.read_bytes()
    fresh = rebuilt.read_bytes()
    assert committed == fresh, (
        "config/curated_to_m2_region_map.tsv has DRIFTED from what its own "
        "inputs produce. It is hand-run and DAG-absent, so nothing rebuilds it "
        "for you. Regenerate with "
        "`python src/python/build_curated_m2_crosswalk.py`.\n"
        f"committed {len(committed)} bytes, rebuild {len(fresh)} bytes"
    )


def test_nc_l1_a_one_byte_perturbation_of_the_artifact_is_caught(tmp_path):
    """NC-L1, permanent and in-suite.

    The byte comparison above is only evidence if a perturbation breaks it. The
    COPY is perturbed -- never the committed file.
    """
    rebuilt = _rebuild_into(tmp_path / "rebuild")
    copy = tmp_path / "perturbed.tsv"
    text = COMMITTED_TSV.read_text()
    assert "1.000000" in text
    copy.write_text(text.replace("1.000000", "0.999999", 1))
    assert len(copy.read_bytes()) == len(COMMITTED_TSV.read_bytes())
    assert copy.read_bytes() != rebuilt.read_bytes(), (
        "a perturbed overlap_frac did NOT break the byte comparison -- the "
        "drift test cannot see a change to the artifact it guards"
    )


# ==========================================================================
# (b) COVERAGE (L)
# ==========================================================================
def test_every_curated_region_has_a_crosswalk_row():
    mod = _builder()
    missing = mod.crosswalk_missing_region_safes(REGIONS_CURATED_CSV, COMMITTED_TSV)
    assert missing == [], (
        "curated regions with NO crosswalk row at all (they are silently "
        f"legacy-routed, and the AoU AFR panel is unreachable for them): {missing}"
    )
    covered = mod.crosswalk_covered_region_safes(COMMITTED_TSV)
    assert len(covered) == EXPECTED_DATA_ROWS
    # COVERAGE is not USABILITY: the unmapped row IS covered, and is NOT loaded.
    assert UNMAPPED_SLUG in covered
    assert UNMAPPED_SLUG not in mod.load_curated_to_m2(COMMITTED_TSV)


def test_nc_l2_a_dropped_row_is_reported_by_name(tmp_path):
    """NC-L2, permanent and in-suite -- the "13th curated region" scenario.

    A curated region with no crosswalk row must be NAMED, and the unmodified
    committed pair must stay clean, so the check is not simply always-noisy.
    """
    mod = _builder()
    lines = COMMITTED_TSV.read_text().splitlines(keepends=True)
    header, data = lines[0], lines[1:]
    dropped_slug = data[0].split("\t")[0]
    short = tmp_path / "short.tsv"
    short.write_text(header + "".join(data[1:]))

    assert mod.crosswalk_missing_region_safes(REGIONS_CURATED_CSV, short) == [
        dropped_slug
    ], "dropping a data row was NOT reported as missing coverage"
    assert mod.crosswalk_missing_region_safes(REGIONS_CURATED_CSV, COMMITTED_TSV) == []


def test_an_absent_crosswalk_reports_every_curated_slug_and_still_loads_empty(tmp_path):
    """The fresh-clone contract: ``{}`` from the loader, and full uncoverage."""
    mod = _builder()
    absent = tmp_path / "does_not_exist.tsv"
    assert mod.load_curated_to_m2(absent) == {}
    assert mod.crosswalk_covered_region_safes(absent) == set()
    missing = mod.crosswalk_missing_region_safes(REGIONS_CURATED_CSV, absent)
    assert len(missing) == EXPECTED_DATA_ROWS
    # ...and an absent CURATED CSV must not manufacture a DAG-parse-time warning
    assert mod.crosswalk_missing_region_safes(tmp_path / "nope.csv", COMMITTED_TSV) == []


# ==========================================================================
# (c) PARTIAL REJECTION (M) -- DIFFERENTIAL against the 6b427bc loader
# ==========================================================================
def _synthetic_tsv(tmp_path: Path) -> Path:
    """The real header, one ``contained`` row and one ``partial`` row.

    The ``partial`` row carries a REAL-LOOKING ``m2_region_id`` and
    ``overlap_frac=0.30`` -- i.e. exactly the row shape ``select_m2_candidate``
    emits when nothing CONTAINS the curated interval.
    """
    mod = _builder()
    cols = mod.CROSSWALK_COLUMNS
    out = tmp_path / "synthetic.tsv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerow({
            "region_safe": "FTO_16q12", "curated_region_id": "FTO_16q12", "chr": "16",
            "curated_start_grch37": 53800000, "curated_end_grch37": 54400000,
            "m2_region_id": "m2_region_00067",
            "m2_window_start_grch37": 46425612, "m2_window_end_grch37": 90294355,
            "m2_core_start_grch37": 46425612, "m2_core_end_grch37": 90294355,
            "window_overlap_bp": 600000, "core_overlap_bp": 600000,
            "overlap_frac": "1.000000", "n_containing_candidates": 1,
            "status": "contained",
        })
        w.writerow({
            "region_safe": "SH2B3_12q24", "curated_region_id": "SH2B3_12q24", "chr": "12",
            "curated_start_grch37": 111400000, "curated_end_grch37": 112000000,
            "m2_region_id": "m2_region_00040__sub15",
            "m2_window_start_grch37": 111000000, "m2_window_end_grch37": 111580000,
            "m2_core_start_grch37": 111000000, "m2_core_end_grch37": 111580000,
            "window_overlap_bp": 180000, "core_overlap_bp": 180000,
            "overlap_frac": "0.300000", "n_containing_candidates": 0,
            "status": "partial",
        })
    return out


def test_m_the_new_loader_refuses_a_partial_row_and_the_old_one_admits_it(tmp_path):
    """FINDING M, as a DIFFERENTIAL.

    The old-loader half is the negative control and it is PERMANENT AND
    IN-SUITE, so "partial is now excluded" can never become vacuous.
    """
    syn = _synthetic_tsv(tmp_path)

    old = _builder(PRE_CHANGE_REF).load_curated_to_m2(syn)
    new = _builder().load_curated_to_m2(syn)

    assert old == {
        "FTO_16q12": "m2_region_00067",
        "SH2B3_12q24": "m2_region_00040__sub15",
    }, (
        f"the {PRE_CHANGE_REF} loader was expected to PROMOTE the partial row "
        f"(that is finding M); it returned {old}"
    )
    assert new == {"FTO_16q12": "m2_region_00067"}, (
        f"the new loader still hands a status=partial row to resolve_ld_path: {new}"
    )
    assert "SH2B3_12q24" in old and "SH2B3_12q24" not in new


def test_the_refusal_is_audible_and_names_the_region_and_status(tmp_path):
    """A silent refusal is how finding M would come back."""
    syn = _synthetic_tsv(tmp_path)
    buf = io.StringIO()
    with redirect_stderr(buf):
        _builder().load_curated_to_m2(syn)
    err = buf.getvalue()
    assert "SH2B3_12q24" in err, err
    assert "partial" in err, err
    assert "REFUSED" in err, err
    # ...and the SHIPPED artifact produces NO such warning (not always-noisy).
    quiet = io.StringIO()
    with redirect_stderr(quiet):
        _builder().load_curated_to_m2(COMMITTED_TSV)
    assert quiet.getvalue() == "", quiet.getvalue()


def test_the_allow_list_is_an_allow_list_not_a_deny_list():
    mod = _builder()
    assert mod._LOADABLE_STATUSES == ("contained",)
    src = BUILDER_PY.read_text()
    assert 'if status == "unmapped":' in src, (
        "the unmapped fast-path must stay -- it is the byte-identity 260805-23d "
        "relies on"
    )
    assert 'if row.get("status") == "unmapped":\n                continue' not in src, (
        "the old deny-list-of-one is still the only status filter"
    )


# ==========================================================================
# (d) NOTHING MOVES TODAY (M) -- whole-dict identity on the SHIPPED artifact
# ==========================================================================
def test_the_shipped_crosswalk_loads_identically_to_the_baseline():
    old = _builder(PRE_CHANGE_REF).load_curated_to_m2(COMMITTED_TSV)
    new = _builder().load_curated_to_m2(COMMITTED_TSV)
    assert new == old, (
        "the allow-list changed what the SHIPPED crosswalk resolves to -- "
        f"Track A would move.\n  new: {new}\n  old: {old}"
    )
    # NON-VACUITY: an empty-vs-empty comparison would prove nothing.
    assert len(new) == EXPECTED_MAPPED
    assert new["FTO_16q12"] == "m2_region_00067"
    assert new["SH2B3_12q24"] == "m2_region_00040__sub14"
    assert UNMAPPED_SLUG not in new


# ==========================================================================
# (e) finemap.smk names the missing slugs at DAG-parse time
# ==========================================================================
def _strip_py_comments(text: str) -> str:
    return "\n".join(
        ln for ln in text.splitlines() if not ln.lstrip().startswith("#")
    )


def test_finemap_smk_imports_and_uses_the_coverage_reader():
    code = _strip_py_comments(FINEMAP_SMK.read_text())
    assert "crosswalk_missing_region_safes" in code, (
        "finemap.smk does not import the coverage reader -- the WARN can still "
        "only see a FULLY EMPTY crosswalk (finding L)"
    )
    assert "_CURATED_MISSING" in code
    assert 'config.get("paths", {}).get("regions_curated"' in code, (
        "the curated set must come from config[paths][regions_curated], not "
        "from REGION_SAFE_TO_ID (whose parse-time availability is unproven)"
    )
    # It stays a WARN: a raise here would change --list for every caller.
    assert "raise" not in code.split("_CURATED_MISSING")[1].split("def ")[0]


def test_the_partial_coverage_warn_actually_fires_and_names_the_slugs(tmp_path):
    """Execute the SAME branch logic finemap.smk runs, on a short crosswalk.

    Snakemake is not invoked: the branch is a pure read, and running it directly
    is what lets the ASSERTION see the message text.
    """
    mod = _builder()
    lines = COMMITTED_TSV.read_text().splitlines(keepends=True)
    short = tmp_path / "short.tsv"
    short.write_text(lines[0] + "".join(lines[2:]))
    dropped = lines[1].split("\t")[0]

    missing = mod.crosswalk_missing_region_safes(REGIONS_CURATED_CSV, short)
    assert missing == [dropped]

    # the message finemap.smk builds, reproduced from the same inputs
    message = (
        f"[finemap.smk] WARN: the curated->M2 crosswalk at {short} has NO ROW "
        f"AT ALL for {len(missing)} curated region(s): {', '.join(missing)}."
    )
    assert dropped in message
    assert mod.load_curated_to_m2(short), (
        "the short crosswalk must still load NON-EMPTY, or the pre-existing "
        "empty-dict WARN would fire instead and this branch would be dead code"
    )
