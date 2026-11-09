"""W3f 15.4 Task 3 (N14): the simulation never refits with R = I, reports rates by method, and aggregation requires
every (region, scenario, generation panel) cell of the repo's simulation.yaml with the configured replicate count."""
from __future__ import annotations

import shutil

import pandas as pd
import pytest
import yaml

from .conftest import REPO_ROOT
from .test_simulation_harness import r_json

# --- R: no identity refit; method none with the ladder statuses ---------------------------------------------------

NO_REFIT_R = r'''
d <- tempfile("sim_norefit"); dir.create(file.path(d, "EUR_1kg_isect_r4"), recursive = TRUE)
dir.create(file.path(d, "EUR_ukb337k_isect_r4"))
m <- 30L
R1 <- 0.9^abs(outer(seq_len(m), seq_len(m), "-"))
v <- data.frame(SNP_ID = sprintf("rs%d", seq_len(m)), CHR = "12", POS = 1000L + seq_len(m), A1 = "C", A2 = "A",
                REF = "A", ALT = "C", stringsAsFactors = FALSE)
for (p in c("EUR_1kg_isect_r4", "EUR_ukb337k_isect_r4")) saveRDS(list(R = R1, variants = v),
                                                                    file.path(d, p, "SH2B3_12q24.rds"))
real <- H$FZ$run_susie_with_ladder
calls <- character(0)
assign("run_susie_with_ladder", function(z, R, policy, n) {
  ident <- isTRUE(all.equal(unname(R), diag(nrow(R))))
  calls <<- c(calls, if (ident) "identity" else "panel")
  if (ident) real(z = z, R = R, policy = policy, n = n) else list(fit = NULL, status = "non_converged")
}, envir = H$FZ)
pol <- H$read_policy("config/susie_policy.yaml")
f <- H$fit_frozen(H$FZ, rnorm(m), R1, 1e5, pol, 0.95, paste0("12:", 1000L + seq_len(m)))
unit_calls <- calls; calls <- character(0)
ctx <- H$make_context(fit_panel = file.path(d, "EUR_1kg_isect_r4/SH2B3_12q24.rds"),
                      gen_panel = file.path(d, "EUR_ukb337k_isect_r4/SH2B3_12q24.rds"), gen = "gen_ukb",
                      scenario = "H4", region = "SH2B3_12q24", config = "config/ta_r4/simulation.yaml",
                      priors = "config/ta_r4/coloc_priors.yaml", policy = "config/susie_policy.yaml", coverage = 0.95)
r <- H$run_rep(ctx, 1L)$rows
cat(toJSON(list(fit_null = is.null(f$fit), status = f$status, unit_calls = I(unit_calls), rep_calls = I(calls),
                columns = names(r), rows = lapply(split(r, r$arm), as.list)),
           auto_unbox = TRUE, digits = NA, na = "string"))
'''


@pytest.fixture(scope="module")
def norefit():
    return r_json(NO_REFIT_R)


def test_fit_frozen_returns_null_and_the_ladder_status(norefit):
    assert norefit["fit_null"] is True
    assert norefit["status"] == "non_converged"
    assert norefit["unit_calls"] == ["panel"]  # the ladder is never re-run with R = I


def test_run_rep_writes_method_none_with_fit_statuses(norefit):
    cols = norefit["columns"]
    assert cols[-3:] == ["none_reason", "fit_status_a", "fit_status_b"]
    a3 = norefit["rows"]["A3"]
    assert a3["method"] == "none"
    assert a3["none_reason"] == "fit_failed:non_converged|non_converged"
    assert (a3["fit_status_a"], a3["fit_status_b"]) == ("non_converged", "non_converged")
    assert all(a3[k] == "NA" for k in ("pp_h0", "pp_h1", "pp_h2", "pp_h3", "pp_h4", "pp_h4_max"))
    a2 = norefit["rows"]["A2"]
    assert a2["method"] in ("coloc_susie", "fallback_abf", "none") and a2["fit_status_a"] != "NA"
    assert a2["none_reason"] == "NA" or a2["method"] == "none"
    assert norefit["rows"]["A1"]["fit_status_a"] == "NA"
    # A2 identity fits (2) + A3 panel fits (2), each called once: no identity refit of the failed A3 fits
    assert sorted(norefit["rep_calls"]) == ["identity", "identity", "panel", "panel"]


# --- Python: rates by method ---------------------------------------------------------------------------------------

def test_e8_rates_by_method_never_pool():
    from ta_r4.estimands import e8_simulation_rates

    recs = []
    for rep in range(10):
        m = "coloc_susie" if rep < 6 else ("fallback_abf" if rep < 9 else "none")
        h4 = {"coloc_susie": 0.9 if rep < 3 else 0.1, "fallback_abf": 0.95, "none": None}[m]
        recs.append({"region": "R1", "scenario": "H4", "gen_panel": "gen_1kg", "rep": rep + 1, "arm": "A3",
                     "method": m, "pp_h4": h4, "pp_h4_max": h4})
    t = e8_simulation_rates(pd.DataFrame(recs), threshold=0.8).set_index(["arm", "method", "scenario", "gen_panel"])
    assert len(t) == 3
    cs = t.loc[("A3", "coloc_susie", "H4", "gen_1kg")]
    assert (cs.n, cs.k, cs.rate) == (6, 3, 0.5)
    fb = t.loc[("A3", "fallback_abf", "H4", "gen_1kg")]
    assert (fb.n, fb.k, fb.rate) == (3, 3, 1.0)
    nn = t.loc[("A3", "none", "H4", "gen_1kg")]
    assert nn.n == 1 and pd.isna(nn.rate) and pd.isna(nn.ci_lo) and pd.isna(nn.ci_hi)


# --- Python: the complete-cell requirement --------------------------------------------------------------------------

def test_committed_yaml_expects_100_cells():
    from ta_r4.run_aggregation import expected_sim_cells

    cells, reps = expected_sim_cells(REPO_ROOT)
    assert len(cells) == 100 and reps == 200
    assert len({c for c in cells.values()}) == 100
    assert "SH2B3_12q24.H3_r2_0.6.gen_ukb.tsv" in cells


HEAD = ("region\tscenario\tgen_panel\trep\tseed\tarm\tmethod\tpp_h0\tpp_h1\tpp_h2\tpp_h3\tpp_h4\tpp_h4_max\tn_cs_a"
        "\tn_cs_b\tcausal_a\tcausal_b\tr2_causal\tnone_reason\tfit_status_a\tfit_status_b\n")


def _cell(region, sc, gen, reps, status="ok", override="none", arms=("A1", "A2", "A3")):
    body = "".join(f"{region}\t{sc}\t{gen}\t{r}\t{r}\t{a}\t{'A1_abf_matched' if a == 'A1' else 'coloc_susie'}\t0\t0\t0"
                   f"\t0.1\t0.9\t0.9\t1\t1\t1:1\t1:1\t1\tNA\tNA\tNA\n" for r in range(1, reps + 1) for a in arms)
    return f"# status={status}\n# reps_override={override}\n{HEAD}" + (body if status == "ok" else "")


def sim_repo(root, reps=2):
    """Two regions x H4 / H3_r2_0.9 x gen_1kg = 4 cells; R2.H3_r2_0.9 has no qualifying pair."""
    cfg = yaml.safe_load((REPO_ROOT / "config/ta_r4/simulation.yaml").read_text())
    cfg.update(regions=["R1", "R2"], scenarios={k: cfg["scenarios"][k] for k in ("H4", "H3_r2_0.9")},
               gen_panels={"gen_1kg": cfg["gen_panels"]["gen_1kg"]}, reps=reps)
    (root / "config/ta_r4").mkdir(parents=True, exist_ok=True)
    (root / "config/ta_r4/simulation.yaml").write_text(yaml.safe_dump(cfg))
    d = root / "data/r4/results/sim"
    d.mkdir(parents=True, exist_ok=True)
    for reg in ("R1", "R2"):
        for sc in ("H4", "H3_r2_0.9"):
            nq = reg == "R2" and sc == "H3_r2_0.9"
            (d / f"{reg}.{sc}.gen_1kg.tsv").write_text(
                _cell(reg, sc, "gen_1kg", reps, status="no_qualifying_pair" if nq else "ok"))
    return d


RULES = yaml.safe_load((REPO_ROOT / "config/ta_r4/decision_rules.yaml").read_text())


def test_e8_complete_cells_counted(tmp_path):
    from ta_r4.run_aggregation import _e8

    sim_repo(tmp_path)
    t = _e8(tmp_path, RULES, final=True)
    assert set(zip(t.scenario, t.gen_panel)) == {("H4", "gen_1kg"), ("H3_r2_0.9", "gen_1kg")}
    h4 = t[(t.scenario == "H4") & (t.arm == "A2")]
    assert h4[["method", "n", "k", "n_files", "n_files_no_qualifying_pair"]].values.tolist() == [
        ["coloc_susie", 4, 4, 2, 0]]
    h3 = t[t.scenario == "H3_r2_0.9"]
    assert set(h3.n_files) == {2} and set(h3.n_files_no_qualifying_pair) == {1}


@pytest.mark.parametrize("case", ["missing", "extra", "short", "arm_short", "override", "nq_rows", "bad_status"])
def test_e8_incomplete_cells_raise(tmp_path, case):
    from ta_r4.estimands import SimulationIncomplete
    from ta_r4.run_aggregation import _e8

    d = sim_repo(tmp_path)
    f = d / "R1.H4.gen_1kg.tsv"
    if case == "missing":
        f.unlink()
    elif case == "extra":
        (d / "R3.H4.gen_1kg.tsv").write_text(_cell("R3", "H4", "gen_1kg", 2))
    elif case == "short":
        f.write_text(_cell("R1", "H4", "gen_1kg", 1))
    elif case == "arm_short":
        f.write_text(_cell("R1", "H4", "gen_1kg", 2, arms=("A1", "A2", "A2")))
    elif case == "override":
        f.write_text(_cell("R1", "H4", "gen_1kg", 2, override="2"))
    elif case == "nq_rows":
        (d / "R2.H3_r2_0.9.gen_1kg.tsv").write_text(_cell("R2", "H3_r2_0.9", "gen_1kg", 2).replace(
            "# status=ok", "# status=no_qualifying_pair"))
    elif case == "bad_status":
        f.write_text(_cell("R1", "H4", "gen_1kg", 2).replace("# status=ok", "# status=partial"))
    with pytest.raises(SimulationIncomplete) as e:
        _e8(tmp_path, RULES, final=True)
    print(e.value)
    named = {"extra": "R3.H4.gen_1kg.tsv", "nq_rows": "R2.H3_r2_0.9.gen_1kg.tsv"}.get(case, "R1.H4.gen_1kg.tsv")
    assert named in str(e.value)
    if case == "override":
        _e8(tmp_path, RULES, final=False)  # DRAFT accepts a smoke override with the configured row count
    else:
        with pytest.raises(SimulationIncomplete):
            _e8(tmp_path, RULES, final=False)


def test_run_aggregation_exits_3_on_a_missing_cell(tmp_path):
    from .test_run_aggregation import _run, build_tree

    repo = tmp_path / "repo"
    build_tree(repo)
    out = tmp_path / "out"
    assert _run(repo, out, draft=True) == 0
    shutil.rmtree(out)
    next((repo / "data/r4/results/sim").glob("*.tsv")).unlink()
    assert _run(repo, out, draft=True) == 3
    assert not out.exists() or not any(out.iterdir())
