"""N8 (W3f): early-exit fits, an empty coloc.susie summary and a summary with no finite PP.H4 are written as
method "none" outputs with an explicit none_reason; estimands treat them as (nan, not fallback), never both_have_cs.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess

import pandas as pd
import pytest

from .conftest import REPO_ROOT
from .fixtures.build_toy_workflow import ANC, RSCRIPT, coloc, ok, pair_row, pair_session_root, run

from ta_r4 import commands, estimands, paths

ARM = "A3_1kg"
SAME = pair_row("FIXP_SAME")
PP = ("pp_h0", "pp_h1", "pp_h2", "pp_h3", "pp_h4")
SCRIPT = REPO_ROOT / commands.COLOC_SCRIPT

_CORE = r'''
suppressPackageStartupMessages({library(data.table); library(jsonlite)})
E <- new.env(); sys.source("%s", envir = E)
side <- function(k) list(fit = list(sets = list(cs = list(L1 = 1L)),
                                    lbf_variable = matrix(0, 1, length(k), dimnames = list(NULL, k))),
                         keys = k, rows = data.table(BETA = rep(0.1, length(k)), SE = 0.05))
k <- c("1:1", "1:2", "1:3")
pri <- list(p1 = 1e-4, p2 = 1e-4, p12 = 5e-6, overlap_min = 0.5, trim = TRUE)
ti <- list(type = "cc", sdY = NA_real_, N = 400)
E$coloc.susie <- function(...) list(summary = NULL)
a <- E$coloc_pair_core(side(k), side(k), ti, ti, pri, "susie")
E$coloc.susie <- function(...) list(summary = data.table(nsnps = 3L, hit1 = "1:1", hit2 = "1:2", PP.H0.abf = NA_real_,
  PP.H1.abf = NA_real_, PP.H2.abf = NA_real_, PP.H3.abf = NA_real_, PP.H4.abf = NA_real_, idx1 = 1L, idx2 = 1L))
b <- E$coloc_pair_core(side(k), side(k), ti, ti, pri, "susie")
f <- function(x) list(method = x$method, pp = x$pp, none_reason = x$out$none_reason, n_snps = x$r$n_snps,
                      names = names(x))
cat(toJSON(list(empty = f(a), no_finite = f(b)), auto_unbox = TRUE, na = "null", null = "null"))
'''


@pytest.fixture(scope="module")
def core():
    p = subprocess.run([RSCRIPT, "-e", _CORE % SCRIPT], cwd=REPO_ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-3000:]
    return json.loads(p.stdout.strip().splitlines()[-1])


@pytest.mark.parametrize("state, reason", [("empty", "coloc_susie_empty"), ("no_finite", "coloc_susie_no_finite_h4")])
def test_core_none_states(core, state, reason):
    c = core[state]
    assert c["method"] == "none" and c["none_reason"] == reason and c["n_snps"] == 3
    assert all(x is None for x in c["pp"])
    assert c["names"] == ["method", "pp", "r", "out"]


@pytest.fixture(scope="module")
def fits(tmp_path_factory):
    return pair_session_root(tmp_path_factory)


def _early_exit_root(fits, tmp_path, statuses):
    root = tmp_path / "ee"
    shutil.copytree(fits, root, symlinks=True)
    for trait, st in zip((SAME["trait_a"], SAME["trait_b"]), statuses):
        if st:
            rds = root / paths.fit_rds(ARM, trait, ANC, "FIXP_SAME")
            ok(run([RSCRIPT, "-e", f'saveRDS(list(status = "{st}", region = "FIXP_SAME"), "{rds}")'], root))
    return root


@pytest.mark.r4_heavy
@pytest.mark.parametrize("mode", ["susie", "A1_matched"])
@pytest.mark.parametrize("statuses, reason", [
    ((None, "too_many_variants"), "fit_early_exit:NA|too_many_variants"),
    (("no_variants", "too_many_variants"), "fit_early_exit:no_variants|too_many_variants"),
])
def test_early_exit_writes_method_none(fits, tmp_path, mode, statuses, reason):
    root = _early_exit_root(fits, tmp_path, statuses)
    p, d = coloc(root, ARM, SAME, "p12_primary", mode)
    ok(p)
    assert d["method"] == "none" and d["none_reason"] == reason, d
    assert all(d[k] is None for k in PP) and d["pp_h4_max"] is None


@pytest.mark.r4_heavy
def test_fitted_pair_has_null_none_reason(fits):
    p, d = coloc(fits, ARM, SAME, "p12_primary", "susie")
    ok(p)
    assert d["method"] == "coloc_susie" and d["none_reason"] is None


_MAIN = r'''
source("%s")
coloc.susie <- %s
main()
'''
_MOCKS = {"coloc_susie_empty": "function(...) list(summary = NULL)",
          "coloc_susie_no_finite_h4": "function(...) { s <- coloc::coloc.susie(...)$summary; "
                                      "s$PP.H4.abf <- NA_real_; list(summary = s) }"}


def _main_with_mock(root, reason, out):
    cmd = commands.coloc_command(ARM, SAME, "p12_primary", "susie")
    cmd[cmd.index("--output") + 1] = out
    p = run([RSCRIPT, "-e", _MAIN % (SCRIPT, _MOCKS[reason]), *cmd[2:]], root)
    ok(p)
    return json.loads((root / out).read_text())


@pytest.mark.r4_heavy
def test_three_none_states_flow_through_estimands(fits, tmp_path):
    docs = []
    root = _early_exit_root(fits, tmp_path, (None, "too_many_variants"))
    p, d = coloc(root, ARM, SAME, "p12_primary", "susie")
    ok(p)
    docs.append(d)
    for reason in _MOCKS:
        d = _main_with_mock(fits, reason, f"data/r4/tmp/none_{reason}.json")
        assert d["method"] == "none" and d["none_reason"] == reason
        docs.append(d)
    man = pd.DataFrame([{"row_id": SAME["row_id"], "region_safe": "FIXP_SAME", "ancestry": ANC,
                         "row_class": "primary", "nc_set": ""}])
    ref = dict(docs[0], arm="REF", method="coloc_susie", none_reason=None, pp_h4_max=0.9, pp_h4=0.9)
    for d in docs:
        rows = estimands.build_rows([d, ref], man)
        x = rows[rows.label == ARM].iloc[0]
        assert math.isnan(x.region_stat) and not x.is_fallback
        pf = estimands.paired_frame(rows, ARM, "REF", "p12_primary", "both methods coloc_susie")
        assert len(pf) == 1 and not pf.both_have_cs.iloc[0]


def test_region_stat_none():
    s, fb = estimands.region_stat({"method": "none", "pp_h4": 0.7, "pp_h4_max": 0.7})
    assert math.isnan(s) and fb is False
