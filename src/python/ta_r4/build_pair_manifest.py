"""Pre-registered static all-pairs manifest (D-07, D-24). No fit outcome enters any column."""
from __future__ import annotations

import argparse
import csv
import itertools
import sys
from pathlib import Path

import yaml

EUR_TRAITS = ("asthma", "bmi", "hypertension", "stroke", "t2d")
AFR_TRAITS = ("asthma", "stroke", "t2d")
COLUMNS = ("row_id", "ancestry", "region_id", "region_safe", "trait_a", "trait_b", "row_class",
           "admissible", "inadmissible_reason", "canonical_pair", "nc_set", "nc_caveat")
INADMISSIBLE = {
    "HLA_6p21": "D-24: no admissible panel (69k HM3 variants > 16000 cap); UKB exploratory fits only, no coloc row",
    "BMI_Xq24": "D-24: chrX absent from LDSC 1000G and UKB LD",
}
NC_CAVEATS = {"NC_ABO": "reported_stroke_association_verify"}  # research A5
NC_SETS = ("cosmetic", "blood_group")


def safe_ids(region_ids):
    """The Snakefile:51-61 rule: '.' and '/' -> '_', with a numeric suffix on collision."""
    seen, out = set(), []
    for orig in region_ids:
        safe = orig.replace(".", "_").replace("/", "_")
        suffix = 1
        while safe in seen:
            suffix += 1
            safe = f"{safe}_{suffix}"
        seen.add(safe)
        out.append(safe)
    return out


def _nc_set_by_coord(negative_controls):
    with open(negative_controls) as fh:
        sets = yaml.safe_load(fh)["curated_sets"]
    return {(str(r["chr"]), int(r["start"]), int(r["end"])): name
            for name in NC_SETS for r in sets[name]["regions_grch37"]}


def build_rows(regions, negative_controls):
    with open(regions, newline="") as fh:
        regs = list(csv.DictReader(fh))
    nc_by_coord = _nc_set_by_coord(negative_controls)
    rows = []
    for r, safe in zip(regs, safe_ids([r["region_id"] for r in regs])):
        rid, src = r["region_id"], r["source"]
        canon = {p for p in r["canonical_pairs"].split(";") if p}
        if src == "negative_control_gwas_null":
            cls, nc_set = "negative_control", "gwas_null"
        elif src == "negative_control":
            cls = "negative_control"
            nc_set = nc_by_coord[(r["chr"], int(r["start"]), int(r["end"]))]
        else:
            cls, nc_set = "primary", ""
        plans = [("EUR", EUR_TRAITS)] + ([("AFR", AFR_TRAITS)] if cls == "primary" else [])
        for anc, traits in plans:
            for a, b in itertools.combinations(sorted(traits), 2):
                rows.append({
                    "row_id": f"{safe}__{anc}__{a}_vs_{b}",
                    "ancestry": anc, "region_id": rid, "region_safe": safe,
                    "trait_a": a, "trait_b": b, "row_class": cls,
                    "admissible": "false" if rid in INADMISSIBLE else "true",
                    "inadmissible_reason": INADMISSIBLE.get(rid, ""),
                    "canonical_pair": "true" if f"{a}_vs_{b}" in canon else "false",
                    "nc_set": nc_set, "nc_caveat": NC_CAVEATS.get(rid, ""),
                })
    rows.sort(key=lambda x: (x["row_class"], x["ancestry"], x["region_safe"], x["trait_a"], x["trait_b"]))
    return rows


def render(rows) -> str:
    return "".join("\t".join(r) + "\n" for r in [COLUMNS] + [[x[c] for c in COLUMNS] for x in rows])


def schema_violations(path) -> list[str]:
    """Exactly COLUMNS in order (so no status/tier/outcome column), booleans true|false, unique row_id."""
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        cols = tuple(reader.fieldnames or ())
        rows = list(reader)
    out = []
    if cols != COLUMNS:
        out.append(f"columns {list(cols)} != {list(COLUMNS)}; extra: {sorted(set(cols) - set(COLUMNS))}")
    for c in ("admissible", "canonical_pair"):
        if c in cols and {r[c] for r in rows} - {"true", "false"}:
            out.append(f"{c} not in true|false")
    ids = [r.get("row_id") for r in rows]
    if len(set(ids)) != len(ids):
        out.append("duplicate row_id")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--regions", required=True)
    ap.add_argument("--negative-controls",
                    default=str(Path(__file__).resolve().parents[3] / "config/negative_controls.yaml"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    with open(args.out, "w", newline="") as fh:
        fh.write(render(build_rows(args.regions, args.negative_controls)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
