"""run_coloc_pair_r4.R (D-01, D-21): coloc.susie, A1 matched, A1 all-variants from one script.

Fits come from the frozen run_susie_rss.R via ta_r4.commands (r4_heavy). A1 all-variants needs no fits.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import shutil
from pathlib import Path

import pytest
import yaml

from .conftest import REPO_ROOT
from .fixtures.build_toy_workflow import (ANC, RSCRIPT, TRAIT_A, TRAIT_B, coloc, ok, pair_row,
                                          pair_session_root, run, write_trait_manifest)

from ta_r4 import commands, paths

ARM = "A3_1kg"
PRI = yaml.safe_load(open(REPO_ROOT / commands.COLOC_PRIORS))
PP = ("pp_h0", "pp_h1", "pp_h2", "pp_h3", "pp_h4")
KEYS = {"row_id", "arm", "mode", "method", "trait_a", "trait_b", "ancestry", "region_id", "type_a", "type_b",
        "sdY_a", "sdY_b", "p12_key", "p1", "p2", "p12", "overlap_min", "trim_by_posterior", "n_cs_a", "n_cs_b",
        "fallback_reason", "n_snps", "variant_set_sha256", *PP, "pp_h4_max", "n_cs_pairs",
        "n_cs_pairs_h4_ge_0.8", "summary", "n_matched_allele", "n_matched_pos_only", "n_allele_mismatch",
        "n_dropped_duplicate", "n_dropped_unusable", "coloc_version", "susieR_version", "R.version.string"}
SAME, MIX, NULL, OVR = (pair_row(r) for r in ("FIXP_SAME", "FIXP_MIX", "FIXP_NULL", "FIXP_OVR"))


@pytest.fixture(scope="module")
def fits(tmp_path_factory):
    return pair_session_root(tmp_path_factory)


@pytest.fixture(scope="module")
def light(tmp_path_factory):
    return pair_session_root(tmp_path_factory, with_fits=False)


def run_ok(root, row, mode, key="p12_primary", extra=()):
    p, d = coloc(root, ARM, row, key, mode, extra)
    ok(p)
    return d


def rjson(root, code):
    p = ok(run([RSCRIPT, "-e", "suppressPackageStartupMessages({library(coloc); library(jsonlite)});" + code], root))
    return json.loads(p.stdout.strip().splitlines()[-1])


def region_rows(root, trait, region_id):
    reg = next(r for r in __import__("csv").DictReader(open(root / paths.regions_csv()))
               if r["region_id"] == region_id)
    with gzip.open(root / paths.sumstats_path(trait, ANC, ARM), "rt") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        rows = [dict(zip(hdr, ln.rstrip("\n").split("\t"))) for ln in fh]
    return [r for r in rows if r["CHR"] == reg["chr"] and int(reg["start"]) <= int(r["POS"]) <= int(reg["end"])]


def fit_names(root, trait, region_id):
    rds = root / paths.fit_rds(ARM, trait, ANC, region_id)
    p = ok(run([RSCRIPT, "-e", f'cat(names(readRDS("{rds}")$pip), sep="\\n")'], root))
    return [x for x in p.stdout.splitlines() if x]


def chrpos_keys(root, trait, region_id):
    """Independent of the script: fit name -> chr:pos via the frozen naming rule (SNP_ID, else CHR:POS)."""
    m = {(r["SNP_ID"] or f"{r['CHR']}:{r['POS']}"): f"{r['CHR']}:{r['POS']}" for r in region_rows(root, trait,
                                                                                                    region_id)}
    return {m[n] for n in fit_names(root, trait, region_id)}


def sha_ids(ids):
    return hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()


# --- coloc.susie ---------------------------------------------------------------------------------------------

@pytest.mark.r4_heavy
def test_susie_equals_direct_coloc_susie(fits):
    d = run_ok(fits, SAME, "susie")
    assert d["method"] == "coloc_susie" and d["fallback_reason"] is None
    assert d["n_cs_a"] == 2 and d["n_cs_b"] == 1
    fa, fb = (fits / paths.fit_rds(ARM, t, ANC, "FIXP_SAME") for t in (TRAIT_A, TRAIT_B))
    direct = rjson(fits, f'r <- coloc.susie(readRDS("{fa}"), readRDS("{fb}"), p1={PRI["p1"]!r}, '
                         f'p2={PRI["p2"]!r}, p12={PRI["p12_primary"]!r}); cat(toJSON(r$summary, digits=NA))')
    mine = {(r["idx1"], r["idx2"]): r for r in d["summary"]}
    assert len(mine) == len(direct) == d["n_cs_pairs"] == 2
    worst = 0.0
    for r in direct:
        m = mine[(r["idx1"], r["idx2"])]
        assert (m["nsnps"], m["hit1"], m["hit2"]) == (r["nsnps"], r["hit1"], r["hit2"])
        for h in range(5):
            worst = max(worst, abs(m[f"PP.H{h}.abf"] - r[f"PP.H{h}.abf"]))
    best = max(direct, key=lambda r: r["PP.H4.abf"])
    print(f"coloc_susie pp_h4_max {d['pp_h4_max']!r} direct {best['PP.H4.abf']!r} max|diff| {worst!r}")
    assert worst <= 1e-12 and abs(d["pp_h4_max"] - best["PP.H4.abf"]) <= 1e-12
    assert [d[k] for k in PP] == [mine[(best["idx1"], best["idx2"])][f"PP.H{h}.abf"] for h in range(5)]
    assert d["n_cs_pairs_h4_ge_0.8"] == sum(r["PP.H4.abf"] >= 0.8 for r in direct)
    keys = chrpos_keys(fits, TRAIT_A, "FIXP_SAME") & chrpos_keys(fits, TRAIT_B, "FIXP_SAME")
    assert d["n_snps"] == len(keys) and d["variant_set_sha256"] == sha_ids(keys)


@pytest.mark.r4_heavy
def test_output_keys_exact(fits, light):
    for root, row, mode in ((fits, SAME, "susie"), (fits, NULL, "susie"), (fits, SAME, "A1_matched"),
                            (light, SAME, "A1_allvars")):
        d = run_ok(root, row, mode)
        assert set(d) == KEYS, (mode, set(d) ^ KEYS)
        assert d["coloc_version"] == "5.2.3" and d["R.version.string"].startswith("R version")


# --- A1 ------------------------------------------------------------------------------------------------------

DIRECT_ABF = '''
ss <- function(p) {{ x <- data.table::fread(cmd = sprintf("gunzip -c %s", shQuote(p))); x[, CHR := as.character(CHR)];
  x <- x[CHR == "{chr}" & POS >= 1000 & POS <= 61000]; x[, SNP_ID := as.character(SNP_ID)];
  x[is.na(SNP_ID) | SNP_ID == "", SNP_ID := sprintf("%s:%s", CHR, POS)]; x[, cp := sprintf("%s:%s", CHR, POS)]; x }}
a <- ss("{sa}"); b <- ss("{sb}")
ka <- a$cp[match(names(readRDS("{fa}")$pip), a$SNP_ID)]; kb <- b$cp[match(names(readRDS("{fb}")$pip), b$SNP_ID)]
k <- sort(intersect(ka, kb), method = "radix"); a <- a[match(k, cp)]; b <- b[match(k, cp)]
d1 <- list(beta = a$BETA, varbeta = a$SE^2, snp = k, type = "cc", N = 400)
d2 <- list(beta = b$BETA, varbeta = b$SE^2, snp = k, type = "quant", sdY = 1.0, N = 400)
e <- coloc.abf(d1, d2, p1 = {p1!r}, p2 = {p2!r}, p12 = {p12!r})$summary
f <- coloc.abf(d1, d2)$summary
cat(toJSON(list(n = length(k), explicit = as.list(e), default = as.list(f)), auto_unbox = TRUE, digits = NA))
'''


@pytest.mark.r4_heavy
def test_a1_matched_is_fit_intersection_and_explicit_prior(fits):
    for key in ("p12_primary", "p12_sensitivity"):
        d = run_ok(fits, MIX, "A1_matched", key)
        assert d["method"] == "A1_abf_matched" and d["n_cs_pairs"] is None
        keys = chrpos_keys(fits, TRAIT_A, "FIXP_MIX") & chrpos_keys(fits, TRAIT_B, "FIXP_MIX")
        assert d["n_snps"] == len(keys) and d["variant_set_sha256"] == sha_ids(keys)
        fa, fb = (fits / paths.fit_rds(ARM, t, ANC, "FIXP_MIX") for t in (TRAIT_A, TRAIT_B))
        sa, sb = (fits / paths.sumstats_path(t, ANC, ARM) for t in (TRAIT_A, TRAIT_B))
        r = rjson(fits, DIRECT_ABF.format(chr="2", sa=sa, sb=sb, fa=fa, fb=fb, p1=PRI["p1"], p2=PRI["p2"],
                                          p12=PRI[key]))
        assert r["n"] == d["n_snps"]
        diff = max(abs(d[f"pp_h{h}"] - r["explicit"][f"PP.H{h}.abf"]) for h in range(5))
        print(f"{key}: A1_matched n_snps {d['n_snps']} pp_h4 {d['pp_h4']!r} direct {r['explicit']['PP.H4.abf']!r} "
              f"max|diff| {diff!r}; package-default pp_h4 {r['default']['PP.H4.abf']!r}")
        assert diff <= 1e-12 and d["pp_h4_max"] == d["pp_h4"]
        if PRI[key] != 1e-5:  # coloc.abf's own default p12 is 1e-5
            assert r["default"]["PP.H4.abf"] != d["pp_h4"]  # negative control: the explicit prior is load-bearing


@pytest.mark.r4_heavy
def test_a1_allvars_superset_of_matched(fits):
    m = run_ok(fits, MIX, "A1_matched")
    a = run_ok(fits, MIX, "A1_allvars")
    assert a["method"] == "A1_abf_allvars" and a["n_snps"] >= m["n_snps"]
    print(f"A1 matched n_snps {m['n_snps']}, allvars n_snps {a['n_snps']}")


def test_a1_allvars_matching_counts(light):
    d = run_ok(light, MIX, "A1_allvars")
    # 60 positions: SNP 12 transposed in B still matches (unordered {REF,ALT}); SNP 20 has no B alleles.
    assert (d["n_snps"], d["n_matched_allele"], d["n_matched_pos_only"], d["n_allele_mismatch"],
            d["n_dropped_duplicate"], d["n_dropped_unusable"]) == (60, 59, 1, 0, 0, 0)
    assert d["n_cs_a"] is None and d["n_cs_b"] is None and d["summary"][0]["nsnps"] == 60
    assert (d["type_a"], d["type_b"], d["sdY_a"], d["sdY_b"]) == ("cc", "quant", None, 1.0)


def test_quant_sdY_is_used(light, tmp_path):
    base = run_ok(light, MIX, "A1_allvars")
    tm = write_trait_manifest(tmp_path, sdY_b="2.0", rel="tm.tsv")
    d = run_ok(light, MIX, "A1_allvars", extra=["--trait-manifest", tm])
    # PP.H4 is saturated on this fixture; sdY scales trait B's ABFs, which moves PP.H0/PP.H1.
    assert d["sdY_b"] == 2.0 and d["pp_h0"] != base["pp_h0"]


@pytest.mark.parametrize("sdY", ["NA", ""])
def test_quant_without_sdY_stops(light, tmp_path, sdY):
    tm = write_trait_manifest(tmp_path, sdY_b=sdY, rel="tm.tsv")
    p, d = coloc(light, ARM, MIX, "p12_primary", "A1_allvars", ["--trait-manifest", tm])
    assert p.returncode != 0 and d is None and "SDY_MISSING" in p.stderr, p.stderr[-800:]


def test_bad_p12_key_and_missing_fit_refused(light):
    cmd = commands.coloc_command(ARM, MIX, "p12_primary", "A1_allvars")
    cmd[cmd.index("--p12-key") + 1] = "p12"
    p = run(cmd, light)
    assert p.returncode != 0 and "P12_KEY" in p.stderr
    cmd = commands.coloc_command(ARM, MIX, "p12_primary", "A1_allvars")
    cmd[cmd.index("--mode") + 1] = "susie"
    p = run(cmd, light)
    assert p.returncode != 0 and "--fit-a" in p.stderr


# --- name alignment ------------------------------------------------------------------------------------------

def _run_legacy_coloc_susie(root, row, tmp_path):
    """run_coloc_susie.R itself on copies of the fits whose sidecar JSON points at a PLAIN sumstats copy:
    its fread() of a .bgz needs R.utils, absent from the named r_coloc env (it would skip the rewrite)."""
    args = []
    for t, flag in ((row["trait_a"], "--fit-a"), (row["trait_b"], "--fit-b")):
        src = root / paths.fit_rds(ARM, t, ANC, row["region_safe"])
        dst = tmp_path / f"{t}.fit.rds"
        shutil.copy2(src, dst)
        side = json.loads((root / paths.fit_json(ARM, t, ANC, row["region_safe"])).read_text())
        plain = tmp_path / f"{t}.tsv"
        with gzip.open(root / side["sumstats"], "rb") as fi, open(plain, "wb") as fo:
            fo.write(fi.read())
        side["sumstats"] = str(plain)
        (tmp_path / f"{t}.json").write_text(json.dumps(side))
        args += [flag, dst]
    out = tmp_path / "legacy.json"
    p = ok(run([RSCRIPT, REPO_ROOT / "src/snakemake/scripts/run_coloc_susie.R", *args, "--pair-id", row["row_id"],
                "--output", out], root))
    line = next(ln for ln in p.stdout.splitlines() if "chr:pos rewrite" in ln)
    return json.loads(out.read_text()), line


@pytest.mark.r4_heavy
def test_align_names_matches_run_coloc_susie(fits, tmp_path):
    """Differential: rsid-named A vs chr:pos-named B. Same priors as run_coloc_susie.R's package defaults."""
    assert PRI["p12_primary"] == 5e-6 and PRI["p1"] == PRI["p2"] == 1e-4
    assert PRI["overlap_min"] == 0.5 and PRI["trim_by_posterior"] is True
    names_a, names_b = fit_names(fits, TRAIT_A, "FIXP_MIX"), fit_names(fits, TRAIT_B, "FIXP_MIX")
    assert names_a[0].startswith("rs") and ":" in names_b[0] and not set(names_a) & set(names_b)
    legacy, line = _run_legacy_coloc_susie(fits, MIX, tmp_path)
    d = run_ok(fits, MIX, "susie")
    print("run_coloc_susie.R:", line.strip(), "| mine n_snps", d["n_snps"])
    assert f"(intersect={d['n_snps']})" in line
    assert legacy["status"] == "success" and len(legacy["susie_pairs"]) == len(d["summary"])
    mine = {(r["idx1"], r["idx2"]): r for r in d["summary"]}
    for r in legacy["susie_pairs"]:
        m = mine[(r["idx1"], r["idx2"])]
        assert (m["nsnps"], m["hit1"], m["hit2"]) == (r["nsnps"], r["hit1"], r["hit2"])
        # run_coloc_susie.R writes jsonlite default digits=4 (5 significant digits): compare at that precision.
        assert all(math.isclose(m[f"PP.H{h}.abf"], r[f"PP.H{h}.abf"], rel_tol=1e-4) for h in range(5))


@pytest.mark.r4_heavy
def test_panel_rsid_override_is_refused_not_dropped(fits, tmp_path):
    """B's fit names are LD-panel rsids that no sumstats column carries. run_coloc_susie.R silently drops every
    such column that no CS references; the R4 script stops instead (fail closed; decision handed off)."""
    names_b = fit_names(fits, TRAIT_B, "FIXP_OVR")
    assert names_b[0].startswith("rs")
    legacy, line = _run_legacy_coloc_susie(fits, OVR, tmp_path)
    print("run_coloc_susie.R on the override shape:", line.strip(), "pairs", legacy.get("n_pairs_total"))
    for mode in ("susie", "A1_matched"):
        p, d = coloc(fits, ARM, OVR, "p12_primary", mode)
        assert p.returncode != 0 and d is None and "UNMAPPED_FIT_NAMES" in p.stderr, p.stderr[-800:]
