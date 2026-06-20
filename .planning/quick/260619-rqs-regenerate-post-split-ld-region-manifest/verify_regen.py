#!/usr/bin/env python3
"""Post-regen invariant checks for quick task 260619-rqs.

Run from the repo root. Exits 0 + prints MANIFEST_REGEN_OK on success, else
raises AssertionError. Verifies the split-existing regen produced the expected
__sub compute rows and preserved non-xlarge passthrough.
"""
import csv
import sys


def load(path):
    with open(path) as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return list(reader), reader.fieldnames


def main() -> int:
    rows, cols = load("config/ld_regions.tsv")
    assert "parent_region_id" in cols and "buffer_bp" in cols, f"missing split cols: {cols}"

    sub40 = [x for x in rows if x["region_id"] == "m2_region_00040__sub00"]
    anc40 = {x["ancestry"] for x in sub40}
    assert {"AFR", "EUR"} <= anc40, f"m2_region_00040__sub00 ancestries: {anc40}"

    assert any(x["region_id"].startswith("m2_region_00145__sub") for x in rows), \
        "no region_00145 __sub rows"

    subs = [x for x in rows if "__sub" in x["region_id"]]
    bad = {x["buffer_bp"] for x in subs if x["buffer_bp"] not in ("10000000", "10000000.0")}
    assert not bad, f"non-10Mb buffer on __sub rows: {bad}"

    r6 = [x for x in rows if x["region_id"] == "m2_region_00006"]
    assert r6 and all(
        x["region_class"] == "medium" and "__sub" not in x["region_id"] for x in r6
    ), "m2_region_00006 is not a whole medium row"

    drows, _ = load("config/ld_regions_dev.tsv")
    danc = {x["ancestry"] for x in drows if x["region_id"] == "m2_region_00040__sub00"}
    assert {"AFR", "EUR"} <= danc, f"dev m2_region_00040__sub00 ancestries: {danc}"

    print(f"MANIFEST_REGEN_OK manifest_rows={len(rows)} dev_rows={len(drows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
