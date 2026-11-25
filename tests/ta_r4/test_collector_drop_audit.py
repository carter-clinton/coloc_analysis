"""r4 collector drop audit: every row collect_region_variants.py does not keep is classified and counted (W3f 15.8a;
review R2; DEC-2026-11-24-ta-r4-w3f-15-8-open-items)."""
from __future__ import annotations

import csv
import gzip
import hashlib
import os
import re
import time

import pytest

from .conftest import MAN_DIR, REPO_ROOT

HDR = ["CHR", "POS", "REF", "ALT", "BETA", "SNP_ID"]


def _write_gz(path, rows, header=HDR):
    with gzip.open(path, "wt", newline="") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    return str(path)


def _final_keys(collector_df):
    """Final-catalog key set as production builds it: collector TSV -> catalog_unique_key -> normalized keys."""
    from ta_r4 import collector_drop_audit as cda
    from ta_r4.catalog_unique_key import unique_allele_key

    text = collector_df.to_csv(sep="\t", index=False)
    kept, _, _ = unique_allele_key(text.splitlines(keepends=True))
    return cda.catalog_keys_from_lines(kept)


def _run(tmp_path, f1_rows, f2_rows, chrom="16", start=1, end=10_000):
    from ta_r4 import collector_drop_audit as cda

    p1 = _write_gz(tmp_path / "t1.tsv.gz", f1_rows)
    p2 = _write_gz(tmp_path / "t2.tsv.gz", f2_rows)
    kept, dropped = cda.replay([p1, p2], chrom, start, end)
    collector = cda.load_collector().collect_variants([p1, p2], chrom, start, end)
    flagged = cda.flag_dropped(dropped, _final_keys(collector))
    return kept, collector, flagged, (p1, p2)


def _by(flagged, **kv):
    return [d for d in flagged if all(str(d[k]) == str(v) for k, v in kv.items())]


def test_replay_keeps_exactly_what_the_collector_keeps(tmp_path):
    f1 = [
        (16, 100, "A", "G", 0.1, "rs1"),
        (16, 100, "A", "G", 0.1, ""),          # unnamed at a named position
        (16, 200, "C", "T", 0.1, "rs2"),
        (16, 300, "N", "N", 0.1, "rs3"),        # allele-less, replaced from file 2
        (16, 400, "A", "C", 0.1, ""),
        (16, 400, "A", "T", 0.1, ""),           # second unnamed at the same position
        (16, 500, "G", "A", 0.1, ""),
        (17, 100, "A", "G", 0.1, "rs9"),        # other chromosome: outside the window
        (16, 20_000, "A", "G", 0.1, "rs10"),    # outside the window
    ]
    f2 = [
        (16, 100, "A", "G", 0.2, "rs1"),        # exact duplicate across files
        (16, 200, "C", "A", 0.2, "rs2"),        # same rsid, other allele key
        (16, 200, "c", "t", 0.2, "rs2"),        # same rsid, same key, other bytes
        (16, 300, "A", "G", 0.2, "rs3"),        # replaces the allele-less record
        (16, 500, "g", "a", 0.2, ""),           # unnamed duplicate (case-insensitive key)
        ("chr16", 600, "T", "C", 0.2, "rs6"),
        (16, 700, "N", "N", 0.2, "rs7"),
        (16, 700, "N", "N", 0.2, "rs7"),        # exact duplicate of an allele-less row
        (16, 800, "A", "G", 0.2, "rs8"),
        (16, 800, "N", "N", 0.2, ""),           # allele-less unnamed at a named position
    ]
    kept, collector, flagged, _ = _run(tmp_path, f1, f2)
    assert kept.equals(collector)
    n_input = sum(1 for r in f1 + f2 if str(r[0]).replace("chr", "") == "16" and 1 <= r[1] <= 10_000)
    assert len(kept) + len(flagged) == n_input
    ids = [(d["source_file"], d["source_row"]) for d in flagged]
    assert len(ids) == len(set(ids))
    assert all(d["class"] != "other" for d in flagged)
    steps = {d["class"] for d in flagged}
    assert {"exact_duplicate", "rsid_other_allele_key", "rsid_same_key_other_bytes", "rsid_replaced_allele_less",
            "unnamed_duplicate", "unnamed_at_named_position", "unnamed_same_position_other_alleles",
            "allele_less"} <= steps


def test_same_rsid_other_allele_key_is_audited(tmp_path):
    f1 = [(16, 300, "A", "G", 0.1, "rs5")]
    f2 = [(16, 300, "A", "C", 0.2, "rs5"), (16, 300, "a", "g", 0.2, "rs5"), (16, 300, "A", "G", 0.2, "rs5")]
    kept, collector, flagged, (p1, p2) = _run(tmp_path, f1, f2)
    assert kept.equals(collector)
    assert list(kept["SNP_ID"]) == ["rs5"] and list(kept["ALT"]) == ["G"]
    other = _by(flagged, ALT="C")
    assert len(other) == 1
    d = other[0]
    assert d["class"] == "rsid_other_allele_key"
    assert (d["source_file"], d["kept_SNP_ID"], d["kept_REF"], d["kept_ALT"]) == (p2, "rs5", "A", "G")
    assert d["key_in_final_catalog"] is False and d["swapped_key_in_final_catalog"] is False
    assert [x["class"] for x in _by(flagged, REF="a")] == ["rsid_same_key_other_bytes"]
    assert [x["class"] for x in _by(flagged, REF="A", ALT="G")] == ["exact_duplicate"]
    assert len(flagged) == 3


def test_allele_less_record_replaced_by_real_alleles_is_audited(tmp_path):
    f1 = [(16, 400, "N", "N", 0.1, "rs7")]
    f2 = [(16, 400, "A", "G", 0.2, "rs7")]
    kept, collector, flagged, (p1, p2) = _run(tmp_path, f1, f2)
    assert kept.equals(collector)
    assert list(kept[["REF", "ALT", "SNP_ID"]].itertuples(index=False, name=None)) == [("A", "G", "rs7")]
    assert len(flagged) == 1
    d = flagged[0]
    assert d["class"] == "rsid_replaced_allele_less"
    assert (d["source_file"], d["REF"], d["ALT"]) == (p1, "N", "N")
    assert (d["kept_SNP_ID"], d["kept_REF"], d["kept_ALT"]) == ("rs7", "A", "G")


def test_unnamed_at_named_position_is_audited_with_key_flags(tmp_path):
    f1 = [(16, 100, "A", "G", 0.1, "rs1"), (16, 200, "A", "G", 0.1, "rs2")]
    f2 = [
        (16, 100, "A", "G", 0.2, ""),       # same key as the named row
        (16, 100, "A", "T", 0.2, ""),       # different key
        ("chr16", 200, "a", "g", 0.2, ""),  # differs from the catalog row only by allele case and a chr prefix
        (16, 100, "G", "A", 0.2, ""),       # swap of a catalog row
    ]
    kept, collector, flagged, _ = _run(tmp_path, f1, f2)
    assert kept.equals(collector)
    assert len(flagged) == 4
    assert {d["class"] for d in flagged} == {"unnamed_at_named_position"}
    same = _by(flagged, POS=100, REF="A", ALT="G")[0]
    other = _by(flagged, POS=100, REF="A", ALT="T")[0]
    case_chr = _by(flagged, POS=200)[0]
    swap = _by(flagged, POS=100, REF="G", ALT="A")[0]
    assert case_chr["CHR"] == "chr16"
    assert (same["key_in_final_catalog"], same["swapped_key_in_final_catalog"]) == (True, False)
    assert (other["key_in_final_catalog"], other["swapped_key_in_final_catalog"]) == (False, False)
    assert case_chr["key_in_final_catalog"] is True
    assert (swap["key_in_final_catalog"], swap["swapped_key_in_final_catalog"]) == (False, True)
    assert same["kept_SNP_ID"] == "rs1" and case_chr["kept_SNP_ID"] == "rs2"


def test_unnamed_same_position_other_alleles_is_audited(tmp_path):
    f1 = [(16, 500, "A", "G", 0.1, "")]
    f2 = [(16, 500, "A", "T", 0.2, "")]
    kept, collector, flagged, (p1, p2) = _run(tmp_path, f1, f2)
    assert kept.equals(collector)
    assert list(kept["ALT"]) == ["G"]
    assert len(flagged) == 1
    d = flagged[0]
    assert d["class"] == "unnamed_same_position_other_alleles"
    assert (d["source_file"], d["ALT"], d["kept_REF"], d["kept_ALT"]) == (p2, "T", "A", "G")
    assert d["key_in_final_catalog"] is False


def _manifest_rows():
    with open(MAN_DIR / "catalog_collector_drops.tsv", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


@pytest.mark.r4_heavy
def test_manifest_matches_disk():
    from ta_r4 import collector_drop_audit as cda
    from ta_r4 import paths

    os.chdir(REPO_ROOT)
    rows = _manifest_rows()
    regions = cda.r4_regions(REPO_ROOT)
    assert sorted(r["region_safe"] for r in rows) == sorted(regions)
    for r in rows:
        audit = REPO_ROOT / r["audit_path"]
        raw = open(audit, "rb").read()
        assert hashlib.sha256(raw).hexdigest() == r["audit_sha256"], r["region_safe"]
        with gzip.open(audit, "rt", newline="") as fh:
            body = list(csv.DictReader(fh, delimiter="\t"))
        assert len(body) == int(r["audit_rows"]) == int(r["n_dropped"]), r["region_safe"]
        for cls in cda.CLASSES + ("other",):
            assert sum(b["class"] == cls for b in body) == int(r[f"n_dropped_{cls}"]), (r["region_safe"], cls)
        assert int(r["n_dropped_other"]) == 0
        lost = [b for b in body if b["real_alleles"] == "True" and b["key_in_final_catalog"] == "False"]
        assert len(lost) == int(r["n_lost_keys"]), r["region_safe"]
        assert sum(b["swapped_key_in_final_catalog"] == "True" for b in lost) == int(r["n_lost_keys_swapped_present"])
        with open(REPO_ROOT / paths.catalog_raw_path(r["region_safe"])) as fh:
            n_raw = sum(1 for _ in fh) - 1
        assert int(r["n_kept"]) == n_raw, r["region_safe"]
        assert int(r["n_input_rows"]) == int(r["n_kept"]) + int(r["n_dropped"]), r["region_safe"]
    small = min(rows, key=lambda r: int(r["n_input_rows"]))
    t0 = time.monotonic()
    summary, body = cda.audit_region(small["region_safe"], REPO_ROOT, write=False)
    print(f"replay {small['region_safe']} {time.monotonic() - t0:.0f}s")
    assert summary["n_input_rows"] == int(small["n_input_rows"])
    assert hashlib.sha256(body).hexdigest() == small["audit_sha256"]
