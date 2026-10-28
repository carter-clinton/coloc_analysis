"""Fixture builders for the R4 coloc tests (W0d).

build_pair_regions(): two-trait fixture regions at their R4 repo-relative paths under `root`
(panel, bgzipped+tabixed sumstats per trait, catalog, regions CSV, panel manifest, optional A2 payload).
build_toy_workflow(): a make_fixture_repo() git repo with 3 regions, a 3-row pair manifest, a trait manifest,
a lock record + W4b-T3 fixture sign-off (write_fixture_lock). Fixture gate files exist only under tmp_path;
the real repo never gets a hand-made lock record (§B.12).
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ta_r4 import commands, paths

REPO_ROOT = Path(__file__).resolve().parents[3]
RSCRIPT = "/rs1/researchers/c/ckclinto/conda_envs/r_coloc/bin/Rscript"
HTS_BIN = "/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4/55c377a7e8fce799d92381bcc5138d7f_/bin"
PAIR_BUILDER = REPO_ROOT / "tests/ta_r4/fixtures/build_fixture_pair.R"
PAYLOAD = REPO_ROOT / "src/snakemake/scripts/ta_r4/make_matched_identity_payload.R"
FROZEN_REL = "src/legacy/region_analysis/scripts/run_susie_rss.R"
TRAIT_A, TRAIT_B, ANC = "asthma", "bmi", "EUR"
PANEL_HDR = ["ancestry", "region_safe", "path", "md5", "sha256", "size_bytes", "n_var", "n_samples", "build",
             "source", "has_ref_alt"]
REGION_HDR = ["region_id", "ancestry", "chr", "start", "end", "lead_snp", "gene", "trait_list", "source",
              "canonical_pairs"]
PAIR_HDR = ["row_id", "ancestry", "region_id", "region_safe", "trait_a", "trait_b", "row_class", "admissible",
            "inadmissible_reason", "canonical_pair", "nc_set", "nc_caveat"]
GIT_ID = ["-c", "user.name=R4 Fixture", "-c", "user.email=r4-fixture@example.invalid", "-c", "commit.gpgsign=false"]


@dataclass(frozen=True)
class Region:
    region_id: str
    chr: str
    start: int
    seed: int
    a_snpid: str = "rsid"
    b_snpid: str = "chrpos"
    panel_snpid: str = "chrpos"
    b_null: bool = False


def env():
    return dict(os.environ, PATH=f"{Path(RSCRIPT).parent}:{os.environ['PATH']}")


def run(cmd, cwd, **kw):
    return subprocess.run([str(c) for c in cmd], cwd=cwd, env=kw.pop("env", None) or env(), capture_output=True,
                          text=True, **kw)


def ok(p):
    assert p.returncode == 0, f"rc={p.returncode}\nSTDOUT\n{p.stdout[-3000:]}\nSTDERR\n{p.stderr[-3000:]}"
    return p


def pair_row(region_id, region_safe=None, anc=ANC, a=TRAIT_A, b=TRAIT_B):
    rs = region_safe or region_id
    return {"row_id": f"{rs}__{anc}__{a}_vs_{b}", "ancestry": anc, "region_id": region_id, "region_safe": rs,
            "trait_a": a, "trait_b": b, "row_class": "primary", "admissible": "true", "inadmissible_reason": "",
            "canonical_pair": "false", "nc_set": "", "nc_caveat": ""}


def _write_tsv(path, header, rows, delimiter="\t"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, header, delimiter=delimiter)
        w.writeheader()
        w.writerows(rows)


def _manifest_row(root, panel_rel, region_safe):
    data = (root / panel_rel).read_bytes()
    return dict(ancestry=ANC, region_safe=region_safe, path=panel_rel, md5=hashlib.md5(data).hexdigest(),
                sha256=hashlib.sha256(data).hexdigest(), size_bytes=len(data), n_var=60, n_samples=400,
                build="GRCh37", source="fixture", has_ref_alt="true")


def write_trait_manifest(root, sdY_b="1.0", rel=commands.TRAIT_MANIFEST):
    rows = [dict(trait=TRAIT_A, ancestry=ANC, type="cc", sdY="NA", sdY_source="NA", N_median=400),
            dict(trait=TRAIT_B, ancestry=ANC, type="quant", sdY=sdY_b, sdY_source="fixture", N_median=400)]
    _write_tsv(root / rel, ["trait", "ancestry", "type", "sdY", "sdY_source", "N_median"], rows)
    return root / rel


def build_pair_regions(root, regions, fit_arm="A3_1kg", identity_arm=None):
    """Fixture regions (distinct chromosomes, ascending) at their R4 paths under root."""
    root = Path(root)
    tmp = root / "data/r4/tmp/fixture_plain"
    plain = {TRAIT_A: [], TRAIT_B: []}
    manifest = {fit_arm: [], identity_arm: []}
    for r in regions:
        panel = paths.panel_path(fit_arm, r.region_id, ANC)
        pa, pb = tmp / f"{TRAIT_A}.{r.region_id}.tsv", tmp / f"{TRAIT_B}.{r.region_id}.tsv"
        cmd = [RSCRIPT, PAIR_BUILDER, "--panel", root / panel, "--sumstats-a", pa, "--sumstats-b", pb,
               "--catalog", root / paths.catalog_path("r4", r.region_id), "--region-id", r.region_id,
               "--chr", r.chr, "--start", r.start, "--seed", r.seed, "--a-snpid", r.a_snpid,
               "--b-snpid", r.b_snpid, "--panel-snpid", r.panel_snpid, "--trait-a", TRAIT_A, "--trait-b", TRAIT_B]
        ok(run(cmd + (["--b-null"] if r.b_null else []), root))
        plain[TRAIT_A].append(pa)
        plain[TRAIT_B].append(pb)
        manifest[fit_arm].append(_manifest_row(root, panel, r.region_id))
        if identity_arm:
            a2 = paths.panel_path(identity_arm, r.region_id, ANC)
            ok(run([RSCRIPT, PAYLOAD, "--in", root / panel, "--out", root / a2], root))
            manifest[identity_arm].append(_manifest_row(root, a2, r.region_id))
    for trait, parts in plain.items():
        out = root / paths.sumstats_path(trait, ANC, fit_arm)
        out.parent.mkdir(parents=True, exist_ok=True)
        merged = tmp / f"{trait}.merged.tsv"
        with open(merged, "w") as fh:
            for i, p in enumerate(parts):
                lines = p.read_text().splitlines(keepends=True)
                fh.writelines(lines if i == 0 else lines[1:])
        with open(out, "wb") as fh:
            assert subprocess.run([f"{HTS_BIN}/bgzip", "-c", str(merged)], stdout=fh).returncode == 0
        ok(run([f"{HTS_BIN}/tabix", "-f", "-s", "1", "-b", "2", "-e", "2", "-S", "1", out], root))
    for arm, rows in manifest.items():
        if arm:
            _write_tsv(root / paths.panel_manifest_path(arm, ANC), PANEL_HDR, rows)
    _write_tsv(root / paths.regions_csv(), REGION_HDR,
               [dict(region_id=r.region_id, ancestry=ANC, chr=r.chr, start=r.start, end=r.start + 60000,
                     lead_snp="", gene="FIX", trait_list=f"{TRAIT_A};{TRAIT_B}", source="fixture",
                     canonical_pairs="") for r in regions], delimiter=",")
    return root


def link_repo_files(root, arms=("A3_1kg",)):
    """Policy/overlays/priors copied; frozen script, src/python and the R4 scripts dir symlinked."""
    root = Path(root)
    copies = {commands.COLOC_PRIORS, "config/ta_r4/overlay_base.yaml"}
    for arm in arms:
        from ta_r4.arms import ARMS
        copies |= {ARMS[arm]["policy"], f"config/ta_r4/overlay_{arm}.yaml"}
    for rel in sorted(copies):
        if not (root / rel).exists():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO_ROOT / rel, root / rel)
    for rel in (FROZEN_REL, "src/python", "src/snakemake/scripts/ta_r4"):
        link = root / rel
        if not link.exists():
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(REPO_ROOT / rel)
    return root


def fit_arm(root, arm, trait, region, anc=ANC):
    """Receipt, frozen script, validator: the argv r4_run_finemap joins (ta_r4.commands)."""
    from ..conftest import merged_config
    cfg = merged_config("config/ta_r4/overlay_base.yaml", f"config/ta_r4/overlay_{arm}.yaml")
    out = {"receipt": run(commands.receipt_command(arm, trait, anc, region), root),
           "fit": run(commands.fit_command(arm, trait, anc, region, cfg, region_id=region), root),
           "validate": run(commands.validate_command(arm, trait, anc, region), root)}
    for k, p in out.items():
        ok(p)
    return out


def coloc(root, arm, row, p12_key, mode, extra=()):
    """Runs the coloc argv; returns (CompletedProcess, parsed JSON or None)."""
    cmd = commands.coloc_command(arm, row, p12_key, mode) + list(extra)
    p = run(cmd, root)
    out = root / cmd[cmd.index("--output") + 1]
    return p, (json.loads(out.read_text()) if p.returncode == 0 and out.exists() else None)


# --- the W0d unit-test fixture (one build per pytest session, shared by the three coloc modules) -------------

#: SAME: both fits chr:pos-named (direct coloc.susie comparable). MIX: A rsid-named, B chr:pos-named (the
#: run_coloc_susie.R alignment case). NULL: B has no signal. OVR: rsid panel + chr:pos sumstats for B, so the
#: frozen script renames B's variants to panel rsids that no sumstats column carries.
PAIR_REGIONS = (
    Region("FIXP_SAME", "1", 1000, 20261101, a_snpid="chrpos", b_snpid="chrpos"),
    Region("FIXP_MIX", "2", 1000, 20261102, a_snpid="rsid", b_snpid="chrpos"),
    Region("FIXP_NULL", "3", 1000, 20261103, a_snpid="chrpos", b_snpid="chrpos", b_null=True),
    Region("FIXP_OVR", "4", 1000, 20261104, a_snpid="rsid", b_snpid="chrpos", panel_snpid="rsid"),
)


def pair_session_root(tmp_path_factory, with_fits=True):
    name = "w0d_pair_fits" if with_fits else "w0d_pair_light"
    root = tmp_path_factory.getbasetemp() / name
    done = root / ".built"
    if done.exists():
        return root
    root.mkdir(parents=True, exist_ok=True)
    link_repo_files(root)
    build_pair_regions(root, PAIR_REGIONS)
    write_trait_manifest(root)
    if with_fits:
        for r in PAIR_REGIONS:
            for t in (TRAIT_A, TRAIT_B):
                fit_arm(root, "A3_1kg", t, r.region_id)
    done.touch()
    return root


# --- the REQ-SNAKEMAKE-CI toy workflow (W0d Task 2) ----------------------------------------------------------

R4_CONDA_PREFIX = "/rs1/researchers/c/ckclinto/conda_envs/smk_job_envs/ta_r4"
CONDA_BIN = "/rs1/researchers/c/ckclinto/miniconda3/condabin"
TOY_REGIONS = tuple(Region(f"FIX_{k}", str(k), 1000, 20261021 + k, b_null=(k == 3)) for k in (1, 2, 3))
TOY_ARMS = ("A3_1kg", "A2_identity")


def _git(repo, *args):
    r = subprocess.run(["git", *GIT_ID, *args], cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args}: {r.stderr}")
    return r.stdout.strip()


def build_toy_workflow(tmp_path):
    """Fixture repo: 3 regions x 1 pair, A3 panels + A2 payloads, lock record + W4b-T3 fixture sign-off, under tmp_path only."""
    from .make_fixture_repo import make_fixture_repo, write_fixture_lock
    repo = make_fixture_repo(tmp_path)
    link_repo_files(repo, TOY_ARMS)
    build_pair_regions(repo, TOY_REGIONS, fit_arm="A3_1kg", identity_arm="A2_identity")
    _write_tsv(repo / "config/ta_r4/pair_manifest.tsv", PAIR_HDR, [pair_row(r.region_id) for r in TOY_REGIONS])
    write_trait_manifest(repo)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "toy inputs")
    write_fixture_lock(repo)
    return repo


def toy_targets(arm):
    """Fits (2 traits x 3 regions), coloc rows x p12 keys, and A1 matched + allvars in the A3_1kg invocation."""
    fits = [paths.fit_json(arm, t, ANC, r.region_id) for r in TOY_REGIONS for t in (TRAIT_A, TRAIT_B)]
    modes = ["susie"] + (["A1_matched", "A1_allvars"] if arm in commands.A1_FIT_ARMS else [])
    rows = [pair_row(r.region_id) for r in TOY_REGIONS]
    return fits + [commands.coloc_output(arm, row, k, m) for row in rows for k in commands.P12_KEYS for m in modes]


def smk_env():
    condarc = Path(R4_CONDA_PREFIX) / "condarc"
    assert condarc.is_file(), f"{condarc} absent: run bin/r4_fire.sh --show-conda-pkgs-dirs once"
    return dict(os.environ, CONDA_PKGS_DIRS=f"{R4_CONDA_PREFIX}/pkgs", HOME=f"{R4_CONDA_PREFIX}/home",
                CONDARC=str(condarc), PATH=f"{CONDA_BIN}:{os.environ['PATH']}")


def run_toy(repo, arm, targets, *extra, smk):
    cfg = [repo / "config/pipeline.yaml", repo / "config/ta_r4/overlay_base.yaml",
           repo / f"config/ta_r4/overlay_{arm}.yaml"]
    cmd = [smk, "-s", repo / "Snakefile.ta_r4", "-d", repo, "--configfile", *cfg, "--use-conda",
           "--conda-prefix", R4_CONDA_PREFIX, "--conda-frontend", "conda", "--cores", "2", *extra, *targets]
    return run(cmd, repo, env=smk_env())
