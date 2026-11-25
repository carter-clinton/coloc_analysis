"""r4 sumstats in the r4 catalog's orientation (W3f 15.8a2; Carter Q-158R2 D, Q-158OR A, Q-158PAL A;
DEC-2026-11-25-ta-r4-sumstats-orientation)."""
from __future__ import annotations

import csv
import gzip
import hashlib
import os

import pytest

from .conftest import MAN_DIR, REPO_ROOT

HDR = ["CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF", "N", "SNP_ID", "TRAIT", "ANCESTRY", "BUILD"]
ORIENT_BY_FIT = "data/r4/tmp/w3f/q158/orient_by_fit.tsv"
ORIENT_BY_FIT_SHA = "b154b0fa789c997e4f3ba2497bdfef6a7a0b8f50d8b8cfe6ffe7b9d2fa05c4f1"
TABIX = "/rs1/researchers/c/ckclinto/conda_envs/hlp_haplogroups/bin/tabix"


def _row(chrom, pos, ref, alt, beta="0.1", se="0.01", p="0.5", eaf="0.3", n="1000", sid="", tail=("t", "EUR", "GRCh37")):
    return [str(chrom), str(pos), ref, alt, beta, se, p, eaf, n, sid, *tail]


def _write_gz(path, rows, header=HDR):
    with gzip.open(path, "wt", newline="") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")
    return str(path)


def _lines(path):
    with gzip.open(path, "rt", newline="") as fh:
        return fh.readlines()


def _plain_lines(path):
    with open(path, newline="") as fh:
        return fh.readlines()


# two windows on chr 16 and chr 2; catalogs as key sets
WINDOWS = [("R16", "16", 100, 500), ("R2", "2", 1000, 2000)]
CATS = {
    "R16": {("16", 100, "A", "G"), ("16", 200, "C", "T"), ("16", 300, "G", "C"), ("16", 300, "C", "G"),
            ("16", 400, "A", "T")},
    "R2": {("2", 1000, "G", "A"), ("2", 1500, "T", "C")},
}


def test_classify_reproduces_the_measurement_rule():
    from ta_r4 import sumstats_orient as so
    from ta_r4.collector_drop_audit import norm_key

    cat = {("16", 100, "A", "G"), ("16", 300, "G", "C"), ("16", 300, "C", "G")}
    assert so.classify(norm_key("16", 100, "A", "G"), cat) == "exact"
    assert so.classify(norm_key("16", 100, "G", "A"), cat) == "swapped_only"
    assert so.classify(norm_key("16", 300, "G", "C"), cat) == "both"
    assert so.classify(norm_key("16", 100, "A", "C"), cat) == "absent"
    assert so.classify(norm_key("chr16", "100", "g", "a"), cat) == "swapped_only"
    assert so.classify(norm_key("CHR16", "100", " a", "g "), cat) == "exact"
    assert so.CLASSES == ("exact", "swapped_only", "both", "absent")
    assert so.is_palindromic("a", "t") and so.is_palindromic("G", "C") and not so.is_palindromic("A", "G")
    assert not so.is_palindromic("AT", "TA")


def test_flip_fields_is_exact_on_strings():
    from ta_r4 import sumstats_orient as so

    def f(beta, eaf, ref="A", alt="G"):
        return so.flip_fields(_row(16, 100, ref, alt, beta=beta, eaf=eaf, sid="rs1"))

    base = _row(16, 100, "A", "G", beta="-0.0621", eaf="0.372364438206786", sid="rs1")
    out = so.flip_fields(base)
    assert out[2:4] == ["G", "A"]
    assert out[4] == "0.0621" and out[7] == "0.627635561793214"
    assert [out[i] for i in (0, 1, 5, 6, 8, 9, 10, 11, 12)] == [base[i] for i in (0, 1, 5, 6, 8, 9, 10, 11, 12)]
    assert base[4] == "-0.0621"  # input not mutated
    assert f("7.297000000000001e-57", "0.5")[4] == "-7.297000000000001e-57"
    assert f("0.0100", "0.5")[4] == "-0.0100"
    assert f("0", "0.5")[4] == "0"
    assert f("0.1", "0.8365")[7] == "0.1635"
    assert f("0.1", "NA")[7] == "NA"
    assert f("0.1", "")[7] == ""
    assert f("0.1", "0.5", ref="a", alt="g")[2:4] == ["g", "a"]


def _harmonize(tmp_path, rows, name="t.tsv.gz"):
    from ta_r4 import sumstats_orient as so

    src = _write_gz(tmp_path / name, rows)
    out = str(tmp_path / (name + ".out.tsv"))
    rep = so.harmonize(src, out, WINDOWS, CATS)
    return src, out, rep


def _synthetic_rows():
    return [
        _row(16, 50, "G", "A", sid="rs0"),          # outside (before the window), would be swapped
        _row(16, 100, "G", "A", beta="-0.2", eaf="0.25", sid="rs1"),   # swapped_only -> flipped
        _row(16, 200, "C", "T", sid="rs2"),         # exact
        _row(16, 300, "G", "C", sid="rs3"),         # both
        _row(16, 400, "T", "A", eaf="0.45", sid="rs4"),  # A/T swapped_only -> flipped (palindromic, EAF 0.4-0.6)
        _row(16, 450, "A", "C", sid="rs5"),         # absent
        _row(16, 460, "N", "N", sid="rs6"),         # unusable -> absent
        _row(16, 900, "G", "A", sid="rs7"),         # outside (after)
        _row(2, 1000, "A", "G", eaf="NA", sid="rs8"),   # swapped_only -> flipped
        _row(2, 1500, "T", "C", sid="rs9"),         # exact
        _row(3, 1500, "C", "T", sid="rs10"),        # other chromosome
    ]


def test_harmonize_flips_only_swapped_only_rows_in_a_window(tmp_path):
    from ta_r4 import sumstats_orient as so

    rows = _synthetic_rows()
    src, out, rep = _harmonize(tmp_path, rows)
    a, b = _lines(src), _plain_lines(out)
    assert len(a) == len(b) == len(rows) + 1
    flipped = {2, 5, 9}  # line numbers (header = 0)
    for i, (x, y) in enumerate(zip(a, b)):
        if i in flipped:
            assert y == "\t".join(so.flip_fields(x.rstrip("\n").split("\t"))) + "\n", i
            assert x != y
        else:
            assert x == y, i
    assert b[2].split("\t")[2:5] == ["A", "G", "0.2"] and b[2].split("\t")[7] == "0.75"
    assert b[5].split("\t")[2:4] == ["A", "T"]
    r16, r2 = rep["regions"]["R16"], rep["regions"]["R2"]
    assert (r16["exact"], r16["swapped_only"], r16["both"], r16["absent"]) == (1, 2, 1, 2)
    assert (r16["n_flipped"], r16["n_flipped_palindromic"], r16["n_flipped_palindromic_eaf_0.4_0.6"]) == (2, 1, 1)
    assert (r2["exact"], r2["swapped_only"], r2["both"], r2["absent"], r2["n_flipped"]) == (1, 1, 0, 0, 1)
    assert rep["n_flipped"] == 3 and rep["n_lines"] == len(rows)


def test_harmonize_is_idempotent(tmp_path):
    from ta_r4 import sumstats_orient as so

    _, out1, rep1 = _harmonize(tmp_path, _synthetic_rows())
    gz = tmp_path / "once.tsv.gz"
    with open(out1, "rb") as fh, gzip.open(gz, "wb") as oh:
        oh.write(fh.read())
    out2 = str(tmp_path / "twice.tsv")
    rep2 = so.harmonize(str(gz), out2, WINDOWS, CATS)
    assert rep1["n_flipped"] == 3 and rep2["n_flipped"] == 0
    assert open(out1, "rb").read() == open(out2, "rb").read()


def test_harmonize_refuses_a_new_duplicate_allele_key(tmp_path):
    from ta_r4 import sumstats_orient as so

    rows = [_row(16, 100, "A", "G", sid="rs1"), _row(16, 100, "G", "A", sid="rs1b")]
    with pytest.raises(so.OrientError, match="16:100"):
        _harmonize(tmp_path, rows)


def test_harmonize_refuses_an_unexpected_header(tmp_path):
    from ta_r4 import sumstats_orient as so

    rows = [_row(16, 100, "G", "A") + ["z"]]
    src = _write_gz(tmp_path / "z.tsv.gz", rows, header=HDR + ["Z"])
    with pytest.raises(so.OrientError):
        so.harmonize(src, str(tmp_path / "z.out.tsv"), WINDOWS, CATS)
    reordered = HDR[:2] + ["ALT", "REF"] + HDR[4:]
    src = _write_gz(tmp_path / "r.tsv.gz", [_row(16, 100, "G", "A")], header=reordered)
    with pytest.raises(so.OrientError):
        so.harmonize(src, str(tmp_path / "r.out.tsv"), WINDOWS, CATS)


def test_harmonize_refuses_an_output_outside_r4_sumstats(tmp_path, capsys):
    from ta_r4 import sumstats_orient as so

    for out in ("data/processed/sumstats_harmonized/stroke.AFR.tsv.bgz",
                "data/r4/tmp/w3f/q158/a2/stroke.AFR.r4_oriented.tsv.bgz",
                "data/r4/sumstats/../../processed/x.tsv.bgz",
                str(REPO_ROOT / "data/processed/x.tsv.bgz")):
        rc = so.main(["harmonize", "--trait", "stroke", "--anc", "AFR", "--bgzip", "/nonexistent/bgzip",
                      "--tabix", "/nonexistent/tabix", "--report", str(tmp_path / "r.json"), "--out", out,
                      "--repo", str(REPO_ROOT)])
        assert rc == 2, out
        assert "OrientError" in capsys.readouterr().err
        assert not (tmp_path / "r.json").exists()
    so.check_out_path("data/r4/sumstats/stroke.AFR.r4_oriented.tsv.bgz", REPO_ROOT, so.CATALOG_SOURCES)
    with pytest.raises(so.OrientError):  # an input path is never an output
        so.check_out_path("data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz", REPO_ROOT, so.CATALOG_SOURCES)


def test_verify_unflip_detects_any_other_change(tmp_path):
    from ta_r4 import sumstats_orient as so

    src, out, _ = _harmonize(tmp_path, _synthetic_rows())
    assert so.verify_unflip(src, out, WINDOWS, CATS)["n_flipped"] == 3
    good = _plain_lines(out)

    def mutate(i, fn):
        lines = list(good)
        f = lines[i].rstrip("\n").split("\t")
        fn(f)
        lines[i] = "\t".join(f) + "\n"
        p = tmp_path / f"bad{i}.tsv"
        p.write_text("".join(lines))
        return str(p)

    se_changed = mutate(2, lambda f: f.__setitem__(5, "0.02"))      # SE changed on a flipped row
    outside = mutate(1, lambda f: f.__setitem__(slice(2, 4), [f[3], f[2]]))  # an outside-window row flipped
    unflipped = list(good)
    unflipped[9] = _lines(src)[9]                                   # a swapped_only row left unflipped
    p = tmp_path / "unflipped.tsv"
    p.write_text("".join(unflipped))
    for bad in (se_changed, outside, str(p)):
        with pytest.raises(so.OrientError):
            so.verify_unflip(src, bad, WINDOWS, CATS)


def _compare(measured, reference_path):
    """measure() rows == the reference TSV row for row on its columns (strings)."""
    with open(reference_path, newline="") as fh:
        ref = list(csv.DictReader(fh, delimiter="\t"))
    assert len(measured) == len(ref)
    for m, r in zip(measured, ref):
        assert {k: str(m[k]) for k in r} == r


@pytest.mark.r4_heavy
def test_measure_reproduces_the_orchestrator_measurement():
    from ta_r4 import sumstats_orient as so

    os.chdir(REPO_ROOT)
    assert hashlib.sha256(open(ORIENT_BY_FIT, "rb").read()).hexdigest() == ORIENT_BY_FIT_SHA
    win = so.windows(REPO_ROOT)
    measured = so.measure([(t, a, p) for t, a, p in so.CATALOG_SOURCES], win, so.catalog_keys_by_region(win), TABIX)
    _compare(measured, ORIENT_BY_FIT)


def test_null_window_scan_is_invariant_to_flips(tmp_path):
    from ta_r4 import select_null_windows as snw
    from ta_r4 import sumstats_orient as so

    rows = _synthetic_rows()
    for i, p in enumerate(("1e-9", "0.04", "3e-12", "0.7", "NA")):
        rows[i * 2][6] = p
    src, out, rep = _harmonize(tmp_path, rows)
    assert rep["n_flipped"] == 3
    gz = tmp_path / "out.tsv.gz"
    with open(out, "rb") as fh, gzip.open(gz, "wb") as oh:
        oh.write(fh.read())
    for count in (False, True):
        assert snw.scan(src, 100, count) == snw.scan(str(gz), 100, count)


ORIENTATION = MAN_DIR / "sumstats_r4_orientation.tsv"
SUMSTATS_MANIFEST = MAN_DIR / "sumstats_r4_sha256.tsv"
MANIFEST_BEFORE = REPO_ROOT / "data/r4/tmp/w3f/q158/a2/sumstats_manifest_before.tsv"
AUDIT_MANIFEST = MAN_DIR / "catalog_collector_drops.tsv"


def _orientation_rows():
    with open(ORIENTATION, newline="") as fh:
        return list(csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t"))


def _check_oriented(files):
    """measure() on `files` against the orientation manifest: the must-be-identity of the oriented files."""
    from ta_r4 import sumstats_orient as so

    win = so.windows(REPO_ROOT)
    measured = so.measure(files, win, so.catalog_keys_by_region(win, REPO_ROOT), TABIX)
    rows = _orientation_rows()
    assert len(measured) == len(rows) == len(win) * len(so.CATALOG_SOURCES)
    for m, r in zip(measured, rows):
        where = (r["region_safe"], r["trait"], r["ancestry"])
        assert (m["region"], m["trait"], m["ancestry"]) == where
        assert m["swapped_only"] == 0, where
        assert m["exact"] == int(r["exact"]) + int(r["swapped_only"]), where
        assert m["both"] == int(r["both"]) and m["absent"] == int(r["absent"]), where
        assert m["n_rows"] == int(r["n_rows"]), where
        assert [m[k] for k in ("exact", "swapped_only", "both", "absent")] == [
            int(r[f"after_{k}"]) for k in ("exact", "swapped_only", "both", "absent")], where


@pytest.mark.r4_heavy
def test_oriented_files_have_no_swapped_only_rows():
    from ta_r4 import sumstats_orient as so

    os.chdir(REPO_ROOT)
    _check_oriented([(t, a, so.oriented_path(t, a)) for t, a, _ in so.CATALOG_SOURCES])


def _audit_counts():
    """Per source file: 15.8a audit rows with key false / swapped key true, and with both false."""
    with open(AUDIT_MANIFEST, newline="") as fh:
        man = list(csv.DictReader(fh, delimiter="\t"))
    out = {}
    for r in man:
        raw = open(REPO_ROOT / r["audit_path"], "rb").read()
        assert hashlib.sha256(raw).hexdigest() == r["audit_sha256"], r["region_safe"]
        for b in csv.DictReader(gzip.decompress(raw).decode("utf-8").splitlines(), delimiter="\t"):
            c = out.setdefault(b["source_file"], {"swapped_present": 0, "absent": 0})
            if b["key_in_final_catalog"] == "False":
                c["swapped_present" if b["swapped_key_in_final_catalog"] == "True" else "absent"] += 1
    return out


def _audit_identity(orientation_rows, audit_counts):
    from ta_r4 import sumstats_orient as so

    tot = {"swapped_present": 0, "absent": 0}
    for t, a, path in so.CATALOG_SOURCES:
        rows = [r for r in orientation_rows if (r["trait"], r["ancestry"]) == (t, a)]
        flipped = sum(int(r["n_flipped"]) for r in rows)
        absent = sum(int(r["absent"]) for r in rows)
        want = audit_counts.get(path, {"swapped_present": 0, "absent": 0})
        assert flipped == want["swapped_present"], (path, flipped, want)
        assert absent == want["absent"], (path, absent, want)
        tot["swapped_present"] += flipped
        tot["absent"] += absent
    assert set(audit_counts) <= {p for _, _, p in so.CATALOG_SOURCES}
    return tot


@pytest.mark.r4_heavy
def test_flips_equal_the_collector_audit_counts():
    with open(AUDIT_MANIFEST, newline="") as fh:
        man = list(csv.DictReader(fh, delimiter="\t"))
    tot = _audit_identity(_orientation_rows(), _audit_counts())
    assert tot["swapped_present"] == sum(int(r["n_lost_keys_swapped_present"]) for r in man)
    assert tot["absent"] == sum(int(r["n_lost_keys"]) - int(r["n_lost_keys_swapped_present"]) for r in man)


def _check_pins(manifest, before):
    from ta_r4 import sumstats_orient as so

    now = open(manifest, "rb").read().splitlines(keepends=True)
    old = open(before, "rb").read().splitlines(keepends=True)
    assert now[: len(old)] == old
    new = list(csv.reader([ln.decode() for ln in now[len(old):]], delimiter="\t"))
    want = [p for t, a, _ in so.CATALOG_SOURCES for p in (so.oriented_path(t, a), so.oriented_path(t, a) + ".tbi")]
    assert [r[0] for r in new] == want
    rows = list(csv.reader([ln.decode() for ln in old[1:]], delimiter="\t")) + new
    for path, sha, size, role in rows:
        p = REPO_ROOT / path
        assert os.path.getsize(p) == int(size), path
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
        assert h.hexdigest() == sha, path
    assert {r[3] for r in new} == {"output"}


@pytest.mark.r4_heavy
def test_oriented_pins_match_disk_and_track_b_is_unchanged():
    _check_pins(SUMSTATS_MANIFEST, MANIFEST_BEFORE)


def _verify_real(src, out):
    from ta_r4 import sumstats_orient as so

    win = so.windows(REPO_ROOT)
    rep = so.verify_unflip(src, out, win, so.catalog_keys_by_region(win, REPO_ROOT))
    want = sum(int(r["n_flipped"]) for r in _orientation_rows() if (r["trait"], r["ancestry"]) == ("stroke", "AFR"))
    assert rep["n_flipped"] == want > 0
    return rep


@pytest.mark.r4_heavy
def test_real_oriented_file_differs_only_in_flipped_rows():
    from ta_r4 import sumstats_orient as so

    os.chdir(REPO_ROOT)
    _verify_real(REPO_ROOT / so.source_path("stroke", "AFR"), REPO_ROOT / so.oriented_path("stroke", "AFR"))
