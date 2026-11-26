"""W3f 15.7f (review F2; DEC-2026-11-20-run-susie-rss-exact-purity-unfreeze, DEC-2026-11-20-ta-r4-qtl-exact-purity-flag).

susieR 0.14.2 get_purity scores a credible set of more than n_purity = 100 members on sample(pos, 100). Under
--exact-purity true, run_susie_rss.R and run_qtl_coloc.R pass n_purity = the number of variants, so purity is the
minimum |r| over all pairs of set members and no longer depends on the RNG.

GWAS toy: build_fixture's FIX_1 inputs with a 150-variant one-factor panel (loading 0.98, variant LOW 0.6 / 0.98, so
min |r| over any set holding LOW is 0.6) and a uniform z = 4; L = 1 and min_abs_corr_default 0.9 in the toy policy, so
the single 143-member set is kept at 0.5 either way while its purity value, the 0.9 sweep row and L_saturated depend
on whether a 100-member subsample holds LOW. QTL toy: test_qtl_group_runner's fixture with a one-factor FIX_1 panel
(LOW_Q loading 0.45: min |r| 0.441) and a uniform QTL z. Seeds are set through R_PROFILE_USER.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from .conftest import REPO_ROOT, merged_config
from .fixtures import qtl_group_fixture as QF
from .test_frozen_script_armed_e2e import (ANC, FROZEN_REL, HTS_BIN, REGION, RSCRIPT, TRAIT, _ok, _write_manifest,
                                           build_fixture)

from ta_r4 import commands, paths
from ta_r4 import run_qtl_group_r4 as G
from ta_r4.arms import ARMS, CURRENT_SCRIPT

#: DIFFERENTIAL SUBSTRATE: HEAD before 15.7f (data/r4/tmp/w3f/q157/start_15_7f.txt). Never re-pin.
PRE_157F_REF = "78f627192934639a6d647409d6aa38d48218ec32"
FLAG = "--exact-purity"
ARM = "A3_1kg"
M, LOW = 150, 20
SEEDS = (1, 2, 3, 4, 5, 6, 7, 8)
QTL_SCRIPT_REL = "src/snakemake/scripts/run_qtl_coloc.R"
MANIFEST = (".planning/phases/ta-r4-head-to-head-reanalysis-and-submission/manifests/"
            "purity_flip_measurement.tsv")

TOY_R = r'''
m <- __M__L; LOW <- __LOW__L
a <- rep(0.98, m); a[LOW] <- 0.6 / 0.98
R <- tcrossprod(a); diag(R) <- 1
pos <- 1000L + 400L * (seq_len(m) - 1L)
v <- data.frame(SNP_ID = sprintf("rs%d", 8000000L + seq_len(m)), CHR = "1", POS = pos, A1 = "C", A2 = "A",
                REF = "A", ALT = "C", stringsAsFactors = FALSE)
saveRDS(list(R = R, variants = v, ld_source = "fixture_r4", region_id = "FIX_1", ancestry = "EUR"), "__PANEL__")
ss <- data.frame(CHR = "1", POS = pos, REF = "A", ALT = "C", BETA = 0.04, SE = 0.01, P = 6.3e-5, EAF = 0.3,
                 N = 10000L, SNP_ID = sprintf("1:%d", pos), TRAIT = "hypertension", ANCESTRY = "EUR", BUILD = "GRCh37")
plain <- sub("\\.bgz$", "", "__SUMSTATS__")
write.table(ss, plain, sep = "\t", quote = FALSE, row.names = FALSE)
stopifnot(system2("__BGZIP__", c("-f", "-c", plain), stdout = "__SUMSTATS__") == 0); unlink(plain)
stopifnot(system2("__TABIX__", c("-f", "-s", "1", "-b", "2", "-e", "2", "-S", "1", "__SUMSTATS__")) == 0)
write.table(ss[, c("CHR", "POS", "REF", "ALT", "SNP_ID")], "__CATALOG__", sep = "\t", quote = FALSE, row.names = FALSE)
cat("TOY_OK\n")
'''

READ_FIT_R = r'''
f <- readRDS("__RDS__"); p <- readRDS("__PANEL__")
cs <- f$sets$cs; pur <- f$sets$purity
full <- lapply(cs, function(x) { i <- match(names(f$pip)[x], p$variants$SNP_ID); A <- abs(p$R[i, i]); min(A[upper.tri(A)]) })
cat(jsonlite::toJSON(list(sets = lapply(unname(cs), function(x) I(sort(names(f$pip)[x]))),
                          purity = if (is.null(pur)) list() else as.list(pur$min.abs.corr),
                          full_min = unname(full), low_in = unname(lapply(cs, function(x) __LOW__L %in% x))),
                     auto_unbox = TRUE, digits = NA))
'''


def _renv(seed, root):
    prof = Path(root) / f"seed_{seed}.Rprofile"
    prof.write_text(f"set.seed({seed}L)\n")
    return dict(os.environ, PATH=f"{Path(RSCRIPT).parent}:{os.environ['PATH']}", R_PROFILE_USER=str(prof))


def _run(cmd, cwd, env=None):
    return subprocess.run([str(c) for c in cmd], cwd=cwd, env=env or _renv(0, cwd), capture_output=True, text=True)


def _sub(code, **kw):
    for k, v in kw.items():
        code = code.replace(f"__{k}__", str(v))
    return code


def _argv(flag):
    cfg = merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{ARM}.yaml")
    cmd = commands.fit_command(ARM, TRAIT, ANC, REGION, cfg, region_id=REGION)
    while FLAG in cmd:
        i = cmd.index(FLAG)
        del cmd[i:i + 2]
    return cmd + ([FLAG, flag] if flag is not None else [])


@pytest.fixture(scope="module")
def toy(tmp_path_factory):
    root = tmp_path_factory.mktemp("purity_toy")
    panel = build_fixture(root)
    code = _sub(TOY_R, M=M, LOW=LOW, PANEL=root / panel, SUMSTATS=root / paths.sumstats_path(TRAIT, ANC, ARM),
                CATALOG=root / paths.catalog_path(ARMS[ARM]["route"], REGION), BGZIP=f"{HTS_BIN}/bgzip",
                TABIX=f"{HTS_BIN}/tabix")
    assert "TOY_OK" in _ok(_run([RSCRIPT, "-e", code], root)).stdout
    (root / paths.panel_manifest_path(ARM, ANC)).unlink()
    _write_manifest(root, ARM, panel, REGION)
    pol = root / ARMS[ARM]["policy"]
    txt = pol.read_text()
    for old, new in (("  L: 10\n", "  L: 1\n"), ("min_abs_corr_default: 0.5", "min_abs_corr_default: 0.9")):
        assert txt.count(old) == 1, old
        txt = txt.replace(old, new)
    pol.write_text(txt)
    return {"root": root, "panel": panel, "cache": {}}


def _fit(toy, flag, seed, root=None):
    """(rc, stderr, JSON sweep/L_saturated, RDS sets/purity, md5 of JSON and RDS) for one toy fit."""
    key = (flag, seed, str(root))
    if root is None and key in toy["cache"]:
        return toy["cache"][key]
    r = root or toy["root"]
    js, rds = r / paths.fit_json(ARM, TRAIT, ANC, REGION), r / paths.fit_rds(ARM, TRAIT, ANC, REGION)
    js.unlink(missing_ok=True)
    rds.unlink(missing_ok=True)
    p = _run(_argv(flag), r, _renv(seed, r))
    out = {"rc": p.returncode, "stderr": p.stderr}
    if p.returncode == 0:
        d = json.loads(js.read_text())
        out["json"] = d
        out["sweep"] = {s["min_abs_corr"]: s["n_CS"] for s in d["min_abs_corr_sweep"]}
        out["l_saturated"] = d["L_saturated"]
        q = _ok(_run([RSCRIPT, "-e", _sub(READ_FIT_R, RDS=rds, PANEL=r / toy["panel"], LOW=LOW)], r))
        out["rds"] = json.loads(q.stdout.strip().splitlines()[-1])
        out["md5"] = (hashlib.md5(js.read_bytes()).hexdigest(), hashlib.md5(rds.read_bytes()).hexdigest())
    if root is None:
        toy["cache"][key] = out
    return out


def _ok_fit(o):
    assert o["rc"] == 0, o["stderr"][-3000:]
    return o


# ---- run_susie_rss.R -----------------------------------------------------------------------------------------------
@pytest.mark.r4_heavy
def test_default_path_unchanged_without_the_flag(toy, tmp_path):
    old_root = tmp_path / "old"
    shutil.copytree(toy["root"], old_root, symlinks=True)
    pre = subprocess.run(["git", "show", f"{PRE_157F_REF}:{FROZEN_REL}"], cwd=REPO_ROOT, capture_output=True,
                         text=True, check=True).stdout
    link = old_root / FROZEN_REL
    link.unlink()
    link.write_text(pre)
    purities = set()
    for seed in SEEDS:
        new = _ok_fit(_fit(toy, None, seed))
        old = _ok_fit(_fit(toy, None, seed, root=old_root))
        assert new["json"] == old["json"], seed
        assert new["rds"] == old["rds"] and new["md5"] == old["md5"], seed
        purities.add(new["rds"]["purity"][0])
    assert len(purities) > 1  # the differential covers both outcomes of the subsample draw


@pytest.mark.r4_heavy
def test_exact_purity_equals_the_full_pairwise_minimum(toy):
    for s in SEEDS:
        o = _ok_fit(_fit(toy, "true", s))["rds"]
        assert len(o["sets"]) == 1 and len(o["sets"][0]) > 100 and o["low_in"] == [True], s
        assert abs(o["purity"][0] - o["full_min"][0]) <= 1e-12, s
        assert abs(o["full_min"][0] - 0.6) <= 1e-9, s


@pytest.mark.r4_heavy
def test_exact_purity_is_invariant_to_the_rng_seed(toy):
    runs = [_ok_fit(_fit(toy, "true", s)) for s in SEEDS]
    first = runs[0]
    for o in runs[1:]:
        assert o["rds"] == first["rds"] and o["json"] == first["json"] and o["md5"] == first["md5"]


@pytest.mark.r4_heavy
def test_subsample_purity_depends_on_the_seed_without_the_flag(toy):
    """Negative control: without the flag the toy reaches susieR's random 100-member subsample."""
    runs = [_ok_fit(_fit(toy, None, s)) for s in SEEDS]
    assert all(len(o["rds"]["sets"]) == 1 and len(o["rds"]["sets"][0]) > 100 for o in runs)
    assert len({o["rds"]["purity"][0] for o in runs}) > 1
    assert len({o["sweep"][0.9] for o in runs}) > 1
    assert len({o["l_saturated"] for o in runs}) > 1


@pytest.mark.r4_heavy
def test_sweep_and_l_saturation_use_exact_purity(toy):
    for s in SEEDS:
        o = _ok_fit(_fit(toy, "true", s))
        assert o["sweep"] == {0.1: 1, 0.5: 1, 0.9: 0}, s
        assert o["l_saturated"] is False, s


@pytest.mark.r4_heavy
def test_bad_exact_purity_value_stops(toy):
    o = _fit(toy, "maybe", SEEDS[0])
    assert o["rc"] != 0
    assert FLAG in o["stderr"] and "true|false" in o["stderr"], o["stderr"][-2000:]


def _arm_cmd(arm, row):
    cfg = merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml")
    anc = row["ancestry"] if isinstance(row["ancestry"], str) else row["ancestry"][0]
    return commands.fit_command(arm, TRAIT, anc, REGION, cfg, region_id=REGION)


def _production(row):
    return row["script"] == CURRENT_SCRIPT and row["validator_mode"] != "legacy_any"


def test_fit_command_passes_exact_purity_for_production_arms():
    prod = [a for a, row in ARMS.items() if _production(row)]
    assert prod
    for arm in prod:
        cmd = _arm_cmd(arm, ARMS[arm])
        assert cmd.count(FLAG) == 1 and cmd[cmd.index(FLAG) + 1] == "true", arm
        assert cmd.index(FLAG) == cmd.index("--require-unique-allele-key") + 2, arm
        assert cmd.index(FLAG) + 2 == cmd.index("--variant-list"), arm


def test_repro_arms_do_not_pass_exact_purity():
    other = [a for a, row in ARMS.items() if not _production(row)]
    assert other
    for arm in other:
        assert FLAG not in _arm_cmd(arm, ARMS[arm]), arm


# ---- simulation harness ----------------------------------------------------------------------------------------------
SIM_R = r'''
suppressPackageStartupMessages(library(jsonlite))
H <- new.env(); sys.source("__HARNESS__", envir = H, chdir = FALSE)
m <- __M__L; LOW <- __LOW__L
a <- rep(0.98, m); a[LOW] <- 0.6 / 0.98
R <- tcrossprod(a); diag(R) <- 1
pol <- H$read_policy("__POLICY__")
out <- lapply(c(__SEEDS__), function(s) {
  set.seed(s)
  f <- H$fit_frozen(H$FZ, rep(4, m), R, 10000, pol, 0.95, sprintf("v%d", seq_len(m)))$fit
  x <- f$sets$cs[[1]]; A <- abs(R[x, x])
  list(size = length(x), low_in = LOW %in% x, purity = f$sets$purity$min.abs.corr[1], full_min = min(A[upper.tri(A)]))
})
cat(toJSON(out, auto_unbox = TRUE, digits = NA))
'''


@pytest.mark.r4_heavy
def test_simulation_ladder_uses_exact_purity(tmp_path):
    code = _sub(SIM_R, HARNESS=REPO_ROOT / "src/snakemake/scripts/ta_r4/simulate_coloc_r4.R", M=M, LOW=LOW,
                POLICY=REPO_ROOT / "config/susie_policy.yaml", SEEDS=",".join(map(str, SEEDS)))
    p = _ok(_run([RSCRIPT, "-e", code], REPO_ROOT, _renv(0, tmp_path)))
    out = json.loads(p.stdout.strip().splitlines()[-1])
    assert len(out) == len(SEEDS)
    for o in out:
        assert o["size"] > 100 and o["low_in"] is True
        assert abs(o["purity"] - o["full_min"]) <= 1e-12


# ---- the committed pre-fix flip measurement ------------------------------------------------------------------------
RECOUNT_R = r'''
suppressPackageStartupMessages({ library(data.table); library(jsonlite) })
source("__VM__")
d <- fromJSON("__JSON__"); f <- readRDS("__RDS__"); k <- __K__L
reg <- fread("config/ta_r4/regions_r4.csv", colClasses = "character")[region_id == d$region_id]
hdr <- strsplit(system(sprintf("gunzip -c %s | head -1", shQuote(d$sumstats)), intern = TRUE), "\t")[[1]]
w <- system2("__TABIX__", c(d$sumstats, sprintf("%s:%s-%s", reg$chr, reg$start, reg$end)), stdout = TRUE)
ss <- fread(text = paste(w, collapse = "\n"), header = FALSE, col.names = hdr, colClasses = "character", sep = "\t")
ss[, POS := as.numeric(POS)]
ss[SNP_ID == "" | SNP_ID == "NA", SNP_ID := NA_character_]
ss <- ss[CHR == reg$chr & POS >= as.numeric(reg$start) & POS <= as.numeric(reg$end)]
panel <- readRDS(d$ld_file_declared); pv <- panel$variants; R <- as.matrix(panel$R)
nm <- colnames(f$lbf_variable)
st <- susieR:::in_CS(f$alpha, coverage = 0.95)
pos <- which(st[k, ] != 0)
res <- resolve_fit_names(nm[pos], ss, fread(d$variant_catalog_path, colClasses = "character"), pv, TRUE)
stopifnot(all(res$status == "ok"))
p <- panel_alleles(pv); pk <- paste(p$chr, p$pos, p$ref, p$alt, sep = ":")
idx <- vapply(seq_len(nrow(res)), function(j) {
  h <- which(pk == paste(res$chr[j], res$pos[j], res$ref[j], res$alt[j], sep = ":"))
  if (!length(h)) h <- which(pk == paste(res$chr[j], res$pos[j], res$alt[j], res$ref[j], sep = ":"))
  stopifnot(length(h) == 1); h }, integer(1))
sc <- __SCALE__
A <- abs((R[idx, idx] + t(R[idx, idx])) / 2) * sc
ex <- min(A[upper.tri(A)])
hit <- vapply(1:1000, function(s) { set.seed(s); q <- match(sample(pos, 100), pos); B <- A[q, q]; min(B[upper.tri(B)]) >= 0.5 }, logical(1))
cat(toJSON(list(size = length(pos), exact = ex, share = sprintf("%.3f", mean(hit)),
                kept = sprintf("L%d", k) %in% names(f$sets$cs)), auto_unbox = TRUE, digits = NA))
'''


@pytest.mark.r4_heavy
def test_flip_measurement_manifest_matches_its_recount():
    rows = [r for r in csv.DictReader((ln for ln in open(REPO_ROOT / MANIFEST) if not ln.startswith("#")),
                                      delimiter="\t")]
    assert len(rows) >= 109
    for r in rows:  # every file the manifest lists must be present: fail, never skip
        for rel in (r["fit_rds"], r["fit_rds"].replace(".fit.rds", ".json"), r["panel"]):
            assert (REPO_ROOT / rel).exists(), rel
    sha = {}
    for r in rows:
        if r["panel"] not in sha:
            sha[r["panel"]] = hashlib.sha256((REPO_ROOT / r["panel"]).read_bytes()).hexdigest()
        assert sha[r["panel"]] == r["panel_sha256"], r["panel"]
    picks = [max(rows, key=lambda r: int(r["set_size"])), min(rows, key=lambda r: int(r["set_size"]))]
    for r in picks:
        code = _sub(RECOUNT_R, VM=REPO_ROOT / "src/snakemake/scripts/ta_r4/variant_match.R",
                    JSON=r["fit_rds"].replace(".fit.rds", ".json"), RDS=r["fit_rds"],
                    K=int(r["component"].lstrip("L")), TABIX=f"{HTS_BIN}/tabix", SCALE=r["r_scale"])
        p = _ok(_run([RSCRIPT, "-e", code], REPO_ROOT, _renv(0, REPO_ROOT / "data/r4/tmp")))
        o = json.loads(p.stdout.strip().splitlines()[-1])
        print(r["fit"], r["component"], o)
        assert o["size"] == int(r["set_size"])
        assert abs(o["exact"] - float(r["exact_min_abs_corr"])) <= 1e-10
        assert o["share"] == r["share_subsample_min_ge_0_5"]
        assert o["kept"] == (r["kept_in_fit"] == "TRUE")


# ---- run_qtl_coloc.R -------------------------------------------------------------------------------------------------
def _qrow(trait="tA", feature=QF.FEATURES[0]):
    return {"qtl_row_id": f"{QF.REGION}__EUR__{trait}__eqtl__{QF.TISSUE}__{feature}", "region_safe": QF.REGION,
            "trait": trait, "source": "eqtl", "tissue": QF.TISSUE, "qtd": QF.QTD, "gene_id": feature,
            "molecular_trait_id": feature}


def _qenv(seed, root):
    prof = Path(root) / f"qseed_{seed}.Rprofile"
    prof.write_text(f"set.seed({seed}L)\n")
    return dict(QF.r_env(), R_PROFILE_USER=str(prof))


def _qtl_run(root, qtl_arm, row, out, flag, seed=1, script=None):
    cmd = G.qtl_command(qtl_arm, row, out, 1.0)
    for f in (FLAG, "--json-full-precision"):  # 15.8c: the PRE_157F script has neither option
        while f in cmd:
            i = cmd.index(f)
            del cmd[i:i + 2]
    if flag is not None:
        cmd = cmd[:-2] + [FLAG, flag] + cmd[-2:]
    cmd[0] = QF.RSCRIPT
    if script is not None:
        cmd[1] = str(script)
    p = subprocess.run(cmd, cwd=root, env=_qenv(seed, root), capture_output=True, text=True)
    assert p.returncode == 0, p.stdout[-2000:] + p.stderr[-3000:]
    return json.loads((Path(root) / out).read_text())


@pytest.fixture(scope="module")
def qtl_root(tmp_path_factory):
    return QF.build(tmp_path_factory.mktemp("purity_qtl") / "root")


@pytest.mark.r4_heavy
def test_qtl_default_path_unchanged_without_the_flag(qtl_root, tmp_path):
    pre_dir = tmp_path / "pre_scripts"
    pre_dir.mkdir()
    src = REPO_ROOT / "src/snakemake/scripts"
    for f in src.iterdir():
        if f.name != "run_qtl_coloc.R":
            (pre_dir / f.name).symlink_to(f)
    pre = subprocess.run(["git", "show", f"{PRE_157F_REF}:{QTL_SCRIPT_REL}"], cwd=REPO_ROOT, capture_output=True,
                         text=True, check=True).stdout
    (pre_dir / "run_qtl_coloc.R").write_text(pre)
    statuses = set()
    for qtl_arm in ("QTL_A3", "QTL_legacy"):
        for feature in QF.FEATURES:
            row = _qrow(feature=feature)
            new = _qtl_run(qtl_root, qtl_arm, row, f"out/new_{qtl_arm}_{feature}.json", None)
            old = _qtl_run(qtl_root, qtl_arm, row, f"out/old_{qtl_arm}_{feature}.json", None,
                           script=pre_dir / "run_qtl_coloc.R")
            assert new == old, (qtl_arm, feature)
            statuses.add(new["status"])
    assert statuses == {"success", "no_qtl_cs"}


QTL_TOY_R = r'''
m <- 200L; LOW <- __LOW__L
a <- rep(0.98, m); a[LOW] <- 0.45
R <- tcrossprod(a); diag(R) <- 1
for (rel in c("__PANEL__")) { p <- readRDS(rel); stopifnot(nrow(p$R) == m); p$R <- R; saveRDS(p, rel) }
cat(sprintf("TOY_OK %.12g\n", min(R)))
'''
LOW_Q = 30


@pytest.mark.r4_heavy
def test_qtl_exact_purity_equals_the_full_pairwise_minimum(tmp_path_factory):
    root = QF.build(tmp_path_factory.mktemp("purity_qtl_toy") / "root")
    assert LOW_Q not in QF.SWAP and LOW_Q not in QF.PAL
    p = subprocess.run([QF.RSCRIPT, "-e", _sub(QTL_TOY_R, LOW=LOW_Q, PANEL=paths.panel_path("A3_1kg", QF.REGION))],
                       cwd=root, env=QF.r_env(), capture_output=True, text=True)
    assert p.returncode == 0 and "TOY_OK" in p.stdout, p.stderr
    assert abs(float(p.stdout.split()[-1]) - 0.441) <= 1e-12
    f1 = QF.FEATURES[0]
    h = root / G.harmonized_path("eqtl", QF.QTD, f1, QF.REGION)
    with gzip.open(h, "rt") as fh:
        lines = fh.read().splitlines()
    hdr = lines[0].split("\t")
    ib, ise = hdr.index("beta"), hdr.index("se")
    body = []
    for i, ln in enumerate(lines[1:], start=1):
        f = ln.split("\t")
        f[ib] = repr((-4.0 if i in QF.SWAP else 4.0) * float(f[ise]))
        body.append("\t".join(f))
    with gzip.open(h, "wt") as fh:
        fh.write("\n".join([lines[0]] + body) + "\n")
    row = _qrow(feature=f1)
    exact = [_qtl_run(root, "QTL_A3", row, f"out/x{s}.json", "true", seed=s)["n_cs_qtl"] for s in SEEDS]
    sub = [_qtl_run(root, "QTL_A3", row, f"out/s{s}.json", "false", seed=s)["n_cs_qtl"] for s in SEEDS]
    print("exact", exact, "subsample", sub)
    assert exact == [0] * len(SEEDS)  # min |r| over the set is 0.441 < 0.5 under every seed
    assert 1 in sub  # the same toy reaches the random path without the flag


def test_qtl_command_passes_exact_purity_except_legacy():
    for qtl_arm in G.QTL_ARMS:
        cmd = G.qtl_command(qtl_arm, _qrow(), "OUT", 1.0)
        if qtl_arm == "QTL_legacy":
            assert FLAG not in cmd
        else:
            assert cmd.count(FLAG) == 1 and cmd[-4:] == [FLAG, "true", "--output", "OUT"], qtl_arm
            assert cmd.index(FLAG) == cmd.index("--qtl-orient") + 2, qtl_arm
