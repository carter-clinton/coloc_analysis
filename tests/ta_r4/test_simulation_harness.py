"""E8 simulation-calibration harness (D-23, D-26): simulate_coloc_r4.R, config/ta_r4/simulation.yaml, rule r4_sim.

Generator, causal selection, window and seeds run through the harness functions (sourced, main-guarded). The
SuSiE identity runs the frozen run_susie_rss.R through ta_r4.commands.fit_command; the coloc identity runs the
run_coloc_pair_r4.R CLI on the harness's own fits. No production simulation runs here (W5c, behind the gate).
"""
from __future__ import annotations

import csv
import gzip
import itertools
import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from .conftest import REPO_ROOT

from ta_r4 import paths

RSCRIPT = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"
HARNESS = "src/snakemake/scripts/ta_r4/simulate_coloc_r4.R"
COLOC_SCRIPT = "src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R"
SIM_CFG = "config/ta_r4/simulation.yaml"
PRIORS = "config/ta_r4/coloc_priors.yaml"
POLICY = "config/susie_policy.yaml"
COLUMNS = ["region", "scenario", "gen_panel", "rep", "seed", "arm", "method", "pp_h0", "pp_h1", "pp_h2", "pp_h3",
           "pp_h4", "pp_h4_max", "n_cs_a", "n_cs_b", "causal_a", "causal_b", "r2_causal"]
METHODS = {"A1": {"A1_abf_matched"}, "A2": {"coloc_susie", "fallback_abf"}, "A3": {"coloc_susie", "fallback_abf"}}
SCENARIOS = {"H0": {"type": "H0"}, "H4": {"type": "H4"},
             "H3_r2_0.3": {"type": "H3", "r2_bin": [0.25, 0.35]},
             "H3_r2_0.6": {"type": "H3", "r2_bin": [0.55, 0.65]},
             "H3_r2_0.9": {"type": "H3", "r2_bin": [0.85, 0.95]}}


def _run(cmd, cwd=REPO_ROOT):
    return subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True)


def _ok(p):
    assert p.returncode == 0, f"rc={p.returncode}\nSTDOUT\n{p.stdout[-3000:]}\nSTDERR\n{p.stderr[-3000:]}"
    return p


def r_json(code, cwd=REPO_ROOT):
    """Runs `code` with the harness sourced into H (main-guarded); the last stdout line is JSON."""
    pre = (f'suppressPackageStartupMessages(library(jsonlite)); H <- new.env(); '
           f'sys.source("{REPO_ROOT / HARNESS}", envir = H, chdir = FALSE); ')
    p = _ok(_run([RSCRIPT, "-e", pre + code], cwd))
    return json.loads(p.stdout.strip().splitlines()[-1])


def sim_cfg():
    return yaml.safe_load(open(REPO_ROOT / SIM_CFG))


# --- config ----------------------------------------------------------------------------------------------------

def test_config_values():
    c = sim_cfg()
    assert c["scenarios"] == SCENARIOS
    assert c["gen_panels"] == {"gen_1kg": "EUR_1kg_isect_r4", "gen_ukb": "EUR_ukb337k_isect_r4"}
    assert c["fit_panel"] == "EUR_1kg_isect_r4"
    assert c["window_variants"] == 1000
    assert c["n_per_trait"] == 100000 and c["causal_z"] == 7 and c["reps"] == 200
    assert c["seed_base"] == 20261021
    assert c["p12_key"] == "p12_primary"
    assert c["locked"] is False


def test_config_regions_are_the_ten_admissible():
    with open(REPO_ROOT / "config/ta_r4/pair_manifest.tsv", newline="") as fh:
        adm = {r["region_safe"] for r in csv.DictReader(fh, delimiter="\t")
               if r["ancestry"] == "EUR" and r["admissible"] == "true" and r["row_class"] == "primary"}
    assert len(adm) == 10
    assert sim_cfg()["regions"] == sorted(adm)


# --- harness units (one R process) -----------------------------------------------------------------------------

UNIT_R = r'''
R5 <- 0.6^abs(outer(1:5, 1:5, "-"))
g <- H$psd_generator(R5)
set.seed(11); Z0 <- H$draw_z(g, rep(0, 5), 20000)
sb <- c(0, 7, 0, 0, 0)
set.seed(12); Z1 <- H$draw_z(g, sb, 20000)
set.seed(13); a <- H$draw_z(g, sb); set.seed(13); b <- H$draw_z(g, sb); set.seed(14); d <- H$draw_z(g, sb)
Rn <- R5; Rn[1, 5] <- Rn[5, 1] <- -0.9
gn <- H$psd_generator(Rn)
e <- eigen(Rn, symmetric = TRUE)
clip <- e$vectors %*% diag(pmax(e$values, 0)) %*% t(e$vectors)
Rf <- 0.97^abs(outer(1:80, 1:80, "-"))
pairs <- H$qualifying_pairs(Rf, c(0.55, 0.65))
ch <- lapply(1:25, function(s) { set.seed(s); H$choose_causal("H3", 80, pairs) })
r2 <- sapply(ch, function(x) Rf[x$a, x$b]^2)
h4 <- lapply(1:5, function(s) { set.seed(s); H$choose_causal("H4", 80, pairs) })
cfg <- yaml::read_yaml("config/ta_r4/simulation.yaml")
si <- function(...) H$stable_index(cfg, ...)
cat(toJSON(list(
  cov_dev = max(abs(cov(t(Z0)) - R5)), mean0_dev = max(abs(rowMeans(Z0))),
  mean1_dev = max(abs(rowMeans(Z1) - as.vector(R5 %*% sb))),
  same_seed = identical(a, b), diff_seed = !identical(a, d), z_len = length(a),
  clip_min_eig = min(eigen(gn$R, symmetric = TRUE, only.values = TRUE)$values), clip_dev = max(abs(gn$R - clip)),
  raw_min_eig = min(e$values),
  n_pairs = nrow(pairs), r2 = r2, h3_distinct = all(sapply(ch, function(x) x$a != x$b)),
  h4_same = all(sapply(h4, function(x) x$a == x$b)),
  h0 = { set.seed(1); x <- H$choose_causal("H0", 80, pairs); is.na(x$a) && is.na(x$b) },
  none = nrow(H$qualifying_pairs(diag(80), c(0.55, 0.65))),
  win_1500 = range(H$window_idx(1500, 1000)), win_1001 = range(H$window_idx(1001, 1000)),
  win_600 = range(H$window_idx(600, 1000)), win_len = length(H$window_idx(1500, 1000)),
  idx = list(si("9p21_CDKN2A", "H0", "gen_1kg", 1), si("SH2B3_12q24", "H4", "gen_ukb", 7),
             si("SLC2A9_urate", "H4", "gen_ukb", 200)),
  idx_err = inherits(try(si("SH2B3_12q24", "H4", "gen_ukb", 201), silent = TRUE), "try-error"),
  coloc_core = exists("coloc_pair_core", envir = H$CP, inherits = FALSE),
  coloc_main_not_run = !exists("opt", envir = H$CP, inherits = FALSE),
  frozen = sort(ls(H$FZ, all.names = TRUE))
), auto_unbox = TRUE, digits = NA))
'''


@pytest.fixture(scope="module")
def unit():
    return r_json(UNIT_R)


def test_generator_null_moments(unit):
    print("cov_dev", unit["cov_dev"], "mean0_dev", unit["mean0_dev"])
    assert unit["cov_dev"] <= 0.03 and unit["mean0_dev"] <= 0.03


def test_generator_mean_is_R_sqrt_n_b(unit):
    print("mean1_dev", unit["mean1_dev"])
    assert unit["mean1_dev"] <= 0.05


def test_generator_deterministic(unit):
    assert unit["same_seed"] is True and unit["diff_seed"] is True and unit["z_len"] == 5


def test_generator_psd_clip(unit):
    assert unit["raw_min_eig"] < -0.05
    assert unit["clip_min_eig"] >= -1e-10 and unit["clip_dev"] <= 1e-10


def test_h3_causal_pair_in_bin(unit):
    assert unit["n_pairs"] > 0 and unit["h3_distinct"] is True
    assert all(0.55 <= r <= 0.65 for r in unit["r2"]), unit["r2"]
    assert unit["h4_same"] is True and unit["h0"] is True
    assert unit["none"] == 0


def test_window_centred_on_midpoint(unit):
    assert unit["win_1500"] == [251, 1250] and unit["win_len"] == 1000
    assert unit["win_1001"] == [1, 1000]
    assert unit["win_600"] == [1, 600]


def test_seed_is_stable_index_in_sorted_cartesian_list(unit):
    c = sim_cfg()
    keys = list(itertools.product(sorted(c["regions"]), sorted(c["scenarios"]), sorted(c["gen_panels"]),
                                  range(1, c["reps"] + 1)))
    pos = {k: i + 1 for i, k in enumerate(keys)}
    assert len(pos) == 10 * 5 * 2 * 200
    want = [pos[("9p21_CDKN2A", "H0", "gen_1kg", 1)], pos[("SH2B3_12q24", "H4", "gen_ukb", 7)],
            pos[("SLC2A9_urate", "H4", "gen_ukb", 200)]]
    assert unit["idx"] == want and want[0] == 1 and want[2] == 20000
    assert unit["idx_err"] is True


def test_coloc_core_is_sourced_main_guarded(unit):
    assert unit["coloc_core"] is True and unit["coloc_main_not_run"] is True


def test_frozen_functions_parsed_from_frozen_file(unit):
    assert unit["frozen"] == sorted(["%||%", "regularize_ld", "run_susie_with_ladder"])


# --- SuSiE identity vs the frozen script (r4_heavy) ------------------------------------------------------------

IDENTITY_R = r'''
p <- readRDS("{panel}")
p$variants$REF <- "A"; p$variants$ALT <- "C"; p$variants$A2 <- "A"; p$variants$A1 <- "C"
saveRDS(p, "{panel}")
n <- 100000
g <- H$psd_generator(p$R)
sb <- rep(0, nrow(p$R)); sb[c(5, 45)] <- c(7, 5)
set.seed(20261103); z <- H$draw_z(g, sb)
v <- p$variants
ss <- data.frame(CHR = v$CHR, POS = v$POS, REF = v$REF, ALT = v$ALT, BETA = sprintf("%.17g", z / sqrt(n)),
                 SE = sprintf("%.17g", 1 / sqrt(n)), P = 0.5, EAF = 0.3, N = n, SNP_ID = paste(v$CHR, v$POS, sep = ":"),
                 TRAIT = "hypertension", ANCESTRY = "EUR", BUILD = "GRCh37")
plain <- sub("\\.bgz$", "", "{sumstats}")
write.table(ss, plain, sep = "\t", quote = FALSE, row.names = FALSE)
stopifnot(system2("{bgzip}", c("-f", "-c", plain), stdout = "{sumstats}") == 0); unlink(plain)
stopifnot(system2("{tabix}", c("-f", "-s", "1", "-b", "2", "-e", "2", "-S", "1", "{sumstats}")) == 0)
write.table(ss[, c("CHR", "POS", "REF", "ALT", "SNP_ID")], "{catalog}", sep = "\t", quote = FALSE, row.names = FALSE)
pol <- H$read_policy("{policy}")
keys <- paste(v$CHR, v$POS, sep = ":")
zz <- as.numeric(ss$BETA) / as.numeric(ss$SE)
a3 <- H$fit_frozen(H$FZ, zz, p$R, n, pol, 0.95, keys)
a2 <- H$fit_frozen(H$FZ, zz, diag(nrow(p$R)), n, pol, 0.95, keys)
cs <- function(f) lapply(unname(f$sets$cs), function(x) I(sort(names(x))))
cat(toJSON(list(A3_1kg = list(pip = as.list(a3$fit$pip), cs = cs(a3$fit), status = a3$status),
                A2_identity = list(pip = as.list(a2$fit$pip), cs = cs(a2$fit), status = a2$status)),
           auto_unbox = TRUE, digits = NA))
'''


def _frozen_pips(root, arm, panel_rel):
    from .test_frozen_script_armed_e2e import ANC, REGION, TRAIT
    rds = root / paths.fit_rds(arm, TRAIT, ANC, REGION)
    p = _ok(_run([RSCRIPT, "-e",
                  f'f <- readRDS("{rds}"); v <- readRDS("{root / panel_rel}")$variants; '
                  'k <- setNames(paste(v$CHR, v$POS, sep = ":"), v$SNP_ID); '
                  'cs <- lapply(unname(f$sets$cs), function(x) I(sort(unname(k[names(x)])))); '
                  'cat(jsonlite::toJSON(list(pip = as.list(setNames(f$pip, k[names(f$pip)])), cs = cs), '
                  'auto_unbox = TRUE, digits = NA))'], root))
    return json.loads(p.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def identity(tmp_path_factory):
    from .test_frozen_script_armed_e2e import (ANC, HTS_BIN, PAYLOAD, REGION, TRAIT, _write_manifest, build_fixture,
                                               fit_arm)
    root = tmp_path_factory.mktemp("sim_identity")
    a3 = build_fixture(root)
    harness = r_json(IDENTITY_R.format(panel=root / a3, sumstats=root / paths.sumstats_path(TRAIT, ANC, "A3_1kg"),
                                       catalog=root / paths.catalog_path("r4", REGION), policy=REPO_ROOT / POLICY,
                                       bgzip=f"{HTS_BIN}/bgzip", tabix=f"{HTS_BIN}/tabix"))
    (root / paths.panel_manifest_path("A3_1kg", ANC)).unlink()
    _write_manifest(root, "A3_1kg", a3, REGION)
    a2 = paths.panel_path("A2_identity", REGION, ANC)
    _ok(_run([RSCRIPT, PAYLOAD, "--in", root / a3, "--out", root / a2], root))
    _write_manifest(root, "A2_identity", a2, REGION)
    frozen = {}
    for arm, panel in (("A3_1kg", a3), ("A2_identity", a2)):
        r = fit_arm(root, arm)
        _ok(r["fit"])
        assert r["json"]["status"] == "ok" and r["json"]["ld_matrix"] == panel
        frozen[arm] = _frozen_pips(root, arm, a3)
    return {"harness": harness, "frozen": frozen}


@pytest.mark.r4_heavy
@pytest.mark.parametrize("arm", ["A2_identity", "A3_1kg"])
def test_susie_identity_vs_frozen_script(identity, arm):
    h, f = identity["harness"][arm], identity["frozen"][arm]
    assert set(h["pip"]) == set(f["pip"]) and len(f["pip"]) == 60
    worst = max(abs(h["pip"][k] - f["pip"][k]) for k in f["pip"])
    print(f"{arm}: max|dPIP| {worst!r} n_cs harness {len(h['cs'])} frozen {len(f['cs'])} status {h['status']}")
    assert worst <= 1e-10
    assert h["cs"] == f["cs"] and len(f["cs"]) >= 1


# --- harness runs on fixture panels (r4_heavy) -----------------------------------------------------------------

FIXTURE_PANELS_R = r'''
m <- 120L
R1 <- 0.985^abs(outer(seq_len(m), seq_len(m), "-")); R2 <- 0.98 * R1 + 0.02 * diag(m)
v <- data.frame(SNP_ID = sprintf("rs%d", 100 + seq_len(m)), CHR = "12", POS = 5000L + 10L * seq_len(m),
                A1 = "C", A2 = "A", REF = "A", ALT = "C", stringsAsFactors = FALSE)
for (d in c("{fit}", "{ukb}")) dir.create(d, recursive = TRUE, showWarnings = FALSE)
saveRDS(list(R = R1, variants = v, ld_source = "fixture"), file.path("{fit}", "SH2B3_12q24.rds"))
saveRDS(list(R = R2, variants = v, ld_source = "fixture"), file.path("{ukb}", "SH2B3_12q24.rds"))
saveRDS(list(R = diag(m), variants = v, ld_source = "fixture"), file.path("{fit}", "FTO_16q12.rds"))
saveRDS(list(R = diag(m), variants = v, ld_source = "fixture"), file.path("{ukb}", "FTO_16q12.rds"))
cat("{{}}\n")
'''


def _harness(root, region, scenario, gen, out, reps=2):
    ld = root / "ld"
    cmd = [RSCRIPT, REPO_ROOT / HARNESS, "--fit-panel", ld / f"EUR_1kg_isect_r4/{region}.rds",
           "--gen-panel", ld / (("EUR_1kg_isect_r4" if gen == "gen_1kg" else "EUR_ukb337k_isect_r4") + f"/{region}.rds"),
           "--gen", gen, "--scenario", scenario, "--region", region, "--config", SIM_CFG, "--priors", PRIORS,
           "--policy", POLICY, "--credible-set", "0.95", "--out", out]
    if reps is not None:
        cmd += ["--reps-override", str(reps)]
    return _run(cmd)


def _read_tsv(path):
    lines = Path(path).read_text().splitlines()
    head = [ln for ln in lines if ln.startswith("#")]
    body = [ln for ln in lines if not ln.startswith("#")]
    rows = list(csv.DictReader(body, delimiter="\t"))
    return head, body[0].split("\t") if body else [], rows


@pytest.fixture(scope="module")
def fx_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("sim_fx")
    r_json(FIXTURE_PANELS_R.format(fit=root / "ld/EUR_1kg_isect_r4", ukb=root / "ld/EUR_ukb337k_isect_r4"))
    return root


@pytest.fixture(scope="module")
def fx_runs(fx_root):
    out = {}
    for tag, sc, gen in (("h4", "H4", "gen_ukb"), ("h4b", "H4", "gen_ukb"), ("h3", "H3_r2_0.6", "gen_1kg")):
        o = fx_root / f"{tag}.tsv"
        _ok(_harness(fx_root, "SH2B3_12q24", sc, gen, o))
        out[tag] = o
    return out


@pytest.mark.r4_heavy
def test_output_columns_and_rows(fx_runs):
    head, cols, rows = _read_tsv(fx_runs["h4"])
    assert cols == COLUMNS
    assert "# reps_override=2" in head
    assert len(rows) == 2 * 3
    assert [(r["rep"], r["arm"]) for r in rows] == [(str(k), a) for k in (1, 2) for a in ("A1", "A2", "A3")]
    for r in rows:
        assert r["method"] in METHODS[r["arm"]], r
        assert (r["region"], r["scenario"], r["gen_panel"]) == ("SH2B3_12q24", "H4", "gen_ukb")
        assert r["causal_a"] == r["causal_b"] != "" and float(r["r2_causal"]) == pytest.approx(1.0)
        assert abs(sum(float(r[f"pp_h{h}"]) for h in range(5)) - 1) < 1e-9
    a1 = [r for r in rows if r["arm"] == "A1"]
    assert all(r["n_cs_a"] in ("", "NA") for r in a1)


@pytest.mark.r4_heavy
def test_output_seeds_and_determinism(fx_runs):
    _, _, rows = _read_tsv(fx_runs["h4"])
    c = sim_cfg()
    keys = list(itertools.product(sorted(c["regions"]), sorted(c["scenarios"]), sorted(c["gen_panels"]),
                                  range(1, c["reps"] + 1)))
    want = {k[3]: c["seed_base"] + i + 1 for i, k in enumerate(keys) if k[:3] == ("SH2B3_12q24", "H4", "gen_ukb")}
    assert {int(r["rep"]): int(r["seed"]) for r in rows} == {1: want[1], 2: want[2]}
    assert fx_runs["h4"].read_bytes() == fx_runs["h4b"].read_bytes()


@pytest.mark.r4_heavy
def test_h3_output_pairs_in_bin(fx_runs):
    head, _, rows = _read_tsv(fx_runs["h3"])
    assert rows and all(0.55 <= float(r["r2_causal"]) <= 0.65 for r in rows)
    assert all(r["causal_a"] != r["causal_b"] for r in rows)


@pytest.mark.r4_heavy
def test_no_qualifying_pair_writes_zero_reps(fx_root):
    o = fx_root / "none.tsv"
    _ok(_harness(fx_root, "FTO_16q12", "H3_r2_0.6", "gen_1kg", o))
    head, cols, rows = _read_tsv(o)
    assert "# status=no_qualifying_pair" in head and cols == COLUMNS and rows == []


@pytest.mark.r4_heavy
def test_panel_label_mismatch_refused(fx_root, tmp_path):
    ld = fx_root / "ld"
    p = _run([RSCRIPT, REPO_ROOT / HARNESS, "--fit-panel", ld / "EUR_ukb337k_isect_r4/SH2B3_12q24.rds",
              "--gen-panel", ld / "EUR_ukb337k_isect_r4/SH2B3_12q24.rds", "--gen", "gen_ukb", "--scenario", "H4",
              "--region", "SH2B3_12q24", "--config", SIM_CFG, "--priors", PRIORS, "--policy", POLICY,
              "--credible-set", "0.95", "--out", tmp_path / "x.tsv", "--reps-override", "1"])
    assert p.returncode != 0 and "PANEL" in p.stderr
    assert not (tmp_path / "x.tsv").exists()


# --- coloc identity: harness rows == run_coloc_pair_r4.R CLI on the harness's fits (r4_heavy) -------------------

COLOC_ID_R = r'''
ctx <- H$make_context(fit_panel = "{fit}", gen_panel = "{ukb}", gen = "gen_ukb", scenario = "H4",
                      region = "SH2B3_12q24", config = "config/ta_r4/simulation.yaml",
                      priors = "config/ta_r4/coloc_priors.yaml", policy = "config/susie_policy.yaml", coverage = 0.95)
res <- H$run_rep(ctx, 3L)
d <- "{out}"; dir.create(d, recursive = TRUE, showWarnings = FALSE)
v <- ctx$variants
for (t in c("a", "b")) {{
  ss <- data.frame(CHR = v$CHR, POS = v$POS, SNP_ID = ctx$keys, BETA = sprintf("%.17g", res$z[[t]] / sqrt(ctx$n)),
                   SE = sprintf("%.17g", 1 / sqrt(ctx$n)))
  con <- gzfile(file.path(d, paste0("ss_", t, ".tsv.gz")), "w")
  write.table(ss, con, sep = "\t", quote = FALSE, row.names = FALSE); close(con)
  for (arm in c("A2", "A3")) {{
    saveRDS(res$fits[[arm]][[t]]$fit, file.path(d, sprintf("%s_%s.fit.rds", arm, t)))
    write(toJSON(list(ld_file_declared = "{fit}"), auto_unbox = TRUE), file.path(d, sprintf("%s_%s.json", arm, t)))
  }}
}}
write.table(data.frame(trait = c("sima", "simb"), ancestry = "EUR", type = "quant", sdY = 1, N_median = ctx$n),
            file.path(d, "traits.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
write.csv(data.frame(region_id = "SH2B3_12q24", ancestry = "EUR", chr = "12", start = 0, end = 1e9),
          file.path(d, "regions.csv"), row.names = FALSE)
r <- res$rows
cat(toJSON(lapply(split(r, r$arm), function(x) as.list(x)), auto_unbox = TRUE, digits = NA))
'''


@pytest.mark.r4_heavy
def test_coloc_identity_harness_vs_cli(fx_root, tmp_path):
    d = tmp_path / "cli"
    fit_panel = fx_root / "ld/EUR_1kg_isect_r4/SH2B3_12q24.rds"
    rows = r_json(COLOC_ID_R.format(fit=fit_panel, ukb=fx_root / "ld/EUR_ukb337k_isect_r4/SH2B3_12q24.rds", out=d))
    worst = 0.0
    for arm, mode, fits in (("A1", "A1_matched", "A3"), ("A2", "susie", "A2"), ("A3", "susie", "A3")):
        out = d / f"{arm}.json"
        _ok(_run([RSCRIPT, REPO_ROOT / COLOC_SCRIPT, "--mode", mode, "--fit-a", d / f"{fits}_a.fit.rds",
                  "--fit-b", d / f"{fits}_b.fit.rds", "--ld-panel", fit_panel, "--sumstats-a", d / "ss_a.tsv.gz", "--sumstats-b",
                  d / "ss_b.tsv.gz", "--trait-a", "sima", "--trait-b", "simb", "--ancestry", "EUR",
                  "--region-id", "SH2B3_12q24", "--regions-csv", d / "regions.csv", "--trait-manifest",
                  d / "traits.tsv", "--priors", PRIORS, "--p12-key", "p12_primary", "--row-id", "SIM",
                  "--arm", arm, "--output", out]))
        cli = json.loads(out.read_text())
        h = rows[arm]
        assert h["method"] == cli["method"], arm
        for k in ("pp_h0", "pp_h1", "pp_h2", "pp_h3", "pp_h4", "pp_h4_max"):
            worst = max(worst, abs(h[k] - cli[k]))
        if arm != "A1":
            assert (h["n_cs_a"], h["n_cs_b"]) == (cli["n_cs_a"], cli["n_cs_b"])
    print("coloc identity max|dPP|", worst)
    assert worst <= 1e-12


# --- the rule: production-gated, 100 jobs, no --reps-override (r4_heavy) -----------------------------------------

def _fx_repo(tmp_path, lock):
    from .fixtures.make_fixture_repo import git, make_fixture_repo, write_fixture_lock
    repo = make_fixture_repo(tmp_path)
    for rel in ("src/snakemake/scripts/ta_r4", POLICY):
        src, dst = REPO_ROOT / rel, repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        (shutil.copytree if src.is_dir() else shutil.copy2)(src, dst)
    git(repo, "add", "src/snakemake/scripts/ta_r4", POLICY)
    git(repo, "commit", "-q", "-m", "fixture scripts")
    if lock:
        write_fixture_lock(repo)
    c = sim_cfg()
    for reg in c["regions"]:
        for panel in {c["fit_panel"], *c["gen_panels"].values()}:
            f = repo / f"data/r4/ld/{panel}/{reg}.rds"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.touch()
    return repo


def _dry(repo, *targets):
    from .test_lock_gate import SMK
    cfg = ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_A3_1kg.yaml"]
    r = subprocess.run([SMK, *targets, "-s", str(repo / "Snakefile.ta_r4"), "-d", str(repo), "-n", "-p",
                        "--configfile", *cfg], cwd=repo, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


@pytest.mark.r4_heavy
def test_sim_rule_refused_without_lock(tmp_path):
    repo = _fx_repo(tmp_path, lock=False)
    rc, out = _dry(repo, "data/r4/results/sim/SH2B3_12q24.H4.gen_1kg.tsv")
    assert rc != 0 and "LockGateError" in out and "lock record absent" in out, out[-2000:]


@pytest.mark.r4_heavy
def test_sim_rule_100_jobs_with_lock_and_no_reps_override(tmp_path):
    repo = _fx_repo(tmp_path, lock=True)
    rc, out = _dry(repo, "r4_sim_all")
    assert rc == 0, out[-3000:]
    jobs = [ln for ln in out.splitlines() if ln.strip().startswith("rule r4_sim:")]
    assert len(jobs) == 100
    shells = [ln for ln in out.splitlines() if ln.strip().startswith("Rscript ")]
    assert len(shells) == 100 and not any("--reps-override" in s for s in shells)
    want = {f"data/r4/results/sim/{g}.{s}.{n}.tsv" for g in sim_cfg()["regions"] for s in SCENARIOS
            for n in ("gen_1kg", "gen_ukb")}
    assert all(any(f"--out {w}" in s for s in shells) for w in want)
