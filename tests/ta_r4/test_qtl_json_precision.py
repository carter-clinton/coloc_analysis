"""W3f 15.8c (review R4; DEC-2026-11-24-ta-r4-qtl-json-full-precision-flag; Carter Q-157J R4, Q-158DIG A).

jsonlite's default writes 4 decimals and `digits = NA` 15 significant digits; neither recovers every double (0.8 - 2^-53
is written as 0.8). Under `--json-full-precision true` run_qtl_coloc.R writes `digits = I(17)` (QTL_A3 / QTL_A2 only;
QTL_legacy and Track B keep the default, byte-identical); run_coloc_pair_r4.R writes I(17); simulate_coloc_r4.R writes
its posterior columns with sprintf("%.17g"). A 17-significant-digit token recovers its double exactly, and jsonlite's
I(17) token is the C "%.17g" token, so "written exact" is checked as: every number token t == format(float(t), ".17g").
"""
from __future__ import annotations

import gzip
import json
import os
import subprocess
from pathlib import Path

import pytest

from .conftest import REPO_ROOT
from .fixtures import qtl_group_fixture as QF
from .fixtures.build_toy_workflow import RSCRIPT as PAIR_RSCRIPT
from .fixtures.build_toy_workflow import env as pair_env
from .fixtures.build_toy_workflow import pair_row, pair_session_root
from .test_simulation_harness import _harness, _ok, _read_tsv, fx_root  # noqa: F401  (fx_root is a fixture)

from ta_r4 import commands
from ta_r4 import run_qtl_group_r4 as G

#: DIFFERENTIAL SUBSTRATE: HEAD before 15.8c (data/r4/tmp/w3f/q158/start_15_8c.txt). Never re-pin.
PRE_158C_REF = "4d7419d17ee7a25b457e14dab069d6f8d210323d"
FLAG = "--json-full-precision"
QTL_SCRIPT_REL = "src/snakemake/scripts/run_qtl_coloc.R"
SIM_PP = ("pp_h0", "pp_h1", "pp_h2", "pp_h3", "pp_h4", "pp_h4_max", "r2_causal")

#: Every serializer call in the r4 R scripts and run_qtl_coloc.R, by file and call text (whitespace collapsed), with
#: its class: exact (round-trips every double), thresholded=False (no threshold reads it), track_b_default (the
#: Track-B-shared default path, kept byte-identical). writers_15_8c.tsv holds the measurement.
WRITERS = {
    ("src/snakemake/scripts/run_qtl_coloc.R",
     'write_json(x, path, auto_unbox = TRUE, pretty = TRUE, na = "null", digits = I(17))'): ("exact", 1),
    ("src/snakemake/scripts/run_qtl_coloc.R",
     'write_json(x, path, auto_unbox = TRUE, pretty = TRUE, na = "null")'): ("track_b_default", 1),
    ("src/snakemake/scripts/ta_r4/run_coloc_pair_r4.R",
     'write_json(doc, tmp, auto_unbox = TRUE, digits = I(17), na = "null", null = "null", pretty = TRUE)'): ("exact", 2),
    ("src/snakemake/scripts/ta_r4/simulate_coloc_r4.R",
     'fwrite(tab, tmp, sep = "\\t", append = TRUE, col.names = TRUE, na = "NA", quote = FALSE)'): ("exact", 1),
    ("src/snakemake/scripts/ta_r4/cs_cross_purity.R",
     'write.table(out, tmp, sep = "\\t", quote = FALSE, row.names = FALSE, na = "NA")'): ("thresholded=False", 1),
    ("src/snakemake/scripts/ta_r4/measure_trait_facts.R",
     'fwrite(rbindlist(rows), opt$out, sep = "\\t")'): ("thresholded=False", 1),
}

WRITER_CALLS_R = r'''
fs <- commandArgs(TRUE)
for (f in fs) {
  pd <- getParseData(parse(f, keep.source = TRUE))
  hit <- pd[pd$token == "SYMBOL_FUNCTION_CALL" & pd$text %in% c("write_json", "toJSON", "fwrite", "write.table"), ]
  for (i in seq_len(nrow(hit))) {
    call_id <- pd$parent[pd$id == pd$parent[pd$id == hit$id[i]]]
    cat(f, "\t", gsub("\\s+", " ", getParseText(pd, call_id)), "\n", sep = "")
  }
}
'''

TRACE_R = ('suppressPackageStartupMessages(library(jsonlite)); '
           'trace("write_json", tracer = quote(saveRDS(x, Sys.getenv("WJ_DUMP"))), print = FALSE); '
           'source("__SCRIPT__")__MAIN__')

DOUBLES_R = r'''
num <- function(o) { v <- rapply(o, as.numeric, classes = c("numeric", "integer"), how = "unlist")
                     v <- unname(as.numeric(v)); sort(v[is.finite(v)]) }
x <- readRDS("__DUMP__"); p <- jsonlite::fromJSON("__JSON__", simplifyVector = FALSE)
a <- num(x); b <- num(p)
cat(jsonlite::toJSON(list(n = length(a), same = identical(a, b),
                          n_beyond_15 = sum(signif(a, 15) != a)), auto_unbox = TRUE), "\n")
'''

DEFAULT_OF_FULL_R = r'''
p <- jsonlite::fromJSON("__FULL__", simplifyVector = FALSE)
cat(jsonlite::toJSON(p, auto_unbox = TRUE, pretty = TRUE, na = "null", null = "null"), "\n", file = "__OUT__")
'''

HELPER_R = r'''
suppressPackageStartupMessages(library(jsonlite))
ex <- parse("__SCRIPT__")
def <- Filter(function(e) is.call(e) && identical(e[[1]], as.name("<-")) && identical(e[[2]], as.name("write_result")),
              as.list(ex))
stopifnot(length(def) == 1L)
for (full in c(TRUE, FALSE)) {
  env <- new.env(); env$JSON_FULL_PRECISION <- full
  eval(def[[1]], env)
  env$write_result(list(a = 0.79999, b = 0.8 - 2^-53), sprintf("__OUT__.%s.json", tolower(full)))
}
cat("HELPER_OK\n")
'''


def _sub(code, **kw):
    for k, v in kw.items():
        code = code.replace(f"__{k}__", str(v))
    return code


def _tokens(text):
    """Every number token of a JSON text, raw, in document order (the parser's own tokenization)."""
    out = []

    def keep(s):
        out.append(s)
        return s
    json.loads(text, parse_float=keep, parse_int=keep)
    return out


def _is_17g(t):
    return t == format(float(t), ".17g")


def _tree(text):
    return json.loads(text, parse_float=lambda s: ("num", s), parse_int=lambda s: ("num", s))


def _qrow(trait="tA", feature=QF.FEATURES[0]):
    return {"qtl_row_id": f"{QF.REGION}__EUR__{trait}__eqtl__{QF.TISSUE}__{feature}", "region_safe": QF.REGION,
            "trait": trait, "source": "eqtl", "tissue": QF.TISSUE, "qtd": QF.QTD, "gene_id": feature,
            "molecular_trait_id": feature}


def _qenv(root, extra=None):
    prof = Path(root) / "q158c_seed.Rprofile"
    prof.write_text("set.seed(1L)\n")
    return dict(QF.r_env(), R_PROFILE_USER=str(prof), **(extra or {}))


def _strip(cmd, flag):
    cmd = list(cmd)
    while flag in cmd:
        i = cmd.index(flag)
        del cmd[i:i + 2]
    return cmd


def _set(cmd, flag, value):
    cmd = list(cmd)
    cmd[cmd.index(flag) + 1] = value
    return cmd


def _qrun(root, cmd, script=None, check=True):
    cmd = [QF.RSCRIPT, str(script) if script is not None else cmd[1], *cmd[2:]]
    p = subprocess.run(cmd, cwd=root, env=_qenv(root), capture_output=True, text=True)
    if check:
        assert p.returncode == 0, p.stdout[-2000:] + p.stderr[-3000:]
    return p


def _traced(root, rscript, cmd, dump, main=False, env=None):
    code = _sub(TRACE_R, SCRIPT=cmd[1], MAIN="; main()" if main else "")
    p = subprocess.run([rscript, "-e", code, *cmd[2:]], cwd=root, capture_output=True, text=True,
                       env=dict(env or os.environ, WJ_DUMP=str(dump)))
    assert p.returncode == 0, p.stdout[-2000:] + p.stderr[-3000:]
    out = Path(root) / cmd[cmd.index("--output") + 1]
    assert Path(dump).is_file(), "write_json trace did not fire"
    return out


def _doubles_check(root, rscript, dump, out):
    p = subprocess.run([rscript, "-e", _sub(DOUBLES_R, DUMP=dump, JSON=out)], cwd=root, capture_output=True,
                       text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    return json.loads(p.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def qtl_root(tmp_path_factory):
    return QF.build(tmp_path_factory.mktemp("q158c_qtl") / "root")


@pytest.mark.r4_heavy
def test_flag_rejects_values_other_than_true_false(qtl_root):
    base = G.qtl_command("QTL_A3", _qrow(), "out/flag.json", 1.0)
    assert FLAG in base
    for bad in ("TRUE", "yes", "1", ""):
        p = _qrun(qtl_root, _set(base, FLAG, bad), check=False)
        assert p.returncode != 0, bad
        assert f"{FLAG} must be exactly 'true' or 'false', got '{bad}'" in p.stderr, (bad, p.stderr[-1000:])


@pytest.mark.r4_heavy
def test_default_output_is_byte_identical_to_the_pre_15_8c_script(qtl_root, tmp_path):
    pre_dir = tmp_path / "pre_scripts"
    pre_dir.mkdir()
    for f in (REPO_ROOT / "src/snakemake/scripts").iterdir():
        if f.name != "run_qtl_coloc.R":
            (pre_dir / f.name).symlink_to(f)
    pre = subprocess.run(["git", "show", f"{PRE_158C_REF}:{QTL_SCRIPT_REL}"], cwd=REPO_ROOT, capture_output=True,
                         text=True, check=True).stdout
    assert FLAG not in pre
    (pre_dir / "run_qtl_coloc.R").write_text(pre)
    empty = qtl_root / "out/header_only.harmonized.tsv.gz"  # below the overlap floor: too_few_snps
    empty.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(qtl_root / G.harmonized_path("eqtl", QF.QTD, QF.FEATURES[0], QF.REGION), "rt") as fh:
        hdr = fh.readline()
    with gzip.open(empty, "wt") as fh:
        fh.write(hdr)
    statuses = set()
    for qtl_arm in ("QTL_A3", "QTL_legacy"):
        for tag, feature, qs in (("f1", QF.FEATURES[0], None), ("f2", QF.FEATURES[1], None),
                                 ("floor", QF.FEATURES[0], str(empty.relative_to(qtl_root)))):
            outs = []
            for which, script in (("new", None), ("old", pre_dir / "run_qtl_coloc.R")):
                out = f"out/{which}_{qtl_arm}_{tag}.json"
                cmd = _strip(G.qtl_command(qtl_arm, _qrow(feature=feature), out, 1.0), FLAG)
                if qs is not None:
                    cmd = _set(cmd, "--qtl-sumstats", qs)
                _qrun(qtl_root, cmd, script=script)
                outs.append((qtl_root / out).read_bytes())
            assert outs[0] == outs[1], (qtl_arm, tag)
            statuses.add(json.loads(outs[0])["status"])
    assert statuses == {"success", "no_qtl_cs", "too_few_snps"}


@pytest.mark.r4_heavy
def test_full_precision_round_trips_and_rounds_to_the_default(qtl_root, tmp_path):
    full_cmd = G.qtl_command("QTL_A3", _qrow(), "out/full.json", 1.0)
    assert full_cmd[full_cmd.index(FLAG) + 1] == "true"
    dump = tmp_path / "x.rds"
    full = _traced(qtl_root, QF.RSCRIPT, full_cmd, dump, env=_qenv(qtl_root))
    d = _doubles_check(qtl_root, QF.RSCRIPT, dump, full)
    print("full precision doubles", d)
    assert d["same"] is True and d["n"] > 0 and d["n_beyond_15"] > 0  # parsed values == the R doubles, exactly
    text = full.read_text()
    assert json.loads(text)["status"] == "success"
    assert all(_is_17g(t) for t in _tokens(text))
    _qrun(qtl_root, _strip(_set(full_cmd, "--output", "out/default.json"), FLAG))
    default = (qtl_root / "out/default.json").read_text()
    oracle = tmp_path / "default_of_full.json"  # R's default toJSON of the parsed full output: the 4-decimal rounding
    p = subprocess.run([QF.RSCRIPT, "-e", _sub(DEFAULT_OF_FULL_R, FULL=full, OUT=oracle)], capture_output=True,
                       text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    assert _tree(oracle.read_text()) == _tree(default)
    assert _tokens(oracle.read_text()) == _tokens(default) and _tokens(default) != _tokens(text)


@pytest.mark.r4_heavy
def test_boundary_posteriors_are_not_rounded_onto_the_threshold(tmp_path):
    out = tmp_path / "helper"
    p = subprocess.run([QF.RSCRIPT, "-e", _sub(HELPER_R, SCRIPT=REPO_ROOT / QTL_SCRIPT_REL, OUT=out)],
                       capture_output=True, text=True)
    assert p.returncode == 0 and "HELPER_OK" in p.stdout, p.stderr[-2000:]
    full = json.loads(Path(f"{out}.true.json").read_text())
    assert full["a"] == 0.79999 and full["b"] == 0.8 - 2 ** -53 and full["b"] != 0.8
    default = _tokens(Path(f"{out}.false.json").read_text())
    assert default == ["0.8", "0.8"]  # the default path (QTL_legacy, Track B) rounds both onto 0.8


def test_qtl_command_passes_full_precision_except_legacy():
    for qtl_arm in G.QTL_ARMS:
        cmd = G.qtl_command(qtl_arm, _qrow(), "OUT", 1.0)
        if qtl_arm == "QTL_legacy":
            assert FLAG not in cmd
        else:
            assert cmd.count(FLAG) == 1 and cmd[cmd.index(FLAG) + 1] == "true", qtl_arm
            assert cmd.index(FLAG) + 2 == cmd.index("--qtl-orient"), qtl_arm


@pytest.mark.r4_heavy
def test_qtl_legacy_tiers_input_keeps_4_decimal_posteriors(qtl_root):
    cmd = G.qtl_command("QTL_legacy", _qrow(), "out/legacy_tiers_input.json", 1.0)
    _qrun(qtl_root, cmd)
    text = (qtl_root / "out/legacy_tiers_input.json").read_text()
    assert json.loads(text)["status"] == "success"
    toks = _tokens(text)
    frac = [t.lower().split("e")[0].partition(".")[2] for t in toks]
    assert toks and max(len(f) for f in frac) == 4, toks  # 4 decimals reached, never more
    assert any(not _is_17g(t) for t in toks)


@pytest.fixture(scope="module")
def pair_fits(tmp_path_factory):
    return pair_session_root(tmp_path_factory)


@pytest.mark.r4_heavy
def test_r4_pair_and_simulation_writers_round_trip(pair_fits, qtl_root, fx_root, tmp_path):  # noqa: F811
    # trait-pair mode (run_coloc_pair_r4.R main)
    cmd = commands.coloc_command("A3_1kg", pair_row("FIXP_SAME"), "p12_primary", "susie")
    assert cmd[1] == commands.COLOC_SCRIPT
    dump = tmp_path / "pair.rds"
    out = _traced(pair_fits, PAIR_RSCRIPT, cmd, dump, main=True, env=pair_env())
    # --mode qtl_abf (run_coloc_pair_r4.R qtl_abf_main)
    qcmd = G.abf_command("QTL_A3", _qrow(), QF.REGION, "out/abf.json", 1.0, "qtl_n_cs==0")
    qdump = tmp_path / "abf.rds"
    qout = _traced(qtl_root, QF.RSCRIPT, qcmd, qdump, main=True, env=QF.r_env())
    for root, rs, dmp, o in ((pair_fits, PAIR_RSCRIPT, dump, out), (qtl_root, QF.RSCRIPT, qdump, qout)):
        d = _doubles_check(root, rs, dmp, o)
        print(o.name, d)
        assert d["same"] is True and d["n"] > 0 and d["n_beyond_15"] > 0, o
        assert all(_is_17g(t) for t in _tokens(o.read_text())), o
    # the simulation table
    sim = tmp_path / "sim.tsv"
    _ok(_harness(fx_root, "SH2B3_12q24", "H4", "gen_ukb", sim))
    _, cols, rows = _read_tsv(sim)
    vals = [r[c] for r in rows for c in SIM_PP if r[c] != "NA"]
    assert vals and all(_is_17g(v) for v in vals), [v for v in vals if not _is_17g(v)][:5]
    assert any(float(format(float(v), ".15g")) != float(v) for v in vals)


def test_every_r4_writer_is_classified():
    files = sorted(str(p.relative_to(REPO_ROOT)) for p in (REPO_ROOT / "src/snakemake/scripts/ta_r4").glob("*.R"))
    files.append(QTL_SCRIPT_REL)
    p = subprocess.run([QF.RSCRIPT, "-e", WRITER_CALLS_R, *files], cwd=REPO_ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    found = {}
    for ln in p.stdout.splitlines():
        f, call = ln.split("\t", 1)
        found[(f, call.strip())] = found.get((f, call.strip()), 0) + 1
    unclassified = sorted(set(found) - set(WRITERS))
    assert not unclassified, unclassified
    assert {k: n for k, (_, n) in WRITERS.items()} == found
    assert {c for c, _ in WRITERS.values()} <= {"exact", "thresholded=False", "track_b_default"}
