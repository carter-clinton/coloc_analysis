"""RED-first tests for src/python/pcs_panelwide_reclassify.py (quick-260831-kw8).

WHAT THE MODULE UNDER TEST ANSWERS
----------------------------------
``pairwise_completeness_scan``'s ``already_occluded`` is ANCHOR-RELATIVE — it is
``deletion.pos < partner.pos <= deletion.span_end`` against THE ANCHOR DELETION
ONLY (``pairwise_completeness_scan.py:616``). The PRODUCTION excludelist is a
different quantity: ``occlusion_span_filter.detect_occluded_variants`` over EVERY
deletion in the window (``run_native_ld_panel.py:878``). So
``already_occluded == False`` does NOT mean "survives ``--exclude``", and
``n_undefined_not_already_occluded`` does NOT count pairs that survive filtering.

The module under test answers the PANEL-WIDE question POST-HOC, from an
already-emitted ``pcs_pairs.tsv`` plus the cohort ``.bim``. It reads no
genotypes and cannot require the ~4h20m sweep to be re-run — the sweep's output
is its INPUT.

WHAT THIS FILE DOES NOT ESTABLISH
---------------------------------
No prevalence, no boundary width, no policy change. The known-answer fixtures
are SUBSETS of their real windows, so their NOT-occluded verdicts are
scope-limited by the monotonicity asymmetry that
:func:`test_occlusion_is_monotone_in_the_row_set` proves.

RED-for-the-right-reason: ``pcs_panelwide_reclassify`` is imported INSIDE each
test body, NOT at module top, so pytest COLLECTS this file cleanly and every
test fails as an assert/call-time failure rather than as a collection error.
This mirrors ``tests/m3/test_pairwise_completeness_scan.py``.

Runs in smoke_dev py3.11 (stdlib only). No Hail, no plink, no perimeter, no
``.bed``.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

_MODULE_REL = "src/python/pcs_panelwide_reclassify.py"

# NOTE: NO module-level ``import pcs_panelwide_reclassify`` — see the docstring.


# --------------------------------------------------------------------------- #
# THE BANKED IDENTITY ROWS (verbatim from                                      #
# .planning/debug/260826-PCS-...-prereg-prediction.md BLOCK 2).                #
# Nothing here is re-derived; the vids are transcribed and the OCCLUSION       #
# verdicts are computed by the FROZEN detector at test time, never asserted    #
# from memory.                                                                 #
# --------------------------------------------------------------------------- #

# The ELEVEN distinct vids named on the SEVEN banked ``m2_region_00001`` rows.
R1_VIDS = (
    "chr1:1980423:CCTCTTACCGTGTGGGGAGGACGGGTGAACGAGAGACTGTATCTAAGCCACCGGCACAGA:C",
    "chr1:1980475:G:A",
    "chr1:5733474:TCCCATCAGTCCACACACAGCTTCCGTCC:T",
    "chr1:5733487:C:T",
    "chr1:5922716:ACGGTGG:A",
    "chr1:5922718:G:A",
    "chr1:5922724:ACTGCCTGCAGTCCTGGCTTAGCCGGGCACG:A",
    "chr1:7492679:ACAAACACAAACCTACAAACACACACGCAGG:A",
    "chr1:7492693:ACAAACACACACGCAGG:A",
    "chr1:8375794:TTCCTCACTCAGCAGCCACTGAAAATGCA:T",
    "chr1:8375822:A:T",
)

#: The occluder in the region-1 tangle and the member it covers (span
#: 5922716-5922722; MEASURED, not assumed — see
#: :func:`test_the_region1_tangle_is_reclassified_member_occluded`).
R1_OCCLUDER = "chr1:5922716:ACGGTGG:A"
R1_OCCLUDED = "chr1:5922718:G:A"
#: The ANCHOR of the -6 row: a DIFFERENT deletion whose span never reaches the SNP.
R1_MINUS6_ANCHOR = "chr1:5922724:ACTGCCTGCAGTCCTGGCTTAGCCGGGCACG:A"

R8_VIDS = (
    "chr1:155856782:G:GAAATAGAATGGGAGTAGCCAGGGCAGCTCTTTTATTTCACAGATAATTACTGAGATCAA",
    "chr1:155856785:AAAG:A",
    "chr1:155856788:G:GGGGAAAAAAAGAAAAAGAAAGAAAGAAA",
)
R149_VIDS = (
    "chr7:89454076:C:T",
    "chr7:89454077:GCGTA:G",
)


# --------------------------------------------------------------------------- #
# Fixture builders                                                             #
# --------------------------------------------------------------------------- #

def _row_from_vid(vid: str) -> list[str]:
    """``chr:pos:REF:ALT`` -> a 6-field ``.bim`` row ``[chr, id, cm, bp, A1, A2]``.

    A1 is ALT and A2 is REF (``hl.export_plink`` convention, pinned in
    ``occlusion_span_filter``'s docstring), so ``len(A2)`` IS the footprint.
    """
    chrom, pos, ref, alt = vid.split(":")
    return [chrom, vid, "0", pos, alt, ref]


def _del_row(bp: int, ref_len: int, chrom: str = "chr1", vid: str | None = None):
    """A DELETION ``.bim`` row whose REF (A2) spans exactly ``ref_len`` bases."""
    assert ref_len > 1, "a deletion must have len(REF) > 1"
    filler = "ACGT" * ((ref_len // 4) + 1)
    ref = ("G" + filler)[:ref_len]
    alt = ref[0]
    return [chrom, vid or f"{chrom}:{bp}:{ref}:{alt}", "0", str(bp), alt, ref]


def _snp_row(bp: int, chrom: str = "chr1", ref: str = "T", alt: str = "C",
             vid: str | None = None):
    """A ``len(REF) == 1`` row — never an occluder."""
    return [chrom, vid or f"{chrom}:{bp}:{ref}:{alt}", "0", str(bp), alt, ref]


def _write_bim(tmp_path: Path, rows, name: str = "panel") -> Path:
    """Write a ``.bim`` (rows in file order) and return the BIM PATH.

    ⚠ The file is deliberately named ``panel.bim`` and NEVER after any variant
    id or region id, so no assertion in this file can be satisfied by the
    FILENAME rather than by the message it is checking
    (``feedback_green_assertion_needs_a_negative_control``).
    """
    path = tmp_path / f"{name}.bim"
    path.write_text(
        "".join("\t".join(str(f) for f in row) + "\n" for row in rows),
        encoding="utf-8",
    )
    return path


def _write_regions_tsv(tmp_path: Path, specs, *, ancestry: str = "AFR",
                       name: str = "regions.tsv") -> Path:
    """A ``config/ld_regions.tsv``-SHAPED manifest.

    1-based columns 1 region_id / 2 chr / 7 ancestry / 15 window_start /
    16 window_end — the exact layout ``_read_regions_tsv`` parses.
    """
    lines = []
    for region_id, chrom, start_bp, end_bp in specs:
        cells = [""] * 16
        cells[0] = region_id
        cells[1] = chrom
        cells[6] = ancestry
        cells[14] = str(start_bp)
        cells[15] = str(end_bp)
        lines.append("\t".join(cells))
    path = tmp_path / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _pairs_row(**overrides) -> dict:
    """A FULL-WIDTH ``pcs_pairs.tsv`` row: every ``TSV_COLUMNS`` field present.

    Defaults are derived from ``PairResult``'s annotations rather than
    hand-listed, so a new scanner field cannot silently make these fixtures
    short (which would trip the tool's own header check for the wrong reason).
    """
    import pairwise_completeness_scan as pcs

    ann = dict(pcs.PairResult.__annotations__)
    row: dict = {}
    for col in pcs.TSV_COLUMNS:
        raw = ann.get(col, "str")
        # ``PairResult`` is annotated under ``from __future__ import
        # annotations``, so each value is a ``ForwardRef('bool')``-style object
        # rather than the type. Reading ``__name__`` off it yields nothing and
        # would silently default every boolean to the EMPTY string, which the
        # tool then rejects for the wrong reason. Unwrap the forward ref.
        if isinstance(raw, str):
            tname = raw
        else:
            tname = getattr(raw, "__forward_arg__", None) or getattr(
                raw, "__name__", str(raw)
            )
        row[col] = {"bool": "False", "int": "0", "float": "0.0"}.get(tname, "")
    for key, value in overrides.items():
        assert key in row, f"unknown pcs_pairs column {key!r}"
        row[key] = value if isinstance(value, str) else pcs._render_field(value)
    return row


def _write_pairs_tsv(tmp_path: Path, rows, *, header=None,
                     name: str = "pcs_pairs.tsv") -> Path:
    import pairwise_completeness_scan as pcs

    cols = list(pcs.TSV_COLUMNS) if header is None else list(header)
    path = tmp_path / name
    body = ["\t".join(cols)]
    for row in rows:
        body.append("\t".join(str(row.get(c, "")) for c in list(pcs.TSV_COLUMNS)))
    path.write_text("\n".join(body) + "\n", encoding="utf-8")
    return path


def _region1_fixture(tmp_path: Path, *, drop=(), extra_pairs=()):
    """The region-1 tangle: banked ``.bim`` rows + the banked ``-6`` undefined row.

    ``drop`` removes vids from the ``.bim`` (the NEGATIVE CONTROL knob).
    """
    vids = [v for v in R1_VIDS if v not in set(drop)]
    bim = _write_bim(tmp_path, [_row_from_vid(v) for v in vids])
    regions = _write_regions_tsv(
        tmp_path, [("m2_region_00001", "chr1", 1_900_000, 8_400_000)]
    )
    pairs = [
        _pairs_row(
            region_id="m2_region_00001",
            del_index=46715, del_vid=R1_MINUS6_ANCHOR,
            del_chr="chr1", del_pos=5922724,
            partner_index=46714, partner_vid=R1_OCCLUDED, partner_pos=5922718,
            offset=-6, side="upstream", already_occluded="False",
            pair_key="46714|46715", undefined="True",
        ),
    ]
    pairs.extend(extra_pairs)
    pairs_tsv = _write_pairs_tsv(tmp_path, pairs)
    return pairs_tsv, bim, regions


def _run(module, pairs_tsv, bim, regions, **kwargs):
    return module.reclassify(pairs_tsv, bim, regions, **kwargs)


def _row_for(out_rows, pair_key):
    matches = [r for r in out_rows if r["pair_key"] == pair_key]
    assert len(matches) == 1, f"expected exactly one row for {pair_key}: {matches}"
    return matches[0]


# --------------------------------------------------------------------------- #
# 1. THE RULE HAS EXACTLY ONE IMPLEMENTATION                                   #
# --------------------------------------------------------------------------- #

def test_the_frozen_detector_is_called_not_reimplemented():
    """FUNCTION IDENTITY, never name equality.

    Functions are never interned across modules, so a forked copy of the
    occlusion rule (or of the scanner's window selection) genuinely fails this.
    A second copy of the rule is the failure mode this test exists to make
    impossible: it would drift from the FROZEN detector the day either moves.
    """
    import occlusion_span_filter as osf
    import pairwise_completeness_scan as pcs
    import pcs_panelwide_reclassify as R

    assert R.detect_occluded_variants is osf.detect_occluded_variants
    assert R.iter_bim_windows is pcs.iter_bim_windows
    assert R._read_regions_tsv is pcs._read_regions_tsv


def test_the_tool_never_opens_a_bed_or_decodes_a_genotype():
    """THE POST-HOC-ONLY PROPERTY, MACHINE-CHECKED — this is what keeps the
    ~4h20m in-flight sweep from having to be re-run.

    AST, not ``grep``: a DOCSTRING that merely MENTIONS ``.bed`` must not
    false-fire, while a ``.bed`` string literal in CODE must. Source is READ AT
    CALL TIME, so a stale ``__pycache__`` cannot defeat it
    (``feedback_negative_control_defeated_by_bytecode_cache``).
    """
    tree = ast.parse((PROJECT_ROOT / _MODULE_REL).read_text(encoding="utf-8"))

    doc_ids = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(
            node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ) and body:
            first = body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                doc_ids.add(id(first.value))

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.update(a.asname or a.name for a in node.names)
        elif isinstance(node, ast.Import):
            imported.update((a.asname or a.name).split(".")[0] for a in node.names)
    for banned in ("BedReader", "Genotypes", "MISSING_DOSAGE"):
        assert banned not in imported, f"GENOTYPE SURFACE IMPORTED: {banned}"

    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "BedReader" not in names and "BedReader" not in attrs
    assert "read_variant" not in attrs

    literals = [
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, str)
        and id(n) not in doc_ids
    ]
    assert not [s for s in literals if ".bed" in s], "BED PATH LITERAL IN CODE"
    assert any(".bim" in s for s in literals), "NO .bim LITERAL"


def test_the_in_flight_artifact_column_name_is_pinned():
    """``already_occluded`` must stay in ``TSV_COLUMNS``.

    A ~4h20m sweep is MID-FLIGHT on this scanner and will emit a header
    carrying this exact column. Renaming it would desynchronize this tool's
    strict header check from the artifact it is built to read. Tuple membership
    on a structured object — never a substring grep over source text.
    """
    import pairwise_completeness_scan as pcs

    assert "already_occluded" in pcs.TSV_COLUMNS
    assert pcs.TSV_COLUMNS == pcs.PairResult._fields


# --------------------------------------------------------------------------- #
# 2. THE SOUNDNESS ARGUMENT'S OWN NEGATIVE CONTROL                             #
# --------------------------------------------------------------------------- #

def test_occlusion_is_monotone_in_the_row_set():
    """``R subset-of R'`` implies ``occluded(v, R) => occluded(v, R')``.

    Demonstrated by EXHIBITING the flip: the SNP is NOT occluded on the subset
    and IS occluded once the covering deletion is added. That is precisely why
    an OCCLUDED verdict on a subset is SOUND while a NOT-OCCLUDED verdict on a
    subset is NOT — and therefore why every not-occluded verdict this tool
    emits must carry the row set it is relative to.
    """
    import pcs_panelwide_reclassify as R

    snp = _snp_row(1005, vid="chr1:1005:T:C")
    non_covering = _del_row(1010, 3)          # span 1010-1012, never reaches 1005
    covering = _del_row(1000, 7)              # span 1000-1006, covers 1005

    subset_ids, _ = R.detect_occluded_variants([snp, non_covering])
    superset_ids, _ = R.detect_occluded_variants([covering, snp, non_covering])

    assert "chr1:1005:T:C" not in subset_ids
    assert "chr1:1005:T:C" in superset_ids
    assert set(subset_ids) <= set(superset_ids)


# --------------------------------------------------------------------------- #
# 3. THE KNOWN ANSWER, AND THE CONTROL THAT FLIPS IT                           #
# --------------------------------------------------------------------------- #

def test_the_region1_tangle_is_reclassified_member_occluded(tmp_path):
    """The banked ``46714|46715`` row carries ``already_occluded == False`` —
    and its partner is nonetheless on the PRODUCTION excludelist.

    This is FINDING A, exhibited on real banked coordinates: the anchor
    (``5922724``) never reaches the SNP, so the ANCHOR-RELATIVE field is False;
    a DIFFERENT deletion (``5922716``, span 5922716-5922722) covers it, so the
    panel-wide verdict is occluded and the pair never reaches the matrix.
    """
    import pcs_panelwide_reclassify as R

    pairs_tsv, bim, regions = _region1_fixture(tmp_path)
    out_rows, summary = _run(R, pairs_tsv, bim, regions)

    row = _row_for(out_rows, "46714|46715")
    assert row["already_occluded"] is False, "the banked input row must be False"
    assert row["partner_occluded_panelwide"] is True
    assert row["del_occluded_panelwide"] is False
    assert row["partner_occluding_deletion_id"] == R1_OCCLUDER
    assert row["occluding_deletion_id"] == R1_OCCLUDER
    assert row["pair_reaches_matrix"] is False

    assert summary["pooled"]["n_pairs_member_occluded_panelwide"] == 1
    assert summary["pooled"]["n_pairs_neither_member_occluded_panelwide"] == 0
    assert R1_OCCLUDED in summary["pooled"]["occluded_member_vids"]


def test_dropping_the_occluding_deletion_flips_the_region1_verdict(tmp_path):
    """NEGATIVE CONTROL for the known answer above.

    Remove ONLY ``chr1:5922716:ACGGTGG:A`` from the ``.bim`` and the SAME pair
    classifies neither-member-occluded. A green above is evidence only because
    this red exists.
    """
    import pcs_panelwide_reclassify as R

    pairs_tsv, bim, regions = _region1_fixture(
        tmp_path, drop=(R1_OCCLUDER,)
    )
    out_rows, summary = _run(R, pairs_tsv, bim, regions)

    row = _row_for(out_rows, "46714|46715")
    assert row["partner_occluded_panelwide"] is False
    assert row["del_occluded_panelwide"] is False
    assert row["occluding_deletion_id"] == ""
    assert row["pair_reaches_matrix"] is True
    assert summary["pooled"]["n_pairs_member_occluded_panelwide"] == 0
    assert summary["pooled"]["n_pairs_neither_member_occluded_panelwide"] == 1


def test_the_two_unknown_pairs_classify_as_neither_on_the_banked_subset(tmp_path):
    """The ``-3`` (region 8) and ``-1`` (region 149) pairs, and their SCOPE.

    Both classify neither-occluded ON THE BANKED SUBSET — which the
    monotonicity asymmetry says is NOT a panel-wide answer. The summary must
    therefore carry the row set the verdict is relative to: a literal
    ``verdict_scope`` sentence plus ``bim_n_lines`` and per-region
    ``n_rows_in_window``.
    """
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    bim = _write_bim(tmp, [_row_from_vid(v) for v in R8_VIDS + R149_VIDS])
    regions = _write_regions_tsv(tmp, [
        ("m2_region_00008", "chr1", 155_800_000, 155_900_000),
        ("m2_region_00149", "chr7", 89_400_000, 89_500_000),
    ])
    pairs_tsv = _write_pairs_tsv(tmp, [
        _pairs_row(
            region_id="m2_region_00008",
            del_index=924401, del_vid="chr1:155856785:AAAG:A", del_pos=155856785,
            partner_index=924402, partner_vid=R8_VIDS[0], partner_pos=155856782,
            offset=-3, side="upstream", already_occluded="False",
            pair_key="924401|924402", undefined="True",
        ),
        _pairs_row(
            region_id="m2_region_00149",
            del_index=9776035, del_vid="chr7:89454077:GCGTA:G", del_pos=89454077,
            partner_index=9776036, partner_vid="chr7:89454076:C:T",
            partner_pos=89454076,
            offset=-1, side="upstream", already_occluded="False",
            pair_key="9776035|9776036", undefined="True",
        ),
    ])
    out_rows, summary = _run(R, pairs_tsv, bim, regions)

    for key in ("924401|924402", "9776035|9776036"):
        row = _row_for(out_rows, key)
        assert row["del_occluded_panelwide"] is False
        assert row["partner_occluded_panelwide"] is False
        assert row["pair_reaches_matrix"] is True

    assert summary["pooled"]["n_pairs_neither_member_occluded_panelwide"] == 2
    assert summary["pooled"]["n_pairs_member_occluded_panelwide"] == 0

    prov = summary["provenance"]
    assert isinstance(prov["verdict_scope"], str) and prov["verdict_scope"].strip()
    flat = " ".join(prov["verdict_scope"].split())
    assert "NOT-OCCLUDED" in flat or "not-occluded" in flat
    assert prov["bim_n_lines"] == len(R8_VIDS) + len(R149_VIDS)
    assert prov["region_ids"] == ["m2_region_00008", "m2_region_00149"]
    assert prov["n_rows_in_window_per_region"] == {
        "m2_region_00008": 3, "m2_region_00149": 2
    }
    assert summary["per_region"]["m2_region_00008"]["n_rows_in_window"] == 3


# --------------------------------------------------------------------------- #
# 4. HANDING IT THE WRONG INPUTS IS LOUD                                       #
# --------------------------------------------------------------------------- #

def test_a_pair_member_missing_from_the_bim_raises_naming_the_vid_and_region(tmp_path):
    """A member absent from the region window is a WRONG-``.bim`` tell.

    It must RAISE naming BOTH the vid and the region — never be reported as a
    quiet ``genuine residual``. ⚠ The fixture file is named ``panel.bim`` and
    the region-bearing manifest ``regions.tsv``, so NEITHER filename can
    satisfy either half of the assertion.
    """
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    absent = "chr1:4242424:G:T"
    present_del = "chr1:4242400:GACGT:G"
    bim = _write_bim(tmp, [_del_row(4242400, 5, vid=present_del), _snp_row(4242500)])
    regions = _write_regions_tsv(tmp, [("m2_region_00777", "chr1", 4_242_000, 4_243_000)])
    pairs_tsv = _write_pairs_tsv(tmp, [
        _pairs_row(
            region_id="m2_region_00777",
            del_index=1, del_vid=present_del, del_pos=4242400,
            partner_index=2, partner_vid=absent, partner_pos=4242424,
            offset=0, side="interior", already_occluded="False",
            pair_key="1|2", undefined="True",
        ),
    ])
    with pytest.raises(ValueError) as exc:
        _run(R, pairs_tsv, bim, regions)
    message = str(exc.value)
    assert absent in message
    assert "m2_region_00777" in message


def test_a_drifted_pairs_tsv_header_raises(tmp_path):
    """A header that is not EXACTLY ``TSV_COLUMNS`` means the artifact was not
    produced by this scanner, so its pair semantics are unverified.

    Both directions are exercised: the drifted header RAISES naming the
    mismatch, and the exact header parses clean.
    """
    import pairwise_completeness_scan as pcs
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    bim = _write_bim(tmp, [_row_from_vid(v) for v in R149_VIDS])
    regions = _write_regions_tsv(tmp, [("m2_region_00149", "chr7", 89_400_000, 89_500_000)])
    good_row = _pairs_row(
        region_id="m2_region_00149",
        del_index=9776035, del_vid="chr7:89454077:GCGTA:G", del_pos=89454077,
        partner_index=9776036, partner_vid="chr7:89454076:C:T", partner_pos=89454076,
        offset=-1, side="upstream", already_occluded="False",
        pair_key="9776035|9776036", undefined="True",
    )

    drifted = list(pcs.TSV_COLUMNS)
    drifted[drifted.index("already_occluded")] = "occluded_already"
    bad = _write_pairs_tsv(tmp, [good_row], header=drifted, name="drifted.tsv")
    with pytest.raises(ValueError) as exc:
        _run(R, bad, bim, regions)
    assert "occluded_already" in str(exc.value)

    good = _write_pairs_tsv(tmp, [good_row], name="good.tsv")
    out_rows, _summary = _run(R, good, bim, regions)
    assert len(out_rows) == 1


def test_a_missing_bim_raises_naming_the_missing_file(tmp_path):
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    regions = _write_regions_tsv(tmp, [("m2_region_00149", "chr7", 1, 2)])
    pairs_tsv = _write_pairs_tsv(tmp, [])
    with pytest.raises(FileNotFoundError) as exc:
        _run(R, pairs_tsv, tmp / "nope.bim", regions)
    assert "nope.bim" in str(exc.value)


def test_a_region_in_the_pairs_tsv_but_not_in_the_manifest_raises(tmp_path):
    """No silent drop: an undefined row whose region the manifest does not carry
    (wrong ancestry, wrong manifest) RAISES naming the region."""
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    bim = _write_bim(tmp, [_row_from_vid(v) for v in R149_VIDS])
    regions = _write_regions_tsv(tmp, [("m2_region_00149", "chr7", 89_400_000, 89_500_000)])
    pairs_tsv = _write_pairs_tsv(tmp, [
        _pairs_row(
            region_id="m2_region_00999",
            del_index=1, del_vid="chr7:89454077:GCGTA:G", del_pos=89454077,
            partner_index=2, partner_vid="chr7:89454076:C:T", partner_pos=89454076,
            offset=-1, side="upstream", already_occluded="False",
            pair_key="1|2", undefined="True",
        ),
    ])
    with pytest.raises(ValueError) as exc:
        _run(R, pairs_tsv, bim, regions)
    assert "m2_region_00999" in str(exc.value)


def test_out_of_scope_rows_are_counted_and_named_when_region_ids_narrows_the_run(tmp_path):
    """A DELIBERATE narrowing is not a silent drop: the skipped rows are counted
    and their region ids are NAMED."""
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    bim = _write_bim(tmp, [_row_from_vid(v) for v in R8_VIDS + R149_VIDS])
    regions = _write_regions_tsv(tmp, [
        ("m2_region_00008", "chr1", 155_800_000, 155_900_000),
        ("m2_region_00149", "chr7", 89_400_000, 89_500_000),
    ])
    pairs_tsv = _write_pairs_tsv(tmp, [
        _pairs_row(
            region_id="m2_region_00008",
            del_index=924401, del_vid="chr1:155856785:AAAG:A", del_pos=155856785,
            partner_index=924402, partner_vid=R8_VIDS[0], partner_pos=155856782,
            offset=-3, side="upstream", already_occluded="False",
            pair_key="924401|924402", undefined="True",
        ),
        _pairs_row(
            region_id="m2_region_00149",
            del_index=9776035, del_vid="chr7:89454077:GCGTA:G", del_pos=89454077,
            partner_index=9776036, partner_vid="chr7:89454076:C:T", partner_pos=89454076,
            offset=-1, side="upstream", already_occluded="False",
            pair_key="9776035|9776036", undefined="True",
        ),
    ])
    _out, summary = _run(R, pairs_tsv, bim, regions, region_ids=["m2_region_00008"])
    assert summary["pooled"]["n_undefined_rows_in"] == 1
    assert summary["pooled"]["n_undefined_rows_out_of_scope"] == 1
    assert summary["provenance"]["region_ids_out_of_scope"] == ["m2_region_00149"]


def test_an_empty_region_ids_value_is_an_error_not_a_full_scan(tmp_path):
    """Mirrors the scanner's own ruling: ``--region-ids ' , '`` names no id and
    is an ERROR (exit 2), NOT a silent all-region scan."""
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    bim = _write_bim(tmp, [_row_from_vid(v) for v in R149_VIDS])
    regions = _write_regions_tsv(tmp, [("m2_region_00149", "chr7", 89_400_000, 89_500_000)])
    pairs_tsv = _write_pairs_tsv(tmp, [])
    code = R.main([
        "--pairs-tsv", str(pairs_tsv),
        "--bfile-prefix", str(bim.with_suffix("")),
        "--regions-tsv", str(regions),
        "--region-ids", " , ",
        "--out", str(tmp / "o.tsv"),
        "--summary", str(tmp / "o.json"),
    ])
    assert code == 2
    assert not (tmp / "o.tsv").exists()


# --------------------------------------------------------------------------- #
# 5. VID-KEYED OCCLUSION vs INDEX-KEYED PAIRS — BOTH LIVE IN ONE FIXTURE       #
# --------------------------------------------------------------------------- #

def test_pair_rollups_are_pair_key_keyed_while_occlusion_is_vid_keyed(tmp_path):
    """Two conventions, both correct, answering different questions.

    ``--exclude`` consumes col-2 IDS and drops EVERY row carrying a duplicated
    id, so the occlusion verdict is VID-keyed and MATCHES PRODUCTION. Pair
    rollups stay INDEX-keyed (``_pair_key``) because two rows sharing a ``.``
    id are DISTINCT pairs. The ambiguity a duplicated id creates is
    PRODUCTION'S — it is surfaced and NAMED, never ``fixed`` by switching the
    occlusion verdict to indices.
    """
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    bim = _write_bim(tmp, [
        _del_row(1000, 7, vid="chr1:1000:ACGGTGG:A"),   # span 1000-1006
        _snp_row(1002, vid="."),                        # OCCLUDED, id "."
        _snp_row(1900, vid="."),                        # NOT occluded, same id
    ])
    regions = _write_regions_tsv(tmp, [("m2_region_00042", "chr1", 900, 2000)])
    pairs_tsv = _write_pairs_tsv(tmp, [
        _pairs_row(
            region_id="m2_region_00042",
            del_index=10, del_vid="chr1:1000:ACGGTGG:A", del_pos=1000,
            partner_index=11, partner_vid=".", partner_pos=1002,
            offset=0, side="interior", already_occluded="True",
            pair_key="10|11", undefined="True",
        ),
        _pairs_row(
            region_id="m2_region_00042",
            del_index=10, del_vid="chr1:1000:ACGGTGG:A", del_pos=1000,
            partner_index=12, partner_vid=".", partner_pos=1900,
            offset=893, side="downstream", already_occluded="False",
            pair_key="10|12", undefined="True",
        ),
    ])
    out_rows, summary = _run(R, pairs_tsv, bim, regions)

    # INDEX-keyed pair rollup: two DISTINCT pairs, never collapsed to one.
    assert summary["pooled"]["n_undefined_distinct_pairs_in"] == 2

    # VID-keyed occlusion: BOTH rows carry the occluded id, so BOTH are dropped
    # by `--exclude`. Switching to indices would call the second one retained
    # and CONTRADICT production.
    for key in ("10|11", "10|12"):
        assert _row_for(out_rows, key)["partner_occluded_panelwide"] is True
        assert _row_for(out_rows, key)["member_id_ambiguous"] is True
    assert summary["pooled"]["n_pairs_member_occluded_panelwide"] == 2

    assert summary["pooled"]["n_pairs_with_ambiguous_member_id"] == 2
    assert summary["pooled"]["ambiguous_member_ids"] == ["."]


# --------------------------------------------------------------------------- #
# 6. THE COUNTS RECONCILE OR THE TOOL STOPS                                    #
# --------------------------------------------------------------------------- #

def test_the_two_counts_reconcile_or_the_tool_raises(tmp_path, monkeypatch):
    """A count is a claim: it reconciles arithmetically or it stops.

    Green half: ``member_occluded + neither == n_undefined_distinct_pairs_in``
    and the ROW twin. Red half: a monkeypatched inconsistency in the
    MODULE-GLOBAL pair counter must RAISE naming both sides.
    """
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    pairs_tsv, bim, regions = _region1_fixture(tmp)
    _out, summary = _run(R, pairs_tsv, bim, regions)
    pooled = summary["pooled"]
    assert (
        pooled["n_pairs_member_occluded_panelwide"]
        + pooled["n_pairs_neither_member_occluded_panelwide"]
        == pooled["n_undefined_distinct_pairs_in"]
    )
    assert (
        pooled["n_rows_member_occluded_panelwide"]
        + pooled["n_rows_neither_member_occluded_panelwide"]
        == pooled["n_undefined_rows_in"]
    )

    monkeypatch.setattr(R, "_count_distinct_pairs", lambda rows: 999)
    with pytest.raises(ValueError) as exc:
        _run(R, pairs_tsv, bim, regions)
    assert "999" in str(exc.value)


def test_the_third_tier_subtracts_the_globally_invariant_members(tmp_path):
    """The ``--mac 1`` side, subtracted WITHOUT collapsing the tier above it.

    A pair whose member is globally invariant lands OUTSIDE the strictest tier
    while STILL being counted in ``n_pairs_neither_member_occluded_panelwide``.
    Both are emitted; neither is collapsed into the other.
    """
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    bim = _write_bim(tmp, [_row_from_vid(v) for v in R149_VIDS])
    regions = _write_regions_tsv(tmp, [("m2_region_00149", "chr7", 89_400_000, 89_500_000)])
    pairs_tsv = _write_pairs_tsv(tmp, [
        _pairs_row(
            region_id="m2_region_00149",
            del_index=9776035, del_vid="chr7:89454077:GCGTA:G", del_pos=89454077,
            partner_index=9776036, partner_vid="chr7:89454076:C:T",
            partner_pos=89454076,
            offset=-1, side="upstream", already_occluded="False",
            pair_key="9776035|9776036", undefined="True",
            partner_globally_invariant="True",
        ),
    ])
    _out, summary = _run(R, pairs_tsv, bim, regions)
    pooled = summary["pooled"]
    assert pooled["n_pairs_neither_member_occluded_panelwide"] == 1
    assert pooled["n_pairs_neither_occluded_and_no_globally_invariant_member"] == 0


def test_only_undefined_rows_are_reclassified(tmp_path):
    """DEFINED rows in the input are ignored, and both counts are reported so a
    reader can never mistake one basis for the other."""
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    extra_defined = _pairs_row(
        region_id="m2_region_00001",
        del_index=46713, del_vid=R1_OCCLUDER, del_pos=5922716,
        partner_index=46714, partner_vid=R1_OCCLUDED, partner_pos=5922718,
        offset=0, side="interior", already_occluded="True",
        pair_key="46713|46714", undefined="False",
    )
    pairs_tsv, bim, regions = _region1_fixture(tmp, extra_pairs=(extra_defined,))
    out_rows, summary = _run(R, pairs_tsv, bim, regions)

    assert len(out_rows) == 1
    assert summary["pooled"]["n_rows_in_tsv"] == 2
    assert summary["pooled"]["n_undefined_rows_in"] == 1
    assert summary["pooled"]["n_defined_rows_in"] == 1
    assert all(r["pair_key"] != "46713|46714" for r in out_rows)


# --------------------------------------------------------------------------- #
# 7. THE EMITTED SHAPE IS PINNED EXACTLY                                       #
# --------------------------------------------------------------------------- #

def test_summary_key_sets_are_exact(tmp_path):
    """EXACT equality on every key set, and ``region_ids`` is a NAMED list.

    A COUNT of 21 regions is satisfiable by the WRONG 21; a named list is not.
    The expected key sets are written out LITERALLY here rather than pulled
    from the module, so this test cannot be satisfied by the module changing
    its own constant.
    """
    import pcs_panelwide_reclassify as R

    tmp = tmp_path
    pairs_tsv, bim, regions = _region1_fixture(tmp)
    _out, summary = _run(R, pairs_tsv, bim, regions)

    assert set(summary) == {"provenance", "pooled", "per_region"}
    assert set(summary["provenance"]) == {
        "pairs_tsv_path", "pairs_tsv_sha256", "pairs_tsv_n_lines",
        "bim_path", "bim_sha256", "bim_n_lines",
        "regions_tsv_path", "regions_tsv_sha256",
        "ancestry", "region_ids", "region_ids_selected",
        "region_ids_out_of_scope", "n_rows_in_window_per_region",
        "verdict_scope",
    }
    assert set(summary["pooled"]) == {
        "n_rows_in_tsv", "n_defined_rows_in", "n_undefined_rows_in",
        "n_undefined_distinct_pairs_in", "n_undefined_rows_out_of_scope",
        "n_rows_member_occluded_panelwide",
        "n_rows_neither_member_occluded_panelwide",
        "n_pairs_member_occluded_panelwide",
        "n_pairs_neither_member_occluded_panelwide",
        "n_pairs_neither_occluded_and_no_globally_invariant_member",
        "n_pairs_with_ambiguous_member_id", "ambiguous_member_ids",
        "occluded_member_vids",
    }
    assert set(summary["per_region"]["m2_region_00001"]) == {
        "region_id", "chrom", "start_bp", "end_bp",
        "n_rows_in_window", "n_occluded_ids_in_window",
        "n_undefined_rows_in", "n_undefined_distinct_pairs_in",
        "n_rows_member_occluded_panelwide",
        "n_rows_neither_member_occluded_panelwide",
        "n_pairs_member_occluded_panelwide",
        "n_pairs_neither_member_occluded_panelwide",
        "n_pairs_neither_occluded_and_no_globally_invariant_member",
        "n_pairs_with_ambiguous_member_id", "ambiguous_member_ids",
    }
    # The module's own constants must AGREE with the literals above.
    assert set(R.PROVENANCE_KEYS) == set(summary["provenance"])
    assert set(R.POOLED_KEYS) == set(summary["pooled"])
    assert set(R.PER_REGION_KEYS) == set(summary["per_region"]["m2_region_00001"])
    assert summary["provenance"]["region_ids"] == ["m2_region_00001"]


def test_the_cli_writes_both_artifacts_and_the_parser_is_the_declared_contract(tmp_path):
    """``_build_parser`` / ``main`` mirror ``pairwise_completeness_scan:1343``.

    ⚠ ``_build_parser`` is a DECLARED CROSS-TASK CONTRACT: the staged-doc gate
    feeds the STAGED argv to this exact function, so a differently-named
    builder would break that gate with ``AttributeError`` instead of catching a
    staged typo.
    """
    import argparse

    import pcs_panelwide_reclassify as R

    assert isinstance(R._build_parser(), argparse.ArgumentParser)

    tmp = tmp_path
    pairs_tsv, bim, regions = _region1_fixture(tmp)
    out = tmp / "reclass.tsv"
    summary_path = tmp / "reclass.json"
    code = R.main([
        "--pairs-tsv", str(pairs_tsv),
        "--bfile-prefix", str(bim.with_suffix("")),
        "--regions-tsv", str(regions),
        "--ancestry", "AFR",
        "--out", str(out),
        "--summary", str(summary_path),
    ])
    assert code == 0
    header = out.read_text(encoding="utf-8").splitlines()[0].split("\t")
    assert tuple(header) == tuple(R.OUT_COLUMNS)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["pooled"]["n_pairs_member_occluded_panelwide"] == 1


def test_the_window_selection_uses_pad_bp_zero_to_match_production():
    """``pad_bp=0`` is LOAD-BEARING: production's excludelist row set is EXACTLY
    the in-window rows for ``[from_bp, to_bp]`` (``run_native_ld_panel.py``
    851-878, no padding). Any other pad answers a DIFFERENT question.

    Checked on the parsed call, not on source text.
    """
    tree = ast.parse((PROJECT_ROOT / _MODULE_REL).read_text(encoding="utf-8"))
    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "iter_bim_windows"
    ]
    assert calls, "iter_bim_windows is never called"
    for call in calls:
        pads = [k for k in call.keywords if k.arg == "pad_bp"]
        assert len(pads) == 1, "pad_bp must be passed EXPLICITLY"
        assert isinstance(pads[0].value, ast.Constant)
        assert pads[0].value.value == 0
