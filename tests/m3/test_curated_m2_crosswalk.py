"""Tests for ``src/python/build_curated_m2_crosswalk.py`` (m3-04c Task 1a, Layer A).

The crosswalk is the ONLY place the curated Track-A region namespace
(``FTO_16q12``, ``SH2B3_12q24``, ...) and the M2 276-region namespace
(``m2_region_00067``, ``m2_region_00040__sub14``, ...) meet. A wrong row silently
points a fine-map at another locus's LD matrix, so the suite validates the
crosswalk by PHYSICAL GEOMETRY rather than by re-running the builder's own
ranking.

⚠ WHY THAT DISTINCTION IS LOAD-BEARING. An earlier specification of this
crosswalk selected on ``config/ld_regions.tsv``'s ``start_grch37`` /
``end_grch37`` columns. For a SPLIT parent those hold the PARENT's ~89 Mb
bounding box copied verbatim into every subregion row
(``build_ld_region_manifest.py:585-587,650-653``); only the ``*_grch38`` columns
vary. "Smallest containing span" was therefore a perfect 18-way tie whose
lexicographic tie-break returned ``m2_region_00040__sub00`` — a window with ZERO
bp overlap with SH2B3, ~66 Mb away, i.e. the Track A ANCHOR locus pointed at an
unrelated window's LD panel. That defect survived an "independent 12/12
reproduction" because the reproduction re-implemented the same comparison.
Convergent reproduction of a bug is not verification.

Hence:

* ``test_selected_window_physically_overlaps_the_curated_interval`` (T1.5)
  re-lifts the SELECTED region's window straight out of ``config/ld_regions.tsv``
  and asserts physical containment of the curated interval. It never consults the
  builder's ranking.
* ``test_sh2b3_does_not_select_sub00`` (T1.6) is the named regression pin, and it
  asserts WHY ``__sub00`` is wrong (zero physical overlap), not merely that it was
  not chosen.

Module under test is imported INSIDE each test body / helper so collection stays
clean while the module does not yet exist (RED-first, m3-04c Task 1a STEP 0).
"""
from __future__ import annotations

import csv
import functools
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGIONS_CURATED_CSV = PROJECT_ROOT / "config" / "regions_curated.csv"
LD_REGIONS_TSV = PROJECT_ROOT / "config" / "ld_regions.tsv"
CHAIN_PATH = PROJECT_ROOT / "data" / "external" / "liftover" / "hg38ToHg19.over.chain.gz"

EXPECTED_COLUMNS = [
    "region_safe",
    "curated_region_id",
    "chr",
    "curated_start_grch37",
    "curated_end_grch37",
    "m2_region_id",
    "m2_window_start_grch37",
    "m2_window_end_grch37",
    "m2_core_start_grch37",
    "m2_core_end_grch37",
    "window_overlap_bp",
    "core_overlap_bp",
    "overlap_frac",
    "n_containing_candidates",
    "status",
]

# --------------------------------------------------------------------------
# THE RE-DERIVED ORACLE (2026-08-05). Selection by lifted-GRCh38 physical
# containment, ranked on CORE overlap first. SUPERSEDES the prior table --
# ``SH2B3_12q24`` moved ``__sub00`` -> ``__sub14``. The other 11 are unchanged
# and are now re-confirmed by physical overlap rather than by the broken
# parent-repeated-column mechanism.
#   region_safe -> (m2_region_id, status, n_containing_candidates)
# --------------------------------------------------------------------------
RE_DERIVED_ORACLE = {
    "9p21_CDKN2A": ("m2_region_00159", "contained", 1),
    "APOE_19q13": ("m2_region_00083", "contained", 1),
    "APOL1_22q12": ("m2_region_00105", "contained", 1),
    "BMI_5q13_3": ("m2_region_00135", "contained", 1),
    "BMI_Xq24": ("", "unmapped", 0),
    "CXADR_F2RL1_6p21": ("m2_region_00142", "contained", 1),
    "FTO_16q12": ("m2_region_00067", "contained", 1),
    "HLA_6p21": ("m2_region_00143", "contained", 1),
    "MC4R_18q21": ("m2_region_00078", "contained", 1),
    "PYHIN1_1q23": ("m2_region_00008", "contained", 1),
    "SH2B3_12q24": ("m2_region_00040__sub14", "contained", 2),  # *** MOVED ***
    "SLC2A9_urate": ("m2_region_00114", "contained", 1),
}

SH2B3_WRONG_ANSWER = "m2_region_00040__sub00"
SH2B3_TIE_MEMBERS = {"m2_region_00040__sub14", "m2_region_00040__sub15"}
# From the plan's <interfaces>: __sub14's core owns 523,169 bp of the 600,000 bp
# curated span (87.2%); __sub15's core owns 76,831 bp (12.8%).
SH2B3_CORE_OVERLAP = {
    "m2_region_00040__sub14": 523_169,
    "m2_region_00040__sub15": 76_831,
}


# --------------------------------------------------------------------------
# helpers -- deliberately INDEPENDENT of the module under test
# --------------------------------------------------------------------------
def _safe_slug(region_id: str) -> str:
    """Mirror ``Snakefile:49``'s safe-slug construction."""
    return region_id.replace(".", "_").replace("/", "_")


def _norm_chrom(value: str) -> str:
    return value.replace("chr", "").replace("CHR", "").strip()


@functools.lru_cache(maxsize=1)
def _curated_regions() -> dict:
    """region_safe -> dict(curated_region_id, chr, start, end) from the real config."""
    out = {}
    with REGIONS_CURATED_CSV.open(newline="") as fh:
        for row in csv.DictReader(fh):
            out[_safe_slug(row["region_id"])] = {
                "curated_region_id": row["region_id"],
                "chr": _norm_chrom(row["chr"]),
                "start": int(float(row["start"])),
                "end": int(float(row["end"])),
            }
    return out


@functools.lru_cache(maxsize=1)
def _afr_manifest_rows() -> tuple:
    with LD_REGIONS_TSV.open(newline="") as fh:
        rows = [r for r in csv.DictReader(fh, delimiter="\t") if r["ancestry"] == "AFR"]
    return tuple(rows)


@functools.lru_cache(maxsize=1)
def _lifter():
    from pyliftover import LiftOver

    return LiftOver(str(CHAIN_PATH))


def _lift_point(chrom: str, pos: int):
    hits = _lifter().convert_coordinate(f"chr{_norm_chrom(chrom)}", int(pos))
    if not hits:
        return None
    return int(hits[0][1])


@functools.lru_cache(maxsize=None)
def _lifted_window(region_id: str):
    """Independently lift a manifest region's GRCh38 WINDOW back to GRCh37.

    Reads ``config/ld_regions.tsv`` directly. This is the geometry oracle for
    T1.5/T1.6/T1.7 -- it does not touch the builder's ranking.
    """
    for row in _afr_manifest_rows():
        if row["region_id"] == region_id:
            a = _lift_point(row["chr"], int(row["window_start_grch38"]))
            b = _lift_point(row["chr"], int(row["window_end_grch38"]))
            if a is None or b is None:
                return None
            return (min(a, b), max(a, b))
    raise AssertionError(f"{region_id} not present as an AFR row in {LD_REGIONS_TSV}")


@functools.lru_cache(maxsize=None)
def _lifted_core(region_id: str):
    for row in _afr_manifest_rows():
        if row["region_id"] == region_id:
            a = _lift_point(row["chr"], int(row["core_start_grch38"]))
            b = _lift_point(row["chr"], int(row["core_end_grch38"]))
            if a is None or b is None:
                return None
            return (min(a, b), max(a, b))
    raise AssertionError(f"{region_id} not present as an AFR row in {LD_REGIONS_TSV}")


def _overlap_bp(a0: int, a1: int, b0: int, b1: int) -> int:
    return max(0, min(a1, b1) - max(a0, b0))


def _build_into(out_dir: Path) -> Path:
    """Run the REAL builder over the REAL production inputs."""
    from build_curated_m2_crosswalk import build_curated_m2_crosswalk

    out_tsv = out_dir / "curated_to_m2_region_map.tsv"
    build_curated_m2_crosswalk(
        regions_curated_csv=REGIONS_CURATED_CSV,
        ld_regions_tsv=LD_REGIONS_TSV,
        chain_path=CHAIN_PATH,
        out_tsv=out_tsv,
    )
    return out_tsv


@functools.lru_cache(maxsize=1)
def _production_rows() -> tuple:
    """Build the production crosswalk ONCE per session and return its rows."""
    out_dir = Path(tempfile.mkdtemp(prefix="curated_m2_xwalk_"))
    out_tsv = _build_into(out_dir)
    with out_tsv.open(newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    return tuple(rows)


def _row_for(region_safe: str) -> dict:
    for row in _production_rows():
        if row["region_safe"] == region_safe:
            return row
    raise AssertionError(f"no crosswalk row for {region_safe!r}")


# --------------------------------------------------------------------------
# T1.1
# --------------------------------------------------------------------------
def test_crosswalk_covers_every_curated_region():
    rows = _production_rows()
    curated = _curated_regions()

    assert len(rows) == len(curated) == 12, (
        f"expected exactly one crosswalk row per curated region (12), got {len(rows)}"
    )
    assert [r["region_safe"] for r in rows] == sorted(curated), (
        "crosswalk must be keyed on region_safe and sorted by it"
    )
    assert list(rows[0].keys()) == EXPECTED_COLUMNS, (
        f"crosswalk column order changed: {list(rows[0].keys())}"
    )


# --------------------------------------------------------------------------
# T1.2 -- THE RANKING-ORDER PIN (the key the SH2B3 defect turned on)
# --------------------------------------------------------------------------
def test_core_overlap_outranks_window_span():
    """A WIDER window whose CORE contains the locus beats a TIGHTER window whose
    core barely touches it. Core overlap is the PRIMARY key; window span is only
    a determinism backstop."""
    from build_curated_m2_crosswalk import select_m2_candidate

    curated_start, curated_end = 1_000, 2_000
    tight_but_wrong_core = {
        "region_id": "cand_tight",
        "window_start": 900,
        "window_end": 2_100,  # span 1,200 -- the tighter window
        "core_start": 1_990,
        "core_end": 2_100,  # only 10 bp of the curated interval
    }
    wide_but_right_core = {
        "region_id": "cand_wide",
        "window_start": 500,
        "window_end": 3_000,  # span 2,500 -- the wider window
        "core_start": 900,
        "core_end": 2_500,  # owns the whole curated interval
    }

    got = select_m2_candidate(
        curated_start, curated_end, [tight_but_wrong_core, wide_but_right_core]
    )
    assert got["status"] == "contained"
    assert got["m2_region_id"] == "cand_wide", (
        "ranking must put CORE overlap ahead of window span -- putting span first "
        "is the shape of the __sub00 defect"
    )
    assert got["core_overlap_bp"] == 1_000
    assert got["n_containing_candidates"] == 2


# --------------------------------------------------------------------------
# T1.3
# --------------------------------------------------------------------------
def test_partial_overlap_is_marked_not_silently_promoted():
    from build_curated_m2_crosswalk import select_m2_candidate

    curated_start, curated_end = 1_000, 2_000
    overlapping_but_not_containing = {
        "region_id": "cand_partial",
        "window_start": 1_500,
        "window_end": 2_500,
        "core_start": 1_600,
        "core_end": 2_400,
    }

    got = select_m2_candidate(
        curated_start, curated_end, [overlapping_but_not_containing]
    )
    assert got["status"] == "partial", (
        "a candidate that does not CONTAIN the curated interval must never be "
        "presented as a clean containment"
    )
    assert got["m2_region_id"] == "cand_partial"
    assert got["window_overlap_bp"] == 500
    assert got["overlap_frac"] == pytest.approx(0.5)
    assert got["n_containing_candidates"] == 0


# --------------------------------------------------------------------------
# T1.4
# --------------------------------------------------------------------------
def test_chrx_region_is_unmapped():
    """M2 is autosomes-only (D-M2-09), so a chrX curated region has no counterpart."""
    from build_curated_m2_crosswalk import select_m2_candidate

    got = select_m2_candidate(118_000_000, 122_000_000, [])
    assert got["status"] == "unmapped"
    assert got["m2_region_id"] == ""

    row = _row_for("BMI_Xq24")
    assert row["status"] == "unmapped"
    assert row["m2_region_id"] == ""
    assert _curated_regions()["BMI_Xq24"]["chr"] == "X"

    unmapped = [r["region_safe"] for r in _production_rows() if r["status"] == "unmapped"]
    assert unmapped == ["BMI_Xq24"], (
        f"BMI_Xq24 must be the ONLY unmapped curated region; got {unmapped}"
    )


# --------------------------------------------------------------------------
# T1.5 -- ⚠ THE CLASS-OF-BUG TEST
# --------------------------------------------------------------------------
@pytest.mark.parametrize("region_safe", sorted(RE_DERIVED_ORACLE))
def test_selected_window_physically_overlaps_the_curated_interval(region_safe):
    """Validate the OUTPUT by geometry, never by re-running the ranking.

    A test that re-implements the selection cannot catch a wrong selection rule --
    that is exactly how the prior "12/12 independent reproduction" reproduced the
    ``__sub00`` defect instead of finding it.

    ⚠ DELIBERATELY NO ``pytest.skip`` FOR THE NON-CONTAINED ROW. Skipping on
    ``status != "contained"`` would mean a row that silently degraded from
    ``contained`` to ``partial`` SKIPPED this geometry check instead of failing
    it -- a guard that hides the bug rather than catching it. The one expected
    non-contained row is asserted by name instead.
    """
    row = _row_for(region_safe)
    expected_id, expected_status, _n = RE_DERIVED_ORACLE[region_safe]
    if expected_status != "contained":
        assert row["status"] == expected_status, (
            f"{region_safe} was expected to be {expected_status}; a row that "
            f"changes status must FAIL here, never skip"
        )
        assert region_safe == "BMI_Xq24", (
            "BMI_Xq24 (chrX; M2 is autosomes-only per D-M2-09) is the ONLY curated "
            f"region allowed to be non-contained; {region_safe} is not"
        )
        assert row["m2_region_id"] == ""
        assert row["m2_window_start_grch37"] == ""
        return
    assert row["status"] == "contained", (
        f"{region_safe} degraded from contained to {row['status']!r} -- a partial "
        "match must never be promoted, and must never be skipped past"
    )

    curated = _curated_regions()[region_safe]
    m2_id = row["m2_region_id"]
    assert m2_id, "a contained row must name an M2 region"

    lifted = _lifted_window(m2_id)
    assert lifted is not None, f"{m2_id}'s GRCh38 window failed to lift to GRCh37"
    w0, w1 = lifted

    assert w0 <= curated["start"] and w1 >= curated["end"], (
        f"{region_safe} -> {m2_id}: lifted GRCh37 window {w0}-{w1} does NOT contain "
        f"the curated interval {curated['start']}-{curated['end']}"
    )
    assert (
        _overlap_bp(w0, w1, curated["start"], curated["end"])
        == curated["end"] - curated["start"]
    )
    assert int(row["window_overlap_bp"]) == curated["end"] - curated["start"], (
        "window_overlap_bp on a contained row must equal the FULL curated span"
    )
    # And the recorded window must be the one that was actually lifted.
    assert (int(row["m2_window_start_grch37"]), int(row["m2_window_end_grch37"])) == (w0, w1)


# --------------------------------------------------------------------------
# T1.6 -- ⚠ THE REGRESSION PIN
# --------------------------------------------------------------------------
def test_sh2b3_does_not_select_sub00():
    """SH2B3_12q24 is the Track A ANCHOR. ``__sub00`` is 66 Mb off target."""
    row = _row_for("SH2B3_12q24")
    curated = _curated_regions()["SH2B3_12q24"]

    assert row["m2_region_id"] == "m2_region_00040__sub14", (
        "SH2B3_12q24 must resolve to the subregion whose CORE owns the locus"
    )
    assert row["m2_region_id"] != SH2B3_WRONG_ANSWER, (
        "reverting to the parent-repeated grch37 columns re-selects __sub00"
    )

    # WHY __sub00 is wrong: it has ZERO physical overlap with the locus.
    wrong = _lifted_window(SH2B3_WRONG_ANSWER)
    assert wrong is not None
    assert _overlap_bp(wrong[0], wrong[1], curated["start"], curated["end"]) == 0, (
        f"{SH2B3_WRONG_ANSWER} lifted window {wrong} was expected to have ZERO bp "
        f"overlap with SH2B3 {curated['start']}-{curated['end']}"
    )
    assert wrong[1] < curated["start"], "__sub00 sits well BELOW the SH2B3 locus"


# --------------------------------------------------------------------------
# T1.7 -- the only place a tie-break is load-bearing in production
# --------------------------------------------------------------------------
def test_sh2b3_tie_is_broken_on_core_overlap():
    row = _row_for("SH2B3_12q24")
    curated = _curated_regions()["SH2B3_12q24"]

    assert int(row["n_containing_candidates"]) == 2, (
        "exactly two AFR manifest windows fully contain SH2B3"
    )

    # Independently recompute the containing set from the manifest geometry.
    containing = set()
    for man in _afr_manifest_rows():
        if _norm_chrom(man["chr"]) != curated["chr"]:
            continue
        lifted = _lifted_window(man["region_id"])
        if lifted is None:
            continue
        if lifted[0] <= curated["start"] and lifted[1] >= curated["end"]:
            containing.add(man["region_id"])
    assert containing == SH2B3_TIE_MEMBERS, (
        f"containing-candidate set for SH2B3 changed: {sorted(containing)}"
    )

    # Both fully contain the locus -- containment cannot decide. Core overlap can.
    for member in sorted(SH2B3_TIE_MEMBERS):
        core = _lifted_core(member)
        assert core is not None
        got = _overlap_bp(core[0], core[1], curated["start"], curated["end"])
        assert got == SH2B3_CORE_OVERLAP[member], (
            f"{member} core overlap changed: {got} != {SH2B3_CORE_OVERLAP[member]}"
        )

    winner = max(SH2B3_CORE_OVERLAP, key=SH2B3_CORE_OVERLAP.get)
    assert row["m2_region_id"] == winner
    assert int(row["core_overlap_bp"]) == SH2B3_CORE_OVERLAP[winner] == 523_169


# --------------------------------------------------------------------------
# T1.8
# --------------------------------------------------------------------------
@pytest.mark.parametrize("region_safe", sorted(RE_DERIVED_ORACLE))
def test_production_crosswalk_matches_the_rederived_oracle(region_safe):
    """Exact-value pin. Trustworthy ONLY because T1.5 validates the values
    geometrically -- an exact-value table reproduced the last defect."""
    expected_id, expected_status, expected_n = RE_DERIVED_ORACLE[region_safe]
    row = _row_for(region_safe)
    assert (row["m2_region_id"], row["status"], int(row["n_containing_candidates"])) == (
        expected_id,
        expected_status,
        expected_n,
    )


# --------------------------------------------------------------------------
# T1.9
# --------------------------------------------------------------------------
def test_crosswalk_is_deterministic(tmp_path):
    first = _build_into(tmp_path / "a")
    second = _build_into(tmp_path / "b")
    assert first.read_bytes() == second.read_bytes(), (
        "building the crosswalk twice over identical inputs must be byte-identical"
    )


# --------------------------------------------------------------------------
# T1.10 -- the unmapped fallback is byte-identical to today's resolver argument
# --------------------------------------------------------------------------
def test_unmapped_region_resolver_argument_is_byte_identical_to_today(tmp_path):
    """``CURATED_TO_M2.get(region, REGION_SAFE_TO_ID[region])`` for an unmapped
    curated slug must hand ``resolve_ld_path`` character-for-character today's
    value, so no frozen numeric can move."""
    from build_curated_m2_crosswalk import load_curated_to_m2

    out_tsv = _build_into(tmp_path / "load")
    curated_to_m2 = load_curated_to_m2(out_tsv)

    # Rebuild REGION_SAFE_TO_ID exactly as Snakefile:45-62 does.
    region_safe_to_id = {
        safe: meta["curated_region_id"] for safe, meta in _curated_regions().items()
    }

    assert "BMI_Xq24" not in curated_to_m2, (
        "unmapped rows must be SKIPPED when the crosswalk is loaded, so the "
        "dict .get() falls through to REGION_SAFE_TO_ID"
    )
    resolved = curated_to_m2.get("BMI_Xq24", region_safe_to_id["BMI_Xq24"])
    assert resolved == "BMI_Xq24" == region_safe_to_id["BMI_Xq24"]

    # And a mapped region really does route through the crosswalk.
    assert curated_to_m2.get("FTO_16q12", region_safe_to_id["FTO_16q12"]) == (
        "m2_region_00067"
    )
    # Every loaded value is non-empty and every mapped curated slug is present.
    assert all(v for v in curated_to_m2.values())
    assert set(curated_to_m2) == {
        safe for safe, (mid, _s, _n) in RE_DERIVED_ORACLE.items() if mid
    }


# --------------------------------------------------------------------------
# Missing-file behaviour: finemap.smk must still build a DAG on a fresh clone.
# --------------------------------------------------------------------------
def test_load_curated_to_m2_returns_empty_dict_when_file_absent(tmp_path):
    from build_curated_m2_crosswalk import load_curated_to_m2

    assert load_curated_to_m2(tmp_path / "does_not_exist.tsv") == {}
