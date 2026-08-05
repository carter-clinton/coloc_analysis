#!/usr/bin/env python
import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def summarize_file(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text())
    cs = data.get("credible_sets") or {}

    variant_total = 0
    cs_sizes: List[str] = []
    top_record = None
    top_pip = 0.0

    for name, entries in cs.items():
        size = len(entries)
        cs_sizes.append(f"{name}:{size}")
        variant_total += size
        for entry in entries:
            pip = float(entry.get("pip", 0.0))
            if pip >= top_pip:
                top_record = entry
                top_pip = pip

    pip_source = data.get("pip") or []
    if isinstance(pip_source, dict):
        pip_iter = pip_source.values()
    elif isinstance(pip_source, (list, tuple, set)):
        pip_iter = pip_source
    else:
        pip_iter = [pip_source]
    pip_nonzero = sum(
        1 for value in pip_iter if value not in (None, "") and float(value) > 0.0
    )

    summary = {
        "trait": data.get("trait"),
        "ancestry": data.get("ancestry"),
        "method": data.get("method"),
        "region_id": data.get("region_id"),
        "status": data.get("status"),
        "credible_sets": len(cs),
        "credible_set_sizes": ";".join(cs_sizes),
        "variants_in_cs": variant_total,
        "pip_nonzero": pip_nonzero,
        "top_chr": top_record.get("CHR") if top_record else None,
        "top_pos": top_record.get("POS") if top_record else None,
        "top_pip": top_pip if top_record else None,
        "top_beta": top_record.get("BETA") if top_record else None,
        "top_se": top_record.get("SE") if top_record else None,
        "sumstats": data.get("sumstats"),
        "ld_dir": data.get("ld_dir"),
        "output_path": str(path),
        # 260805-o7o (m3-04c blast radius, FINDING I). Everything below is
        # APPENDED -- see the note at FIELDNAMES. ld_dir above is the CONSTANT
        # config["finemap"]["ld_reference_dir"]; ld_matrix is the panel this row
        # was actually computed on.
        "ld_matrix": data.get("ld_matrix"),
        "ld_file_declared": data.get("ld_file_declared"),
        "ld_authoritative": data.get("ld_authoritative"),
        "ld_status": data.get("ld_status"),
        "ld_overlap": data.get("ld_overlap"),
        "ld_overlap_fraction": data.get("ld_overlap_fraction"),
        "ld_allele_aware": data.get("ld_allele_aware"),
        "ld_allele_exact": data.get("ld_allele_exact"),
        "ld_allele_flipped": data.get("ld_allele_flipped"),
        "ld_allele_dropped_ambiguous": data.get("ld_allele_dropped_ambiguous"),
        "ld_allele_dropped_palindromic": data.get("ld_allele_dropped_palindromic"),
        "ld_allele_dropped_mismatch": data.get("ld_allele_dropped_mismatch"),
        "ld_allele_dropped_unusable": data.get("ld_allele_dropped_unusable"),
        "ld_allele_catalog_join": data.get("ld_allele_catalog_join"),
    }
    return summary


def summarize_inputs(paths: Iterable[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for input_path in paths:
        path = Path(input_path)
        if not path.exists():
            continue
        try:
            rows.append(summarize_file(path))
        except json.JSONDecodeError as err:
            rows.append(
                {
                    "trait": None,
                    "ancestry": None,
                    "method": None,
                    "region_id": path.stem,
                    "status": f"json_error: {err}",
                    "credible_sets": 0,
                    "credible_set_sizes": "",
                    "variants_in_cs": 0,
                    "pip_nonzero": 0,
                    "top_chr": None,
                    "top_pos": None,
                    "top_pip": None,
                    "top_beta": None,
                    "top_se": None,
                    "sumstats": None,
                    "ld_dir": None,
                    "output_path": str(path),
                    # 260805-o7o (FINDING I). This dict MUST stay key-for-key in
                    # parity with `summary` above. A divergence here is a silent
                    # COLUMN SHIFT for exactly the rows that already failed --
                    # the least-inspected rows in the table. Pinned by
                    # tests/m3/test_finemap_summary_panel_visible.py.
                    "ld_matrix": None,
                    "ld_file_declared": None,
                    "ld_authoritative": None,
                    "ld_status": None,
                    "ld_overlap": None,
                    "ld_overlap_fraction": None,
                    "ld_allele_aware": None,
                    "ld_allele_exact": None,
                    "ld_allele_flipped": None,
                    "ld_allele_dropped_ambiguous": None,
                    "ld_allele_dropped_palindromic": None,
                    "ld_allele_dropped_mismatch": None,
                    "ld_allele_dropped_unusable": None,
                    "ld_allele_catalog_join": None,
                }
            )
    return rows


# 260805-o7o (m3-04c blast radius, FINDING I). finemap_summary.tsv was
# PANEL-BLIND: the only LD column was `ld_dir`, which is the CONSTANT
# config["finemap"]["ld_reference_dir"] and is therefore identical on every row.
# A reader could not tell an AoU-panel row from a 1kG-panel row -- and after the
# ~11-day fire, that table is what the manuscript is built from.
#
# `ld_matrix` is the panel this row was ACTUALLY computed on; `ld_file_declared`
# is what Snakemake resolved; `ld_authoritative` is the regime that makes their
# comparison interpretable (off the allow-list they are EXPECTED to differ, and
# that difference is the EUR/TRANS containment working, not a regression).
#
# `ld_dir` STAYS WHERE IT IS even though it is the constant that constitutes
# finding I: removing it would REORDER the header, and this file is read by five
# scripts. APPEND ONLY. DO NOT REORDER A SINGLE EXISTING ENTRY. The first 17
# entries are pinned byte-for-byte against 0378ec8 by
# tests/m3/test_finemap_summary_panel_visible.py.
#
# The eight ld_allele_* columns are EMPTY (not 0) whenever the allele-aware join
# did not run -- run_susie_rss.R emits NA and toJSON(na = "null") renders it as
# JSON null -> Python None -> an empty cell. Empty means "not measured"
# (EUR/TRANS); 0 means "measured, and the join was clean" (AFR).
FIELDNAMES = [
    "trait",
    "ancestry",
    "method",
    "region_id",
    "status",
    "credible_sets",
    "credible_set_sizes",
    "variants_in_cs",
    "pip_nonzero",
    "top_chr",
    "top_pos",
    "top_pip",
    "top_beta",
    "top_se",
    "sumstats",
    "ld_dir",
    "output_path",
    # --- 260805-o7o APPENDED (FINDING I) ------------------------------------
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


def write_summary(rows: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as handle:
        handle.write("\t".join(FIELDNAMES) + "\n")
        for row in rows:
            values = [row.get(field) for field in FIELDNAMES]
            handle.write(
                "\t".join("" if value is None else str(value) for value in values) + "\n"
            )


def main():
    parser = argparse.ArgumentParser(description="Summarize fine-mapping JSON outputs.")
    parser.add_argument(
        "--inputs",
        nargs="*",
        default=[],
        help="Fine-mapping JSON files (optional when --inputs-file is provided).",
    )
    parser.add_argument(
        "--inputs-file",
        help="Optional text file with one JSON path per line (blank/comment lines ignored).",
    )
    parser.add_argument("--output", required=True, help="TSV output path.")
    args = parser.parse_args()

    inputs = list(args.inputs or [])
    if args.inputs_file:
        for line in Path(args.inputs_file).read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            inputs.append(line)

    if not inputs:
        raise SystemExit("No inputs provided to summarize.")

    rows = summarize_inputs(inputs)
    write_summary(rows, Path(args.output))


if __name__ == "__main__":
    if "snakemake" in globals():
        input_paths = [str(path) for path in snakemake.input]
        rows = summarize_inputs(input_paths)
        write_summary(rows, Path(snakemake.output.summary))
    else:
        main()
