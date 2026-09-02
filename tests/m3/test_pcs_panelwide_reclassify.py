"""RED-first tests for src/python/pcs_panelwide_reclassify.py (quick-260831-kw8).

WHAT THE MODULE UNDER TEST ANSWERS
----------------------------------
``pairwise_completeness_scan``'s ``already_occluded`` is ANCHOR-RELATIVE — it is
``deletion.pos < partner.pos <= deletion.span_end`` against THE ANCHOR DELETION
ONLY (in ``pairwise_completeness_scan.enumerate_candidates`` — the SYMBOL, not a
line number, which decays silently). The PRODUCTION excludelist is a
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
import re
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


def _region1_fixture(tmp_path: Path, *, drop=(), extra_pairs=(), extra_bim=()):
    """The region-1 tangle: banked ``.bim`` rows + the banked ``-6`` undefined row.

    ``drop`` removes vids from the ``.bim`` (the NEGATIVE CONTROL knob).
    ``extra_bim`` APPENDS raw ``.bim`` rows (6-field sequences) so a CLEAN,
    un-occluded pair can live in the same window as the tangle — every banked
    ``R1_VIDS`` pair is an occlusion tangle by construction, so a POST-filter
    case cannot be built out of them.
    """
    vids = [v for v in R1_VIDS if v not in set(drop)]
    bim = _write_bim(tmp_path, [_row_from_vid(v) for v in vids] + list(extra_bim))
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


#: THE IMPORT ALLOWLIST. A blacklist decays the moment someone adds a surface
#: nobody thought to ban; a SUBSET check does not. Everything reachable from this
#: module must be stdlib-and-two-siblings, so the set is small enough to enumerate
#: and any addition is a deliberate, reviewable act rather than an omission.
_ALLOWED_IMPORT_ROOTS = frozenset({
    "__future__", "argparse", "csv", "hashlib", "json", "sys",
    "collections", "pathlib",
    "occlusion_span_filter", "pairwise_completeness_scan",
})

#: Banned in CODE (docstrings exempt). ``.bed`` / ``.fam`` are the genotype
#: surface; the three URL schemes are the network surface.
_BANNED_CODE_LITERALS = (".bed", ".fam", "gs://", "http://", "https://")

#: Banned as a NAME or an ATTRIBUTE anywhere: process spawning and sockets.
_BANNED_SYMBOLS = ("BedReader", "subprocess", "socket", "urlopen", "Popen", "system")


def _docstring_constant_ids(tree):
    """``id()`` of every Module/Function/Class DOCSTRING constant node."""
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
    return doc_ids


def _assert_no_genotype_or_network_surface(text: str) -> None:
    """THE POST-HOC-ONLY PROPERTY, driven by SOURCE TEXT so it can be perturbed.

    Takes TEXT rather than a path so the negative controls below can drive it
    with injected sources held IN MEMORY -- no file is written and no stale
    ``__pycache__`` can decide the outcome
    (``feedback_negative_control_defeated_by_bytecode_cache``).

    AST, never ``grep``: a DOCSTRING that merely MENTIONS ``.bed`` must not
    false-fire, while a ``.bed`` literal in CODE must.

    ⚠ THE IMPORT CHECK IS AN ALLOWLIST, NOT A BLACKLIST. The banned-name list is
    RETAINED (it names the specific surfaces this project has actually reached
    for), but the load-bearing assertion is that the imported module roots are a
    SUBSET of :data:`_ALLOWED_IMPORT_ROOTS`. A blacklist is only as good as the
    imagination of whoever wrote it and decays silently on the first surface
    nobody enumerated; a subset check is closed under future additions. Imports
    are collected by ``ast.walk``, i.e. ANYWHERE in the module -- strictly
    stronger than top-level only, so a function-local import cannot slip past.
    """
    tree = ast.parse(text)
    doc_ids = _docstring_constant_ids(tree)

    imported_names = set()
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported_names.update(a.asname or a.name for a in node.names)
            imported_roots.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add((alias.asname or alias.name).split(".")[0])
                imported_roots.add(alias.name.split(".")[0])

    for banned in ("BedReader", "Genotypes", "MISSING_DOSAGE"):
        assert banned not in imported_names, f"GENOTYPE SURFACE IMPORTED: {banned}"

    extra = sorted(imported_roots - _ALLOWED_IMPORT_ROOTS)
    assert not extra, (
        f"IMPORT OUTSIDE THE ALLOWLIST: {extra}. This tool reads an emitted "
        f"pcs_pairs.tsv, a .bim and a region manifest and NOTHING ELSE; a new "
        f"import is a new surface and must be added to the allowlist "
        f"deliberately, not discovered later. Allowed: "
        f"{sorted(_ALLOWED_IMPORT_ROOTS)}"
    )
    assert imported_roots, "no imports were collected -- this check is vacuous"

    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for banned in _BANNED_SYMBOLS:
        assert banned not in names, f"BANNED SYMBOL REFERENCED AS A NAME: {banned}"
        assert banned not in attrs, f"BANNED SYMBOL REFERENCED AS AN ATTRIBUTE: {banned}"
    assert "read_variant" not in attrs

    literals = [
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, str)
        and id(n) not in doc_ids
    ]
    for banned in _BANNED_CODE_LITERALS:
        offending = [s for s in literals if banned in s]
        assert not offending, (
            f"BANNED LITERAL {banned!r} IN CODE (not a docstring): {offending[:2]}"
        )
    assert any(".bim" in s for s in literals), "NO .bim LITERAL"


def test_the_tool_never_opens_a_bed_or_decodes_a_genotype():
    """THE POST-HOC-ONLY PROPERTY, MACHINE-CHECKED — this is what keeps the
    ~4h20m sweep from having to be re-run: the sweep's OUTPUT is this tool's
    INPUT.

    Source is READ AT CALL TIME. The assertions live in
    :func:`_assert_no_genotype_or_network_surface`, which
    :func:`test_the_surface_gate_fails_on_an_injected_surface` drives RED in
    three directions.
    """
    _assert_no_genotype_or_network_surface(
        (PROJECT_ROOT / _MODULE_REL).read_text(encoding="utf-8")
    )


def test_the_surface_gate_fails_on_an_injected_surface():
    """THREE IN-MEMORY NEGATIVE CONTROLS. Green above is evidence only because
    these reds exist (``feedback_green_assertion_needs_a_negative_control``).

    Each perturbation asserts that it CHANGED the text and — for the two that
    claim to land in CODE — that it landed inside a ``FunctionDef`` byte span.
    A control that is vacuous is worse than no control
    (the M7 trap: a first-match ``text.replace`` lands in a DOCSTRING).
    """
    text = (PROJECT_ROOT / _MODULE_REL).read_text(encoding="utf-8")
    _assert_no_genotype_or_network_surface(text)  # the baseline is GREEN

    # (1) ALLOWLIST VIOLATION — a surface nobody thought to blacklist.
    numpy_injected = text.replace(
        "from __future__ import annotations",
        "from __future__ import annotations\n\nimport numpy",
        1,
    )
    assert numpy_injected != text and "import numpy" in numpy_injected
    with pytest.raises(AssertionError) as exc_import:
        _assert_no_genotype_or_network_surface(numpy_injected)
    assert "ALLOWLIST" in str(exc_import.value) and "numpy" in str(exc_import.value)

    # (2) A `.bed` PATH LITERAL IN A FUNCTION BODY — never in a docstring.
    bed_injected = _inject_into_a_function_body(
        text, 'genotypes = "/home/jupyter/afr_cohort.bed"'
    )
    with pytest.raises(AssertionError) as exc_bed:
        _assert_no_genotype_or_network_surface(bed_injected)
    assert ".bed" in str(exc_bed.value)

    # (3) A `BedReader` ATTRIBUTE REFERENCE IN A FUNCTION BODY.
    reader_injected = _inject_into_a_function_body(
        text, "reader = _plink.BedReader"
    )
    with pytest.raises(AssertionError) as exc_reader:
        _assert_no_genotype_or_network_surface(reader_injected)
    assert "BedReader" in str(exc_reader.value)


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


def test_defined_rows_below_the_tail_are_counted_but_not_emitted(tmp_path):
    """DEFINED rows BELOW the tail produce no output row, and both counts are
    reported so a reader can never mistake one basis for the other.

    RENAMED from ``test_only_undefined_rows_are_reclassified``: defined rows are
    no longer ignored -- the ones in the ``lost_frac >= 0.9`` TAIL are classified
    and emitted (see section 9), and every defined row feeds the informative-
    carrier distribution. What stays true, and is what this test now pins, is
    that emission remains BOUNDED: a below-tail defined row is COUNTED, never
    EMITTED. ``n_defined_rows_in`` keeps its exact name and semantics.
    """
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
        # -- THE BANKED THIRTEEN. Names and semantics FROZEN. ---------------- #
        "n_rows_in_tsv", "n_defined_rows_in", "n_undefined_rows_in",
        "n_undefined_distinct_pairs_in", "n_undefined_rows_out_of_scope",
        "n_rows_member_occluded_panelwide",
        "n_rows_neither_member_occluded_panelwide",
        "n_pairs_member_occluded_panelwide",
        "n_pairs_neither_member_occluded_panelwide",
        "n_pairs_neither_occluded_and_no_globally_invariant_member",
        "n_pairs_with_ambiguous_member_id", "ambiguous_member_ids",
        "occluded_member_vids",
        # -- THE TAIL SCOPE, ADDED BESIDE THEM (quick-260901-rvu). ----------- #
        "tail_min_carriers_lost_frac",
        "n_tail_rows_in", "n_tail_rows_out_of_scope",
        "n_tail_distinct_pairs_in",
        "n_tail_rows_member_occluded_panelwide",
        "n_tail_rows_neither_member_occluded_panelwide",
        "n_tail_pairs_member_occluded_panelwide",
        "n_tail_pairs_neither_member_occluded_panelwide",
        "n_tail_regions_with_rows",
        "n_defined_rows_out_of_scope",
        "n_defined_rows_member_occluded_panelwide",
        "n_defined_rows_reaching_matrix",
        "n_defined_rows_rarer_and_min_definitions_disagree",
        "informative_carriers_percentiles_defined_rows",
        "informative_carriers_percentiles_defined_rows_reaching_matrix",
        "informative_carriers_low_tail_defined_rows",
        "informative_carriers_low_tail_defined_rows_reaching_matrix",
        "no_floor_notice", "tail_verdict_scope",
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
        "n_defined_rows_in", "n_defined_rows_reaching_matrix",
        "n_tail_rows_in", "n_tail_distinct_pairs_in",
        "n_tail_rows_member_occluded_panelwide",
        "n_tail_rows_neither_member_occluded_panelwide",
        "n_tail_pairs_member_occluded_panelwide",
        "n_tail_pairs_neither_member_occluded_panelwide",
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


# --------------------------------------------------------------------------- #
# THE MITIGATION IS DISCHARGED (quick-260901-l55).                              #
#                                                                              #
# quick-260831-kw8 put the TRUE semantics HERE, in section (1b) of              #
# pcs_panelwide_reclassify.py's docstring, because the scanner's own docstring  #
# still carried the false claim and could not be corrected: the live runbook's  #
# STEP 0 gate pinned the scanner's WHOLE-FILE md5 and byte size, so deleting a  #
# known falsehood cost an edit to a runbook that was a TRUE statement about an  #
# in-flight sweep. That note was written SELF-INVALIDATING on purpose -- its    #
# claims about the scanner were recomputed from disk -- so that it would go RED #
# and force its own removal the moment the parked patch landed. It did exactly  #
# that, and this is that removal.                                              #
#                                                                              #
# WHAT CHANGED: the gate was rescoped OFF the byte proxy onto a git-ref CODE    #
# pin (assert_code_frozen against cb199b6), so a docstring correction now costs #
# NOTHING -- MEASURED: the parked patch moved the scanner's md5 and 5,071 bytes #
# and left the CODE PIN green, both sides 540 code lines. The correction then   #
# landed in the scanner itself. Section (1b) is DELETED; its true semantics     #
# survive in section (1), which this test still enforces.                       #
#                                                                              #
# THIS TEST STAYS LIVE AGAINST ANOTHER FILE. Claim (3) below reads the SCANNER  #
# on disk and requires the correction to be PRESENT and the false sentence      #
# ABSENT, so the two docstrings cannot drift back apart silently. Sources are   #
# read at CALL TIME and parsed with ast, never imported                         #
# (feedback_negative_control_defeated_by_bytecode_cache).                       #
# --------------------------------------------------------------------------- #

#: The sentence the scanner used to carry. It was FALSE (`already_occluded` is
#: ANCHOR-RELATIVE, the excludelist is PANEL-WIDE) and it is now a REQUIRED
#: ABSENCE, not a required presence.
_SCANNER_FALSE_CLAIM = "already visible as ``already_occluded``"


def test_the_tool_and_the_scanner_agree_that_already_occluded_is_anchor_relative():
    """The correction is in BOTH docstrings, and the deferral framing is GONE.

    ⚠ WHITESPACE IS NORMALISED FIRST -- both docstrings wrap at ~79 chars, so an
    un-normalised phrase match would fail on a merely line-WRAPPED copy
    (`feedback_grep_gate_matches_text_not_meaning`). Sources are READ AT CALL
    TIME and parsed with :mod:`ast`, never imported, so a stale ``__pycache__``
    cannot decide the outcome
    (`feedback_negative_control_defeated_by_bytecode_cache`).

    REPLACES
    ``test_the_tool_docstring_carries_the_true_semantics_and_flags_the_scanners_false_claim``,
    whose claims (2) and (5) -- that the scanner STILL carries the false sentence,
    and that the runbook pins the scanner's md5 and byte size -- are both false as
    of quick-260901-l55 and were self-invalidating by design.
    """
    reclass_path = PROJECT_ROOT / "src" / "python" / "pcs_panelwide_reclassify.py"
    doc = ast.get_docstring(ast.parse(reclass_path.read_text(encoding="utf-8"))) or ""
    assert doc, "the tool's module docstring vanished"
    assert len(doc) > 1000, (
        f"the tool's module docstring is only {len(doc)} chars -- a truncated "
        "docstring must not be able to green the ABSENCE assertions below"
    )
    flat = " ".join(doc.split())

    # -- (1) THE TRUE SEMANTICS ARE STATED HERE, IN SECTION (1) ------------- #
    assert "ANCHOR-RELATIVE" in flat
    assert "PANEL-WIDE" in flat
    assert "does NOT mean" in flat and "survives ``--exclude``" in flat

    # -- (2) THE DEFERRAL FRAMING IS GONE ----------------------------------- #
    # Section (1b) existed only because the correction could not be made. It
    # was made. A note that describes a discharged deferral is a stale lie in
    # waiting, and this module is the file the at-risk reader opens.
    assert _SCANNER_FALSE_CLAIM not in flat, (
        "the tool still QUOTES the scanner's false sentence as if it were live. "
        "The scanner was corrected in quick-260901-l55; section (1b) must go."
    )
    assert "THAT SENTENCE IS FALSE" not in flat, (
        "the tool still refutes a sentence that no longer exists"
    )
    assert "260831-DEFERRED-pairwise-completeness-scan-docstring.patch" not in flat, (
        "the tool still names the PARKED patch as pending; it has been applied"
    )
    assert "DEFERRED" not in doc, (
        "a DEFERRAL note survives in the tool's docstring after the deferral was "
        "discharged"
    )

    # ---------------------------------------------------------------------- #
    # (3) THE CLAIM THAT KEEPS THIS TEST LIVE AGAINST ANOTHER FILE.          #
    # The scanner's OWN docstring must now carry the correction. Read from    #
    # disk at call time -- the authority is the FILE, never a frozen literal. #
    # ---------------------------------------------------------------------- #
    scanner_path = PROJECT_ROOT / "src" / "python" / "pairwise_completeness_scan.py"
    scanner_doc = ast.get_docstring(
        ast.parse(scanner_path.read_text(encoding="utf-8"))
    ) or ""
    assert len(scanner_doc) > 1000, (
        f"the scanner's module docstring is only {len(scanner_doc)} chars -- a "
        "vanished docstring must not be able to green the ABSENCE assertion below"
    )
    scanner_flat = " ".join(scanner_doc.split())

    assert _SCANNER_FALSE_CLAIM not in scanner_flat, (
        "the scanner's FALSE claim is back: it says the ``--exclude`` side is "
        "already visible as ``already_occluded``. It is not -- the field is "
        "ANCHOR-RELATIVE and the excludelist is PANEL-WIDE."
    )
    assert "ANCHOR-RELATIVE" in scanner_flat, (
        "the scanner's docstring no longer states the anchor-relative semantics; "
        "the two files have drifted apart"
    )
    assert "does NOT mean" in scanner_flat and "survives ``--exclude``" in scanner_flat


# =========================================================================== #
# quick-260901-rvu — THE DEFINED-ROW TAIL AND THE INFORMATIVE-CARRIER          #
# DISTRIBUTION.                                                                #
#                                                                              #
# Seth's LOAD-BEARING question: are the 3,094 defined rows carrying            #
# max(del, partner)_carriers_lost_frac >= 0.9 PRE-filter (a member is on the   #
# production excludelist, so the rule already discards them) or POST-filter    #
# (neither member is, so a noise-dominated finite r enters the banked LD       #
# matrix silently)? The machinery that answers it already exists in            #
# pcs_panelwide_reclassify -- it was simply pointed at the UNDEFINED subset.   #
# =========================================================================== #

# --------------------------------------------------------------------------- #
# 8. THE TAIL PREDICATE IS PINNED TO THE SCANNER'S OWN, DIFFERENTIALLY          #
# --------------------------------------------------------------------------- #

def _pair_result(**overrides):
    """A FULL-WIDTH ``PairResult``, defaults derived from its OWN annotations.

    The field list is read from ``PairResult._fields`` rather than hand-typed,
    so a new scanner field cannot silently make these fixtures short.
    """
    import pairwise_completeness_scan as pcs

    ann = dict(pcs.PairResult.__annotations__)
    values: dict = {}
    for field in pcs.PairResult._fields:
        raw = ann.get(field, "str")
        if isinstance(raw, str):
            tname = raw
        else:
            tname = getattr(raw, "__forward_arg__", None) or getattr(
                raw, "__name__", str(raw)
            )
        values[field] = {"bool": False, "int": 0, "float": 0.0}.get(tname, "")
    for key, value in overrides.items():
        assert key in values, f"unknown PairResult field {key!r}"
        values[key] = value
    return pcs.PairResult(**values)


def _as_tsv_dict(result) -> dict:
    """``PairResult`` -> the EXACT dict the tool reads back out of the TSV.

    Rendered through ``_render_field`` (floats via ``repr``), so the differential
    below is run against the same STRING values a real ``pcs_pairs.tsv`` carries,
    not against in-memory floats the tool never sees.
    """
    import pairwise_completeness_scan as pcs

    return {f: pcs._render_field(getattr(result, f)) for f in pcs.PairResult._fields}


def _tail_grid():
    """The differential grid: the exact boundary, its float neighbours, both
    sides, both members, and an UNDEFINED row that neither side may count."""
    return [
        # 0 — EXACTLY 0.9. In the tail (>=) AND in the "(0.5,0.9]" bin (<=).
        _pair_result(region_id="R", del_index=1, partner_index=2, pair_key="1|2",
                     del_carriers_lost_frac=0.9, partner_carriers_lost_frac=0.0),
        # 1 — the float NEIGHBOUR below: NOT in the tail.
        _pair_result(region_id="R", del_index=1, partner_index=3, pair_key="1|3",
                     del_carriers_lost_frac=0.8999999999999999),
        # 2 — the float NEIGHBOUR above: in the tail.
        _pair_result(region_id="R", del_index=1, partner_index=4, pair_key="1|4",
                     del_carriers_lost_frac=0.9000000000000001),
        # 3 — zero on both sides.
        _pair_result(region_id="R", del_index=1, partner_index=5, pair_key="1|5",
                     del_carriers_lost_frac=0.0, partner_carriers_lost_frac=0.0),
        # 4 — UNDEFINED at 1.0: excluded from the tail on BOTH sides.
        _pair_result(region_id="R", del_index=1, partner_index=6, pair_key="1|6",
                     del_carriers_lost_frac=1.0, undefined=True),
        # 5 — del-side high, partner-side low.
        _pair_result(region_id="R", del_index=1, partner_index=7, pair_key="1|7",
                     del_carriers_lost_frac=0.994, partner_carriers_lost_frac=0.1),
        # 6 — partner-side high, del-side low (the max(), not the del, decides).
        _pair_result(region_id="R", del_index=1, partner_index=8, pair_key="1|8",
                     del_carriers_lost_frac=0.1, partner_carriers_lost_frac=0.995),
        # 7 — both high.
        _pair_result(region_id="R", del_index=1, partner_index=9, pair_key="1|9",
                     del_carriers_lost_frac=0.95, partner_carriers_lost_frac=0.96),
    ]


def test_the_tail_predicate_agrees_with_the_scanners_own_defined_lost_frac_ge_0p9():
    """THE PREDICATE IS NOT A SILENT FORK.

    ``pairwise_completeness_scan`` is CODE-FROZEN against ``cb199b6`` by the live
    runbook's STEP 0 gate (which ``test_pairwise_completeness_scan.py`` executes
    in a subprocess and requires to exit 0), so the tail predicate CANNOT be
    extracted into a shared helper there and no alias can be added. It is
    therefore declared once in ``pcs_panelwide_reclassify`` and pinned HERE, by
    running the scanner's OWN :func:`summarize` over a synthetic grid and
    requiring ``n_defined_lost_frac_ge_0p9`` to equal the local predicate's count.

    ⚠ The scanner's function is ``summarize`` -- there is NO ``summarize_region``
    (``hasattr`` is False) -- and ``region_id`` is POSITIONAL-FIRST with
    ``results`` POSITIONAL-SECOND.
    """
    import pairwise_completeness_scan as pcs
    import pcs_panelwide_reclassify as R

    rows = _tail_grid()
    summary = pcs.summarize(
        "R", rows, window_bp=25, n_deletions=0, n_candidates_edge_clipped=0
    )
    local = sum(1 for r in rows if R.is_tail_row(_as_tsv_dict(r)))

    assert summary["n_defined_lost_frac_ge_0p9"] == local, (
        f"the local tail predicate ({local}) has drifted from the scanner's own "
        f"n_defined_lost_frac_ge_0p9 ({summary['n_defined_lost_frac_ge_0p9']})"
    )
    # NON-VACUITY: a predicate that is always-true or always-false would agree
    # with nothing meaningful. Neither 0 nor len(rows) is acceptable.
    assert 0 < local < len(rows), f"vacuous grid: {local} of {len(rows)}"

    # The UNDEFINED row is excluded on BOTH sides.
    assert R.is_tail_row(_as_tsv_dict(rows[4])) is False
    # The EXACT boundary is IN the tail.
    assert R.is_tail_row(_as_tsv_dict(rows[0])) is True
    assert R.is_tail_row(_as_tsv_dict(rows[1])) is False
    assert R.is_tail_row(_as_tsv_dict(rows[2])) is True
    # Either member can carry it -- the predicate is on the max(), not the del.
    assert R.is_tail_row(_as_tsv_dict(rows[6])) is True

    # THE BOUNDARY DISAGREEMENT IS REAL AND IS PINNED HERE, not discovered later:
    # the bins put 0.9 in "(0.5,0.9]" (<=) while the tail INCLUDES it (>=). The
    # bins are NOT a substitute for the tail.
    assert pcs._lost_frac_bin(0.9) == "(0.5,0.9]"


def test_the_tail_differential_is_not_vacuous(monkeypatch):
    """NEGATIVE CONTROL for the differential above.

    A one-``ulp`` perturbation of the MODULE-GLOBAL threshold must break the
    equality, and it must break it AT THE ``frac == 0.9`` CASE SPECIFICALLY --
    which is only observable because :func:`is_tail_row` resolves the threshold at
    CALL time rather than binding it as a default argument at ``def`` time (a
    default would make this monkeypatch silently inert -- a vacuous control is
    worse than no control).
    """
    import pairwise_completeness_scan as pcs
    import pcs_panelwide_reclassify as R

    rows = _tail_grid()
    scanner_count = pcs.summarize(
        "R", rows, window_bp=25, n_deletions=0, n_candidates_edge_clipped=0
    )["n_defined_lost_frac_ge_0p9"]
    assert sum(1 for r in rows if R.is_tail_row(_as_tsv_dict(r))) == scanner_count

    at_0p9 = _as_tsv_dict(rows[0])
    assert float(at_0p9["del_carriers_lost_frac"]) == 0.9, "grid row 0 moved"
    assert R.is_tail_row(at_0p9) is True

    monkeypatch.setattr(R, "TAIL_MIN_CARRIERS_LOST_FRAC", 0.9000000000000001)
    perturbed = sum(1 for r in rows if R.is_tail_row(_as_tsv_dict(r)))
    assert perturbed == scanner_count - 1, (
        f"the perturbation changed nothing observable: {perturbed} vs "
        f"{scanner_count}. The monkeypatch is inert -- is the threshold bound as "
        f"a default argument at def time?"
    )
    assert R.is_tail_row(at_0p9) is False, (
        "the differential does not turn on the frac == 0.9 boundary case"
    )


# --------------------------------------------------------------------------- #
# 9. THE TAIL ROWS ARE CLASSIFIED AGAINST THE SAME EXCLUDELIST                  #
# --------------------------------------------------------------------------- #

#: A CLEAN pair placed in the region-1 window: a 2-base deletion whose span
#: (8000000-8000001) reaches nothing, and a SNP 50 bases downstream. Every
#: banked ``R1_VIDS`` pair is an occlusion tangle, so a POST-filter case has to
#: be built rather than transcribed.
CLEAN_DEL = "chr1:8000000:GA:G"
CLEAN_SNP = "chr1:8000050:T:C"


def _clean_bim_rows():
    return [_del_row(8000000, 2, vid=CLEAN_DEL), _snp_row(8000050, vid=CLEAN_SNP)]


def _defined_pairs_row(region_id, *, del_vid, del_pos, partner_vid, partner_pos,
                       del_index, partner_index, del_lost=0.0, partner_lost=0.0,
                       del_maf=0.01, partner_maf=0.5,
                       del_retained=0, partner_retained=0,
                       del_marginal=0, partner_marginal=0, n_both_called=0,
                       undefined="False"):
    """One FULL-WIDTH DEFINED ``pcs_pairs.tsv`` row with the carrier fields set."""
    return _pairs_row(
        region_id=region_id,
        del_index=del_index, del_vid=del_vid, del_chr=del_vid.split(":")[0],
        del_pos=del_pos,
        partner_index=partner_index, partner_vid=partner_vid,
        partner_pos=partner_pos,
        offset=partner_pos - del_pos,
        side="downstream" if partner_pos > del_pos else "upstream",
        already_occluded="False",
        # ORDER-NORMALISED, mirroring pairwise_completeness_scan._pair_key: the
        # sorted index pair is identical from either anchor.
        pair_key=f"{min(del_index, partner_index)}|{max(del_index, partner_index)}",
        undefined=undefined,
        n_both_called=n_both_called,
        del_carriers_lost_frac=del_lost,
        partner_carriers_lost_frac=partner_lost,
        del_maf_marginal=del_maf,
        partner_maf_marginal=partner_maf,
        del_carriers_retained=del_retained,
        partner_carriers_retained=partner_retained,
        del_carriers_marginal=del_marginal,
        partner_carriers_marginal=partner_marginal,
    )


def _pre_filter_tail_row():
    """A TAIL row whose PARTNER is on the panel-wide excludelist -> PRE-filter."""
    return _defined_pairs_row(
        "m2_region_00001",
        del_vid=R1_MINUS6_ANCHOR, del_pos=5922724,
        partner_vid=R1_OCCLUDED, partner_pos=5922718,
        # DISTINCT indices: reusing 46714/46715 would give this DEFINED row the
        # same order-normalised pair_key as the banked UNDEFINED row and the two
        # scopes would be indistinguishable in the output.
        del_index=90002, partner_index=90001,
        del_lost=0.994, partner_lost=0.10,
        del_maf=0.005, partner_maf=0.40,
        del_retained=4, partner_retained=900,
        del_marginal=728, partner_marginal=1200,
        n_both_called=1000,
    )


def _post_filter_tail_row():
    """A TAIL row with NEITHER member occluded -> POST-filter: it reaches the
    matrix and its noise-dominated finite r is consumed as a measurement."""
    return _defined_pairs_row(
        "m2_region_00001",
        del_vid=CLEAN_DEL, del_pos=8000000,
        partner_vid=CLEAN_SNP, partner_pos=8000050,
        del_index=70000, partner_index=70001,
        del_lost=0.999, partner_lost=0.0,
        del_maf=0.005, partner_maf=0.45,
        del_retained=1, partner_retained=800,
        del_marginal=728, partner_marginal=1400,
        n_both_called=900,
    )


def test_a_tail_row_whose_member_is_occluded_is_PRE_filter(tmp_path):
    """PRE-filter: the posted rule ALREADY discards this row's pair.

    Same excludelist, same single ``detect_occluded_variants`` call per region --
    the tail rows are classified against the row set the UNDEFINED rows were
    always classified against, never a second call with a different row set.
    """
    import pcs_panelwide_reclassify as R

    pairs_tsv, bim, regions = _region1_fixture(
        tmp_path, extra_pairs=(_pre_filter_tail_row(),),
        extra_bim=_clean_bim_rows(),
    )
    out_rows, summary = _run(R, pairs_tsv, bim, regions)

    row = _row_for(out_rows, "90001|90002")
    assert row["row_class"] == "tail"
    assert row["del_occluded_panelwide"] is False
    assert row["partner_occluded_panelwide"] is True
    assert row["pair_reaches_matrix"] is False
    assert row["carriers_lost_frac_pair_max"] == 0.994

    pooled = summary["pooled"]
    assert pooled["n_tail_rows_in"] == 1
    assert pooled["n_tail_distinct_pairs_in"] == 1
    assert pooled["n_tail_rows_member_occluded_panelwide"] == 1
    assert pooled["n_tail_rows_neither_member_occluded_panelwide"] == 0
    assert pooled["n_tail_pairs_member_occluded_panelwide"] == 1
    assert pooled["n_tail_pairs_neither_member_occluded_panelwide"] == 0
    assert pooled["n_tail_regions_with_rows"] == 1
    assert pooled["tail_min_carriers_lost_frac"] == 0.9


def test_a_tail_row_with_neither_member_occluded_is_POST_filter(tmp_path):
    """POST-filter: it SURVIVES into the banked panel.

    This is the branch Seth calls *"a prevalent, systematic, silent corruption in
    the banked LD matrix"* -- and it is the branch whose verdict is CONDITIONAL on
    the row set (occlusion is monotone), which is why ``tail_verdict_scope``
    travels with the split.
    """
    import pcs_panelwide_reclassify as R

    pairs_tsv, bim, regions = _region1_fixture(
        tmp_path, extra_pairs=(_post_filter_tail_row(),),
        extra_bim=_clean_bim_rows(),
    )
    out_rows, summary = _run(R, pairs_tsv, bim, regions)

    row = _row_for(out_rows, "70000|70001")
    assert row["row_class"] == "tail"
    assert row["del_occluded_panelwide"] is False
    assert row["partner_occluded_panelwide"] is False
    assert row["pair_reaches_matrix"] is True
    assert row["carriers_lost_frac_pair_max"] == 0.999

    pooled = summary["pooled"]
    assert pooled["n_tail_rows_in"] == 1
    assert pooled["n_tail_rows_member_occluded_panelwide"] == 0
    assert pooled["n_tail_rows_neither_member_occluded_panelwide"] == 1
    assert pooled["n_tail_pairs_member_occluded_panelwide"] == 0
    assert pooled["n_tail_pairs_neither_member_occluded_panelwide"] == 1

    # PRE and POST are SEPARATE KEYS. Nothing in the output permits collapsing
    # them into one number.
    assert "n_tail_rows_member_occluded_panelwide" in pooled
    assert "n_tail_rows_neither_member_occluded_panelwide" in pooled
    assert isinstance(pooled["tail_verdict_scope"], str)
    flat = " ".join(pooled["tail_verdict_scope"].split())
    assert "PRE-filter" in flat and "POST-filter" in flat
    assert "CONDITIONAL" in flat


def test_both_tail_verdicts_reconcile_at_row_and_pair_level(tmp_path):
    """The two tail populations are EXHAUSTIVE and DISJOINT, at BOTH levels."""
    import pcs_panelwide_reclassify as R

    pairs_tsv, bim, regions = _region1_fixture(
        tmp_path,
        extra_pairs=(_pre_filter_tail_row(), _post_filter_tail_row()),
        extra_bim=_clean_bim_rows(),
    )
    _out, summary = _run(R, pairs_tsv, bim, regions)
    pooled = summary["pooled"]

    assert (
        pooled["n_tail_rows_member_occluded_panelwide"]
        + pooled["n_tail_rows_neither_member_occluded_panelwide"]
        == pooled["n_tail_rows_in"] == 2
    )
    assert (
        pooled["n_tail_pairs_member_occluded_panelwide"]
        + pooled["n_tail_pairs_neither_member_occluded_panelwide"]
        == pooled["n_tail_distinct_pairs_in"] == 2
    )
    # 1 PRE + 1 POST -- the split is not degenerate in either direction.
    assert pooled["n_tail_rows_member_occluded_panelwide"] == 1
    assert pooled["n_tail_rows_neither_member_occluded_panelwide"] == 1


def test_a_defined_row_below_the_tail_is_not_emitted_and_an_undefined_row_is_never_tail(
    tmp_path,
):
    """EMISSION STAYS BOUNDED: undefined + tail ONLY.

    A defined row at ``frac == 0.5`` contributes to the AGGREGATES but produces no
    output row; an UNDEFINED row at ``frac == 1.0`` is emitted as ``undefined``,
    never as ``tail`` (the tail is a DEFINED-row quantity by construction --
    ``lost_frac == 1.0`` implies invariant implies undefined).
    """
    import pcs_panelwide_reclassify as R

    below = _defined_pairs_row(
        "m2_region_00001",
        del_vid=CLEAN_DEL, del_pos=8000000,
        partner_vid=CLEAN_SNP, partner_pos=8000050,
        del_index=70002, partner_index=70003,
        del_lost=0.5, partner_lost=0.5,
        del_retained=77, partner_retained=88,
    )
    pairs_tsv, bim, regions = _region1_fixture(
        tmp_path, extra_pairs=(below,), extra_bim=_clean_bim_rows(),
    )
    out_rows, summary = _run(R, pairs_tsv, bim, regions)

    assert all(r["pair_key"] != "70002|70003" for r in out_rows), (
        "a below-tail defined row was EMITTED; emission must stay bounded"
    )
    assert len(out_rows) == 1
    assert out_rows[0]["row_class"] == "undefined"
    assert summary["pooled"]["n_tail_rows_in"] == 0
    assert summary["pooled"]["n_defined_rows_in"] == 1
    assert summary["pooled"]["n_defined_rows_reaching_matrix"] == 1

    # The banked -6 undefined row, given a lost_frac of 1.0, stays "undefined".
    hot_undefined = _pairs_row(
        region_id="m2_region_00001",
        del_index=46715, del_vid=R1_MINUS6_ANCHOR, del_chr="chr1", del_pos=5922724,
        partner_index=46714, partner_vid=R1_OCCLUDED, partner_pos=5922718,
        offset=-6, side="upstream", already_occluded="False",
        pair_key="46714|46715", undefined="True",
        del_carriers_lost_frac=1.0, partner_carriers_lost_frac=1.0,
    )
    pairs2 = _write_pairs_tsv(tmp_path, [hot_undefined], name="hot.tsv")
    out2, summary2 = _run(R, pairs2, bim, regions)
    assert len(out2) == 1
    assert out2[0]["row_class"] == "undefined"
    assert summary2["pooled"]["n_tail_rows_in"] == 0
    assert summary2["pooled"]["n_undefined_rows_in"] == 1


def test_the_tail_counts_reconcile_or_the_tool_raises(tmp_path, monkeypatch):
    """A count is a claim -- for the TAIL scope too.

    The monkeypatch is SCOPED to tail-class rows so the raise it produces can
    only come from the TAIL rollup: patching the counter unconditionally would
    fire the pre-existing UNDEFINED reconciliation first and prove nothing about
    the new one.
    """
    import pcs_panelwide_reclassify as R

    pairs_tsv, bim, regions = _region1_fixture(
        tmp_path, extra_pairs=(_pre_filter_tail_row(),),
        extra_bim=_clean_bim_rows(),
    )
    _out, summary = _run(R, pairs_tsv, bim, regions)
    assert summary["pooled"]["n_tail_distinct_pairs_in"] == 1

    real = R._count_distinct_pairs

    def only_tail(rows):
        rows = list(rows)
        if rows and all(r.get("row_class") == "tail" for r in rows):
            return 999
        return real(rows)

    monkeypatch.setattr(R, "_count_distinct_pairs", only_tail)
    with pytest.raises(ValueError) as exc:
        _run(R, pairs_tsv, bim, regions)
    message = str(exc.value)
    assert "999" in message
    assert "TAIL" in message or "tail" in message, (
        f"the raise does not name the TAIL scope: {message}"
    )


# --------------------------------------------------------------------------- #
# 10. `THE RARER VARIANT` — THE RULE, THE TIE, AND THE DISAGREEMENT             #
# --------------------------------------------------------------------------- #

def _one_defined_row_fixture(tmp_path, row, *, name="one"):
    """A minimal clean window carrying exactly one supplied DEFINED row."""
    bim = _write_bim(tmp_path, _clean_bim_rows(), name=f"panel_{name}")
    regions = _write_regions_tsv(
        tmp_path, [("m2_region_00500", "chr1", 7_900_000, 8_100_000)],
        name=f"regions_{name}.tsv",
    )
    pairs = _write_pairs_tsv(tmp_path, [row], name=f"pairs_{name}.tsv")
    return pairs, bim, regions


def test_the_rarer_member_is_chosen_by_marginal_maf_not_by_marginal_carrier_count(
    tmp_path,
):
    """RARITY IS A FREQUENCY, NOT A COUNT.

    ``*_carriers_marginal`` is NOT comparable across members, because
    ``n_called_del != n_called_partner`` IS the phenomenon under study. Here the
    del member is RARER by MAF (0.004 < 0.02) while carrying MORE marginal
    carriers (100 > 50) -- possible only because the two called sets differ.
    """
    import pcs_panelwide_reclassify as R

    row = _defined_pairs_row(
        "m2_region_00500",
        del_vid=CLEAN_DEL, del_pos=8000000,
        partner_vid=CLEAN_SNP, partner_pos=8000050,
        del_index=1, partner_index=2,
        del_lost=0.994,
        del_maf=0.004, partner_maf=0.02,
        del_marginal=100, partner_marginal=50,
        del_retained=9, partner_retained=40,
    )
    pairs, bim, regions = _one_defined_row_fixture(tmp_path, row, name="maf")
    out_rows, summary = _run(R, pairs, bim, regions)

    emitted = _row_for(out_rows, "1|2")
    assert emitted["rarer_member"] == "del"
    assert emitted["rarer_by_maf_tie"] is False
    assert emitted["informative_carriers_rarer"] == 9
    assert emitted["informative_carriers_min"] == 9
    assert emitted["informative_carriers_defs_disagree"] is False
    assert summary["pooled"]["n_defined_rows_rarer_and_min_definitions_disagree"] == 0


def test_an_exact_maf_tie_picks_the_worse_precision_and_flags_the_tie(tmp_path):
    """THE TIE BREAKS TOWARD THE WORSE PRECISION.

    Same conservative shape as the scanner's own MINOR-ALLELE TIE RULE (which
    reports the LARGER ``lost_frac`` at ``af_a1 == 0.5``). The tie is FLAGGED, not
    hidden, so a reader can see the choice was forced rather than measured.
    """
    import pcs_panelwide_reclassify as R

    row = _defined_pairs_row(
        "m2_region_00500",
        del_vid=CLEAN_DEL, del_pos=8000000,
        partner_vid=CLEAN_SNP, partner_pos=8000050,
        del_index=3, partner_index=4,
        del_lost=0.95,
        del_maf=0.01, partner_maf=0.01,
        del_marginal=500, partner_marginal=500,
        del_retained=30, partner_retained=8,
    )
    pairs, bim, regions = _one_defined_row_fixture(tmp_path, row, name="tie")
    out_rows, _summary = _run(R, pairs, bim, regions)

    emitted = _row_for(out_rows, "3|4")
    assert emitted["rarer_member"] == "partner"
    assert emitted["rarer_by_maf_tie"] is True
    assert emitted["informative_carriers_rarer"] == 8
    assert emitted["informative_carriers_min"] == 8
    assert emitted["informative_carriers_defs_disagree"] is False


def test_the_two_carrier_definitions_can_disagree_and_the_disagreement_is_counted(
    tmp_path,
):
    """A NEAR-MISS BETWEEN TWO DEFINITIONS MAY NOT MOTIVATE A HYPOTHESIS.

    ``SE(r) ~ 1/sqrt(m)`` binds on the MINIMUM retained count, while `the rarer
    variant` is Seth's own wording. They are DIFFERENT quantities and they can
    disagree; the disagreement is COUNTED rather than assumed away
    (``feedback_aggregate_agreement_hides_component_errors``).
    """
    import pcs_panelwide_reclassify as R

    row = _defined_pairs_row(
        "m2_region_00500",
        del_vid=CLEAN_DEL, del_pos=8000000,
        partner_vid=CLEAN_SNP, partner_pos=8000050,
        del_index=5, partner_index=6,
        del_lost=0.99,
        del_maf=0.01, partner_maf=0.30,
        del_marginal=1448, partner_marginal=40000,
        del_retained=50, partner_retained=12,
    )
    pairs, bim, regions = _one_defined_row_fixture(tmp_path, row, name="disagree")
    out_rows, summary = _run(R, pairs, bim, regions)

    emitted = _row_for(out_rows, "5|6")
    assert emitted["rarer_member"] == "del"
    assert emitted["informative_carriers_rarer"] == 50
    assert emitted["informative_carriers_min"] == 12
    assert emitted["informative_carriers_rarer"] != emitted["informative_carriers_min"]
    assert emitted["informative_carriers_defs_disagree"] is True
    assert summary["pooled"]["n_defined_rows_rarer_and_min_definitions_disagree"] == 1


# --------------------------------------------------------------------------- #
# 11. THE DISTRIBUTION SETH SAYS HE LACKS                                       #
# --------------------------------------------------------------------------- #

#: A KNOWN multiset of ``informative_carriers_rarer`` values, deliberately
#: unsorted in the input so the percentile code cannot pass by accident.
_KNOWN_CARRIERS = (0, 1, 2, 5, 10, 25, 50, 100, 150, 3)


def _distribution_fixture(tmp_path, values=_KNOWN_CARRIERS):
    """One clean window; one DEFINED tail row per value in ``values``.

    ``del_maf`` (0.01) is strictly below ``partner_maf`` (0.5) on every row, so
    the rarer member is always the del and ``informative_carriers_rarer`` is
    exactly the supplied value. Every pair is CLEAN, so all rows reach the matrix.
    """
    bim_rows = [_del_row(1000, 2, vid="chr1:1000:GA:G")]
    pairs = []
    for i, value in enumerate(values):
        bp = 2000 + i
        snp_vid = f"chr1:{bp}:T:C"
        bim_rows.append(_snp_row(bp, vid=snp_vid))
        pairs.append(_defined_pairs_row(
            "m2_region_00300",
            del_vid="chr1:1000:GA:G", del_pos=1000,
            partner_vid=snp_vid, partner_pos=bp,
            del_index=10, partner_index=100 + i,
            del_lost=0.994,
            del_maf=0.01, partner_maf=0.5,
            del_retained=value, partner_retained=value + 1000,
            del_marginal=value + 700, partner_marginal=value + 5000,
        ))
    bim = _write_bim(tmp_path, bim_rows, name="panel_dist")
    regions = _write_regions_tsv(
        tmp_path, [("m2_region_00300", "chr1", 900, 3000)], name="regions_dist.tsv",
    )
    pairs_tsv = _write_pairs_tsv(tmp_path, pairs, name="pairs_dist.tsv")
    return pairs_tsv, bim, regions


def test_the_percentiles_are_integer_nearest_rank_on_a_known_array(tmp_path):
    """INTEGER NEAREST-RANK, hand-derived, on a KNOWN multiset.

    ``rank = ceil(q * n / 100)`` clamped to ``>= 1``; ``p0`` is the MIN and
    ``p100`` the MAX. n = 10, sorted = [0, 1, 2, 3, 5, 10, 25, 50, 100, 150].
    Every expectation below is derived by hand from that convention, never read
    back out of the module.
    """
    import pcs_panelwide_reclassify as R

    pairs, bim, regions = _distribution_fixture(tmp_path)
    _out, summary = _run(R, pairs, bim, regions)
    pct = summary["pooled"]["informative_carriers_percentiles_defined_rows"]

    assert pct == {
        "p0": 0,      # rank max(1, ceil(0.0))  = 1  -> sorted[0]  = MIN
        "p1": 0,      # rank max(1, ceil(0.1))  = 1  -> sorted[0]
        "p5": 0,      # rank max(1, ceil(0.5))  = 1  -> sorted[0]
        "p10": 0,     # rank ceil(1.0)          = 1  -> sorted[0]
        "p25": 2,     # rank ceil(2.5)          = 3  -> sorted[2]
        "p50": 5,     # rank ceil(5.0)          = 5  -> sorted[4]
        "p75": 50,    # rank ceil(7.5)          = 8  -> sorted[7]
        "p90": 100,   # rank ceil(9.0)          = 9  -> sorted[8]
        "p99": 150,   # rank ceil(9.9)          = 10 -> sorted[9]
        "p100": 150,  # rank ceil(10.0)         = 10 -> sorted[9] = MAX
    }
    assert pct["p0"] == min(_KNOWN_CARRIERS)
    assert pct["p100"] == max(_KNOWN_CARRIERS)


def test_the_low_tail_counts_are_exact_and_cumulative_and_cover_every_m_to_100(
    tmp_path,
):
    """EXACT counts for EVERY m in 0..100 -- zeros included -- plus prefix sums.

    A key per m (not only the occupied ones) is what lets a reader see the SHAPE
    of the low tail rather than a summary of it; the cumulative entries are
    asserted to EQUAL the prefix sums so the two can never drift.
    """
    import pcs_panelwide_reclassify as R

    pairs, bim, regions = _distribution_fixture(tmp_path)
    _out, summary = _run(R, pairs, bim, regions)
    low = summary["pooled"]["informative_carriers_low_tail_defined_rows"]

    for m in range(0, 101):
        assert f"m_{m}" in low, f"missing exact count key m_{m}"
    expected_occupied = {v for v in _KNOWN_CARRIERS if v <= 100}
    for m in range(0, 101):
        assert low[f"m_{m}"] == (1 if m in expected_occupied else 0), f"m_{m}"

    prefix = 0
    for m in range(0, 101):
        prefix += low[f"m_{m}"]
        key = f"n_le_{m}"
        if key in low:
            assert low[key] == prefix, f"{key} is not the prefix sum through m={m}"
    for k in (0, 1, 2, 5, 10, 25, 50, 100):
        assert f"n_le_{k}" in low
    assert low["n_le_0"] == 1
    assert low["n_le_1"] == 2
    assert low["n_le_2"] == 3
    assert low["n_le_5"] == 5
    assert low["n_le_10"] == 6
    assert low["n_le_25"] == 7
    assert low["n_le_50"] == 8
    assert low["n_le_100"] == 9
    assert low["n_gt_100"] == 1
    assert low["n_le_100"] + low["n_gt_100"] == len(_KNOWN_CARRIERS)


def test_the_distribution_is_reported_twice_over_all_defined_rows_and_over_rows_reaching_the_matrix(
    tmp_path,
):
    """TWICE: over ALL in-scope defined rows, and over Seth's `retained pairs`.

    They are DIFFERENT populations and the difference is the entire pre/post
    question, so reporting one would beg it.
    """
    import pcs_panelwide_reclassify as R

    # An occluder (span 1000-1007) covering the SNP at 1005, plus a clean pair.
    occluder = "chr1:1000:GACGTACG:G"
    bim = _write_bim(tmp_path, [
        _del_row(1000, 8, vid=occluder),
        _snp_row(1005, vid="chr1:1005:T:C"),
        _del_row(1500, 2, vid="chr1:1500:GA:G"),
        _snp_row(2000, vid="chr1:2000:T:C"),
    ], name="panel_two")
    regions = _write_regions_tsv(
        tmp_path, [("m2_region_00301", "chr1", 900, 3000)], name="regions_two.tsv",
    )
    pairs_tsv = _write_pairs_tsv(tmp_path, [
        _defined_pairs_row(
            "m2_region_00301",
            del_vid=occluder, del_pos=1000,
            partner_vid="chr1:1005:T:C", partner_pos=1005,
            del_index=1, partner_index=2,
            del_lost=0.994, del_maf=0.01, partner_maf=0.5,
            del_retained=7, partner_retained=900,
        ),
        _defined_pairs_row(
            "m2_region_00301",
            del_vid="chr1:1500:GA:G", del_pos=1500,
            partner_vid="chr1:2000:T:C", partner_pos=2000,
            del_index=3, partner_index=4,
            del_lost=0.994, del_maf=0.01, partner_maf=0.5,
            del_retained=42, partner_retained=900,
        ),
    ], name="pairs_two.tsv")

    _out, summary = _run(R, pairs_tsv, bim, regions)
    pooled = summary["pooled"]

    all_pct = pooled["informative_carriers_percentiles_defined_rows"]
    reaching_pct = pooled[
        "informative_carriers_percentiles_defined_rows_reaching_matrix"
    ]
    assert all_pct != reaching_pct, (
        "the two distributions are identical on a fixture built to separate them"
    )
    assert all_pct["p0"] == 7 and all_pct["p100"] == 42
    assert reaching_pct["p0"] == 42 and reaching_pct["p100"] == 42

    all_low = pooled["informative_carriers_low_tail_defined_rows"]
    reaching_low = pooled[
        "informative_carriers_low_tail_defined_rows_reaching_matrix"
    ]
    assert all_low["m_7"] == 1 and all_low["m_42"] == 1
    assert reaching_low["m_7"] == 0 and reaching_low["m_42"] == 1

    assert pooled["n_defined_rows_in"] == 2
    assert pooled["n_defined_rows_member_occluded_panelwide"] == 1
    assert pooled["n_defined_rows_reaching_matrix"] == 1
    assert (
        pooled["n_defined_rows_reaching_matrix"]
        + pooled["n_defined_rows_member_occluded_panelwide"]
        == pooled["n_defined_rows_in"]
    )


def test_the_tail_split_cannot_be_printed_without_its_scope_condition(tmp_path, capsys):
    """THE MONOTONICITY CONDITION TRAVELS WITH THE CLAIM, NOT BESIDE IT.

    A POST-filter verdict is CONDITIONAL on the row set; a PRE-filter verdict is
    SOUND. Quoting the split without that condition is the repudiation surface
    (T-rvu-06), so the condition is asserted to appear WITHIN the split's own
    block -- never a screenful away.
    """
    import pcs_panelwide_reclassify as R

    pairs_tsv, bim, regions = _region1_fixture(
        tmp_path,
        extra_pairs=(_pre_filter_tail_row(), _post_filter_tail_row()),
        extra_bim=_clean_bim_rows(),
    )
    code = R.main([
        "--pairs-tsv", str(pairs_tsv),
        "--bfile-prefix", str(bim.with_suffix("")),
        "--regions-tsv", str(regions),
        "--out", str(tmp_path / "split.tsv"),
        "--summary", str(tmp_path / "split.json"),
    ])
    assert code == 0
    lines = capsys.readouterr().out.splitlines()

    heads = [i for i, ln in enumerate(lines) if "PRE-FILTER vs POST-FILTER" in ln]
    assert len(heads) == 1, f"the tail block header is not printed exactly once: {heads}"
    block = " ".join(" ".join(lines[heads[0]:heads[0] + 20]).split())

    assert "n_tail_rows_member_occluded_panelwide" in block
    assert "n_tail_rows_neither_member_occluded_panelwide" in block
    scope_flat = " ".join(R.TAIL_VERDICT_SCOPE.split())
    assert scope_flat in block, (
        "the pre/post split is printed WITHOUT the monotonicity condition beside it"
    )


# --------------------------------------------------------------------------- #
# 12. NO CARRIER FLOOR — AND THE GUARD MUST NOT BAN ITS OWN DISCLAIMER          #
# --------------------------------------------------------------------------- #

#: An emitted key that NO negative control below perturbs. It anchors the (e3)
#: collection against silently narrowing to nothing -- which is exactly what
#: happened on the first draft: ``POOLED_KEYS`` became
#: ``BANKED_POOLED_KEYS + TAIL_SCOPE_POOLED_KEYS``, an ``ast.BinOp`` with no
#: ``.elts``, and the check walked away green over ZERO keys.
_KEY_COLLECTION_ANCHOR = "n_rows_in_tsv"


def _module_level_numeric_assignments(tree):
    """``[(target_name, node)]`` for every MODULE-LEVEL numeric assignment."""
    found = []
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets, value = [node.target], node.value
        elif isinstance(node, ast.Assign):
            targets = [t for t in node.targets if isinstance(t, ast.Name)]
            value = node.value
        else:
            continue
        if value is None:
            continue
        numeric = (
            isinstance(value, ast.Constant)
            and isinstance(value.value, (int, float))
            and not isinstance(value.value, bool)
        ) or (
            isinstance(value, ast.UnaryOp)
            and isinstance(value.operand, ast.Constant)
            and isinstance(value.operand.value, (int, float))
        )
        if numeric:
            found.extend((t.id, node) for t in targets)
    return found


def _declared_key_names(tree):
    """Every string element of EVERY module-level ``*_KEYS`` / ``*_COLUMNS`` tuple.

    Selected by NAME SUFFIX rather than by an explicit list of three names,
    because ``POOLED_KEYS`` is a CONCATENATION (``BANKED_POOLED_KEYS +
    TAIL_SCOPE_POOLED_KEYS``) -- an ``ast.BinOp`` with no ``.elts`` -- so a check
    that walked only the three named tuples collected ZERO tail keys and passed
    the (iii) control while proving nothing. The suffix rule reaches the operands
    themselves and is closed under future splits.
    """
    names = []
    for node in tree.body:
        target = None
        value = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target, value = node.target.id, node.value
        elif isinstance(node, ast.Assign):
            named = [t.id for t in node.targets if isinstance(t, ast.Name)]
            target = named[0] if named else None
            value = node.value
        if target is None or value is None:
            continue
        if not (target.endswith("_KEYS") or target.endswith("_COLUMNS")):
            continue
        for elt in getattr(value, "elts", []):
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                names.append(elt.value)
    return names


def _assert_no_carrier_floor(text: str) -> None:
    """Fail if a carrier FLOOR is DECLARED, APPLIED, or NAMED as a verdict.

    Three checks, each scoped to where a floor can ACTUALLY exist:

    (e1) DECLARED -- a module-level assignment whose target names a floor (or
         names an informative-carrier quantity) and whose VALUE IS NUMERIC. The
         numeric qualifier is load-bearing: ``NO_FLOOR_NOTICE`` is a module-level
         target matching ``(?i)floor`` and it is the module's own DISCLAIMER. A
         floor is a NUMBER; banning the word regardless of value would fire this
         guard on the tool's compliant, unperturbed source -- green unreachable
         while the constant stays required.
    (e2) APPLIED -- ANY ``ast.Compare`` with an informative-carrier operand on one
         side and a numeric literal on the other. THIS IS THE ONE WITH TEETH: a
         floor is a COMPARISON, and (e1) alone would miss
         ``if row["informative_carriers_rarer"] < 25``.
    (e3) NAMED -- no emitted key matches the bare substrings
         ``pass|fail|reliable|unreliable``, i.e. no key states a VERDICT that only
         a floor could produce.

    ⚠ ``floor`` is DELIBERATELY ABSENT from (e3). Task 2 requires the pooled key
    ``no_floor_notice``, whose NAME DISCLAIMS a floor; banning the substring in
    key names would fire this guard on the tool's own compliant output. A floor
    cannot live in a key name -- a key is a label, not a threshold -- so it is
    banned where a real one would live, and not where it cannot.
    """
    tree = ast.parse(text)

    # ---- (e1) DECLARED --------------------------------------------------- #
    for name, _node in _module_level_numeric_assignments(tree):
        assert not re.search(r"(?i)floor", name), (
            f"A CARRIER FLOOR IS DECLARED: module-level numeric constant {name!r}. "
            f"Seth withheld the value deliberately -- 'picking a number from what "
            f"passes is the error we have now made twice.' Emit the DISTRIBUTION."
        )
        assert "informative_carriers" not in name.lower(), (
            f"A CARRIER FLOOR IS DECLARED: module-level numeric constant {name!r} "
            f"names an informative-carrier quantity."
        )

    # ---- (e2) APPLIED ---------------------------------------------------- #
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        operands = [node.left] + list(node.comparators)
        if not any("informative_carriers" in ast.unparse(o) for o in operands):
            continue
        for operand in operands:
            const = None
            if isinstance(operand, ast.Constant):
                const = operand.value
            elif isinstance(operand, ast.UnaryOp) and isinstance(
                operand.operand, ast.Constant
            ):
                const = operand.operand.value
            if isinstance(const, (int, float)) and not isinstance(const, bool):
                raise AssertionError(
                    f"A CARRIER FLOOR IS APPLIED: "
                    f"{ast.unparse(node)!r} compares an informative-carrier "
                    f"quantity against the numeric literal {const!r}. This tool "
                    f"emits the DISTRIBUTION; it applies no floor."
                )

    # ---- (e3) NAMED ------------------------------------------------------ #
    declared = _declared_key_names(tree)
    assert declared, "no key/column tuples were found -- the (e3) check is vacuous"
    assert _KEY_COLLECTION_ANCHOR in declared, (
        f"the (e3) key collection lost its anchor {_KEY_COLLECTION_ANCHOR!r} -- "
        f"it has narrowed and is no longer checking the keys it claims to "
        f"({len(declared)} collected)"
    )
    for key in declared:
        assert not re.search(r"(?i)(pass|fail|reliable|unreliable)", key), (
            f"A VERDICT KEY IMPLIES A FLOOR: {key!r}. Only a threshold can make a "
            f"pair reliable or unreliable, and no threshold is proposed."
        )


def test_no_carrier_floor_is_declared_anywhere(tmp_path, capsys):
    """NO FLOOR ANYWHERE -- in code, in key names, or in the printed banner.

    Source is READ AND PARSED AT CALL TIME, so a stale ``__pycache__`` cannot
    decide the outcome (``feedback_negative_control_defeated_by_bytecode_cache``).
    """
    import pcs_panelwide_reclassify as R

    text = (PROJECT_ROOT / _MODULE_REL).read_text(encoding="utf-8")
    _assert_no_carrier_floor(text)

    # The DISCLAIMER exists, is a real sentence, and says what it must.
    flat_notice = " ".join(R.NO_FLOOR_NOTICE.split())
    assert "NO CARRIER FLOOR IS PROPOSED" in flat_notice
    assert "DISTRIBUTION" in flat_notice

    # The module docstring carries it too.
    doc = ast.get_docstring(ast.parse(text)) or ""
    assert "no floor" in " ".join(doc.split()).lower()

    # ...and main() PRINTS it. Whitespace-normalised: the banner wraps.
    pairs_tsv, bim, regions = _region1_fixture(
        tmp_path, extra_pairs=(_post_filter_tail_row(),), extra_bim=_clean_bim_rows(),
    )
    code = R.main([
        "--pairs-tsv", str(pairs_tsv),
        "--bfile-prefix", str(bim.with_suffix("")),
        "--regions-tsv", str(regions),
        "--out", str(tmp_path / "nf.tsv"),
        "--summary", str(tmp_path / "nf.json"),
    ])
    assert code == 0
    printed = " ".join(capsys.readouterr().out.split())
    assert flat_notice in printed, "main() does not print the no-floor notice"


def _inject_into_a_function_body(text: str, snippet: str) -> str:
    """Insert ``snippet`` as the FIRST statement of the LAST top-level function.

    AST-located by BYTE RANGE, never ``text.replace`` -- a first-match replace
    lands in a DOCSTRING (the M7 trap), which proves nothing. The insertion point
    and the indentation are both taken from the parsed target statement.
    """
    tree = ast.parse(text)
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert funcs, "no top-level function to inject into"
    target = funcs[-1]
    body = [s for s in target.body if not (
        isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
        and isinstance(s.value.value, str)
    )]
    assert body, f"{target.name} has no non-docstring statement"
    anchor = body[0]
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    start = offsets[anchor.lineno - 1] + anchor.col_offset
    indent = " " * anchor.col_offset
    injected = text[:start] + snippet + "\n" + indent + text[start:]

    # NON-VACUITY + LANDING SITE, both asserted: it changed the text, it parses,
    # and the new statement is INSIDE the FunctionDef's byte span.
    assert injected != text, "the injection changed nothing"
    new_tree = ast.parse(injected)
    new_target = [n for n in new_tree.body if isinstance(n, ast.FunctionDef)][-1]
    assert new_target.name == target.name
    rendered = ast.unparse(new_target)
    assert snippet.split("\n")[0].strip().rstrip(":") in rendered.replace("'", '"') \
        or snippet.strip().split()[0] in rendered, (
        f"the injection did not land inside {target.name}"
    )
    return injected


def test_the_no_floor_guard_fires_on_each_injected_floor():
    """THREE NEGATIVE CONTROLS -- one per check. Green is evidence only because
    these reds exist (``feedback_green_assertion_needs_a_negative_control``).

    The UNPERTURBED source -- INCLUDING its ``no_floor_notice`` key and its
    ``NO_FLOOR_NOTICE`` constant -- must pass all three.
    """
    text = (PROJECT_ROOT / _MODULE_REL).read_text(encoding="utf-8")
    _assert_no_carrier_floor(text)  # the baseline is GREEN

    # (i) DECLARED.
    declared = text.replace(
        "from __future__ import annotations",
        "from __future__ import annotations\n\nCARRIER_FLOOR = 25",
        1,
    )
    assert "CARRIER_FLOOR = 25" in declared and declared != text
    with pytest.raises(AssertionError) as exc_declared:
        _assert_no_carrier_floor(declared)
    assert "DECLARED" in str(exc_declared.value)

    # (ii) APPLIED -- inside a FUNCTION BODY, byte-located, never a docstring.
    applied = _inject_into_a_function_body(
        text, 'if row["informative_carriers_rarer"] < 25:\n        pass'
    )
    with pytest.raises(AssertionError) as exc_applied:
        _assert_no_carrier_floor(applied)
    assert "APPLIED" in str(exc_applied.value)

    # (iii) NAMED -- a key renamed to a verdict only a floor could produce.
    named = text.replace('"n_tail_rows_in",', '"n_tail_rows_unreliable",', 1)
    assert named != text, "the key rename changed nothing"
    with pytest.raises(AssertionError) as exc_named:
        _assert_no_carrier_floor(named)
    assert "n_tail_rows_unreliable" in str(exc_named.value)


# --------------------------------------------------------------------------- #
# 13. THE INVARIANCE REGRESSION — THE ONE THAT PROTECTS THE BANKED NUMBERS      #
# --------------------------------------------------------------------------- #

#: The THIRTEEN pooled keys the banked run emitted. Written out LITERALLY so this
#: test cannot be satisfied by the module changing its own constant.
_BANKED_THIRTEEN = (
    "n_rows_in_tsv",
    "n_defined_rows_in",
    "n_undefined_rows_in",
    "n_undefined_distinct_pairs_in",
    "n_undefined_rows_out_of_scope",
    "n_rows_member_occluded_panelwide",
    "n_rows_neither_member_occluded_panelwide",
    "n_pairs_member_occluded_panelwide",
    "n_pairs_neither_member_occluded_panelwide",
    "n_pairs_neither_occluded_and_no_globally_invariant_member",
    "n_pairs_with_ambiguous_member_id",
    "ambiguous_member_ids",
    "occluded_member_vids",
)

#: Of those thirteen, the two that count the INPUT rather than the undefined
#: scope. They MUST move when defined rows are added to the input -- asserting
#: equality on them would assert a bug.
_INPUT_BASIS_KEYS = ("n_rows_in_tsv", "n_defined_rows_in")


def test_adding_defined_rows_does_not_move_any_undefined_scope_pooled_key(tmp_path):
    """THE BANKED 15 / 13 / 14-1 / 12-1 DO NOT MOVE UNDER THE EXTENSION.

    ⚠ ``out_rows`` MUST be split by ``row_class`` BEFORE rolling up. Letting the
    COMBINED list reach ``_roll_up`` folds tail rows into ``n_undefined_rows_in``
    and the occlusion twins, silently moving the pre-registered numbers. This
    test is what catches that.

    The two INPUT-BASIS keys are handled by EXACT MOVEMENT rather than equality:
    ``n_rows_in_tsv`` and ``n_defined_rows_in`` count the input file, so equality
    would be false by construction (and the banked run's own
    ``n_defined_rows_in`` is 353,074 -- it was never zero). Asserting the exact
    delta is strictly stronger than asserting nothing.
    """
    import pcs_panelwide_reclassify as R

    base_dir = tmp_path / "undefined_only"
    base_dir.mkdir()
    with_dir = tmp_path / "with_defined"
    with_dir.mkdir()

    added = (
        _pre_filter_tail_row(),
        _post_filter_tail_row(),
        _defined_pairs_row(
            "m2_region_00001",
            del_vid=CLEAN_DEL, del_pos=8000000,
            partner_vid=CLEAN_SNP, partner_pos=8000050,
            del_index=70004, partner_index=70005,
            del_lost=0.25, del_retained=11, partner_retained=12,
        ),
    )

    p1, b1, r1 = _region1_fixture(base_dir, extra_bim=_clean_bim_rows())
    p2, b2, r2 = _region1_fixture(
        with_dir, extra_pairs=added, extra_bim=_clean_bim_rows()
    )
    _o1, s1 = _run(R, p1, b1, r1)
    _o2, s2 = _run(R, p2, b2, r2)

    assert set(R.POOLED_KEYS) >= set(_BANKED_THIRTEEN), (
        "a pre-existing pooled key was RENAMED or REMOVED"
    )

    for key in _BANKED_THIRTEEN:
        if key in _INPUT_BASIS_KEYS:
            continue
        assert s1["pooled"][key] == s2["pooled"][key], (
            f"UNDEFINED-SCOPE KEY {key!r} MOVED when defined rows were added: "
            f"{s1['pooled'][key]!r} -> {s2['pooled'][key]!r}. The banked "
            f"15 / 13 / 14-1 / 12-1 are exactly these keys."
        )

    # NON-VACUITY: the run WITH defined rows really did classify them.
    assert s2["pooled"]["n_tail_rows_in"] == 2
    assert s1["pooled"]["n_tail_rows_in"] == 0
    assert s2["pooled"]["n_defined_rows_in"] == 3
    assert s1["pooled"]["n_defined_rows_in"] == 0

    # The two INPUT-BASIS keys move by EXACTLY the number of rows added.
    assert s2["pooled"]["n_rows_in_tsv"] == s1["pooled"]["n_rows_in_tsv"] + len(added)
    assert (
        s2["pooled"]["n_defined_rows_in"]
        == s1["pooled"]["n_defined_rows_in"] + len(added)
    )


# --------------------------------------------------------------------------- #
# 14. THE STAGED INVOCATION PARSES *HERE*, NOT INSIDE THE PERIMETER             #
# --------------------------------------------------------------------------- #

_STAGED_DOC_REL = (
    ".planning/debug/260901-PENDING-PASTE-POSTHOC-tail-prefilter-vs-postfilter-"
    "and-carrier-distribution.md"
)


def _fenced_bash_blocks(text: str):
    """Every ```bash fenced block's body, in document order."""
    blocks = []
    current = None
    for line in text.splitlines():
        stripped = line.strip()
        if current is None:
            if stripped.startswith("```") and "bash" in stripped:
                current = []
            continue
        if stripped.startswith("```"):
            blocks.append("\n".join(current))
            current = None
            continue
        current.append(line)
    assert current is None, "an unterminated ```bash fence in the staged doc"
    return blocks


def _staged_invocations(text: str):
    """Every ``pcs_panelwide_reclassify.py`` invocation, backslash-joined."""
    import shlex

    found = []
    for block in _fenced_bash_blocks(text):
        # Join backslash continuations FIRST: the staged commands are wrapped
        # across lines and a per-line scan would see only the first flag.
        joined = block.replace("\\\n", " ")
        for command in joined.splitlines():
            if "src/python/pcs_panelwide_reclassify.py" not in command:
                continue
            tokens = shlex.split(command, comments=True)
            # Strip the interpreter and the script path; keep the argv.
            while tokens and not tokens[0].startswith("-"):
                tokens.pop(0)
            found.append(tokens)
    return found


def test_the_staged_doc_argv_parses_against_the_declared_contract():
    """A STAGED TYPO MUST FAIL ON THIS NODE, NOT INSIDE THE PERIMETER.

    ``_build_parser`` is a DECLARED CROSS-TASK CONTRACT (T-rvu-05): the staged
    document's own argv is extracted here and fed to it, so a mistyped flag is a
    RED test on the HPC node rather than an ``error: unrecognized arguments``
    after the operator has already started an in-perimeter VM.
    """
    import pcs_panelwide_reclassify as R

    doc = PROJECT_ROOT / _STAGED_DOC_REL
    assert doc.exists(), f"the staged document is missing: {_STAGED_DOC_REL}"
    text = doc.read_text(encoding="utf-8")

    invocations = _staged_invocations(text)
    assert len(invocations) == 2, (
        f"expected BOTH staged invocations (the one-region smoke and the full "
        f"21-region run); found {len(invocations)}: {invocations}"
    )

    parsed = []
    for tokens in invocations:
        assert tokens, "an invocation with no flags at all"
        parsed.append(R._build_parser().parse_args(tokens))

    # The SMOKE run is narrowed and the FULL run is not — otherwise "smoke then
    # full" is two identical commands and the staging is decorative.
    narrowed = [p for p in parsed if p.region_ids is not None]
    assert len(narrowed) == 1, (
        f"exactly one staged invocation must carry --region-ids (the smoke); "
        f"got {[p.region_ids for p in parsed]}"
    )
    # Distinct outputs, or the second run silently overwrites the first.
    assert len({str(p.out) for p in parsed}) == 2
    assert len({str(p.summary) for p in parsed}) == 2

    # NEGATIVE CONTROL: one mutated flag must be REJECTED, so a green above is
    # evidence that the parser really vetted these tokens.
    mutated = text.replace("--pairs-tsv", "--pairs-tsvv", 1)
    assert mutated != text, "the flag mutation changed nothing"
    bad = _staged_invocations(mutated)
    assert any("--pairs-tsvv" in tokens for tokens in bad), (
        "the mutation did not land inside an extracted invocation"
    )
    with pytest.raises(SystemExit):
        for tokens in bad:
            R._build_parser().parse_args(tokens)
