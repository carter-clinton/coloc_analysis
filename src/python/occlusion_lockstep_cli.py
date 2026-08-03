"""The m3-04b CONSUME SEAM: CLI + path resolvers for the exclude-in-lockstep drop.

``src/python/drop_occluded_from_sumstats.py:49-56`` ("THE DEFERRED m3-04 SEAM — READ
BEFORE WIRING") names this module's plan. 07c built the REUSABLE filter and
deliberately left ``finemap.smk`` untouched because the m3-04 consume rule was
SUPERSEDED-PENDING-REPLAN. This is the replan's NC-State half.

A THIN WRAPPER, ON PURPOSE
--------------------------
Everything scientific happens in ``drop_occluded_from_sumstats``, which this module
CALLS and never re-implements. That module is at a verified 0-line diff: a second
implementation of the drop would be a second chance for the panel, the sumstats and
the region variant list to disagree about which variants exist, which is the exact
failure the pre-registered lockstep policy exists to prevent (osf.io/az52u, file
``trsx5``, POSTED 2026-07-10T13:32:22Z).

TWO SUBCOMMANDS
---------------
``filter-sumstats``  harmonized ``.tsv.bgz`` -> filtered ``.tsv.bgz``. The shipped
    filter writes PLAIN, UNCOMPRESSED bytes (``out_path.open("wb")``), so this
    subcommand filters to a temp plain file and then compresses with **bgzip**.
    ``run_susie_rss.R:275`` reads the sumstats with ``gunzip -c`` and
    ``collect_region_variants.py:40,56`` reads with ``compression="gzip"``: an
    uncompressed file wearing a ``.tsv.bgz`` name would fail at the consumer, far
    from the cause.

    If ``bgzip`` is absent this FAILS LOUDLY naming ``envs/python_stats.yml``. It
    does NOT fall back to ``gzip``: plain gzip is not BGZF, so the result would be
    unindexable by ``tabix`` while still reading fine — an env misconfiguration
    hidden behind a green run, discovered later and elsewhere.

``filter-variants``  the per-region variant list, plain TSV in and plain TSV out
    (that is what ``collect_region_variants`` emits and what
    ``run_susie_rss.R --variant-list`` reads). SAME function, SAME catalog, SAME
    ``(CHR,POS)`` key.

THE TWO PATH RESOLVERS
----------------------
:func:`lockstep_sumstats_path` and :func:`lockstep_variants_path` are what
``finemap.smk`` calls. They live here (not inline in the rule file) so they are
unit-testable without instantiating a Snakemake workflow.

BOTH ``run_finemap`` inputs are repointed, not one:
``ld_reference.smk::collect_region_variants`` pools EVERY harmonized file
ancestry-agnostically into ``{ld_reference}/variants/{region}.tsv``, so repointing
only the sumstats would let the occluded coordinate back in through
``run_finemap.input.variants``.

The gate is ANCESTRY-scoped. For every ancestry outside
``occlusion_lockstep.ancestries`` the returned string is CHARACTER-FOR-CHARACTER the
legacy expression, so Track-A / EUR frozen numerics cannot move. And when the
``occlusion_lockstep`` block is ABSENT the resolvers return legacy too: these
functions hand a path to a rule that reads scientific data, so "config absent ->
assume enabled" would silently redirect every AFR fine-map at a directory nothing in
that config declares. Fail-safe is CALLER-relative, and for this caller it means
change nothing.

Runs in smoke_dev py3.11 (stdlib + the 07c filter). No Hail, no perimeter, $0.
m3-06 stays HELD: this module touches nothing on the LD-conditioning path, and the
NaN-to-zero fill it once proposed is DEAD — occluded variants are EXCLUDED with
provenance, never zeroed.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from drop_occluded_from_sumstats import drop_occluded_from_sumstats

__all__ = [
    "filter_sumstats",
    "filter_variants",
    "lockstep_sumstats_path",
    "lockstep_variants_path",
    "main",
]

#: The env that carries bgzip + tabix (htslib=1.21). Named in the failure message so
#: an operator is told the fix, not just the symptom.
_BGZIP_ENV = "envs/python_stats.yml"

#: Default ancestries the lockstep applies to. The occlusion manifest is a by-product
#: of the AoU AFR native-plink panel build; the EUR chain head is the public UKBB
#: 337k panel, which carries no occlusion manifest at all.
_DEFAULT_ANCESTRIES = ["AFR"]

_DEFAULT_SUMSTATS_DIR = "data/processed/sumstats_harmonized_occl"
_DEFAULT_VARIANTS_DIR_NAME = "variants_occl"

#: The legacy (pre-m3-04b) variant-list subdirectory, ld_reference.smk:91.
_LEGACY_VARIANTS_DIR_NAME = "variants"


# --------------------------------------------------------------------------- #
# path resolvers (consumed by src/snakemake/rules/finemap.smk)                 #
# --------------------------------------------------------------------------- #

def _lockstep_block(config) -> dict:
    """The ``occlusion_lockstep`` config block, or ``{}`` when absent/malformed."""
    try:
        block = config.get("occlusion_lockstep", {})
    except AttributeError:
        return {}
    return dict(block) if isinstance(block, dict) else {}


def _lockstep_applies(ancestry, config) -> bool:
    """True when the occlusion filter applies to ``ancestry`` under ``config``.

    False (i.e. LEGACY paths) when the block is absent or empty, when
    ``enabled`` is false, or when ``ancestry`` is not listed. Every one of those
    is a "change nothing" answer, which is the only safe default for a resolver
    that decides which bytes a fine-map reads.
    """
    block = _lockstep_block(config)
    if not block:
        return False
    if not block.get("enabled", True):
        return False
    ancestries = block.get("ancestries", _DEFAULT_ANCESTRIES)
    return str(ancestry) in {str(a) for a in ancestries}


def lockstep_sumstats_path(trait, ancestry, config, harmonized_dir) -> str:
    """Resolve ``run_finemap.input.sumstats``.

    LOCKSTEP (ancestry gated in): ``{occlusion_lockstep.sumstats_dir}/{trait}.{ancestry}.tsv.bgz``
    LEGACY  (everything else)   : ``{harmonized_dir}/{trait}.{ancestry}.tsv.bgz``

    The legacy branch reproduces the pre-m3-04b expression with the same
    ``os.path.join`` call, so the string is byte-identical rather than merely
    equivalent.
    """
    basename = f"{trait}.{ancestry}.tsv.bgz"
    if not _lockstep_applies(ancestry, config):
        return os.path.join(harmonized_dir, basename)
    block = _lockstep_block(config)
    return os.path.join(block.get("sumstats_dir", _DEFAULT_SUMSTATS_DIR), basename)


def lockstep_variants_path(region, ancestry, config, ld_reference_dir) -> str:
    """Resolve ``run_finemap.input.variants``.

    LOCKSTEP: ``{ld_reference_dir}/{occlusion_lockstep.variants_dir_name}/{region}.tsv``
    LEGACY  : ``{ld_reference_dir}/variants/{region}.tsv``

    The occluded coordinate must leave the region variant list as well as the
    sumstats: ``collect_region_variants`` pools all harmonized files
    ancestry-agnostically, so a sumstats-only filter is not a lockstep.
    """
    basename = f"{region}.tsv"
    if not _lockstep_applies(ancestry, config):
        return os.path.join(ld_reference_dir, _LEGACY_VARIANTS_DIR_NAME, basename)
    block = _lockstep_block(config)
    return os.path.join(
        ld_reference_dir,
        block.get("variants_dir_name", _DEFAULT_VARIANTS_DIR_NAME),
        basename,
    )


# --------------------------------------------------------------------------- #
# the two filter subcommands                                                   #
# --------------------------------------------------------------------------- #

def _resolve_bgzip() -> str:
    """Locate ``bgzip`` or raise a message that names the fix.

    NO ``gzip`` FALLBACK. plain gzip is not BGZF: the file would read fine and be
    un-indexable by ``tabix``, so the mirror would silently lose parity with the
    ``sumstats.smk:157`` output it shadows and the breakage would surface much later,
    somewhere else.
    """
    bgzip = shutil.which("bgzip")
    if bgzip:
        return bgzip
    raise RuntimeError(
        "bgzip not found on PATH. The occlusion-filtered sumstats mirror MUST be "
        "real bgzip (the consumers read it with `gunzip -c` and pandas "
        "compression='gzip', and it is tabix-indexed exactly as sumstats.smk:157 "
        f"does). bgzip ships in {_BGZIP_ENV} (htslib); run this rule under that "
        "conda env. Refusing to fall back to plain gzip: that would produce a "
        "readable but UN-INDEXABLE file and hide the env misconfiguration behind a "
        "green run."
    )


def filter_sumstats(in_path, catalog_path, out_path,
                    counts_json=None) -> dict:
    """Occlusion-filter a harmonized sumstats file and re-bgzip it."""
    in_path, catalog_path, out_path = Path(in_path), Path(catalog_path), Path(out_path)
    bgzip = _resolve_bgzip()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="occlusion_filter_") as tmpdir:
        plain = Path(tmpdir) / "filtered.tsv"
        counts = drop_occluded_from_sumstats(in_path, catalog_path, plain)
        # bgzip -c: compress to stdout so the temp file is never mutated in place
        # and a failed compression can never leave a truncated .bgz behind.
        with out_path.open("wb") as fout:
            subprocess.run([bgzip, "-c", str(plain)], stdout=fout, check=True)

    _emit_counts(counts, counts_json)
    return counts


def filter_variants(in_path, catalog_path, out_path,
                    counts_json=None) -> dict:
    """Occlusion-filter a per-region variant list. Plain TSV in, plain TSV out."""
    in_path, catalog_path, out_path = Path(in_path), Path(catalog_path), Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    counts = drop_occluded_from_sumstats(in_path, catalog_path, out_path)
    _emit_counts(counts, counts_json)
    return counts


def _emit_counts(counts: dict, counts_json) -> None:
    """Print the counts as JSON, and persist them when a path is given.

    The counts are the auditable half of the lockstep: ``n_in - n_dropped == n_out``
    is what makes "the panel and the sumstats dropped the same variants" a checkable
    claim rather than an assertion.
    """
    payload = json.dumps(counts, indent=2)
    if counts_json is not None:
        counts_path = Path(counts_json)
        counts_path.parent.mkdir(parents=True, exist_ok=True)
        counts_path.write_text(payload + "\n")
    print(payload)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="occlusion_lockstep_cli",
        description=(
            "Apply the pre-registered exclude-in-lockstep occlusion drop "
            "(osf.io/az52u, file trsx5) to the harmonized sumstats and to the "
            "per-region variant list, using the SAME catalog and the SAME "
            "(chr, pos_grch37) key the LD panel exclusion was derived from."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("filter-sumstats", "filter a harmonized .tsv.bgz and re-bgzip the result"),
        ("filter-variants", "filter a per-region variant list (plain TSV in/out)"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--in", dest="in_path", required=True)
        p.add_argument("--catalog", dest="catalog_path", required=True,
                       help="the enriched occlusion catalog (needs chr + pos_grch37)")
        p.add_argument("--out", dest="out_path", required=True)
        p.add_argument("--counts-json", dest="counts_json", default=None,
                       help="also write {n_in,n_dropped,n_out} here")

    args = parser.parse_args(argv)
    handler = filter_sumstats if args.command == "filter-sumstats" else filter_variants
    handler(args.in_path, args.catalog_path, args.out_path,
            counts_json=args.counts_json)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
