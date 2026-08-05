"""RED-first tests for src/python/assemble_occlusion_catalog.py (m3-04b, Task 1).

THE PROBLEM THIS MODULE EXISTS TO SOLVE. Four functions shipped in m3-07b/07c with
**ZERO production callers**: ``occlusion_manifest.add_grch37_positions``,
``occlusion_manifest.enrich_occlusion_manifest``,
``occlusion_manifest.aggregate_manifests`` (alias ``build_occlusion_catalog``) and
``occlusion_present_rate_scan.scan_present_rate``. Code with no caller is not a
pipeline; it is a promise. The assembler is the caller: it turns the per-region
Stage-A manifests + the hg38ToHg19 chain + the 9 public AFR harmonized sumstats
into ONE genome-wide enriched occlusion catalog — simultaneously the Angle-1/3
catalog seed and the artifact the lockstep sumstats drop keys on
(``drop_occluded_from_sumstats``, 07c).

THE LOAD-BEARING CASE IS THE EMPTY ONE (T1.3). On today's tree there are ZERO
per-region manifests (the AoU fire has not banked any). A naive assembler that just
delegates to ``enrich_occlusion_manifest`` hits its empty-input short-circuit
(``occlusion_manifest.py:361-363``), which writes the INPUT's columns and therefore
NO ``pos_grch37`` — at which point ``drop_occluded_from_sumstats._load_manifest_keys``
raises its (correct, deliberate) fail-closed Stage-A error and the whole m3-04b
consume seam is UNRUNNABLE until the fire lands. The empty catalog must be
SCHEMA-COMPLETE so the drop is an audited, honest ``n_dropped == 0`` no-op today and
becomes live the moment real manifests arrive, with zero further wiring.

RED-for-the-right-reason: ``assemble_occlusion_catalog`` does not exist yet. It is
imported INSIDE each test body (mirroring ``test_occlusion_lockstep_drop.py:30-40``)
so pytest COLLECTS cleanly and each test fails as a test failure, NOT a collection
error.

Runs in smoke_dev py3.11 (pandas + pyliftover). No Hail, no perimeter, $0.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# NOTE: NO module-level ``import assemble_occlusion_catalog`` — see the docstring.

#: The ONLY chain in-repo, and the correct direction (GRCh38 -> GRCh37).
_HG38_TO_HG19_CHAIN = (
    PROJECT_ROOT / "data" / "external" / "liftover" / "hg38ToHg19.over.chain.gz"
)

#: Settled hinge anchors [m3_region1_occlusion_hinge_check.md:40-48].
_SNP_C_B38 = 5_922_718      # the occluded variant, GRCh38
_SNP_C_B37 = 5_982_778      # ... and its GRCh37 coordinate

_HARMONIZED_HEADER = [
    "CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF", "N",
    "SNP_ID", "TRAIT", "ANCESTRY", "BUILD",
]


def _require_chain() -> Path:
    """Skip-if-absent guard for the hg38ToHg19 chain (mirrors
    ``test_occlusion_manifest.py:68-73``; the chain IS present in-repo)."""
    if not _HG38_TO_HG19_CHAIN.exists():
        pytest.skip(f"chain file not present: {_HG38_TO_HG19_CHAIN}")
    return _HG38_TO_HG19_CHAIN


def _region1_rows() -> list[tuple]:
    """Canonical region-1 ``.bim`` fixture, loaded by file path from the single
    source of truth (mirrors ``test_occlusion_manifest.py:76-88``). Duplicating the
    coordinate table here would invite exactly the drift T-m3-07a-02 warns about."""
    import importlib.util

    path = Path(__file__).with_name("test_occlusion_span_filter.py")
    spec = importlib.util.spec_from_file_location("_m3_occlusion_span_fixture", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # safe: its impl imports are function-local
    return list(mod._REGION1_BIM_ROWS)


def _vid_at(rows: list[tuple], bp: int) -> str:
    hits = [r[1] for r in rows if int(r[3]) == bp]
    assert len(hits) == 1
    return hits[0]


def _write_region_manifest(tmp_path: Path, region_id: str) -> Path:
    """One per-region Stage-A manifest, built by the REAL producer.

    ``append_region_manifest`` is used deliberately: a hand-typed schema here would
    be a guess, and a guess is exactly how the producer/consumer seam broke twice
    already (``63bdb59``, ``8d4087a``).
    """
    import occlusion_manifest as om

    path = tmp_path / region_id / "occlusion_manifest.tsv"
    path.parent.mkdir(parents=True, exist_ok=True)
    om.append_region_manifest(path, om.build_region_records(region_id, _region1_rows()))
    return path


def _write_sumstats(path: Path, positions: list[tuple[int, int]],
                    trait: str = "bmi") -> Path:
    """A harmonized-schema AFR sumstats TSV with one row per (chr, pos)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(_HARMONIZED_HEADER)]
    for chrom, pos in positions:
        lines.append("\t".join(str(x) for x in [
            chrom, pos, "A", "G", 0.012, 0.004, 3.1e-3, 0.21, 15000,
            f"{chrom}:{pos}:A:G", trait, "AFR", "GRCh37",
        ]))
    path.write_text("\n".join(lines) + "\n")
    return path


def _write_excludelist(tmp_path: Path, region_id: str,
                       variant_ids: list[str]) -> Path:
    """A ``{region_id}.occluded.excludelist`` exactly as the driver writes it
    (``run_native_ld_panel.py:806-808``): one bare variant id per line."""
    path = tmp_path / f"{region_id}.occluded.excludelist"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{vid}\n" for vid in variant_ids))
    return path


# --------------------------------------------------------------------------- #
# T1.1 the rollup: per-region manifests -> ONE genome-wide catalog             #
# --------------------------------------------------------------------------- #

def test_catalog_rolls_up_per_region_manifests(tmp_path):
    """Two per-region Stage-A manifests roll up into one catalog carrying BOTH
    regions' rows, de-duplicated on (region_id, variant_id).

    This is the assertion that gives ``aggregate_manifests`` / ``build_occlusion_catalog``
    a production caller: without it the genome-wide census the OSF amendment-update
    pre-registers (osf.io/az52u, file trsx5) has no producer at all.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import pandas as pd
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    m2 = _write_region_manifest(tmp_path, "m2_region_00002")
    out = tmp_path / "occlusion_catalog_m3.tsv"

    res = aoc.assemble_occlusion_catalog([m1, m2], chain, [], out)

    df = pd.read_csv(out, sep="\t")
    assert len(df) == 10                                   # 5 occluded x 2 regions
    assert set(df["region_id"]) == {"m2_region_00001", "m2_region_00002"}
    assert not df.duplicated(subset=["region_id", "variant_id"]).any()
    assert res["n_regions"] == 2
    assert res["n_variants"] == 10
    assert res["source"] == "stage_a_manifest"


def test_catalog_is_idempotent_on_a_repeated_manifest(tmp_path):
    """The SAME manifest supplied twice (a resumed/replayed rollup) yields the same
    row count — the dedup key is (region_id, variant_id), not file identity."""
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import pandas as pd
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    out = tmp_path / "occlusion_catalog_m3.tsv"

    aoc.assemble_occlusion_catalog([m1, m1], chain, [], out)

    df = pd.read_csv(out, sep="\t")
    assert len(df) == 5


# --------------------------------------------------------------------------- #
# T1.2 the Stage-B columns are on the catalog                                  #
# --------------------------------------------------------------------------- #

def test_catalog_carries_stage_b_columns(tmp_path):
    """The catalog is ENRICHED, not a bare Stage-A rollup: ``pos_grch37``,
    ``chain_sha256`` and all three ``STAGE_B_TRAIT_COLUMNS`` are present, and
    ``pos_grch37`` reproduces the settled hinge anchor for snpC.

    ``pos_grch37`` is the drop key (``drop_occluded_from_sumstats``,
    ``_MANIFEST_POS``); ``chain_sha256`` is what makes those build-37 coordinates
    reproducible from a recorded chain identity rather than taken on faith.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import pandas as pd
    import occlusion_manifest as om
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    out = tmp_path / "occlusion_catalog_m3.tsv"

    aoc.assemble_occlusion_catalog([m1], chain, [], out)

    df = pd.read_csv(out, sep="\t")
    for col in ["chr", "pos_grch37", "chain_sha256", *om.STAGE_B_TRAIT_COLUMNS]:
        assert col in df.columns, f"catalog missing Stage-B column {col!r}"

    snp_c = df[df["pos_grch38"] == _SNP_C_B38]
    assert len(snp_c) == 1
    assert int(snp_c.iloc[0]["pos_grch37"]) == _SNP_C_B37
    assert snp_c.iloc[0]["chain_sha256"] == om.chain_sha256(chain)


# --------------------------------------------------------------------------- #
# T1.3 THE LOAD-BEARING ONE: an EMPTY catalog is still SCHEMA-COMPLETE         #
# --------------------------------------------------------------------------- #

def test_empty_catalog_still_carries_stage_b_columns(tmp_path):
    """ZERO manifests -> a HEADER-ONLY catalog whose header still carries ``chr``
    and ``pos_grch37``, and which ``drop_occluded_from_sumstats`` consumes as a
    clean ``n_dropped == 0`` no-op WITHOUT raising.

    This is the state of the tree TODAY (the AoU fire has banked no manifests), so
    this is the case that decides whether the m3-04b seam can be wired now and
    permanently or has to be wired "later" — the wire-it-later-and-forget failure
    mode this phase has already paid for twice.

    Naive delegation to ``enrich_occlusion_manifest`` FAILS this test: its
    empty-input branch (``occlusion_manifest.py:361-363``) short-circuits BEFORE the
    lift and writes the input's columns only, so ``pos_grch37`` is absent and
    ``_load_manifest_keys`` fails CLOSED — correctly, but on a legitimate no-op.
    """
    chain = _require_chain()
    import drop_occluded_from_sumstats as dof
    import assemble_occlusion_catalog as aoc

    out = tmp_path / "occlusion_catalog_m3.tsv"
    res = aoc.assemble_occlusion_catalog([], chain, [], out)

    header = out.read_text().splitlines()[0].split("\t")
    assert "chr" in header, "the EMPTY catalog must still declare the drop key's chr"
    assert "pos_grch37" in header, (
        "the EMPTY catalog must still declare pos_grch37, or the lockstep drop "
        "fails CLOSED on a legitimate no-op and the seam is unrunnable"
    )
    assert len(out.read_text().splitlines()) == 1, "header-only, zero data rows"
    assert res["n_variants"] == 0

    ss = _write_sumstats(tmp_path / "bmi.AFR.tsv", [(1, _SNP_C_B37), (1, 7_000_000)])
    filtered = tmp_path / "bmi.AFR.occl.tsv"
    counts = dof.drop_occluded_from_sumstats(ss, out, filtered)   # must NOT raise

    assert counts["n_dropped"] == 0
    assert counts["n_in"] == counts["n_out"] == 2
    assert filtered.read_bytes() == ss.read_bytes()   # an honest, byte-exact no-op


# --------------------------------------------------------------------------- #
# T1.4 present_rate comes from the REAL scan, and is persisted                 #
# --------------------------------------------------------------------------- #

def test_present_rate_is_joined_from_the_real_scan(tmp_path):
    """A synthetic AFR sumstats carrying the occluded variant's GRCh37 coordinate
    yields ``n_traits_present == 1``, ``n_traits_scanned == 1`` and a persisted
    ``present_rate`` of 1.0 on the snpC row.

    This gives ``scan_present_rate`` (07c T3) its production caller and closes the
    first of the two pre-existing ``63bdb59`` consumer notes: present_rate was
    derivable as k/n but never PERSISTED as a catalog column.

    The join is (chr, pos_grch37) POST-liftover — GRCh38 5922718 -> GRCh37 5982778,
    the settled hinge anchor. A GRCh38-keyed join matches nothing and would silently
    blank the rs182965575 "present in 7 of 9" evidence.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import pandas as pd
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    ss = _write_sumstats(tmp_path / "bmi.AFR.tsv",
                         [(1, _SNP_C_B37), (1, 7_000_000)], trait="bmi")
    out = tmp_path / "occlusion_catalog_m3.tsv"

    aoc.assemble_occlusion_catalog([m1], chain, [ss], out)

    df = pd.read_csv(out, sep="\t")
    assert "present_rate" in df.columns, (
        "present_rate must be PERSISTED, not left derivable-in-principle"
    )
    snp_c = df[df["pos_grch38"] == _SNP_C_B38].iloc[0]
    assert int(snp_c["n_traits_present"]) == 1
    assert int(snp_c["n_traits_scanned"]) == 1
    assert float(snp_c["present_rate"]) == pytest.approx(1.0)
    assert "bmi" in str(snp_c["traits_present"])

    # a variant the scan did NOT find is an honest k=0, never a missing row
    other = df[df["pos_grch38"] == 1_980_475].iloc[0]
    assert int(other["n_traits_present"]) == 0
    assert int(other["n_traits_scanned"]) == 1
    assert float(other["present_rate"]) == pytest.approx(0.0)


def test_assembler_surfaces_the_scan_parse_health(tmp_path):
    """HIGH-4 at the catalog boundary: the scan's parse health is REPORTED.

    ``n_scan_unparseable``, NOT ``n_unparseable`` — the latter is already taken by the
    DEGRADED excludelist path (``assemble_occlusion_catalog.py:341, :382, :439``) and
    means something else entirely (unparseable excludelist LINES, not unparseable
    sumstats COORDINATES). Colliding them would make the catalog's own audit numbers
    ambiguous, which is the failure mode this whole plan is closing.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    ss1 = _write_sumstats(tmp_path / "bmi.AFR.tsv",
                          [(1, _SNP_C_B37), (1, 7_000_000)], trait="bmi")
    ss2 = _write_sumstats(tmp_path / "ldl.AFR.tsv", [(1, 7_000_000)], trait="ldl")
    out = tmp_path / "occlusion_catalog_m3.tsv"

    res = aoc.assemble_occlusion_catalog([m1], chain, [ss1, ss2], out)

    assert res["n_files_scanned"] == 2
    assert res["n_distinct_traits_scanned"] == 2
    assert res["n_scan_rows_seen"] == 3
    assert res["n_scan_rows_parsed"] == 3
    assert res["n_scan_unparseable"] == 0
    assert "n_unparseable" in res, (
        "the DEGRADED excludelist counter must survive under its own name"
    )
    assert res["n_unparseable"] == 0


# --------------------------------------------------------------------------- #
# T1.5 / T1.6 degraded reconstruction from the excludelists                    #
# --------------------------------------------------------------------------- #

def test_degraded_reconstruction_from_excludelists(tmp_path):
    """When the per-region Stage-A manifests never reached NC State, the catalog can
    be rebuilt in DEGRADED form from the ``{region_id}.occluded.excludelist`` objects
    (which ARE uploaded, ``run_native_ld_panel.py:937``).

    The reconstruction recovers the identity of every dropped variant but NOT the
    ref-span / occluding-deletion attribution, so those columns are EXPLICITLY NA and
    every row is stamped ``provenance_source == "excludelist_degraded"``. The loss is
    then visible IN the artifact rather than inferred from its absence.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import pandas as pd
    import assemble_occlusion_catalog as aoc

    e1 = _write_excludelist(tmp_path, "m2_region_00001",
                            [f"1:{_SNP_C_B38}:A:G", "1:1980475:A:G"])
    e2 = _write_excludelist(tmp_path, "m2_region_00002", ["1:8375822:A:G"])
    out = tmp_path / "occlusion_catalog_m3.tsv"

    res = aoc.assemble_occlusion_catalog(
        [], chain, [], out, excludelist_paths=[e1, e2], allow_degraded=True,
    )

    df = pd.read_csv(out, sep="\t")
    assert len(df) == 3
    assert set(df["region_id"]) == {"m2_region_00001", "m2_region_00002"}
    assert set(df["provenance_source"]) == {"excludelist_degraded"}
    assert res["source"] == "excludelist_degraded"

    snp_c = df[df["variant_id"] == f"1:{_SNP_C_B38}:A:G"].iloc[0]
    assert str(snp_c["chr"]) == "1"
    assert int(snp_c["pos_grch38"]) == _SNP_C_B38
    assert snp_c["ref"] == "A"
    assert snp_c["alt"] == "G"
    assert "reference-occlusion" in str(snp_c["reason"])
    assert int(snp_c["pos_grch37"]) == _SNP_C_B37      # still lifted, still joinable

    # the attribution the excludelist cannot carry is EXPLICITLY missing
    for col in ["ref_span_start_grch38", "ref_span_end_grch38",
                "occluding_deletion_id", "occluding_deletion_ref_len"]:
        assert df[col].isna().all(), (
            f"{col!r} is underivable from an excludelist and must be NA, never guessed"
        )


def test_degraded_reconstruction_refuses_without_flag(tmp_path):
    """The SAME inputs without ``allow_degraded`` RAISE, naming the missing manifests.

    Silent degradation is the failure mode this test exists to prevent: a catalog
    that quietly lost its occluding-deletion attribution still LOOKS like a catalog,
    and the pre-registration (osf.io/az52u) commits to auditable provenance, not to
    a plausible-looking substitute.
    """
    chain = _require_chain()
    import assemble_occlusion_catalog as aoc

    e1 = _write_excludelist(tmp_path, "m2_region_00001", [f"1:{_SNP_C_B38}:A:G"])
    e2 = _write_excludelist(tmp_path, "m2_region_00002", ["1:8375822:A:G"])
    out = tmp_path / "occlusion_catalog_m3.tsv"

    with pytest.raises(ValueError) as exc:
        aoc.assemble_occlusion_catalog(
            [], chain, [], out, excludelist_paths=[e1, e2],
        )

    msg = str(exc.value)
    assert "manifest" in msg.lower()
    assert "allow-degraded" in msg or "allow_degraded" in msg
    assert "m2_region_00001" in msg and "m2_region_00002" in msg
    assert not out.exists(), "a refused assembly must not leave a partial catalog"


def test_degraded_reconstruction_skips_unparseable_lines_loudly(tmp_path, capsys):
    """A line that is not ``chr:pos:ref:alt`` is SKIPPED with a loud STDERR warning
    and counted — never guessed at. A fabricated coordinate would drop the WRONG
    sumstats row, which is the exact harm the whole lockstep exists to prevent."""
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import pandas as pd
    import assemble_occlusion_catalog as aoc

    e1 = _write_excludelist(
        tmp_path, "m2_region_00001",
        [f"1:{_SNP_C_B38}:A:G", "rs182965575", "1:notanumber:A:G"],
    )
    out = tmp_path / "occlusion_catalog_m3.tsv"

    res = aoc.assemble_occlusion_catalog(
        [], chain, [], out, excludelist_paths=[e1], allow_degraded=True,
    )
    err = capsys.readouterr().err

    df = pd.read_csv(out, sep="\t")
    assert len(df) == 1
    assert res["n_unparseable"] == 2
    assert "rs182965575" in err
    assert "notanumber" in err


# --------------------------------------------------------------------------- #
# T1.7 egress cleanliness of the ASSEMBLED catalog's own header                #
# --------------------------------------------------------------------------- #

def test_catalog_columns_are_egress_clean(tmp_path):
    """REQ-AOU-LD-EGRESS re-asserted at the ROLLUP, not just at Stage A.

    ``tests/m3/test_occlusion_manifest.py:117`` guards the per-record Stage-A keys;
    this guards the assembled catalog's own header, so an individual-level column
    cannot ride out of the perimeter by being introduced during aggregation,
    enrichment or schema completion.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    out = tmp_path / "occlusion_catalog_m3.tsv"
    aoc.assemble_occlusion_catalog([m1], chain, [], out)

    header = out.read_text().splitlines()[0].split("\t")
    forbidden = ("sample", "person", "genotype", "individual", "_ac", "_an")
    for col in header:
        low = col.lower()
        for bad in forbidden:
            assert bad not in low, (
                f"individual-level column {col!r} on the catalog header "
                f"(contains {bad!r}) — REQ-AOU-LD-EGRESS"
            )


# --------------------------------------------------------------------------- #
# BLOCKER-4: a PARTIAL Stage-A rollup must not be stamped `stage_a_manifest`    #
# --------------------------------------------------------------------------- #
#
# `assemble_occlusion_catalog.py:352-362` overrides the excludelists when the rollup
# is merely NON-EMPTY, not when it is COMPLETE. The shipped NOTE says "the manifests
# carry strictly more provenance" — TRUE PER REGION, and FALSE AS A SET CLAIM the
# moment the manifest set is a SUBSET of the regions that have excludelists.
#
# The triggering state is live and already coded: `run_native_ld_panel.py:821-831`
# treats the per-region Stage-A append as BEST-EFFORT and, on any exception, prints a
# WARN and continues — WHILE THE EXCLUDELIST IS STILL WRITTEN. Every region that trips
# it becomes excludelist-only, and so does every region built before the producer-side
# manifest-upload fix.
#
# Verified end-to-end in the blast radius with 1 manifest + 1 excludelist-only region,
# both variants genuinely present in the sumstats:
#
#     return : {'n_regions': 1, ..., 'source': 'stage_a_manifest'}
#     catalog: 1 row — region m2_region_00002 ABSENT
#     drop   : {'n_in': 3, 'n_dropped': 1, 'n_out': 2}   # truth: 2 rows should have gone
#
# i.e. ORPHANED VARIANTS in the sumstats — the exact failure osf.io/az52u exists to
# forbid — wearing a `stage_a_manifest` provenance stamp that says everything is fine.


def test_partial_stage_a_rollup_refuses_the_stage_a_stamp(tmp_path):
    """1 Stage-A manifest + 1 excludelist-ONLY region -> ``ValueError``, nothing written.

    The raise must NAME the orphaned region, state the consequence, and name BOTH
    remedies — supplying the missing Stage-A manifests, or accepting the
    incompleteness explicitly with ``--allow-partial-manifest``.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    e2 = _write_excludelist(tmp_path, "m2_region_00002", ["1:8375822:A:G"])
    ss = _write_sumstats(tmp_path / "bmi.AFR.tsv", [(1, _SNP_C_B37), (1, 8_315_000)])
    out = tmp_path / "occlusion_catalog_m3.tsv"

    with pytest.raises(ValueError) as exc:
        aoc.assemble_occlusion_catalog(
            [m1], chain, [ss], out, excludelist_paths=[e2],
        )

    msg = str(exc.value)
    assert "m2_region_00002" in msg, "the ORPHANED region must be named"
    assert "allow-partial-manifest" in msg or "allow_partial_manifest" in msg
    assert "orphan" in msg.lower()
    assert not out.exists(), "a refused assembly must not leave a partial catalog"


def test_allow_partial_manifest_accepts_it_and_REPORTS_the_incompleteness(tmp_path):
    """The same input with ``allow_partial_manifest=True`` is accepted EXPLICITLY, and
    the incompleteness lands IN the artifact's provenance rather than being inferred
    from its absence: ``n_regions_excludelist_only == 1``."""
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    e2 = _write_excludelist(tmp_path, "m2_region_00002", ["1:8375822:A:G"])
    out = tmp_path / "occlusion_catalog_m3.tsv"

    res = aoc.assemble_occlusion_catalog(
        [m1], chain, [], out, excludelist_paths=[e2], allow_partial_manifest=True,
    )

    assert res["source"] == "stage_a_manifest"
    assert res["n_regions_excludelist_only"] == 1
    assert out.exists()


def test_full_coverage_still_stamps_stage_a_without_complaint(tmp_path, capsys):
    """When the manifest set DOES cover every excludelist region there is no raise,
    the stamp is ``stage_a_manifest``, and the STDERR note now claims only what is
    TRUE (coverage), not the unqualified set claim that was wrong."""
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    e1 = _write_excludelist(tmp_path, "m2_region_00001", [f"1:{_SNP_C_B38}:A:G"])
    out = tmp_path / "occlusion_catalog_m3.tsv"

    res = aoc.assemble_occlusion_catalog(
        [m1], chain, [], out, excludelist_paths=[e1],
    )
    err = capsys.readouterr().err

    assert res["source"] == "stage_a_manifest"
    assert res["n_regions_excludelist_only"] == 0
    assert "IGNORED" in err
    assert "covered" in err.lower(), (
        "the note must claim COVERAGE, which is what actually justifies ignoring them"
    )


def test_allow_partial_manifest_does_not_open_the_degraded_gate(tmp_path):
    """``allow_partial_manifest`` must NOT become a back door around
    ``allow_degraded``. The degraded reconstruction permanently loses the ref-span and
    occluding-deletion attribution the pre-registration commits to publishing, and it
    stays behind its own explicit flag."""
    chain = _require_chain()
    import assemble_occlusion_catalog as aoc

    e1 = _write_excludelist(tmp_path, "m2_region_00001", [f"1:{_SNP_C_B38}:A:G"])
    out = tmp_path / "occlusion_catalog_m3.tsv"

    with pytest.raises(ValueError) as exc:
        aoc.assemble_occlusion_catalog(
            [], chain, [], out, excludelist_paths=[e1],
            allow_partial_manifest=True,
        )

    assert "allow-degraded" in str(exc.value) or "allow_degraded" in str(exc.value)
    assert not out.exists()


# --------------------------------------------------------------------------- #
# THE 276/552 TRAP — the authoritative count is nunique(region_id), NOT len(df) #
# --------------------------------------------------------------------------- #

def test_expected_region_ids_is_276_not_552(tmp_path):
    """``config/ld_regions.tsv`` = header + **552 DATA ROWS** = **276 unique
    ``region_id`` x 2 ancestries (AFR, EUR)**.

    The authoritative count is ``nunique(region_id)`` FILTERED TO the ancestry —
    NEVER ``len(df)`` or ``wc -l``, which give 552/553 and would make any coverage
    assertion built on them fail 100% of the time. Asserting ``!= 552`` and
    ``!= 553`` explicitly is deliberate: it makes that specific regression fail LOUDLY
    with a message that names the trap, instead of looking like a data problem.
    """
    import assemble_occlusion_catalog as aoc

    regions_tsv = PROJECT_ROOT / "config" / "ld_regions.tsv"
    if not regions_tsv.exists():
        pytest.skip(f"region manifest not present: {regions_tsv}")

    ids = aoc.load_expected_region_ids(regions_tsv, ancestry="AFR")

    assert len(ids) == 276
    assert len(ids) != 552, "THE 276/552 TRAP: this is len(df), not nunique(region_id)"
    assert len(ids) != 553, "THE 276/552 TRAP: this is wc -l (header included)"
    assert all(isinstance(r, str) for r in ids)
    assert aoc.load_expected_region_ids(regions_tsv, ancestry="EUR") == ids, (
        "the 276 region ids are shared across both ancestries; only the ROWS double"
    )


def test_observed_region_not_in_the_expected_set_raises(tmp_path):
    """An OBSERVED region id absent from the expected set is naming drift or a
    crosswalk bug — a catalog keyed on ids nothing downstream recognises. RAISE."""
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    out = tmp_path / "occlusion_catalog_m3.tsv"

    with pytest.raises(ValueError) as exc:
        aoc.assemble_occlusion_catalog(
            [m1], chain, [], out, expected_region_ids={"m2_region_00999"},
        )

    assert "m2_region_00001" in str(exc.value)
    assert not out.exists()


def test_a_strict_subset_of_expected_regions_is_REPORTED_not_asserted(tmp_path):
    """Observed ⊂ expected -> NO raise; ``n_regions_expected`` / ``n_regions_missing``
    are REPORTED.

    A region with ZERO occluded variants legitimately writes no manifest
    (``assemble_occlusion_catalog.py:346-347`` / ``aggregate_manifests``), so
    ``n_regions == 276`` is NOT a valid invariant and must NEVER be asserted. Pinning
    the no-raise here is what stops a future reader from "tightening" this into a
    check that fails on every honest run.
    """
    chain = _require_chain()
    pytest.importorskip("pyliftover")
    import assemble_occlusion_catalog as aoc

    m1 = _write_region_manifest(tmp_path, "m2_region_00001")
    out = tmp_path / "occlusion_catalog_m3.tsv"
    expected = {f"m2_region_{i:05d}" for i in range(1, 11)}

    res = aoc.assemble_occlusion_catalog(   # must NOT raise
        [m1], chain, [], out, expected_region_ids=expected,
    )

    assert res["n_regions"] == 1
    assert res["n_regions_expected"] == 10
    assert res["n_regions_missing"] == 9
    assert out.exists()


def test_catalog_readme_documents_the_traits_present_serialization(tmp_path):
    """``traits_present`` serializes as a STRINGIFIED LIST, so a catalog reader gets
    a ``str`` not a ``list`` (the second pre-existing ``63bdb59`` consumer note).
    That is documented next to the artifact rather than fixed in the shipped,
    test-pinned ``enrich_occlusion_manifest`` serialization."""
    chain = _require_chain()
    import assemble_occlusion_catalog as aoc

    out = tmp_path / "occlusion_catalog_m3.tsv"
    aoc.assemble_occlusion_catalog([], chain, [], out)

    readme = Path(f"{out}.README.md")
    assert readme.exists()
    text = readme.read_text()
    assert "traits_present" in text
    assert "literal_eval" in text
