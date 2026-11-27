"""15.7c (F10): cross-panel purity resolves each credible-set member through the fit's own sumstats and panel
(sumstats SNP_ID, panel-rsid override, CHR:POS; make.unique `.N`) and locates its allele key in the other panel by
position + alleles (variant_match.R, shared with run_coloc_pair_r4.R::map_fit_names)."""
from __future__ import annotations

import csv
import gzip
import json
import subprocess
from pathlib import Path

import pandas as pd
import pytest

from .conftest import REPO_ROOT

RSCRIPT = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"
SCRIPT = REPO_ROOT / "src/snakemake/scripts/ta_r4/cs_cross_purity.R"
VARIANT_MATCH = REPO_ROOT / "src/snakemake/scripts/ta_r4/variant_match.R"
COLOC = "src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R"
PRE_157C_REF = "0351c6287092c12732f3720432fc808a3276139e"  # HEAD before 15.7c (map_fit_names before extraction)

BUILD = r"""
suppressPackageStartupMessages(library(jsonlite))
s <- fromJSON(commandArgs(TRUE)[1], simplifyVector = TRUE)
d <- s$dir
lbf <- matrix(0, nrow = 1, ncol = length(s$names), dimnames = list(NULL, s$names))
cs <- lapply(s$cs, as.integer)
fit <- list(lbf_variable = lbf, alpha = lbf,
            sets = list(cs = cs, purity = data.frame(min.abs.corr = rep(1, length(cs)))))
class(fit) <- "susie"
saveRDS(fit, file.path(d, "fit.rds"))
fp <- as.data.frame(s$fit_panel, stringsAsFactors = FALSE)
saveRDS(list(R = diag(nrow(fp)), variants = fp), file.path(d, "fit_panel.rds"))
op <- as.data.frame(s$other_panel, stringsAsFactors = FALSE)
R <- diag(nrow(op))
for (k in seq_along(s$r_i)) R[s$r_i[k], s$r_j[k]] <- R[s$r_j[k], s$r_i[k]] <- s$r_v[k]
saveRDS(list(R = R, variants = op), file.path(d, "other.rds"))
"""


def _cols(rows, alleles=("REF", "ALT")):
    """[(id, pos, a, b)] -> panel columns; alleles names the two allele columns."""
    return {"SNP_ID": [r[0] for r in rows], "CHR": ["1"] * len(rows), "POS": [r[1] for r in rows],
            alleles[0]: [r[2] for r in rows], alleles[1]: [r[3] for r in rows]}


def case(d, names, cs, ss, other, *flags, fit_panel=None, catalog=None, r=()):
    """Build one scenario in d and run cs_cross_purity.R. ss / catalog / fit_panel / other: [(id, pos, ref, alt)];
    catalog defaults to the sumstats keys, fit_panel to the sumstats rows. r: [(i, j, value)] of the other panel."""
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    with gzip.open(d / "ss.tsv.gz", "wt") as fh:
        fh.write("CHR\tPOS\tREF\tALT\tBETA\tSE\tSNP_ID\n")
        for i, p, a, b in ss:
            fh.write(f"1\t{p}\t{a}\t{b}\t0.1\t0.02\t{i}\n")
    with open(d / "catalog.tsv", "w") as fh:
        fh.write("CHR\tPOS\tREF\tALT\tSNP_ID\n")
        for i, p, a, b in (ss if catalog is None else catalog):
            fh.write(f"1\t{p}\t{a}\t{b}\t{i or 'rsC' + str(p)}\n")
    (d / "regions.csv").write_text("region_id,chr,start,end\nR1,1,1,100000\nR2,2,1,100000\n")
    spec = {"dir": str(d), "names": list(names), "cs": cs, "fit_panel": _cols(ss if fit_panel is None else fit_panel),
            "other_panel": _cols(other), "r_i": [x[0] for x in r], "r_j": [x[1] for x in r],
            "r_v": [x[2] for x in r]}
    b = subprocess.run([RSCRIPT, "-e", BUILD, json.dumps(spec)], capture_output=True, text=True)
    assert b.returncode == 0, b.stderr
    out = d / "out.tsv"
    if out.exists():
        out.unlink()
    p = subprocess.run([RSCRIPT, str(SCRIPT), "--fit", str(d / "fit.rds"), "--panel", str(d / "other.rds"),
                        "--output", str(out), "--fit-sumstats", str(d / "ss.tsv.gz"),
                        "--fit-catalog", str(d / "catalog.tsv"), "--region-id", "R1",
                        "--regions-csv", str(d / "regions.csv"), "--fit-panel", str(d / "fit_panel.rds"), *flags],
                       capture_output=True, text=True)
    t = None
    if p.returncode == 0:
        with open(out) as fh:
            t = {row["cs"]: row for row in csv.DictReader(fh, delimiter="\t")}
    return p, t


SS3 = [("rs1", 100, "A", "G"), ("rs2", 200, "C", "T"), ("rs3", 300, "G", "T")]
CS3 = {"L1": [1, 2, 3]}
R3 = [(1, 2, 0.5), (1, 3, 0.7), (2, 3, 0.9)]


def test_same_position_and_alleles_with_a_different_id_is_present(tmp_path):
    other = [("rsA1", 100, "A", "G"), ("rs2", 200, "C", "T"), ("rs3", 300, "G", "T")]
    p, t = case(tmp_path, ["rs1", "rs2", "rs3"], CS3, SS3, other, "--allow-absent", r=R3)
    assert p.returncode == 0, p.stderr
    assert t["L1"]["n_present"] == "3" and t["L1"]["note"] == ""
    assert float(t["L1"]["min_abs_corr"]) == pytest.approx(0.5)


def test_same_id_with_different_alleles_is_absent(tmp_path):
    other = [("rs1", 100, "A", "C"), ("rs2", 200, "C", "T"), ("rs3", 300, "G", "T")]  # A/G: not exact, swap, strand
    p, t = case(tmp_path, ["rs1", "rs2", "rs3"], CS3, SS3, other, "--allow-absent", r=R3)
    assert p.returncode == 0, p.stderr
    assert (t["L1"]["n_present"], t["L1"]["note"]) == ("2", "partial_present")
    assert float(t["L1"]["min_abs_corr"]) == pytest.approx(0.9)


def test_swapped_alleles_match_and_keep_abs_r(tmp_path):
    other = [("rs1", 100, "G", "A"), ("rs2", 200, "C", "T"), ("rs3", 300, "G", "T")]
    p, t = case(tmp_path, ["rs1", "rs2", "rs3"], CS3, SS3, other, "--allow-absent",
                r=[(1, 2, -0.4), (1, 3, 0.7), (2, 3, 0.9)])
    assert p.returncode == 0, p.stderr
    assert t["L1"]["n_present"] == "3"
    assert float(t["L1"]["min_abs_corr"]) == pytest.approx(0.4)


def test_strand_complement_of_a_non_palindromic_snv_matches(tmp_path):
    other = [("rsB", 100, "T", "C"), ("rs2", 200, "C", "T"), ("rs3", 300, "G", "T")]
    p, t = case(tmp_path, ["rs1", "rs2", "rs3"], CS3, SS3, other, "--allow-absent", r=R3)
    assert p.returncode == 0, p.stderr
    assert t["L1"]["n_present"] == "3" and float(t["L1"]["min_abs_corr"]) == pytest.approx(0.5)
    assert (t["L1"]["n_match_strand"], t["L1"]["n_match_exact"]) == ("1", "2")


def test_palindromic_snv_is_not_matched_by_complement(tmp_path):
    """A palindromic pair's strand complement is its own swap, so it is only ever matched exact / swapped; rs1 (A/T)
    against G/C at its position is absent, rs3 (A/T) against T/A is present."""
    ss = [("rs1", 100, "A", "T"), ("rs2", 200, "C", "T"), ("rs3", 300, "A", "T")]
    other = [("rsP", 100, "G", "C"), ("rs2", 200, "C", "T"), ("rs3", 300, "T", "A")]
    p, t = case(tmp_path, ["rs1", "rs2", "rs3"], CS3, ss, other, "--allow-absent", r=R3)
    assert p.returncode == 0, p.stderr
    assert (t["L1"]["n_present"], t["L1"]["note"]) == ("2", "partial_present")
    assert float(t["L1"]["min_abs_corr"]) == pytest.approx(0.9)


def test_two_candidates_at_one_position_is_ambiguous(tmp_path):
    other = [("rsX", 100, "A", "G"), ("rsY", 100, "G", "A"), ("rs2", 200, "C", "T"), ("rs3", 300, "G", "T")]
    p, _ = case(tmp_path, ["rs1", "rs2", "rs3"], CS3, SS3, other, "--allow-absent")
    assert p.returncode != 0 and "AMBIGUOUS" in p.stderr, p.stderr
    assert not (tmp_path / "out.tsv").exists()


def test_unresolved_name_is_an_error_even_with_allow_absent(tmp_path):
    other = [("rs1", 100, "A", "G"), ("rs2", 200, "C", "T"), ("rs3", 300, "G", "T")]
    p, _ = case(tmp_path, ["rs1", "rsQ", "rs3"], CS3, SS3, other, "--allow-absent")
    assert p.returncode != 0 and "UNRESOLVED" in p.stderr and "rsQ" in p.stderr, p.stderr


def test_absent_without_allow_absent_is_an_error(tmp_path):
    other = [("rs2", 200, "C", "T"), ("rs3", 300, "G", "T")]
    p, _ = case(tmp_path, ["rs1", "rs2", "rs3"], CS3, SS3, other)
    assert p.returncode != 0 and "UNMATCHED" in p.stderr, p.stderr


IDENTITY_BUILD = r"""
suppressPackageStartupMessages({library(susieR); library(jsonlite)})
d <- commandArgs(TRUE)[1]
set.seed(157)
n <- 60; blocks <- rep(1:6, each = 10)
R <- outer(seq_len(n), seq_len(n), function(i, j) ifelse(blocks[i] == blocks[j], 0.92^abs(i - j), 0))
ids <- sprintf("rs%d", 1000 + seq_len(n)); pos <- 100L * seq_len(n)
dimnames(R) <- list(ids, ids)
z <- as.vector(R %*% replace(numeric(n), c(5, 33), c(9, -7))) + rnorm(n, sd = 0.3)
names(z) <- ids
fit <- susie_rss(z = z, R = R, n = 5000, L = 5)
if (is.null(colnames(fit$lbf_variable))) colnames(fit$lbf_variable) <- ids
stopifnot(!is.null(fit$sets$cs), length(fit$sets$cs) >= 2, all(lengths(fit$sets$cs) <= 100))
saveRDS(fit, file.path(d, "fit.rds"))
v <- data.frame(SNP_ID = ids, CHR = "1", POS = pos, REF = "A", ALT = "G", stringsAsFactors = FALSE)
saveRDS(list(R = R, variants = v), file.path(d, "panel.rds"))
con <- gzfile(file.path(d, "ss.tsv.gz"), "w")
writeLines(c("CHR\tPOS\tREF\tALT\tBETA\tSE\tSNP_ID", sprintf("1\t%d\tA\tG\t%f\t1\t%s", pos, z, ids)), con); close(con)
writeLines(c("CHR\tPOS\tREF\tALT\tSNP_ID", sprintf("1\t%d\tA\tG\t%s", pos, ids)), file.path(d, "catalog.tsv"))
writeLines(c("region_id,chr,start,end", "R1,1,1,100000"), file.path(d, "regions.csv"))
cat(toJSON(lapply(fit$sets$cs, length)))
"""


def test_identical_panels_reproduce_the_fit_purity(tmp_path):
    """Must-be-identity: fit panel == other panel, sets of <= 100 members (susie subsamples larger sets) ->
    min_abs_corr equals the fit's own purity exactly."""
    b = subprocess.run([RSCRIPT, "-e", IDENTITY_BUILD, str(tmp_path)], capture_output=True, text=True)
    assert b.returncode == 0, b.stderr[-2000:]
    p = subprocess.run([RSCRIPT, str(SCRIPT), "--fit", str(tmp_path / "fit.rds"), "--panel",
                        str(tmp_path / "panel.rds"), "--output", str(tmp_path / "out.tsv"),
                        "--fit-sumstats", str(tmp_path / "ss.tsv.gz"), "--fit-catalog", str(tmp_path / "catalog.tsv"),
                        "--region-id", "R1", "--regions-csv", str(tmp_path / "regions.csv"),
                        "--fit-panel", str(tmp_path / "panel.rds")], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    t = pd.read_csv(tmp_path / "out.tsv", sep="\t")
    assert len(t) >= 2
    assert (t.n_present == t.n_cs_variants).all()
    assert t.min_abs_corr.tolist() == t.purity_fit.tolist()


# --- map_fit_names identity across the extraction ---------------------------------------------------------------

COMPARE = r'''
suppressPackageStartupMessages({library(data.table); library(jsonlite)})
a <- commandArgs(TRUE); old_path <- a[1]; new_path <- a[2]; mutate <- a[3] == "mutate"; heavy <- a[4] == "heavy"
E_old <- new.env(); sys.source(old_path, envir = E_old)
E_new <- new.env(); sys.source(new_path, envir = E_new)
stopifnot(exists("classify_alleles", envir = E_new, inherits = FALSE),
          exists("match_at_position", envir = E_new, inherits = FALSE),
          !exists("classify_alleles", envir = E_old, inherits = FALSE))
if (mutate) {
  vm <- readLines(file.path(dirname(new_path), "variant_match.R"))
  hit <- grep('return(if (basis == "REF/ALT") "swapped" else "exact")', vm, fixed = TRUE)
  stopifnot(length(hit) == 1)
  vm[hit] <- sub('"swapped" else "exact"', '"exact" else "swapped"', vm[hit], fixed = TRUE)
  eval(parse(text = vm), envir = E_new)
}
ss <- data.table(CHR = "1", POS = c(100L, 200L, 300L, 400L, 500L, 600L, 700L, 800L, 900L, 900L, 1000L, 1100L),
                 REF = c("A", "A", "C", "T", "G", "A", "T", "A", "A", "A", NA, "c"),
                 ALT = c("C", "C", "A", "G", "T", "T", "A", "G", "C", "C", NA, "a"))
ss[, SNP_ID := sprintf("1:%d", POS)]
ss[, cp := SNP_ID]; ss[, name := SNP_ID]
pv <- data.frame(SNP_ID = c("rsE", "rsS", "rsT", "rsU", "rsP", "rsQ", "rsM", "rsW", "rsD", "rsD", "rsN", "rsA",
                            "rsL", "rsX"),
                 CHR = 1L, POS = c(200L, 300L, 400L, 500L, 600L, 700L, 800L, 600L, 200L, 200L, 1000L, 900L, 1100L,
                                   1200L),
                 REF = c("A", "A", "A", "A", "A", "A", "A", "C", "A", "A", "A", "A", "A", "A"),
                 ALT = c("C", "C", "C", "C", "T", "T", "C", "G", "C", "C", "C", "C", "C", "C"),
                 stringsAsFactors = FALSE)
pv$A1 <- pv$ALT; pv$A2 <- pv$REF
pvu <- pv[, c("SNP_ID", "CHR", "POS", "A1", "A2")]
run <- function(E, names, ss, panel) tryCatch(E$map_fit_names(names, ss, panel, "lbl"),
                                              error = function(e) conditionMessage(e))
cases <- list(list(c("1:100"), pv), list(c("rsE", "rsS", "rsT", "rsU", "rsP", "rsQ", "rsL"), pv),
              list(c("rsE", "rsS"), pvu), list(c("rsM"), pv), list(c("rsW"), pv), list(c("rsZ"), pv),
              list(c("rsD"), pv), list(c("rsX"), pv), list(c("rsN"), pv), list(c("rsA"), pv),
              list(c("1:100", "rsE", "rsZ", "rsM", "rsW", "rsX", "rsN", "rsA", "rsY"), pv))
n_case <- 0L; same <- TRUE
for (k in cases) {
  n_case <- n_case + 1L
  same <- same && identical(run(E_old, k[[1]], ss, k[[2]]), run(E_new, k[[1]], ss, k[[2]]))
}
n_names <- NA_integer_
if (heavy) {
  reg <- E_old$region_row("config/ta_r4/regions_r4.csv", "SH2B3_12q24")
  pnl <- readRDS("data/r4/ld/legacy_repro/EUR/SH2B3_12q24.rds")$variants
  for (tr in c("hypertension", "stroke")) {
    ssr <- E_old$read_region(sprintf("data/processed/sumstats_harmonized/%s.EUR.tsv.bgz", tr), reg)
    nm <- colnames(readRDS(sprintf("data/r4/results/repro_routeC/fine_mapping/susie/%s.EUR.SH2B3_12q24.fit.rds",
                                   tr))$lbf_variable)
    nm <- nm[nm != "null"]
    if (tr == "hypertension") n_names <- length(nm)
    o <- run(E_old, nm, ssr, pnl); nw <- run(E_new, nm, ssr, pnl)
    stopifnot(is.list(o))
    n_case <- n_case + 1L
    same <- same && identical(o, nw)
  }
}
cat(toJSON(list(same = same, n_case = n_case, n_names = n_names), auto_unbox = TRUE), "\n")
'''


def _compare(tmp_path, mode, heavy):
    old = tmp_path / "run_coloc_pair_r4.pre157c.R"
    g = subprocess.run(["git", "show", f"{PRE_157C_REF}:{COLOC}"], cwd=REPO_ROOT, capture_output=True, text=True)
    assert g.returncode == 0, g.stderr
    old.write_text(g.stdout)
    p = subprocess.run([RSCRIPT, "-e", COMPARE, str(old), str(REPO_ROOT / COLOC), mode, heavy], cwd=REPO_ROOT,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-3000:]
    return json.loads(p.stdout.strip().splitlines()[-1])


@pytest.mark.r4_heavy
def test_map_fit_names_unchanged_after_extraction(tmp_path):
    r = _compare(tmp_path, "same", "heavy")
    assert r["n_case"] == 13 and r["n_names"] == 589
    assert r["same"] is True


def test_mutated_classification_breaks_the_extraction_identity(tmp_path):
    assert _compare(tmp_path, "same", "light")["same"] is True
    assert _compare(tmp_path, "mutate", "light")["same"] is False


# --- run_aggregation wiring ---------------------------------------------------------------------------------------

def test_run_aggregation_passes_the_fit_sumstats_and_panel(tmp_path, monkeypatch, capsys):
    from ta_r4 import estimands, paths, run_aggregation as RA
    from ta_r4.arms import ARMS

    fits = estimands.fit_frame([("A3_ukb", "asthma", "EUR", "BMI_5q13_3", {"status": "ok", "credible_sets": {}}),
                                ("A3_ukb", "bmi", "EUR", "BMI_5q13_3", {"status": "ok", "credible_sets": {}})])
    for f in fits.itertuples():
        for arm in ("A3_ukb", "A3_1kg"):
            p = tmp_path / paths.panel_path(arm, f.region_safe)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x")
        rds = tmp_path / paths.fit_rds("A3_ukb", f.trait, f.ancestry, f.region_safe)
        rds.parent.mkdir(parents=True, exist_ok=True)
        rds.write_text("x")
        cat = tmp_path / paths.catalog_path(ARMS["A3_ukb"]["route"], f.region_safe)
        (tmp_path / paths.fit_json("A3_ukb", f.trait, f.ancestry, f.region_safe)).write_text(json.dumps(
            {"variant_catalog_path": str(cat) if f.trait == "asthma" else str(cat) + ".other",
             "ld_file_declared": paths.panel_path("A3_ukb", f.region_safe)}))
    calls = []

    def runner(repo, rds, panel, allow_absent, **inputs):
        calls.append((Path(rds).name, inputs))
        return pd.DataFrame(columns=RA.PURITY_COLS[6:])

    one = fits[fits.trait == "asthma"]
    t = RA._cross_purity(tmp_path, one, runner)
    assert len(calls) == 1 and set(t.note) == {"no_cs"}  # A3_ukb -> A3_1kg only: A3_1kg has no fits here
    name, inputs = calls[0]
    assert name == "asthma.EUR.BMI_5q13_3.fit.rds"
    assert inputs == {"fit_sumstats": tmp_path / paths.sumstats_path("asthma", "EUR", "A3_ukb"),
                      "fit_catalog": tmp_path / paths.catalog_path("r4", "BMI_5q13_3"), "region_safe": "BMI_5q13_3",
                      "regions_csv": tmp_path / paths.regions_csv(),
                      "fit_panel": tmp_path / paths.panel_path("A3_ukb", "BMI_5q13_3")}
    # the bmi fit's JSON records another catalog: FINAL refuses naming the fit, DRAFT prints it and scores nothing
    with pytest.raises(RA.CrossPurityInputMismatch, match="bmi.EUR.BMI_5q13_3"):
        RA._cross_purity(tmp_path, fits, runner, final=True)
    calls.clear()
    t = RA._cross_purity(tmp_path, fits, runner, final=False)
    assert "bmi.EUR.BMI_5q13_3" in capsys.readouterr().err
    assert [c[0] for c in calls] == ["asthma.EUR.BMI_5q13_3.fit.rds"]
    assert t.set_index(["fit_arm", "trait"]).loc[("A3_ukb", "bmi"), "note"] == "fit_inputs_mismatch"
    # _rscript_purity: the Rscript argv carries every input; region id from the Snakefile safe-id rule
    seen = {}

    def fake_run(cmd, **kw):
        seen["cmd"] = cmd
        out = Path(cmd[cmd.index("--output") + 1])
        out.write_text("\t".join(RA.PURITY_COLS[6:]) + "\n")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(RA.subprocess, "run", fake_run)
    RA._rscript_purity(REPO_ROOT, "f.rds", "o.rds", True, fit_sumstats="s.bgz", fit_catalog="c.tsv",
                       region_safe="BMI_5q13_3", regions_csv=REPO_ROOT / paths.regions_csv(), fit_panel="p.rds")
    c = seen["cmd"]
    got = {k: c[c.index(k) + 1] for k in ("--fit", "--panel", "--fit-sumstats", "--fit-catalog", "--region-id",
                                          "--regions-csv", "--fit-panel")}
    assert got == {"--fit": "f.rds", "--panel": "o.rds", "--fit-sumstats": "s.bgz", "--fit-catalog": "c.tsv",
                   "--region-id": "BMI_5q13.3", "--regions-csv": str(REPO_ROOT / paths.regions_csv()),
                   "--fit-panel": "p.rds"}
    assert "--allow-absent" in c and "--allow-duplicate-rows" not in c
    # run_aggregation: a mismatch raised while building tables is exit 3, nothing written
    monkeypatch.setattr(RA.estimands, "output_status", lambda repo: "FINAL")
    monkeypatch.setattr(RA.estimands, "load_rules", lambda repo: {})
    monkeypatch.setattr(RA.estimands, "load_manifest", lambda repo: None)
    monkeypatch.setattr(RA.estimands, "load_rows", lambda repo, man: None)
    monkeypatch.setattr(RA.estimands, "load_fits", lambda repo: None)
    monkeypatch.setattr(RA, "_coverage", lambda repo, man: ("", {}))
    monkeypatch.setattr(RA, "_qtl_coverage", lambda repo: [])

    def boom(*a, **k):
        raise RA.CrossPurityInputMismatch("A3_ukb bmi.EUR.BMI_5q13_3: variant_catalog_path differs")

    monkeypatch.setattr(RA, "build_tables", boom)
    assert RA.run_aggregation(tmp_path, tmp_path / "out") == 3
    assert not (tmp_path / "out").exists()
    assert "bmi.EUR.BMI_5q13_3" in capsys.readouterr().err


# --- routes and the .N rule -----------------------------------------------------------------------------------------

def test_ukb_indel_id_resolves_through_the_sumstats(tmp_path):
    """A hypertension-style sumstats id 1:100 on an indel; the UKB fit panel calls it 1:100_A_AT (no rsid, no
    override), so the fit name is 1:100; the other panel holds an rsid indel and an SNV at that position."""
    ss = [("1:100", 100, "A", "AT"), ("rs2", 200, "C", "T")]
    fp = [("1:100_A_AT", 100, "A", "AT"), ("rs2", 200, "C", "T")]
    other = [("rs555", 100, "A", "AT"), ("rs556", 100, "A", "G"), ("rs2", 200, "C", "T")]
    p, t = case(tmp_path, ["1:100", "rs2"], {"L1": [1, 2]}, ss, other, "--allow-absent", fit_panel=fp,
                r=[(1, 3, 0.6), (2, 3, 0.2)])
    assert p.returncode == 0, p.stderr
    assert t["L1"]["n_present"] == "2" and float(t["L1"]["min_abs_corr"]) == pytest.approx(0.6)
    assert (t["L1"]["n_route_sumstats"], t["L1"]["n_route_panel"], t["L1"]["n_route_chrpos"]) == ("2", "0", "0")


def test_panel_rsid_override_name_resolves_through_the_panel(tmp_path):
    ss = [("1:100", 100, "A", "G"), ("1:200", 200, "C", "T")]
    fp = [("rs1", 100, "A", "G"), ("rs2", 200, "C", "T")]
    other = [("rsO1", 100, "A", "G"), ("rsO2", 200, "C", "T")]
    p, t = case(tmp_path, ["rs1", "rs2"], {"L1": [1, 2]}, ss, other, "--allow-absent", fit_panel=fp,
                r=[(1, 2, 0.8)])
    assert p.returncode == 0, p.stderr
    assert t["L1"]["n_present"] == "2" and float(t["L1"]["min_abs_corr"]) == pytest.approx(0.8)
    assert (t["L1"]["n_route_sumstats"], t["L1"]["n_route_panel"]) == ("0", "2")


def test_chrpos_name_resolves_to_the_unique_fit_panel_row(tmp_path):
    ss = [("", 100, "A", "G"), ("rs2", 200, "C", "T")]
    fp = [("1:100_A_G", 100, "A", "G"), ("rs2", 200, "C", "T")]
    other = [("rs1", 100, "A", "G"), ("rs2", 200, "C", "T")]
    p, t = case(tmp_path, ["1:100", "rs2"], {"L1": [1, 2]}, ss, other, fit_panel=fp, r=[(1, 2, 0.3)])
    assert p.returncode == 0, p.stderr
    assert t["L1"]["n_present"] == "2" and float(t["L1"]["min_abs_corr"]) == pytest.approx(0.3)


def test_duplicate_row_suffix_is_refused_unless_allowed(tmp_path):
    other = [("rs1", 100, "A", "G"), ("rs2", 200, "C", "T")]
    args = (["rs1", "rs1.1", "rs2"], {"L1": [1, 2, 3]}, SS3[:2], other)
    p, _ = case(tmp_path / "prod", *args, "--allow-absent", r=[(1, 2, 0.5)])
    assert p.returncode != 0 and "DUPLICATE_ROW" in p.stderr and "rs1.1" in p.stderr, p.stderr
    p, t = case(tmp_path / "pre", *args, "--allow-duplicate-rows", r=[(1, 2, 0.5)])
    assert p.returncode == 0, p.stderr
    assert t["L1"]["n_present"] == "3" and float(t["L1"]["min_abs_corr"]) == pytest.approx(0.5)


MULTI_KEY = ([("rsM", 100, "A", "G"), ("rsM", 100, "A", "C"), ("rs2", 200, "C", "T")],   # ss
             [("rsM", 100, "A", "C"), ("rsM", 100, "A", "G"), ("rs2", 200, "C", "T")],   # catalog
             [("rsM", 100, "A", "C"), ("rsMb", 100, "A", "G"), ("rs2", 200, "C", "T")],  # other panel
             [(1, 3, 0.7), (2, 3, 0.2), (1, 2, 0.9)], {"L1": [1, 3], "L2": [2, 3]})


def test_multi_key_base_is_refused_and_counted_in_production_and_chosen_by_catalog_order_only_when_allowed(tmp_path):
    """rsM names two keys (1:100 A/C, then A/G in catalog order) plus rs2: production stops with REFUSED_MULTI_KEY
    (15.8e R5); --allow-duplicate-rows maps rsM -> A/C and rsM.1 -> A/G; rsM.2 is an error."""
    ss, cat, other, r, cs = MULTI_KEY
    p, t = case(tmp_path / "prod", ["rsM", "rsM.1", "rs2"], cs, ss, other, catalog=cat, r=r)
    assert p.returncode != 0 and "REFUSED_MULTI_KEY" in p.stderr and "rsM" in p.stderr, p.stderr
    p, t = case(tmp_path / "pre", ["rsM", "rsM.1", "rs2"], cs, ss, other, "--allow-duplicate-rows", catalog=cat, r=r)
    assert p.returncode == 0, p.stderr
    assert float(t["L1"]["min_abs_corr"]) == pytest.approx(0.7) and float(t["L2"]["min_abs_corr"]) == pytest.approx(0.2)
    assert t["L1"]["n_refused_multi_key"] == "0"
    p, _ = case(tmp_path / "bad", ["rsM", "rsM.2", "rs2"], cs, ss, other, "--allow-duplicate-rows", catalog=cat, r=r)
    assert p.returncode != 0 and "BAD_OCCURRENCE" in p.stderr and "rsM.2" in p.stderr, p.stderr



def test_multi_key_member_is_fatal_with_or_without_allow_absent(tmp_path):
    ss, cat, other, r, cs = MULTI_KEY
    for sub, flags in (("strict", ()), ("allow_absent", ("--allow-absent",))):
        p, t = case(tmp_path / sub, ["rsM", "rsM.1", "rs2"], cs, ss, other, *flags, catalog=cat, r=r)
        assert p.returncode != 0 and t is None, (sub, p.stderr)
        assert "REFUSED_MULTI_KEY" in p.stderr and "rsM" in p.stderr, (sub, p.stderr)
        assert not (tmp_path / sub / "out.tsv").exists() and not (tmp_path / sub / "out.tsv.tmp").exists(), sub

SUPERSET = r'''
suppressPackageStartupMessages(library(jsonlite))
source("src/snakemake/scripts/ta_r4/variant_match.R")
regs <- sub("\\.rds$", "", list.files("data/r4/ld/EUR_1kg_r4", "\\.rds$"))
regs <- regs[file.exists(sprintf("data/r4/ld/EUR_ukb337k_r4/%s.rds", regs))]
n_old <- 0L; n_kept <- 0L; lost <- character(0)
for (g in regs) for (dir in list(c("EUR_1kg_r4", "EUR_ukb337k_r4"), c("EUR_ukb337k_r4", "EUR_1kg_r4"))) {
  a <- panel_alleles(readRDS(sprintf("data/r4/ld/%s/%s.rds", dir[1], g))$variants)
  b <- panel_alleles(readRDS(sprintf("data/r4/ld/%s/%s.rds", dir[2], g))$variants)
  bcp <- paste(b$chr, b$pos, sep = ":"); acp <- paste(a$chr, a$pos, sep = ":")
  b_miss <- missing_allele(b$ref) | missing_allele(b$alt)
  by_pos <- list2env(split(seq_along(bcp), bcp), hash = TRUE)
  # the pre-15.7c rule: the name as a panel SNP_ID (unique), else the name as CHR:POS (unique)
  by_id <- match(a$id, b$id); by_id[a$id %in% b$id[duplicated(b$id)]] <- -1L
  nm_cp <- sub("^chr", "", a$id, ignore.case = TRUE)
  by_cp <- match(nm_cp, bcp); by_cp[nm_cp %in% bcp[duplicated(bcp)]] <- -1L
  old <- ifelse(is.na(by_id), by_cp, by_id)
  for (i in which(!is.na(old) & old > 0L)) {
    j <- old[i]
    if (!setequal(c(a$ref[i], a$alt[i]), c(b$ref[j], b$alt[j]))) next  # the current match must agree on alleles
    n_old <- n_old + 1L
    rows <- get0(acp[i], envir = by_pos, inherits = FALSE)
    if (is.null(rows)) { lost <- c(lost, sprintf("%s %s->%s %s no_row_at_position", g, dir[1], dir[2], a$id[i])); next }
    m <- match_at_position(a$ref[i], a$alt[i], b$ref[rows], b$alt[rows], b_miss[rows], b$basis)
    if (identical(m$status, "matched") && rows[m$j] == j) n_kept <- n_kept + 1L
    else lost <- c(lost, sprintf("%s %s->%s %s", g, dir[1], dir[2], a$id[i]))
  }
}
cat(toJSON(list(n_regions = length(regs), n_old = n_old, n_kept = n_kept, lost = head(lost, 10)), auto_unbox = TRUE),
    "\n")
'''


@pytest.mark.r4_heavy
def test_real_panels_new_rule_is_a_superset_of_allele_agreeing_matches():
    """Committed EUR 1000G / UKB panels, both directions, read-only: every member the pre-15.7c rule matches with
    agreeing alleles is matched to the same row by position + alleles. No count is asserted."""
    if not (REPO_ROOT / "data/r4/ld/EUR_ukb337k_r4").is_dir():
        pytest.fail("committed EUR panels absent")
    p = subprocess.run([RSCRIPT, "-e", SUPERSET], cwd=REPO_ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-3000:]
    r = json.loads(p.stdout.strip().splitlines()[-1])
    print("superset", r)
    assert r["n_regions"] > 0 and r["n_old"] > 0
    assert r["n_kept"] == r["n_old"], r["lost"]
