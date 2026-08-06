"""FINDING G — the orphaned TRANS chain head, and the strict guard that could not see it.

`m3-04c-BLAST-RADIUS.md` finding **G**: retiring ``build_ld_rds_aou_eur`` left
``config/pipeline.yaml``'s TRANS chain HEAD (``TRANS_aou_eur`` ->
``data/processed/ld_reference/EUR_aou/{region_id}.rds``) with **no producer**,
and the ``strict_aou_only`` guard tested ``entry["source"].endswith("_aou")`` --
which is ``False`` for ``TRANS_aou_eur`` (ancestry-of-panel LAST). So TRANS
walked to ``EUR_1kg`` forever, silently, *even with strict mode ON*.

WHAT THIS MODULE PROVES, AND WHAT IT DELIBERATELY DOES NOT
----------------------------------------------------------
It proves the guard can now SEE the orphan, that it does **not** newly fire on a
legitimate non-AoU entry (the false-trip direction -- `quick-260715-vxz`), that
a FOURTH AoU chain entry cannot be added without a registry entry naming its
consequence, and that under the SHIPPED config (``strict_aou_only: false``)
every curated region x ancestry resolves to the byte-identical path it resolved
to at ``6b427bc`` -- Track A cannot move.

It does **NOT** make TRANS work. After this change a TRANS fit still resolves to
``data/processed/ld_reference/EUR/{region_safe}.rds`` -- the legacy 1kG EUR
panel -- exactly as it does today, because ``strict_aou_only`` ships ``false``.
What changed is that the orphan stopped being invisible. Whether a TRANS fit on
a 1kG EUR panel is reportable at all is registered as **G-2** in
``.planning/phases/m3-aou-afr-ld-panel-build/deferred-items.md``.

DISCIPLINE
----------
* The chains are read from the **REAL** ``config/pipeline.yaml`` with
  ``yaml.safe_load``, never hand-copied: a structural copy is exactly why
  ``test_ld_read_path_ancestry_gate.py::_panel_cfg`` cannot observe a shipped
  config drift.
* Every module-under-differential-test is ``compile()``d from source text read
  at CALL TIME (the ``_load_module_from_text`` pattern already in
  ``tests/m3/test_qtl_coloc_ld_resolution.py``), so a negative control that
  perturbs ``ld_panel.py`` cannot be defeated by a stale ``.pyc``
  (``SourceFileLoader`` validates cached bytecode on ``(mtime_seconds, size)``).
* NC-G3 and the inverted half of the invariance proof are **permanent and
  in-suite**, not one-off reverts, so they cannot decay into claims.
"""
from __future__ import annotations

import copy
import csv
import subprocess
import types
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LD_PANEL_PY = PROJECT_ROOT / "src" / "python" / "ld_panel.py"
SHIPPED_CONFIG = PROJECT_ROOT / "config" / "pipeline.yaml"
REGIONS_CURATED_CSV = PROJECT_ROOT / "config" / "regions_curated.csv"
CROSSWALK_TSV = PROJECT_ROOT / "config" / "curated_to_m2_region_map.tsv"
RULES_DIR = PROJECT_ROOT / "src" / "snakemake" / "rules"
SNAKEFILE = PROJECT_ROOT / "Snakefile"

#: The commit this task started from -- the permanent differential substrate for
#: the "Track A cannot move" half.
BASELINE_REV = "6b427bc"

#: The three ancestries the shipped ``ld_panel`` block defines chains for.
ANCESTRIES = ("EUR", "AFR", "TRANS")

#: Every shipped chain entry templates under this prefix. Asserted, not assumed
#: -- if a future entry escapes it, the re-rooting below would silently write
#: into the real tree instead of ``tmp_path``.
LD_REF_PREFIX = "data/processed/ld_reference/"

#: The AoU-sourced entries in the shipped chains, as a LITERAL. Deliberately not
#: derived from ``is_aou_source``: the fixture trees below must not move when a
#: negative control perturbs the predicate, or the control would be masking
#: itself.
SHIPPED_AOU_SOURCES = {"EUR_aou", "AFR_aou", "TRANS_aou_eur"}

#: The verdict table from ``is_aou_source``'s docstring, over the COMPLETE
#: shipped source set. ``TRANS_aou_eur`` was ``False`` before finding G.
EXPECTED_VERDICTS = {
    "EUR_ukbb_pub": False,
    "EUR_aou": True,
    "EUR_ukbb": False,
    "EUR_1kg": False,
    "AFR_aou": True,
    "AFR_hgdp": False,
    "AFR_1kg": False,
    "TRANS_aou_eur": True,
}

# ---------------------------------------------------------------------------
# THE ORPHAN REGISTRY -- the durable half of finding G's closure
# ---------------------------------------------------------------------------
#: An AoU-sourced chain entry that something in the DAG actually BUILDS, mapped
#: to (the .smk that carries the rule, the rule name).
PRODUCED_AOU_SOURCES = {
    "AFR_aou": ("m3_convert_npz_rds.smk", "build_ld_rds_aou_afr"),
}

#: An AoU-sourced chain entry with NO producer, mapped to the consequence of
#: leaving it in the chain. These entries STAY: deleting ``TRANS_aou_eur`` would
#: leave TRANS with no AoU entry at all, making ``strict_aou_only`` structurally
#: unable to ever flag TRANS again -- that DEEPENS the silence rather than
#: closing it.
KNOWN_ORPHANED_AOU_SOURCES = {
    "EUR_aou": (
        "No producer. `build_ld_rds_aou_eur` was RETIRED 2026-08-05 "
        "(src/snakemake/rules/m3_convert_npz_rds.smk retirement note) because "
        "m3-02e Move 2 made the PUBLIC UKBB 337k panel the EUR chain head and "
        "no EUR LD is computed inside the AoU perimeter at all, so "
        "data/interim/aou_ld_exports/EUR_aou/ is never populated. Harmless in "
        "the EUR chain -- EUR_ukbb_pub sits AHEAD of it -- and it must not be "
        "removed: tests/m3/test_ld_panel_resolver.py:184 indexes on it."
    ),
    "TRANS_aou_eur": (
        "FINDING G. Same missing artifact, but it is the TRANS chain HEAD, so "
        "every TRANS resolution walks past it to EUR_1kg -- the legacy 1kG EUR "
        "panel. strict_aou_only (shipped false) is now the lever that converts "
        "that silence into a raise. Do NOT set ld_panel.pin.TRANS as a "
        "containment: pin short-circuits the chain AHEAD of strict mode "
        "(ld_panel.py), so pinning would re-hide exactly what this exposes. "
        "The scientific question -- may a TRANS fit be reported on a 1kG EUR "
        "panel at all -- is registered as G-2 in deferred-items.md."
    ),
}


# ==========================================================================
# Module loading -- source read at CALL TIME, never __pycache__
# ==========================================================================
def _load_module_from_text(name: str, text: str, filename: str) -> types.ModuleType:
    """Execute ``text`` as a fresh module.

    ``compile()`` on source text read at call time, consulting NO bytecode
    cache. Reused verbatim in spirit from
    ``tests/m3/test_qtl_coloc_ld_resolution.py``: any test whose subject is the
    behaviour of a file someone will deliberately perturb as a negative control
    must read that file's TEXT, not import it.
    """
    mod = types.ModuleType(name)
    mod.__file__ = filename
    exec(compile(text, filename, "exec"), mod.__dict__)
    return mod


def _git_show(spec: str) -> str:
    res = subprocess.run(
        ["git", "show", spec],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return res.stdout


def _ld_panel(rev: str | None = None) -> types.ModuleType:
    """``src/python/ld_panel.py`` as it is ON DISK RIGHT NOW, or at ``rev``."""
    if rev is None:
        return _load_module_from_text(
            "_b77_ld_panel_head", LD_PANEL_PY.read_text(), str(LD_PANEL_PY)
        )
    return _load_module_from_text(
        f"_b77_ld_panel_{rev}",
        _git_show(f"{rev}:src/python/ld_panel.py"),
        f"<{rev}:ld_panel.py>",
    )


# ==========================================================================
# The REAL shipped config -- never a structural copy
# ==========================================================================
def _shipped_panel_cfg() -> dict:
    return yaml.safe_load(SHIPPED_CONFIG.read_text())["ld_panel"]


def _shipped_sources() -> list[str]:
    panel = _shipped_panel_cfg()
    return [e["source"] for anc in ANCESTRIES for e in panel[anc]]


def _reroot(panel_cfg: dict, base: Path) -> dict:
    """Deep-copy the shipped block with every path re-rooted under ``base``."""
    cfg = copy.deepcopy(panel_cfg)
    for anc in ANCESTRIES:
        for entry in cfg[anc]:
            assert entry["path"].startswith(LD_REF_PREFIX), (
                f"shipped chain entry {entry['source']!r} escapes {LD_REF_PREFIX!r} "
                f"({entry['path']!r}); re-rooting would write into the REAL tree"
            )
            entry["path"] = str(base / entry["path"][len(LD_REF_PREFIX):])
    return cfg


def _wrap(panel_cfg: dict) -> dict:
    return {"ld_panel": panel_cfg}


def _touch(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("")
    return p


# ==========================================================================
# The curated region universe -- 12 slugs, both id conventions
# ==========================================================================
def _curated_slugs() -> list[str]:
    """The 12 curated slugs, filesystem-safe (mirrors ``Snakefile:49``)."""
    with REGIONS_CURATED_CSV.open(newline="") as fh:
        return [
            row["region_id"].replace(".", "_").replace("/", "_")
            for row in csv.DictReader(fh)
        ]


def _crosswalk_ids() -> dict:
    """``region_safe -> m2_region_id`` straight off the COMMITTED crosswalk."""
    out = {}
    with CROSSWALK_TSV.open(newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            m2 = (row.get("m2_region_id") or "").strip()
            if m2:
                out[row["region_safe"]] = m2
    return out


def _region_pairs() -> list[tuple[str, str]]:
    """Every ``(region_id, region_safe)`` pair production can hand the resolver.

    OFF the ``ld_read_path`` allow-list ``finemap.smk`` passes the legacy slug
    as BOTH; ON it the curated->M2 crosswalk supplies an M2 id for
    ``region_id`` while ``region_safe`` stays the slug. Both conventions are
    exercised so the invariance proof covers the whole call space.
    """
    slugs = _curated_slugs()
    xwalk = _crosswalk_ids()
    pairs = [(s, s) for s in slugs]
    pairs += [(xwalk[s], s) for s in slugs if s in xwalk]
    return pairs


TREES = ("full", "no_aou", "tail_only", "empty")


def _build_tree(panel_cfg: dict, pairs, which: str) -> None:
    """Materialise a fixture tree for a re-rooted chain block.

    ``no_aou`` uses the LITERAL ``SHIPPED_AOU_SOURCES`` set, not the predicate,
    so a control that perturbs ``is_aou_source`` cannot also move the fixture.
    """
    for anc in ANCESTRIES:
        chain = panel_cfg[anc]
        for i, entry in enumerate(chain):
            if which == "full":
                include = True
            elif which == "no_aou":
                include = entry["source"] not in SHIPPED_AOU_SOURCES
            elif which == "tail_only":
                include = i == len(chain) - 1
            elif which == "empty":
                include = False
            else:  # pragma: no cover - guard
                raise AssertionError(f"unknown tree {which!r}")
            if not include:
                continue
            for region_id, region_safe in pairs:
                _touch(
                    Path(
                        entry["path"].format(
                            region_id=region_id, region_safe=region_safe
                        )
                    )
                )


def _outcome(mod, region_id: str, ancestry: str, cfg: dict, region_safe: str):
    """``("path", str)`` or ``(exception-class-name, message)``.

    Whole-object outcome, not a status field: ``ld_status`` /
    ``ld_overlap_fraction`` / ``status`` are DISQUALIFIED as evidence for a
    Track-A invariance claim (m3-04c proved EUR numerics move while all three
    stay byte-identical), and the same discipline applies here.
    """
    try:
        return ("path", str(mod.resolve_ld_path(region_id, ancestry, cfg, region_safe)))
    except Exception as exc:  # noqa: BLE001 -- the class IS the evidence
        return (type(exc).__name__, str(exc))


# ==========================================================================
# (a) The verdict table, exhaustive, over the REAL shipped chains
# ==========================================================================
def test_the_expected_verdict_table_covers_every_shipped_source():
    """Non-vacuity guard for (a): a NEW chain source must force a test update
    rather than sliding through an unasserted default."""
    shipped = set(_shipped_sources())
    assert shipped == set(EXPECTED_VERDICTS), (
        "the shipped ld_panel chains no longer match this module's verdict "
        f"table.\n  shipped only: {sorted(shipped - set(EXPECTED_VERDICTS))}\n"
        f"  table only:   {sorted(set(EXPECTED_VERDICTS) - shipped)}"
    )


@pytest.mark.parametrize("source,expected", sorted(EXPECTED_VERDICTS.items()))
def test_is_aou_source_verdict_matches_the_docstring_table(source, expected):
    g = _ld_panel()
    assert g.is_aou_source(source) is expected, (
        f"is_aou_source({source!r}) should be {expected}; "
        "TRANS_aou_eur returning False IS finding G"
    )


def test_the_true_set_is_exactly_the_three_known_aou_sources():
    """An EQUALITY, not a superset: a WIDENED predicate fails here."""
    g = _ld_panel()
    true_set = {s for s in _shipped_sources() if g.is_aou_source(s)}
    assert true_set == SHIPPED_AOU_SOURCES, (
        f"the AoU-sourced set over the shipped chains is {sorted(true_set)}, "
        f"expected {sorted(SHIPPED_AOU_SOURCES)}"
    )


# ==========================================================================
# (b) token, not substring
# ==========================================================================
@pytest.mark.parametrize(
    "source,expected",
    [
        ("EUR_aoudad", False),   # CONTAINS the letters, is not the token
        ("aoudad", False),
        ("AOU_eur", False),      # case-sensitive token, deliberately
        ("aou", True),
        ("TRANS_aou_eur", True),
        ("EUR_aou", True),
        ("aou_something", True),
    ],
)
def test_is_aou_source_is_token_based_not_substring(source, expected):
    g = _ld_panel()
    assert g.is_aou_source(source) is expected


def test_is_aou_source_is_exported_from_the_real_module():
    import ld_panel as shipped

    assert "is_aou_source" in shipped.__all__
    assert callable(shipped.is_aou_source)


# ==========================================================================
# (c) strict mode, TRANS, end to end
# ==========================================================================
def test_strict_mode_raises_for_trans_when_the_orphaned_head_is_absent(tmp_path):
    """FINDING G, closed. No files created at all: the TRANS head is absent, so
    strict mode must REFUSE rather than walk to the 1kG EUR tail."""
    g = _ld_panel()
    panel = _reroot(_shipped_panel_cfg(), tmp_path / "ld_reference")
    panel["strict_aou_only"] = True

    with pytest.raises(FileNotFoundError, match="strict_aou_only"):
        g.resolve_ld_path("m2_region_00040__sub14", "TRANS", _wrap(panel), "SH2B3_12q24")


def test_the_trans_orphan_is_still_in_the_shipped_chain():
    """DO NOT "fix" finding G by deleting the orphan.

    Removing ``TRANS_aou_eur`` leaves TRANS with NO AoU entry, which makes
    ``strict_aou_only`` structurally unable to ever flag TRANS again -- deletion
    DEEPENS the silence. The entry stays; the guard learned to see it.
    """
    panel = _shipped_panel_cfg()
    trans_sources = [e["source"] for e in panel["TRANS"]]
    assert trans_sources[0] == "TRANS_aou_eur", (
        f"TRANS chain head is {trans_sources[0]!r}; the orphan must stay AS THE "
        "HEAD so strict mode can flag it"
    )
    assert trans_sources[-1] == "EUR_1kg"
    assert SHIPPED_AOU_SOURCES & set(trans_sources), (
        "TRANS has no AoU-sourced entry at all -- strict_aou_only can never "
        "flag it again"
    )


# ==========================================================================
# (d) THE FALSE-TRIP DIRECTION -- the guard must NOT newly fire
# ==========================================================================
def test_strict_mode_does_not_fire_on_a_chain_of_only_non_aou_sources(tmp_path):
    """The `quick-260715-vxz` / P3 lesson: a guard that starts firing too
    broadly stops the fire from starting at all."""
    g = _ld_panel()
    base = tmp_path / "ld_reference"
    panel = {
        "EUR": [
            {"source": "EUR_ukbb_pub", "path": str(base / "EUR_ukbb_pub" / "{region_safe}.rds")},
            {"source": "EUR_1kg", "path": str(base / "EUR" / "{region_safe}.rds")},
        ],
        "strict_aou_only": True,
        "pin": {"EUR": None},
    }
    tail = _touch(base / "EUR" / "FTO_16q12.rds")

    got = g.resolve_ld_path("FTO_16q12", "EUR", _wrap(panel), "FTO_16q12")
    assert str(got) == str(tail), (
        "strict_aou_only fired on a chain with NO AoU entry -- the guard is "
        "over-firing and no legitimate run can start"
    )


def test_under_the_shipped_config_no_ancestry_raises_when_a_tail_entry_exists(tmp_path):
    """The shipped ``strict_aou_only: false`` half of (d)."""
    g = _ld_panel()
    panel = _reroot(_shipped_panel_cfg(), tmp_path / "ld_reference")
    assert panel["strict_aou_only"] is False, (
        "the shipped config no longer ships strict_aou_only: false -- this "
        "whole task's Track-A invariance argument rests on that default"
    )
    pairs = [("m2_region_00067", "FTO_16q12")]
    _build_tree(panel, pairs, "tail_only")

    for anc in ANCESTRIES:
        got = g.resolve_ld_path("m2_region_00067", anc, _wrap(panel), "FTO_16q12")
        assert Path(got).exists()


# ==========================================================================
# (e) The orphan registry -- a FOURTH AoU entry cannot be added silently
# ==========================================================================
def _unregistered_aou_sources(panel_cfg: dict, is_aou) -> list[str]:
    """Shipped AoU-sourced entries that no registry entry names."""
    registered = set(PRODUCED_AOU_SOURCES) | set(KNOWN_ORPHANED_AOU_SOURCES)
    found = {
        e["source"]
        for anc in ANCESTRIES
        for e in panel_cfg[anc]
        if is_aou(e["source"])
    }
    return sorted(found - registered)


def test_the_registry_covers_exactly_the_shipped_aou_sources():
    g = _ld_panel()
    panel = _shipped_panel_cfg()
    registered = set(PRODUCED_AOU_SOURCES) | set(KNOWN_ORPHANED_AOU_SOURCES)
    assert registered == SHIPPED_AOU_SOURCES
    assert _unregistered_aou_sources(panel, g.is_aou_source) == [], (
        "an AoU-sourced chain entry has no registry entry naming either its "
        "producing rule or the consequence of it having none"
    )
    assert not (set(PRODUCED_AOU_SOURCES) & set(KNOWN_ORPHANED_AOU_SOURCES))


def test_nc_g3_a_fourth_unregistered_aou_entry_fails_the_registry_check():
    """NC-G3 -- PERMANENT AND IN-SUITE.

    "A new orphan cannot be added silently" is a CI-enforced property here, not
    a claim: inject a synthetic AoU entry into an IN-MEMORY copy of the real
    loaded config and require the registry check to name it.
    """
    g = _ld_panel()
    panel = copy.deepcopy(_shipped_panel_cfg())
    panel["AFR"].insert(
        1,
        {
            "source": "AFR_aou_v2",
            "path": "data/processed/ld_reference/AFR_aou_v2/{region_id}.rds",
        },
    )
    assert _unregistered_aou_sources(panel, g.is_aou_source) == ["AFR_aou_v2"], (
        "the registry check cannot see a newly-added AoU chain entry -- it is "
        "documentation, not a gate"
    )
    # ...and the shipped config still passes, so the control is not just noisy.
    assert _unregistered_aou_sources(_shipped_panel_cfg(), g.is_aou_source) == []


@pytest.mark.parametrize("source", sorted(PRODUCED_AOU_SOURCES))
def test_every_produced_aou_source_has_a_live_rule(source):
    smk_name, rule_name = PRODUCED_AOU_SOURCES[source]
    text = (RULES_DIR / smk_name).read_text()
    assert f"rule {rule_name}:" in text, (
        f"{source} is registered as PRODUCED by {smk_name}::{rule_name}, but "
        "that rule is not there"
    )


def _smk_sources() -> list[tuple[str, str]]:
    files = [(p.name, p.read_text()) for p in sorted(RULES_DIR.glob("*.smk"))]
    files.append((SNAKEFILE.name, SNAKEFILE.read_text()))
    return files


def _strip_hash_comments(text: str) -> str:
    """Lines whose ``lstrip()`` starts with ``#`` removed.

    The ``_shell_command_block`` discipline: a COMMENT satisfying its own regex
    broke two assertions in ``260805-w7u``, and the ``build_ld_rds_aou_eur``
    retirement note is an entire block of exactly such comments.
    """
    return "\n".join(
        ln for ln in text.splitlines() if not ln.lstrip().startswith("#")
    )


def test_the_retired_eur_producer_rule_exists_nowhere():
    for name, text in _smk_sources():
        assert "rule build_ld_rds_aou_eur" not in _strip_hash_comments(text), (
            f"{name} still declares the retired rule build_ld_rds_aou_eur"
        )


def test_no_non_comment_line_declares_the_eur_aou_artifact_path():
    """THE ARTIFACT HALF -- the one the retirement note skipped.

    The removal note verified that the RULE NAME had no references. It never
    checked the ARTIFACT PATH, which is why the TRANS head outlived its
    producer. Measured today: the only ``ld_reference/EUR_aou`` occurrence in
    any rule file is inside the ``#``-commented retirement note.
    """
    offenders = []
    for name, text in _smk_sources():
        for i, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            if "ld_reference/EUR_aou" in line:
                offenders.append(f"{name}:{i}: {line.strip()}")
    assert offenders == [], (
        "a NON-COMMENT rule line declares the unproduced EUR_aou artifact "
        "path:\n  " + "\n  ".join(offenders)
    )


# ==========================================================================
# (f) SHIPPED-CONFIG RESOLUTION INVARIANCE -- Track A cannot move
# ==========================================================================
@pytest.mark.parametrize("tree", TREES)
def test_shipped_config_resolution_is_identical_to_the_baseline(tmp_path, tree):
    """Every curated slug x ancestry x id-convention resolves to the byte-
    identical outcome the ``6b427bc`` resolver produced, under the SHIPPED
    ``strict_aou_only: false``.

    Whole-outcome equality (resolved string, or exception class + message) --
    never a status field.
    """
    new = _ld_panel()
    old = _ld_panel(BASELINE_REV)

    base = tmp_path / "ld_reference"
    panel = _reroot(_shipped_panel_cfg(), base)
    assert panel["strict_aou_only"] is False
    pairs = _region_pairs()
    assert len(pairs) >= 12, f"fixture is degenerate: only {len(pairs)} region pairs"
    _build_tree(panel, pairs, tree)

    resolved_cells = 0
    for region_id, region_safe in pairs:
        for anc in ANCESTRIES:
            got_new = _outcome(new, region_id, anc, _wrap(panel), region_safe)
            got_old = _outcome(old, region_id, anc, _wrap(panel), region_safe)
            assert got_new == got_old, (
                f"[tree={tree}] {region_safe}/{anc} moved off {BASELINE_REV}'s "
                f"resolution:\n  new={got_new}\n  old={got_old}"
            )
            if got_new[0] == "path":
                resolved_cells += 1

    if tree == "empty":
        assert resolved_cells == 0
    else:
        # NON-VACUITY: an all-raise fixture would make the equality meaningless.
        assert resolved_cells >= len(pairs), (
            f"[tree={tree}] only {resolved_cells} cells resolved to a real path; "
            "the equality above would be comparing two identical errors"
        )


def test_inverted_control_strict_trans_differs_from_the_baseline(tmp_path):
    """THE INVERTED CONTROL, permanent and in-suite.

    Without it the equality above is a tautology. Same fixture, same call --
    only ``strict_aou_only`` flipped ON and the TRANS head absent: the NEW
    resolver must RAISE where ``6b427bc``'s silently returned the 1kG EUR path.
    """
    new = _ld_panel()
    old = _ld_panel(BASELINE_REV)

    base = tmp_path / "ld_reference"
    panel = _reroot(_shipped_panel_cfg(), base)
    pairs = _region_pairs()
    _build_tree(panel, pairs, "no_aou")
    panel["strict_aou_only"] = True

    region_id, region_safe = "m2_region_00040__sub14", "SH2B3_12q24"
    got_new = _outcome(new, region_id, "TRANS", _wrap(panel), region_safe)
    got_old = _outcome(old, region_id, "TRANS", _wrap(panel), region_safe)

    assert got_new != got_old, (
        "the strict-mode TRANS outcome is UNCHANGED from the baseline -- "
        "finding G is not closed"
    )
    assert got_new[0] == "FileNotFoundError"
    assert "strict_aou_only" in got_new[1]
    assert got_old[0] == "path", (
        f"the baseline must SILENTLY return a path here (that IS finding G); "
        f"got {got_old}"
    )
    assert got_old[1] == str(base / "EUR" / f"{region_safe}.rds"), (
        f"the baseline resolved to {got_old[1]!r}, expected the 1kG EUR tail"
    )

    # EUR is untouched by the flip -- its chain head is non-AoU and present.
    eur_new = _outcome(new, region_id, "EUR", _wrap(panel), region_safe)
    eur_old = _outcome(old, region_id, "EUR", _wrap(panel), region_safe)
    assert eur_new == eur_old == (
        "path",
        str(base / "EUR_ukbb_pub" / f"{region_safe}.rds"),
    )
