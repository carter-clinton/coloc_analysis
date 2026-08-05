"""tests/m3/test_ld_allele_aware_wiring.py -- 260805-o7o Task 2 (FINDING H, wiring half).

THE FLAG IS DECLARED, RENDERED, STRICTLY PARSED **AND CONSUMED**.

WHY WIRING AND CONSUMPTION ARE ONE MODULE. 260805-23d split them across two
commits and produced a one-commit BLOCKER-B transient: ``--ld-authoritative`` was
declared, rendered by ``finemap.smk`` and strictly parsed by the R script -- and
then NOT PASSED to ``load_ld_matrix``, so the formal's default silently applied
to every ancestry and the real script opened ``EUR_ukbb_pub`` under
``--ld-authoritative false``. ``[[feedback_declared_input_is_not_the_read_path]]``
in its exact dual: a parsed flag that nothing reads. The proof for consumption
therefore lives in a FULL-SCRIPT run, never in a ``load_ld_matrix()`` unit test.

TRACK A IS IN SUBMISSION. EUR invariance is proven with ``identical()`` on the
ENTIRE ``load_ld_matrix`` result object. ``ld_status`` and
``ld_overlap_fraction`` are explicitly DISQUALIFIED as evidence: m3-04c measured
EUR numerics moving (r[1,2] 0.1 -> 0.9, credible sets 3 -> 10, nonzero PIPs
200 -> 78) while BOTH of those fields stayed BYTE-IDENTICAL.

NO-SKIP RULE (must_have A6): ``_require_m3_r_toolchain()`` ERRORS rather than
skipping when the m3-r-ld marker env is present.
"""
from __future__ import annotations

import copy
import gzip
import json
import random
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from test_stitch_subregions_to_rds import (  # noqa: E402
    R_SUBPROCESS_TIMEOUT_S,
    _loader_functions_only,
    _require_m3_r_toolchain,
)
from test_ld_allele_aware_join import (  # noqa: E402
    BASE_POS,
    CHROM,
    PRE_CHANGE_REF,
    PROJECT_ROOT,
    SUSIE_R,
    SUSIE_R_REL,
    _pre_change_loader_prefix,
    _render_preamble,
    _run_r,
)

sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))
from ld_read_path import ld_allele_aware, ld_file_authoritative  # noqa: E402

FINEMAP_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "finemap.smk"
SCHEMA = PROJECT_ROOT / "src" / "snakemake" / "schemas" / "pipeline.schema.yaml"
PIPELINE_YAML = PROJECT_ROOT / "config" / "pipeline.yaml"
SNAKEMAKE_BIN = Path("/rs1/researchers/c/ckclinto/conda_envs/smoke_dev/bin/snakemake")

E2E_REGION = "FTO_16q12"
N_E2E = 300


@pytest.fixture(scope="session")
def r_toolchain() -> tuple[Path, dict]:
    return _require_m3_r_toolchain()


# ==========================================================================
# A -- the resolver: the allow-list AND the sub-key, both required
# ==========================================================================
_SHIPPED = yaml.safe_load(PIPELINE_YAML.read_text())


def test_shipped_config_arms_afr_and_not_eur_or_trans():
    """A1. THE SHIPPED-CONFIG GUARD. The real ``config/pipeline.yaml`` must
    render ``"true"`` for AFR and ``"false"`` for EUR / TRANS, so the shipped
    config cannot silently drift to disabled (or, worse, to enabled for a
    manuscript ancestry) without this going red.

    NEGATIVE CONTROL (in-test): the same assertion against a copy with
    ``allele_aware`` REMOVED must be ``"false"`` -- proving A1 is observing the
    sub-key and not just the allow-list.
    """
    assert ld_allele_aware("AFR", _SHIPPED) == "true", (
        "the shipped config no longer arms the allele-aware join for AFR -- "
        "finding H is re-opened for every AFR region"
    )
    assert ld_allele_aware("EUR", _SHIPPED) == "false"
    assert ld_allele_aware("TRANS", _SHIPPED) == "false"
    # ...and the 260805-23d flag is untouched by this change
    assert ld_file_authoritative("AFR", _SHIPPED) == "true"
    assert ld_file_authoritative("EUR", _SHIPPED) == "false"

    # NEGATIVE CONTROL
    stripped = copy.deepcopy(_SHIPPED)
    stripped["ld_read_path"].pop("allele_aware")
    assert ld_allele_aware("AFR", stripped) == "false", (
        "removing allele_aware from the block did NOT flip AFR to false -- A1 "
        "is passing off the allow-list alone and the sub-key is dead"
    )
    assert ld_file_authoritative("AFR", stripped) == "true", (
        "removing allele_aware also disarmed 260805-23d's authoritative "
        "mandate -- the two levers are not independent"
    )


@pytest.mark.parametrize(
    "block,ancestry,expected",
    [
        ({"enabled": True, "ancestries": ["AFR"], "allele_aware": True}, "AFR", "true"),
        ({"enabled": True, "ancestries": ["AFR"], "allele_aware": True}, "EUR", "false"),
        ({"enabled": True, "ancestries": ["AFR"], "allele_aware": True}, "TRANS", "false"),
        # block absent
        (None, "AFR", "false"),
        # enabled: false
        ({"enabled": False, "ancestries": ["AFR"], "allele_aware": True}, "AFR", "false"),
        # ancestries: []
        ({"enabled": True, "ancestries": [], "allele_aware": True}, "AFR", "false"),
        # sub-key absent
        ({"enabled": True, "ancestries": ["AFR"]}, "AFR", "false"),
        # sub-key explicitly false
        ({"enabled": True, "ancestries": ["AFR"], "allele_aware": False}, "AFR", "false"),
        # truthy-but-not-True must NOT arm it: the flag decides which LD row a z
        # binds to, so "1" / "yes" are not silently promoted
        ({"enabled": True, "ancestries": ["AFR"], "allele_aware": "true"}, "AFR", "false"),
        ({"enabled": True, "ancestries": ["AFR"], "allele_aware": 1}, "AFR", "false"),
        # malformed block
        ({"enabled": True, "ancestries": 7, "allele_aware": True}, "AFR", "false"),
    ],
)
def test_resolver_fail_safe_direction_is_change_nothing(block, ancestry, expected):
    """A2. Every uncertain answer resolves to ``"false"`` -- LEGACY, change
    nothing. The fail-safe is CALLER-relative and for this caller it means the
    join must not move.

    The parametrisation includes BOTH polarities, so "always false" cannot pass.
    """
    config = {} if block is None else {"ld_read_path": block}
    assert ld_allele_aware(ancestry, config) == expected


def test_resolver_returns_a_string_not_a_bool():
    """A3. The value is interpolated straight into ``run_finemap``'s shell, so
    it must be the literal ``"true"`` / ``"false"`` a shell can carry -- not a
    Python bool that would render as ``True``/``False`` and make the R script's
    strict parser ``stop()``."""
    v = ld_allele_aware("AFR", _SHIPPED)
    assert isinstance(v, str) and v in ("true", "false"), repr(v)


# ==========================================================================
# B -- the schema entry
# ==========================================================================
def test_schema_declares_allele_aware_as_a_boolean():
    """B1. ``src/snakemake/schemas/pipeline.schema.yaml`` must type the key.

    ⚠ FACT CORRECTION vs the plan, recorded here rather than absorbed. The plan
    (Task 2 STEP 3, ``<behavior>``, threat T-o7o-08) states that WITHOUT this
    entry ``snakemake --list`` dies at ``validate()``. MEASURED: it does NOT.
    ``additionalProperties: false`` is set only at the TOP LEVEL of the schema
    (``:431``); the ``ld_read_path`` object declares none of its own, so
    JSON-Schema's permissive default applies to its SUB-keys and an undeclared
    ``allele_aware`` validates fine. The 260805-23d precedent was different --
    ``ld_read_path`` was a new TOP-LEVEL key, which the top-level rule really
    does reject (verified: an undeclared top-level key gives
    ``ValidationError: Additional properties are not allowed``, rc 1).

    So the entry is load-bearing for a DIFFERENT reason, and that is what this
    test pins: it TYPES the key, so a non-boolean value is rejected. Its
    negative control is
    ``test_schema_entry_is_what_rejects_a_non_boolean_allele_aware``.
    """
    schema = yaml.safe_load(SCHEMA.read_text())
    block = schema["properties"]["ld_read_path"]
    assert block["properties"]["allele_aware"]["type"] == "boolean"
    assert schema.get("additionalProperties") is False, (
        "the top-level additionalProperties guard is gone; a typo'd top-level "
        "config key would now be accepted silently"
    )


@pytest.mark.skipif(not SNAKEMAKE_BIN.exists(), reason="smoke_dev snakemake absent")
def test_snakemake_list_succeeds_on_the_shipped_config_and_every_overlay(tmp_path):
    """B2. ``snakemake --list`` exits 0 on ``config/pipeline.yaml`` AND on every
    ``config/pipeline_lsweep_L*_overlay.yaml``. This is the ONLY thing that
    exercises ``validate()`` -- no other unit test does.

    NEGATIVE CONTROL: ``test_schema_entry_is_what_rejects_a_non_boolean_allele_aware``
    below drives the SAME command to a non-zero exit, so "it always passes"
    cannot satisfy this.
    """
    proc = subprocess.run(
        [str(SNAKEMAKE_BIN), "--snakefile", "Snakefile", "--list"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=600,
    )
    assert proc.returncode == 0, (
        f"snakemake --list failed on the shipped config:\n{proc.stderr[-3000:]}"
    )
    overlays = sorted(PROJECT_ROOT.glob("config/pipeline_lsweep_L*_overlay.yaml"))
    assert overlays, "no lsweep overlays found -- the overlay half is vacuous"
    for overlay in overlays:
        p = subprocess.run(
            [str(SNAKEMAKE_BIN), "--snakefile", "Snakefile",
             "--configfile", str(overlay), "--list"],
            cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=600,
        )
        assert p.returncode == 0, (
            f"snakemake --list failed on {overlay.name}:\n{p.stderr[-3000:]}"
        )


@pytest.mark.skipif(not SNAKEMAKE_BIN.exists(), reason="smoke_dev snakemake absent")
def test_schema_entry_is_what_rejects_a_non_boolean_allele_aware(tmp_path):
    """B3 (NEGATIVE CONTROL for B1/B2, PERMANENT and in-suite).

    Runs the REAL ``validate()`` twice over a copy of the shipped config in
    which ``allele_aware`` is the string ``"not-a-boolean"``:

      * WITH the schema entry  -> ValidationError, ``is not of type 'boolean'``
      * WITHOUT it             -> silently accepted

    That difference IS the entry's value, and it is observed rather than argued.
    Uses ``snakemake.utils.validate`` directly so nothing is written into the
    working tree.
    """
    from snakemake.utils import validate as sm_validate  # noqa: PLC0415

    schema = yaml.safe_load(SCHEMA.read_text())
    config = copy.deepcopy(_SHIPPED)
    config["ld_read_path"]["allele_aware"] = "not-a-boolean"

    good = tmp_path / "with_entry.yaml"
    good.write_text(yaml.safe_dump(schema))
    with pytest.raises(Exception) as excinfo:
        sm_validate(copy.deepcopy(config), str(good))
    assert "boolean" in str(excinfo.value), str(excinfo.value)[:400]

    stripped = copy.deepcopy(schema)
    stripped["properties"]["ld_read_path"]["properties"].pop("allele_aware")
    bad = tmp_path / "without_entry.yaml"
    bad.write_text(yaml.safe_dump(stripped))
    # no raise -- the entry is what does the rejecting
    sm_validate(copy.deepcopy(config), str(bad))


# ==========================================================================
# C -- finemap.smk wiring, with a git-show negative control
# ==========================================================================
def _strip_comments(block: str) -> str:
    return "\n".join(
        ln for ln in block.splitlines() if not ln.strip().startswith("#")
    )


def _assert_smk_wiring(src: str) -> None:
    """Every SOURCE-LEVEL wiring claim of Task 2, as one reusable predicate, so
    the PERMANENT negative control can run the IDENTICAL assertions against
    ``git show 0378ec8:`` and be seen to fail."""
    assert re.search(r"^from ld_read_path import \(", src, re.M), "import block gone"
    assert re.search(r"^\s+ld_allele_aware,\s*$", src, re.M), (
        "finemap.smk does not import ld_allele_aware"
    )
    assert re.search(
        r"ld_allele_aware=lambda wildcards: ld_allele_aware\(", src), (
        "run_finemap.params does not compute ld_allele_aware"
    )
    stripped = _strip_comments(src)
    n = stripped.count("--ld-allele-aware {params.ld_allele_aware}")
    assert n == 1, (
        f"--ld-allele-aware {{params.ld_allele_aware}} appears {n} times in the "
        "comment-stripped shell block; expected exactly 1"
    )
    for key in ("ld_allele_exact", "ld_allele_flipped",
                "ld_allele_dropped_palindromic", "ld_allele_dropped_mismatch",
                "ld_allele_dropped_ambiguous", "ld_allele_dropped_unusable",
                "ld_allele_catalog_join"):
        assert f"d.get('{key}')" in stripped, (
            f"the per-region receipt does not read {key} -- a write-only counter "
            "is not observability"
        )


def test_finemap_smk_declares_renders_and_reads_the_flag():
    """C. The rule imports the resolver, computes ``params.ld_allele_aware``,
    renders it into the shell EXACTLY once, and reads all eight new JSON fields
    back out into the per-region receipt.

    NEGATIVE CONTROL (PERMANENT): the identical predicate against ``0378ec8``
    must FAIL.
    """
    _assert_smk_wiring(FINEMAP_SMK.read_text())

    proc = subprocess.run(
        ["git", "show", f"{PRE_CHANGE_REF}:src/snakemake/rules/finemap.smk"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    with pytest.raises(AssertionError):
        _assert_smk_wiring(proc.stdout)


def test_region_id_param_is_byte_unchanged():
    """C2. ``run_finemap.params.region_id`` is pinned by
    ``tests/m3/test_occlusion_lockstep_wiring.py`` and sits IMMEDIATELY adjacent
    to the ``params:`` lines Task 2 edits. It must not move by so much as a
    character.
    """
    proc = subprocess.run(
        ["git", "diff", PRE_CHANGE_REF, "--",
         "src/snakemake/rules/finemap.smk"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    offending = [ln for ln in proc.stdout.splitlines()
                 if ln.startswith(("+", "-")) and "region_id=lambda" in ln]
    assert not offending, f"params.region_id appears in the diff: {offending}"
    assert ("        region_id=lambda wildcards: REGION_SAFE_TO_ID[wildcards.region],"
            in FINEMAP_SMK.read_text())


# ==========================================================================
# D -- the R script: declaration, STRICT parse, and the sole call site
# ==========================================================================
def _assert_r_wiring(src: str) -> None:
    assert 'make_option("--ld-allele-aware"' in src, (
        "run_susie_rss.R's option_list must declare --ld-allele-aware"
    )
    assert re.search(
        r'stop\(sprintf\("--ld-allele-aware must be true\|false', src), (
        "--ld-allele-aware is not STRICTLY parsed"
    )
    # the sole call site threads it through, on ONE line, with ld_file LAST
    assert re.search(
        r"load_ld_matrix\([^\n]*authoritative\s*=\s*ld_authoritative[^\n]*"
        r"allele_aware\s*=\s*ld_allele_aware[^\n]*ld_file\s*=\s*opt\$`ld-file`",
        src), (
        "the sole load_ld_matrix call site must pass allele_aware = "
        "ld_allele_aware BETWEEN authoritative and ld_file, on one line -- "
        "without it the flag is parsed and then ignored (the 260805-23d "
        "BLOCKER-B transient, repeated)"
    )
    # the flip, and its length guard
    assert "LD_ALLELE_ORIENT_LENGTH_MISMATCH:" in src
    assert re.search(r"subset\[, z := z \* ld_result\$allele_orient\]", src)


def test_r_script_declares_parses_and_threads_the_flag():
    """D. NEGATIVE CONTROL (PERMANENT): the identical predicate against
    ``0378ec8`` must FAIL."""
    _assert_r_wiring(SUSIE_R.read_text())
    proc = subprocess.run(
        ["git", "show", f"{PRE_CHANGE_REF}:{SUSIE_R_REL}"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    with pytest.raises(AssertionError):
        _assert_r_wiring(proc.stdout)


def test_preexisting_call_site_regexes_still_match():
    """D2. The two SINGLE-LINE regexes pre-existing suites pin the call site
    with must still match after a third named argument was inserted. Asserted
    here explicitly as well as by running those modules, because a broken regex
    would otherwise surface as an unrelated-looking failure two suites away.
    """
    src = SUSIE_R.read_text()
    assert re.search(r"load_ld_matrix\([^\n]*ld_file\s*=\s*opt\$`ld-file`", src), (
        "test_ld_read_path.py:298's regex no longer matches"
    )
    assert re.search(
        r"load_ld_matrix\([^\n]*authoritative\s*=\s*ld_authoritative[^\n]*"
        r"ld_file\s*=\s*opt\$`ld-file`", src), (
        "test_ld_declared_authoritative.py:436's regex no longer matches"
    )
    sig = re.search(r"load_ld_matrix\s*<-\s*function\s*\(([^)]*)\)", src)
    assert sig is not None, "the signature regex (no parens in defaults) broke"
    params = [p.split("=")[0].strip() for p in sig.group(1).split(",")]
    assert params[-1] == "ld_file", params
    assert "allele_aware" in params, params


# ==========================================================================
# E -- FULL-SCRIPT: the flag is CONSUMED and z ACTUALLY flips
# ==========================================================================
#: The panel correlation used by every end-to-end fixture: AR(1), rho 0.6. A
#: NON-trivial structure on purpose -- against an identity R the fitted numbers
#: would not depend on the z signs at all and every consumption assertion below
#: would be vacuous.
_AR1_RHO = 0.6


def _ar1_consistent_z(n: int, peak: int, amp: float = 6.0) -> list[float]:
    """A z profile that is CONSISTENT with the AR(1) panel: one signal at
    ``peak`` decaying along the LD band. ``estimate_s_rss`` scores such a vector
    as near-zero mismatch, so any orientation error against it is visible."""
    return [amp * (_AR1_RHO ** abs(i - peak)) for i in range(1, n + 1)]


def _make_e2e_inputs(tmp_path: Path, *, ref: str = "A", alt: str = "G",
                     betas: list[float] | None = None) -> dict:
    """The minimum REAL inputs run_susie_rss.R needs, WITH REF/ALT.

    Mirrors ``test_ld_declared_authoritative.py::_make_full_script_inputs``
    (gzip .tsv.bgz -- the script reads it with ``gunzip -c``; a 4-column regions
    CSV; the REAL config/susie_policy.yaml; no --variant-list) and adds the
    REF/ALT columns the allele-aware join needs. The coordinates are driven by
    the SAME BASE_POS / CHROM the R preamble uses, so panel-vs-sumstats overlap
    is controlled purely by the panel.
    """
    root = tmp_path / "e2e"
    root.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20260805)
    rows = ["\t".join(("SNP_ID", "CHR", "POS", "REF", "ALT", "BETA", "SE", "N"))]
    for i in range(1, N_E2E + 1):
        # a deterministic, decidedly non-zero effect so z is large and its SIGN
        # is unambiguous in every downstream number
        beta = betas[i - 1] if betas is not None else 0.05 + rng.random() * 0.05
        rows.append("\t".join((
            f"rs{i}", CHROM, str(BASE_POS + i), ref, alt,
            f"{beta:.8f}", "0.020000", "100000",
        )))
    sumstats = root / "sumstats.tsv.bgz"
    with gzip.open(sumstats, "wt") as fh:
        fh.write("\n".join(rows) + "\n")
    regions_csv = root / "regions.csv"
    regions_csv.write_text(
        "region_id,chr,start,end\n"
        f"{E2E_REGION},{CHROM},{BASE_POS},{BASE_POS + 100000}\n"
    )
    return {"root": root, "sumstats": sumstats, "regions_csv": regions_csv}


def _run_full_script(rscript: Path, env: dict, inputs: dict, out_json: Path, *,
                     ancestry: str, authoritative: str, allele_aware: str | None,
                     ld_dir: Path, ld_file: Path | str | None,
                     ) -> subprocess.CompletedProcess:
    cmd = [
        str(rscript), str(SUSIE_R),
        "--sumstats", str(inputs["sumstats"]),
        "--trait", "TEST_TRAIT",
        "--ancestry", ancestry,
        "--method", "susie_rss",
        "--region", E2E_REGION,
        "--regions-csv", str(inputs["regions_csv"]),
        "--ld-dir", str(ld_dir),
        "--ld-authoritative", authoritative,
        "--policy", str(PROJECT_ROOT / "config" / "susie_policy.yaml"),
        "--output", str(out_json),
    ]
    if allele_aware is not None:
        cmd += ["--ld-allele-aware", allele_aware]
    if ld_file is not None:
        cmd += ["--ld-file", str(ld_file)]
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=R_SUBPROCESS_TIMEOUT_S, env=env,
                          cwd=str(PROJECT_ROOT))


def _build_e2e_panel(rscript: Path, env: dict, tmp_path: Path, path: Path,
                     *, ref: str, alt: str, name: str,
                     transpose_odd: bool = False) -> None:
    """A full-width panel over the e2e coordinates with the given panel-side
    REF/ALT, and a NON-TRIVIAL correlation structure (an AR(1) band) so the
    fitted numbers genuinely depend on the z signs.

    ``transpose_odd`` swaps REF/ALT on the ODD-indexed panel rows only, giving a
    MIXED-orientation panel. That mixture is load-bearing: ``estimate_s_rss`` is
    exactly invariant to a GLOBAL sign flip (``s(z, R) == s(-z, R)``), so an
    all-transposed fixture cannot discriminate consumption from non-consumption
    at all -- measured, 6.4741e-09 with the flag on AND off.
    """
    swap = (
        'odd <- which(i %% 2L == 1L)\n'
        'refv[odd] <- "__ALT__"; altv[odd] <- "__REF__"\n'
    ).replace("__REF__", ref).replace("__ALT__", alt) if transpose_odd else ""
    body = (
        f'n <- {N_E2E}L\n'
        'i <- seq_len(n)\n'
        f'R <- outer(i, i, function(a, b) {_AR1_RHO} ^ abs(a - b))\n'
        'diag(R) <- 1\n'
        f'refv <- rep("{ref}", n); altv <- rep("{alt}", n)\n'
        + swap +
        'variants <- data.frame(\n'
        '  SNP_ID = paste(CHROM, BASE_POS + i, refv, altv, sep = ":"),\n'
        '  CHR = rep(CHROM, n), POS = BASE_POS + i,\n'
        '  REF = refv, ALT = altv,\n'
        '  stringsAsFactors = FALSE)\n'
        f'dir.create(dirname("{path}"), recursive = TRUE, showWarnings = FALSE)\n'
        'saveRDS(list(R = R, variants = variants, status = "ld_loaded"), '
        f'"{path}")\n'
        'cat("PANEL=ok\\n")\n'
    )
    _run_r(rscript, env, tmp_path, body, name=name)


def test_full_script_consumes_the_flag_and_actually_flips_z(r_toolchain, tmp_path):
    """E. THE CONSUMPTION PROOF, at the level that ships.

    THE FIXTURE IS BUILT BACKWARDS FROM THE TRUTH, on purpose. A z profile
    ``z_pan`` that is CONSISTENT with the AR(1) panel is chosen first; then the
    ODD-indexed panel rows are transposed and the sumstats BETA is written as
    ``z_pan * orient * SE``. So the sumstats are a faithful record of a real
    study whose alleles disagree with the panel on half the variants, and:

      false -> the legacy CHR:POS match() binds every variant and the fit runs
               on the MIS-SIGNED z -- a mirrored LD structure, no error, no flag
      true  -> the 4-key match negates the transposed half, recovering z_pan

    ⚠ A MIXED orientation is REQUIRED. ``estimate_s_rss`` is exactly invariant
    to a GLOBAL sign flip (``s(z, R) == s(-z, R)``), so an all-transposed
    fixture cannot discriminate consumption from non-consumption. Measured on
    exactly that fixture: 6.4741e-09 with the flag ON and 6.4741e-09 with it
    OFF. The mixture is what makes this test able to fail.

    The discriminator is NOT a path string a receipt could mislabel. It is
    ``d3b_ld_z_consistency_s`` -- ``susieR::estimate_s_rss(z, R, n)``, the Zou
    2022 z-vs-LD consistency scalar, computed FROM the z vector the fit used and
    the canonical measure of exactly the allele-flip/encoding failure this
    change exists to close. ``ld_allele_flipped`` is asserted too, but as the
    label, not as the evidence.
    """
    rscript, env = r_toolchain
    # z_pan is LD-consistent; the odd panel rows are transposed, so the SUMSTATS
    # z for those rows is the negation of the panel-coded value.
    z_pan = _ar1_consistent_z(N_E2E, peak=N_E2E // 2)
    se = 0.02
    betas = [
        z * (-1.0 if i % 2 == 1 else 1.0) * se
        for i, z in enumerate(z_pan, start=1)
    ]
    inputs = _make_e2e_inputs(tmp_path, ref="A", alt="G", betas=betas)
    ld_dir = inputs["root"] / "ld_reference"
    declared = ld_dir / "AFR_aou" / "m2_region_00040__sub14.rds"
    _build_e2e_panel(rscript, env, tmp_path, declared, ref="A", alt="G",
                     name="tE_panel.R", transpose_odd=True)

    def _run(tag, aware):
        out = inputs["root"] / f"{tag}.json"
        proc = _run_full_script(rscript, env, inputs, out, ancestry="AFR",
                               authoritative="true", allele_aware=aware,
                               ld_dir=ld_dir, ld_file=declared)
        assert proc.returncode == 0, f"[{tag}] rc={proc.returncode}\n{proc.stderr}"
        assert out.exists(), f"[{tag}] no JSON written"
        return json.loads(out.read_text())

    off = _run("aware_false", "false")
    on = _run("aware_true", "true")

    # both opened the SAME declared panel with the SAME overlap -- so nothing
    # below can be explained by a different panel or a different variant set
    assert off["ld_matrix"] == on["ld_matrix"] == str(declared)
    assert off["ld_overlap"] == on["ld_overlap"] == N_E2E, (
        off["ld_overlap"], on["ld_overlap"]
    )

    # the counters: not measured vs measured
    assert off["ld_allele_aware"] is False
    assert off["ld_allele_flipped"] is None, off["ld_allele_flipped"]
    assert on["ld_allele_aware"] is True
    assert on["ld_allele_flipped"] == N_E2E // 2, on["ld_allele_flipped"]
    assert on["ld_allele_exact"] == N_E2E // 2, on["ld_allele_exact"]

    # THE REAL DISCRIMINATOR -- a number the fit was computed from
    s_off = off["d3b_ld_z_consistency_s"]
    s_on = on["d3b_ld_z_consistency_s"]
    assert isinstance(s_off, (int, float)) and isinstance(s_on, (int, float)), (
        s_off, s_on
    )
    assert abs(s_off - s_on) > 1e-6, (
        f"estimate_s_rss is IDENTICAL with the flag on and off "
        f"({s_off} vs {s_on}) -- the z vector did not change, so the flag is "
        "declared, rendered, parsed and NOT CONSUMED (the 260805-23d "
        "BLOCKER-B transient repeated)"
    )
    assert s_on < s_off, (
        f"flipping z did not IMPROVE z-vs-LD consistency (s {s_off} -> {s_on}); "
        "on an all-transposed fixture the flip must reduce the estimate_s "
        "mismatch, so the sign convention is inverted"
    )
    # the fit itself moved
    assert off["d1_zscore_sanity"]["lambda_gc"] == pytest.approx(
        on["d1_zscore_sanity"]["lambda_gc"]), (
        "lambda_gc uses z^2 and must be INVARIANT to a sign flip -- if it moved, "
        "the flip changed magnitudes, not just signs"
    )


def test_full_script_stops_on_a_bad_allele_aware_value(r_toolchain, tmp_path):
    """E2. ``--ld-allele-aware wobble`` is a non-zero exit with a named message,
    the same strictness ``--ld-authoritative`` carries. Asserted with a REAL
    invocation, not by reading the parser.

    NEGATIVE CONTROL (in-test): the same invocation with ``false`` exits 0.
    """
    rscript, env = r_toolchain
    inputs = _make_e2e_inputs(tmp_path)
    ld_dir = inputs["root"] / "ld_reference"
    declared = ld_dir / "AFR_aou" / "p.rds"
    _build_e2e_panel(rscript, env, tmp_path, declared, ref="A", alt="G",
                     name="tE2_panel.R")

    bad = _run_full_script(rscript, env, inputs, inputs["root"] / "bad.json",
                          ancestry="AFR", authoritative="true",
                          allele_aware="wobble", ld_dir=ld_dir, ld_file=declared)
    assert bad.returncode != 0, (
        "an unrecognised --ld-allele-aware value ran to completion -- a typo "
        "would silently decide which LD row every z binds to"
    )
    assert "--ld-allele-aware must be true|false" in bad.stderr, bad.stderr
    assert not (inputs["root"] / "bad.json").exists()

    ok = _run_full_script(rscript, env, inputs, inputs["root"] / "ok.json",
                         ancestry="AFR", authoritative="true",
                         allele_aware="false", ld_dir=ld_dir, ld_file=declared)
    assert ok.returncode == 0, ok.stderr


def test_both_ld_flags_parse_in_the_same_argv(r_toolchain, tmp_path):
    """E3. ``--ld-authoritative`` and ``--ld-allele-aware`` coexist in ONE argv
    and BOTH bind their own value -- asserted EMPIRICALLY over all four
    combinations rather than by reasoning about R optparse's long-option
    abbreviation rules. Neither name is a prefix of the other, but that is a
    claim about optparse, and this arc has been burned by reasoned claims.
    """
    rscript, env = r_toolchain
    inputs = _make_e2e_inputs(tmp_path)
    ld_dir = inputs["root"] / "ld_reference"
    declared = ld_dir / "AFR_aou" / "declared.rds"
    dirpanel = ld_dir / "AFR" / f"{E2E_REGION}.rds"
    _build_e2e_panel(rscript, env, tmp_path, declared, ref="A", alt="G",
                     name="tE3_d.R")
    _build_e2e_panel(rscript, env, tmp_path, dirpanel, ref="A", alt="G",
                     name="tE3_p.R")

    seen = {}
    for auth in ("true", "false"):
        for aware in ("true", "false"):
            out = inputs["root"] / f"{auth}_{aware}.json"
            proc = _run_full_script(rscript, env, inputs, out, ancestry="AFR",
                                   authoritative=auth, allele_aware=aware,
                                   ld_dir=ld_dir, ld_file=declared)
            assert proc.returncode == 0, (
                f"auth={auth} aware={aware} rc={proc.returncode}\n{proc.stderr}"
            )
            d = json.loads(out.read_text())
            seen[(auth, aware)] = (d["ld_matrix"], d["ld_allele_aware"])

    for (auth, aware), (matrix, flag) in seen.items():
        assert flag is (aware == "true"), (
            f"--ld-allele-aware {aware} bound {flag} when --ld-authoritative "
            f"was {auth}: the two flags are cross-talking"
        )
        expected = str(declared) if auth == "true" else str(dirpanel)
        assert matrix == expected, (
            f"--ld-authoritative {auth} opened {matrix} (expected {expected}) "
            f"when --ld-allele-aware was {aware}"
        )


# ==========================================================================
# F -- TRACK A: EUR INVARIANCE, identical() on the WHOLE result object
# ==========================================================================
def test_eur_result_object_is_identical_to_pre_change(r_toolchain, tmp_path):
    """F. THE MANUSCRIPT-PROTECTING PROOF. Track A is in submission.

    ``identical()`` on the ENTIRE ``load_ld_matrix`` result object, HEAD source
    vs ``git show 0378ec8:`` source, on the SAME EUR fixture, with the flag
    rendered ``false`` (which is what ``ld_allele_aware("EUR", shipped_config)``
    returns -- asserted here, from the real config, not assumed).

    ``ld_status`` and ``ld_overlap_fraction`` are NOT the evidence: m3-04c
    proved EUR numerics move while both stay byte-identical.

    NEGATIVE CONTROL (in-test): the SAME comparison on an AFR fixture with
    ``allele_aware = TRUE`` must be FALSE -- proving the comparison can detect a
    difference at all. Without it, ``identical()`` would be satisfied by a
    comparison that is blind.
    """
    rscript, env = r_toolchain
    # the flag EUR would actually be rendered, read from the shipped config
    assert ld_allele_aware("EUR", _SHIPPED) == "false"
    assert ld_allele_aware("TRANS", _SHIPPED) == "false"

    pre = _pre_change_loader_prefix(tmp_path)
    cur = _loader_functions_only(tmp_path)
    ld_dir = tmp_path / "ld_reference"
    eur = ld_dir / "EUR" / f"{E2E_REGION}.rds"
    afr = ld_dir / "AFR_aou" / "m2.rds"
    body = (
        'n <- 300L\ni <- seq_len(n)\n'
        'R <- outer(i, i, function(a, b) 0.6 ^ abs(a - b)); diag(R) <- 1\n'
        'mkv <- function(ref, alt) data.frame(\n'
        '  SNP_ID = paste0("rs", i), CHR = rep(CHROM, n), POS = BASE_POS + i,\n'
        '  REF = rep(ref, n), ALT = rep(alt, n), stringsAsFactors = FALSE)\n'
        'sv <- function(p, v) { dir.create(dirname(p), recursive = TRUE,\n'
        '  showWarnings = FALSE); saveRDS(list(R = R, variants = v,\n'
        '  status = "ld_loaded"), p) }\n'
        f'sv("{eur}", mkv("A", "G"))\n'
        f'sv("{afr}", mkv("G", "A"))\n'
        'sub <- mkv("A", "G")\n'
        f'source("{cur}"); new_load <- load_ld_matrix\n'
        f'source("{pre}"); old_load <- load_ld_matrix\n'
        # EUR, exactly as finemap.smk would render it off the allow-list
        f'a <- new_load("{ld_dir}", "EUR", "{E2E_REGION}", sub,'
        ' authoritative = FALSE, allele_aware = FALSE)\n'
        f'b <- old_load("{ld_dir}", "EUR", "{E2E_REGION}", sub,'
        ' authoritative = FALSE)\n'
        'cat(sprintf("EUR_IDENTICAL=%s\\n", identical(a, b)))\n'
        'cat(sprintf("EUR_SOURCE=%s\\n", a$source))\n'
        'cat(sprintf("EUR_OVERLAP=%s\\n", a$overlap))\n'
        'cat(sprintf("EUR_R12=%.6f\\n", a$R[1, 2]))\n'
        # ...and EUR under the shipped authoritative regime, still identical
        f'a2 <- new_load("{ld_dir}", "EUR", "{E2E_REGION}", sub,'
        f' authoritative = FALSE, allele_aware = FALSE, ld_file = "{afr}")\n'
        f'b2 <- old_load("{ld_dir}", "EUR", "{E2E_REGION}", sub,'
        f' authoritative = FALSE, ld_file = "{afr}")\n'
        'cat(sprintf("EUR_DECL_IDENTICAL=%s\\n", identical(a2, b2)))\n'
        # NEGATIVE CONTROL -- AFR with the flag ON must DIFFER
        f'c1 <- new_load("{ld_dir}", "AFR", "m2", sub, authoritative = TRUE,'
        f' allele_aware = TRUE, ld_file = "{afr}")\n'
        f'c0 <- old_load("{ld_dir}", "AFR", "m2", sub, authoritative = TRUE,'
        f' ld_file = "{afr}")\n'
        'cat(sprintf("AFR_IDENTICAL=%s\\n", identical(c1, c0)))\n'
        'cat(sprintf("AFR_FLIPPED=%s\\n", c1$allele_counts$flipped))\n'
    )
    vals = _run_r(rscript, env, tmp_path, body, name="tF.R", loader_funcs=cur)

    assert vals["EUR_IDENTICAL"] == "TRUE", (
        "the EUR result object is NOT identical() to the pre-change loader's. "
        "Track A is in submission and this is the containment that protects it."
    )
    assert vals["EUR_DECL_IDENTICAL"] == "TRUE", (
        "EUR with a declared --ld-file present is not identical() to "
        "pre-change -- the containment leaks when EUR_ukbb_pub/ lands"
    )
    assert vals["EUR_SOURCE"] == str(eur)
    assert vals["EUR_OVERLAP"] == "300"

    # NEGATIVE CONTROL
    assert vals["AFR_IDENTICAL"] == "FALSE", (
        "identical() returned TRUE for AFR under allele_aware = TRUE -- the "
        "comparison cannot observe a difference at all and the EUR proof above "
        "is vacuous"
    )
    assert vals["AFR_FLIPPED"] == "300", vals["AFR_FLIPPED"]


def test_orient_length_guard_aborts_rather_than_mis_signing(r_toolchain, tmp_path):
    """G. The length guard in ``run_susie_rss.R``. If ``allele_orient`` is ever
    out of step with the shrunk ``subset``, the script must ``stop()`` with a
    greppable prefix rather than recycle the vector and mis-sign an arbitrary
    subset of z-scores (R recycles silently, which is exactly how this would
    ship undetected).

    OBSERVED by driving the guard directly with a deliberately short vector --
    a real R invocation with a real non-zero exit, not a source grep.

    NEGATIVE CONTROL (in-test): the same block with a correctly-sized vector
    runs past the guard and applies the flip.
    """
    rscript, env = r_toolchain
    src = SUSIE_R.read_text()
    m = re.search(
        r"if \(isTRUE\(ld_allele_aware\) && !is\.null\(ld_result\$allele_orient\)\) \{.*?\n\}",
        src, re.S)
    assert m is not None, "the orientation-flip block was not found in the source"
    guard = m.group(0)

    def _probe(orient_len: int, tag: str):
        body = (
            'suppressPackageStartupMessages(library(data.table))\n'
            'ld_allele_aware <- TRUE\n'
            'opt <- list(region = "R1", ancestry = "AFR")\n'
            'subset <- data.table(z = as.numeric(1:10))\n'
            f'ld_result <- list(allele_orient = rep(-1, {orient_len}))\n'
            + guard + "\n"
            f'cat(sprintf("{tag}_Z=%s\\n", paste(subset$z, collapse = ",")))\n'
        )
        script = tmp_path / f"tG_{tag}.R"
        script.write_text(_render_preamble(_loader_functions_only(tmp_path))
                          + "\n" + body)
        return subprocess.run([str(rscript), str(script)], capture_output=True,
                              text=True, timeout=R_SUBPROCESS_TIMEOUT_S, env=env)

    bad = _probe(7, "BAD")
    assert bad.returncode != 0, (
        "a 7-long orientation vector against a 10-row subset did NOT abort -- R "
        "recycled it and mis-signed 3 z-scores silently"
    )
    assert "LD_ALLELE_ORIENT_LENGTH_MISMATCH:" in bad.stderr, bad.stderr
    assert "orient=7" in bad.stderr and "subset=10" in bad.stderr, bad.stderr

    # NEGATIVE CONTROL -- correctly sized: runs, and the flip is applied
    good = _probe(10, "GOOD")
    assert good.returncode == 0, good.stderr
    assert "GOOD_Z=-1,-2,-3,-4,-5,-6,-7,-8,-9,-10" in good.stdout, good.stdout


# ==========================================================================
# H -- the variant-catalog join
# ==========================================================================
def test_variant_catalog_join_is_allele_keyed_under_the_flag(r_toolchain, tmp_path):
    """H. The SECOND join site. Under ``--ld-allele-aware true`` the variant
    catalog is joined on CHR/POS/REF/ALT and the regime is recorded in
    ``ld_allele_catalog_join``.

    Fixture: a catalog whose alleles DISAGREE with the sumstats at 100 of the
    300 positions. Allele-keyed -> those 100 do not join. Position-keyed (the
    legacy branch) -> they do.

    NEGATIVE CONTROL (in-test): the byte-identical invocation with the flag
    ``false`` keeps all 300 and records ``chr_pos``.
    """
    rscript, env = r_toolchain
    inputs = _make_e2e_inputs(tmp_path, ref="A", alt="G")
    ld_dir = inputs["root"] / "ld_reference"
    declared = ld_dir / "AFR_aou" / "p.rds"
    _build_e2e_panel(rscript, env, tmp_path, declared, ref="A", alt="G",
                     name="tH_panel.R")

    catalog = inputs["root"] / "variants.tsv"
    lines = ["\t".join(("CHR", "POS", "REF", "ALT", "SNP_ID"))]
    for i in range(1, N_E2E + 1):
        ref, alt = ("C", "T") if i > 200 else ("A", "G")
        lines.append("\t".join((CHROM, str(BASE_POS + i), ref, alt, f"rs{i}")))
    catalog.write_text("\n".join(lines) + "\n")

    def _run(tag, aware):
        out = inputs["root"] / f"{tag}.json"
        cmd = [
            str(rscript), str(SUSIE_R),
            "--sumstats", str(inputs["sumstats"]), "--trait", "T",
            "--ancestry", "AFR", "--method", "susie_rss",
            "--region", E2E_REGION, "--regions-csv", str(inputs["regions_csv"]),
            "--ld-dir", str(ld_dir), "--ld-file", str(declared),
            "--ld-authoritative", "true", "--ld-allele-aware", aware,
            "--variant-list", str(catalog),
            "--policy", str(PROJECT_ROOT / "config" / "susie_policy.yaml"),
            "--output", str(out),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=R_SUBPROCESS_TIMEOUT_S, env=env,
                              cwd=str(PROJECT_ROOT))
        assert proc.returncode == 0, f"[{tag}] {proc.stderr}"
        return json.loads(out.read_text())

    on = _run("cat_true", "true")
    off = _run("cat_false", "false")

    assert on["ld_allele_catalog_join"] == "allele_key", on["ld_allele_catalog_join"]
    assert on["ld_overlap"] == 200, (
        f"the allele-keyed catalog join kept {on['ld_overlap']} variants; the "
        "100 allele-disagreeing rows should not have joined"
    )
    # NEGATIVE CONTROL
    assert off["ld_allele_catalog_join"] in ("snp_id", "chr_pos"), (
        off["ld_allele_catalog_join"]
    )
    assert off["ld_overlap"] == 300, (
        f"the legacy catalog join kept {off['ld_overlap']}; if it were already "
        "allele-aware the assertion above would be vacuous"
    )


def test_unusable_catalog_alleles_skip_the_restriction_rather_than_degrade(
    r_toolchain, tmp_path
):
    """H2. ``collect_region_variants.py:86-88`` fills ``"N"`` when a trait lacks
    alleles. Under the flag that must SKIP the catalog restriction entirely --
    NOT fall back to the SNP_ID / CHR:POS branches, which is finding H's defect
    applied to the catalog. The catalog is an optional restriction and the panel
    join now does the real allele-aware work, so not restricting is the
    conservative direction.

    NEGATIVE CONTROL (in-test): the same catalog with USABLE alleles takes the
    allele-key branch, so "always skip" cannot pass.
    """
    rscript, env = r_toolchain
    inputs = _make_e2e_inputs(tmp_path, ref="A", alt="G")
    ld_dir = inputs["root"] / "ld_reference"
    declared = ld_dir / "AFR_aou" / "p.rds"
    _build_e2e_panel(rscript, env, tmp_path, declared, ref="A", alt="G",
                     name="tH2_panel.R")

    def _catalog(path: Path, ref: str, alt: str, n: int):
        lines = ["\t".join(("CHR", "POS", "REF", "ALT", "SNP_ID"))]
        for i in range(1, n + 1):
            lines.append("\t".join((CHROM, str(BASE_POS + i), ref, alt, f"rs{i}")))
        path.write_text("\n".join(lines) + "\n")

    n_cat = 150
    nfilled = inputs["root"] / "variants_N.tsv"
    usable = inputs["root"] / "variants_ok.tsv"
    _catalog(nfilled, "N", "N", n_cat)
    _catalog(usable, "A", "G", n_cat)

    def _run(tag, catalog):
        out = inputs["root"] / f"{tag}.json"
        cmd = [
            str(rscript), str(SUSIE_R),
            "--sumstats", str(inputs["sumstats"]), "--trait", "T",
            "--ancestry", "AFR", "--method", "susie_rss",
            "--region", E2E_REGION, "--regions-csv", str(inputs["regions_csv"]),
            "--ld-dir", str(ld_dir), "--ld-file", str(declared),
            "--ld-authoritative", "true", "--ld-allele-aware", "true",
            "--variant-list", str(catalog),
            "--policy", str(PROJECT_ROOT / "config" / "susie_policy.yaml"),
            "--output", str(out),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=R_SUBPROCESS_TIMEOUT_S, env=env,
                              cwd=str(PROJECT_ROOT))
        assert proc.returncode == 0, f"[{tag}] {proc.stderr}"
        return json.loads(out.read_text()), proc.stderr

    skipped, stderr = _run("cat_N", nfilled)
    assert skipped["ld_allele_catalog_join"] == "skipped_alleles_unusable", (
        skipped["ld_allele_catalog_join"]
    )
    assert skipped["variant_catalog_attempted"] is True
    assert skipped["variant_catalog_used"] is False
    assert "LD_ALLELE_CATALOG_SKIPPED:" in stderr, stderr
    assert skipped["ld_overlap"] == N_E2E, (
        f"the catalog was skipped but the subset was still restricted to "
        f"{skipped['ld_overlap']} -- it degraded rather than skipped"
    )

    # NEGATIVE CONTROL
    kept, _ = _run("cat_ok", usable)
    assert kept["ld_allele_catalog_join"] == "allele_key", (
        kept["ld_allele_catalog_join"]
    )
    assert kept["ld_overlap"] == n_cat, kept["ld_overlap"]


# ==========================================================================
# I -- the counted JSON: NA vs 0
# ==========================================================================
_COUNTER_KEYS = (
    "ld_allele_exact", "ld_allele_flipped", "ld_allele_dropped_ambiguous",
    "ld_allele_dropped_palindromic", "ld_allele_dropped_mismatch",
    "ld_allele_dropped_unusable",
)


def test_counters_are_null_when_not_measured_and_integers_when_measured(
    r_toolchain, tmp_path
):
    """I. ``null`` (not measured -- EUR / TRANS) must be distinguishable from
    ``0`` (measured, and the join was clean). A field that can only ever hold
    one value is not observability.

    Both polarities are asserted in ONE test, so "always null" and "always 0"
    both fail.
    """
    rscript, env = r_toolchain
    inputs = _make_e2e_inputs(tmp_path, ref="A", alt="G")
    ld_dir = inputs["root"] / "ld_reference"
    declared = ld_dir / "AFR_aou" / "p.rds"
    _build_e2e_panel(rscript, env, tmp_path, declared, ref="A", alt="G",
                     name="tI_panel.R")

    def _run(tag, aware):
        out = inputs["root"] / f"{tag}.json"
        proc = _run_full_script(rscript, env, inputs, out, ancestry="AFR",
                               authoritative="true", allele_aware=aware,
                               ld_dir=ld_dir, ld_file=declared)
        assert proc.returncode == 0, proc.stderr
        return json.loads(out.read_text())

    off = _run("i_off", "false")
    on = _run("i_on", "true")

    for k in _COUNTER_KEYS:
        assert off[k] is None, (
            f"{k} is {off[k]!r} under allele_aware = false; it must be null so a "
            "reader can tell 'not measured' from 'measured zero'"
        )
        assert isinstance(on[k], int), f"{k} is {on[k]!r} under allele_aware = true"
    # a CLEAN join: measured, and legitimately zero
    assert on["ld_allele_exact"] == N_E2E
    assert on["ld_allele_flipped"] == 0
    assert on["ld_allele_dropped_palindromic"] == 0
    assert on["ld_allele_dropped_mismatch"] == 0
    # the regime string is present on BOTH
    assert off["ld_allele_catalog_join"] == "none"
    assert on["ld_allele_catalog_join"] == "none"
    assert off["ld_allele_aware"] is False and on["ld_allele_aware"] is True


def test_finding_j_early_exit_writers_are_left_open(r_toolchain, tmp_path):
    """I2. The ``no_variants`` / ``too_many_variants`` early-exit writers emit NO
    LD keys at all. That is blast-radius FINDING J and it is DELIBERATELY LEFT
    OPEN by this plan (hard rule 10).

    Asserted explicitly so the residual is VISIBLE in the suite rather than
    discovered later as a surprise empty column, and so nobody "fixes" it here
    by accident.
    """
    rscript, env = r_toolchain
    inputs = _make_e2e_inputs(tmp_path)
    # a region far from the sumstats coordinates -> zero variants
    inputs["regions_csv"].write_text(
        "region_id,chr,start,end\n"
        f"{E2E_REGION},{CHROM},1,2\n"
    )
    ld_dir = inputs["root"] / "ld_reference"
    out = inputs["root"] / "nov.json"
    proc = _run_full_script(rscript, env, inputs, out, ancestry="AFR",
                           authoritative="true", allele_aware="true",
                           ld_dir=ld_dir, ld_file=None)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(out.read_text())
    assert payload["status"] == "no_variants", payload["status"]
    for k in _COUNTER_KEYS + ("ld_allele_aware", "ld_allele_catalog_join",
                              "ld_matrix", "ld_authoritative"):
        assert k not in payload, (
            f"{k} appeared in a no_variants JSON. That is finding J being "
            "closed, which this plan explicitly does NOT do -- if it is now "
            "intended, say so in the SUMMARY rather than letting it land here."
        )
