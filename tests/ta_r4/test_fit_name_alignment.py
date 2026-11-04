"""N2 (W3f): fit variant names align to the region sumstats through the LD panel the fit was built against.

map_fit_names(names, ss, panel_variants): a unique sumstats name maps directly; otherwise the name must be a unique
panel SNP_ID whose CHR:POS has exactly one allele-compatible sumstats row (exact, swapped, or the strand complement
of either for a non-palindromic SNV). Any unmapped name is a hard error. --ld-panel must be the panel the fit's JSON
records (FIT_PANEL_MISMATCH).
"""
from __future__ import annotations

import gzip
import json
import os
import re
import shutil
import subprocess

import pytest

from .conftest import REPO_ROOT
from .fixtures.build_toy_workflow import ANC, RSCRIPT, coloc, ok, pair_row, pair_session_root, run

from ta_r4 import commands, paths

SCRIPT = REPO_ROOT / commands.COLOC_SCRIPT
ARM = "A3_1kg"
OVR, MIX = pair_row("FIXP_OVR"), pair_row("FIXP_MIX")

_R = r'''
suppressPackageStartupMessages({library(data.table); library(jsonlite)})
E <- new.env(); sys.source("%s", envir = E)
ss <- data.table(CHR = "1", POS = c(100L, 200L, 300L, 400L, 500L, 600L, 700L, 800L, 900L, 900L, 1000L, 1100L),
                 REF = c("A", "A", "C", "T", "G", "A", "T", "A", "A", "A", NA, "c"),
                 ALT = c("C", "C", "A", "G", "T", "T", "A", "G", "C", "C", NA, "a"))
ss[, SNP_ID := sprintf("1:%%d", POS)]
ss[, cp := SNP_ID]; ss[, name := SNP_ID]
pv <- data.frame(SNP_ID = c("rsE", "rsS", "rsT", "rsU", "rsP", "rsQ", "rsM", "rsW", "rsD", "rsD", "rsN", "rsA",
                            "rsL", "rsX"),
                 CHR = 1L, POS = c(200L, 300L, 400L, 500L, 600L, 700L, 800L, 600L, 200L, 200L, 1000L, 900L, 1100L,
                                   1200L),
                 REF = c("A", "A", "A", "A", "A", "A", "A", "C", "A", "A", "A", "A", "A", "A"),
                 ALT = c("C", "C", "C", "C", "T", "T", "C", "G", "C", "C", "C", "C", "C", "C"),
                 stringsAsFactors = FALSE)
pv$A1 <- pv$ALT; pv$A2 <- pv$REF
pv_unordered <- pv[, c("SNP_ID", "CHR", "POS", "A1", "A2")]
case <- function(names, panel = pv) tryCatch(list(ok = TRUE, r = E$map_fit_names(names, ss, panel, "lbl")),
                                             error = function(e) list(ok = FALSE, msg = conditionMessage(e)))
cases <- list(
  direct = case("1:100"), exact = case("rsE"), swapped = case("rsS"), strand_exact = case("rsT"),
  strand_swapped = case("rsU"), palindrome_exact = case("rsP"), palindrome_swapped = case("rsQ"),
  mismatch = case("rsM"), palindrome_mismatch = case("rsW"), absent = case("rsZ"), panel_duplicate = case("rsD"),
  no_position = case("rsX"), no_alleles = case("rsN"), ambiguous = case("rsA"), lowercase = case("rsL"),
  unordered_exact = case("rsE", pv_unordered), unordered_swapped = case("rsS", pv_unordered),
  many = case(c("1:100", "rsE", "rsZ", "rsM", "rsW", "rsX", "rsN", "rsA", "rsY"))
)
cat(toJSON(lapply(cases, function(x) if (x$ok) list(ok = TRUE, idx = I(x$r$idx), counts = x$r$counts) else x),
           auto_unbox = TRUE, null = "null", na = "null"))
'''


@pytest.fixture(scope="module")
def unit():
    p = subprocess.run([RSCRIPT, "-e", _R % SCRIPT], cwd=REPO_ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-3000:]
    return json.loads(p.stdout.strip().splitlines()[-1])


@pytest.mark.parametrize("case, idx, kind", [
    ("direct", 1, "n_direct"), ("exact", 2, "n_panel_exact"), ("swapped", 3, "n_panel_swapped"),
    ("strand_exact", 4, "n_panel_strand"), ("strand_swapped", 5, "n_panel_strand"),
    ("palindrome_exact", 6, "n_panel_exact"), ("palindrome_swapped", 7, "n_panel_swapped"),
    ("lowercase", 12, "n_panel_swapped"), ("unordered_exact", 2, "n_panel_exact"),
    ("unordered_swapped", 3, "n_panel_exact"),
])
def test_mapped(unit, case, idx, kind):
    c = unit[case]
    assert c["ok"], c
    assert c["idx"] == [idx] and c["counts"][kind] == 1
    assert sum(c["counts"][k] for k in ("n_direct", "n_panel_exact", "n_panel_swapped", "n_panel_strand")) == 1


@pytest.mark.parametrize("case, reason", [
    ("mismatch", "allele_mismatch"), ("palindrome_mismatch", "allele_mismatch"), ("absent", "absent"),
    ("panel_duplicate", "panel_duplicate"), ("no_position", "no_position"), ("no_alleles", "no_alleles"),
    ("ambiguous", "ambiguous"),
])
def test_unmapped(unit, case, reason):
    c = unit[case]
    assert not c["ok"], c
    assert c["msg"].startswith("UNMAPPED_FIT_NAMES: lbl: 1 of 1 fit variant names unmapped (")
    assert f"({reason}=1)" in c["msg"], c["msg"]


def test_error_message_counts_and_first_five(unit):
    c = unit["many"]
    assert not c["ok"]
    m = re.fullmatch(r"UNMAPPED_FIT_NAMES: lbl: (\d+) of (\d+) fit variant names unmapped \((.*)\); first: (.*)",
                     c["msg"])
    assert m, c["msg"]
    assert (int(m.group(1)), int(m.group(2))) == (7, 9)
    reasons = dict(kv.split("=") for kv in m.group(3).split(", "))
    assert reasons == {"absent": "2", "allele_mismatch": "2", "no_position": "1", "no_alleles": "1",
                       "ambiguous": "1"}
    assert m.group(4).split(", ") == ["rsZ", "rsM", "rsW", "rsX", "rsN"]


# --- CLI on the W0d pair fixture ----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def fits(tmp_path_factory):
    return pair_session_root(tmp_path_factory)


@pytest.mark.r4_heavy
@pytest.mark.parametrize("mode", ["susie", "A1_matched"])
def test_override_names_map_through_panel(fits, mode):
    """FIXP_OVR: B's fit names are panel rsids no sumstats column carries; they map through the panel."""
    p, d = coloc(fits, ARM, OVR, "p12_primary", mode)
    ok(p)
    nb = d["name_map_b"]
    assert nb["n_direct"] == 0 and nb["n_panel_exact"] + nb["n_panel_swapped"] + nb["n_panel_strand"] == nb["n_names"]
    assert nb["n_names"] > 0 and d["name_map_a"]["n_direct"] == d["name_map_a"]["n_names"]


@pytest.mark.r4_heavy
def test_panel_mismatch_refused(fits, tmp_path):
    root = tmp_path / "pm"
    shutil.copytree(fits, root, symlinks=True)
    cmd = commands.coloc_command(ARM, MIX, "p12_primary", "susie")
    i = cmd.index("--ld-panel")
    other = root / "data/r4/tmp/other_panel.rds"
    other.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / cmd[i + 1], other)
    cmd[i + 1] = str(other)
    p = run(cmd, root)
    assert p.returncode != 0 and "FIT_PANEL_MISMATCH" in p.stderr, p.stderr[-800:]
    js = root / paths.fit_json(ARM, MIX["trait_a"], ANC, "FIXP_MIX")
    d = json.loads(js.read_text())
    d.pop("ld_file_declared", None)
    d.pop("ld_matrix", None)
    js.write_text(json.dumps(d))
    p = run(commands.coloc_command(ARM, MIX, "p12_primary", "susie"), root)
    assert p.returncode != 0 and "FIT_PANEL_MISMATCH" in p.stderr, p.stderr[-800:]


# --- qtl_abf: bridged names through --ld-matrix ---------------------------------------------------------------
from .fixtures import qtl_group_fixture as QF  # noqa: E402

from ta_r4 import run_qtl_group_r4 as QG  # noqa: E402


@pytest.mark.r4_heavy
def test_qtl_abf_maps_bridged_names_through_panel(tmp_path_factory):
    root = QF.build(tmp_path_factory.mktemp("qtl_names") / "root")
    ssp = root / "data/processed/sumstats_harmonized/tA.EUR.tsv.bgz"
    lines = gzip.decompress(ssp.read_bytes()).decode().splitlines()
    hdr = lines[0].split("\t")
    c, p_, s = hdr.index("CHR"), hdr.index("POS"), hdr.index("SNP_ID")
    out = [lines[0]]
    for ln in lines[1:]:
        f = ln.split("\t")
        f[s] = f"{f[c]}:{f[p_]}"
        out.append("\t".join(f))
    ssp.write_bytes(gzip.compress(("\n".join(out) + "\n").encode()))
    row = {"qtl_row_id": f"{QF.REGION}__EUR__tA__eqtl__{QF.TISSUE}__{QF.FEATURES[0]}", "region_safe": QF.REGION,
           "trait": "tA", "source": "eqtl", "tissue": QF.TISSUE, "qtd": QF.QTD, "gene_id": QF.FEATURES[0],
           "molecular_trait_id": QF.FEATURES[0]}
    argv = QG.abf_command("QTL_A3", row, QF.REGION, "abf.json", 1.0, "qtl_n_cs==0")
    p = subprocess.run([QF.RSCRIPT, *argv[1:]], cwd=root, capture_output=True, text=True, env=QF.r_env())
    assert p.returncode == 0, p.stderr[-2000:]
    d = json.loads((root / "abf.json").read_text())
    nm = d["name_map"]
    assert nm["n_direct"] == 0 and nm["n_panel_exact"] == nm["n_names"] == d["n_snps"]


# --- real data: repro_routeC SH2B3_12q24 hypertension x stroke (W4a probe: 589/589 unmapped) ---------------

@pytest.mark.r4_heavy
def test_sh2b3_hypertension_stroke_maps_every_name():
    import csv
    row = next(r for r in csv.DictReader(open(REPO_ROOT / "config/ta_r4/pair_manifest.tsv"), delimiter="\t")
               if r["row_id"] == "SH2B3_12q24__EUR__hypertension_vs_stroke")
    for t in ("hypertension", "stroke"):
        if not (REPO_ROOT / paths.fit_rds("repro_routeC", t, "EUR", "SH2B3_12q24")).exists():
            pytest.skip("repro_routeC SH2B3 fits absent")
    cmd = commands.coloc_command("repro_routeC", row, "p12_primary", "susie")
    out = "data/r4/tmp/w3f/sh2b3_hypertension_vs_stroke.susie.p12_primary.json"
    cmd[cmd.index("--output") + 1] = out
    env = dict(os.environ, PATH=f"{os.path.dirname(RSCRIPT)}:{os.environ['PATH']}")
    p = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, env=env)
    assert p.returncode == 0, p.stderr[-2000:]
    d = json.loads((REPO_ROOT / out).read_text())
    print("SH2B3 name_map_a", d["name_map_a"], "name_map_b", d["name_map_b"], "method", d["method"])
    for side, n in (("name_map_a", 589), ("name_map_b", 622)):
        m = d[side]
        assert m["n_names"] == n
        assert m["n_direct"] + m["n_panel_exact"] + m["n_panel_swapped"] + m["n_panel_strand"] == n
