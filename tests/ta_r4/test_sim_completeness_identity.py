"""W3f 15.7b (F4): run_aggregation._sim checks simulation cell files by identity: replicate ids 1..reps once per arm,
row labels equal to the cell, seeds equal to seed_base + the harness's stable_index, and the header config_sha256
equal to the sha256 of the repo's simulation.yaml. A count of rows per arm is not enough."""
from __future__ import annotations

import hashlib

import pytest
import yaml

from .conftest import REPO_ROOT
from .test_simulation_harness import r_json

HEAD = ("region\tscenario\tgen_panel\trep\tseed\tarm\tmethod\tpp_h0\tpp_h1\tpp_h2\tpp_h3\tpp_h4\tpp_h4_max\tn_cs_a"
        "\tn_cs_b\tcausal_a\tcausal_b\tr2_causal\tnone_reason\tfit_status_a\tfit_status_b\n")
# the header lines simulate_coloc_r4.R writes (its sprintf formats)
R_HEAD = ("# simulate_coloc_r4 region=%s scenario=%s gen_panel=%s", "# reps_override=%s", "# status=%s",
          "# n_qualifying_pairs=%s", "# window_variants=%d reps=%d config_sha256=%s")
REGIONS, SCENARIOS, GENS, REPS = ("R2", "R1"), ("H4", "H0"), ("gen_ukb", "gen_1kg"), 3
CELL = ("R1", "H4", "gen_ukb")
CELL_FILE = "R1.H4.gen_ukb.tsv"


def _cfg():
    cfg = yaml.safe_load((REPO_ROOT / "config/ta_r4/simulation.yaml").read_text())
    cfg.update(regions=list(REGIONS), scenarios={k: cfg["scenarios"][k] for k in SCENARIOS},
               gen_panels={k: cfg["gen_panels"][k] for k in GENS}, reps=REPS)
    return cfg


def _index(cfg, region, scenario, gen, rep):
    """Written here from simulate_coloc_r4.R:91-97, independently of ta_r4.id_reconcile."""
    d = [sorted(cfg["regions"]), sorted(cfg["scenarios"]), sorted(cfg["gen_panels"])]
    i, j, k = d[0].index(region), d[1].index(scenario), d[2].index(gen)
    return (i * len(d[1]) * len(d[2]) + j * len(d[2]) + k) * cfg["reps"] + rep


def _rows(cfg, region, sc, gen, reps):
    return [{"region": region, "scenario": sc, "gen_panel": gen, "rep": r,
             "seed": cfg["seed_base"] + _index(cfg, region, sc, gen, r), "arm": a} for r in reps for a in ("A1", "A2", "A3")]


def _text(cell, rows, sha, reps_hdr=REPS, override="none", sha_token=True):
    head = [R_HEAD[0] % cell, R_HEAD[1] % override, R_HEAD[2] % "ok", R_HEAD[3] % "NA",
            (R_HEAD[4] % (1000, reps_hdr, sha)) if sha_token else "# window_variants=%d reps=%d" % (1000, reps_hdr)]
    body = "".join(f"{r['region']}\t{r['scenario']}\t{r['gen_panel']}\t{r['rep']}\t{r['seed']}\t{r['arm']}\t"
                   f"{'A1_abf_matched' if r['arm'] == 'A1' else 'coloc_susie'}\t0\t0\t0\t0.1\t0.9\t0.9\t1\t1\t1:1\t1:2\t1"
                   "\tNA\tNA\tNA\n" for r in rows)
    return "\n".join(head) + "\n" + HEAD + body


def _repo(root):
    """8 cells (2 regions x H4/H0 x 2 generation panels), reps 3, every file as the harness writes it."""
    cfg = _cfg()
    text = yaml.safe_dump(cfg)
    (root / "config/ta_r4").mkdir(parents=True, exist_ok=True)
    (root / "config/ta_r4/simulation.yaml").write_text(text)
    sha = hashlib.sha256(text.encode()).hexdigest()
    d = root / "data/r4/results/sim"
    d.mkdir(parents=True, exist_ok=True)
    for r in REGIONS:
        for s in SCENARIOS:
            for g in GENS:
                (d / f"{r}.{s}.{g}.tsv").write_text(_text((r, s, g), _rows(cfg, r, s, g, range(1, REPS + 1)), sha))
    return cfg, sha, d


def test_sim_accepts_a_correct_cell(tmp_path):
    from ta_r4.run_aggregation import _sim

    _repo(tmp_path)
    for final in (True, False):
        sim, meta = _sim(tmp_path, final=final)
        assert len(sim) == 8 * REPS * 3 and len(meta) == 8
        c = sim[(sim.region == "R1") & (sim.scenario == "H4") & (sim.gen_panel == "gen_ukb")]
        assert sorted(c.rep[c.arm == "A2"]) == [1, 2, 3]


def _mutate(case, cfg, sha):
    rows = _rows(cfg, *CELL, range(1, REPS + 1))
    kw = {}
    if case == "copies_of_rep1":  # Codex's probe: reps rows per arm, every one replicate 1
        rows = _rows(cfg, *CELL, [1] * REPS)
    elif case == "rep_out_of_range":
        for r in rows:
            if r["rep"] == REPS:
                r["rep"] = REPS + 1
    elif case == "wrong_region_label":
        rows[4]["region"] = "R2"
    elif case == "wrong_scenario_label":
        rows[4]["scenario"] = "H0"
    elif case == "wrong_gen_panel_label":
        rows[4]["gen_panel"] = "gen_1kg"
    elif case == "wrong_seed":
        rows[4]["seed"] += 1
    elif case == "config_sha256_mismatch":
        sha = hashlib.sha256(b"another simulation.yaml\n").hexdigest()
    elif case == "missing_config_sha256":
        kw["sha_token"] = False
    return _text(CELL, rows, sha, **kw)


WHAT = {"copies_of_rep1": "rep", "rep_out_of_range": "rep", "wrong_region_label": "region",
        "wrong_scenario_label": "scenario", "wrong_gen_panel_label": "gen_panel", "wrong_seed": "seed",
        "config_sha256_mismatch": "config_sha256", "missing_config_sha256": "config_sha256"}


@pytest.mark.parametrize("case", list(WHAT))
def test_sim_rejects(tmp_path, case):
    from ta_r4.estimands import SimulationIncomplete
    from ta_r4.run_aggregation import _sim

    cfg, sha, d = _repo(tmp_path)
    (d / CELL_FILE).write_text(_mutate(case, cfg, sha))
    for final in (True, False):
        with pytest.raises(SimulationIncomplete) as e:
            _sim(tmp_path, final=final)
        msg = str(e.value)
        print(final, msg)
        assert CELL_FILE in msg and WHAT[case] in msg.split(CELL_FILE, 1)[1]
        assert ": 1 problem(s) " in msg


def test_sim_header_parsed_from_the_r_format():
    from ta_r4.run_aggregation import sim_header

    sha = "ab" * 32
    lines = [R_HEAD[0] % ("SH2B3_12q24", "H3_r2_0.6", "gen_1kg"), R_HEAD[1] % "none", R_HEAD[2] % "ok",
             R_HEAD[3] % 17, R_HEAD[4] % (1000, 200, sha), "region\tscenario"]
    assert sim_header("\n".join(lines) + "\n") == {
        "region": "SH2B3_12q24", "scenario": "H3_r2_0.6", "gen_panel": "gen_1kg", "reps_override": "none",
        "status": "ok", "n_qualifying_pairs": "17", "window_variants": "1000", "reps": "200", "config_sha256": sha}


# --- the Python stable_index against the R harness, full table (r4_heavy) ----------------------------------------

STABLE_INDEX_R = r'''
cfg <- yaml::read_yaml("config/ta_r4/simulation.yaml")
g <- expand.grid(rep = seq_len(cfg$reps), gen = names(cfg$gen_panels), scenario = names(cfg$scenarios),
                 region = unlist(cfg$regions), stringsAsFactors = FALSE)
g$index <- mapply(function(r, s, ge, k) H$stable_index(cfg, r, s, ge, k), g$region, g$scenario, g$gen, g$rep)
cat(toJSON(g[, c("region", "scenario", "gen", "rep", "index")], dataframe = "rows", digits = NA))
'''


@pytest.fixture(scope="module")
def r_table():
    t = r_json(STABLE_INDEX_R)
    return {(x["region"], x["scenario"], x["gen"], x["rep"]): x["index"] for x in t}


def _committed():
    return yaml.safe_load((REPO_ROOT / "config/ta_r4/simulation.yaml").read_text())


@pytest.mark.r4_heavy
def test_stable_index_matches_the_r_harness(r_table):
    from ta_r4.id_reconcile import stable_index

    cfg = _committed()
    assert len(r_table) == 20000 and sorted(r_table.values()) == list(range(1, 20001))
    py = {k: stable_index(cfg, *k) for k in r_table}
    assert py == r_table


@pytest.mark.r4_heavy
def test_stable_index_with_swapped_dimensions_differs_from_the_r_harness(r_table):
    from ta_r4.id_reconcile import stable_index

    cfg = _committed()
    sw = {**cfg, "scenarios": cfg["gen_panels"], "gen_panels": cfg["scenarios"]}
    py = {(r, s, g, k): stable_index(sw, r, g, s, k) for (r, s, g, k) in r_table}
    assert len(py) == 20000
    assert sum(py[k] != r_table[k] for k in r_table) > 0
