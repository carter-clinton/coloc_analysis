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
                }
            )
    return rows


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
