"""Cross-evaluated credible-set purity: an R = I fit's CS scored against a real panel (Pitfall 9; W3d)."""
from __future__ import annotations

import csv
import subprocess

import pytest

from .conftest import REPO_ROOT

RSCRIPT = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"
SCRIPT = REPO_ROOT / "src/snakemake/scripts/ta_r4/cs_cross_purity.R"

BUILD = r"""
args <- commandArgs(TRUE); d <- args[1]
nm <- c("rs1", "rs2", "rs3", "1:400", "rs5")
lbf <- matrix(0, nrow = 2, ncol = 5, dimnames = list(NULL, nm))
fit <- list(lbf_variable = lbf, alpha = lbf,
            sets = list(cs = list(L1 = c(1L, 2L), L2 = c(3L, 4L, 5L), L3 = c(5L)),
                        purity = data.frame(min.abs.corr = c(1, 1, 1), mean.abs.corr = c(1, 1, 1),
                                            median.abs.corr = c(1, 1, 1))))
class(fit) <- "susie"
saveRDS(fit, file.path(d, "A2.fit.rds"))
R <- diag(6)
R[1, 2] <- R[2, 1] <- -0.1
R[3, 4] <- R[4, 3] <- 0.8; R[3, 5] <- R[5, 3] <- 0.6; R[4, 5] <- R[5, 4] <- -0.7
v <- data.frame(SNP_ID = c("rs1", "rs2", "rs3", "rsX", "rs5", "rs6"), CHR = "1",
                POS = c(100L, 200L, 300L, 400L, 500L, 600L), A1 = "A", A2 = "G")
saveRDS(list(R = R, variants = v, ld_source = "fixture", region_id = "R1", ancestry = "EUR"),
        file.path(d, "EUR_1kg_r4.rds"))
v2 <- v; v2$SNP_ID[4] <- "rsY"; v2$POS[5] <- 400L
saveRDS(list(R = R, variants = v2), file.path(d, "dup.rds"))
v3 <- v; v3$SNP_ID[1] <- "rsZ"
saveRDS(list(R = R, variants = v3), file.path(d, "missing.rds"))
saveRDS(list(R = diag(6), variants = v), file.path(d, "identity.rds"))
"""


@pytest.fixture(scope="module")
def fx(tmp_path_factory):
    d = tmp_path_factory.mktemp("cross_purity")
    subprocess.run([RSCRIPT, "-e", BUILD, str(d)], check=True, capture_output=True, text=True)
    return d


def _run(fx, panel, out="out.tsv"):
    return subprocess.run([RSCRIPT, str(SCRIPT), "--fit", str(fx / "A2.fit.rds"), "--panel", str(fx / panel),
                           "--output", str(fx / out)], capture_output=True, text=True)


def _read(p):
    with open(p) as fh:
        return {r["cs"]: r for r in csv.DictReader(fh, delimiter="\t")}


def test_cross_purity_against_real_panel(fx):
    p = _run(fx, "EUR_1kg_r4.rds")
    assert p.returncode == 0, p.stderr
    t = _read(fx / "out.tsv")
    assert set(t) == {"L1", "L2", "L3"}
    assert float(t["L1"]["min_abs_corr"]) == pytest.approx(0.1)
    assert float(t["L1"]["purity_fit"]) == 1.0
    assert float(t["L2"]["min_abs_corr"]) == pytest.approx(0.6)
    assert float(t["L3"]["min_abs_corr"]) == 1.0
    assert [t[k]["size"] for k in ("L1", "L2", "L3")] == ["2", "3", "1"]


def test_identity_panel_gives_zero_for_multi_member_sets(fx):
    p = _run(fx, "identity.rds", "id.tsv")
    assert p.returncode == 0, p.stderr
    t = _read(fx / "id.tsv")
    assert float(t["L1"]["min_abs_corr"]) == 0.0 and float(t["L3"]["min_abs_corr"]) == 1.0


@pytest.mark.parametrize("panel, code", [("dup.rds", "AMBIGUOUS"), ("missing.rds", "UNMATCHED")])
def test_refuses_unmatched_or_ambiguous_members(fx, panel, code):
    p = _run(fx, panel, f"{panel}.tsv")
    assert p.returncode != 0
    assert code in p.stderr
    assert not (fx / f"{panel}.tsv").exists()
