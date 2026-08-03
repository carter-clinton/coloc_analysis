"""RED-first tests for the m3-04b CONSUME SEAM (Task 2).

``src/python/drop_occluded_from_sumstats.py:49-56`` names this plan: the 07c filter
is REUSABLE but was deliberately left UNWIRED, because ``finemap.smk:89-93`` declared
the m3-04 consume rule SUPERSEDED-PENDING-REPLAN. This suite pins the replan.

WHAT IS BEING PINNED, AND WHY EACH CASE EXISTS
----------------------------------------------
**Two leaks, not one.** ``ld_reference.smk::collect_region_variants`` pools EVERY
harmonized file ancestry-agnostically into ``{ld_reference}/variants/{region}.tsv``
(``collect_region_variants.py`` OrderedDict dedup). Repointing only
``run_finemap.input.sumstats`` leaves the occluded coordinate alive in
``run_finemap.input.variants`` — the panel drops it, the sumstats drop it, and the
variant list quietly puts it back.

**The output really is compressed.** ``drop_occluded_from_sumstats`` writes PLAIN,
UNCOMPRESSED bytes by contract (``out_path.open("wb")``, no re-compression), while
``run_susie_rss.R:275`` reads with ``gunzip -c`` and ``collect_region_variants.py:40,56``
reads with ``compression="gzip"``. An uncompressed file wearing a ``.tsv.bgz`` name
would fail downstream, so the CLI must compress and must FAIL LOUDLY rather than
silently emit plain bytes.

**EUR / Track-A cannot move.** The resolved non-AFR path strings must be
character-for-character the legacy expressions. Track-A numerics are frozen and have
been byte-verified 16/16 in prior waves.

**``params.region_id`` is NOT this plan's to touch.** It feeds
``run_susie_rss.R --region``, which looks the id up in ``config/regions_curated.csv``.
The sibling ``resolve_ld_path(region_id=...)`` argument IS changed — by m3-04c, in a
later wave, deliberately so the two ``finemap.smk`` edits never collide.

ON bgzip IN THE TEST ENVIRONMENT (honest limitation, stated up front): ``bgzip``
ships in ``envs/python_stats.yml`` (htslib=1.21) and is NOT on the login PATH and NOT
in ``smoke_dev``, where this suite runs. The gzip-magic case therefore installs an
executable ``bgzip`` SHIM on PATH and asserts the CLI shells out to it and emits real
gzip bytes. That pins the plumbing (compressor invoked, output readable by
``gzip.open``, plain-bytes contract not leaking through) deterministically and
without a skip. It does NOT pin BGZF block structure or tabix-indexability — those
are exercised by ``rule occlusion_filter_sumstats`` under the real
``envs/python_stats.yml``, which also runs the ``tabix -f -S 1 -s 1 -b 2 -e 2``
mirroring ``sumstats.smk:157``.

RED-for-the-right-reason: ``occlusion_lockstep_cli`` does not exist yet. It is
imported INSIDE each test body so pytest COLLECTS cleanly and each test fails as a
test failure, NOT a collection error.

Runs in smoke_dev py3.11. No Hail, no perimeter, $0.
"""
from __future__ import annotations

import gzip
import json
import os
import stat
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# NOTE: NO module-level ``import occlusion_lockstep_cli`` — see the docstring.

_FINEMAP_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "finemap.smk"

#: GRCh37 hinge anchors (lifted): the occluded variant and two survivors.
_SNP_C_B37 = 5_982_778
_DEL3_B37 = 5_982_776

_HARMONIZED_HEADER = [
    "CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF", "N",
    "SNP_ID", "TRAIT", "ANCESTRY", "BUILD",
]

#: The emitted columns of collect_region_variants.py (plain TSV, header present).
_VARIANT_LIST_HEADER = ["CHR", "POS", "SNP_ID", "REF", "ALT"]


def _lockstep_config(**overrides) -> dict:
    """A config shaped like config/pipeline.yaml's occlusion_lockstep block."""
    block = {
        "enabled": True,
        "ancestries": ["AFR"],
        "catalog": "data/processed/occlusion/occlusion_catalog_m3.tsv",
        "sumstats_dir": "data/processed/sumstats_harmonized_occl",
        "variants_dir_name": "variants_occl",
    }
    block.update(overrides)
    return {"occlusion_lockstep": block}


def _write_sumstats(path: Path, positions: list[tuple[int, int]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(_HARMONIZED_HEADER)]
    for chrom, pos in positions:
        lines.append("\t".join(str(x) for x in [
            chrom, pos, "A", "G", 0.012, 0.004, 3.1e-3, 0.21, 15000,
            f"{chrom}:{pos}:A:G", "bmi", "AFR", "GRCh37",
        ]))
    path.write_text("\n".join(lines) + "\n")
    return path


def _write_bgzipped_sumstats(path: Path, positions: list[tuple[int, int]]) -> Path:
    """A gzip-compressed harmonized sumstats (BGZF is gzip-compatible, and the
    07c reader is ``gzip.open`` via ``_open_binary``)."""
    plain = path.with_suffix(".plain.tsv")
    _write_sumstats(plain, positions)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(plain.read_bytes()))
    plain.unlink()
    return path


def _write_variant_list(path: Path, positions: list[tuple[int, int]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(_VARIANT_LIST_HEADER)]
    for chrom, pos in positions:
        lines.append("\t".join(
            [str(chrom), str(pos), f"{chrom}:{pos}:A:G", "A", "G"]
        ))
    path.write_text("\n".join(lines) + "\n")
    return path


def _write_catalog(path: Path, occluded: list[tuple[int, int]]) -> Path:
    """A schema-minimal ENRICHED catalog: the drop is keyed on (chr, pos_grch37)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(["region_id", "variant_id", "chr", "pos_grch37"])]
    for chrom, pos in occluded:
        lines.append("\t".join(
            ["m2_region_00001", f"{chrom}:5922718:A:A", str(chrom), str(pos)]
        ))
    path.write_text("\n".join(lines) + "\n")
    return path


def _install_bgzip_shim(tmp_path: Path, monkeypatch) -> Path:
    """Put an executable ``bgzip`` on PATH that behaves like ``bgzip -c FILE``.

    htslib is not in smoke_dev (see the module docstring). The shim makes the
    gzip-magic assertion deterministic and skip-free; it deliberately does NOT
    emulate BGZF block structure, which is the Snakemake rule's business.
    """
    bindir = tmp_path / "shimbin"
    bindir.mkdir(parents=True, exist_ok=True)
    shim = bindir / "bgzip"
    shim.write_text(
        f"#!{sys.executable}\n"
        "import gzip, sys\n"
        "paths = [a for a in sys.argv[1:] if not a.startswith('-')]\n"
        "with open(paths[0], 'rb') as fh:\n"
        "    sys.stdout.buffer.write(gzip.compress(fh.read()))\n"
    )
    shim.chmod(shim.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}")
    return shim


# --------------------------------------------------------------------------- #
# T2.1 the filtered mirror is REALLY compressed                                #
# --------------------------------------------------------------------------- #

def test_filter_sumstats_cli_writes_real_gzip(tmp_path, monkeypatch):
    """``filter-sumstats`` given a bgzipped input and a ``.tsv.bgz`` out path emits a
    file that starts with the gzip magic ``\\x1f\\x8b`` and that ``gzip.open`` reads.

    THIS IS THE CASE THAT CATCHES THE SHIPPED MODULE'S PLAIN-BYTES OUTPUT.
    ``drop_occluded_from_sumstats`` writes UNCOMPRESSED bytes by contract; the
    consumers do not: ``run_susie_rss.R:275`` uses ``gunzip -c`` and
    ``collect_region_variants.py:40,56`` uses ``compression="gzip"``. A mirror that
    is plain bytes under a ``.bgz`` name fails at the consumer, far from the cause.
    """
    _install_bgzip_shim(tmp_path, monkeypatch)
    import occlusion_lockstep_cli as cli

    src = _write_bgzipped_sumstats(tmp_path / "bmi.AFR.tsv.bgz",
                                   [(1, _DEL3_B37), (1, _SNP_C_B37), (1, 7_000_000)])
    catalog = _write_catalog(tmp_path / "catalog.tsv", [(1, _SNP_C_B37)])
    out = tmp_path / "occl" / "bmi.AFR.tsv.bgz"

    cli.main(["filter-sumstats", "--in", str(src),
              "--catalog", str(catalog), "--out", str(out)])

    assert out.read_bytes()[:2] == b"\x1f\x8b", (
        "the filtered mirror must be REAL gzip, not plain bytes wearing a .bgz name"
    )
    with gzip.open(out, "rt") as fh:
        header = fh.readline().rstrip("\n").split("\t")
    assert header == _HARMONIZED_HEADER


def test_filter_sumstats_fails_loudly_without_bgzip(tmp_path, monkeypatch):
    """No ``bgzip`` on PATH -> a LOUD failure naming ``envs/python_stats.yml``.

    Falling back to plain ``gzip`` would produce a file that reads fine and cannot be
    tabix-indexed, hiding an env misconfiguration behind a green run. The mirror
    shadows ``sumstats.smk``'s bgzip+tabix output and must keep parity with it.
    """
    empty_bin = tmp_path / "emptybin"
    empty_bin.mkdir()
    monkeypatch.setenv("PATH", str(empty_bin))
    import occlusion_lockstep_cli as cli

    src = _write_bgzipped_sumstats(tmp_path / "bmi.AFR.tsv.bgz", [(1, 7_000_000)])
    catalog = _write_catalog(tmp_path / "catalog.tsv", [(1, _SNP_C_B37)])
    out = tmp_path / "occl" / "bmi.AFR.tsv.bgz"

    with pytest.raises(RuntimeError) as exc:
        cli.main(["filter-sumstats", "--in", str(src),
                  "--catalog", str(catalog), "--out", str(out)])

    msg = str(exc.value)
    assert "bgzip" in msg
    assert "python_stats.yml" in msg


# --------------------------------------------------------------------------- #
# T2.2 the counts survive the compression round trip                           #
# --------------------------------------------------------------------------- #

def test_filter_sumstats_preserves_counts(tmp_path, monkeypatch):
    """The emitted JSON satisfies ``n_in - n_dropped == n_out``, and ``n_out`` equals
    the DECOMPRESSED body-line count — the invariant that makes "the panel and the
    sumstats dropped the same variants" a checkable claim, re-asserted after the
    compression step this seam adds."""
    _install_bgzip_shim(tmp_path, monkeypatch)
    import occlusion_lockstep_cli as cli

    src = _write_bgzipped_sumstats(
        tmp_path / "bmi.AFR.tsv.bgz",
        [(1, _DEL3_B37), (1, _SNP_C_B37), (1, 7_000_000), (2, 500)],
    )
    catalog = _write_catalog(tmp_path / "catalog.tsv", [(1, _SNP_C_B37)])
    out = tmp_path / "occl" / "bmi.AFR.tsv.bgz"
    counts_json = tmp_path / "bmi.AFR.counts.json"

    cli.main(["filter-sumstats", "--in", str(src), "--catalog", str(catalog),
              "--out", str(out), "--counts-json", str(counts_json)])

    counts = json.loads(counts_json.read_text())
    assert counts["n_in"] == 4
    assert counts["n_dropped"] == 1
    assert counts["n_out"] == 3
    assert counts["n_in"] - counts["n_dropped"] == counts["n_out"]

    with gzip.open(out, "rt") as fh:
        body = [ln for ln in fh.read().splitlines() if ln.strip()][1:]
    assert len(body) == counts["n_out"]
    kept = [(int(ln.split("\t")[0]), int(ln.split("\t")[1])) for ln in body]
    assert (1, _SNP_C_B37) not in kept


# --------------------------------------------------------------------------- #
# T2.3 the variant list uses the SAME function, the SAME catalog, the SAME key  #
# --------------------------------------------------------------------------- #

def test_filter_variants_reuses_the_same_function(tmp_path):
    """``filter-variants`` drops the occluded (CHR,POS) from a plain 5-column variant
    list and leaves survivors BYTE-identical.

    "Same function" is not a style preference: a second implementation is a second
    chance for the panel, the sumstats and the variant list to disagree about which
    variants exist. The variant list is plain TSV in and plain TSV out — no
    compression — because that is what ``collect_region_variants`` emits and what
    ``run_susie_rss.R --variant-list`` reads.
    """
    import occlusion_lockstep_cli as cli

    src = _write_variant_list(
        tmp_path / "variants" / "FTO_16q12.tsv",
        [(1, _DEL3_B37), (1, _SNP_C_B37), (1, 7_000_000), (2, _SNP_C_B37)],
    )
    catalog = _write_catalog(tmp_path / "catalog.tsv", [(1, _SNP_C_B37)])
    out = tmp_path / "variants_occl" / "FTO_16q12.tsv"
    counts_json = tmp_path / "FTO_16q12.counts.json"

    cli.main(["filter-variants", "--in", str(src), "--catalog", str(catalog),
              "--out", str(out), "--counts-json", str(counts_json)])

    counts = json.loads(counts_json.read_text())
    assert counts["n_dropped"] == 1

    src_lines = [ln for ln in src.read_text().splitlines() if ln.strip()]
    out_lines = [ln for ln in out.read_text().splitlines() if ln.strip()]
    assert out_lines[0] == src_lines[0]                        # header verbatim
    expected = [ln for ln in src_lines[1:] if not ln.startswith(f"1\t{_SNP_C_B37}\t")]
    assert out_lines[1:] == expected                           # bytes + order verbatim
    # the chr2 twin at the same POS survives: the key is (CHR,POS), never POS-only
    assert any(ln.startswith(f"2\t{_SNP_C_B37}\t") for ln in out_lines[1:])


# --------------------------------------------------------------------------- #
# T2.4 - T2.6 the two path resolvers finemap.smk consumes                      #
# --------------------------------------------------------------------------- #

def test_afr_inputs_are_repointed():
    """With the seam enabled, BOTH resolved AFR inputs move: the sumstats to
    ``occlusion_lockstep.sumstats_dir`` and the variant list to ``variants_occl``.

    Repointing only the sumstats leaves ``collect_region_variants`` re-introducing
    the occluded coordinate through ``run_finemap.input.variants``.
    """
    import occlusion_lockstep_cli as cli

    cfg = _lockstep_config()

    sumstats = cli.lockstep_sumstats_path(
        "t2d", "AFR", cfg, "data/processed/sumstats_harmonized"
    )
    variants = cli.lockstep_variants_path(
        "FTO_16q12", "AFR", cfg, "data/processed/ld_reference"
    )

    assert sumstats == "data/processed/sumstats_harmonized_occl/t2d.AFR.tsv.bgz"
    assert variants == "data/processed/ld_reference/variants_occl/FTO_16q12.tsv"


@pytest.mark.parametrize("ancestry", ["EUR", "TRANS", "EAS", "HIS", "SAS"])
def test_non_afr_input_paths_are_byte_identical(ancestry):
    """For every ancestry NOT in ``occlusion_lockstep.ancestries`` the two resolved
    strings are CHARACTER-FOR-CHARACTER the legacy expressions.

    Track-A / EUR numerics are frozen; a resolver that "helpfully" normalised a
    separator or an extension would move them. The expected values are built with the
    same ``os.path.join`` the pre-m3-04b ``finemap.smk`` used, so this is an identity
    check against the real legacy expression rather than against a retyped literal.
    """
    import occlusion_lockstep_cli as cli

    cfg = _lockstep_config()
    harmonized_dir = "data/processed/sumstats_harmonized"
    ld_reference_dir = "data/processed/ld_reference"

    legacy_sumstats = os.path.join(harmonized_dir, f"bmi.{ancestry}.tsv.bgz")
    legacy_variants = os.path.join(ld_reference_dir, "variants", "FTO_16q12.tsv")

    assert cli.lockstep_sumstats_path(
        "bmi", ancestry, cfg, harmonized_dir) == legacy_sumstats
    assert cli.lockstep_variants_path(
        "FTO_16q12", ancestry, cfg, ld_reference_dir) == legacy_variants


def test_disabled_flag_restores_legacy_paths():
    """``enabled: false`` restores the legacy strings for AFR too. The kill switch
    works, so the seam can be taken out of the DAG without editing a rule."""
    import occlusion_lockstep_cli as cli

    cfg = _lockstep_config(enabled=False)
    harmonized_dir = "data/processed/sumstats_harmonized"
    ld_reference_dir = "data/processed/ld_reference"

    assert cli.lockstep_sumstats_path("t2d", "AFR", cfg, harmonized_dir) == os.path.join(
        harmonized_dir, "t2d.AFR.tsv.bgz")
    assert cli.lockstep_variants_path(
        "FTO_16q12", "AFR", cfg, ld_reference_dir) == os.path.join(
        ld_reference_dir, "variants", "FTO_16q12.tsv")


def test_absent_config_block_is_fail_safe_legacy():
    """A config with NO ``occlusion_lockstep`` block resolves to the LEGACY paths.

    FAIL-SAFE DEFAULT, CALLER-RELATIVE (the 2026-07-15 lesson): these resolvers hand
    a path to a rule that reads SCIENTIFIC DATA. "Config absent -> assume enabled"
    would silently redirect every AFR fine-map at a directory nothing in that config
    declares, which is a data-integrity failure, not a convenience. Absent config
    must therefore mean "change nothing".
    """
    import occlusion_lockstep_cli as cli

    harmonized_dir = "data/processed/sumstats_harmonized"
    ld_reference_dir = "data/processed/ld_reference"

    for cfg in ({}, {"occlusion_lockstep": {}}):
        assert cli.lockstep_sumstats_path(
            "t2d", "AFR", cfg, harmonized_dir) == os.path.join(
            harmonized_dir, "t2d.AFR.tsv.bgz")
        assert cli.lockstep_variants_path(
            "FTO_16q12", "AFR", cfg, ld_reference_dir) == os.path.join(
            ld_reference_dir, "variants", "FTO_16q12.tsv")


# --------------------------------------------------------------------------- #
# T2.7 the m3-04c guard rail: params.region_id is NOT this plan's to touch     #
# --------------------------------------------------------------------------- #

def test_params_region_id_is_untouched():
    """``run_finemap.params.region_id`` still resolves through ``REGION_SAFE_TO_ID``.

    It feeds ``run_susie_rss.R --region``, which looks the id up in
    ``config/regions_curated.csv`` — swapping it would break the R script's region
    lookup. m3-04c DOES change the sibling ``resolve_ld_path(region_id=...)``
    argument (the panel-reachability crosswalk); this pin is the guard rail that
    keeps the two edits from being conflated.

    Asserted at SOURCE level rather than as a pure-function check: ``params.region_id``
    is a Snakemake rule directive with no importable callable, and instantiating a
    workflow here would drag in the whole DAG (which currently cannot resolve an AFR
    LD panel on this tree).
    """
    src = _FINEMAP_SMK.read_text()

    assert "region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region]," in src, (
        "run_finemap.params.region_id must still translate the safe slug via "
        "REGION_SAFE_TO_ID"
    )
    assert "region_id=REGION_SAFE_TO_ID[wildcards.region]," in src, (
        "run_finemap.input.ld_matrix's resolve_ld_path(region_id=...) argument is "
        "m3-04c's to change, not m3-04b's"
    )
    assert src.count("REGION_SAFE_TO_ID") == 3, (
        "REGION_SAFE_TO_ID occurrences in finemap.smk changed (expected 3: the "
        "explanatory comment, the resolve_ld_path argument, and params.region_id)"
    )


def test_finemap_smk_routes_both_inputs_through_the_lockstep_seam():
    """``finemap.smk`` calls BOTH resolvers exactly once each, and no longer carries
    the stale SUPERSEDED-PENDING-REPLAN declaration the replan discharges."""
    src = _FINEMAP_SMK.read_text()

    assert src.count("lockstep_sumstats_path") == 1
    assert src.count("lockstep_variants_path") == 1
    assert "SUPERSEDED-PENDING-REPLAN" not in src, (
        "the m3-02e (B-1) boundary block must record that the replan LANDED as "
        "m3-04b + m3-04c"
    )
    assert "occlusion_lockstep" in src
    # the legacy expressions are retained as audit comments, matching the house
    # style already used for ld_matrix at :112-116
    assert "# OLD: sumstats=" in src
    assert "# OLD: variants=" in src
