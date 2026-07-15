"""RED-first tests for src/python/drop_occluded_from_sumstats.py (m3-07a Wave 0, T4).

LOCKSTEP is the load-bearing word of the pre-registered policy: a variant excluded
from the LD panel because an overlapping deletion's REF span makes its LD
structurally undefined MUST also leave the harmonized sumstats — the SAME variants,
in BOTH artifacts, or the panel and the sumstats disagree about which variants
exist and every downstream fine-map inherits the mismatch.

Contract (module.function, mirroring plink_ld_to_npz.plink_ld_to_npz):
    drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> dict

Key facts this suite pins:
  * the drop is keyed on the manifest's **GRCh37 (CHR, POS)** — the harmonized
    sumstats are GRCh37 and the panel<->sumstats join is (CHR,POS)-only,
    DROP-ONLY / no re-key [snp_id_bridge.R:107-121];
  * non-occluded rows come through BYTE-IDENTICAL (a "filter" that silently
    reformats surviving rows is a re-key by another name);
  * it is IDEMPOTENT (a second apply is a no-op) — the loop is resumable and this
    filter must survive being replayed after preemption;
  * every drop is LOGGED (the provenance requirement, not a debug nicety).

RED-for-the-right-reason: ``drop_occluded_from_sumstats`` does not exist yet (07c
builds it). It is imported INSIDE each test body so pytest COLLECTS cleanly and
each test fails as a test/assert failure, NOT a collection error.

Runs in smoke_dev py3.11 (pandas). No Hail.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_PYTHON = PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

# NOTE: NO module-level ``import drop_occluded_from_sumstats`` — see the docstring.

_HARMONIZED_HEADER = [
    "CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF", "N",
    "SNP_ID", "TRAIT", "ANCESTRY", "BUILD",
]

#: GRCh37 positions of the pair-4 tangle (lifted hinge-check anchors).
_SNP_C_B37 = 5_982_778      # the OCCLUDED variant -> must be dropped
_DEL3_B37 = 5_982_776       # the occluding deletion -> stays (only V is dropped)
_DEL4_B37 = 5_982_784       # the disjoint downstream deletion -> stays


def _sumstats_line(chrom: int, pos: int, trait: str = "bmi") -> str:
    return "\t".join(str(x) for x in [
        chrom, pos, "A", "G", 0.012, 0.004, 3.1e-3, 0.21, 15000,
        f"{chrom}:{pos}:A:G", trait, "AFR", "GRCh37",
    ])


def _write_sumstats(path: Path, positions: list[tuple[int, int]]) -> Path:
    """Write a harmonized AFR sumstats TSV with one row per (chr, pos)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(_HARMONIZED_HEADER)]
    lines += [_sumstats_line(c, p) for c, p in positions]
    path.write_text("\n".join(lines) + "\n")
    return path


def _write_manifest(path: Path, records: list[tuple[str, str, int, int]]) -> Path:
    """Write a minimal occlusion manifest TSV.

    Each record = (region_id, variant_id, chr, pos_grch37). Only the GRCh37
    (CHR,POS) key is load-bearing for the drop; the id/region columns ride along as
    provenance.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["\t".join(["region_id", "variant_id", "chr", "pos_grch37"])]
    lines += ["\t".join(str(x) for x in rec) for rec in records]
    path.write_text("\n".join(lines) + "\n")
    return path


def _body_lines(path: Path) -> list[str]:
    return [ln for ln in path.read_text().splitlines() if ln.strip()][1:]


# --------------------------------------------------------------------------- #
# 1. drops EXACTLY the manifest's GRCh37 (CHR, POS)                            #
# --------------------------------------------------------------------------- #

def test_drops_exactly_the_manifest_grch37_positions(tmp_path):
    """Exactly the manifest rows leave; the occluding deletion and the disjoint
    downstream deletion both SURVIVE (only the occluded V is excluded)."""
    import drop_occluded_from_sumstats as dof

    ss = _write_sumstats(tmp_path / "bmi.AFR.tsv", [
        (1, _DEL3_B37), (1, _SNP_C_B37), (1, _DEL4_B37), (1, 7_000_000), (2, 500),
    ])
    mf = _write_manifest(tmp_path / "occlusion_manifest.tsv", [
        ("m2_region_00001", "1:5922718:A:A", 1, _SNP_C_B37),
    ])
    out = tmp_path / "bmi.AFR.filtered.tsv"

    res = dof.drop_occluded_from_sumstats(ss, mf, out)

    kept = [(int(ln.split("\t")[0]), int(ln.split("\t")[1])) for ln in _body_lines(out)]
    assert (1, _SNP_C_B37) not in kept          # the occluded variant is GONE
    assert kept == [(1, _DEL3_B37), (1, _DEL4_B37), (1, 7_000_000), (2, 500)]
    assert res["n_dropped"] == 1


def test_drop_is_chr_aware_not_pos_only(tmp_path):
    """The key is (CHR, POS) — the SAME POS on a DIFFERENT chromosome must NOT be
    dropped. A POS-only key would silently delete unrelated variants genome-wide."""
    import drop_occluded_from_sumstats as dof

    ss = _write_sumstats(tmp_path / "bmi.AFR.tsv", [(1, _SNP_C_B37), (2, _SNP_C_B37)])
    mf = _write_manifest(tmp_path / "m.tsv", [("r1", "1:5922718:A:A", 1, _SNP_C_B37)])
    out = tmp_path / "out.tsv"

    dof.drop_occluded_from_sumstats(ss, mf, out)

    kept = [(int(ln.split("\t")[0]), int(ln.split("\t")[1])) for ln in _body_lines(out)]
    assert kept == [(2, _SNP_C_B37)]   # chr2 twin survives


def test_manifest_variant_absent_from_this_trait_is_a_noop(tmp_path):
    """An occluded variant with NO row in this trait's sumstats drops nothing —
    present-rate k/n < 1 is the normal case, not an error."""
    import drop_occluded_from_sumstats as dof

    ss = _write_sumstats(tmp_path / "ldl.AFR.tsv", [(1, 7_000_000), (1, 8_000_000)])
    mf = _write_manifest(tmp_path / "m.tsv", [("r1", "1:5922718:A:A", 1, _SNP_C_B37)])
    out = tmp_path / "out.tsv"

    res = dof.drop_occluded_from_sumstats(ss, mf, out)

    assert res["n_dropped"] == 0
    assert _body_lines(out) == _body_lines(ss)


# --------------------------------------------------------------------------- #
# 2. surviving rows are BYTE-IDENTICAL + no re-key                             #
# --------------------------------------------------------------------------- #

def test_non_occluded_rows_are_byte_identical(tmp_path):
    """Surviving rows pass through VERBATIM — same header, same bytes, same order.
    Drop-only, no reformatting (a reformat is a re-key by another name)."""
    import drop_occluded_from_sumstats as dof

    keep = [(1, _DEL3_B37), (1, 7_000_000), (2, 500)]
    ss = _write_sumstats(tmp_path / "bmi.AFR.tsv", [keep[0], (1, _SNP_C_B37), keep[1], keep[2]])
    mf = _write_manifest(tmp_path / "m.tsv", [("r1", "1:5922718:A:A", 1, _SNP_C_B37)])
    out = tmp_path / "out.tsv"

    src_lines = [ln for ln in ss.read_text().splitlines() if ln.strip()]
    dof.drop_occluded_from_sumstats(ss, mf, out)
    out_lines = [ln for ln in out.read_text().splitlines() if ln.strip()]

    assert out_lines[0] == src_lines[0]                       # header verbatim
    expected = [ln for ln in src_lines[1:] if f"\t{_SNP_C_B37}\t" not in ln]
    assert out_lines[1:] == expected                          # bytes + order verbatim


def test_does_not_rekey_snp_id_column(tmp_path):
    """SNP_ID is passed through untouched — the join is drop-only with NO re-key
    [snp_id_bridge.R:107-121]. Re-keying here would silently re-map variants."""
    import drop_occluded_from_sumstats as dof

    ss = _write_sumstats(tmp_path / "bmi.AFR.tsv", [(1, _DEL3_B37), (1, _SNP_C_B37)])
    mf = _write_manifest(tmp_path / "m.tsv", [("r1", "1:5922718:A:A", 1, _SNP_C_B37)])
    out = tmp_path / "out.tsv"

    dof.drop_occluded_from_sumstats(ss, mf, out)

    hdr = out.read_text().splitlines()[0].split("\t")
    assert hdr == _HARMONIZED_HEADER                    # column set/order unchanged
    snp_ids = [ln.split("\t")[hdr.index("SNP_ID")] for ln in _body_lines(out)]
    assert snp_ids == [f"1:{_DEL3_B37}:A:G"]           # id untouched, not re-derived


# --------------------------------------------------------------------------- #
# 3. idempotency (resume-safe: a replayed apply is a no-op)                    #
# --------------------------------------------------------------------------- #

def test_second_apply_is_a_noop(tmp_path):
    """Applying the filter to its OWN output drops nothing and changes no bytes —
    the loop is resumable and the filter must survive a replay."""
    import drop_occluded_from_sumstats as dof

    ss = _write_sumstats(tmp_path / "bmi.AFR.tsv", [(1, _DEL3_B37), (1, _SNP_C_B37), (1, 7_000_000)])
    mf = _write_manifest(tmp_path / "m.tsv", [("r1", "1:5922718:A:A", 1, _SNP_C_B37)])
    out1 = tmp_path / "pass1.tsv"
    out2 = tmp_path / "pass2.tsv"

    res1 = dof.drop_occluded_from_sumstats(ss, mf, out1)
    res2 = dof.drop_occluded_from_sumstats(out1, mf, out2)

    assert res1["n_dropped"] == 1
    assert res2["n_dropped"] == 0                       # nothing left to drop
    assert out2.read_bytes() == out1.read_bytes()       # byte-identical no-op


# --------------------------------------------------------------------------- #
# 4. every drop is LOGGED (provenance, not a debug nicety)                     #
# --------------------------------------------------------------------------- #

def test_logs_each_drop(tmp_path, capsys):
    """Each dropped row emits an auditable log line naming the coordinate — the
    manifest is the durable record, the log is the in-run witness."""
    import drop_occluded_from_sumstats as dof

    ss = _write_sumstats(tmp_path / "bmi.AFR.tsv", [
        (1, _DEL3_B37), (1, _SNP_C_B37), (1, 7_000_000), (1, 8_000_000),
    ])
    mf = _write_manifest(tmp_path / "m.tsv", [
        ("r1", "1:5922718:A:A", 1, _SNP_C_B37),
        ("r1", "1:8000000:A:G", 1, 8_000_000),
    ])
    out = tmp_path / "out.tsv"

    res = dof.drop_occluded_from_sumstats(ss, mf, out)
    err = capsys.readouterr().err

    assert res["n_dropped"] == 2
    assert str(_SNP_C_B37) in err          # each dropped coordinate is named
    assert "8000000" in err


def test_result_reports_counts(tmp_path):
    """The result dict carries durable counts (n_in / n_dropped / n_out) so the
    lockstep is auditable against the panel's n_dropped_occluded."""
    import drop_occluded_from_sumstats as dof

    ss = _write_sumstats(tmp_path / "bmi.AFR.tsv", [
        (1, _DEL3_B37), (1, _SNP_C_B37), (1, 7_000_000),
    ])
    mf = _write_manifest(tmp_path / "m.tsv", [("r1", "1:5922718:A:A", 1, _SNP_C_B37)])
    out = tmp_path / "out.tsv"

    res = dof.drop_occluded_from_sumstats(ss, mf, out)

    assert res["n_in"] == 3
    assert res["n_dropped"] == 1
    assert res["n_out"] == 2
    assert res["n_in"] - res["n_dropped"] == res["n_out"]
    assert len(_body_lines(out)) == res["n_out"]
