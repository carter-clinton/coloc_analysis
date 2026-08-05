"""Lockstep occlusion drop for the harmonized sumstats (m3-07c, T4).

LOCKSTEP is the load-bearing word of the pre-registered policy (osf.io/az52u,
amendment-update POSTED 2026-07-10T13:32:22Z, recorded ``ac4c990``). A variant
excluded from the LD panel because an overlapping deletion's REF span makes its LD
structurally undefined (``occlusion_span_filter.py``, 07b) MUST also leave the
harmonized sumstats. The SAME variants, in BOTH artifacts — otherwise the panel and
the sumstats disagree about which variants exist and every downstream fine-map
inherits the mismatch.

Excluding panel-side ONLY is not a smaller version of the policy; it is a different
and WRONG one. rs182965575 (GRCh37 chr1:5982778) is present in 7 of 9 AFR sumstats:
drop it from the panel alone and 7 traits carry a variant the LD matrix has never
heard of — an ORPHAN. That is the failure this module exists to prevent, and it is
why the drop is keyed on the SAME manifest the panel exclusion is keyed on rather
than re-derived here (a second derivation is a second chance to disagree).

CONTRACT (module.function, mirroring ``plink_ld_to_npz.plink_ld_to_npz``)
------------------------------------------------------------------------
    drop_occluded_from_sumstats(sumstats_path, manifest_path, out_path) -> dict

FILE-IN / FILE-OUT: all three arguments are PATHS and the function WRITES
``out_path``. Returns the durable counts ``{"n_in", "n_dropped", "n_out"}`` so the
lockstep is auditable against the panel's ``n_dropped_occluded`` — the invariant
``n_in - n_dropped == n_out`` is what makes "the panel and the sumstats dropped the
same variants" a checkable claim rather than an assertion.

DROP-ONLY, NEVER A RE-KEY
--------------------------
The panel<->sumstats join is (CHR,POS)-only on GRCh37, drop-only, first-record-wins
on a multi-allelic collision (``snp_id_bridge.R:107-121``). REF/ALT are NOT in the
key. ``SNP_ID`` is passed through untouched and never re-derived, surviving rows are
byte-identical, and their order is preserved: a "filter" that silently reformats or
re-labels survivors is a re-key by another name, and a re-key would remap variants
that nothing downstream asked to remap.

THE KEY IS CHR-AWARE. A POS-only key would silently delete unrelated variants that
merely share a coordinate on another chromosome — genome-wide, invisibly.

IDEMPOTENT ON ITS OWN OUTPUT. ``out_path`` is written in the same format it reads,
so re-running the filter ON ITS OUTPUT drops nothing and reproduces the same bytes.
That is stronger than a no-op flag, and it is what lets the filter survive being
replayed after a preemption without corrupting a partially-filtered file.

``n_dropped == 0`` IS A VALID NO-OP, not an error: an occluded variant with no row
in this trait's sumstats drops nothing. Present-rate k/n < 1 is the NORMAL case
(``occlusion_present_rate_scan.py``, T3).

THE DEFERRED m3-04 SEAM — READ BEFORE WIRING
---------------------------------------------
This is the REUSABLE filter; the exact consume-step wiring is DEFERRED. The m3-04
consume rule is SUPERSEDED-PENDING-REPLAN (``finemap.smk:89-93``; m3-04-W4 is STALE
and must be re-planned to consume m3-02e's AFR-native ``.npz``), so this filter is
wired at the sumstats-load seam when the m3-04 consume replan lands — keyed on the
same manifest (CHR,POS) as the panel exclusion so panel and sumstats stay in
lockstep (no orphaned variant). ``finemap.smk`` is deliberately NOT modified here.

Every drop is LOGGED to STDERR — provenance, not a debug nicety. The manifest is the
durable record; the log is the in-run witness.

Runs in smoke_dev py3.11 (pandas for the small manifest; the sumstats is streamed
BINARY line-wise, so a genome-wide file is never materialized and surviving bytes
are passed through untouched). No Hail.
"""
from __future__ import annotations

import gzip
import sys
from pathlib import Path

import pandas as pd

from occlusion_coord_key import canonical_coord_key

__all__ = ["drop_occluded_from_sumstats"]

#: Fallback column indices, mirroring the hinge-check awk prototype
#: (``m3_region1_occlusion_hinge_check.md:124-141``) that also drives the T3 scan:
#: ``cc=(h["CHR"]?h["CHR"]:1); pc=(h["POS"]?h["POS"]:(h["BP"]?h["BP"]:2))``.
_FALLBACK_CHR_IDX = 0
_FALLBACK_POS_IDX = 1

#: Accepted position-column names, in precedence order (POS wins over BP).
_POS_NAMES = ("POS", "BP")

#: The manifest columns this consumer drops on. Only these two are load-bearing;
#: region_id/variant_id ride along as provenance for the log line.
_MANIFEST_CHR = "chr"
_MANIFEST_POS = "pos_grch37"


def _canonical_key(chrom, pos) -> tuple:
    """Canonical GRCh37 (CHR,POS) key — see ``occlusion_coord_key``.

    A ONE-LINE DELEGATION, kept under its private name so every existing reference
    still resolves. Both sides of the join go through it, which is what lets the
    manifest's ``chr`` (the producer emits ``'1'``; pandas may hand back
    ``numpy.int64`` ``1``) match the sumstats' ``CHR`` text ``"1"`` instead of
    near-missing and silently dropping NOTHING.

    The rule used to be duplicated verbatim here, in ``occlusion_present_rate_scan``
    and in ``occlusion_manifest``. It is now IMPORTED from one place — which is how
    D-04b-01 (a bare ``int(pos)``, fatal on a float-formatted POS column) stops being
    a defect that has to be found and fixed three times.
    """
    return canonical_coord_key(chrom, pos)


def _open_binary(path: Path):
    """Open a sumstats file BINARY, transparently handling bgzip/gzip.

    Binary is deliberate: surviving rows must come through byte-identical, so the
    bytes are never decoded/re-encoded or newline-translated on the way out.
    """
    if path.suffix.lower() in {".gz", ".bgz"}:
        return gzip.open(path, "rb")
    return path.open("rb")


def _locate_chr_pos(header: list) -> tuple:
    """Locate (chr_idx, pos_idx) in the sumstats header BY NAME, never positionally."""
    idx = {name.strip().upper(): i for i, name in enumerate(header)}
    chr_idx = idx.get("CHR", _FALLBACK_CHR_IDX)
    pos_idx = next((idx[n] for n in _POS_NAMES if n in idx), _FALLBACK_POS_IDX)
    return chr_idx, pos_idx


def _load_manifest_keys(manifest_path: Path) -> dict:
    """Read the occlusion manifest -> ``{(chr, pos_grch37): "region_id/variant_id"}``.

    FAIL-CLOSED on a Stage-A manifest: ``pos_grch37`` is added by Stage B
    (``occlusion_manifest.add_grch37_positions``). Silently dropping nothing because
    the key column is absent would report a clean ``n_dropped == 0`` while leaving
    every occluded variant orphaned in the sumstats — the exact failure this module
    exists to prevent, wearing a green result.

    A row that did NOT lift (``pos_grch37`` NA) has no GRCh37 coordinate and so
    cannot be located in GRCh37 sumstats at all. It is skipped with an explicit
    STDERR warning rather than raising (a variant in a liftover/assembly gap is rare
    but plausible, and hard-aborting a whole trait over one is wrong) and rather than
    being guessed at (a plausible-but-wrong coordinate would drop the WRONG row).
    The warning is the honest record that the lockstep could not be enforced there.
    """
    df = pd.read_csv(manifest_path, sep="\t",
                     dtype={"region_id": str, "variant_id": str})
    missing = [c for c in (_MANIFEST_CHR, _MANIFEST_POS) if c not in df.columns]
    if missing:
        raise ValueError(
            f"occlusion manifest {manifest_path} is missing {missing}; the drop is "
            f"keyed on ({_MANIFEST_CHR}, {_MANIFEST_POS}) — GRCh37, POST-liftover. "
            "A Stage-A manifest carries pos_grch38 only: run "
            "occlusion_manifest.add_grch37_positions / enrich_occlusion_manifest "
            "first. Refusing to report a clean no-op that would silently orphan "
            "every occluded variant in the sumstats."
        )

    keys: dict = {}
    for rec in df.to_dict("records"):
        chrom, pos = rec[_MANIFEST_CHR], rec[_MANIFEST_POS]
        provenance = f"{rec.get('region_id', '?')}/{rec.get('variant_id', '?')}"
        if pos is None or pd.isna(pos):
            print(
                f"[drop_occluded_from_sumstats] WARNING: manifest row {provenance} "
                f"has no {_MANIFEST_POS} (did not lift) — it cannot be located in "
                "GRCh37 sumstats and is NOT enforced in lockstep here.",
                file=sys.stderr,
            )
            continue
        keys[_canonical_key(chrom, pos)] = provenance
    return keys


def drop_occluded_from_sumstats(sumstats_path: "str | Path",
                                manifest_path: "str | Path",
                                out_path: "str | Path") -> dict:
    """Drop the manifest's occluded variants from a harmonized sumstats file.

    Reads ``sumstats_path`` (harmonized GRCh37 TSV, plain or bgzipped) and
    ``manifest_path`` (the 07b occlusion manifest, Stage-B/lifted), writes the
    filtered sumstats to ``out_path``, and returns ``{"n_in", "n_dropped",
    "n_out"}`` with ``n_in - n_dropped == n_out`` and ``n_out`` == the number of body
    rows actually written.

    Removes EXACTLY the rows whose (CHR,POS) matches a manifest entry's GRCh37
    ``(chr, pos_grch37)``. Drop-only: no re-key, no allele re-orientation, no
    reformatting of survivors. Each drop is logged to STDERR. Idempotent when
    re-run on its own output. See the module docstring for the DEFERRED m3-04
    consume-wiring seam (finemap.smk:89-93 is SUPERSEDED-PENDING-REPLAN).
    """
    sumstats_path, manifest_path = Path(sumstats_path), Path(manifest_path)
    out_path = Path(out_path)

    occluded = _load_manifest_keys(manifest_path)

    n_in = n_dropped = n_out = 0
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with _open_binary(sumstats_path) as fin, out_path.open("wb") as fout:
        header_raw = fin.readline()
        if not header_raw.strip():
            return {"n_in": 0, "n_dropped": 0, "n_out": 0}
        fout.write(header_raw)                       # header verbatim
        chr_idx, pos_idx = _locate_chr_pos(
            header_raw.decode("utf-8").rstrip("\r\n").split("\t")
        )

        for raw in fin:
            if not raw.strip():
                continue                             # blank line: not a record
            n_in += 1
            fields = raw.decode("utf-8").rstrip("\r\n").split("\t")

            key = None
            if max(chr_idx, pos_idx) < len(fields):
                try:
                    key = _canonical_key(fields[chr_idx], fields[pos_idx])
                except (TypeError, ValueError):
                    key = None                       # unparseable coord: cannot match

            if key is not None and key in occluded:
                n_dropped += 1
                print(
                    f"[drop_occluded_from_sumstats] DROP {key[0]}:{key[1]} "
                    f"(occluded; manifest {occluded[key]}) from {sumstats_path.name}",
                    file=sys.stderr,
                )
                continue

            fout.write(raw)                          # survivor: bytes verbatim
            n_out += 1

    return {"n_in": n_in, "n_dropped": n_dropped, "n_out": n_out}
