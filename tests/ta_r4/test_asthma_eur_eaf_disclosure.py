"""asthma EUR flipped-row EAF diagnostic measured against GRCh38 and 1000G Phase 3 GRCh37 (W3f 15.8f; Carter Q-158AEI,
Q-158AEIM; DEC-2026-11-26-ta-r4-asthma-eur-eaf-disclose-no-filter). Diagnostic only; nothing here filters a row."""
from __future__ import annotations

import ast
import csv
import gzip
import hashlib
import os
import statistics
import subprocess
import sys

import pytest
import yaml

from .conftest import MAN_DIR, REPO_ROOT

BIN = "/rs1/researchers/c/ckclinto/conda_envs/hlp_haplogroups/bin"
TABIX = f"{BIN}/tabix"
SAMTOOLS = f"{BIN}/samtools"
BGZIP = f"{BIN}/bgzip"
MODULE = REPO_ROOT / "src/python/ta_r4/orientation_eaf.py"
EAF_MAN = MAN_DIR / "sumstats_r4_orientation_eaf.tsv"
ROWS_MAN = MAN_DIR / "sumstats_r4_orientation_eaf_asthma_eur_flipped.tsv"
CTRL_MAN = MAN_DIR / "sumstats_r4_orientation_eaf_asthma_eur_unflipped_control.tsv"
G37_MAN = MAN_DIR / "grch37_reference_sha256.tsv"
G38_MAN = MAN_DIR / "grch38_reference_sha256.tsv"
SUMSTATS_MAN = MAN_DIR / "sumstats_r4_sha256.tsv"
INPUT_BGZ = "data/processed/sumstats_harmonized/asthma.EUR.tsv.bgz"
LIFTED_BED = "data/r4/sumstats/liftover_strand/work_EUR/lifted.bed"
FASTA_NAME = "GRCh38_mapDamage.fa"
HOUSE = "rel_path\tsize_bytes\tsha256\tsource"
GRCH38_PRIMARY = dict(zip(
    [str(i) for i in range(1, 23)] + ["X", "Y"],
    [248956422, 242193529, 198295559, 190214555, 181538259, 170805979, 159345973, 145138636, 138394717, 133797422,
     135086622, 133275309, 114364328, 107043718, 101991189, 90338345, 83257441, 80373285, 58617616, 64444167,
     46709983, 50818468, 156040895, 57227415]))
COLUMNS = ["region_safe", "CHR", "POS", "SNP_ID", "REF", "ALT", "REF_oriented", "ALT_oriented", "class", "EAF",
           "EAF_reference", "abs_delta_eaf", "above_0.2", "input_line", "strand", "CHR_GRCh38", "POS_GRCh38",
           "REF_GRCh38", "ALT_GRCh38", "grch38_bases", "grch38_ref_match", "grch37_bases", "grch37_ref_match",
           "lift_changed_ref", "source_ref_not_grch38", "grch37_bases_oriented", "catalog_ref_grch37_match"]
CTRL_COLUMNS = COLUMNS + ["stratum", "stratum_n"]
SEED = 20261127
N_PER_STRATUM = 2000
STRATA = ("SNV>0.2", "SNV<=0.2", "indel>0.2", "indel<=0.2")


def _ref_paths():
    src = yaml.safe_load(open(REPO_ROOT / "config/ta_r4/data_sources.yaml"))["sources"]
    return src["onekg_phase3_vcf"]["url"], src["grch38_fasta_mapdamage"]["url"]


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def _house(path):
    lines = open(path, newline="").read().split("\n")
    assert lines[-1] == "", f"{path}: no final newline"
    assert lines[0] == HOUSE, f"{path}: line 1 {lines[0]!r}"
    out = {}
    for ln in lines[1:-1]:
        rel, size, sha, src = ln.split("\t")
        assert rel not in out and src
        out[rel] = (int(size), sha)
    return out


def control_header(rows):
    """Line 1 of the control manifest: the sampling rule and each stratum's population size."""
    pops = {}
    for r in rows:
        pops[r["stratum"]] = r["stratum_n"]
    return ("# control: asthma EUR unflipped rows of the sumstats_r4_orientation_eaf.tsv join; seed 20261127; strata "
            "class × (abs_delta_eaf > 0.2); all rows of > 0.2 strata; 2000 per <= 0.2 stratum (all if fewer); "
            "stratum_n = population; " + "; ".join(f"{s} stratum_n {pops.get(s, 0)}" for s in STRATA))


def measure(oe, rows, vcf_dir, fasta):
    """The measured columns, composed from the module's functions (the driver composes them the same way)."""
    out = []
    for r in rows:
        r = dict(r)
        b38 = oe.grch38_bases(r["CHR_GRCh38"], int(r["POS_GRCh38"]), len(r["REF_GRCh38"]), fasta, SAMTOOLS)
        m38 = oe.ref_match(r["REF_GRCh38"], b38)
        b37 = oe.grch37_bases(r["CHR"], int(r["POS"]), len(r["REF"]), vcf_dir, TABIX)
        m37 = oe.ref_match(r["REF"], b37)
        b37o = oe.grch37_bases(r["CHR"], int(r["POS"]), len(r["REF_oriented"]), vcf_dir, TABIX)
        r.update({
            "above_0.2": "true" if r["abs_delta_eaf"] > 0.2 else "false",
            "grch38_bases": "NA" if b38 is None else b38, "grch38_ref_match": m38,
            "grch37_bases": b37, "grch37_ref_match": m37,
            "lift_changed_ref": oe.k_and(m38, oe.k_not(m37)), "source_ref_not_grch38": oe.k_not(m38),
            "grch37_bases_oriented": b37o, "catalog_ref_grch37_match": oe.ref_match(r["REF_oriented"], b37o)})
        out.append(r)
    return out


def _cell(v):
    return repr(v) if isinstance(v, float) else str(v)


def _read_tsv(path, skip=0):
    with open(path, newline="") as fh:
        lines = fh.read().split("\n")
    assert lines[-1] == ""
    return lines[:skip], [ln.split("\t") for ln in lines[skip:-1]]


def _aggregate():
    with open(EAF_MAN, newline="") as fh:
        rd = csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t")
        return {(r["trait"], r["ancestry"], r["class"]): r for r in rd}


@pytest.mark.r4_heavy
def test_asthma_eur_flipped_eaf_manifests_rederive():
    sys.path.insert(0, str(REPO_ROOT / "src/python"))
    from ta_r4 import orientation_eaf as oe

    os.chdir(REPO_ROOT)
    vcf_rel, g38_rel = _ref_paths()
    fasta = f"{g38_rel}/{FASTA_NAME}"
    # (b) reference pins first (size + sha256 of every listed file; the opened set is checked below)
    p37, p38 = _house(G37_MAN), _house(G38_MAN)
    listed = {**p37, **p38}
    for rel, (size, sha) in listed.items():
        assert os.stat(rel).st_size == size, rel
        assert _sha256(rel) == sha, rel
    with open(SUMSTATS_MAN, newline="") as fh:
        pin = {r["path"]: r["sha256"] for r in csv.DictReader(fh, delimiter="\t")}
    assert _sha256(INPUT_BGZ) == pin[INPUT_BGZ]
    fai = {ln.split("\t")[0]: int(ln.split("\t")[1]) for ln in open(f"{fasta}.fai")}
    assert {c: fai.get(c) for c in GRCH38_PRIMARY} == GRCH38_PRIMARY
    agg = _aggregate()
    # (a) the aggregate manifest, byte for byte
    assert oe.render_eaf_manifest(oe.eaf_diffs(".", TABIX)).encode() == EAF_MAN.read_bytes()
    rows = oe.flipped_rows(".", TABIX)
    ctrl_pop = oe.eaf_rows(".", TABIX, "asthma", "EUR", "unflipped")
    ctrl = oe.control_sample(ctrl_pop, seed=SEED, n_per_stratum=N_PER_STRATUM)
    g38 = oe.grch38_rows(rows + ctrl, INPUT_BGZ, LIFTED_BED)
    rows, ctrl = g38[:len(rows)], g38[len(rows):]
    chroms = sorted({("X" if r["CHR"] == "23" else r["CHR"]) for r in rows + ctrl})
    opened = {f"{fasta}", f"{fasta}.fai", LIFTED_BED}
    opened |= {f"{vcf_rel}/chr{c}.vcf.gz" for c in chroms} | {f"{vcf_rel}/chr{c}.vcf.gz.tbi" for c in chroms}
    missing = sorted(opened - set(listed))
    assert not missing, missing
    # (c) both per-row manifests rebuilt, all columns, in order
    rows, ctrl = measure(oe, rows, vcf_rel, fasta), measure(oe, ctrl, vcf_rel, fasta)
    _, got = _read_tsv(ROWS_MAN)
    assert got[0] == COLUMNS
    assert got[1:] == [[_cell(r[c]) for c in COLUMNS] for r in rows]
    head, got = _read_tsv(CTRL_MAN, skip=1)
    assert head == [control_header(ctrl)]
    assert got[0] == CTRL_COLUMNS
    assert got[1:] == [[_cell(r[c]) for c in CTRL_COLUMNS] for r in ctrl]
    pops = {r["stratum"]: r["stratum_n"] for r in ctrl}
    unf = agg[("asthma", "EUR", "unflipped")]
    assert sum(pops.values()) == int(unf["n"]) == 216105
    assert pops["SNV>0.2"] + pops["indel>0.2"] == int(unf["n_above_0.2"]) == 525
    assert sum(1 for r in ctrl if r["abs_delta_eaf"] > 0.2) == 525
    # (d) the per-row flipped manifest agrees with the aggregate flipped row
    fl = agg[("asthma", "EUR", "flipped")]
    d = [r["abs_delta_eaf"] for r in rows]
    assert (len(d), f"{statistics.median(d):.4f}", sum(x > 0.2 for x in d)) == (int(fl["n"]), fl["median_abs_delta_eaf"], int(fl["n_above_0.2"])) == (225, "0.0270", 19)
    assert (sum(r["class"] == "SNV" for r in rows), sum(r["class"] == "indel" for r in rows)) == (204, 21)
    assert sum(r["class"] == "indel" and r["abs_delta_eaf"] > 0.2 for r in rows) == 14


def _vcf(tmp_path, name, contig, records):
    plain = tmp_path / name.replace(".gz", "")
    with open(plain, "w") as fh:
        fh.write("##fileformat=VCFv4.1\n")
        fh.write(f"##contig=<ID={contig}>\n")
        fh.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        for pos, ref, alt in records:
            fh.write(f"{contig}\t{pos}\t.\t{ref}\t{alt}\t.\tPASS\t.\n")
    subprocess.run([BGZIP, "-f", str(plain)], check=True)
    subprocess.run([TABIX, "-p", "vcf", str(tmp_path / name)], check=True)


def test_orientation_eaf_rules_and_import_hygiene(tmp_path):
    sys.path.insert(0, str(REPO_ROOT / "src/python"))
    from ta_r4 import orientation_eaf as oe

    b = oe.bases_from_records
    assert b(100, 2, [(99, "CAT")]) == "AT"           # upstream multi-base record: only its in-span bases
    assert b(100, 2, [(90, "N")]) == ".."             # SV record whose REF is outside the span
    assert b(100, 2, [(102, "G")]) == ".."            # record past the span end
    assert b(100, 2, [(100, "A")]) == "A."            # partial coverage
    assert b(100, 2, [(100, "AT"), (101, "T")]) == "AT"  # full coverage, agreeing records
    with pytest.raises(Exception):
        b(100, 2, [(100, "AT"), (101, "G")])          # records disagree
    # CHR 23 -> chrX.vcf.gz / contig X
    vdir = tmp_path / "vcf"
    vdir.mkdir()
    _vcf(vdir, "chrX.vcf.gz", "X", [(500, "G", "A"), (501, "CT", "C")])
    _vcf(vdir, "chr23.vcf.gz", "23", [(500, "T", "A")])
    assert oe.grch37_bases("23", 500, 3, str(vdir), TABIX) == "GCT"
    assert oe.grch37_bases("X", 500, 1, str(vdir), TABIX) == "G"
    # ref_match and Kleene truth tables
    assert oe.ref_match("AT", "AT") == "true"
    assert oe.ref_match("AT", "AG") == "false"
    assert oe.ref_match("AT", "A.") == "undetermined"
    assert oe.ref_match("AT", "G.") == "false"
    assert oe.ref_match("A", None) == "undetermined"
    V = ("true", "false", "undetermined")
    AND = {("true", "true"): "true", ("true", "false"): "false", ("true", "undetermined"): "undetermined",
           ("false", "true"): "false", ("false", "false"): "false", ("false", "undetermined"): "false",
           ("undetermined", "true"): "undetermined", ("undetermined", "false"): "false",
           ("undetermined", "undetermined"): "undetermined"}
    assert {(x, y): oe.k_and(x, y) for x in V for y in V} == AND
    assert {x: oe.k_not(x) for x in V} == {"true": "false", "false": "true", "undetermined": "undetermined"}
    # control_sample: deterministic for the seed, every > 0.2 row kept, min(n, N) per <= 0.2 stratum, input order
    syn = []
    for i in range(60):
        cls = "SNV" if i % 3 else "indel"
        syn.append({"CHR": str(1 + i % 2), "POS": str(1000 + i), "REF": "A" if cls == "SNV" else "AT", "ALT": "G",
                    "SNP_ID": f"rs{i}", "class": cls, "abs_delta_eaf": 0.5 if i % 10 == 0 else 0.01, "i": i})
    s1 = oe.control_sample(syn, seed=SEED, n_per_stratum=5)
    s2 = oe.control_sample(list(reversed(syn)), seed=SEED, n_per_stratum=5)
    assert sorted(r["i"] for r in s1) == sorted(r["i"] for r in s2)
    assert [r["i"] for r in s1] == sorted(r["i"] for r in s1)
    hi = [r["i"] for r in syn if r["abs_delta_eaf"] > 0.2]
    assert set(hi) <= {r["i"] for r in s1}
    n = {s: sum(1 for r in s1 if r["stratum"] == s) for s in STRATA}
    pop = {s: sum(1 for r in syn if f"{r['class']}{'>0.2' if r['abs_delta_eaf'] > 0.2 else '<=0.2'}" == s) for s in STRATA}
    assert n == {"SNV>0.2": pop["SNV>0.2"], "indel>0.2": pop["indel>0.2"], "SNV<=0.2": 5, "indel<=0.2": 5}
    assert all(r["stratum_n"] == pop[r["stratum"]] for r in s1)
    big = oe.control_sample(syn, seed=SEED, n_per_stratum=1000)
    assert len(big) == len(syn)
    assert [r["i"] for r in oe.control_sample(syn, seed=SEED + 1, n_per_stratum=5)] != [r["i"] for r in s1]
    # import hygiene: no side effect at import, no tests import, no storage literal
    cwd = tmp_path / "empty"
    cwd.mkdir()
    mans = [EAF_MAN, ROWS_MAN, CTRL_MAN]
    before = {str(p): (_sha256(p), os.stat(p).st_mtime_ns) for p in mans if p.exists()}
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src/python"), PYTHONDONTWRITEBYTECODE="1")
    subprocess.run([sys.executable, "-c", "import ta_r4.orientation_eaf"], cwd=cwd, env=env, check=True)
    assert os.listdir(cwd) == []
    assert {str(p): (_sha256(p), os.stat(p).st_mtime_ns) for p in mans if p.exists()} == before
    assert len(before) == 3
    tree = ast.parse(MODULE.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not any(a.name.split(".")[0] == "tests" for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] != "tests"
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert not any(s in node.value for s in ("/rs1", "/share", "/gpfs_common")), node.value
