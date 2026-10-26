"""W2a T3: panel manifests (memory-bounded inspection) and the D-12a known-answer live gate."""
from __future__ import annotations

import csv
import shutil
import subprocess
from pathlib import Path

import pytest

from ta_r4 import panel_manifest as pm

REPO = Path(__file__).resolve().parents[2]
RSCRIPT = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"


def _r(code):
    p = subprocess.run([RSCRIPT, "-e", code], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr


def _fixture(d):
    d.mkdir(parents=True, exist_ok=True)
    _r(f"""
v <- data.frame(SNP_ID=c('rs1','rs2','rs3'), CHR='1', POS=c(10L,20L,30L), A1=c('A','C','G'), A2=c('G','T','A'),
                stringsAsFactors=FALSE)
v$REF <- v$A2; v$ALT <- v$A1
R <- matrix(c(1,.5,-.2,.5,1,.1,-.2,.1,1), 3)
saveRDS(list(R=R, variants=v, ld_source='x'), '{d}/REAL.rds')
saveRDS(list(R=diag(3), variants=v, ld_source='identity_matched_r4'), '{d}/IDENT.rds')
saveRDS(list(R=NULL, variants=v[,c('CHR','POS','REF','ALT','SNP_ID')], use_identity=TRUE, status='identity'), '{d}/NULLR.rds')
""")


def _read(p):
    with open(p, newline="") as fh:
        return {r["region_safe"]: r for r in csv.DictReader(fh, delimiter="\t")}


def test_manifest_rows(tmp_path):
    _fixture(tmp_path / "p")
    out = tmp_path / "m.tsv"
    pm.write_manifest(tmp_path / "p", "EUR", "src", "GRCh37", "489", out, rscript=RSCRIPT, block=2)
    rows = _read(out)
    assert set(rows) == {"REAL", "IDENT", "NULLR"}
    assert list(rows["REAL"])[:2] == ["ancestry", "region_safe"]
    assert {k: rows["REAL"][k] for k in ("n_var", "r_kind", "has_ref_alt", "n_samples", "build", "source")} == \
        {"n_var": "3", "r_kind": "matrix", "has_ref_alt": "true", "n_samples": "489", "build": "GRCh37",
         "source": "src"}
    assert rows["REAL"]["identity_exact"] == "false"
    assert rows["IDENT"]["identity_exact"] == "true"
    assert rows["NULLR"]["r_kind"] == "null" and rows["NULLR"]["n_var"] == "3"
    assert rows["NULLR"]["has_ref_alt"] == "true"  # k2d frame carries REF/ALT columns from the catalog
    assert pm.md5_mismatches(out) == []


def test_duplicate_key_refused(tmp_path):
    _fixture(tmp_path / "p")
    out = tmp_path / "m.tsv"
    pm.write_manifest(tmp_path / "p", "EUR", "s", "GRCh37", "NA", out, rscript=RSCRIPT)
    pm.write_manifest(tmp_path / "p", "AFR", "s", "GRCh37", "NA", out, rscript=RSCRIPT)
    assert len(_read_all(out)) == 6
    with pytest.raises(pm.ManifestError, match="duplicate"):
        pm.write_manifest(tmp_path / "p", "EUR", "s", "GRCh37", "NA", out, rscript=RSCRIPT)


def _read_all(p):
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


@pytest.mark.parametrize("bad,match", [
    ("R[1,2] <- 0.3", "symmetric"),
    ("R[2,2] <- 0.9", "diag"),
    ("R[1,3] <- NaN; R[3,1] <- NaN", "finite"),
])
def test_bad_matrix_refused(tmp_path, bad, match):
    d = tmp_path / "p"
    d.mkdir()
    _r(f"""
v <- data.frame(SNP_ID=c('rs1','rs2','rs3'), CHR='1', POS=c(10L,20L,30L), A1='A', A2='G')
R <- matrix(c(1,.5,-.2,.5,1,.1,-.2,.1,1), 3); {bad}
saveRDS(list(R=R, variants=v), '{d}/BAD.rds')
""")
    with pytest.raises(pm.ManifestError, match=match):
        pm.write_manifest(d, "EUR", "s", "GRCh37", "NA", tmp_path / "m.tsv", rscript=RSCRIPT, block=2)
    assert not (tmp_path / "m.tsv").exists()


def test_md5_check_sees_a_corrupted_byte(tmp_path):
    _fixture(tmp_path / "p")
    out = tmp_path / "m.tsv"
    pm.write_manifest(tmp_path / "p", "EUR", "s", "GRCh37", "NA", out, rscript=RSCRIPT)
    f = tmp_path / "p" / "REAL.rds"
    b = bytearray(f.read_bytes())
    b[len(b) // 2] ^= 0xFF
    f.write_bytes(bytes(b))
    bad = pm.md5_mismatches(out)
    assert [r[1] for r in bad] == ["REAL"]


# --- live gate (D-12a) ----------------------------------------------------------------------------

R4_DIR = REPO / "data/r4/ld/EUR_1kg_r4"


@pytest.mark.r4_heavy
@pytest.mark.skipif(not R4_DIR.is_dir(), reason="data/r4/ld/EUR_1kg_r4 absent (W2a not built)")
def test_known_answer_live_gate(tmp_path):
    findings = REPO / "data/r4/findings/panel_known_answers.tsv"
    rows = pm.known_answers(REPO, findings, rscript=RSCRIPT)
    on_disk = _read_all(findings)
    assert len(on_disk) == len(rows) > 0
    by = {}
    for r in on_disk:
        by.setdefault(r["check"], []).append(r)
    man = {k: _read_all(REPO / pm.MANIFESTS[k]) for k in pm.MANIFESTS}
    assert len(by["md5"]) == sum(len(v) for v in man.values())
    assert len(by["n_var_equal"]) == len(by["abs_r_equal"]) == len(man["legacy_repro"]) == 10
    assert len(by["identity_variants_identical"]) == len(man["EUR_identity_r4"]) == len(man["EUR_1kg_r4"]) == 29
    assert len(by["has_ref_alt"]) == 39
    assert len(by["sh2b3_legacy_n_var"]) == 1
    failed = [r for r in on_disk if r["check"] != "sh2b3_legacy_n_var" and r["status"] != "PASS"]
    assert failed == []


@pytest.mark.r4_heavy
@pytest.mark.skipif(not R4_DIR.is_dir(), reason="data/r4/ld/EUR_1kg_r4 absent (W2a not built)")
def test_live_md5_negative_control(tmp_path):
    """A corrupted byte in a copy of a real panel must be caught by the md5 check the gate uses."""
    man = REPO / pm.MANIFESTS["EUR_1kg_r4"]
    rows = _read_all(man)
    row = next(r for r in rows if r["region_safe"] == "SH2B3_12q24")
    copy = tmp_path / "SH2B3_12q24.rds"
    shutil.copyfile(REPO / row["path"], copy)
    b = bytearray(copy.read_bytes())
    b[len(b) // 3] ^= 0x01
    copy.write_bytes(bytes(b))
    m2 = tmp_path / "m.tsv"
    with open(man) as fh, open(m2, "w") as out:
        hdr = fh.readline()
        out.write(hdr)
        cols = hdr.rstrip("\n").split("\t")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if f[cols.index("region_safe")] == "SH2B3_12q24":
                f[cols.index("path")] = str(copy)
                out.write("\t".join(f) + "\n")
    assert [r[1] for r in pm.md5_mismatches(m2, root=REPO)] == ["SH2B3_12q24"]
