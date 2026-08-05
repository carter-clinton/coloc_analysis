"""tests/m3/test_m3_ingest_convert_destale.py — m3-04c Task 2.

De-staling contract tests for the NCSU-side AoU LD consume path.

The ingest/convert rule files were written in m3-03 (Wave 3) against a
producer that no longer exists: a Hail BlockMatrix fire building a symmetric
AFR + EUR AoU panel over 322 compute cells. m3-02e replaced it with

  * AFR — ``src/python/run_native_ld_panel.py`` (native plink1.9, Hail-free,
    a single AoU Cloud Analysis VM) writing per-region ``.npz`` DIRECTLY to
    ``gs://<bucket>/ld/AFR_aou/{region_id}.npz`` over the 276 windows in
    ``config/ld_regions.tsv``; and
  * EUR — the PUBLIC UKBB 337k panel (``EUR_ukbb_pub`` chain head, ``$0``,
    built on NC State by ``m3_public_eur_ld.smk``).

So ``data/interim/aou_ld_exports/EUR_aou/`` will never be populated, and the
``region_id`` wildcard must admit the 123 subregion-split ids (m3-02b's
``m2_region_00040__sub00`` form) that ``r"m2_region_\\d{5}"`` silently excludes.
That exclusion is load-bearing, not cosmetic: m3-04c Task 1a's crosswalk maps
the Track A anchor ``SH2B3_12q24`` onto ``m2_region_00040__sub14``, so a
wildcard that rejects ``__sub`` ids makes the anchor's panel un-ingestable.

This module also pins the egress-planning contract: the bundle sizer already
shipped as ``src/python/ld_egress_bundle.py`` (``ade6066``), so
``src/python/plan_ld_egress.py`` must be a THIN CLI over it and
``src/python/validate_bundle_sizes.py`` must never be written.

No perimeter access, no billed action: every test here reads repo text or
drives the pure-Python planner over a synthetic size table.
"""
from __future__ import annotations

import csv
import importlib
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SRC_PY = REPO / "src" / "python"
INGEST_SMK = REPO / "src" / "snakemake" / "rules" / "m3_ingest_aou_ld.smk"
CONVERT_SMK = REPO / "src" / "snakemake" / "rules" / "m3_convert_npz_rds.smk"
LD_REGIONS_TSV = REPO / "config" / "ld_regions.tsv"
AUDIT_LOG = REPO / ".planning" / "amendments" / "aou-egress-audit-log.md"
PROTOCOL_ADDENDUM = (
    REPO / ".planning" / "amendments" / "m3-egress-and-validation-protocol-addendum.md"
)

_GB = 1_000_000_000

# The wildcard-constraint assignment form used in both rule files:
#     region_id=r"m2_region_\d{5}(__sub\d{2})?",
_REGION_ID_CONSTRAINT_RE = re.compile(r'region_id\s*=\s*r"([^"]+)"')
_ANCESTRY_CONSTRAINT_RE = re.compile(r'ancestry\s*=\s*r"([^"]+)"')


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _region_id_patterns(smk_text: str) -> list[str]:
    """Every ``region_id=r"..."`` wildcard constraint in a rule file."""
    return _REGION_ID_CONSTRAINT_RE.findall(smk_text)


def _unique_manifest_region_ids() -> list[str]:
    """The 276 unique region_id values in config/ld_regions.tsv (552 data rows)."""
    with LD_REGIONS_TSV.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        ids = {row["region_id"] for row in reader if row.get("region_id")}
    return sorted(ids)


# ---------------------------------------------------------------------------
# T3.1 — the region_id wildcard admits the subregion-split ids
# ---------------------------------------------------------------------------
def test_subregion_ids_match_the_region_wildcard():
    """Every one of the 276 manifest ids matches the wildcard in BOTH rule files.

    Driven from the REAL manifest, not a hand-written list. Today
    ``r"m2_region_\\d{5}"`` fails for the 123 ``__sub`` ids.
    """
    region_ids = _unique_manifest_region_ids()
    # Guard the oracle itself: the manifest really does carry 276 unique ids,
    # 123 of which are subregion splits. If this drifts the test below is
    # measuring something else.
    assert len(region_ids) == 276, f"expected 276 unique region ids, got {len(region_ids)}"
    n_sub = sum(1 for r in region_ids if "__sub" in r)
    assert n_sub == 123, f"expected 123 __sub ids, got {n_sub}"
    assert "m2_region_00040__sub14" in region_ids  # SH2B3_12q24's panel (Task 1a)
    assert "m2_region_00040__sub00" in region_ids
    assert "m2_region_00001" in region_ids

    for smk_path in (INGEST_SMK, CONVERT_SMK):
        patterns = _region_id_patterns(_read(smk_path))
        assert patterns, f"no region_id wildcard constraint found in {smk_path.name}"
        for pat in patterns:
            compiled = re.compile(pat)
            unmatched = [r for r in region_ids if compiled.fullmatch(r) is None]
            assert not unmatched, (
                f"{smk_path.name} region_id constraint {pat!r} excludes "
                f"{len(unmatched)} of {len(region_ids)} manifest ids, e.g. "
                f"{unmatched[:3]}"
            )
            # Named regression pins: the anchor's panel and a plain region.
            assert compiled.fullmatch("m2_region_00040__sub14") is not None
            assert compiled.fullmatch("m2_region_00040__sub00") is not None
            assert compiled.fullmatch("m2_region_00001") is not None
            # ...and the constraint must still REJECT non-manifest shapes, so
            # widening it did not degenerate into ".*".
            assert compiled.fullmatch("m2_region_0004") is None
            assert compiled.fullmatch("m2_region_00040__sub") is None
            assert compiled.fullmatch("not_a_region") is None


# ---------------------------------------------------------------------------
# T3.2 — the ingest gate is AFR-only
# ---------------------------------------------------------------------------
def test_ingest_is_afr_only():
    """EUR_aou is never produced (m3-02e Move 2), so the gate must not admit it."""
    text = _read(INGEST_SMK)

    assert "AFR|EUR" not in text, "the AFR-or-EUR ancestry alternation must be gone"

    ancestry_patterns = _ANCESTRY_CONSTRAINT_RE.findall(text)
    assert len(ancestry_patterns) == 2, (
        f"expected an ancestry constraint in BOTH wildcard_constraints blocks, "
        f"found {ancestry_patterns}"
    )
    for pat in ancestry_patterns:
        compiled = re.compile(pat)
        assert compiled.fullmatch("AFR") is not None
        assert compiled.fullmatch("EUR") is None, (
            f"ancestry constraint {pat!r} still admits EUR"
        )

    # The aggregate expand() must iterate AFR only -> at most 22 flags, not 44.
    assert re.search(r'ancestry=\[\s*"AFR"\s*\]', text), (
        "the aggregate expand() must iterate ancestry=[\"AFR\"] only"
    )
    assert not re.search(r'ancestry=\[[^\]]*"EUR"', text), (
        "the aggregate expand() still iterates EUR"
    )

    # The retired Hail BlockMatrix substrate must be gone from the docstring,
    # and the 322-cell basis with it (the real scope is 276 AFR regions).
    assert "blockmatrix" not in text.lower(), "Path A.3 BlockMatrix language is retired"
    assert "322" not in text, "the 322-cell basis is stale; the AFR scope is 276 regions"
    assert "run_native_ld_panel.py" in text, (
        "the module docstring must name the REAL producer"
    )
    assert "276" in text, "the 276-region AFR scope must be stated"


# ---------------------------------------------------------------------------
# T3.3 — the EUR_aou conversion rule is retired
# ---------------------------------------------------------------------------
def test_eur_aou_convert_rule_is_retired():
    """build_ld_rds_aou_eur could only ever fail on a missing input."""
    text = _read(CONVERT_SMK)
    assert "rule build_ld_rds_aou_eur" not in text
    assert "build_ld_rds_aou_afr" in text, "the AFR conversion rule must survive"
    assert "EUR_ukbb_pub" in text, (
        "the retirement must name EUR_ukbb_pub as the reason (m3-02e Move 2)"
    )
    assert "m3_public_eur_ld.smk" in text, (
        "the retirement must point at the live EUR producer"
    )


# ---------------------------------------------------------------------------
# T3.4 — the egress planner reuses the shipped helper
# ---------------------------------------------------------------------------
def test_egress_plan_uses_the_shipped_helper():
    """plan_ld_egress is a THIN CLI: no second bin-packer in the repo."""
    module_path = SRC_PY / "plan_ld_egress.py"
    assert module_path.is_file(), f"missing {module_path}"
    src = module_path.read_text(encoding="utf-8")

    assert "plan_egress_bundles" in src
    assert re.search(
        r"(from\s+ld_egress_bundle\s+import|import\s+ld_egress_bundle|"
        r'import_module\(\s*["\']ld_egress_bundle["\']\s*\))',
        src,
    ), "plan_ld_egress must import the shipped ld_egress_bundle helper"

    local_defs = re.findall(r"^\s*def\s+(\w+)", src, flags=re.MULTILINE)
    reimplementations = [
        name for name in local_defs if "bin_pack" in name or "split_bundle" in name
    ]
    assert not reimplementations, (
        f"plan_ld_egress must not reimplement grouping/splitting: {reimplementations}"
    )


# ---------------------------------------------------------------------------
# T3.5 — the planner groups by chromosome and splits over the cap
# ---------------------------------------------------------------------------
def test_egress_plan_groups_by_chromosome_and_splits_over_cap(tmp_path: Path):
    """Behavioural: drive the real CLI over a synthetic size table."""
    if str(SRC_PY) not in sys.path:
        sys.path.insert(0, str(SRC_PY))
    plan_ld_egress = importlib.import_module("plan_ld_egress")

    sizes_tsv = tmp_path / "sizes.tsv"
    rows = ["region_id\tchr\tbytes"]
    # chr1: 6 x 10 GB = 60 GB -> over the 50 GB cap -> chr1_a / chr1_b
    for i in range(6):
        rows.append(f"m2_region_{i:05d}\t1\t{10 * _GB}")
    # chr2: 2 x 5 GB = 10 GB -> a single chr2 bundle
    for i in range(10, 12):
        rows.append(f"m2_region_{i:05d}\t2\t{5 * _GB}")
    # a subregion-split id must survive the planner untouched
    rows.append(f"m2_region_00040__sub14\t12\t{3 * _GB}")
    sizes_tsv.write_text("\n".join(rows) + "\n", encoding="utf-8")

    out_tsv = tmp_path / "plan.tsv"
    rc = plan_ld_egress.main(
        ["--sizes-tsv", str(sizes_tsv), "--out", str(out_tsv)]
    )
    assert rc == 0
    assert out_tsv.is_file()

    bundle_rows = [
        line.split("\t")
        for line in out_tsv.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    header, data = bundle_rows[0], bundle_rows[1:]
    assert header[:6] == [
        "bundle_id",
        "chr",
        "n_cells",
        "total_bytes",
        "total_gb",
        "region_ids",
    ]
    by_id = {r[0]: dict(zip(header, r)) for r in data}

    assert "chr1_a" in by_id and "chr1_b" in by_id, sorted(by_id)
    assert "chr1" not in by_id
    cap_bytes = plan_ld_egress.EGRESS_CAP_GB * _GB
    for bid in ("chr1_a", "chr1_b"):
        assert int(by_id[bid]["total_bytes"]) <= cap_bytes

    assert "chr2" in by_id
    assert int(by_id["chr2"]["total_bytes"]) == 10 * _GB
    assert by_id["chr2"]["n_cells"] == "2"

    assert "chr12" in by_id
    assert "m2_region_00040__sub14" in by_id["chr12"]["region_ids"]

    # The trailing summary must report the split, so a reviewer sees it.
    text = out_tsv.read_text(encoding="utf-8")
    assert "n_bundles_over_cap" in text
    assert "chromosomes_split" in text


# ---------------------------------------------------------------------------
# T3.6 — the stale plan's module is NOT written
# ---------------------------------------------------------------------------
def test_no_validate_bundle_sizes_module():
    """Its function already shipped as ld_egress_bundle.plan_egress_bundles (ade6066)."""
    assert not (SRC_PY / "validate_bundle_sizes.py").exists(), (
        "src/python/validate_bundle_sizes.py duplicates ld_egress_bundle.py"
    )
    assert (SRC_PY / "ld_egress_bundle.py").is_file()


# ---------------------------------------------------------------------------
# T3.7 — the append-only audit log keeps its 2026-04-28 ruling byte-intact
# ---------------------------------------------------------------------------
_RULING_HEADING = "## Egress Classification Ruling (HARD GATE) — RULED PASS 2026-04-28"
_RULING_VERBATIM = (
    "letter is required: variant×variant LD R matrices are aggregate /\n"
    "derived statistics carrying no individual-level information and pass\n"
    "through standard AoU egress review (automated + manual reviewer\n"
    "pipeline) at egress-request time, governed by Carter's institutional\n"
    "NCSU faculty controlled-tier access — not by per-data-class custom\n"
    "rulings. All 44 production egress requests inherit this classification\n"
    "under standard egress review."
)
_APPEND_ONLY_LINE_9 = (
    "This file is **append-only**. Each entry documents one AoU export request"
)


def test_egress_audit_log_ruling_text_is_intact():
    text = _read(AUDIT_LOG)
    lines = text.splitlines()

    assert lines[8] == _APPEND_ONLY_LINE_9, (
        f"the append-only declaration at line 9 changed: {lines[8]!r}"
    )
    assert _RULING_HEADING in text
    assert _RULING_VERBATIM in text, "the 2026-04-28 ruling text was rewritten"
    assert "Aggregate summary statistic" in text
    # The header's 44-bundle scope line is HISTORY and must survive verbatim;
    # the correction is APPENDED, never edited in place.
    assert "**M3 egress scope:** 44 export bundles total (22 chromosomes × 2 ancestries" in text

    # ...and the scope correction must actually have been appended.
    assert "SCOPE CORRECTION" in text.upper(), (
        "the 44 -> at most 22 AFR-group scope correction was never appended"
    )
    assert "m3-egress-and-validation-protocol-addendum.md" in text, (
        "the appended section must point at the protocol addendum"
    )


# ---------------------------------------------------------------------------
# T3.8 — the two protocol redefinitions are RECORDED, not silently dropped
# ---------------------------------------------------------------------------
def test_protocol_addendum_records_both_redefinitions():
    assert PROTOCOL_ADDENDUM.is_file(), f"missing {PROTOCOL_ADDENDUM}"
    text = _read(PROTOCOL_ADDENDUM)
    assert len(text.splitlines()) >= 90

    # (a) the egress UNIT redefinition
    assert "run_native_ld_panel.py" in text
    assert "at most 22" in text
    assert "REQUEST-LEVEL" in text.upper()

    # (b) the EGRESS_CAP_GB provenance correction
    assert "CONSERVATIVE PROJECT WORKING CEILING" in text
    assert "documented hard AoU API limit" in text
    assert "ld_egress_bundle.py:9-15" in text

    # (c) the Check 2 redefinition, all three parts, plus the OSF consequence
    for part in ("2a", "2b", "2c"):
        assert re.search(rf"\b{part}\b", text), f"Check-2 part {part} is unrecorded"
    assert "STRUCTURALLY UNRUNNABLE" in text.upper()
    assert "OSF amendment-update" in text
    assert "pre-registered" in text.lower()


@pytest.mark.parametrize("token", ["9.2", "1000G"])
def test_addendum_cites_the_superseded_check(token: str):
    """The redefinition must name what it supersedes, so the trail is auditable."""
    assert PROTOCOL_ADDENDUM.is_file(), f"missing {PROTOCOL_ADDENDUM}"
    assert token in _read(PROTOCOL_ADDENDUM)
