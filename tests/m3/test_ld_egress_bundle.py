"""m3-02d Task 2 — per-chromosome LD egress bundling helper tests.

ld_egress_bundle.plan_egress_bundles groups summary LD compute-cell outputs by
chromosome and splits a chromosome whose summed bytes exceed the 50 GB working
ceiling into chrN_a / chrN_b sub-bundles. The cap is a CONSERVATIVE project
working ceiling (research Q5/A2), NOT a hard AoU API limit. Pure-Python, no Hail.
"""
import importlib
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

bundle = importlib.import_module("ld_egress_bundle")

_GB = 1_000_000_000


def test_egress_cap_is_conservative_working_ceiling():
    assert bundle.EGRESS_CAP_GB == 50
    assert bundle.EGRESS_CAP_BYTES == 50 * _GB


def test_egress_bundle_groups_by_chrom():
    cells = [
        {"region_id": "m2_region_00001", "chr": "1", "bytes": 3 * _GB},
        {"region_id": "m2_region_00002", "chr": "1", "bytes": 4 * _GB},
        {"region_id": "m2_region_00010", "chr": "2", "bytes": 5 * _GB},
        {"region_id": "m2_region_00020", "chr": "chr2", "bytes": 2 * _GB},  # 'chr' prefix tolerated
    ]
    bundles = bundle.plan_egress_bundles(cells)
    by_id = {b["bundle_id"]: b for b in bundles}
    assert set(by_id) == {"chr1", "chr2"}
    assert by_id["chr1"]["total_bytes"] == 7 * _GB
    assert by_id["chr1"]["n_cells"] == 2
    assert by_id["chr2"]["total_bytes"] == 7 * _GB
    assert set(by_id["chr2"]["region_ids"]) == {"m2_region_00010", "m2_region_00020"}
    # under-cap chromosomes stay single bundles
    assert bundle.n_bundles_over_cap(bundles) == 0
    assert bundle.chromosomes_split(bundles) == []


def test_egress_bundle_splits_over_cap():
    # chr1 sums to 80 GB > 50 GB -> split into chr1_a / chr1_b; chr3 stays single.
    cells = [
        {"region_id": "m2_region_00001", "chr": "1", "bytes": 30 * _GB},
        {"region_id": "m2_region_00002", "chr": "1", "bytes": 25 * _GB},
        {"region_id": "m2_region_00003", "chr": "1", "bytes": 25 * _GB},
        {"region_id": "m2_region_00050", "chr": "3", "bytes": 10 * _GB},
    ]
    bundles = bundle.plan_egress_bundles(cells)
    by_id = {b["bundle_id"]: b for b in bundles}
    # chr1 split into a/b, each <= the cap
    assert "chr1_a" in by_id and "chr1_b" in by_id
    assert by_id["chr1_a"]["total_bytes"] <= bundle.EGRESS_CAP_BYTES
    assert by_id["chr1_b"]["total_bytes"] <= bundle.EGRESS_CAP_BYTES
    # the split preserves all cells, no loss/dup
    chr1_ids = by_id["chr1_a"]["region_ids"] + by_id["chr1_b"]["region_ids"]
    assert sorted(chr1_ids) == ["m2_region_00001", "m2_region_00002", "m2_region_00003"]
    # greedy: 30 GB then +25 = 55 > 50 -> a={00001}; b={00002,00003}=50
    assert by_id["chr1_a"]["region_ids"] == ["m2_region_00001"]
    assert by_id["chr1_b"]["total_bytes"] == 50 * _GB
    # chr3 under the cap stays single
    assert "chr3" in by_id
    assert by_id["chr3"]["total_bytes"] == 10 * _GB
    # chr1 reported as split
    assert "1" in bundle.chromosomes_split(bundles)
    assert "3" not in bundle.chromosomes_split(bundles)


def test_egress_bundle_indivisible_oversized_cell_is_own_subbundle():
    # A single cell larger than the cap cannot be subdivided; it occupies its own
    # sub-bundle (flagged via n_bundles_over_cap) rather than being dropped.
    cells = [
        {"region_id": "m2_region_00001", "chr": "6", "bytes": 60 * _GB},  # > cap alone
        {"region_id": "m2_region_00002", "chr": "6", "bytes": 10 * _GB},
    ]
    bundles = bundle.plan_egress_bundles(cells)
    chr6 = [b for b in bundles if b["chr"] == "6"]
    assert len(chr6) == 2  # split a/b
    big = [b for b in chr6 if "m2_region_00001" in b["region_ids"]][0]
    assert big["total_bytes"] == 60 * _GB
    assert bundle.n_bundles_over_cap(bundles) == 1


def test_egress_bundle_no_path_constants():
    # REQ-PATH-PARAMETERIZATION: the helper source carries no absolute HPC paths.
    src = (SRC / "ld_egress_bundle.py").read_text()
    for forbidden in ("/share/clintonlab", "/rs1/researchers", "/gpfs_common"):
        assert forbidden not in src
