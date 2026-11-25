"""r4 production reads the oriented sumstats; the catalogs, the collector audit and the pilots keep their inputs
(W3f 15.8a3; Carter Q-158R2 D, Q-158OR A; DEC-2026-11-25-ta-r4-sumstats-orientation)."""
from __future__ import annotations

import csv
import itertools
import json
import shlex
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

from .conftest import MAN_DIR, REPO_ROOT

from ta_r4 import arms, commands, paths  # noqa: E402

H = "data/processed/sumstats_harmonized"
#: The 8 r4 catalog inputs in collector order (config/pipeline.yaml traits x trait_ancestries), typed from
#: data/r4/tmp/w3f/q158/a3/paths_before.tsv (A3_1kg column at 83e17b38).
SOURCES = [
    "data/r4/sumstats/bmi.EUR.r4_alleles.tsv.bgz", f"{H}/t2d.EUR.tsv.bgz", f"{H}/t2d.AFR.tsv.bgz",
    f"{H}/hypertension.EUR.tsv.bgz", "data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz",
    "data/r4/sumstats/asthma.AFR.grch37_lifted_strand.tsv.bgz", f"{H}/stroke.EUR.tsv.bgz", f"{H}/stroke.AFR.tsv.bgz"]
PAIRS = [("bmi", "EUR"), ("t2d", "EUR"), ("t2d", "AFR"), ("hypertension", "EUR"), ("asthma", "EUR"),
         ("asthma", "AFR"), ("stroke", "EUR"), ("stroke", "AFR")]
#: Every repro arm reads data/processed/sumstats_harmonized/<t>.<a>.tsv.bgz for all 8 pairs (paths_before.tsv).
LEGACY = {p: f"{H}/{p[0]}.{p[1]}.tsv.bgz" for p in PAIRS}
REGION = "FTO_16q12"
SMK = str(Path(sys.executable).parent / "snakemake")


def _prod_problems(argvs):
    """Every sumstats argument that is not an oriented copy, and every argv element under data/processed."""
    bad = []
    for argv in argvs:
        for i, x in enumerate(argv):
            if x.startswith("data/processed"):
                bad.append((argv[:4], x))
            if i and argv[i - 1] in ("--sumstats", "--sumstats-a", "--sumstats-b", "--file") and "sumstats" in x \
                    and ".r4_oriented." not in x:
                bad.append((argv[:4], x))
    return bad


def _rows(anc):
    traits = [t for t, a in PAIRS if a == anc]
    return [{"row_id": f"{REGION}__{anc}__{a}_vs_{b}", "region_safe": REGION, "region_id": REGION, "ancestry": anc,
             "trait_a": a, "trait_b": b} for a, b in itertools.combinations(traits, 2)]


def _cross_purity_sumstats(tmp_path):
    """The fit_sumstats run_aggregation._cross_purity hands the purity runner, for every CROSS_PURITY fit arm."""
    from ta_r4 import run_aggregation as RA

    fits, seen = [], []
    for fit_arm, panel_arm, _ in RA.CROSS_PURITY:
        anc = arms.arm_ancestries(fit_arm)[0]
        for t, a in PAIRS:
            if a != anc:
                continue
            fits.append({"arm": fit_arm, "status": "converged", "trait": t, "ancestry": a, "region_safe": REGION})
            for rel in (paths.fit_rds(fit_arm, t, a, REGION), paths.panel_path(panel_arm, REGION),
                        paths.panel_path(fit_arm, REGION)):
                (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
                (tmp_path / rel).touch()
            js = tmp_path / paths.fit_json(fit_arm, t, a, REGION)
            js.write_text(json.dumps({"variant_catalog_path": str(tmp_path / paths.catalog_path("r4", REGION)),
                                      "ld_file_declared": str(tmp_path / paths.panel_path(fit_arm, REGION))}))

    def runner(repo, rds, panel, allow_absent, *, fit_sumstats, **kw):
        seen.append(str(Path(fit_sumstats).relative_to(tmp_path)))
        return pd.DataFrame()

    RA._cross_purity(tmp_path, pd.DataFrame(fits), runner, final=True)
    assert len(seen) == len(fits) > 0
    return seen


# 1
def test_production_arms_read_only_oriented_sumstats(tmp_path):
    from ta_r4 import measure_fit_eligibility as m
    from ta_r4 import run_qtl_group_r4 as QG

    prod = sorted(arms.production_arms())
    assert len(prod) == 8
    for arm in prod:
        for t, a in PAIRS:
            assert paths.sumstats_path(t, a, arm) == f"data/r4/sumstats/{t}.{a}.r4_oriented.tsv.bgz", (arm, t, a)
    argvs = []
    for arm in prod:
        cfg, anc = m.arm_config(arm), arms.arm_ancestries(arm)[0]
        for t, a in PAIRS:
            if a == anc:
                argvs += [commands.fit_command(arm, t, a, REGION, cfg), commands.verify_command(arm, t, a, REGION)]
        for row in _rows(anc):
            modes = commands.COLOC_MODES if commands.A1_FIT_ARMS.get(arm) == anc else ("susie",)
            for mode in modes:
                argvs += [commands.coloc_command(arm, row, "p12_primary", mode),
                          commands.coloc_verify_command(arm, row, mode)]
    for q in ("QTL_A3", "QTL_A2"):
        assert arms.arm_stage(QG.fit_arm(q)) == "production"
        rows = [{"qtl_row_id": f"{REGION}__EUR__{t}__eqtl__Whole_Blood__g", "region_safe": REGION, "trait": t,
                 "source": "eqtl", "tissue": "Whole_Blood", "qtd": "QTD000356", "gene_id": "g",
                 "molecular_trait_id": "g"} for t, a in PAIRS if a == "EUR"]
        argvs += [QG.abf_command(q, r, REGION, "o.json", 1.0, "qtl_n_cs==0") for r in rows]
        files = QG.group_inputs(q, rows)
        assert sorted(f for f in files if "sumstats" in f) == sorted(
            f"data/r4/sumstats/{t}.EUR.r4_oriented.tsv.bgz" for t, a in PAIRS if a == "EUR")
        argvs.append(files)
    purity = _cross_purity_sumstats(tmp_path)
    assert all(".r4_oriented." in p for p in purity), purity
    argvs.append(purity)
    assert _prod_problems(argvs) == []
    assert sum(".r4_oriented." in x for v in argvs for x in v) > 100


# 2 (characterization: passes on the old code by design; NC (d) is its evidence)
def test_legacy_route_paths_are_unchanged():
    from ta_r4 import run_qtl_group_r4 as QG

    repro = sorted(a for a in arms.ARMS if arms.arm_stage(a) == "repro")
    assert repro == ["repro_k2d_routeC", "repro_k2d_routeL", "repro_routeC", "repro_routeL", "repro_sh2b3_r2"]
    for arm in repro:
        for p in PAIRS:
            assert paths.sumstats_path(*p, arm) == LEGACY[p], (arm, p)
    row = _rows("EUR")[0]
    argv = commands.coloc_command("repro_routeC", row, "p12_primary", "susie")
    assert argv[argv.index("--sumstats-a") + 1] == LEGACY[(row["trait_a"], "EUR")]
    assert argv[argv.index("--sumstats-b") + 1] == LEGACY[(row["trait_b"], "EUR")]
    assert QG.fit_arm("QTL_legacy") == "repro_routeL"
    qrow = {"qtl_row_id": "x", "region_safe": REGION, "trait": "bmi", "source": "eqtl", "tissue": "Whole_Blood",
            "qtd": "QTD000356", "gene_id": "g", "molecular_trait_id": "g"}
    qa = QG.abf_command("QTL_legacy", qrow, REGION, "o.json", 1.0, "qtl_n_cs==0")
    assert qa[qa.index("--sumstats-a") + 1] == LEGACY[("bmi", "EUR")]
    assert [f for f in QG.group_inputs("QTL_legacy", [qrow]) if "sumstats" in f] == [LEGACY[("bmi", "EUR")]]


# 3
def test_catalog_source_paths_equal_the_previous_r4_inputs():
    from ta_r4 import sumstats_orient
    from .test_null_windows_production_pool import PRODUCTION_INPUTS

    assert {paths.catalog_source_sumstats_path(t, a) for t, a in PAIRS} == set(PRODUCTION_INPUTS)
    cfg = yaml.safe_load((REPO_ROOT / "config/pipeline.yaml").read_text())
    order = [(t, a) for t in cfg["traits"] for a in cfg["trait_ancestries"].get(t, [])]
    assert order == PAIRS
    got = [paths.catalog_source_sumstats_path(t, a) for t, a in order]
    assert got == SOURCES == [p for _, _, p in sumstats_orient.CATALOG_SOURCES]
    assert [(t, a) for t, a, _ in sumstats_orient.CATALOG_SOURCES] == PAIRS


# 4 (characterization: the rule reads the sources before and after the edit; NC (b) is its evidence)
@pytest.mark.r4_heavy
def test_catalog_rule_dry_run_reads_the_catalog_sources():
    cfg = ["config/pipeline.yaml", "config/ta_r4/overlay_base.yaml", "config/ta_r4/overlay_repro_routeC.yaml"]
    r = subprocess.run([SMK, "-s", "Snakefile.ta_r4", "-n", "-F", "--printshellcmds", "--configfile", *cfg, "--",
                        paths.catalog_raw_path("NC_ABO")], cwd=REPO_ROOT, capture_output=True, text=True)
    out = r.stdout + r.stderr
    assert r.returncode == 0, out[-2000:]
    lines = [ln for ln in r.stdout.replace("\\\n", " ").splitlines() if "collect_region_variants.py" in ln]
    assert len(lines) == 1, out[-2000:]
    cmd = shlex.split(lines[0])
    i = cmd.index("--harmonized")
    j = cmd.index("--output", i)
    assert cmd[i + 1: j] == SOURCES
    assert ".r4_oriented." not in out


# 5 (characterization: both read the sources before and after the edit; NC (c) and NC (e) are its evidence)
def test_collector_audit_and_asthma_pilot_read_the_catalog_sources():
    from ta_r4 import collector_drop_audit as CDA
    from ta_r4 import measure_fit_eligibility as m

    assert CDA.r4_sumstats(REPO_ROOT) == SOURCES
    assert m.ASTHMA_PILOT_SUMSTATS == "data/r4/sumstats/asthma.EUR.grch37_lifted_strand.tsv.bgz"


# 6
def test_data_sources_record_the_oriented_copies():
    src = yaml.safe_load((REPO_ROOT / "config/ta_r4/data_sources.yaml").read_text())["sources"]
    with open(MAN_DIR / "sumstats_r4_sha256.tsv", newline="") as fh:
        pin = {r["path"]: r["sha256"] for r in csv.DictReader(fh, delimiter="\t")}
    for t, a in PAIRS:
        e = src[f"sumstats_{t}_{a}"]
        o = e["r4_oriented"]
        assert set(o) == {"path", "sha256", "from"}
        assert o["path"] == paths.sumstats_path(t, a, "A3_1kg") == f"data/r4/sumstats/{t}.{a}.r4_oriented.tsv.bgz"
        assert o["sha256"] == pin[o["path"]]
        # the file the copy was made from (the 15.8a2 harmonize report's src): the entry's url, except bmi EUR,
        # whose r4 input is the D-18 restored-allele file, not the url's data/processed file
        assert o["from"] == paths.catalog_source_sumstats_path(t, a)
        assert (o["from"] == e["url"]) is ((t, a) != ("bmi", "EUR"))


def _rebuild(region):
    """collect_variants on the 8 oriented files (collector order) written as collect_region_variants.py writes it,
    then catalog_unique_key as its main() writes the kept and dropped files: (raw, final, dropped) bytes."""
    import io

    from ta_r4 import catalog_unique_key as CUK
    from ta_r4 import verify_inputs as V
    from ta_r4.collector_drop_audit import load_collector, region_window

    inputs = [paths.sumstats_path(t, a, "A3_1kg") for t, a in PAIRS]
    assert all((REPO_ROOT / p).is_file() for p in inputs)  # the collector skips a missing path silently
    V.verify(inputs, [V.SUMSTATS], REPO_ROOT)
    _, chrom, start, end = region_window(region, REPO_ROOT)
    df = load_collector(REPO_ROOT).collect_variants([str(REPO_ROOT / p) for p in inputs], chrom, start, end)
    raw = df.to_csv(sep="\t", index=False)
    kept, dropped, _ = CUK.unique_allele_key(io.StringIO(raw, newline="").readlines())
    drop = CUK.DROPPED_HEADER + "".join(ln.rstrip("\r\n") + f"\t{s}\t{c}\n" for ln, s, c in dropped)
    return raw.encode(), "".join(kept).encode(), drop.encode()


# 7
@pytest.mark.r4_heavy
def test_catalog_is_a_fixed_point_of_the_oriented_inputs():
    region = "NC_ABO"  # fewest input rows of the 31
    raw, final, drop = _rebuild(region)
    assert raw == (REPO_ROOT / paths.catalog_raw_path(region)).read_bytes()
    assert final == (REPO_ROOT / paths.catalog_path("r4", region)).read_bytes()
    assert drop == (REPO_ROOT / paths.catalog_dropped_path(region)).read_bytes()


FIXED_POINT = MAN_DIR / "catalogs_r4_fixed_point.tsv"


# 8
def test_fixed_point_manifest_matches_disk():
    import hashlib

    def sha(rel):
        return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()

    with open(FIXED_POINT, newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    with open(MAN_DIR / "catalogs_sha256.tsv", newline="") as fh:
        final = {r["region_safe"]: r for r in csv.DictReader(fh, delimiter="\t") if r["route"] == "r4"}
    with open(MAN_DIR / "catalogs_r4_unique_key.tsv", newline="") as fh:
        uk = {r["region_safe"]: r for r in csv.DictReader(fh, delimiter="\t")}
    assert len(rows) == 31 and sorted(r["region_safe"] for r in rows) == sorted(final) == sorted(uk)
    for r in rows:
        g = r["region_safe"]
        assert r["equal"] == "true", g
        for k in ("raw", "final", "dropped"):
            assert r[f"{k}_sha256_rebuilt"] == r[f"{k}_sha256_pinned"], (g, k)
        assert r["final_sha256_pinned"] == final[g]["sha256"] == sha(paths.catalog_path("r4", g))
        assert r["raw_sha256_pinned"] == uk[g]["raw_sha256"] == sha(paths.catalog_raw_path(g))
        assert r["dropped_sha256_pinned"] == uk[g]["dropped_sha256"] == sha(paths.catalog_dropped_path(g))
        assert int(r["final_rows"]) == int(final[g]["n_rows"]) == int(uk[g]["n_kept"])
        assert int(r["raw_rows"]) == int(uk[g]["n_raw"])
