"""r4 catalog producer: one row per normalized CHR:POS:REF:ALT (W3f 15.5a;
DEC-2026-11-17-ta-r4-catalog-unique-allele-key)."""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from .conftest import REPO_ROOT

HEADER = "CHR\tPOS\tREF\tALT\tSNP_ID\n"


def _lines(*rows):
    return [HEADER] + ["\t".join(str(x) for x in r) + "\n" for r in rows]


def _uak(lines):
    from ta_r4.catalog_unique_key import unique_allele_key

    return unique_allele_key(lines)


def _kept_ids(kept):
    return [ln.rstrip("\n").split("\t")[4] for ln in kept[1:]]


def _norm_key(line):
    c, p, r, a = line.rstrip("\n").split("\t")[:4]
    c = c.strip()
    for pre in ("chr", "CHR"):
        if c.startswith(pre):
            c = c[len(pre):]
            break
    return (c, int(p.strip()), r.strip().upper(), a.strip().upper())


def _dropped_lines(dropped):
    return [d[0] for d in dropped]


def _classes(dropped):
    return [d[2] for d in dropped]


def test_a_chrpos_and_rs_exact_twins_keep_rs():
    kept, dropped, stats = _uak(_lines((1, 100, "A", "G", "1:100"), (1, 100, "A", "G", "rs7")))
    assert _kept_ids(kept) == ["rs7"]
    assert _classes(dropped) == ["exact"]
    assert dropped[0][1] == "rs7"
    assert stats["n_dropped_exact"] == 1 and stats["n_dropped_case_ws"] == 0


def test_b_lowercase_chrpos_twin_keep_rs_case_ws():
    kept, dropped, stats = _uak(_lines((19, 1, "g", "t", "19:1"), (19, 1, "G", "T", "rs5")))
    assert _kept_ids(kept) == ["rs5"]
    assert _classes(dropped) == ["case_ws"]
    assert stats["n_dropped_case_ws"] == 1 and stats["n_dropped_exact"] == 0


def test_c_whitespace_twin_is_case_ws():
    kept, dropped, stats = _uak(_lines((2, 50, " G", "A", "2:50"), (2, 50, "G", "A", "rs3")))
    assert _kept_ids(kept) == ["rs3"]
    assert _classes(dropped) == ["case_ws"]


def test_d_multiallelic_different_alt_both_kept():
    rows = ((3, 10, "A", "C", "rs1"), (3, 10, "A", "T", "rs2"))
    kept, dropped, stats = _uak(_lines(*rows))
    assert _kept_ids(kept) == ["rs1", "rs2"]
    assert dropped == []
    assert stats["n_chrpos_extra_kept"] == 1


def test_e_ref_alt_swap_is_not_a_duplicate():
    rows = ((3, 10, "A", "G", "3:10"), (3, 10, "G", "A", "rs2"))
    kept, dropped, stats = _uak(_lines(*rows))
    assert _kept_ids(kept) == ["3:10", "rs2"]
    assert dropped == []


def test_f_triple_keeps_smallest_rsid():
    rows = ((4, 5, "C", "T", "4:5"), (4, 5, "C", "T", "rs200"), (4, 5, "C", "T", "rs100"))
    kept, dropped, stats = _uak(_lines(*rows))
    assert _kept_ids(kept) == ["rs100"]
    assert sorted(d[4] for d in (x[0].rstrip("\n").split("\t") for x in dropped)) == ["4:5", "rs200"]
    assert stats["n_groups_3plus"] == 1 and stats["n_groups_2"] == 0


def test_g_two_rsids_keep_smaller():
    kept, dropped, stats = _uak(_lines((5, 9, "A", "C", "rs90"), (5, 9, "A", "C", "rs9")))
    assert _kept_ids(kept) == ["rs9"]


def test_h_empty_snp_id_loses_to_chrpos():
    kept, dropped, stats = _uak(_lines((6, 7, "T", "C", ""), (6, 7, "T", "C", "6:7")))
    assert _kept_ids(kept) == ["6:7"]


def test_i_lowercase_twins_without_rsid_keep_uppercase():
    kept, dropped, stats = _uak(_lines((7, 8, "a", "c", "7:8"), (7, 8, "A", "C", "7:8")))
    kept_alleles = [ln.split("\t")[2:4] for ln in kept[1:]]
    assert kept_alleles == [["A", "C"]]
    assert _classes(dropped) == ["case_ws"]


MIXED = _lines(
    (1, 100, "A", "G", "1:100"),
    (1, 100, "A", "G", "rs7"),
    (1, 150, "A", "NA", "rs8"),
    (2, 50, " G", "A", "2:50"),
    (2, 50, "G", "A", "rs3"),
    (3, 10, "A", "C", "rs1"),
    (3, 10, "A", "T", "rs2"),
    (3, 10, "G", "A", "3:10"),
    (4, 5, "C", "T", "4:5"),
    (4, 5, "C", "T", "rs200"),
    (4, 5, "C", "T", "rs100"),
    (6, 7, "T", "C", ""),
    (6, 7, "T", "C", "6:7"),
    (19, 1, "g", "t", "19:1"),
    (19, 1, "G", "T", "rs5"),
)


def test_multiset_identity_and_key_set():
    kept, dropped, stats = _uak(MIXED)
    assert kept[0] == HEADER
    assert sorted(kept[1:] + _dropped_lines(dropped)) == sorted(MIXED[1:])
    assert {_norm_key(x) for x in kept[1:]} == {_norm_key(x) for x in MIXED[1:]}
    assert len(kept[1:]) == len({_norm_key(x) for x in kept[1:]})


def test_kept_in_input_order_and_byte_identical():
    kept, _, _ = _uak(MIXED)
    idx = [MIXED.index(ln) for ln in kept[1:]]
    assert idx == sorted(idx)


def test_stats_reconcile():
    kept, dropped, s = _uak(MIXED)
    assert s["n_raw"] == 15
    assert s["n_kept"] == len(kept) - 1 == 9
    assert s["n_dropped_exact"] + s["n_dropped_case_ws"] == len(dropped) == 6
    assert s["n_dropped_exact"] == 4 and s["n_dropped_case_ws"] == 2
    assert s["n_groups_2"] == 4 and s["n_groups_3plus"] == 1
    assert s["n_groups_2"] + 2 * s["n_groups_3plus"] == len(dropped)
    assert s["n_chrpos_extra_kept"] == 2


def test_no_duplicates_bytes_unchanged():
    lines = _lines((1, 100, "A", "G", "rs7"), (1, 150, "A", "NA", "rs8"), (2, 1, "c", "t", ""), (3, 10, "A", "C", "3:10"))
    kept, dropped, _ = _uak(lines)
    assert "".join(kept) == "".join(lines)
    assert dropped == []


def test_no_trailing_newline_bytes_unchanged():
    lines = _lines((1, 100, "A", "G", "rs7"), (1, 150, "A", "T", "rs8"))
    lines[-1] = lines[-1].rstrip("\n")
    kept, dropped, _ = _uak(lines)
    assert "".join(kept) == "".join(lines)


def test_missing_column_raises_with_line_number():
    lines = _lines((1, 100, "A", "G", "rs7"))
    lines.append("1\t200\tA\n")
    with pytest.raises(ValueError, match="line 3"):
        _uak(lines)


def test_non_integer_pos_raises_with_line_number():
    lines = _lines((1, 100, "A", "G", "rs7"), (1, "1e5", "A", "G", "rs8"))
    with pytest.raises(ValueError, match="line 3"):
        _uak(lines)


def test_bad_header_raises():
    with pytest.raises(ValueError, match="line 1"):
        _uak(["CHR\tPOS\tREF\tSNP_ID\n", "1\t1\tA\trs1\n"])


def test_cli_round_trip(tmp_path):
    raw = tmp_path / "raw.tsv"
    raw.write_text("".join(MIXED))
    out = tmp_path / "sub" / "kept.tsv"
    dropped = tmp_path / "drop" / "dropped.tsv"
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src/python"))
    r = subprocess.run(
        [sys.executable, "-m", "ta_r4.catalog_unique_key", "--in", str(raw), "--out", str(out), "--dropped", str(dropped)],
        capture_output=True, text=True, env=env, cwd=str(tmp_path),
    )
    assert r.returncode == 0, r.stderr
    stats = json.loads(r.stdout.strip().splitlines()[-1])
    kept, drows, s = _uak(MIXED)
    assert stats == s
    assert out.read_text() == "".join(kept)
    dl = dropped.read_text().splitlines(keepends=True)
    assert dl[0] == "CHR\tPOS\tREF\tALT\tSNP_ID\tkept_SNP_ID\tclass\n"
    body = [ln.rstrip("\n").split("\t") for ln in dl[1:]]
    assert ["\t".join(b[:5]) + "\n" for b in body] == _dropped_lines(drows)
    assert [b[5] for b in body] == [d[1] for d in drows]
    assert [b[6] for b in body] == _classes(drows)
    assert not list(tmp_path.rglob("*.part"))
