"""D-06 unit 3: run_qtl_coloc.R --qtl-orient (default false). QTL betas are signed on the QTL's own variant_id
ALT; under --qtl-orient true they are re-signed to the bound panel row's ALT (exact +1, transposed -1,
palindromic / mismatch / unparseable dropped and counted). Flag off: parsed JSON equal to the pre-change script."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "src/snakemake/scripts/run_qtl_coloc.R"
ORIENT_R = REPO / "src/snakemake/scripts/qtl_orient.R"
PRE_CHANGE_BLOB = "3ec59663cf7b9ea93e2eef87903ede9d016c0cd4"  # run_qtl_coloc.R at 9eb162d8 (before W1)
RSCRIPT = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"
COUNTERS = ("exact", "flipped", "dropped_palindromic", "dropped_mismatch", "dropped_unparseable")

# 200-variant region; panel A/G everywhere. QTL variant_id classes by index (1-based):
SWAP = list(range(2, 201, 4))           # QTL G/A (transposed), beta written negated
PAL = [7, 57, 107, 157]                 # QTL A/T
MIS = [13, 63, 113, 163]                # QTL C/T
UNP = [19, 69, 119, 169]                # QTL alt "<INS>" (unparseable)
CAT_SWAP = list(range(3, 201, 5))       # catalog transposed vs panel: join$orient = -1 there (not the QTL's)

_BUILDER = r'''
suppressPackageStartupMessages({library(coloc); library(susieR); library(data.table)})
set.seed(20261021)
OUT <- "__OUT__"; TRANSPOSE <- __TRANSPOSE__; PANEL_ALLELES <- __PANEL_ALLELES__
SWAP <- c(__SWAP__); PAL <- c(__PAL__); MIS <- c(__MIS__); UNP <- c(__UNP__); CAT_SWAP <- c(__CAT_SWAP__)
dir.create(OUT, recursive = TRUE, showWarnings = FALSE)
n <- 200L; chrom <- "12"; pos <- 110000000L + seq_len(n) * 500L
fit_names <- sprintf("rs%d", 900000L + seq_len(n))
pan <- data.frame(CHR = chrom, POS = pos, REF = "A", ALT = "G", SNP_ID = fit_names, stringsAsFactors = FALSE)
if (!PANEL_ALLELES) pan$REF <- pan$ALT <- NULL
d <- abs(outer(seq_len(n), seq_len(n), "-")); Rd <- 0.85 ^ d; diag(Rd) <- 1
Rb <- Rd; dimnames(Rb) <- NULL
saveRDS(list(R = Rb, variants = pan, use_identity = FALSE, status = "ok"), file.path(OUT, "ld.rds"))
cat_ref <- rep("A", n); cat_alt <- rep("G", n); cat_ref[CAT_SWAP] <- "G"; cat_alt[CAT_SWAP] <- "A"
fwrite(data.frame(CHR = chrom, POS = pos, REF = cat_ref, ALT = cat_alt, SNP_ID = fit_names),
       file.path(OUT, "variants.tsv"), sep = "\t")
Rfit <- Rd; dimnames(Rfit) <- list(fit_names, fit_names)
z <- rep(0, n); z[100L] <- 6.5; z <- as.vector(Rfit %*% z) + rnorm(n, sd = 0.05)
se <- rep(0.02, n)
fit <- coloc::runsusie(list(beta = z * se, varbeta = se^2, snp = fit_names, position = pos, type = "quant",
                            N = 50000L, sdY = 1, MAF = rep(0.25, n), LD = Rfit), suffix = 1)
saveRDS(fit, file.path(OUT, "gwas.fit.rds"))
zq <- rep(0, n); zq[100L] <- 5.5; zq <- as.vector(Rfit %*% zq) + rnorm(n, sd = 0.05)
sq <- rep(0.03, n); beta <- zq * sq
q_ref <- rep("A", n); q_alt <- rep("G", n)
if (TRANSPOSE) { q_ref[SWAP] <- "G"; q_alt[SWAP] <- "A"; beta[SWAP] <- -beta[SWAP] }
q_alt[PAL] <- "T"; q_ref[MIS] <- "C"; q_alt[MIS] <- "T"; q_alt[UNP] <- "<INS>"
fwrite(data.table(variant_id = sprintf("chr%s_%d_%s_%s", chrom, pos, q_ref, q_alt), rsid = fit_names,
                  beta = beta, se = sq, maf = rep(0.25, n), position = pos), file.path(OUT, "qtl.tsv"), sep = "\t")
cat("FIXTURE_OK\n")
'''


def _build(out, transpose=True, panel_alleles=True):
    code = _BUILDER
    for k, v in {"__OUT__": str(out), "__TRANSPOSE__": "TRUE" if transpose else "FALSE",
                 "__PANEL_ALLELES__": "TRUE" if panel_alleles else "FALSE",
                 "__SWAP__": ",".join(map(str, SWAP)), "__PAL__": ",".join(map(str, PAL)),
                 "__MIS__": ",".join(map(str, MIS)), "__UNP__": ",".join(map(str, UNP)),
                 "__CAT_SWAP__": ",".join(map(str, CAT_SWAP))}.items():
        code = code.replace(k, v)
    out.mkdir(parents=True, exist_ok=True)
    (out / "build.R").write_text(code)
    r = subprocess.run([RSCRIPT, str(out / "build.R")], capture_output=True, text=True)
    assert r.returncode == 0 and "FIXTURE_OK" in r.stdout, r.stdout + r.stderr
    return out


def _run(fx, out, script=SCRIPT, allele_join="true", orient=None):
    cmd = [RSCRIPT, str(script), "--gwas-fit", str(fx / "gwas.fit.rds"), "--qtl-sumstats", str(fx / "qtl.tsv"),
           "--ld-matrix", str(fx / "ld.rds"), "--qtl-source", "gtex_eqtl", "--tissue", "Whole_Blood",
           "--gene-id", "ENSG00000111252", "--region", "FIX_1", "--ancestry", "EUR", "--sdy", "1.0",
           "--sample-size", "670", "--policy", "config/susie_policy.yaml", "--output", str(out)]
    if allele_join is not None:
        cmd += ["--ld-allele-join", allele_join, "--variant-list", str(fx / "variants.tsv")]
    if orient is not None:
        cmd += ["--qtl-orient", orient]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)


def _json(r, out):
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(Path(out).read_text())


@pytest.fixture(scope="module")
def fx_t(tmp_path_factory):
    return _build(tmp_path_factory.mktemp("qtl_transposed"), transpose=True)


@pytest.fixture(scope="module")
def fx_e(tmp_path_factory):
    return _build(tmp_path_factory.mktemp("qtl_exact"), transpose=False)


@pytest.fixture(scope="module")
def old_script(tmp_path_factory):
    p = tmp_path_factory.mktemp("pre") / "run_qtl_coloc.pre_W1.R"
    p.write_text(subprocess.run(["git", "cat-file", "blob", PRE_CHANGE_BLOB], cwd=REPO, capture_output=True,
                                text=True, check=True).stdout)
    # the pre-change script sources ld_allele_join.R script-relatively
    (p.parent / "ld_allele_join.R").write_text((REPO / "src/snakemake/scripts/ld_allele_join.R").read_text())
    return p


# ---- unit: the orientation function on a 4-variant panel -------------------------------------------------
def test_orient_vector_unit():
    code = f'''
source("{ORIENT_R}")
r <- qtl_orient_vector(
  c("chr1_100_A_G", "chr1_200_T_C", "chr1_300_A_T", "chr1_400_A_C", "chr1_500_A_<DEL>", "1:600:A:G", "chr1_700_g_a"),
  c("A", "C", "A", "A", "A", "A", "a"),
  c("G", "T", "T", "G", "G", "G", "g"))
cat(paste(ifelse(is.na(r$orient), "NA", r$orient), collapse = ","), "\\n")
cat(paste(names(r$counts), unlist(r$counts), sep = "=", collapse = ","), "\\n")
'''
    r = subprocess.run([RSCRIPT, "-e", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    orient, counts = r.stdout.strip().split("\n")
    # exact, transposed, palindromic, mismatch (A/C vs A/G), unparseable x2, transposed (case-normalised)
    assert orient.strip().split(",") == ["1", "-1", "NA", "NA", "NA", "NA", "-1"]
    assert counts.strip() == ("exact=1,flipped=2,dropped_palindromic=1,dropped_mismatch=1,"
                              "dropped_unparseable=2")


# ---- end to end -------------------------------------------------------------------------------------------
def test_counters_reconcile_to_bridged_rows(fx_t, tmp_path):
    out = tmp_path / "t.json"
    d = _json(_run(fx_t, out, orient="true"), out)
    assert d["status"] == "success" and d["qtl_orient"] is True
    c = {k: d[f"qtl_orient_{k}"] for k in COUNTERS}
    bridged = 200  # every catalog row binds its panel row (all non-palindromic, usable)
    assert c == {"exact": 200 - len(SWAP) - 12, "flipped": len(SWAP), "dropped_palindromic": len(PAL),
                 "dropped_mismatch": len(MIS), "dropped_unparseable": len(UNP)}
    assert sum(c.values()) == d["ld_panel_overlap"] == bridged
    assert d["n_snps_overlap"] == c["exact"] + c["flipped"]


def test_transposed_qtl_is_negated(fx_t, fx_e, tmp_path):
    """The transposed fixture writes the swapped rows with G/A alleles AND negated betas. Oriented to the panel it
    must give exactly the exact fixture's coloc result; un-oriented it must not (the negation matters here)."""
    t = _json(_run(fx_t, tmp_path / "t.json", orient="true"), tmp_path / "t.json")
    e = _json(_run(fx_e, tmp_path / "e.json", orient="true"), tmp_path / "e.json")
    assert (t["qtl_orient_flipped"], e["qtl_orient_flipped"]) == (len(SWAP), 0)
    for k in ("summary", "all_pairs", "n_cs_qtl", "n_cs_gwas", "n_snps_overlap"):
        assert t[k] == e[k], k
    t0 = _json(_run(fx_t, tmp_path / "t0.json", orient="false"), tmp_path / "t0.json")
    e0 = _json(_run(fx_e, tmp_path / "e0.json", orient="false"), tmp_path / "e0.json")
    assert (t0["summary"], t0["all_pairs"]) != (e0["summary"], e0["all_pairs"])


@pytest.mark.parametrize("orient", [None, "false"])
@pytest.mark.parametrize("allele_join", [None, "true"])
def test_flag_off_json_equal_to_pre_change(fx_t, old_script, tmp_path, orient, allele_join):
    a, b = tmp_path / "old.json", tmp_path / "new.json"
    ja = _json(_run(fx_t, a, script=old_script, allele_join=allele_join), a)
    jb = _json(_run(fx_t, b, allele_join=allele_join, orient=orient), b)
    assert ja == jb
    assert not any(k.startswith("qtl_orient") for k in jb)


@pytest.mark.parametrize("bad", ["yes", "TRUE", "1"])
def test_unrecognised_value_stops(fx_t, tmp_path, bad):
    r = _run(fx_t, tmp_path / "x.json", orient=bad)
    assert r.returncode != 0 and "--qtl-orient" in r.stderr and not (tmp_path / "x.json").exists()


def test_orient_requires_the_bridge(fx_t, tmp_path):
    r = _run(fx_t, tmp_path / "x.json", allele_join="false", orient="true")
    assert r.returncode != 0 and "--qtl-orient true requires --ld-allele-join true" in r.stderr
    assert not (tmp_path / "x.json").exists()


def test_orient_requires_panel_ref_alt(tmp_path):
    fx = _build(tmp_path / "noalleles", panel_alleles=False)
    r = _run(fx, tmp_path / "x.json", orient="true")
    assert r.returncode != 0 and "qtl-orient requires panel REF/ALT" in r.stderr
    assert not (tmp_path / "x.json").exists()
