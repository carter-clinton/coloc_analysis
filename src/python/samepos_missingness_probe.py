"""SAME-POSITION missingness probe — is the co-located class CO-CALLED or COMPLEMENTARY?

(1) WHY IT EXISTS
------------------
The POSTED occlusion predicate's left bound is STRICT::

    d.index != v.index  and  d.pos < v.pos <= d.pos + len(REF_d) - 1

so a variant at ``v.pos == d.pos`` is invisible to it BY CONSTRUCTION — not
mis-measured, UNLOOKED-AT. That blind spot is not small. Same-position rows are
~7-11% of rows in every region sampled; region 1 alone has 8,358 duplicate-
position rows at 2,645 duplicate sites, mean multiplicity 3.16, max 21 (the
POSTED scope statement,
``.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md:228-244``).

Whether that blind spot hides anything depends on ONE empirical fact: at a
same-position site, are the sibling rows called TOGETHER, or does one row's ALT
carriers show up MISSING at the other?

(2) THE DECISION RULE — STATED HERE, BEFORE ANY RUN
----------------------------------------------------
``co_called``      the site being called implies BOTH rows are called.
                   Intersecting ``called(a)`` with ``called(b)`` strips nothing,
                   so the same-position class CANNOT produce an undefined pair
                   by co-location alone => THE CLASS IS EMPTY.

``complementary``  a row's ALT carriers are MISSING at its same-position
                   sibling. ``called(a) ∩ called(b)`` then strips exactly a's
                   carriers, which is the mechanism that makes a member
                   invariant on the intersection => THE CLASS IS REAL, and the
                   strict left bound is a genuine blind spot.

``mixed``          neither. Reported as itself, never rounded into a story.

Writing the rule down BEFORE the run is the point: a rule chosen after seeing
the number is not a rule.

(3) THE COMPETING INFERENCE, AND ITS STATUS
--------------------------------------------
The pipeline splits multiallelics with ``hl.split_multi_hts``
(``src/python/aou_ld_panel.py:2138``). Its DOCUMENTED behaviour downcodes
other-ALT carriers to REFERENCE — not to MISSING — which predicts ``co_called``
and an EMPTY class.

⚠ THAT IS AN INFERENCE FROM DOCUMENTATION, NOT A MEASUREMENT. Hail is
not installed on this node, so the claim CANNOT be verified here. The reviewer asked
for a measurement rather than an inference, and this probe is that measurement.

THE STANDING RULE, verbatim: a mismatch between the inference and the
measurement is a FINDING TO REPORT, never a number to adjust.

(4) WHAT THIS IS NOT
---------------------
It changes NO criterion, NO threshold and NO policy. It is not on the fire path.
It states NO prevalence. The two label thresholds are REPORTING BINS, never
gates — nothing is included or excluded on their basis. A capped run is a
SAMPLE and reports its census (``n_sites_total`` beside ``n_sites_measured``,
plus both skip counters) so it can never be read as a census.

(5) EGRESS
-----------
Aggregate counts, fractions, histogram bins and VARIANT IDS only. No per-sample
vector, no sample identifier, no dosage value ever enters the summary. The
per-pair TSV stays in-perimeter.

Pure stdlib + numpy. No Hail, no plink, no network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import OrderedDict
from pathlib import Path
from typing import NamedTuple

import numpy as np

# ONE .bed byte contract, ONE window selection, ONE manifest parse. Identity is
# asserted by tests/m3/test_samepos_missingness_probe.py::
# test_the_bed_reader_is_the_scanners_own -- a second implementation of any of
# these would drift from the scanner the day either moves.
# `_read_regions_tsv` is PRIVATE BY NAME, SHARED BY DESIGN.
from pairwise_completeness_scan import (  # noqa: F401
    BedReader,
    DEFAULT_ANCESTRY,
    _read_regions_tsv,
    iter_bim_windows,
)

_COL_CHR = 0
_COL_VID = 1
_COL_BP = 3

#: The label vocabulary. NEUTRAL BY CONSTRUCTION: every label describes the
#: MEASUREMENT (how the two rows are called relative to each other) and none
#: names a mechanism, a cause or a conclusion. Pinned by exact set equality.
LABELS: tuple = ("co_called", "complementary", "mixed")

#: ⚠ REPORTING BINS, NOT GATES. Nothing is included, excluded, filtered or
#: decided on the basis of these two numbers; they only choose which of the
#: three words labels a row. The underlying fraction is emitted per pair and
#: histogrammed pooled, so any reader can re-bin without re-running.
CO_CALLED_MAX_FRAC: float = 0.05
COMPLEMENTARY_MIN_FRAC: float = 0.95

DEFAULT_MAX_MULTIPLICITY: int = 8
DEFAULT_MAX_SITES_PER_REGION: int = 200

#: Histogram edges for `frac_carriers_a_missing_at_b`. The quantity is expected
#: to be BIMODAL under either hypothesis, so it is HISTOGRAMMED and its two tail
#: counts reported -- never averaged, which would erase exactly the structure
#: the probe exists to see.
_FRAC_BIN_EDGES: tuple = (0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0)


class PairRecord(NamedTuple):
    """One ORDERED (a, b) within-site pair. Field order IS :data:`TSV_COLUMNS`."""

    region_id: str
    chrom: str
    pos: int
    a_index: int
    a_vid: str
    b_index: int
    b_vid: str
    n_samples: int
    n_called_a: int
    n_called_b: int
    n_both: int
    n_carriers_a: int
    n_carriers_a_called_at_b: int
    frac_carriers_a_missing_at_b: float
    a_invariant_on_both: bool
    b_invariant_on_both: bool
    undefined: bool
    label: str


TSV_COLUMNS: tuple = PairRecord._fields


def label_for_fraction(frac: float) -> str:
    """Bin ``frac_carriers_a_missing_at_b`` into :data:`LABELS`.

    ⚠ A REPORTING BIN. This decides a WORD, never an inclusion.
    """
    if frac <= CO_CALLED_MAX_FRAC:
        return "co_called"
    if frac >= COMPLEMENTARY_MIN_FRAC:
        return "complementary"
    return "mixed"


def _frac_bin(frac: float) -> str:
    for lo, hi in zip(_FRAC_BIN_EDGES, _FRAC_BIN_EDGES[1:]):
        if frac <= hi:
            return f"{lo:g}-{hi:g}"
    return f"{_FRAC_BIN_EDGES[-1]:g}+"


def group_same_position_rows(indexed_rows) -> "OrderedDict":
    """Group in-window rows by ``(chrom, pos)``; keep ONLY multiplicity >= 2.

    File order is preserved, which is what makes the capped sample a
    DETERMINISTIC PREFIX with no RNG anywhere.
    """
    groups: "OrderedDict" = OrderedDict()
    for index, row in indexed_rows:
        key = (str(row[_COL_CHR]), int(row[_COL_BP]))
        groups.setdefault(key, []).append((int(index), row))
    return OrderedDict((k, v) for k, v in groups.items() if len(v) >= 2)


def measure_pair(reader, region_id: str, a, b) -> PairRecord:
    """Measure ONE ordered pair of same-position rows from the ``.bed`` bytes."""
    a_index, a_row = a
    b_index, b_row = b
    ga = reader.read_variant(a_index)
    gb = reader.read_variant(b_index)

    called_a = ga.called
    called_b = gb.called
    both = called_a & called_b
    carriers_a = ga.dosage > 0

    n_carriers_a = int(carriers_a.sum())
    n_carriers_a_called_at_b = int((carriers_a & called_b).sum())
    # An empty carrier set yields 0.0 -- "none of a's carriers are missing at b"
    # is vacuously true, and inventing a NaN here would poison the histogram.
    frac = (
        0.0 if n_carriers_a == 0
        else 1.0 - (n_carriers_a_called_at_b / n_carriers_a)
    )

    a_inv = bool(np.unique(ga.dosage[both]).size <= 1)
    b_inv = bool(np.unique(gb.dosage[both]).size <= 1)

    return PairRecord(
        region_id=region_id,
        chrom=str(a_row[_COL_CHR]),
        pos=int(a_row[_COL_BP]),
        a_index=int(a_index),
        a_vid=str(a_row[_COL_VID]),
        b_index=int(b_index),
        b_vid=str(b_row[_COL_VID]),
        n_samples=int(reader.n_samples),
        n_called_a=int(called_a.sum()),
        n_called_b=int(called_b.sum()),
        n_both=int(both.sum()),
        n_carriers_a=n_carriers_a,
        n_carriers_a_called_at_b=n_carriers_a_called_at_b,
        frac_carriers_a_missing_at_b=float(frac),
        a_invariant_on_both=a_inv,
        b_invariant_on_both=b_inv,
        # UNDEFINED is the pairwise property itself: r is undefined iff EITHER
        # member is constant within the intersection. Symmetric by construction.
        undefined=bool(a_inv or b_inv),
        label=label_for_fraction(float(frac)),
    )


def measure_region(reader, region_id, indexed_rows, *, max_multiplicity,
                   max_sites_per_region):
    """Measure one region. Returns ``(records, region_summary)``.

    ⚠ EVERY SKIP IS COUNTED. A silent skip is a masked measurement
    (`feedback_skip_guard_masks_not_fixes`), so both the multiplicity skip and
    the sample cap report themselves beside the totals.
    """
    groups = group_same_position_rows(indexed_rows)

    over_multiplicity = [k for k, v in groups.items() if len(v) > max_multiplicity]
    kept = OrderedDict(
        (k, v) for k, v in groups.items() if len(v) <= max_multiplicity
    )
    n_sites_total = len(kept)

    # DETERMINISTIC PREFIX SAMPLE in file order. No RNG, so a re-run on the same
    # input is byte-identical and the sample is reproducible from the inputs
    # alone.
    measured_keys = list(kept.keys())[:max_sites_per_region]
    n_sites_measured = len(measured_keys)

    records = []
    for key in measured_keys:
        rows = kept[key]
        for i, a in enumerate(rows):
            for j, b in enumerate(rows):
                if i == j:
                    continue
                records.append(measure_pair(reader, region_id, a, b))

    label_counts = {lab: 0 for lab in LABELS}
    frac_hist: dict = {}
    undefined_keys: "OrderedDict" = OrderedDict()
    n_frac_eq_0 = 0
    n_frac_eq_1 = 0
    for r in records:
        label_counts[r.label] += 1
        b = _frac_bin(r.frac_carriers_a_missing_at_b)
        frac_hist[b] = frac_hist.get(b, 0) + 1
        if r.frac_carriers_a_missing_at_b == 0.0:
            n_frac_eq_0 += 1
        if r.frac_carriers_a_missing_at_b == 1.0:
            n_frac_eq_1 += 1
        if r.undefined:
            undefined_keys["|".join(sorted((r.a_vid, r.b_vid)))] = None

    summary = {
        "region_id": region_id,
        "n_rows_in_window": len(list(indexed_rows)),
        "n_sites_total": n_sites_total,
        "n_sites_measured": n_sites_measured,
        "n_sites_skipped_over_max_sites_per_region": n_sites_total - n_sites_measured,
        "n_groups_skipped_over_max_multiplicity": len(over_multiplicity),
        "n_pairs": len(records),
        "n_undefined_pairs": sum(1 for r in records if r.undefined),
        "label_counts": label_counts,
        "frac_histogram": {k: frac_hist[k] for k in sorted(frac_hist)},
        "n_frac_eq_0": n_frac_eq_0,
        "n_frac_eq_1": n_frac_eq_1,
        "undefined_pair_vids": list(undefined_keys),
    }
    return records, summary


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_region_ids(raw: "str | None") -> "list[str] | None":
    """``None`` means every region. An EMPTY-after-strip value is an ERROR.

    Matching the scanner's ruling: silently widening a narrowed run to a full
    scan is the expensive direction, so it RAISES.
    """
    if raw is None:
        return None
    ids = [x.strip() for x in raw.split(",")]
    if not ids or any(not x for x in ids):
        raise ValueError(
            f"--region-ids was given but parses to an empty selection: {raw!r}. "
            "Omit --region-ids entirely to scan every region; an empty value "
            "will not be treated as 'all'."
        )
    return ids


def _build_parser() -> argparse.ArgumentParser:
    """⚠ A DECLARED CROSS-TASK CONTRACT, not an incidental helper.

    The staged paste doc's argv is fed to THIS function at verify time, so a
    staged typo fails at NCSU rather than in the perimeter. Renaming it breaks
    that verify with ``AttributeError``.
    """
    p = argparse.ArgumentParser(
        prog="samepos_missingness_probe",
        description=(
            "Measure whether same-position .bim rows are co-called or "
            "complementary. Reads .bim/.bed only; aggregate egress."
        ),
    )
    p.add_argument("--bfile-prefix", required=True)
    p.add_argument("--regions-tsv", required=True)
    p.add_argument("--ancestry", default=DEFAULT_ANCESTRY)
    p.add_argument("--region-ids", default=None)
    p.add_argument("--max-multiplicity", type=int, default=DEFAULT_MAX_MULTIPLICITY)
    p.add_argument("--max-sites-per-region", type=int,
                   default=DEFAULT_MAX_SITES_PER_REGION)
    p.add_argument("--out", required=True)
    p.add_argument("--summary", required=True)
    return p


def main(argv: "list[str] | None" = None) -> int:
    args = _build_parser().parse_args(argv)

    region_ids = _parse_region_ids(args.region_ids)
    prefix = Path(args.bfile_prefix)
    bim_path = prefix.with_suffix(".bim")
    if not bim_path.exists():
        raise FileNotFoundError(f"missing .bim for prefix {prefix}: {bim_path}")

    windows = _read_regions_tsv(args.regions_tsv, region_ids, ancestry=args.ancestry)
    # pad_bp=0 -- the SAME window population the scanner and the producer use.
    rows_by_region = iter_bim_windows(bim_path, windows, pad_bp=0)
    reader = BedReader(prefix)

    all_records: list = []
    per_region: dict = {}
    for region_id, _chrom, _start, _end in windows:
        rows = rows_by_region.get(region_id, [])
        records, summary = measure_region(
            reader, region_id, rows,
            max_multiplicity=args.max_multiplicity,
            max_sites_per_region=args.max_sites_per_region,
        )
        all_records.extend(records)
        per_region[region_id] = summary

    out_path = Path(args.out)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\t".join(TSV_COLUMNS) + "\n")
        for r in all_records:
            fh.write("\t".join(str(v) for v in r) + "\n")

    pooled_labels = {lab: 0 for lab in LABELS}
    pooled_hist: dict = {}
    undefined_keys: "OrderedDict" = OrderedDict()
    for s in per_region.values():
        for lab, n in s["label_counts"].items():
            pooled_labels[lab] += n
        for k, n in s["frac_histogram"].items():
            pooled_hist[k] = pooled_hist.get(k, 0) + n
        for v in s["undefined_pair_vids"]:
            undefined_keys[v] = None

    pooled = {
        "n_regions": len(per_region),
        "n_sites_total": sum(s["n_sites_total"] for s in per_region.values()),
        "n_sites_measured": sum(s["n_sites_measured"] for s in per_region.values()),
        "n_sites_skipped_over_max_sites_per_region": sum(
            s["n_sites_skipped_over_max_sites_per_region"] for s in per_region.values()
        ),
        "n_groups_skipped_over_max_multiplicity": sum(
            s["n_groups_skipped_over_max_multiplicity"] for s in per_region.values()
        ),
        "n_pairs": sum(s["n_pairs"] for s in per_region.values()),
        "n_undefined_pairs": sum(s["n_undefined_pairs"] for s in per_region.values()),
        "label_counts": pooled_labels,
        "frac_histogram": {k: pooled_hist[k] for k in sorted(pooled_hist)},
        "n_frac_eq_0": sum(s["n_frac_eq_0"] for s in per_region.values()),
        "n_frac_eq_1": sum(s["n_frac_eq_1"] for s in per_region.values()),
        "undefined_pair_vids": list(undefined_keys),
    }

    summary_doc = {
        "provenance": {
            "bfile_prefix": str(prefix),
            "bim_path": str(bim_path),
            "bim_sha256": _sha256(bim_path),
            "regions_tsv_path": str(args.regions_tsv),
            "regions_tsv_sha256": _sha256(Path(args.regions_tsv)),
            "ancestry": str(args.ancestry),
            "n_samples": int(reader.n_samples),
            "max_multiplicity": int(args.max_multiplicity),
            "max_sites_per_region": int(args.max_sites_per_region),
            "region_ids": [str(w[0]) for w in windows],
            "sampling": (
                "DETERMINISTIC PREFIX in .bim file order, no RNG. A capped run "
                "is a SAMPLE, not a census: compare n_sites_measured against "
                "n_sites_total and both skip counters before quoting anything."
            ),
            "label_scope": (
                "co_called / complementary / mixed describe the MEASUREMENT "
                "only. They name no mechanism. The hl.split_multi_hts "
                "expectation is an INFERENCE FROM DOCUMENTATION that this node "
                "cannot verify; a mismatch is a finding to report, never a "
                "number to adjust."
            ),
        },
        "pooled": pooled,
        "per_region": per_region,
    }
    Path(args.summary).write_text(json.dumps(summary_doc, indent=2) + "\n",
                                  encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
