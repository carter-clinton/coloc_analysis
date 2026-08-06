"""tests/m3/test_qtl_coloc_ld_resolution.py -- 260805-w7u Task 1 (FINDING E, path half).

ONE RESOLVER DECIDES THE COLOC LD PATH.

WHY THIS MODULE EXISTS. ``m3-04c-BLAST-RADIUS.md:141`` gate row "Any GWAS x QTL
colocalization", finding **E**: ``qtl_coloc.smk`` is the ONE LD consumer that was
never crosswalked. Measured at ``7b1025d``::

    grep -cE "CURATED_TO_M2|resolve_ld_path|ld_read_path|curated_to_m2" \\
        src/snakemake/rules/qtl_coloc.smk   ->   0

So an AFR GWAS fit produced on the AoU panel would be colocalized against the
*1kG* LD matrix inside one ``coloc.susie`` -- two different LD panels inside a
single posterior, with nothing to say so.

WHAT IS PINNED HERE
-------------------
1. ``ld_coloc_applies`` is the SINGLE gate for BOTH halves of the remedy (the
   resolver route here, the allele join in Task 2). Two independent levers would
   permit the state *resolution ON / join OFF* -- silently-wrong LD traded for
   silently-no LD. Every degraded config shape resolves to **False** = CHANGE
   NOTHING (``[[feedback_failsafe_default_is_caller_relative]]``).
2. OFF the allow-list ``_qtl_coloc_ld_input`` returns a string
   **character-for-character** equal to ``7b1025d``'s -- and that is asserted
   DIFFERENTIALLY, by extracting and executing ``7b1025d``'s real function out of
   ``git show``, never by re-typing its expression here. A test that compares an
   implementation against a hand-copy of itself is a vacuous assertion wearing a
   green check (``[[feedback_green_assertion_needs_a_negative_control]]``).
3. ON the allow-list the answer is ``==`` the string ``finemap.smk``'s
   ``ld_matrix`` lambda produces for the same (region, ancestry). That lambda is
   likewise EXTRACTED from the real ``finemap.smk`` text and evaluated, not
   re-typed -- otherwise "one crosswalk object" would be an assertion about a
   copy.
4. With the gate ON and no panel on disk the input function **raises**
   ``FileNotFoundError`` naming the region. That is the same property
   ``finemap.smk`` already has, and it is LOUD -- which is the point: finding E's
   remedy must not trade a silently-wrong panel for a silently-absent one.
5. The manifest can no longer supply a competing path for a gated ancestry: the
   builder emits ``RESOLVED_BY_LD_PANEL_RESOLVER``, a value that is deliberately
   **not path-shaped** so any other reader (``plan_ld_builds.py:238``,
   ``fine_mapping_gap_reports.py:91``, ``sample_null_loci.py:378``) fails visibly
   rather than opening a plausible-but-stale path.

NO PANEL EXISTS ON THIS NODE. ``data/processed/ld_reference/`` is absent
entirely and 0/276 ``.npz`` are banked, so every resolution assertion here runs
against FIXTURES written into ``tmp_path``. Nothing in this module may assert
against a real panel, and nothing here can trigger the AoU fire.

NO R, NO SNAKEMAKE, NO NETWORK -- pure Python over the source tree plus
``git show``. There is no toolchain here that could make one of these SKIP.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import types
from pathlib import Path

import pytest
import yaml

from ld_panel import resolve_ld_path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
QTL_COLOC_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "qtl_coloc.smk"
FINEMAP_SMK = PROJECT_ROOT / "src" / "snakemake" / "rules" / "finemap.smk"
LD_READ_PATH_PY = PROJECT_ROOT / "src" / "python" / "ld_read_path.py"
BUILDER_PY = PROJECT_ROOT / "src" / "python" / "build_qtl_coloc_manifest.py"
SHIPPED_CONFIG = PROJECT_ROOT / "config" / "pipeline.yaml"

#: The commit this plan started from -- the tree carrying the un-crosswalked
#: coloc LD path. The permanent differential substrate for the OFF branch.
PRE_CHANGE_REF = "7b1025d"

#: Every ancestry that MUST stay off the coloc read path. EUR and TRANS carry
#: Track A (in submission, 1,957 legacy coloc JSONs on disk, and today's coloc
#: successes are 32/32 EUR); EAS and HIS have no AoU panel at all.
INERT_ANCESTRIES = ("EUR", "TRANS", "EAS", "HIS")

ANCHOR = "SH2B3_12q24"
ANCHOR_M2 = "m2_region_00040__sub14"
CURATED_TO_M2 = {ANCHOR: ANCHOR_M2}
REGION_SAFE_TO_ID = {ANCHOR: ANCHOR}


# ==========================================================================
# Module loading -- source read at CALL TIME, never __pycache__
# ==========================================================================
def _load_module_from_text(name: str, text: str, filename: str) -> types.ModuleType:
    """Execute ``text`` as a fresh module.

    ``compile()`` on source text read at call time, consulting NO bytecode
    cache. ``SourceFileLoader`` validates a ``.pyc`` on ``(mtime_seconds,
    size)``, so a byte-length-identical edit restored inside the same wall-clock
    second runs STALE bytecode -- measured in 260805-o7o, where it produced a
    FALSE RED and could equally have produced a FALSE GREEN. Any test whose
    subject is the behaviour of a file someone will deliberately perturb as a
    negative control must read that file's text.
    """
    mod = types.ModuleType(name)
    mod.__file__ = filename
    exec(compile(text, filename, "exec"), mod.__dict__)
    return mod


def _gate():
    """``src/python/ld_read_path.py`` as it is ON DISK RIGHT NOW."""
    return _load_module_from_text(
        "_w7u_ld_read_path", LD_READ_PATH_PY.read_text(), str(LD_READ_PATH_PY)
    )


def _builder(rev: str | None = None):
    """``src/python/build_qtl_coloc_manifest.py`` at HEAD-on-disk or at ``rev``."""
    if rev is None:
        text = BUILDER_PY.read_text()
        fname = str(BUILDER_PY)
    else:
        text = _git_show(f"{rev}:src/python/build_qtl_coloc_manifest.py")
        fname = f"<{rev}:build_qtl_coloc_manifest.py>"
    return _load_module_from_text(f"_w7u_builder_{rev or 'head'}", text, fname)


def _git_show(spec: str) -> str:
    res = subprocess.run(
        ["git", "show", spec], cwd=PROJECT_ROOT,
        capture_output=True, text=True, check=True,
    )
    return res.stdout


# ==========================================================================
# .smk extraction -- read the REAL function, never re-type it
# ==========================================================================
def extract_top_level_def(source: str, name: str) -> str:
    """Return the verbatim source of the top-level ``def <name>(`` in ``source``.

    ``qtl_coloc.smk`` / ``finemap.smk`` are Snakemake DSL, not importable Python
    (``rule x:`` / ``wildcard_constraints:`` are not Python statements), so the
    function under test is sliced out by column-0 boundary and executed in a
    supplied namespace. This is the Python analogue of the R body-walk extractor
    in ``test_qtl_coloc_allele_join.py``: the object under test is the SHIPPED
    text, so a divergence between what this module asserts and what Snakemake
    runs is not possible.

    Raises loudly rather than returning ``None`` -- a silent miss here would let
    every downstream assertion pass against an empty namespace.
    """
    lines = source.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith(f"def {name}("):
            start = i
            break
    if start is None:
        raise AssertionError(
            f"STOP-and-surface: no top-level `def {name}(` in the supplied source"
        )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        ln = lines[j]
        if not ln.strip():
            continue
        if not ln[0].isspace():
            end = j
            break
    return "\n".join(lines[start:end]).rstrip() + "\n"


def extract_kwarg_expr(source: str, kwarg: str) -> str:
    """Return the verbatim expression assigned to ``<kwarg>=`` inside a rule block.

    Paren/bracket-balanced from the ``=``, so a multi-line ``lambda ...: str(...)``
    comes back whole. Used to evaluate ``finemap.smk``'s REAL ``ld_matrix``
    lambda rather than re-typing it -- "the coloc path resolves to the same
    artifact run_finemap does" is only evidence if the comparand IS run_finemap's
    expression.
    """
    needle = f"{kwarg}="
    idx = source.find(f"\n        {needle}")
    if idx < 0:
        raise AssertionError(f"STOP-and-surface: no `{kwarg}=` kwarg in the supplied source")
    start = idx + len(f"\n        {needle}")
    depth = 0
    for k in range(start, len(source)):
        ch = source[k]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "," and depth == 0:
            return source[start:k]
    raise AssertionError(f"STOP-and-surface: unbalanced `{kwarg}=` expression")


def code_only(text: str) -> str:
    """``text`` with docstrings and ``#`` comments removed.

    ⚠ NOT cosmetic. The m3-04c sweep's process note names "a comment satisfying
    its own regex" as one of FIVE assertions in this arc that were structurally
    incapable of failing. It bit this very module during authoring: a
    ``# NO load_curated_to_m2 IMPORT HERE`` comment -- written precisely to
    document the absence -- made the absence assertion fail. An absence claim
    about CODE must be evaluated against code.
    """
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch in "\"'":
            triple = text[i:i + 3]
            if triple in ('"""', "'''"):
                end = text.find(triple, i + 3)
                i = n if end < 0 else end + 3
                continue
            j = i + 1
            while j < n and text[j] != ch:
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:min(j + 1, n)])
            i = j + 1
            continue
        if ch == "#":
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _wc(**kw):
    return types.SimpleNamespace(**kw)


def _ld_input_fn(smk_text, *, config, row, qtl_coloc_dir="results/qtl_coloc", gate=None):
    """Execute a ``_qtl_coloc_ld_input`` definition in a controlled namespace."""
    g = _gate()
    ns = {
        "os": os,
        "config": config,
        "QTL_COLOC_DIR": qtl_coloc_dir,
        "_qtl_coloc_manifest_row": lambda _id: row,
        "resolve_ld_path": resolve_ld_path,
        "CURATED_TO_M2": CURATED_TO_M2,
        "REGION_SAFE_TO_ID": REGION_SAFE_TO_ID,
        "ld_coloc_applies": gate if gate is not None else g.ld_coloc_applies,
        "ld_matrix_region_id": g.ld_matrix_region_id,
    }
    exec(compile(extract_top_level_def(smk_text, "_qtl_coloc_ld_input"),
                 "<qtl_coloc.smk>", "exec"), ns)
    return ns["_qtl_coloc_ld_input"]


def _finemap_ld_matrix_lambda(config):
    """Evaluate ``finemap.smk``'s REAL ``ld_matrix=`` lambda."""
    expr = extract_kwarg_expr(FINEMAP_SMK.read_text(), "ld_matrix")
    g = _gate()
    ns = {
        "resolve_ld_path": resolve_ld_path,
        "ld_matrix_region_id": g.ld_matrix_region_id,
        "config": config,
        "CURATED_TO_M2": CURATED_TO_M2,
        "REGION_SAFE_TO_ID": REGION_SAFE_TO_ID,
        "str": str,
    }
    return eval(compile(expr, "<finemap.smk>", "eval"), ns)  # noqa: S307


# ==========================================================================
# Config fixtures
# ==========================================================================
def _cfg(ld_read_path, *, ld_reference="data/processed/ld_reference", panel_root=None):
    root = panel_root or "data/processed/ld_reference"
    cfg = {
        "paths": {"ld_reference": ld_reference},
        "ld_panel": {
            "AFR": [
                {"source": "AFR_aou", "path": f"{root}/AFR_aou/{{region_id}}.rds"},
                {"source": "AFR_1kg", "path": f"{root}/AFR/{{region_safe}}.rds"},
            ],
            "EUR": [
                {"source": "EUR_ukbb_pub", "path": f"{root}/EUR_ukbb_pub/{{region_safe}}.rds"},
                {"source": "EUR_1kg", "path": f"{root}/EUR/{{region_safe}}.rds"},
            ],
            "pin": {"AFR": None, "EUR": None},
            "strict_aou_only": False,
        },
    }
    if ld_read_path is not None:
        cfg["ld_read_path"] = ld_read_path
    return cfg


ON = {"enabled": True, "ancestries": ["AFR"], "allele_aware": True, "coloc": True}
OFF = {"enabled": True, "ancestries": ["AFR"], "allele_aware": True}


# ==========================================================================
# T1.1 -- the single gate
# ==========================================================================
def test_ld_coloc_applies_is_true_only_for_the_full_conjunction():
    g = _gate()
    assert g.ld_coloc_applies("AFR", _cfg(ON)) is True


@pytest.mark.parametrize(
    "block,label",
    [
        (None, "block absent"),
        ("not-a-dict", "block not a dict"),
        ([], "block is a list"),
        ({}, "block empty"),
        ({"enabled": False, "ancestries": ["AFR"], "coloc": True}, "enabled: false"),
        ({"enabled": True, "ancestries": [], "coloc": True}, "ancestries: []"),
        ({"enabled": True, "ancestries": ["AFR"]}, "coloc sub-key ABSENT"),
        ({"enabled": True, "ancestries": ["AFR"], "coloc": False}, "coloc: false"),
        ({"enabled": True, "ancestries": ["AFR"], "coloc": "true"}, "coloc: 'true' (string)"),
        ({"enabled": True, "ancestries": ["AFR"], "coloc": 1}, "coloc: 1 (truthy non-bool)"),
        ({"enabled": True, "ancestries": ["EUR"], "coloc": True}, "AFR not listed"),
    ],
)
def test_ld_coloc_applies_every_degraded_shape_is_false(block, label):
    """The fail-safe direction is CHANGE NOTHING, on every uncertain answer.

    ``is True`` (not truthiness) mirrors ``ld_allele_aware``: a YAML string
    ``"true"`` or an integer ``1`` must NOT arm a lever that decides which LD
    bytes a published posterior is computed from.
    """
    g = _gate()
    assert g.ld_coloc_applies("AFR", _cfg(block)) is False, label


def test_ld_coloc_applies_against_the_real_shipped_config():
    """AFR armed, EUR/TRANS/EAS/HIS inert -- against the file that actually ships."""
    g = _gate()
    shipped = yaml.safe_load(SHIPPED_CONFIG.read_text())
    assert g.ld_coloc_applies("AFR", shipped) is True
    for anc in INERT_ANCESTRIES:
        assert g.ld_coloc_applies(anc, shipped) is False, anc


def test_ld_coloc_join_renders_a_shell_string_not_a_bool():
    g = _gate()
    shipped = yaml.safe_load(SHIPPED_CONFIG.read_text())
    assert g.ld_coloc_join("AFR", shipped) == "true"
    for anc in INERT_ANCESTRIES:
        assert g.ld_coloc_join(anc, shipped) == "false", anc
    assert isinstance(g.ld_coloc_join("AFR", shipped), str)


def test_ld_coloc_applies_and_join_are_exported():
    g = _gate()
    assert "ld_coloc_applies" in g.__all__
    assert "ld_coloc_join" in g.__all__


# ==========================================================================
# T1.2 -- OFF the allow-list: character-for-character identity with 7b1025d,
#         asserted DIFFERENTIALLY against the real pre-change function
# ==========================================================================
@pytest.mark.parametrize("with_column", [True, False])
@pytest.mark.parametrize("ancestry", INERT_ANCESTRIES)
def test_off_the_allow_list_is_character_for_character_7b1025d(ancestry, with_column):
    """The OFF branch is the Track-A containment and must not be "tidied"."""
    row = {"ancestry": ancestry, "region": ANCHOR}
    if with_column:
        row["ld_matrix_path"] = f"data/processed/ld_reference/{ancestry}/{ANCHOR}.rds"
    cfg = _cfg(ON)

    head_fn = _ld_input_fn(QTL_COLOC_SMK.read_text(), config=cfg, row=dict(row))
    old_fn = _ld_input_fn(
        _git_show(f"{PRE_CHANGE_REF}:src/snakemake/rules/qtl_coloc.smk"),
        config=cfg, row=dict(row),
    )
    got = head_fn(_wc(qtl_coloc_id="x"))
    want = old_fn(_wc(qtl_coloc_id="x"))
    assert got == want, (
        f"the OFF-branch expression for {ancestry} is not character-for-character "
        f"{PRE_CHANGE_REF}'s: {got!r} != {want!r}"
    )


def test_missing_manifest_row_sentinel_is_character_for_character_7b1025d():
    cfg = _cfg(ON)
    head_fn = _ld_input_fn(QTL_COLOC_SMK.read_text(), config=cfg, row=None)
    old_fn = _ld_input_fn(
        _git_show(f"{PRE_CHANGE_REF}:src/snakemake/rules/qtl_coloc.smk"),
        config=cfg, row=None,
    )
    assert head_fn(_wc(qtl_coloc_id="zz")) == old_fn(_wc(qtl_coloc_id="zz"))


# ==========================================================================
# T1.3 -- ON the allow-list: the resolver's answer, and it EQUALS finemap's
# ==========================================================================
def _panel_on_disk(tmp_path: Path) -> tuple[dict, Path]:
    root = tmp_path / "ld_reference"
    (root / "AFR_aou").mkdir(parents=True)
    panel = root / "AFR_aou" / f"{ANCHOR_M2}.rds"
    panel.write_bytes(b"fixture-not-a-real-rds")
    return _cfg(ON, panel_root=str(root)), panel


def test_gate_on_returns_the_resolver_path(tmp_path):
    cfg, panel = _panel_on_disk(tmp_path)
    fn = _ld_input_fn(QTL_COLOC_SMK.read_text(), config=cfg,
                      row={"ancestry": "AFR", "region": ANCHOR})
    assert fn(_wc(qtl_coloc_id="x")) == str(panel)


def test_gate_on_equals_finemap_smk_ld_matrix_lambda(tmp_path):
    """ONE crosswalk object, ONE resolver, ONE artifact.

    The comparand is ``finemap.smk``'s REAL ``ld_matrix=`` lambda, extracted from
    the file and evaluated -- not a re-typed copy of it.
    """
    cfg, _panel = _panel_on_disk(tmp_path)
    coloc = _ld_input_fn(QTL_COLOC_SMK.read_text(), config=cfg,
                         row={"ancestry": "AFR", "region": ANCHOR})
    finemap = _finemap_ld_matrix_lambda(cfg)
    assert coloc(_wc(qtl_coloc_id="x")) == finemap(_wc(region=ANCHOR, ancestry="AFR"))


def test_gate_on_with_no_panel_raises_naming_the_region(tmp_path):
    """LOUD, not a legacy fallback.

    F3: four stacked exit-0 layers already make an unusable coloc LD look like
    biology. Substituting a silent legacy path here would add a fifth.
    """
    cfg = _cfg(ON, panel_root=str(tmp_path / "nothing-here"))
    fn = _ld_input_fn(QTL_COLOC_SMK.read_text(), config=cfg,
                      row={"ancestry": "AFR", "region": ANCHOR})
    with pytest.raises(FileNotFoundError) as exc:
        fn(_wc(qtl_coloc_id="x"))
    assert ANCHOR_M2 in str(exc.value) or ANCHOR in str(exc.value)


def test_gate_on_ignores_a_competing_existing_manifest_path(tmp_path):
    """T-w7u-01. The manifest is an on-disk TSV, regenerable out-of-band. Under
    the gate it is NOT a path oracle: the resolver's answer wins even when the
    manifest names a DIFFERENT file that EXISTS."""
    cfg, panel = _panel_on_disk(tmp_path)
    decoy = tmp_path / "decoy.rds"
    decoy.write_bytes(b"decoy")
    fn = _ld_input_fn(
        QTL_COLOC_SMK.read_text(), config=cfg,
        row={"ancestry": "AFR", "region": ANCHOR, "ld_matrix_path": str(decoy)},
    )
    got = fn(_wc(qtl_coloc_id="x"))
    assert got == str(panel)
    assert got != str(decoy)


# ==========================================================================
# T1.4 -- exactly ONE crosswalk object, exactly ONE allow-list read
# ==========================================================================
def test_qtl_coloc_smk_loads_no_second_crosswalk():
    """A second ``load_curated_to_m2`` is a second source of truth (T-w7u-07)."""
    code = code_only(QTL_COLOC_SMK.read_text())
    assert "load_curated_to_m2" not in code
    assert 'config.get("ld_read_path"' not in code
    assert 'config["ld_read_path"]' not in code
    # The plan's forward gate is the LITERAL file-wide grep, so it must be 0 in
    # the raw text too -- the explanatory comment names the loader by role, not
    # by symbol, precisely so that gate stays meaningful.
    assert "load_curated_to_m2" not in QTL_COLOC_SMK.read_text()
    # non-vacuity: the stripper must not have eaten the file
    assert "def _qtl_coloc_ld_input(wildcards):" in code
    assert "resolve_ld_path" in code


def test_qtl_coloc_smk_never_re_derives_the_gate():
    """No sub-key of ``ld_read_path`` is named anywhere in the .smk.

    The DECISION must be exactly one predicate. A rule that reads ``enabled`` /
    ``coloc`` / ``ancestries`` for itself is a second answer that agrees TODAY
    only because nobody has changed the block's shape yet -- and it would agree
    silently while diverging (T-w7u-07). The enumeration the manifest builder
    needs lives in ``ld_coloc_ancestries``, inside the module that owns the
    block, and is itself filtered through ``ld_coloc_applies``.
    """
    code = code_only(QTL_COLOC_SMK.read_text())
    for sub_key in ('"enabled"', '"coloc"', '"ancestries"', '"allele_aware"'):
        assert sub_key not in code, sub_key
    assert "ld_coloc_ancestries(config)" in code


def test_ld_coloc_ancestries_is_filtered_through_the_single_predicate():
    """Not an independent answer: it goes to [] whenever the gate goes False."""
    g = _gate()
    assert g.ld_coloc_ancestries(_cfg(ON)) == ["AFR"]
    for block in (
        None,
        {"enabled": False, "ancestries": ["AFR"], "coloc": True},
        {"enabled": True, "ancestries": ["AFR"]},
        {"enabled": True, "ancestries": ["AFR"], "coloc": False},
        {"enabled": True, "ancestries": ["AFR"], "coloc": "true"},
        {"enabled": True, "ancestries": [], "coloc": True},
    ):
        assert g.ld_coloc_ancestries(_cfg(block)) == [], block
    shipped = yaml.safe_load(SHIPPED_CONFIG.read_text())
    assert g.ld_coloc_ancestries(shipped) == ["AFR"]


def test_qtl_coloc_smk_routes_through_the_resolver():
    text = QTL_COLOC_SMK.read_text()
    assert "resolve_ld_path" in text
    assert "ld_matrix_region_id" in text
    assert "ld_coloc_applies" in text


# ==========================================================================
# T1.5 -- the manifest emits a NON-PATH sentinel for gated ancestries
# ==========================================================================
def _min_builder_inputs(tmp_path: Path):
    """A fixture that produces a NON-EMPTY manifest.

    ⚠ The ``gene`` column name is load-bearing: ``_genes_for_region`` reads
    ``region.get("gene", "")`` and returns ``[]`` when it is absent, which yields
    ZERO rows -- and zero rows would make every byte-identity assertion below
    vacuously true (``[] == []``, header-only files comparing equal). Caught
    during authoring; ``_rows`` now asserts non-emptiness so it cannot regress.
    """
    regions = tmp_path / "regions.csv"
    with regions.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "region_id", "chr", "start_grch38", "end_grch38",
            "trait_list", "gene",
        ])
        w.writeheader()
        w.writerow({"region_id": ANCHOR, "chr": "12",
                    "start_grch38": "111000000", "end_grch38": "111600000",
                    "trait_list": "htn", "gene": "SH2B3"})
        w.writerow({"region_id": "FTO_16q12", "chr": "16",
                    "start_grch38": "53700000", "end_grch38": "54200000",
                    "trait_list": "obesity", "gene": "FTO"})
    sources = tmp_path / "qtl_sources.yaml"
    # ``load_qtl_sources`` reads ``cfg.get("sources", {})`` -- the top-level
    # ``sources:`` key is load-bearing for the same non-vacuity reason.
    sources.write_text(yaml.safe_dump(
        {"sources": {"gtex_eqtl": {"sdY": 1.0, "sample_size": 500}}}
    ))
    lookup = tmp_path / "tissue_n.json"
    lookup.write_text(json.dumps({"Whole_Blood": 670, "Artery_Aorta": 387}))
    return regions, sources, lookup


def _rows(mod, tmp_path, **kw):
    regions, sources, lookup = _min_builder_inputs(tmp_path)
    rows = mod.build_manifest(
        mod.load_regions(regions),
        mod.load_qtl_sources(sources),
        mod.load_tissue_n(lookup),
        "results", "data/processed/ld_reference", "data/processed/qtl_harmonized",
        **kw,
    )
    assert rows, "NON-VACUITY: the builder fixture produced zero rows"
    return rows


def test_ancestry_for_region_is_hardcoded_eur_today():
    """⚠ MEASURED, and it is why the test below cannot use ``{"AFR"}``.

    ``build_qtl_coloc_manifest.py::_ancestry_for_region`` returns ``"EUR"``
    UNCONDITIONALLY -- it ignores the region entirely. So with the SHIPPED
    allow-list (``AFR``) **no manifest row takes the sentinel branch**: the
    manifest half of finding E's remedy is wired and correct but INERT today,
    and goes live the moment this function learns about AFR.

    The plan for this task assumed AFR manifest rows exist. They do not. That is
    recorded as a measured fact here rather than papered over, because an inert
    branch nobody knows is inert is how "the fix is wired" becomes unfalsifiable
    -- and because the fix for it (teaching ``_ancestry_for_region`` about AFR)
    would CHANGE THE MANIFEST for Track A and is emphatically not this task's.
    """
    mod = _builder()
    for region in ({"region_id": "X", "trait_list": "htn", "ancestry": "AFR"},
                   {"region_id": "Y", "trait_list": "stroke"},
                   {}):
        assert mod._ancestry_for_region(region) == "EUR"


def test_builder_emits_the_non_path_sentinel_for_gated_ancestries(tmp_path):
    """The MECHANISM, exercised on the ancestry the builder actually emits.

    Gating EUR here is a FIXTURE choice, not a proposal: it is the only way to
    drive the branch given the measured fact above. The shipped config gates AFR
    only, and ``test_shipped_allow_list_changes_no_row_today`` pins that the real
    configuration leaves every row alone.
    """
    mod = _builder()
    rows = _rows(mod, tmp_path, resolver_ancestries={"EUR"})
    assert rows
    assert {r["ancestry"] for r in rows} == {"EUR"}
    for r in rows:
        assert r["ld_matrix_path"] == mod.LD_PATH_RESOLVER_SENTINEL
    # ...and a row OFF the supplied allow-list keeps the constructed path.
    other = _rows(mod, tmp_path, resolver_ancestries={"AFR"})
    for r in other:
        assert r["ld_matrix_path"] == os.path.join(
            "data/processed/ld_reference", "EUR", f"{r['region']}.rds"
        )


def test_shipped_allow_list_changes_no_row_today(tmp_path):
    """With the REAL config's allow-list, the manifest is byte-identical."""
    g = _gate()
    shipped = yaml.safe_load(SHIPPED_CONFIG.read_text())
    allow = set(g.ld_coloc_ancestries(shipped))
    assert allow == {"AFR"}
    head, old = _builder(), _builder(PRE_CHANGE_REF)
    assert _rows(head, tmp_path, resolver_ancestries=allow) == _rows(old, tmp_path)


def test_the_sentinel_is_deliberately_not_path_shaped():
    """It must FAIL VISIBLY in any other reader, not open something plausible.

    ``plan_ld_builds.py:238``, ``fine_mapping_gap_reports.py:91`` and
    ``sample_null_loci.py:378`` all read this column. A path-shaped placeholder
    would let one of them open a stale-but-existing file; a value with no
    separator and no suffix cannot.
    """
    mod = _builder()
    s = mod.LD_PATH_RESOLVER_SENTINEL
    assert s == "RESOLVED_BY_LD_PANEL_RESOLVER"
    assert os.sep not in s
    assert "/" not in s
    assert not s.endswith(".rds")
    assert not os.path.exists(s)


def test_builder_default_is_byte_identical_to_7b1025d(tmp_path):
    """"Default changes nothing", proven against the REAL pre-change builder."""
    head = _builder()
    old = _builder(PRE_CHANGE_REF)
    assert _rows(head, tmp_path) == _rows(old, tmp_path)
    assert _rows(head, tmp_path, resolver_ancestries=None) == _rows(old, tmp_path)
    assert _rows(head, tmp_path, resolver_ancestries=set()) == _rows(old, tmp_path)


def test_builder_emitted_tsv_is_byte_identical_to_7b1025d(tmp_path):
    """Whole-file bytes, via ``main()``, argv-for-argv."""
    regions, sources, lookup = _min_builder_inputs(tmp_path)
    old_py = tmp_path / "builder_7b1025d.py"
    old_py.write_text(_git_show(f"{PRE_CHANGE_REF}:src/python/build_qtl_coloc_manifest.py"))

    outs = {}
    for label, script in (("head", BUILDER_PY), ("old", old_py)):
        out = tmp_path / f"manifest_{label}.tsv"
        res = subprocess.run(
            [os.sys.executable, str(script),
             "--regions", str(regions), "--qtl-sources", str(sources),
             "--tissue-n-lookup", str(lookup), "--results-root", "results",
             "--ld-reference", "data/processed/ld_reference",
             "--harmonized-dir", "data/processed/qtl_harmonized",
             "--output", str(out)],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert res.returncode == 0, res.stderr
        outs[label] = out.read_bytes()
        # NON-VACUITY: header-only files would compare equal for free.
        assert len(out.read_text().splitlines()) > 1
    assert outs["head"] == outs["old"]


def test_builder_fieldnames_are_unchanged(tmp_path):
    """No column added, no column reordered -- the header is a public contract."""
    regions, sources, lookup = _min_builder_inputs(tmp_path)
    out = tmp_path / "m.tsv"
    subprocess.run(
        [os.sys.executable, str(BUILDER_PY),
         "--regions", str(regions), "--qtl-sources", str(sources),
         "--tissue-n-lookup", str(lookup), "--results-root", "results",
         "--ld-reference", "data/processed/ld_reference",
         "--harmonized-dir", "data/processed/qtl_harmonized",
         "--output", str(out), "--resolver-ancestries", "AFR"],
        capture_output=True, text=True, cwd=PROJECT_ROOT, check=True,
    )
    header = out.read_text().splitlines()[0]
    old_py = tmp_path / "old.py"
    old_py.write_text(_git_show(f"{PRE_CHANGE_REF}:src/python/build_qtl_coloc_manifest.py"))
    out_old = tmp_path / "m_old.tsv"
    subprocess.run(
        [os.sys.executable, str(old_py),
         "--regions", str(regions), "--qtl-sources", str(sources),
         "--tissue-n-lookup", str(lookup), "--results-root", "results",
         "--ld-reference", "data/processed/ld_reference",
         "--harmonized-dir", "data/processed/qtl_harmonized",
         "--output", str(out_old)],
        capture_output=True, text=True, cwd=PROJECT_ROOT, check=True,
    )
    assert header == out_old.read_text().splitlines()[0]


def test_cli_resolver_ancestries_flag_defaults_to_none(tmp_path):
    """Absent flag == today. The flag is opt-in from the ONE allow-list."""
    regions, sources, lookup = _min_builder_inputs(tmp_path)
    a, b = tmp_path / "a.tsv", tmp_path / "b.tsv"
    base = [os.sys.executable, str(BUILDER_PY),
            "--regions", str(regions), "--qtl-sources", str(sources),
            "--tissue-n-lookup", str(lookup), "--results-root", "results",
            "--ld-reference", "data/processed/ld_reference",
            "--harmonized-dir", "data/processed/qtl_harmonized"]
    subprocess.run(base + ["--output", str(a)], check=True,
                   capture_output=True, cwd=PROJECT_ROOT)
    subprocess.run(base + ["--output", str(b), "--resolver-ancestries", ""],
                   check=True, capture_output=True, cwd=PROJECT_ROOT)
    assert a.read_bytes() == b.read_bytes()
    assert b"RESOLVED_BY_LD_PANEL_RESOLVER" not in a.read_bytes()


def test_rule_build_qtl_coloc_manifest_threads_the_same_allow_list():
    """Both places read the SAME allow-list from the SAME config."""
    text = QTL_COLOC_SMK.read_text()
    assert '--resolver-ancestries "{params.resolver_ancestries}"' in text
    assert 'resolver_ancestries=",".join(ld_coloc_ancestries(config))' in text


def test_the_resolver_ancestries_shell_token_is_quoted():
    """OFF the allow-list this value is the EMPTY STRING.

    Unquoted, the shell collapses it and argparse consumes the NEXT flag as its
    value -- so the manifest build would fail in exactly the DEFAULT
    configuration, which is the one nobody runs a fixture against. The quoting is
    the fix; this pins it, and ``test_cli_resolver_ancestries_flag_defaults_to_none``
    proves the empty value is actually accepted end to end.
    """
    text = QTL_COLOC_SMK.read_text()
    assert "--resolver-ancestries {params.resolver_ancestries}" not in text
    assert '--resolver-ancestries "{params.resolver_ancestries}"' in text


def test_empty_resolver_ancestries_argv_is_accepted_by_the_cli(tmp_path):
    """The rendered OFF-the-allow-list argv, executed for real."""
    regions, sources, lookup = _min_builder_inputs(tmp_path)
    out = tmp_path / "m.tsv"
    res = subprocess.run(
        [os.sys.executable, str(BUILDER_PY),
         "--regions", str(regions), "--qtl-sources", str(sources),
         "--tissue-n-lookup", str(lookup), "--results-root", "results",
         "--ld-reference", "data/processed/ld_reference",
         "--harmonized-dir", "data/processed/qtl_harmonized",
         "--resolver-ancestries", "",
         "--output", str(out)],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    assert res.returncode == 0, res.stderr
    assert out.exists()


# ==========================================================================
# T1.6 -- the schema TYPES the key (F7: it does not gate validate())
# ==========================================================================
def test_schema_declares_the_coloc_key_as_boolean():
    schema = yaml.safe_load(
        (PROJECT_ROOT / "src" / "snakemake" / "schemas" / "pipeline.schema.yaml").read_text()
    )
    props = schema["properties"]["ld_read_path"]["properties"]
    assert props["coloc"]["type"] == "boolean"
    # F7, MEASURED in 260805-o7o: additionalProperties: false is TOP LEVEL only,
    # so ld_read_path sub-keys are permitted by JSON-Schema's default. This
    # entry TYPES the key; it is not what keeps validate() alive.
    assert schema.get("additionalProperties") is False
    assert "additionalProperties" not in schema["properties"]["ld_read_path"]


def test_shipped_config_carries_coloc_true():
    shipped = yaml.safe_load(SHIPPED_CONFIG.read_text())
    assert shipped["ld_read_path"]["coloc"] is True
