"""D-06 unit 2: plink_ld_to_rds.R --emit-ref-alt (default off). REF := A2, ALT := A1 from the .bim; the LD sign
under plink 1.9 --keep-allele-order is the correlation of A1 (= ALT) dosages; flag off is identical() to the
pre-change script."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "src/snakemake/scripts/plink_ld_to_rds.R"
PRE_CHANGE_BLOB = "6f9986d7247f97f929950cfc49a6b970d981fb6d"  # plink_ld_to_rds.R at 9eb162d8 (before W1)
RSCRIPT = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"
R4_PLINK = "/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/55c377a7e8fce799d92381bcc5138d7f_/bin/plink"

# 6 samples x 3 SNPs as A1 dosages; SNP 2's A1 is the major allele (8/12), so plink without
# --keep-allele-order would relabel it.
BIM = [("1", "s1", "0", "100", "A", "G"), ("1", "s2", "0", "200", "C", "T"), ("1", "s3", "0", "300", "G", "A")]
DOS = np.array([[2, 1, 0, 1, 0, 0],
                [2, 2, 1, 1, 0, 2],
                [0, 1, 2, 1, 0, 1]])
_CODE = {2: 0b00, 1: 0b10, 0: 0b11}  # PLINK 1 .bed: 00 hom A1, 10 het, 11 hom A2


def _write_bfile(prefix, bim, dos):
    Path(f"{prefix}.bim").write_text("".join("\t".join(r) + "\n" for r in bim))
    Path(f"{prefix}.fam").write_text("".join(f"f{i} i{i} 0 0 0 -9\n" for i in range(dos.shape[1])))
    out = bytearray(b"\x6c\x1b\x01")
    for row in dos:
        for k in range(0, len(row), 4):
            b = 0
            for j, d in enumerate(row[k:k + 4]):
                b |= _CODE[int(d)] << (2 * j)
            out.append(b)
    Path(f"{prefix}.bed").write_bytes(bytes(out))


def _plink_r(tmp, prefix, keep_order=True):
    out = tmp / (Path(prefix).name + ("_kao" if keep_order else "_nokao"))
    cmd = [R4_PLINK, "--bfile", str(prefix), "--r", "square", "--out", str(out)]
    if keep_order:
        cmd.insert(3, "--keep-allele-order")
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return f"{out}.ld"


def _to_rds(script, ld, variants, out, extra=()):
    return subprocess.run([RSCRIPT, str(script), "--ld", str(ld), "--variants", str(variants), "--region-id", "FIX",
                           "--ancestry", "EUR", "--ld-source", "fixture", "--output", str(out), *extra],
                          capture_output=True, text=True)


def _r(expr):
    r = subprocess.run([RSCRIPT, "-e", expr], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def _variants_and_R(rds):
    out = _r(f'o <- readRDS("{rds}"); cat(o$variants$REF, sep=","); cat("\\n"); cat(o$variants$ALT, sep=",");'
             f'cat("\\n"); cat(attr(o, "ref_alt_source")); cat("\\n"); cat(sprintf("%.10f", o$R), sep=",")')
    ref, alt, src, r = out.split("\n")
    return ref.split(","), alt.split(","), src, np.array([float(x) for x in r.split(",")]).reshape(3, 3, order="F")


@pytest.fixture
def old_script(tmp_path):
    p = tmp_path / "plink_ld_to_rds.pre_W1.R"
    p.write_text(subprocess.run(["git", "cat-file", "blob", PRE_CHANGE_BLOB], cwd=REPO, capture_output=True,
                                text=True, check=True).stdout)
    return p


@pytest.fixture
def bfile(tmp_path):
    prefix = tmp_path / "x"
    _write_bfile(prefix, BIM, DOS)
    return prefix


def _pvar(tmp_path):
    p = tmp_path / "x.pvar"
    p.write_text("##fileformat=PVARv1.0\n#CHROM\tPOS\tID\tREF\tALT\n" +
                 "".join(f"{c}\t{pos}\t{i}\t{a2}\t{a1}\n" for c, i, _, pos, a1, a2 in BIM))
    return p


@pytest.mark.parametrize("kind", ["bim", "pvar"])
@pytest.mark.parametrize("flag", [None, "false"])
def test_flag_off_identical_to_pre_change(tmp_path, old_script, bfile, kind, flag):
    ld = _plink_r(tmp_path, bfile)
    variants = f"{bfile}.bim" if kind == "bim" else _pvar(tmp_path)
    extra = [] if flag is None else ["--emit-ref-alt", flag]
    a, b = tmp_path / "old.rds", tmp_path / "new.rds"
    ra, rb = _to_rds(old_script, ld, variants, a), _to_rds(SCRIPT, ld, variants, b, extra)
    assert ra.returncode == 0 and rb.returncode == 0, ra.stderr + rb.stderr
    assert _r(f'cat(identical(readRDS("{a}"), readRDS("{b}")))') == "TRUE"


def test_emit_ref_alt_from_bim(tmp_path, bfile):
    out = tmp_path / "x.rds"
    r = _to_rds(SCRIPT, _plink_r(tmp_path, bfile), f"{bfile}.bim", out, ["--emit-ref-alt", "true"])
    assert r.returncode == 0, r.stderr
    ref, alt, src, _ = _variants_and_R(out)
    assert ref == [b[5] for b in BIM] and alt == [b[4] for b in BIM]
    assert src == "bim_A2_A1_keep_allele_order"


def test_emit_ref_alt_refuses_pvar(tmp_path, bfile):
    r = _to_rds(SCRIPT, _plink_r(tmp_path, bfile), _pvar(tmp_path), tmp_path / "x.rds", ["--emit-ref-alt", "true"])
    assert r.returncode != 0 and "--emit-ref-alt requires .bim" in r.stderr
    assert not (tmp_path / "x.rds").exists()


@pytest.mark.parametrize("bad", ["yes", "TRUE", "1"])
def test_emit_ref_alt_rejects_unrecognised_value(tmp_path, bfile, bad):
    r = _to_rds(SCRIPT, _plink_r(tmp_path, bfile), f"{bfile}.bim", tmp_path / "x.rds", ["--emit-ref-alt", bad])
    assert r.returncode != 0 and "--emit-ref-alt" in r.stderr
    assert not (tmp_path / "x.rds").exists()


def test_known_answer_ld_sign_is_alt_dosage_correlation(tmp_path, bfile):
    out = tmp_path / "x.rds"
    assert _to_rds(SCRIPT, _plink_r(tmp_path, bfile), f"{bfile}.bim", out, ["--emit-ref-alt", "true"]).returncode == 0
    ref, alt, _, R = _variants_and_R(out)
    a1 = [b[4] for b in BIM]
    # ALT-letter count per SNP: the .bed codes A1 dosage, so it is d when ALT is the .bim A1 letter, else 2 - d
    alt_dos = np.array([DOS[k] if alt[k] == a1[k] else 2 - DOS[k] for k in range(3)])
    want = np.corrcoef(alt_dos)
    print(f"R[1,2] {R[0, 1]:.10f} cor(A1 dosage 1, A1 dosage 2) {np.corrcoef(DOS)[0, 1]:.10f}")
    assert abs(R[0, 1] - np.corrcoef(DOS)[0, 1]) < 1e-6
    assert np.allclose(R, want, atol=1e-6)

    # Swap A1/A2 of SNP 2 in the .bim and recode its .bed dosage to 2 - d2 (same letter genotypes):
    # the sign flips, and so does the emitted ALT.
    swapped = tmp_path / "y"
    bim2 = [BIM[0], BIM[1][:4] + (BIM[1][5], BIM[1][4]), BIM[2]]
    recoded = DOS.copy()
    recoded[1] = 2 - DOS[1]
    _write_bfile(swapped, bim2, recoded)
    out2 = tmp_path / "y.rds"
    assert _to_rds(SCRIPT, _plink_r(tmp_path, swapped), f"{swapped}.bim", out2,
                   ["--emit-ref-alt", "true"]).returncode == 0
    ref2, alt2, _, R2 = _variants_and_R(out2)
    print(f"swapped R[1,2] {R2[0, 1]:.10f} cor(d1, 2 - d2) {np.corrcoef(recoded)[0, 1]:.10f}")
    assert abs(R2[0, 1] - np.corrcoef(recoded)[0, 1]) < 1e-6
    assert np.sign(R2[0, 1]) == -np.sign(R[0, 1]) != 0
    assert (alt2[1], ref2[1]) == (BIM[1][5], BIM[1][4])
    a1b = [b[4] for b in bim2]
    alt_dos2 = np.array([recoded[k] if alt2[k] == a1b[k] else 2 - recoded[k] for k in range(3)])
    assert np.allclose(R2, np.corrcoef(alt_dos2), atol=1e-6)


def test_without_keep_allele_order_sign_follows_minor_allele(tmp_path, bfile):
    """Why the R4 rule needs --keep-allele-order: plink otherwise re-codes SNP 2 (A1 major) to its minor allele
    and R[1,2] no longer equals the correlation of the .bim A1 dosages."""
    R_kao = np.loadtxt(_plink_r(tmp_path, bfile, True))
    R_no = np.loadtxt(_plink_r(tmp_path, bfile, False))
    print(f"kao R[1,2] {R_kao[0, 1]:.10f}  no-kao R[1,2] {R_no[0, 1]:.10f}")
    assert np.sign(R_no[0, 1]) == -np.sign(R_kao[0, 1]) != 0
