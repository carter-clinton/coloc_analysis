"""tests/m3/test_convert_aggregate_target.py — 260805-23d Task 4 (BLOCKER-C).

WHY THIS MODULE EXISTS.

``src/python/ld_panel.py::resolve_ld_path`` returns the FIRST path in the
``ld_panel`` chain that ALREADY EXISTS (``ld_panel.py:87``). A chain head that
has not been built yet is therefore SKIPPED rather than pulled into the DAG as
a to-be-built input. ``src/snakemake/rules/m3_convert_npz_rds.smk`` declared
exactly one rule (``build_ld_rds_aou_afr``) and no aggregate target, and
``Snakefile``'s ``ALL_TARGETS`` (:185-209) names no ``AFR_aou/*.rds``.

Consequence, verified on this tree: after a successful ~11-day billed AoU fire
banks 276 ``.npz``, ``snakemake all`` finds no ``AFR_aou/*.rds``, walks the
chain past the un-built head down to the 1000G ``n=661`` tail, and reports
SUCCESS. The per-region rule IS reachable when a path is named explicitly (a
clean 3-job DAG for ``data/processed/ld_reference/AFR_aou/m2_region_00040__sub14.rds``
was observed), so the missing piece is WIRING, not logic.

WHAT IS PINNED HERE. One aggregate target, ``m3_convert_aou_afr_rds_all``,
mirroring the already-working ingest-side shape
``m3_ingest_aou_export_arrives_all`` (``m3_ingest_aou_ld.smk:230-246``), whose
input set is DERIVED from ``config/ld_regions.tsv`` — not hardcoded, not a
glob that can silently under-cover — and equals the manifest's AFR region set
EXACTLY (276 ids: 153 whole + 123 m3-02b ``__sub`` splits, including
``m2_region_00040__sub14``, the Track A anchor's panel).

DISCLOSED RESIDUAL, pinned by test 3 rather than papered over: this makes the
conversion invocable as ONE operator command. It does NOT make ``snakemake all``
self-sufficient — ``resolve_ld_path``'s first-EXISTING semantics are unchanged
and out of scope — exactly as the ingest side already discloses.

NEGATIVE CONTROLS. Every load-bearing assertion here is exercised against an
input that must make it FAIL: the pre-change ``.smk`` recovered with
``git show 5ec33bd:``, a truncated 275-id target set, a 2-row synthetic
manifest, an all-EUR manifest, and the retired narrow ``r"m2_region_\\d{5}"``
wildcard. Five assertions in the m3-04c change set turned out structurally
incapable of failing; that is why this is mandatory
(``[[feedback_coverage_assertion_can_be_false_invariant]]``).

No perimeter access, no billed action, no DAG build: every test reads repo
text, the shipped manifest, or execs the shipped helper over a tmp file.
"""
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CONVERT_SMK = REPO / "src" / "snakemake" / "rules" / "m3_convert_npz_rds.smk"
INGEST_SMK = REPO / "src" / "snakemake" / "rules" / "m3_ingest_aou_ld.smk"
SNAKEFILE = REPO / "Snakefile"
LD_REGIONS_TSV = REPO / "config" / "ld_regions.tsv"

AGGREGATE_RULE = "m3_convert_aou_afr_rds_all"
INGEST_AGGREGATE_RULE = "m3_ingest_aou_export_arrives_all"

# The pre-change tree. m3_convert_npz_rds.smk is byte-identical at 5ec33bd and
# at the Task 3 tip, so this really is the "before" text for THIS task.
BASE_COMMIT = "5ec33bd"

# The manifest oracle. Derived below from config/ld_regions.tsv; these numbers
# are the guard on the oracle itself, not the source of the target set.
N_AFR_REGIONS = 276
N_SUBREGION_IDS = 123
N_WHOLE_REGION_IDS = 153
ANCHOR_PANEL_ID = "m2_region_00040__sub14"  # SH2B3_12q24 (m3-04c Task 1a)

_REGION_ID_CONSTRAINT_RE = re.compile(r'region_id\s*=\s*r"([^"]+)"')
# The narrow constraint retired by m3-04c Task 2; used as a negative control.
RETIRED_NARROW_CONSTRAINT = r"m2_region_\d{5}"


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _pre_change_text(path_in_repo: str) -> str:
    """The file as it stood at BASE_COMMIT (the negative-control source)."""
    return subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:{path_in_repo}"],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _rule_block(text: str, rule_name: str) -> str | None:
    """The full body of ``rule <name>:`` — every line until the next dedent.

    Returns None when the rule is not declared at all.
    """
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^rule\s+{re.escape(rule_name)}\s*:\s*$", line):
            start = i
            break
    if start is None:
        return None
    body = [lines[start]]
    for line in lines[start + 1 :]:
        if line.strip() and not line.startswith((" ", "\t")):
            break
        body.append(line)
    return "\n".join(body)


def _has_aggregate_rule(text: str) -> bool:
    """The shape check: a rule with an input, an output sentinel and a touch.

    This is the assertion under test in test 1; it is applied to BOTH the
    current text (must be True) and the pre-change text (must be False), so it
    is provably capable of both answers.
    """
    block = _rule_block(text, AGGREGATE_RULE)
    if block is None:
        return False
    return (
        "input:" in block
        and "output:" in block
        and "sentinel=" in block
        and "shell:" in block
        and "touch {output.sentinel}" in block
    )


# ---------------------------------------------------------------------------
# Manifest oracle — read the REAL file, independently of the .smk
# ---------------------------------------------------------------------------
def _manifest_afr_region_ids(manifest: Path = LD_REGIONS_TSV) -> set[str]:
    with manifest.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return {
            row["region_id"]
            for row in reader
            if row.get("ancestry") == "AFR" and row.get("region_id")
        }


def _assert_covers_all_afr(region_ids) -> None:
    """THE load-bearing coverage assertion. Shared by the real check and by
    every negative control, so the controls exercise this exact code."""
    got = set(region_ids)
    expected = _manifest_afr_region_ids()
    assert len(expected) == N_AFR_REGIONS, (
        f"oracle drift: config/ld_regions.tsv now has {len(expected)} AFR "
        f"region ids, not {N_AFR_REGIONS}"
    )
    assert len(got) == N_AFR_REGIONS, (
        f"aggregate target covers {len(got)} AFR regions, expected "
        f"{N_AFR_REGIONS}; missing={sorted(expected - got)[:5]} "
        f"extra={sorted(got - expected)[:5]}"
    )
    assert got == expected, (
        f"aggregate target set != manifest AFR set; "
        f"missing={sorted(expected - got)[:5]} extra={sorted(got - expected)[:5]}"
    )
    assert sum(1 for r in got if "__sub" in r) == N_SUBREGION_IDS
    assert sum(1 for r in got if "__sub" not in r) == N_WHOLE_REGION_IDS
    assert ANCHOR_PANEL_ID in got, "the Track A anchor's panel must be covered"


# ---------------------------------------------------------------------------
# Execute the SHIPPED helper in isolation.
#
# importlib cannot import a .smk (Snakemake directives are not Python), so the
# region-id helper is written as a plain function and the block that defines
# M3_LD_REGIONS_MANIFEST / _afr_aou_region_ids / M3_AFR_AOU_RDS is sliced out
# and exec'd with only stdlib names bound. This runs the REAL shipped code --
# it is not a re-implementation, so it cannot drift from what the rule expands.
# ---------------------------------------------------------------------------
def _extract_region_id_block(text: str) -> str:
    lines = text.splitlines()
    start = None
    end = None
    for i, line in enumerate(lines):
        if start is None and line.startswith("M3_LD_REGIONS_MANIFEST"):
            start = i
        if start is not None and line.startswith("M3_AFR_AOU_RDS"):
            for j in range(i, len(lines)):
                if lines[j].startswith("]"):
                    end = j
                    break
            break
    assert start is not None, (
        "m3_convert_npz_rds.smk defines no M3_LD_REGIONS_MANIFEST; the "
        "aggregate target's region ids are not derived from the manifest"
    )
    assert end is not None, "M3_AFR_AOU_RDS list assignment not found/closed"
    block = "\n".join(lines[start : end + 1])
    for name in ("M3_LD_REGIONS_MANIFEST", "_afr_aou_region_ids", "M3_AFR_AOU_RDS"):
        assert name in block, f"{name} missing from the extracted block"
    return block


def _exec_region_id_block(text: str) -> dict:
    ns: dict = {
        "__builtins__": __builtins__,
        "os": os,
        "sys": sys,
        "csv": csv,
        "Path": Path,
        "_M3_PROJECT_ROOT": REPO,
        "LD_REF_DIR": "data/processed/ld_reference",
    }
    exec(  # noqa: S102 - executing shipped repo source is the point
        "from __future__ import annotations\n" + _extract_region_id_block(text),
        ns,
    )
    return ns


def _write_manifest(path: Path, rows: list[tuple[str, str]]) -> Path:
    """A minimal ld_regions.tsv with only the two columns the helper reads."""
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(["region_id", "ancestry"])
        for rid, anc in rows:
            writer.writerow([rid, anc])
    return path


# ---------------------------------------------------------------------------
# T4.1 — the aggregate rule exists, in the ingest side's proven shape
# ---------------------------------------------------------------------------
def test_aggregate_convert_rule_exists():
    """m3_convert_npz_rds.smk declares the aggregate target, mirroring
    m3_ingest_aou_export_arrives_all rather than inventing a new shape."""
    text = _read(CONVERT_SMK)

    # Guard the oracle: the ingest-side pattern really does have this shape.
    ingest_block = _rule_block(_read(INGEST_SMK), INGEST_AGGREGATE_RULE)
    assert ingest_block is not None, (
        f"{INGEST_AGGREGATE_RULE} not found; the shape being mirrored is gone"
    )
    assert "sentinel=" in ingest_block and "touch {output.sentinel}" in ingest_block

    assert _has_aggregate_rule(text), (
        f"{CONVERT_SMK.name} must declare `rule {AGGREGATE_RULE}:` with an "
        f"input, an output sentinel and a shell touch"
    )

    block = _rule_block(text, AGGREGATE_RULE)
    assert "M3_AFR_AOU_RDS" in block, (
        "the aggregate's input must be the derived AFR .rds list, not a glob "
        "or a hardcoded subset"
    )
    # Exactly one declaration, whole file.
    assert text.count(f"rule {AGGREGATE_RULE}:") == 1

    # NEGATIVE CONTROL: the same shape check on the pre-change file must FAIL.
    old = _pre_change_text("src/snakemake/rules/m3_convert_npz_rds.smk")
    assert not _has_aggregate_rule(old), (
        f"NEGATIVE CONTROL BROKEN: {AGGREGATE_RULE} appears to already exist "
        f"at {BASE_COMMIT}; the assertion above cannot be discriminating"
    )
    assert _rule_block(old, "build_ld_rds_aou_afr") is not None, (
        "sanity: the per-region rule did exist pre-change, so _rule_block "
        "genuinely finds rules in that text"
    )


# ---------------------------------------------------------------------------
# T4.2 — coverage: exactly the 276 manifest AFR regions, derived from the file
# ---------------------------------------------------------------------------
def test_aggregate_covers_every_afr_region_exactly(tmp_path, capsys):
    text = _read(CONVERT_SMK)
    ns = _exec_region_id_block(text)

    # The shipped default must point at the real manifest.
    assert ns["M3_LD_REGIONS_MANIFEST"] == str(LD_REGIONS_TSV)

    ids = ns["_afr_aou_region_ids"]()
    assert ids == sorted(set(ids)), "helper must return sorted unique ids"
    _assert_covers_all_afr(ids)

    # ...and the rule's actual input list is those ids as AFR_aou .rds paths.
    rds = ns["M3_AFR_AOU_RDS"]
    assert len(rds) == N_AFR_REGIONS
    stems = {os.path.basename(p)[: -len(".rds")] for p in rds}
    _assert_covers_all_afr(stems)
    for p in rds:
        assert p.startswith("data/processed/ld_reference/AFR_aou/")
        assert p.endswith(".rds")
    assert f"data/processed/ld_reference/AFR_aou/{ANCHOR_PANEL_ID}.rds" in rds

    # NEGATIVE CONTROL 1 (the one Carter asked for by name): a TRUNCATED target
    # set must fail the coverage assertion. If it does not, the assertion is
    # decorative.
    with pytest.raises(AssertionError):
        _assert_covers_all_afr(sorted(ids)[:-1])
    with pytest.raises(AssertionError):
        _assert_covers_all_afr([])

    # NEGATIVE CONTROL 2: a 2-row synthetic manifest -- the helper genuinely
    # READS the file it is handed rather than returning a baked-in list.
    tiny = _write_manifest(
        tmp_path / "tiny.tsv", [("m2_region_00001", "AFR"), ("m2_region_00002", "AFR")]
    )
    tiny_ids = ns["_afr_aou_region_ids"](str(tiny))
    assert tiny_ids == ["m2_region_00001", "m2_region_00002"]
    with pytest.raises(AssertionError):
        _assert_covers_all_afr(tiny_ids)

    # NEGATIVE CONTROL 3: the AFR filter is live, not a pass-through.
    eur_only = _write_manifest(
        tmp_path / "eur.tsv", [("m2_region_00001", "EUR"), ("m2_region_00002", "EUR")]
    )
    capsys.readouterr()
    assert ns["_afr_aou_region_ids"](str(eur_only)) == []
    assert "WARN" in capsys.readouterr().err, (
        "an empty AFR set must be LOUD on stderr, not a silently empty target"
    )

    # NEGATIVE CONTROL 4: a region present in the manifest but with no AFR row
    # SHRINKS the target set -- that must surface LOUDLY, not silently.
    shrunk = _write_manifest(
        tmp_path / "shrunk.tsv",
        [("m2_region_00001", "AFR"), ("m2_region_00002", "EUR")],
    )
    capsys.readouterr()
    assert ns["_afr_aou_region_ids"](str(shrunk)) == ["m2_region_00001"]
    err = capsys.readouterr().err
    assert "WARN" in err and "m2_region_00002" in err, (
        "a region with no AFR row must be named on stderr; a shrinking target "
        "set is exactly the BLOCKER-C failure mode repeating one level down"
    )

    # NEGATIVE CONTROL 5: a missing manifest is [] + LOUD, never an exception
    # (the DAG must still build on a fresh clone) and never a silent empty.
    capsys.readouterr()
    assert ns["_afr_aou_region_ids"](str(tmp_path / "nope.tsv")) == []
    assert "WARN" in capsys.readouterr().err

    # No AFR row is missing on the REAL manifest today: it must be quiet.
    capsys.readouterr()
    ns["_afr_aou_region_ids"]()
    assert capsys.readouterr().err == "", (
        "the real manifest is complete, so the helper must not cry wolf"
    )


# ---------------------------------------------------------------------------
# T4.3 — deliberately NOT in ALL_TARGETS, and the file says why
# ---------------------------------------------------------------------------
def _afr_aou_code_lines(text: str) -> list[str]:
    """Non-comment lines mentioning AFR_aou."""
    return [
        line
        for line in text.splitlines()
        if "AFR_aou" in line and not line.lstrip().startswith("#")
    ]


def test_aggregate_is_not_in_all_targets_and_says_why():
    snakefile = _read(SNAKEFILE)

    # ALL_TARGETS is assembled entirely from names defined in the Snakefile, so
    # "no non-comment Snakefile line mentions AFR_aou" is sufficient: no
    # AFR_aou path can reach ALL_TARGETS. Same deliberate exclusion as
    # m3_ingest_aou_export_arrives_all -- the .npz arrive by a MANUAL egress.
    assert _afr_aou_code_lines(snakefile) == [], (
        "an AFR_aou path reached the Snakefile's target assembly; `snakemake "
        "all` would then demand an un-egressed AoU panel for every run"
    )
    assert "ALL_TARGETS" in snakefile and _rule_block(snakefile, "all") is not None

    # NEGATIVE CONTROL: the checker must reject a real code line.
    assert _afr_aou_code_lines(
        'ALL_TARGETS = LD_TARGETS + ["data/processed/ld_reference/AFR_aou/x.rds"]'
    ) != []

    # The rule must state the exclusion and name the operator invocation.
    text = _read(CONVERT_SMK)
    block = _rule_block(text, AGGREGATE_RULE)
    assert block is not None, f"{AGGREGATE_RULE} not declared"
    # Prose lives in the comment banner immediately above the rule; search the
    # whole file, then pin that it is the aggregate being discussed.
    assert "NOT IN ALL_TARGETS" in text, (
        "the file must state that the aggregate is deliberately excluded from "
        "ALL_TARGETS, and why"
    )
    assert f"snakemake {AGGREGATE_RULE}" in text, (
        "the file must name the exact command the operator has to invoke"
    )
    assert "manual egress" in text.lower()
    assert ".convert_all.complete" in text, "the sentinel must be named"
    # The DISCLOSED RESIDUAL must be written down, not implied.
    assert "resolve_ld_path" in text and "first" in text.lower(), (
        "the first-EXISTING resolver semantics -- the reason `snakemake all` "
        "still cannot pull an unbuilt panel in -- must be disclosed in situ"
    )

    # NEGATIVE CONTROL: none of that prose exists pre-change.
    old = _pre_change_text("src/snakemake/rules/m3_convert_npz_rds.smk")
    assert "NOT IN ALL_TARGETS" not in old
    assert f"snakemake {AGGREGATE_RULE}" not in old


# ---------------------------------------------------------------------------
# T4.4 — every id the aggregate enumerates is buildable through the wildcard
# ---------------------------------------------------------------------------
def test_wildcard_constraint_still_admits_subregions():
    """The aggregate's 276 paths must all be reachable via build_ld_rds_aou_afr.

    Guards the pair: adding the aggregate while the region_id constraint
    regresses would produce a target list Snakemake cannot route.
    """
    text = _read(CONVERT_SMK)
    ns = _exec_region_id_block(text)
    stems = sorted({os.path.basename(p)[: -len(".rds")] for p in ns["M3_AFR_AOU_RDS"]})
    assert len(stems) == N_AFR_REGIONS

    patterns = _REGION_ID_CONSTRAINT_RE.findall(text)
    assert patterns, "no region_id wildcard constraint in m3_convert_npz_rds.smk"

    for pat in patterns:
        compiled = re.compile(pat)
        unmatched = [s for s in stems if compiled.fullmatch(s) is None]
        assert not unmatched, (
            f"region_id constraint {pat!r} cannot route {len(unmatched)} of "
            f"{len(stems)} aggregate targets, e.g. {unmatched[:3]}"
        )
        assert compiled.fullmatch(ANCHOR_PANEL_ID) is not None
        assert compiled.fullmatch("m2_region_00001") is not None
        # ...and it has not degenerated into ".*".
        assert compiled.fullmatch("m2_region_0004") is None
        assert compiled.fullmatch("not_a_region") is None
        assert compiled.fullmatch(".convert_all.complete") is None

    # NEGATIVE CONTROL: the constraint retired by m3-04c Task 2 fails this
    # exact check on the exact same target set (it excludes all 123 __sub ids).
    narrow = re.compile(RETIRED_NARROW_CONSTRAINT)
    narrow_unmatched = [s for s in stems if narrow.fullmatch(s) is None]
    assert len(narrow_unmatched) == N_SUBREGION_IDS, (
        "NEGATIVE CONTROL BROKEN: the retired narrow constraint should exclude "
        f"{N_SUBREGION_IDS} subregion ids, it excluded {len(narrow_unmatched)}"
    )
