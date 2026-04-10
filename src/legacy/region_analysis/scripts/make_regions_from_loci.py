#!/usr/bin/env python
import argparse
import csv
from pathlib import Path


def load_loci(path: Path):
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    required = {"region_id", "chr", "start", "end"}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Missing columns in {path}: {missing}")
    for row in rows:
        row["chr"] = str(row["chr"]).replace("chr", "").replace("CHR", "")
        row["start"] = int(float(row["start"]))
        row["end"] = int(float(row["end"]))
    return rows


def main():
    parser = argparse.ArgumentParser(description="Convert curated regions CSV to BED.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = load_loci(Path(args.input))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as handle:
        for row in rows:
            handle.write(
                f"{row['chr']}\t{row['start']}\t{row['end']}\t{row['region_id']}\n"
            )


if __name__ == "__main__":
    main()
