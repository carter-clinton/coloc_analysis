"""D-06 unit 1 / D-18: BMI REF/ALT/EAF restored from the same Yengo 2018 release (restore_bmi_alleles)."""
from __future__ import annotations

import csv
import gzip
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HTS_BIN = "/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/55c377a7e8fce799d92381bcc5138d7f_/bin"

FROZEN_HDR = "CHR POS BETA SE P N SNP_ID TRAIT ANCESTRY BUILD".split()
SOURCE_HDR = "CHR BP SNP EA OA BETA SE P EAF N".split()
RAW_HDR = "CHR POS SNP Tested_Allele Other_Allele Freq_Tested_Allele_in_HRS BETA SE P N".split()
OUT_HDR = "CHR POS REF ALT BETA SE P EAF N SNP_ID TRAIT ANCESTRY BUILD".split()

# (CHR, POS, BETA, SE, P, N, SNP_ID) frozen; source row or None; expected class
ROWS = [
    # exact, byte-identical strings
    (("1", "100", "-0.004", "0.0028", "0.15", "517173.0", "rs1"), ("A", "G", "-0.004", "0.0028", "0.15", "0.1425"), "exact"),
    # flipped: source BETA = -frozen
    (("1", "200", "0.0023", "0.0028", "0.41", "551519.0", "rs2"), ("A", "G", "-0.0023", "0.0028", "0.41", "0.3"), "flipped"),
    # value mismatch: SE differs
    (("1", "300", "0.0019", "0.0027", "0.48", "598447.0", "rs3"), ("A", "T", "0.0019", "0.0031", "0.48", "0.2"), "value_mismatch"),
    # unjoined: no source row
    (("2", "400", "0.001", "0.002", "0.6", "600000.0", "rs4"), None, "unjoined"),
    # exact at the frozen precision (source carries an extra digit; P in scientific notation in the frozen)
    (("2", "500", "0.0013", "0.0042", "7.5e-01", "598895.0", "rs5"), ("C", "T", "0.00131", "0.0042", "0.751", "0.06431"), "exact"),
    # flipped with a scientific-notation P
    (("3", "600", "-0.0213", "0.0021", "1.2e-23", "690000.0", "rs6"), ("G", "C", "0.0213", "0.0021", "1.24e-23", "0.5"), "flipped"),
    # value mismatch: |BETA| differs beyond the frozen precision
    (("3", "700", "0.005", "0.002", "0.01", "690000.0", "rs7"), ("T", "C", "0.006", "0.002", "0.01", "0.9"), "value_mismatch"),
    # unjoined: same CHR+POS, different SNP_ID
    (("4", "800", "0.002", "0.002", "0.3", "690000.0", "rs8"), ("A", "C", "0.002", "0.002", "0.3", "0.4"), "unjoined"),
]


def _write_gz(path, header, rows):
    with gzip.open(path, "wt", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _fixture(tmp_path, rows=ROWS):
    frozen, source = tmp_path / "bmi.EUR.tsv.bgz", tmp_path / "bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz"
    _write_gz(frozen, FROZEN_HDR, [f + ("bmi", "EUR", "GRCh37") for f, _, _ in rows])
    src = []
    for f, s, _ in rows:
        if s is None:
            continue
        snp = "rs8_other" if f[6] == "rs8" else f[6]
        ea, oa, beta, se, p, eaf = s
        src.append((f[0], f[1], snp, ea, oa, beta, se, p, eaf, f[5]))
    _write_gz(source, SOURCE_HDR, src)
    man = tmp_path / "m1.tsv"
    man.write_text("relative_path\tsha256\tbytes\n"
                   f"{frozen.name}\t{_sha(frozen)}\t{frozen.stat().st_size}\n"
                   f"{source.name}\t{_sha(source)}\t{source.stat().st_size}\n")
    return frozen, source, man


def _run(args):
    env = dict(os.environ, PYTHONPATH=str(REPO / "src/python"))
    return subprocess.run([sys.executable, "-m", "ta_r4.restore_bmi_alleles"] + [str(a) for a in args],
                          cwd=REPO, env=env, capture_output=True, text=True)


def _restore(tmp_path, frozen, source, man, extra=()):
    out, rep = tmp_path / "out" / "bmi.EUR.r4_alleles.tsv.bgz", tmp_path / "report.tsv"
    r = _run(["restore", "--frozen", frozen, "--source", source, "--manifest", man, "--out", out,
              "--report", rep, "--bgzip", f"{HTS_BIN}/bgzip", "--tabix", f"{HTS_BIN}/tabix", *extra])
    return r, out, rep


def _rows(path):
    with gzip.open(path, "rt") as fh:
        return list(csv.reader(fh, delimiter="\t"))


def _report(rep):
    with open(rep) as fh:
        return {r["metric"]: r["value"] for r in csv.DictReader(fh, delimiter="\t")}


@pytest.fixture
def restored(tmp_path):
    frozen, source, man = _fixture(tmp_path)
    r, out, rep = _restore(tmp_path, frozen, source, man)
    assert r.returncode == 0, r.stderr
    return frozen, out, rep


def test_class_counts(restored):
    _, _, rep = restored
    m = _report(rep)
    got = {k: int(m[f"n_{k}"]) for k in ("exact", "flipped", "value_mismatch", "unjoined")}
    assert got == {"exact": 2, "flipped": 2, "value_mismatch": 2, "unjoined": 2}


def test_report_reconciles(restored):
    frozen, out, rep = restored
    m = _report(rep)
    parts = sum(int(m[f"n_{k}"]) for k in ("exact", "flipped", "value_mismatch", "unjoined"))
    assert int(m["n_frozen"]) == parts == len(_rows(frozen)) - 1
    assert int(m["n_kept"]) == int(m["n_exact"]) + int(m["n_flipped"]) == len(_rows(out)) - 1


def test_header_and_kept_strings_byte_identical(restored):
    frozen, out, _ = restored
    fz = {r[6]: dict(zip(FROZEN_HDR, r)) for r in _rows(frozen)[1:]}
    rows = _rows(out)
    assert rows[0] == OUT_HDR
    kept = [dict(zip(OUT_HDR, r)) for r in rows[1:]]
    assert [k["SNP_ID"] for k in kept] == ["rs1", "rs2", "rs5", "rs6"]  # frozen order, dropped rows gone
    for k in kept:
        for col in ("CHR", "POS", "BETA", "SE", "P", "N", "SNP_ID", "TRAIT", "ANCESTRY", "BUILD"):
            assert k[col] == fz[k["SNP_ID"]][col], (k["SNP_ID"], col)


def test_ref_alt_eaf_assignment(restored):
    _, out, _ = restored
    kept = {r[9]: dict(zip(OUT_HDR, r)) for r in _rows(out)[1:]}
    assert (kept["rs1"]["REF"], kept["rs1"]["ALT"], kept["rs1"]["EAF"]) == ("G", "A", "0.1425")
    assert (kept["rs5"]["REF"], kept["rs5"]["ALT"], kept["rs5"]["EAF"]) == ("T", "C", "0.06431")
    assert (kept["rs2"]["REF"], kept["rs2"]["ALT"], kept["rs2"]["EAF"]) == ("A", "G", "0.7")
    assert (kept["rs6"]["REF"], kept["rs6"]["ALT"], kept["rs6"]["EAF"]) == ("G", "C", "0.5")


def test_output_bgzipped_and_tabix_indexed(restored):
    _, out, _ = restored
    assert out.read_bytes()[:4] == b"\x1f\x8b\x08\x04"  # BGZF extra-field gzip
    r = subprocess.run([f"{HTS_BIN}/tabix", "-l", str(out)], capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.split() == ["1", "2", "3"]
    r = subprocess.run([f"{HTS_BIN}/tabix", str(out), "3:600-600"], capture_output=True, text=True)
    assert r.stdout.split("\t")[9] == "rs6"


def test_wrong_input_sha_exits_2_before_reading(tmp_path):
    frozen, source, man = _fixture(tmp_path)
    frozen.write_bytes(b"not gzip at all")  # any parse attempt would raise, not exit 2
    r, out, rep = _restore(tmp_path, frozen, source, man)
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert "sha256" in r.stderr and not out.exists() and not rep.exists()


def test_input_absent_from_manifest_exits_2(tmp_path):
    frozen, source, man = _fixture(tmp_path)
    man.write_text("relative_path\tsha256\tbytes\n")
    r, out, _ = _restore(tmp_path, frozen, source, man)
    assert r.returncode == 2 and not out.exists()


def test_zero_beta_sign_uninformative_kept_as_exact_and_counted(tmp_path):
    rows = [(("1", "100", "0.0", "0.002", "0.99", "500000.0", "rs1"), ("A", "G", "0.0", "0.002", "0.99", "0.2"), "exact")]
    frozen, source, man = _fixture(tmp_path, rows)
    r, out, rep = _restore(tmp_path, frozen, source, man)
    assert r.returncode == 0, r.stderr
    m = _report(rep)
    assert (m["n_exact"], m["n_flipped"], m["n_sign_uninformative"]) == ("1", "0", "1")


def test_raw_crosscheck(tmp_path):
    frozen, source, man = _fixture(tmp_path)
    raw = tmp_path / "bmi.EUR.raw.gz"
    # rs1 ALT=A agrees, rs2 ALT=G agrees, rs5 ALT=C reversed in raw, rs6 absent from raw
    _write_gz(raw, RAW_HDR, [("1", "100", "rs1", "A", "G", "0.14", " -0.004", "0.0028", " 1.5e-01", "1"),
                             ("1", "200", "rs2", "G", "A", "0.7", " 0.0023", "0.0028", " 4.1e-01", "1"),
                             ("2", "500", "rs5", "T", "C", "0.9", "-0.0013", "0.0042", " 7.5e-01", "1")])
    r, _, rep = _restore(tmp_path, frozen, source, man, ["--raw", raw, "--raw-sample", 10000, "--seed", 20261021])
    assert r.returncode == 0, r.stderr
    m = _report(rep)
    assert (m["raw_n_sampled"], m["raw_n_alt_match"], m["raw_n_ref_match"], m["raw_n_absent"], m["raw_n_other"]) == \
        ("4", "2", "1", "1", "0")
    assert m["raw_alt_match_rate"] == "0.666667"  # of the 3 present


def test_pin_writes_rows_and_refuses_bad_input(tmp_path):
    frozen, source, man = _fixture(tmp_path)
    produced = tmp_path / "produced.bin"
    produced.write_bytes(b"x")
    out = tmp_path / "pins.tsv"
    r = _run(["pin", "--manifest", man, "--inputs", frozen, source, "--outputs", produced, "--out", out])
    assert r.returncode == 0, r.stderr
    with open(out) as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    assert [(x["role"], x["sha256"]) for x in rows] == [
        ("input", _sha(frozen)), ("input", _sha(source)), ("output", _sha(produced))]
    assert all(int(x["bytes"]) == Path(x["path"]).stat().st_size for x in rows)
    frozen.write_bytes(b"changed")
    out.unlink()
    r = _run(["pin", "--manifest", man, "--inputs", frozen, "--outputs", produced, "--out", out])
    assert r.returncode == 2 and not out.exists()
