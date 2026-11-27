"""asthma EUR effect-allele frequency complement check (W3f 15.8f2; Carter Q-158AEIW Hold;
DEC-2026-11-27-ta-r4-asthma-eur-eaf-sentence-held). Diagnostic only; nothing here filters a row."""
from __future__ import annotations

import ast
import csv
import hashlib
import os
import subprocess
import sys

import pytest
import yaml

from .conftest import MAN_DIR, REPO_ROOT

BIN = "/rs1/researchers/c/ckclinto/conda_envs/hlp_haplogroups/bin"
TABIX = f"{BIN}/tabix"
SAMTOOLS = f"{BIN}/samtools"
MODULE = REPO_ROOT / "src/python/ta_r4/orientation_eaf.py"
EAF_MAN = MAN_DIR / "sumstats_r4_orientation_eaf.tsv"
EAF_MAN_SHA = "7ad5ce50abfb6255da90c7eec98d760308a96c2d1eac348d4b8194e6239080c0"
FLIPPED_MAN = MAN_DIR / "sumstats_r4_orientation_eaf_asthma_eur_flipped.tsv"
PER_ROW_MAN = MAN_DIR / "sumstats_r4_orientation_eaf_asthma_eur_complement.tsv"
CROSSTAB_MAN = MAN_DIR / "sumstats_r4_orientation_eaf_asthma_eur_complement_crosstab.tsv"
RAW_MAN = MAN_DIR / "asthma_eur_gbmi_raw_sha256.tsv"
G37_MAN = MAN_DIR / "grch37_reference_sha256.tsv"
G38_MAN = MAN_DIR / "grch38_reference_sha256.tsv"
SUMSTATS_MAN = MAN_DIR / "sumstats_r4_sha256.tsv"
CATALOG_MAN = MAN_DIR / "catalogs_r4_fixed_point.tsv"
INPUT_BGZ = "data/processed/sumstats_harmonized/asthma.EUR.tsv.bgz"
LIFTED_BED = "data/r4/sumstats/liftover_strand/work_EUR/lifted.bed"
FASTA_NAME = "GRCh38_mapDamage.fa"
HOUSE = "rel_path\tsize_bytes\tsha256\tsource"
# Names-only exposure inputs written by R (15.8f2 Task 2 step 3): fit-panel variant keys of the production asthma / t2d
# EUR fit keys, and the pre-lock pilot fits' credible-set members among the complement rows. Pinned after their run.
Q8 = "data/r4/tmp/w3f/q158"
PANEL_KEYS = f"{Q8}/eafc_panel_keys_15_8f2.tsv"
PANEL_KEYS_SHA = "73e181256b90f972747434760d4497f2e3e722af49be9f25d3b0f4a09ac6bb4d"
MEMBERS = f"{Q8}/eafc_pilot_members_15_8f2.tsv"
MEMBERS_SHA = "57e1d9a195c97557fa03c0018161a8416fc11ae6a9438bb71aefcd2e8ee1a932"


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


def _tsv(path):
    with open(path, newline="") as fh:
        lines = fh.read().split("\n")
    assert lines[-1] == ""
    return [ln.split("\t") for ln in lines[:-1]]


@pytest.mark.r4_heavy
def test_asthma_eur_eaf_complement_manifests_rederive():
    sys.path.insert(0, str(REPO_ROOT / "src/python"))
    from ta_r4 import orientation_eaf as oe
    from ta_r4 import sumstats_orient as so

    os.chdir(REPO_ROOT)
    vcf_rel, g38_rel = _ref_paths()
    fasta = f"{g38_rel}/{FASTA_NAME}"
    # (a) every input opened, size + sha256 (the cheap raw pin first)
    raw = _house(RAW_MAN)
    assert len(raw) == 1
    ((raw_gz, (size, sha)),) = raw.items()
    assert os.stat(raw_gz).st_size == size and _sha256(raw_gz) == sha, raw_gz
    with open(SUMSTATS_MAN, newline="") as fh:
        pin = {r["path"]: (int(r["bytes"]), r["sha256"]) for r in csv.DictReader(fh, delimiter="\t")}
    opened = {INPUT_BGZ} | {so.oriented_path(t, a) for t, a in (("asthma", "EUR"),) + oe.EUR_REFERENCES}
    opened |= {so.source_path(t, a) for t, a in (("asthma", "EUR"),) + oe.EUR_REFERENCES}
    for rel in sorted(opened):
        assert (os.stat(rel).st_size, _sha256(rel)) == pin[rel], rel
    g37 = _house(G37_MAN)
    assert len(g37) == 48 and all(r.startswith(f"{vcf_rel}/") for r in g37)
    g38 = _house(G38_MAN)
    assert set(g38) == {fasta, f"{fasta}.fai", LIFTED_BED}
    for rel, (size, sha) in {**g37, **g38}.items():
        assert os.stat(rel).st_size == size and _sha256(rel) == sha, rel
    with open(CATALOG_MAN, newline="") as fh:
        cat_pin = {r["region_safe"]: r["final_sha256_pinned"] for r in csv.DictReader(fh, delimiter="\t")}
    from ta_r4 import paths
    for rs, *_ in so.windows("."):
        assert _sha256(paths.catalog_path("r4", rs)) == cat_pin[rs], rs
    assert _sha256(PANEL_KEYS) == PANEL_KEYS_SHA
    assert _sha256(MEMBERS) == MEMBERS_SHA
    # (d) the 15.8f aggregate manifest is unchanged by the additive functions
    assert hashlib.sha256(oe.render_eaf_manifest(oe.eaf_diffs(".", TABIX)).encode()).hexdigest() == EAF_MAN_SHA
    assert _sha256(EAF_MAN) == EAF_MAN_SHA
    # (b) both complement manifests rebuilt byte for byte
    rows, per_row, exposure = oe.complement_manifests(".", TABIX, vcf_rel, fasta, SAMTOOLS, INPUT_BGZ, LIFTED_BED,
                                                      raw_gz, PANEL_KEYS, MEMBERS)
    assert oe.render_complement_manifest(per_row).encode() == PER_ROW_MAN.read_bytes()
    assert oe.render_complement_crosstab(rows, per_row, exposure).encode() == CROSSTAB_MAN.read_bytes()
    # (c) identities read from the 15.8f manifests, never typed
    with open(EAF_MAN, newline="") as fh:
        agg = {(r["trait"], r["ancestry"], r["class"]): r
               for r in csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t")}
    for grp in ("flipped", "unflipped"):
        n = sum(1 for r in rows if r["group"] == grp and r["class"] != "palindromic_SNV"
                and r["pattern_t2d"] != "unavailable")
        assert n == int(agg[("asthma", "EUR", grp)]["n"]), grp
    fl = _tsv(FLIPPED_MAN)
    h = fl[0]
    want = {tuple(f[h.index(c)] for c in ("CHR", "POS", "REF", "ALT")) for f in fl[1:]
            if float(f[h.index("abs_delta_eaf")]) > 0.2
            and oe.eaf_pattern(float(f[h.index("EAF")]), float(f[h.index("EAF_reference")])) == "complement"}
    got = {(r["CHR"], r["POS"], r["REF"], r["ALT"]) for r in rows
           if r["group"] == "flipped" and r["class"] != "palindromic_SNV" and r["pattern_t2d"] == "complement"
           and abs(float(r["EAF"]) - float(r["EAF_t2d"])) > 0.2}
    assert got == want and len(got) > 0


def _fasta(tmp_path, seq):
    fa = tmp_path / "ref.fa"
    fa.write_text(">7\n" + "\n".join(seq[i:i + 60] for i in range(0, len(seq), 60)) + "\n")
    subprocess.run([SAMTOOLS, "faidx", str(fa)], check=True)
    return str(fa)


def test_eaf_complement_rules_and_module_hygiene(tmp_path):
    sys.path.insert(0, str(REPO_ROOT / "src/python"))
    from ta_r4 import orientation_eaf as oe

    # constants
    assert oe.AGREE_TOL == 0.1 and oe.COMPLEMENT_TOL == 0.1 and oe.DELTA_MIN == 0.2
    assert oe.SENSITIVITY_TOLS == (0.05, 0.10, 0.15)
    assert oe.EUR_REFERENCES == (("t2d", "EUR"), ("hypertension", "EUR"), ("bmi", "EUR"), ("stroke", "EUR"))
    # eaf_pattern
    p = oe.eaf_pattern
    print("float |0.5 - 0.6| =", abs(0.5 - 0.6))
    assert p(0.5, 0.55) == "agree"
    assert p(0.5, 0.6) == "agree"
    assert p(0.9, 0.12) == "complement"
    assert p(0.58, 0.42) == "other"
    assert p(0.7, 0.45) == "other"
    assert p(None, 0.3) == "unavailable" and p(0.3, None) == "unavailable"
    assert p(0.96, 0.12) == "complement"
    assert p(0.96, 0.12, agree_tol=0.05, complement_tol=0.05) == "other"
    assert p(0.5, 0.605) == "other"
    assert p(0.5, 0.605, agree_tol=0.11) == "agree"
    assert p(0.993201, 0.0151196734364025) == "complement"
    assert p(0.4555, 0.241496001646436) == "other"
    assert p(0.3003, 0.797690660177188) == "complement"
    assert p(0.3003, 0.797690660177188, agree_tol=0.05, complement_tol=0.05) == "other"
    # verdict
    v = oe.verdict
    assert v({"asthma": 0.99, "t2d": 0.015, "1kg": 0.02, "hypertension": None}) == "asthma_outlier"
    assert v({"asthma": 0.99, "t2d": 0.015, "1kg": 0.98}) == "t2d_outlier"
    assert v({"asthma": 0.3, "t2d": 0.32, "1kg": 0.29, "bmi": 0.31}) == "all_agree"
    assert v({"asthma": 0.99, "t2d": 0.015, "1kg": 0.5}) == "mixed"
    assert v({"asthma": 0.99, "t2d": 0.015}) == "lt3_sources"
    w = oe.verdict_with_1kg
    assert w({"asthma": 0.99, "t2d": 0.015, "1kg": 0.02}) == "asthma_outlier"
    assert w({"asthma": 0.99, "t2d": 0.015, "hypertension": 0.02, "bmi": 0.01, "1kg": None}) == "outlier_without_1kg"
    assert w({"asthma": 0.02, "t2d": 0.015, "1kg": 0.98}) == "outlier_without_1kg"
    assert w({"asthma": 0.99, "t2d": 0.015}) == "lt3_sources"
    # onekg_eaf (records = the 1000G lines at the row's POS)
    o = oe.onekg_eaf
    assert o("G", "A", [(100, "G", ["A"], ["0.3"])]) == ("exact", 0.3)
    m, e = o("G", "GA", [(100, "GA", ["G"], ["0.02"])])
    assert m == "swapped" and e == pytest.approx(0.98)
    assert o("G", "A", [(100, "G", ["A", "T"], ["0.1", "0.2"])]) == ("exact", 0.1)
    m, e = o("A", "G", [(100, "G", ["A", "T"], ["0.1", "0.2"])])
    assert m == "swapped" and e == pytest.approx(0.7)
    assert o("G", "A", [(100, "G", ["A"], ["0.1"]), (100, "G", ["A", "C"], ["0.1", "0.2"])]) == ("ambiguous", None)
    assert o("G", "A", [(100, "G", ["<CN0>"], ["0.1"])]) == ("none", None)
    assert o("G", "A", [(100, "G", ["<CN0>", "A"], ["0.1", "0.2"])]) == ("exact", 0.2)
    assert o("G", "A", [(100, "G", ["A"], ["."])]) == ("no_af", None)
    assert o("G", "A", [(100, "G", ["A"], [])]) == ("no_af", None)
    assert o("G", "A", []) == ("none", None)
    # indel_form / left_aligned / in_repeat on a tmp FASTA
    assert oe.indel_form("C", "CAT") == {"indel_kind": "insertion", "anchored": "true", "S": "AT"}
    assert oe.indel_form("CAT", "C") == {"indel_kind": "deletion", "anchored": "true", "S": "AT"}
    assert oe.indel_form("AC", "GT")["anchored"] == "false"
    assert oe.left_aligned("CAT", "C", "true") == "true"
    assert oe.left_aligned("ATA", "A", "true") == "false"
    assert oe.left_aligned("AC", "GT", "true") == "undetermined"
    assert oe.left_aligned("CAT", "C", "false") == "undetermined"
    #        pos 1234567890123456789012345678901234567890
    seq = "GGGGGCATATGGGGGGGGGGCTTTTGGGGGGGGGGGGG"
    fa = _fasta(tmp_path, seq)
    assert oe.in_repeat("C", "CAT", "7", 6, fa, SAMTOOLS) == "true"        # inserted AT, next bases AT
    assert oe.in_repeat("C", "CGC", "7", 6, fa, SAMTOOLS) == "false"       # inserted GC, next bases AT
    assert oe.in_repeat("CAT", "C", "7", 6, fa, SAMTOOLS) == "true"        # deleted AT (7-8), bases 9-10 = AT
    assert oe.in_repeat("CATAT", "C", "7", 6, fa, SAMTOOLS) == "false"     # deleted ATAT (7-10), bases 11-14 = GGGG
    assert oe.in_repeat("CT", "C", "7", 21, fa, SAMTOOLS) == "true"        # deleted T, next base T
    assert oe.in_repeat("CTT", "C", "7", 21, fa, SAMTOOLS) == "true"       # deleted TT, next bases TT
    assert oe.in_repeat("AC", "GT", "7", 6, fa, SAMTOOLS) == "undetermined"
    assert oe.in_repeat("C", "CAT", "7", len(seq), fa, SAMTOOLS) == "undetermined"   # past the contig end
    assert oe.in_repeat("C", "CAT", "9", 6, fa, SAMTOOLS) == "undetermined"          # contig absent
    # import hygiene: no side effect at import, no tests import, no storage literal
    cwd = tmp_path / "empty"
    cwd.mkdir()
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src/python"), PYTHONDONTWRITEBYTECODE="1")
    subprocess.run([sys.executable, "-c", "import ta_r4.orientation_eaf"], cwd=cwd, env=env, check=True)
    assert os.listdir(cwd) == []
    tree = ast.parse(MODULE.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not any(a.name.split(".")[0] == "tests" for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] != "tests"
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert not any(s in node.value for s in ("/rs1", "/share", "/gpfs_common")), node.value
