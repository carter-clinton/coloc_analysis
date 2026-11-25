"""W3f 15.7h2 (DEC-2026-11-20-ta-r4-proxy-asthma-refit-keep-n-regions-min-7,
DEC-2026-11-21-ta-r4-proxy-exact-purity-scored-matrix).

The region-contribution proxy over all 5 EUR traits: asthma from the 20 pre-lock pilot fits on the corrected asthma
input (asthma_pilot_commands), and every fitted object's set count recomputed after the fact with exact purity on the
matrix the fit was scored on: R_fit, C_reg = cov2cor(sym(R_fit + eps I)) (a non_converged fit keeps fit3, scored on
regularised LD), or the identity. Fixture fits are built from a 150-variant panel: block A (variants 1-3, r = 0.9),
block B (variants 10-130, equicorrelated r_b) and independent variants elsewhere.
"""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import types
from pathlib import Path

import pytest
import yaml

from .conftest import REPO_ROOT
from .test_frozen_script_armed_e2e import RSCRIPT
from .test_measure_fit_eligibility import _fit, _fixture_repo

from ta_r4 import commands, paths
from ta_r4 import measure_fit_eligibility as m

#: DIFFERENTIAL SUBSTRATE: HEAD before 15.7h2 (data/r4/tmp/w3f/q157/start_15_7h2.txt). Never re-pin.
PRE_157H2_REF = "892c4443a1a8c1605ac57c6bcf824378f7208ab3"
CORRECTED = "data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz"
PILOT_ROOT = "data/r4/measure_asthma_fix/fits"
TABIX = str(Path(RSCRIPT).parent / "tabix")
BGZIP = str(Path(RSCRIPT).parent / "bgzip")
NV = 150
KEY = ("repro_routeC", "bmi", "EUR", "R1")


# ---- fixtures ---------------------------------------------------------------------------------------------------

FIT_R = r'''
suppressPackageStartupMessages(library(jsonlite))
a <- commandArgs(TRUE); s <- fromJSON(a[1])
m <- s$nv; R <- diag(m)
blk <- function(R, ix, r) { R[ix, ix] <- r; diag(R) <- 1; R }
R <- blk(R, 1:3, 0.9); R <- blk(R, 10:130, s$r_big)
P <- if (isTRUE(s$identity_panel)) NULL else R
v <- data.frame(SNP_ID = sprintf("rs%d", 1:m), CHR = "1", POS = 1000L + 10L * (1:m), REF = "A", ALT = "G",
                stringsAsFactors = FALSE)
if (isTRUE(s$dup_panel)) v <- rbind(v, data.frame(SNP_ID = "1:2400", CHR = "1", POS = 2400L, REF = "A", ALT = "G"))
saveRDS(if (is.null(P)) list(R = NULL, variants = v, use_identity = TRUE, status = "identity") else
        list(R = P, variants = v), s$panel)
reg <- function(R, e) { Rr <- R + diag(e, nrow(R)); stats::cov2cor((Rr + t(Rr)) / 2) }
X <- switch(s$score, panel = R, identity = diag(m), reg = reg(R, s$eps), reg3 = reg(R, 3 * s$eps))
nm <- sprintf("rs%d", 1:m)
if (identical(s$kind, "susie_rss")) {
  z <- rep(0, m); z[1:3] <- c(8, 7.9, 7.8)
  fit <- susieR::susie_rss(z = z, R = X, n = 10000, L = 3, coverage = 0.95, max_iter = s$max_iter)
} else {
  comps <- s$comps; L <- length(comps)
  al <- matrix(0, L, m); V <- numeric(L)
  for (i in seq_len(L)) {
    c <- comps[i]
    w <- switch(c, multi = { x <- rep(0.02 / (m - 2), m); x[1:2] <- c(0.5, 0.48); x },
                single1 = { x <- rep(0.03 / (m - 1), m); x[140] <- 0.97; x },
                single2 = { x <- rep(0.03 / (m - 1), m); x[145] <- 0.97; x },
                big = { x <- rep(0.04 / (m - 121), m); x[10:130] <- 0.96 / 121; x },
                null = rep(1 / m, m))
    al[i, ] <- w / sum(w); V[i] <- if (c == "null") 0 else 0.1
  }
  fit <- list(alpha = al, V = V, lbf_variable = al, null_index = 0)
  class(fit) <- "susie"
  set.seed(1)
  fit$sets <- susieR::susie_get_cs(fit, Xcorr = X, coverage = 0.95, min_abs_corr = 0.5)
}
colnames(fit$lbf_variable) <- nm
if (isTRUE(s$drop_sets)) fit$sets <- list(cs = NULL, coverage = NULL, requested_coverage = 0.95)
saveRDS(fit, s$rds)
cat(toJSON(list(n_sets = length(fit$sets$cs), sizes = I(unname(lengths(fit$sets$cs)))), auto_unbox = TRUE))
'''


def _rcall(code, *args, cwd=None):
    p = subprocess.run([RSCRIPT, "-e", code, *map(str, args)], cwd=cwd, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-3000:]
    return p.stdout


def _repo(tmp_path, eps=2e-4):
    """A fixture repo: one confirmatory pair (bmi, t2d) at R1; real configs; a tabix-indexed sumstats window,
    a catalog and a policy YAML with susie.ld_regularization_eps = eps."""
    root = tmp_path / "repo"
    for p in ("config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_repro_routeC.yaml",
              "config/ta_r4/overlay_repro_k2d_routeC.yaml"):
        (root / p).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / p, root / p)
    with open(root / m.PAIR_MANIFEST, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["row_id", "ancestry", "region_id", "region_safe", "trait_a", "trait_b", "row_class", "admissible"])
        w.writerow(["R1__EUR__bmi_vs_t2d", "EUR", "R1", "R1", "bmi", "t2d", "primary", "true"])
    d = root / "data/fx"
    d.mkdir(parents=True)
    rows = ["CHR\tPOS\tREF\tALT\tBETA\tSE\tN\tSNP_ID"] + [f"1\t{1000 + 10 * i}\tA\tG\t0.1\t0.05\t10000\trs{i}"
                                                          for i in range(1, NV + 1)]
    (d / "ss.tsv").write_text("\n".join(rows) + "\n")
    subprocess.run([BGZIP, "-f", str(d / "ss.tsv")], check=True)
    subprocess.run([TABIX, "-f", "-s1", "-b2", "-e2", "-S1", str(d / "ss.tsv.gz")], check=True)
    (d / "cat.tsv").write_text("CHR\tPOS\tREF\tALT\tSNP_ID\n" + "".join(
        f"1\t{1000 + 10 * i}\tA\tG\trs{i}\n" for i in range(1, NV + 1)))
    (tmp_path / "policy.yaml").write_text(yaml.safe_dump({"susie": {"ld_regularization_eps": eps}}))
    for arm in ("repro_routeC", "repro_k2d_routeC"):
        for t in ("bmi", "t2d"):
            if (arm, t) != KEY[:2]:
                _early(root, arm, t)
    return root


def _early(root, arm, trait, region="R1"):
    j = root / paths.fit_json(arm, trait, "EUR", region)
    j.parent.mkdir(parents=True, exist_ok=True)
    j.write_text(json.dumps({"status": "too_many_variants"}))


def _case(root, tmp_path, *, conv, score, comps=(), kind="hand", r_big=0.9, eps=2e-4, max_iter=100,
          drop_sets=False, identity_panel=False, key=KEY, ld_status="ld_loaded", ozf=False, dup_panel=False):
    arm, trait, anc, reg = key
    rds = root / paths.fit_rds(*key)
    rds.parent.mkdir(parents=True, exist_ok=True)
    panel = root / "data/fx/panel.rds"
    spec = {"nv": NV, "r_big": r_big, "eps": eps, "score": score, "comps": list(comps), "kind": kind,
            "max_iter": max_iter, "drop_sets": drop_sets, "identity_panel": identity_panel, "dup_panel": dup_panel,
            "rds": str(rds),
            "panel": str(panel)}
    sp = tmp_path / f"spec_{arm}_{trait}.json"
    sp.write_text(json.dumps(spec))
    info = json.loads(_rcall(FIT_R, sp).strip().splitlines()[-1])
    status = "non_converged" if conv == "non_converged" else "ok"
    (root / paths.fit_json(*key)).write_text(json.dumps({
        "status": status, "convergence_status": conv, "sumstats": "data/fx/ss.tsv.gz", "chrom": "1", "start": 1,
        "end": 1000000, "ld_file_declared": "data/fx/panel.rds", "variant_catalog_path": "data/fx/cat.tsv",
        "ld_status": ld_status, "ld_overlap_zero_fallback": ozf, "policy_hash": "x"}))
    return info


def _proxy(root, tmp_path, **kw):
    out = tmp_path / "fits.tsv"
    rows = m.region_contribution_proxy(RSCRIPT, root, exact_purity=True, fits_tsv=out,
                                       policy_path=tmp_path / "policy.yaml", **kw)
    fits = {(r["arm"], r["trait"], r["region"]): r for r in csv.DictReader(open(out), delimiter="\t")}
    return rows, fits


def _row(fits, key=KEY):
    return fits[(key[0], key[1], key[3])]


def _sub(tmp_path, name, eps=2e-4):
    d = tmp_path / name
    d.mkdir()
    return _repo(d, eps=eps), d


C_REG_COUNT_R = r'''
a <- commandArgs(TRUE); f <- readRDS(a[1]); p <- readRDS(a[2]); e <- as.numeric(a[3])
Rr <- p$R + diag(e, nrow(p$R)); C <- stats::cov2cor((Rr + t(Rr)) / 2)
cat(length(susieR::susie_get_cs(f, Xcorr = C, coverage = 0.95, min_abs_corr = 0.5, dedup = TRUE, squared = FALSE,
                                check_symmetric = TRUE, n_purity = ncol(C))$cs))
'''


# ---- 1-2: exact purity counts ------------------------------------------------------------------------------------

def test_exact_purity_set_counts_on_a_fixture(tmp_path):
    root = _repo(tmp_path)
    _case(root, tmp_path, conv="converged_primary", score="panel", comps=("big", "null"), drop_sets=True)
    _, fits = _proxy(root, tmp_path)
    r = _row(fits)
    assert (r["n_sets_stored"], r["n_sets_exact"], r["scored_matrix"]) == ("0", "1", "panel")
    stored = m._fit_states(RSCRIPT, [KEY], root)[KEY]
    assert stored == 0 and int(r["n_sets_exact"]) == stored + 1


IDENTITY_R = r'''
a <- commandArgs(TRUE); f <- readRDS(a[1]); X <- diag(ncol(f$alpha))
n <- function(k) length(susieR::susie_get_cs(f, Xcorr = X, coverage = 0.95, min_abs_corr = 0.5, n_purity = k)$cs)
cat(length(f$sets$cs), n(100), n(ncol(X)))
'''


def test_identity_ld_counts_unchanged_by_exact_purity(tmp_path):
    """Under identity LD every off-diagonal |r| is 0: a multi-member set has purity 0 whether scored on 100 members
    or all, so the stored, subsampled and exact counts agree (only singletons survive)."""
    root = _repo(tmp_path)
    _case(root, tmp_path, conv="converged_primary", score="identity", comps=("multi", "single1", "big", "single2"),
          identity_panel=True)
    assert _rcall(IDENTITY_R, root / paths.fit_rds(*KEY)).split() == ["2", "2", "2"]
    # (a) production path: a repro_k2d_routeC fit recording identity LD, whose identity panel lists the singleton
    # member rs140's allele key 1:2400:A:G on two rows (rs140 and 1:2400): no mapping, scored on the identity
    k2d = ("repro_k2d_routeC", "bmi", "EUR", "R1")
    root, d = _sub(tmp_path, "k2d_dup")
    _case(root, d, conv="converged_primary", score="identity", comps=("multi", "single1", "big", "single2"),
          identity_panel=True, dup_panel=True, key=k2d, ld_status="identity", ozf=True)
    r = _row(_proxy(root, d)[1], k2d)
    assert (r["scored_matrix"], r["n_sets_exact"], r["n_sets_stored"]) == ("identity", "2", "2")
    # (b) a fit recording ld_missing beside a real declared panel: the recorded-vs-panel cross-check STOPs
    root, d = _sub(tmp_path, "ld_missing_real_panel")
    _case(root, d, conv="converged_primary", score="identity", comps=("single1", "single2", "null"),
          ld_status="ld_missing", ozf=True)
    with pytest.raises(m.PurityIdentityError, match="PURITY_STOP.*identity"):
        _proxy(root, d)


# ---- 3: default path ---------------------------------------------------------------------------------------------

def _old_module():
    src = subprocess.run(["git", "show", f"{PRE_157H2_REF}:src/python/ta_r4/measure_fit_eligibility.py"],
                         cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout
    mod = types.ModuleType("mfe_pre_157h2")
    exec(compile(src, "mfe_pre_157h2", "exec"), mod.__dict__)
    return mod


def test_proxy_default_path_unchanged(tmp_path):
    root = _fixture_repo(tmp_path)
    old = _old_module().region_contribution_proxy(RSCRIPT, root)
    assert m.region_contribution_proxy(RSCRIPT, root, exact_purity=False, asthma_fit_root=None) == old
    assert m.region_contribution_proxy(RSCRIPT, root) == old


# ---- 4, 7: pilot and split argv ----------------------------------------------------------------------------------

def _regions():
    ids = m.region_ids()
    return {g: ids[g] for g in m.confirmatory_pairs()}


def _diff(a, b):
    assert len(a) == len(b)
    return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]


def test_asthma_pilot_commands_use_the_corrected_input_and_the_pilot_dir():
    regs = _regions()
    cmds = m.asthma_pilot_commands(regs, PILOT_ROOT)
    assert sorted(cmds) == sorted((a, g) for a in ("repro_routeC", "repro_k2d_routeC") for g in regs)
    assert len(cmds) == 20
    for (arm, g), argv in cmds.items():
        ref = commands.fit_command(arm, "asthma", "EUR", g, m.arm_config(arm), region_id=regs[g])
        s, o = ref.index("--sumstats") + 1, ref.index("--output") + 1
        assert _diff(argv, ref) == sorted((s, o))
        assert ref[s] == paths.sumstats_path("asthma", "EUR", arm) != CORRECTED
        assert argv[s] == CORRECTED == paths.catalog_source_sumstats_path("asthma", "EUR")
        assert argv[o] == f"{PILOT_ROOT}/proxy_asthma_{arm}/asthma.EUR.{g}.json"
        assert not m._under(argv[o], f"{paths.R4}/results")
    with pytest.raises(ValueError, match="results"):
        m.asthma_pilot_commands(regs, f"{paths.R4}/results/x")


def test_split_argv_equals_the_pilot_argv_except_cap_rscript_and_output(tmp_path):
    regs = _regions()
    rs = "/abs/bin/Rscript"
    pilot = m.asthma_pilot_commands(regs, PILOT_ROOT)
    split = m.asthma_pilot_split_commands(regs, "data/r4/tmp/w3f/q157/proxy_split", rs)
    assert sorted(split) == sorted(pilot)
    for k, argv in split.items():
        o = argv.index("--output") + 1
        assert _diff(argv, pilot[k]) == [1, 2, o]
        assert (argv[1], argv[2]) == ("SUSIE_MAX_VARIANTS=0", rs)
        assert pilot[k][1] == f"SUSIE_MAX_VARIANTS={commands.SUSIE_MAX_VARIANTS}" and pilot[k][2] == "Rscript"
        assert argv[o] == f"data/r4/tmp/w3f/q157/proxy_split/{k[0]}/asthma.EUR.{k[1]}.json"
    with pytest.raises(ValueError, match="absolute"):
        m.asthma_pilot_split_commands(regs, "data/r4/tmp/x", "Rscript")
    with pytest.raises(ValueError, match="results"):
        m.asthma_pilot_split_commands(regs, f"{paths.R4}/results/x", rs)
    with pytest.raises(ValueError, match="cap-after-ld-restriction"):        # measurement_argv untouched
        m.measurement_argv("repro_routeC", "asthma", "EUR", "PYHIN1_1q23", m.arm_config("repro_routeC"),
                           "data/r4/tmp/w3f5/unit", rs)


# ---- 5-6 ---------------------------------------------------------------------------------------------------------

def test_proxy_reads_asthma_from_the_pilot_root_and_stops_excluding_it(tmp_path):
    root = _fixture_repo(tmp_path)
    for arm in ("repro_routeC", "repro_k2d_routeC"):       # the superseded asthma fits are gone
        for p in (paths.fit_json(arm, "asthma", "EUR", "R1"), paths.fit_rds(arm, "asthma", "EUR", "R1")):
            (root / p).unlink()
    pr = root / "pilot"
    for arm, status, n in (("repro_routeC", "ok", 2), ("repro_k2d_routeC", "too_many_variants", None)):
        j = pr / f"proxy_asthma_{arm}" / "asthma.EUR.R1.json"
        j.parent.mkdir(parents=True)
        j.write_text(json.dumps({"status": status}))
        if n is not None:
            _rcall(f'saveRDS(list(sets = list(cs = as.list(seq_len({n})))), "{j.with_name("asthma.EUR.R1.fit.rds")}")')
    rows = {(r["region"], r["contrast"]): r for r in m.region_contribution_proxy(RSCRIPT, root, asthma_fit_root=pr)}
    a1, a2 = rows[("R1", "A1_matched_vs_A3_1kg")], rows[("R1", "A2_identity_vs_A3_1kg")]
    assert (a1["n_pairs"], a1["n_pairs_asthma_excluded"], a1["n_pairs_both_cs_proxy"], a1["n_pairs_unknown"]) == \
        (3, 0, 2, 0)
    assert (a2["n_pairs_asthma_excluded"], a2["n_pairs_both_cs_proxy"], a2["n_pairs_unknown"]) == (0, 1, 1)
    assert all(r["n_pairs_asthma_excluded"] == 0 for r in rows.values())
    # the recorded proxy (Q-DROPASTHMA): exact purity without asthma_fit_root keeps asthma excluded
    root, d = _sub(tmp_path, "exact_excludes_asthma")
    with open(root / m.PAIR_MANIFEST, "a") as fh:
        fh.write("R1__EUR__asthma_vs_bmi\tEUR\tR1\tR1\tasthma\tbmi\tprimary\ttrue\n")
    _case(root, d, conv="converged_primary", score="panel", comps=("multi", "single1", "null"))
    _case(root, d, conv="converged_primary", score="panel", comps=("single1", "null"),
          key=("repro_routeC", "asthma", "EUR", "R1"))
    _early(root, "repro_k2d_routeC", "asthma")
    rows_ex, fits = _proxy(root, d)
    assert fits and not any(t == "asthma" for _, t, _ in fits)
    default = m.region_contribution_proxy(RSCRIPT, root)
    assert [r["n_pairs_asthma_excluded"] for r in rows_ex] == [r["n_pairs_asthma_excluded"] for r in default] == [1, 1]


def test_n_regions_min_is_7():
    assert m.N_REGIONS_MIN == 7
    rules = yaml.safe_load((REPO_ROOT / "config/ta_r4/decision_rules.yaml").read_text())

    def found(x):
        if isinstance(x, dict):
            return [v for k, v in x.items() if k == "n_regions_min"] + [f for v in x.values() for f in found(v)]
        return [f for v in x for f in found(v)] if isinstance(x, list) else []
    assert found(rules) == [7]
    assert subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "config/ta_r4/decision_rules.yaml"],
                          cwd=REPO_ROOT).returncode == 0
    sub = next(a for a in m._parser()._actions if a.dest == "cmd").choices["proxy"]
    opts = {o for a in sub._actions for o in a.option_strings} - {"-h", "--help"}
    assert opts == {"--rscript", "--tsv", "--exact-purity", "--asthma-fit-root", "--fits-tsv"}   # no floor override


# ---- 8-9: the scored matrix ----------------------------------------------------------------------------------------

def test_regularised_fit_is_scored_on_the_regularised_matrix(tmp_path):
    root = _repo(tmp_path, eps=2e-4)
    info = _case(root, tmp_path, conv="non_converged", score="reg", kind="susie_rss", max_iter=2, eps=2e-4)
    assert any(2 <= s <= 100 for s in info["sizes"]), info
    _, fits = _proxy(root, tmp_path)
    r = _row(fits)
    assert (r["scored_matrix"], r["discriminating"]) == ("regularized", "True")
    assert float(r["max_abs_purity_diff"]) > 1e-6 and float(r["max_abs_resid"]) <= 1e-12
    j = root / paths.fit_json(*KEY)
    j.write_text(j.read_text().replace('"non_converged"', '"converged_primary"'))   # R_fit the only candidate
    with pytest.raises(m.PurityIdentityError, match="PURITY_STOP"):
        _proxy(root, tmp_path)


def test_scored_matrix_label_names_the_matrix_that_matched(tmp_path):
    # converged_primary on R -> panel; its analytic n_sets_exact_alt equals the pinned call on C_reg
    root, d = _sub(tmp_path, "primary")
    _case(root, d, conv="converged_primary", score="panel", comps=("multi", "single1", "null"))
    r = _row(_proxy(root, d)[1])
    assert (r["scored_matrix"], r["discriminating"]) == ("panel", "True")
    assert float(r["max_abs_purity_diff"]) > 1e-6
    assert r["n_sets_exact_alt"] == _rcall(C_REG_COUNT_R, root / paths.fit_rds(*KEY), root / "data/fx/panel.rds",
                                           2e-4).strip()
    # non_converged on C_reg -> regularized; non_converged on R (fit3 errored, fit2 kept) -> panel_fallback
    for name, score, want in (("nc_reg", "reg", "regularized"), ("nc_panel", "panel", "panel_fallback")):
        root, d = _sub(tmp_path, name)
        _case(root, d, conv="non_converged", score=score, comps=("multi", "single1", "null"))
        r = _row(_proxy(root, d)[1])
        assert (r["scored_matrix"], r["discriminating"]) == (want, "True"), name
        assert float(r["max_abs_purity_diff"]) > 1e-6, name
    # no candidate matches -> STOP: converged_regularized on R (C_reg only); non_converged on R + 3 eps I
    for name, conv, score in (("creg_on_r", "converged_regularized", "panel"), ("nc_reg3", "non_converged", "reg3")):
        root, d = _sub(tmp_path, name)
        _case(root, d, conv=conv, score=score, comps=("multi", "single1", "null"))
        with pytest.raises(m.PurityIdentityError, match="PURITY_STOP"):
            _proxy(root, d)
    # a singleton-only non_converged fit -> regularized, not discriminating
    root, d = _sub(tmp_path, "singletons")
    _case(root, d, conv="non_converged", score="reg", comps=("single1", "single2", "null"))
    r = _row(_proxy(root, d)[1])
    assert (r["scored_matrix"], r["discriminating"], r["n_sets_exact"], r["n_sets_exact_alt"]) == \
        ("regularized", "False", "2", "2")
    # not discriminating and the alt count differs -> STOP: a >100-member set at exact panel purity 0.50002,
    # which is in [0.5, 0.5 (1 + eps)) for eps 2e-4 read from policy_path
    root, d = _sub(tmp_path, "nondisc")
    info = _case(root, d, conv="converged_primary", score="panel", comps=("single1", "big", "null"), r_big=0.50002)
    assert sorted(info["sizes"]) == [1, 120], info
    with pytest.raises(m.PurityIdentityError, match="PURITY_STOP.*not discriminating"):
        _proxy(root, d)
