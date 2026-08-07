"""tests/m3/test_finemap_summary_panel_visible.py -- 260805-o7o Task 3 (FINDING I).

``finemap_summary.tsv`` NAMES THE PANEL.

WHY THIS MODULE EXISTS. m3-04c blast-radius finding I: the summary table was
PANEL-BLIND. Its only LD column was ``ld_dir`` -- the CONSTANT
``config["finemap"]["ld_reference_dir"]``, identical on every row -- so a reader
could not tell an AoU-panel row from a 1kG-panel row without opening the region
JSON. After the ~11-day fire that table is what the manuscript is built from.

THE APPEND IS THE RISK. ``FIELDNAMES`` is the header of a TSV five scripts
consume. A reorder is a silently wrong published table, so the discipline is
APPEND-ONLY and it is pinned three ways here: first-17 byte-identity against
``0378ec8``, ``summary``/``json_error`` dict parity, and a live
``filter_finemap_summary.py`` round trip.

NEGATIVE CONTROLS. One is PERMANENT and in-suite: the discrimination fixture is
re-run against ``FIELDNAMES`` recovered with ``git show 0378ec8:`` and the two
rows are asserted BYTE-IDENTICAL -- finding I, reproduced and asserted.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUMMARIZE_REL = "src/legacy/region_analysis/scripts/summarize_finemap_results.py"
SUMMARIZE = PROJECT_ROOT / SUMMARIZE_REL
FILTER_SCRIPT = (
    PROJECT_ROOT / "src" / "legacy" / "region_analysis" / "scripts"
    / "filter_finemap_summary.py"
)

#: The commit this plan started from -- the source whose FIELDNAMES is
#: panel-blind. The permanent negative-control substrate.
#: DIFFERENTIAL SUBSTRATE -- never re-pinned. See
#: DEC-2026-08-06-sr4-freeze-scope.
PRE_CHANGE_REF = "0378ec8"

#: The 17 columns that existed at 0378ec8, in order. Recovered from git rather
#: than transcribed, so this cannot drift out of agreement with reality.
N_PRE_CHANGE_FIELDS = 17

#: The 14 columns 260805-o7o appends, in order.
APPENDED = [
    "ld_matrix",
    "ld_file_declared",
    "ld_authoritative",
    "ld_status",
    "ld_overlap",
    "ld_overlap_fraction",
    "ld_allele_aware",
    "ld_allele_exact",
    "ld_allele_flipped",
    "ld_allele_dropped_ambiguous",
    "ld_allele_dropped_palindromic",
    "ld_allele_dropped_mismatch",
    "ld_allele_dropped_unusable",
    "ld_allele_catalog_join",
]

_COUNTERS = tuple(f for f in APPENDED if f.startswith("ld_allele_dropped")) + (
    "ld_allele_exact", "ld_allele_flipped",
)


def _load_module(path: Path, name: str):
    """Load a script as a module FROM ITS SOURCE TEXT, never from ``__pycache__``.

    ⚠ THIS IS NOT PEDANTRY -- a stale ``.pyc`` produced a FALSE RED here during
    260805-o7o Task 3, and would produce a FALSE GREEN in the mirror case.
    ``importlib``'s ``SourceFileLoader`` validates cached bytecode against the
    source's (mtime_seconds, size). Test B below reorders two adjacent
    ``FIELDNAMES`` entries as its negative control -- a BYTE-LENGTH-IDENTICAL
    edit -- and if the restore lands in the same wall-clock second, BOTH
    validation fields still match and Python executes the REORDERED bytecode
    against the corrected source. Observed exactly that:

        pyc records: source mtime=1785972228 size=8872
        actual     : source mtime=1785972228 size=8872   -> considered VALID

    A column-order guard that can be silenced by a filesystem timestamp is not a
    guard. ``compile()`` on text read at call time consults no cache at all.
    """
    src = path.read_text()
    mod = importlib.util.module_from_spec(
        importlib.util.spec_from_loader(name, loader=None)
    )
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(src, str(path), "exec"), mod.__dict__)  # noqa: S102
    return mod


@pytest.fixture(scope="module")
def summarize():
    return _load_module(SUMMARIZE, "o7o_summarize_head")


@pytest.fixture(scope="module")
def pre_change(tmp_path_factory):
    """``summarize_finemap_results.py`` as it stood at ``0378ec8``, importable."""
    proc = subprocess.run(
        ["git", "show", f"{PRE_CHANGE_REF}:{SUMMARIZE_REL}"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    assert "ld_matrix" not in proc.stdout, (
        "the negative-control substrate already names the panel -- it is not a "
        "pre-change source"
    )
    out = tmp_path_factory.mktemp("pre") / "summarize_pre.py"
    out.write_text(proc.stdout)
    return _load_module(out, "o7o_summarize_pre")


# --------------------------------------------------------------------------
# fixtures: two region JSONs identical EXCEPT for the panel
# --------------------------------------------------------------------------
def _region_json(ld_matrix: str, *, allele_aware: bool) -> dict:
    """A `success` region payload in exactly the shape run_susie_rss.R writes."""
    payload = {
        "trait": "t2d",
        "ancestry": "AFR",
        "method": "susie_rss",
        "region_id": "SH2B3_12q24",
        "status": "ok",
        "sumstats": "data/processed/sumstats_harmonized/t2d.AFR.tsv.bgz",
        "ld_dir": "data/processed/ld_reference",
        "ld_matrix": ld_matrix,
        "ld_file_declared": ld_matrix,
        "ld_authoritative": True,
        "ld_status": "ld_loaded;overlap_ok;300;1.000",
        "ld_overlap": 300,
        "ld_overlap_fraction": 1.0,
        "credible_sets": {"CS1": [{"CHR": "12", "POS": 111400006,
                                   "BETA": 0.11, "SE": 0.02, "pip": 0.9}]},
        "pip": [0.9, 0.05],
    }
    if allele_aware:
        payload.update({
            "ld_allele_aware": True,
            "ld_allele_exact": 250,
            "ld_allele_flipped": 50,
            "ld_allele_dropped_ambiguous": 1,
            "ld_allele_dropped_palindromic": 12,
            "ld_allele_dropped_mismatch": 4,
            "ld_allele_dropped_unusable": 0,
            "ld_allele_catalog_join": "allele_key",
        })
    else:
        # exactly what toJSON(na = "null") emits for EUR / TRANS
        payload.update({
            "ld_allele_aware": False,
            "ld_allele_exact": None,
            "ld_allele_flipped": None,
            "ld_allele_dropped_ambiguous": None,
            "ld_allele_dropped_palindromic": None,
            "ld_allele_dropped_mismatch": None,
            "ld_allele_dropped_unusable": None,
            "ld_allele_catalog_join": "none",
        })
    return payload


AOU_PANEL = "data/processed/ld_reference/AFR_aou/m2_region_00040__sub14.rds"
KG_PANEL = "data/processed/ld_reference/AFR/SH2B3_12q24.rds"


def _write_pair(tmp_path: Path) -> list[Path]:
    """Two JSONs identical in EVERY field except the panel they name."""
    paths = []
    for tag, panel in (("aou", AOU_PANEL), ("kg", KG_PANEL)):
        p = tmp_path / f"{tag}.json"
        p.write_text(json.dumps(_region_json(panel, allele_aware=True)))
        paths.append(p)
    return paths


def _rows_of(mod, paths: list[Path], out: Path) -> list[str]:
    rows = mod.summarize_inputs([str(p) for p in paths])
    mod.write_summary(rows, out)
    lines = out.read_text().splitlines()
    return lines[1:]


# ==========================================================================
# A -- THE DISCRIMINATION TEST: finding I's whole point
# ==========================================================================
def test_aou_row_and_1kg_row_are_distinguishable_in_the_tsv(summarize, tmp_path):
    """A. Two regions identical in every respect except the panel that produced
    them must produce DIFFERENT rows in ``finemap_summary.tsv``.

    That is finding I stated as a test: a reader must be able to tell an
    AoU-panel row from a 1kG-panel row WITHOUT opening any JSON.

    NEGATIVE CONTROL (PERMANENT, in-suite):
    ``test_negative_control_pre_change_rows_are_byte_identical``.
    """
    paths = _write_pair(tmp_path)
    rows = _rows_of(summarize, paths, tmp_path / "summary.tsv")
    assert len(rows) == 2
    assert rows[0] != rows[1], (
        "the AoU-panel row and the 1kG-panel row are BYTE-IDENTICAL in the "
        "summary TSV -- the table is still panel-blind (finding I)"
    )
    header = (tmp_path / "summary.tsv").read_text().splitlines()[0].split("\t")
    col = header.index("ld_matrix")
    assert rows[0].split("\t")[col] == AOU_PANEL
    assert rows[1].split("\t")[col] == KG_PANEL


def test_negative_control_pre_change_rows_are_byte_identical(pre_change, tmp_path):
    """A-control (PERMANENT). The IDENTICAL fixture against ``0378ec8``'s
    ``FIELDNAMES`` produces two BYTE-IDENTICAL rows -- finding I, reproduced and
    asserted, permanently in-suite.

    If anyone ever neuters the fixture so the two JSONs stop differing only by
    the panel, THIS goes red rather than test A passing for the wrong reason.
    """
    paths = _write_pair(tmp_path)
    rows = _rows_of(pre_change, paths, tmp_path / "summary_pre.tsv")
    assert len(rows) == 2
    # the ONLY pre-change column that can differ is output_path (the file name),
    # so normalise it away -- the claim is that NOTHING ABOUT THE PANEL differs
    header = (tmp_path / "summary_pre.tsv").read_text().splitlines()[0].split("\t")
    opc = header.index("output_path")
    norm = [
        "\t".join(v for i, v in enumerate(r.split("\t")) if i != opc) for r in rows
    ]
    assert norm[0] == norm[1], (
        "the pre-change summarizer was expected to render the AoU row and the "
        "1kG row identically; it did not -- the control no longer reproduces "
        f"the defect it guards:\n{norm[0]}\n{norm[1]}"
    )
    assert "ld_matrix" not in header


# ==========================================================================
# B -- APPEND-ONLY: the first 17 columns are byte-identical, in order
# ==========================================================================
def test_first_seventeen_fieldnames_are_byte_identical_to_pre_change(
    summarize, pre_change
):
    """B. ``FIELDNAMES`` is the header of a TSV five scripts consume. A REORDER
    is a silently wrong published table. The pre-change list must be an exact
    ORDERED PREFIX of the current one.

    NEGATIVE CONTROL (in-test): a deliberately reordered copy must fail the same
    predicate.
    """
    old = list(pre_change.FIELDNAMES)
    new = list(summarize.FIELDNAMES)
    assert len(old) == N_PRE_CHANGE_FIELDS, len(old)
    assert new[:N_PRE_CHANGE_FIELDS] == old, (
        "the first 17 columns are no longer byte-identical to 0378ec8's, in "
        f"order:\n old={old}\n new={new[:N_PRE_CHANGE_FIELDS]}"
    )
    assert new[N_PRE_CHANGE_FIELDS:] == APPENDED, new[N_PRE_CHANGE_FIELDS:]
    assert len(new) == N_PRE_CHANGE_FIELDS + len(APPENDED) == 31
    assert len(set(new)) == len(new), "duplicate column name"

    # ...and the loaded module genuinely reflects the SOURCE TEXT on disk, not a
    # cached bytecode image of some earlier revision of it. See _load_module.
    src = SUMMARIZE.read_text()
    body = src[src.index("FIELDNAMES = ["):]
    body = body[:body.index("\n]")]
    from_text = [
        ln.strip().rstrip(",").strip('"')
        for ln in body.splitlines()[1:]
        if ln.strip().startswith('"')
    ]
    assert from_text == new, (
        "FIELDNAMES as EXECUTED differs from FIELDNAMES as WRITTEN -- a stale "
        f"__pycache__ entry is shadowing the source:\n text={from_text}\n exec={new}"
    )
    # ld_dir is DELIBERATELY kept -- removing it would reorder the header
    assert "ld_dir" in new and "ld_matrix" in new

    # NEGATIVE CONTROL -- the predicate can fail
    shuffled = old[:5] + [old[6], old[5]] + old[7:]
    assert (new[:N_PRE_CHANGE_FIELDS] == shuffled) is False, (
        "the ordered-prefix check cannot observe a reorder"
    )


def test_summary_and_json_error_dicts_are_key_for_key_in_parity(
    summarize, tmp_path
):
    """C. ``summarize_file``'s ``summary`` dict and ``summarize_inputs``'
    ``json_error`` dict must carry the SAME key set, and it must equal
    ``FIELDNAMES``.

    A divergence is a silent COLUMN SHIFT for exactly the rows that already
    failed -- the least-inspected rows in the table.

    NEGATIVE CONTROL (in-test): the same check on a deliberately de-synced pair
    must fail.
    """
    ok = tmp_path / "ok.json"
    ok.write_text(json.dumps(_region_json(AOU_PANEL, allele_aware=True)))
    broken = tmp_path / "broken.json"
    broken.write_text("{ this is not json")

    good_row = summarize.summarize_file(ok)
    err_rows = summarize.summarize_inputs([str(broken)])
    assert len(err_rows) == 1
    err_row = err_rows[0]

    fields = set(summarize.FIELDNAMES)
    assert set(good_row) == fields, sorted(set(good_row) ^ fields)
    assert set(err_row) == fields, sorted(set(err_row) ^ fields)
    assert set(good_row) == set(err_row)
    assert err_row["status"].startswith("json_error:"), err_row["status"]

    # NEGATIVE CONTROL -- a de-synced pair is detected
    desynced = copy.deepcopy(err_row)
    desynced.pop("ld_matrix")
    assert (set(good_row) == set(desynced)) is False, (
        "the parity check cannot observe a missing key"
    )


# ==========================================================================
# D -- END TO END: the counters arrive as integers, or as EMPTY, never as 0
# ==========================================================================
def test_counters_round_trip_as_integers_for_afr_and_empty_for_eur(
    summarize, tmp_path
):
    """D. An AFR row (``allele_aware = true``) must carry the H counters as
    INTEGERS; a EUR row (``allele_aware = false``) must carry them as EMPTY
    STRINGS -- not ``0``.

    ``0`` would read as "measured, and the join was clean", which for EUR is a
    lie: the join was never run. A field that cannot distinguish those two is
    not observability.

    Both polarities in ONE test, so "always empty" and "always 0" both fail.
    """
    afr = tmp_path / "afr.json"
    afr.write_text(json.dumps(_region_json(AOU_PANEL, allele_aware=True)))
    eur_payload = _region_json(
        "data/processed/ld_reference/EUR/SH2B3_12q24.rds", allele_aware=False)
    eur_payload["ancestry"] = "EUR"
    eur_payload["ld_authoritative"] = False
    eur = tmp_path / "eur.json"
    eur.write_text(json.dumps(eur_payload))

    out = tmp_path / "summary.tsv"
    rows = summarize.summarize_inputs([str(afr), str(eur)])
    summarize.write_summary(rows, out)
    lines = out.read_text().splitlines()
    header = lines[0].split("\t")
    afr_row = dict(zip(header, lines[1].split("\t")))
    eur_row = dict(zip(header, lines[2].split("\t")))

    assert afr_row["ld_allele_aware"] == "True"
    assert afr_row["ld_allele_exact"] == "250"
    assert afr_row["ld_allele_flipped"] == "50"
    assert afr_row["ld_allele_dropped_palindromic"] == "12"
    assert afr_row["ld_allele_dropped_unusable"] == "0", (
        "a MEASURED zero must render as '0', not as empty"
    )
    assert afr_row["ld_allele_catalog_join"] == "allele_key"
    assert afr_row["ld_matrix"] == AOU_PANEL

    assert eur_row["ld_allele_aware"] == "False"
    for k in _COUNTERS:
        assert eur_row[k] == "", (
            f"{k} rendered {eur_row[k]!r} for a EUR row; it must be EMPTY so a "
            "reader can tell 'not measured' from 'measured zero'"
        )
    assert eur_row["ld_authoritative"] == "False"


def test_finding_j_no_variants_row_has_empty_ld_columns(summarize, tmp_path):
    """E. A ``no_variants`` region JSON emits NO LD keys at all -- that is
    blast-radius FINDING J and 260805-o7o DELIBERATELY LEAVES IT OPEN.

    Its row must therefore show EMPTY LD columns. Asserted explicitly so the
    residual is VISIBLE in the suite rather than papered over, and so a future
    reader does not mistake the empty cells for a bug in this change.
    """
    nov = tmp_path / "nov.json"
    nov.write_text(json.dumps({
        "trait": "t2d", "ancestry": "AFR", "method": "susie_rss",
        "region_id": "BMI_Xq24", "status": "no_variants",
        "sumstats": "s.tsv.bgz", "ld_dir": "data/processed/ld_reference",
        "notes": "No variants within region bounds",
    }))
    out = tmp_path / "summary.tsv"
    rows = summarize.summarize_inputs([str(nov)])
    summarize.write_summary(rows, out)
    lines = out.read_text().splitlines()
    header = lines[0].split("\t")
    row = dict(zip(header, lines[1].split("\t")))

    assert row["status"] == "no_variants"
    assert row["ld_dir"] == "data/processed/ld_reference"
    for k in APPENDED:
        assert row[k] == "", (
            f"{k} is {row[k]!r} on a no_variants row. Finding J (the early-exit "
            "writers emit no LD keys) is deliberately OPEN -- if it has been "
            "closed, say so in the SUMMARY rather than letting it land here."
        )


# ==========================================================================
# F -- DOWNSTREAM SURVIVAL: the widened table still feeds its consumers
# ==========================================================================
def test_filter_finemap_summary_survives_the_widened_header(summarize, tmp_path):
    """F. ``filter_finemap_summary.py`` reads the summary with
    ``csv.DictReader`` and writes with ``csv.DictWriter(fieldnames=base_fields +
    extras)``, so appended columns propagate to the augmented/tier outputs
    automatically. ``DictWriter`` defaults to ``extrasaction='raise'``, so a row
    carrying a key absent from ``out_fields`` would abort -- run it and prove it
    does not.

    This is the load-bearing half of the 5-consumer blast-radius check: the
    other four are ``pd.read_csv`` / header-driven and were confirmed by
    inspection (their positional indexing is over tabix'd SUMSTATS or an anchors
    string, never over this file).
    """
    afr = tmp_path / "afr.json"
    afr.write_text(json.dumps(_region_json(AOU_PANEL, allele_aware=True)))
    summary = tmp_path / "finemap_summary.tsv"
    summarize.write_summary(summarize.summarize_inputs([str(afr)]), summary)

    augment = tmp_path / "finemap_summary_augmented.tsv"
    proc = subprocess.run(
        [sys.executable, str(FILTER_SCRIPT),
         "--summary", str(summary),
         "--augment-out", str(augment),
         "--tier1-out", str(tmp_path / "t1.tsv"),
         "--tier2-out", str(tmp_path / "t2.tsv"),
         "--tier3-out", str(tmp_path / "t3.tsv")],
        capture_output=True, text=True, timeout=300, cwd=str(PROJECT_ROOT),
    )
    assert proc.returncode == 0, (
        f"filter_finemap_summary.py failed on the widened summary "
        f"(rc={proc.returncode}):\n{proc.stderr[-3000:]}"
    )
    assert augment.exists(), "no augmented output written"
    aug_header = augment.read_text().splitlines()[0].split("\t")
    for k in APPENDED:
        assert k in aug_header, (
            f"{k} did not propagate into finemap_summary_augmented.tsv -- the "
            "appended columns are dropped before the tier tables"
        )
    # the pre-existing columns are still there, still first, still in order
    assert aug_header[:len(summarize.FIELDNAMES)] == summarize.FIELDNAMES
