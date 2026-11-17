"""W3f 15.5 Task 1: the no-fit measurement of post-restriction variant counts (review N1 recount) and the
confirmatory-region contribution proxy (N7). Nothing here fits: cap 0, outputs only under data/r4/tmp/."""
from __future__ import annotations

import csv
import json
import shutil
import subprocess

import pytest

from .conftest import REPO_ROOT, merged_config
from .test_frozen_script_armed_e2e import ANC, REGION, RSCRIPT, TRAIT, _ok, _run, _write_manifest, build_fixture

from ta_r4 import commands, paths
from ta_r4 import measure_fit_eligibility as m

OUT = "data/r4/tmp/w3f5/unit"
KEY = ("A3_1kg", "asthma", "EUR", "PYHIN1_1q23")
SHA = {"sumstats": "a" * 64, "catalog": "b" * 64, "panel": "c" * 64}


def _cfg(arm):
    return merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml")


def _margv(key=KEY, out=OUT, region_id="PYHIN1_1q23"):
    return m.measurement_argv(*key, _cfg(key[0]), out, RSCRIPT, region_id=region_id)


# ---- measurement_argv -------------------------------------------------------------------------------

def test_argv_is_fit_command_with_three_changes():
    fc = commands.fit_command(*KEY, _cfg(KEY[0]), region_id="PYHIN1_1q23")
    ma = _margv()
    assert len(ma) == len(fc)
    diff = {i: (fc[i], ma[i]) for i in range(len(fc)) if fc[i] != ma[i]}
    i_out = fc.index("--output") + 1
    assert diff == {1: ("SUSIE_MAX_VARIANTS=16000", "SUSIE_MAX_VARIANTS=0"),
                    2: ("Rscript", RSCRIPT),
                    i_out: (paths.fit_json(*KEY), f"{OUT}/A3_1kg/asthma.EUR.PYHIN1_1q23.json")}


def test_argv_cap_is_zero():
    assert _margv()[1] == "SUSIE_MAX_VARIANTS=0"


def test_argv_reads_the_corrected_asthma_lift():
    ma = _margv()
    assert ma[ma.index("--sumstats") + 1] == "data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz"


@pytest.mark.parametrize("out", ["data/r4/results/x", "/tmp/x", "data/r4/tmp/../results/A3_1kg",
                                 "data/r4/tmpx/y", "data/r4/tmp"])
def test_argv_refuses_out_dir_outside_tmp(out):
    with pytest.raises(ValueError, match="data/r4/tmp"):
        _margv(out=out)


def test_argv_refuses_output_in_a_result_dir(monkeypatch):
    real = paths.result_dirs
    monkeypatch.setattr(paths, "result_dirs", lambda kind: real(kind) + [f"{OUT}/A3_1kg"])
    with pytest.raises(ValueError, match="result dir"):
        _margv()


def test_argv_refuses_without_cap_after_ld_restriction(monkeypatch):
    real = commands.fit_command

    def no_flag(*a, **k):
        cmd = real(*a, **k)
        i = cmd.index("--cap-after-ld-restriction")
        return cmd[:i] + cmd[i + 2:]
    monkeypatch.setattr(commands, "fit_command", no_flag)
    with pytest.raises(ValueError, match="cap-after-ld-restriction"):
        _margv()


def test_argv_refuses_a_legacy_arm():
    with pytest.raises(ValueError, match="cap-after-ld-restriction"):
        m.measurement_argv("repro_routeC", "asthma", "EUR", "PYHIN1_1q23", _cfg("repro_routeC"), OUT, RSCRIPT)


# ---- run list and eligibility rule --------------------------------------------------------------------

def test_run_list_boundary_is_strictly_above_the_cap():
    fits = [("A3_ukb", "bmi", "EUR", "R_lo"), ("A3_ukb", "bmi", "EUR", "R_eq"), ("A3_ukb", "bmi", "EUR", "R_hi")]
    nvar = {("EUR_ukb337k_r4", "EUR", "R_lo"): m.CAP - 1, ("EUR_ukb337k_r4", "EUR", "R_eq"): m.CAP,
            ("EUR_ukb337k_r4", "EUR", "R_hi"): m.CAP + 1}
    assert m.CAP == 16000
    assert m.run_list(nvar=nvar, fits=fits, extra=()) == [("A3_ukb", "bmi", "EUR", "R_hi")]
    extra = (("A3_1kg", "t2d", "EUR", "R_lo"),)
    assert m.run_list(nvar=nvar, fits=fits, extra=extra) == sorted([("A3_ukb", "bmi", "EUR", "R_hi"), *extra])


def test_run_list_on_the_rebuilt_panels():
    keys = m.run_list()
    assert len(keys) == len(set(keys))
    assert set(m.REGRESSION_KEYS) <= set(keys) and set(m.pre_fix_keys()) <= set(keys)
    assert ("A3_ukb", "bmi", "EUR", "BMI_5q13_3") in keys          # UKB native 25,160 > 16,000
    assert ("AFR661_A2", "t2d", "AFR", "PYHIN1_1q23") in keys        # AFR661 identity 21,048
    assert not any(k[0] in ("A2_identity", "A3_1kg_isect", "A3_ukb_isect") for k in keys)   # all <= 15,236
    assert not any(k[3] == "HLA_6p21" for k in keys)                 # inadmissible
    assert all(k[0] in m.production_arms() for k in keys)


def test_pre_fix_keys_are_a3_1kg_over_every_primary_eur_trait_and_region():
    keys = m.pre_fix_keys()
    assert {k[0] for k in keys} == {"A3_1kg"} and {k[2] for k in keys} == {"EUR"}
    assert {k[1] for k in keys} == {"asthma", "bmi", "hypertension", "stroke", "t2d"}
    assert len({k[3] for k in keys}) == 10 and len(keys) == 50


def test_fit_keys_are_the_admissible_manifest_traits():
    fits = m.fit_keys()
    assert ("A3_1kg", "asthma", "EUR", "PYHIN1_1q23") in fits
    assert not any(k[3] in ("HLA_6p21", "BMI_Xq24") for k in fits)   # inadmissible regions
    assert ("AFR661_A3", "bmi", "AFR", "PYHIN1_1q23") not in fits        # AFR rows are asthma/stroke/t2d


@pytest.mark.parametrize("n, ok", [(0, True), (16000, True), (16001, False)])
def test_eligible_rule(n, ok):
    assert m.eligible(n) is ok


def test_bound_row_needs_panel_at_or_below_cap():
    r = m.bound_row(("A3_1kg", "asthma", "EUR", "APOE_19q13"), 15236, SHA)
    assert (r["method"], r["eligible"], r["panel_n_var"]) == ("bound", "true", 15236)
    assert (r["sumstats_sha256"], r["catalog_sha256"], r["panel_sha256"]) == ("a" * 64, "b" * 64, "c" * 64)
    with pytest.raises(ValueError, match="above the cap"):
        m.bound_row(("A3_ukb", "asthma", "EUR", "PYHIN1_1q23"), 26050, SHA)


def test_pinned_inputs_come_from_the_committed_manifests():
    p = m.pinned_inputs(KEY)
    assert p["sumstats_path"] == "data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz"
    assert p["sumstats"].startswith("49edfc54")
    assert p["catalog_path"] == "data/r4/ld/variants_r4/PYHIN1_1q23.tsv"
    assert p["panel_path"] == paths.panel_path(*KEY[:1], KEY[3], KEY[2])
    assert all(len(p[k]) == 64 for k in ("sumstats", "catalog", "panel"))


# ---- argv path audit (checker W4) ---------------------------------------------------------------------

@pytest.mark.r4_heavy
def test_path_audit_over_the_real_run_list():
    keys = m.run_list()
    assert keys
    ids = m.region_ids()
    for k in keys:
        argv = m.measurement_argv(*k, m.arm_config(k[0]), OUT, RSCRIPT, region_id=ids[k[3]])
        assert m.audit_argv(argv, OUT, k[0], repo=REPO_ROOT) == [], k


@pytest.mark.r4_heavy
def test_path_audit_catches_output_left_at_fit_json():
    k = KEY
    argv = m.measurement_argv(*k, m.arm_config(k[0]), OUT, RSCRIPT, region_id="PYHIN1_1q23")
    argv[argv.index("--output") + 1] = paths.fit_json(*k)
    v = m.audit_argv(argv, OUT, k[0], repo=REPO_ROOT)
    assert any("--output" in x for x in v), v


def test_path_audit_catches_an_extra_write_path_under_out_dir(tmp_path):
    k = KEY
    argv = m.measurement_argv(*k, _cfg(k[0]), OUT, RSCRIPT, region_id="PYHIN1_1q23")
    argv[argv.index("--policy") + 1] = f"{OUT}/policy.yaml"
    v = m.audit_argv(argv, OUT, k[0], repo=tmp_path)
    assert any("--policy" in x for x in v), v


# ---- driver --------------------------------------------------------------------------------------------

def test_driver_script_is_sbatch_ready(tmp_path):
    s = m.driver_script(list_path="data/r4/tmp/w3f/x/runlist.jsonl", n_tasks=7, log_dir="data/r4/tmp/w3f/x/logs",
                        repo="/repo", py="/abs/python3.11")
    for want in ("#SBATCH -p compute", "#SBATCH -A clintonlab_cpu", "#SBATCH -q normal", "#SBATCH -t 01:00:00",
                 "#SBATCH --mem=32G", "#SBATCH --array=1-7", "cd /repo", "/abs/python3.11",
                 "--task \"$SLURM_ARRAY_TASK_ID\""):
        assert want in s, want
    assert "bin/r4_fire.sh" not in s and "snakemake" not in s


# ---- summarise ----------------------------------------------------------------------------------------

def _write(out_dir, arm, name, doc, rds_expr, inputs=SHA):
    d = out_dir / arm
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps(doc))
    if rds_expr is not None:
        subprocess.run([RSCRIPT, "-e", f'saveRDS({rds_expr}, "{d / (name + ".fit.rds")}")'], check=True)
    if inputs is not None:
        (d / f"{name}.inputs.json").write_text(json.dumps(inputs))


EARLY = {"status": "too_many_variants", "n_variants": 20000, "n_variants_pre_ld": 38000,
         "cap_stage": "after_ld_restriction"}
EARLY_RDS = 'list(status = "too_many_variants", n_variants = 20000L)'
K_UKB = ("A3_ukb", "asthma", "EUR", "PYHIN1_1q23")


def test_summarise_reads_early_exits(tmp_path):
    _write(tmp_path, "A3_ukb", "asthma.EUR.PYHIN1_1q23", EARLY, EARLY_RDS)
    rows = m.summarise(tmp_path, RSCRIPT, [K_UKB])
    assert rows == [{"arm": "A3_ukb", "trait": "asthma", "ancestry": "EUR", "region_safe": "PYHIN1_1q23",
                     "status": "too_many_variants", "n_variants_pre_ld": 38000, "n_variants": 20000,
                     "cap_stage": "after_ld_restriction", "inputs": SHA}]


def test_summarise_raises_on_a_fitted_rds(tmp_path):
    _write(tmp_path, "A3_ukb", "asthma.EUR.PYHIN1_1q23", EARLY, 'list(lbf_variable = matrix(0, 2, 2))')
    with pytest.raises(m.FitHappened, match="lbf_variable"):
        m.summarise(tmp_path, RSCRIPT, [K_UKB])


def test_summarise_raises_on_a_non_early_status(tmp_path):
    _write(tmp_path, "A3_ukb", "asthma.EUR.PYHIN1_1q23", dict(EARLY, status="ok"), EARLY_RDS)
    with pytest.raises(m.FitHappened, match="status"):
        m.summarise(tmp_path, RSCRIPT, [K_UKB])


def test_summarise_raises_on_a_missing_rds(tmp_path):
    _write(tmp_path, "A3_ukb", "asthma.EUR.PYHIN1_1q23", EARLY, None)
    with pytest.raises(m.FitHappened, match="fit.rds"):
        m.summarise(tmp_path, RSCRIPT, [K_UKB])


def test_summarise_raises_on_a_missing_measurement(tmp_path):
    _write(tmp_path, "A3_ukb", "asthma.EUR.PYHIN1_1q23", EARLY, EARLY_RDS)
    with pytest.raises(m.MeasurementSetError, match="no measurement"):
        m.summarise(tmp_path, RSCRIPT, [K_UKB, ("A3_ukb", "bmi", "EUR", "PYHIN1_1q23")])


def test_summarise_raises_on_a_stale_extra_measurement(tmp_path):
    _write(tmp_path, "A3_ukb", "asthma.EUR.PYHIN1_1q23", EARLY, EARLY_RDS)
    _write(tmp_path, "A3_ukb", "bmi.EUR.PYHIN1_1q23", EARLY, EARLY_RDS)
    with pytest.raises(m.MeasurementSetError, match="not in the run list"):
        m.summarise(tmp_path, RSCRIPT, [K_UKB])


def test_summarise_raises_on_a_missing_inputs_record(tmp_path):
    _write(tmp_path, "A3_ukb", "asthma.EUR.PYHIN1_1q23", EARLY, EARLY_RDS, inputs=None)
    with pytest.raises(m.MeasurementSetError, match="inputs"):
        m.summarise(tmp_path, RSCRIPT, [K_UKB])


# ---- eligibility table --------------------------------------------------------------------------------

def _measured(key, n, pre, inputs):
    a, t, anc, g = key
    return {"arm": a, "trait": t, "ancestry": anc, "region_safe": g, "status": "too_many_variants",
            "n_variants_pre_ld": pre, "n_variants": n, "cap_stage": "after_ld_restriction", "inputs": inputs}


def _real_measured(n_of=lambda k, nv: nv, pre_of=lambda k, nv: nv + 1):
    nvar = m.panel_n_var()
    return [_measured(k, n_of(k, m._n_var(k, nvar)), pre_of(k, m._n_var(k, nvar)), m.pinned_inputs(k)) for k in
            m.run_list()]


def test_eligibility_table_on_bound_measured_rows():
    rows = m.eligibility_table(_real_measured())
    assert len(rows) == len(m.fit_keys())
    meas = [r for r in rows if r["method"] == "measured"]
    assert len(meas) == len(m.run_list())
    assert all(r["eligible"] == ("true" if int(r["n_variants"]) <= m.CAP else "false") for r in meas)
    assert all(len(r["panel_sha256"]) == 64 for r in rows)


def test_eligibility_table_raises_on_a_missing_key():
    with pytest.raises(m.MeasurementSetError, match="no measurement"):
        m.eligibility_table(_real_measured()[1:])


def test_eligibility_table_raises_on_an_extra_key():
    extra = _measured(("A3_1kg", "bmi", "EUR", "NC_ABO"), 10, 11, SHA)
    with pytest.raises(m.MeasurementSetError, match="not in the run list"):
        m.eligibility_table(_real_measured() + [extra])


def test_eligibility_table_raises_when_n_exceeds_the_panel():
    with pytest.raises(m.BoundViolation, match="panel n_var"):
        m.eligibility_table(_real_measured(n_of=lambda k, nv: nv + 1, pre_of=lambda k, nv: nv + 5))


def test_eligibility_table_raises_when_post_exceeds_pre():
    with pytest.raises(m.BoundViolation, match="n_variants_pre_ld"):
        m.eligibility_table(_real_measured(n_of=lambda k, nv: nv, pre_of=lambda k, nv: nv - 1))


def test_eligibility_table_raises_on_an_input_sha_mismatch():
    ms = _real_measured()
    ms[0] = dict(ms[0], inputs=dict(ms[0]["inputs"], sumstats="0" * 64))
    with pytest.raises(m.InputMismatch, match="sumstats"):
        m.eligibility_table(ms)


# ---- write_tsv ----------------------------------------------------------------------------------------

def test_write_tsv_round_trip(tmp_path):
    out = tmp_path / "t.tsv"
    m.write_tsv([{"a": 1, "b": None}, {"a": "x", "b": 2}], ["a", "b"], out)
    assert out.read_text() == "a\tb\n1\t\nx\t2\n"
    with pytest.raises(ValueError):
        m.write_tsv([{"a": 1, "b": 2, "c": 3}], ["a", "b"], out)


# ---- region-contribution proxy ------------------------------------------------------------------------

@pytest.mark.parametrize("sides, want", [
    ([2, 1], "both_cs"), ([2, 0], "not_both"), ([None, 0], "not_both"), ([None, 3], "unknown"),
    ([1, 1, 1, 0], "not_both"), ([1, 1, None, 1], "unknown"), ([1, 1, 1, 1], "both_cs")])
def test_pair_state(sides, want):
    assert m.pair_state(sides) == want


@pytest.mark.parametrize("states, want", [
    (["both_cs", "unknown", "not_both"], "likely"), (["unknown", "not_both"], "unknown"),
    (["not_both", "not_both"], "unlikely")])
def test_classify_region(states, want):
    assert m.classify_region(states) == want


def test_fit_cs_state_reads_status_before_sets():
    assert m.fit_cs_state({"status": "too_many_variants"}, 0) is None
    assert m.fit_cs_state(None, None) is None
    assert m.fit_cs_state({"status": "ok"}, 2) == 2
    assert m.fit_cs_state({"status": "ok"}, None) == 0     # no $sets: zero credible sets


@pytest.mark.parametrize("stats, want", [
    ([(0.9, 0.1)], "true"), ([(0.1, 0.9)], "true"), ([(0.8, 0.79)], "true"), ([(0.8, 0.8)], "false"),
    ([(0.1, 0.2), (0.95, 0.99)], "false"), ([(0.1, 0.2), (None, 0.9)], "unknown"),
    ([(0.9, 0.1), (None, None)], "true"), ([], "unknown")])
def test_region_discordance(stats, want):
    assert m.region_discordance(stats, 0.8) == want


def test_coloc_stat_is_pp_h4_max_of_a_coloc_susie_output():
    """The run_coloc_pair_r4.R doc contract (estimands.region_stat): only coloc_susie rows are both-have-CS."""
    assert m.coloc_stat({"method": "coloc_susie", "pp_h4_max": 0.9, "pp_h4": 0.1}) == 0.9
    assert m.coloc_stat({"method": "fallback_abf", "pp_h4_max": 0.9, "pp_h4": 0.9}) is None
    assert m.coloc_stat({"method": "none", "pp_h4_max": None}) is None
    assert m.coloc_stat({"method": "coloc_susie", "pp_h4_max": float("nan")}) is None
    assert m.coloc_stat(None) is None


def test_confirmatory_pairs_real_manifest():
    cp = m.confirmatory_pairs()
    assert len(cp) == 10 and all(len(v) == 10 for v in cp.values())
    assert "HLA_6p21" not in cp and "BMI_Xq24" not in cp
    assert sum(any("asthma" in p for p in [pp]) for v in cp.values() for pp in v) == 40


def _fit(root, arm, trait, region, status, n_cs):
    j = root / paths.fit_json(arm, trait, "EUR", region)
    j.parent.mkdir(parents=True, exist_ok=True)
    j.write_text(json.dumps({"status": status}))
    if status not in m.EARLY:
        expr = "list(pip = 1)" if n_cs is None else f"list(sets = list(cs = as.list(seq_len({n_cs}))))"
        subprocess.run([RSCRIPT, "-e", f'saveRDS({expr}, "{root / paths.fit_rds(arm, trait, "EUR", region)}")'],
                       check=True)


def _fixture_repo(tmp_path):
    root = tmp_path / "repo"
    (root / "config/ta_r4").mkdir(parents=True)
    rows = [("R1", "asthma", "bmi"), ("R1", "bmi", "t2d"), ("R1", "bmi", "stroke"),
            ("R2", "bmi", "t2d"), ("R3", "bmi", "t2d")]
    with open(root / m.PAIR_MANIFEST, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["row_id", "ancestry", "region_id", "region_safe", "trait_a", "trait_b", "row_class",
                    "admissible"])
        for g, a, b in rows:
            w.writerow([f"{g}__EUR__{a}_vs_{b}", "EUR", g, g, a, b, "primary", "true"])
        w.writerow(["R9__EUR__bmi_vs_t2d", "EUR", "R9", "R9", "bmi", "t2d", "negative_control", "true"])
    for arm in ("repro_routeC", "repro_k2d_routeC"):
        _fit(root, arm, "asthma", "R1", "ok", 3)
        _fit(root, arm, "bmi", "R1", "ok", 2)
        _fit(root, arm, "t2d", "R1", "ok", 1)
        _fit(root, arm, "stroke", "R1", "ok", None)        # no $sets -> 0
        _fit(root, arm, "bmi", "R2", "too_many_variants", None)
        _fit(root, arm, "t2d", "R2", "ok", 1)
    # R3: no fits at all -> unknown. Coloc: R1 bmi_vs_t2d both sides, opposite of 0.8 -> discordant.
    for arm, pp in (("repro_routeC", 0.95), ("repro_k2d_routeC", 0.3)):
        c = root / m.repro_coloc_json(arm, "R1", "bmi", "t2d")
        c.parent.mkdir(parents=True, exist_ok=True)
        c.write_text(json.dumps({"method": "coloc_susie", "pp_h4_max": pp}))
    return root


def test_fit_states_reads_rds_sets(tmp_path):
    root = _fixture_repo(tmp_path)
    keys = [("repro_routeC", t, "EUR", g) for t, g in
            (("asthma", "R1"), ("stroke", "R1"), ("bmi", "R2"), ("bmi", "R3"))]
    assert m._fit_states(RSCRIPT, keys, root) == {keys[0]: 3, keys[1]: 0, keys[2]: None, keys[3]: None}


def test_region_contribution_proxy_excludes_asthma_and_computes_discordance(tmp_path):
    root = _fixture_repo(tmp_path)
    rows = {(r["region"], r["contrast"]): r for r in m.region_contribution_proxy(RSCRIPT, root)}
    assert set(rows) == {(g, c) for g in ("R1", "R2", "R3") for c in m.PROXY}
    r1 = rows[("R1", "A2_identity_vs_A3_1kg")]
    assert (r1["n_pairs"], r1["n_pairs_asthma_excluded"], r1["n_pairs_both_cs_proxy"], r1["n_pairs_unknown"],
            r1["classification"], r1["discordant_proxy"]) == (3, 1, 1, 0, "likely", "true")
    a1 = rows[("R1", "A1_matched_vs_A3_1kg")]
    assert (a1["classification"], a1["discordant_proxy"]) == ("likely", "unknown")   # no A1 proxy coloc
    assert rows[("R2", "A2_identity_vs_A3_1kg")]["classification"] == "unknown"
    assert rows[("R2", "A2_identity_vs_A3_1kg")]["discordant_proxy"] == "unknown"
    assert rows[("R3", "A1_matched_vs_A3_1kg")]["classification"] == "unknown"
    assert "R9" not in {g for g, _ in rows}


def test_proxy_totals_and_flags():
    rows = [{"region": f"R{i}", "contrast": c, "classification": cl, "discordant_proxy": d}
            for i, (cl, d) in enumerate([("likely", "true")] * 3 + [("unknown", "unknown")] * 2 +
                                        [("unlikely", "false")] * 5) for c in m.PROXY]
    t = m.proxy_totals(rows)
    for c in m.PROXY:
        assert t[c]["likely"] + t[c]["unknown"] + t[c]["unlikely"] == 10
        assert (t[c]["likely"], t[c]["k"]) == (3, "unknown")
    flags = m.proxy_flags(t)
    assert sum(f.startswith("FLAG FOR CARTER: n_regions_min 7 may yield NON_INFORMATIVE") for f in flags) == 2
    # k unknown but bounded: 3 true + 2 unknown = at most 5 < 7 discordant regions -> the k flag still fires
    assert sum("likely discordant regions k <= 5 < 7" in f for f in flags) == 2 and len(flags) == 4
    t_open = m.proxy_totals([dict(r, discordant_proxy="unknown") for r in rows])
    assert not any("discordant" in f for f in m.proxy_flags(t_open))       # 10 unknown: k may reach 7
    t2 = m.proxy_totals([dict(r, discordant_proxy="false" if r["discordant_proxy"] == "unknown" else
                              r["discordant_proxy"]) for r in rows])
    assert t2["A2_identity_vs_A3_1kg"]["k"] == 3
    assert any("likely discordant regions k = 3 < 7" in f for f in m.proxy_flags(t2))


# ---- the real no-fit mode on the tiny e2e fixture -----------------------------------------------------

@pytest.mark.r4_heavy
def test_no_fit_mode_on_the_fixture(tmp_path):
    root = tmp_path / "r"
    root.mkdir()
    build_fixture(root)
    out = "data/r4/tmp/w3f_fixture"
    argv = m.measurement_argv("A3_1kg", TRAIT, ANC, REGION, _cfg("A3_1kg"), out, RSCRIPT, region_id=REGION)
    (root / out / "A3_1kg").mkdir(parents=True)
    _ok(_run(argv, root))
    m.write_inputs_record(argv, root)
    rows = m.summarise(root / out, RSCRIPT, [("A3_1kg", TRAIT, ANC, REGION)])
    assert len(rows) == 1
    r = rows[0]
    assert (r["status"], r["cap_stage"]) == ("too_many_variants", "after_ld_restriction")
    assert 0 < r["n_variants"] <= 60 and r["n_variants_pre_ld"] >= r["n_variants"]
    assert not (root / paths.fit_json("A3_1kg", TRAIT, ANC, REGION)).exists()
    assert not (root / "data/r4/results").exists()
    p = _ok(_run([RSCRIPT, "-e", f'f <- readRDS("{root / out}/A3_1kg/{TRAIT}.{ANC}.{REGION}.fit.rds"); '
                                 'cat(is.null(f$lbf_variable))'], root))
    assert p.stdout.strip().endswith("TRUE")


@pytest.mark.r4_heavy
def test_no_fit_mode_with_zero_panel_overlap_cannot_fit(tmp_path):
    """Review item 4: under cap 0 the post-restriction early exit needs nrow(subset) > 0. A panel that shares no
    variant with the sumstats must stop the script (authoritative declared panel rejected), never fit."""
    root, other = tmp_path / "r", tmp_path / "o"
    root.mkdir(), other.mkdir()
    panel = build_fixture(root)
    build_fixture(other, start=900000)
    shutil.copy2(other / panel, root / panel)
    (root / paths.panel_manifest_path("A3_1kg", ANC)).unlink()
    _write_manifest(root, "A3_1kg", panel, REGION)
    out = "data/r4/tmp/w3f_fixture"
    argv = m.measurement_argv("A3_1kg", TRAIT, ANC, REGION, _cfg("A3_1kg"), out, RSCRIPT, region_id=REGION)
    (root / out / "A3_1kg").mkdir(parents=True)
    p = _run(argv, root)
    assert p.returncode != 0 and "LD_DECLARED_REJECTED" in p.stderr, p.stderr[-2000:]
    assert not (root / out / "A3_1kg" / f"{TRAIT}.{ANC}.{REGION}.fit.rds").exists()
    with pytest.raises(m.MeasurementSetError, match="no measurement"):
        m.summarise(root / out, RSCRIPT, [("A3_1kg", TRAIT, ANC, REGION)])
