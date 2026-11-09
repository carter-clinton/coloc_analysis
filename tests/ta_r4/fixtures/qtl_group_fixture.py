"""W3e fixture: one region (FIX_1), traits tA (signal) / tB (null), eQTL features f1 (signal) / f2 (null), laid out at
the R4 relative paths for QTL_A3 (A3_1kg), QTL_A2 (A2_identity) and QTL_legacy (repro_routeL) under a fixture root."""
from __future__ import annotations

import csv
import os
import shutil
import subprocess
from pathlib import Path

from ta_r4 import paths
from ta_r4.harmonize_qtl_r4 import QTL_SOURCES, harmonized_path

REPO_ROOT = Path(__file__).resolve().parents[3]
R4_CONDA_PREFIX = Path("/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4")


def _job_env(yml="envs/r_coloc.yml"):
    """The Snakemake job env built from `yml` (the R the rules run: has R.utils, which fread needs for .gz)."""
    text = (REPO_ROOT / yml).read_text()
    hit = [y.with_suffix("") for y in R4_CONDA_PREFIX.glob("*_.yaml") if y.read_text() == text]
    assert len(hit) == 1, f"{len(hit)} job envs match {yml}"
    return hit[0]


RSCRIPT = str(_job_env() / "bin/Rscript")
REGION, CHR, START, END = "FIX_1", "12", 110000000, 110200000
TRAITS = ("tA", "tB")
FEATURES = ("ENSG00000000101", "ENSG00000000102")  # f1 signal, f2 null
QTD, TISSUE = "QTD999999", "Whole_Blood"
MCOLS = ["qtl_row_id", "region_safe", "ancestry", "trait", "source", "tissue", "qtd", "gene_id",
         "molecular_trait_id", "chr38", "start38", "end38", "n_qtl_variants_in_window"]
SWAP = list(range(2, 201, 9))   # QTL alleles transposed vs the panel, beta negated
PAL = [7, 57, 107, 157]         # QTL A/T: dropped under --qtl-orient
CAT_SWAP = list(range(3, 201, 11))

_BUILDER = r'''
suppressPackageStartupMessages({library(coloc); library(susieR); library(data.table)})
set.seed(20261103)
ROOT <- "__ROOT__"; SWAP <- c(__SWAP__); PAL <- c(__PAL__); CAT_SWAP <- c(__CAT_SWAP__)
p <- function(rel) { f <- file.path(ROOT, rel); dir.create(dirname(f), recursive = TRUE, showWarnings = FALSE); f }
n <- 200L; chrom <- "__CHR__"; pos <- __START__L + seq_len(n) * 500L
nm <- sprintf("rs%d", 900000L + seq_len(n))
pan <- data.frame(CHR = chrom, POS = pos, REF = "A", ALT = "G", SNP_ID = nm, stringsAsFactors = FALSE)
d <- abs(outer(seq_len(n), seq_len(n), "-")); Rd <- 0.85 ^ d; diag(Rd) <- 1
Rb <- Rd; dimnames(Rb) <- NULL
for (rel in c("__PANEL_A3__", "__PANEL_A2__")) saveRDS(list(R = Rb, variants = pan), p(rel))
saveRDS(list(R = Rb, variants = pan[, c("SNP_ID", "CHR", "POS")]), p("__PANEL_LEG__"))
cr <- rep("A", n); ca <- rep("G", n); cr[CAT_SWAP] <- "G"; ca[CAT_SWAP] <- "A"
fwrite(data.frame(CHR = chrom, POS = pos, REF = cr, ALT = ca, SNP_ID = nm), p("__CATALOG__"), sep = "\t")
Rf <- Rd; dimnames(Rf) <- list(nm, nm)
sim <- function(lead, z0, se) { z <- rep(0, n); if (lead > 0) z[lead] <- z0; as.vector(Rf %*% z) + rnorm(n, sd = 1) * (lead == 0) + rnorm(n, sd = 0.05) * (lead > 0) }
for (tr in c("tA", "tB")) {
  z <- if (tr == "tA") sim(100L, 6.5) else sim(0L, 0)
  se <- rep(0.02, n)
  fit <- coloc::runsusie(list(beta = z * se, varbeta = se^2, snp = nm, position = pos, type = "quant",
                              N = 50000L, sdY = 1, MAF = rep(0.25, n), LD = Rf), suffix = 1)
  cat(tr, "n_cs", length(fit$sets$cs), "\n")
  for (rel in strsplit("__FITS__", ";")[[1]]) if (grepl(paste0("/", tr, "\\."), rel)) saveRDS(fit, p(rel))
  ss <- data.table(CHR = chrom, POS = pos, SNP_ID = nm, REF = "A", ALT = "G", BETA = z * se, SE = se)
  f <- p(sprintf("data/processed/sumstats_harmonized/%s.EUR.tsv", tr)); fwrite(ss, f, sep = "\t")
  system2("gzip", c("-f", shQuote(f))); file.rename(paste0(f, ".gz"), sub("\\.tsv$", ".tsv.bgz", f))
}
for (k in 1:2) {
  zq <- if (k == 1) sim(100L, 5.5) else sim(0L, 0)
  sq <- rep(0.03, n); beta <- zq * sq
  qr <- rep("A", n); qa <- rep("G", n); qr[SWAP] <- "G"; qa[SWAP] <- "A"; beta[SWAP] <- -beta[SWAP]; qa[PAL] <- "T"
  q <- data.table(variant_id = sprintf("chr%s_%d_%s_%s", chrom, pos, qr, qa), beta = beta, se = sq,
                  maf = 0.25, position = pos, N = 335L, sdY = 1, gene_id = c("__F1__", "__F2__")[k],
                  tissue = "__TISSUE__", pvalue = 0.5, rsid = nm, chromosome = chrom)
  fwrite(q, p(c("__H1__", "__H2__")[k]), sep = "\t")
}
cat("FIXTURE_OK\n")
'''


def _write_tsv(path, header, rows, delim="\t"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter=delim, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def manifest_rows():
    return [[f"{REGION}__EUR__{t}__eqtl__{TISSUE}__{f}", REGION, "EUR", t, "eqtl", TISSUE, QTD, f, f,
             CHR, START, END, 200] for t in TRAITS for f in FEATURES]


def build(root):
    root = Path(root)
    fits = [paths.fit_rds(a, t, "EUR", REGION) for a in ("A3_1kg", "A2_identity", "repro_routeL") for t in TRAITS]
    subs = {"__ROOT__": str(root), "__SWAP__": ",".join(map(str, SWAP)), "__PAL__": ",".join(map(str, PAL)),
            "__CAT_SWAP__": ",".join(map(str, CAT_SWAP)), "__CHR__": CHR, "__START__": str(START),
            "__PANEL_A3__": paths.panel_path("A3_1kg", REGION), "__PANEL_A2__": paths.panel_path("A2_identity", REGION),
            "__PANEL_LEG__": paths.panel_path("repro_routeL", REGION, "EUR"),
            "__CATALOG__": paths.catalog_path("r4", REGION), "__FITS__": ";".join(fits),
            "__F1__": FEATURES[0], "__F2__": FEATURES[1], "__TISSUE__": TISSUE,
            "__H1__": harmonized_path("eqtl", QTD, FEATURES[0], REGION) + ".tmp.tsv",
            "__H2__": harmonized_path("eqtl", QTD, FEATURES[1], REGION) + ".tmp.tsv"}
    code = _BUILDER
    for k, v in subs.items():
        code = code.replace(k, v)
    root.mkdir(parents=True, exist_ok=True)
    (root / "build.R").write_text(code)
    r = subprocess.run([RSCRIPT, str(root / "build.R")], capture_output=True, text=True)
    assert r.returncode == 0 and "FIXTURE_OK" in r.stdout, r.stdout + r.stderr
    for f in FEATURES:  # harmonized files are gzipped TSVs, as harmonize_qtl_r4 writes them
        tmp = root / (harmonized_path("eqtl", QTD, f, REGION) + ".tmp.tsv")
        subprocess.run(["gzip", "-f", str(tmp)], check=True)
        os.replace(str(tmp) + ".gz", root / harmonized_path("eqtl", QTD, f, REGION))
    if paths.catalog_path("legacy", REGION) != paths.catalog_path("r4", REGION):
        (root / paths.catalog_path("legacy", REGION)).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / paths.catalog_path("r4", REGION), root / paths.catalog_path("legacy", REGION))
    _write_tsv(root / paths.regions_csv(), ["region_id", "ancestry", "chr", "start", "end"],
               [[REGION, "EUR", CHR, START, END]], delim=",")
    _write_tsv(root / "config/ta_r4/trait_manifest.tsv", ["trait", "ancestry", "type", "sdY", "sdY_source", "N_median"],
               [[t, "EUR", "quant", "1", "fixture", "50000"] for t in TRAITS])
    _write_tsv(root / "config/ta_r4/qtl_manifest.tsv", MCOLS, manifest_rows())
    for rel in ("config/ta_r4/coloc_priors.yaml", QTL_SOURCES):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, root / rel)
    link = root / "src/snakemake/scripts"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(REPO_ROOT / "src/snakemake/scripts")
    from .build_toy_workflow import write_input_manifests
    write_input_manifests(root, sumstats=[paths.sumstats_path(t, "EUR", a) for a in ("A3_1kg", "repro_routeL") for t in TRAITS],
                          catalogs=[paths.catalog_path(k, REGION) for k in ("r4", "legacy")],
                          harmonized=[harmonized_path("eqtl", QTD, f, REGION) for f in FEATURES])
    (root / "build.out").write_text(r.stdout)
    return root


def r_env():
    return dict(os.environ, PATH=f"{Path(RSCRIPT).parent}:{os.environ['PATH']}")
