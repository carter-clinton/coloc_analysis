"""harvest_mtag_fdr_scalars.py — production-fire harvest of M2-POST-M3-07
per-trait Turley max_FDR scalars across EUR/AFR/TRANS strata.

Production-fire closure of Wave 2-D6 hand-off
(m2-02-task4-mtag-production-fire.md §6):
    "the result will replace the placeholder 0.0 with the actual
     per-trait Turley scalars in a subsequent commit"

Pipeline:

  1. parse_fdr_log:
     Reads <STRATUM>_mtag_fdr_run.log produced by
     bin/fire_m2_post_m3_07_mtag_fdr.sh and extracts the
     ^FDR of Trait N: <float>$ scalar lines (1-indexed N, mix of
     fixed-decimal and scientific notation).

  2. build_trait_key_to_fdr:
     Joins trait_index (1-indexed log) -> trait_key (0-indexed
     residcov.trait_order.json sidecar) -> max_FDR scalar.

  3. rewrite_maxfdr_column:
     Rewrites col 11 (max_FDR) of <STRATUM>_mtag_maxfdr_filtered.txt
     in-place by joining on col 12 (trait_key). Atomic via *.tmp +
     os.replace(). Preserves row count + all other cols byte-for-byte.
     Emits per-stratum audit TSV (trait_key, max_FDR, n_rows).

Failure modes (fail-loud):

  - Log with no 'FDR of Trait N:' lines  -> ValueError
  - Mismatch between log K and sidecar K -> ValueError
  - Row with trait_key not in mapping    -> KeyError

Stdlib only (json, os, re, pathlib); runs under smoke_dev/Python 3.11
(consistent with pytest runner). The m2-mtag/3.10 env was env-pinned
for MTAG --fdr LSF execution only.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

# 1-indexed in the log; float can be fixed-decimal or scientific notation.
FDR_LINE_RE = re.compile(r"^FDR of Trait (\d+):\s+([\d.eE+\-]+)")


def parse_fdr_log(log_path: Path) -> dict[int, float]:
    """Parse `FDR of Trait N: <float>` lines from an MTAG --fdr run log.

    Returns {1-indexed trait_number: max_FDR_scalar}.

    Raises ValueError if no lines match the regex (caller must guard
    against silent zero-row parse).
    """
    out: dict[int, float] = {}
    for line in log_path.read_text().splitlines():
        m = FDR_LINE_RE.match(line.strip())
        if m:
            out[int(m.group(1))] = float(m.group(2))
    if not out:
        raise ValueError(f"No 'FDR of Trait N: ...' lines in {log_path}")
    return out


def build_trait_key_to_fdr(stratum_dir: Path) -> dict[str, float]:
    """Join trait_index -> trait_key (from residcov.trait_order.json,
    0-indexed) onto trait_index -> max_FDR (from log, 1-indexed).

    Asserts log K == sidecar K (otherwise raises ValueError — guards
    against partial log writes / mismatched fire vs sidecar).
    """
    sidecar = json.loads(
        (stratum_dir / "residcov.trait_order.json").read_text()
    )
    trait_order = sidecar["trait_order"]  # 0-indexed
    K = sidecar["K"]
    log_path = stratum_dir / f"{stratum_dir.name}_mtag_fdr_run.log"
    fdr_by_idx = parse_fdr_log(log_path)
    if len(fdr_by_idx) != K:
        raise ValueError(
            f"Expected K={K} 'FDR of Trait' lines in {log_path}, "
            f"got {len(fdr_by_idx)}"
        )
    return {trait_order[n - 1]: fdr_by_idx[n] for n in fdr_by_idx}


def rewrite_maxfdr_column(
    filtered_path: Path,
    trait_key_to_fdr: dict[str, float],
    audit_path: Path,
) -> None:
    """Rewrite col 11 (max_FDR) of `filtered_path` by joining col 12
    (trait_key) -> `trait_key_to_fdr`. Preserve row count + all other
    cols byte-for-byte.

    Atomic: write to *.tmp then os.replace() — on any mid-stream
    exception (KeyError on unknown trait_key, IOError, etc.) the
    original file is preserved untouched.

    Emits audit TSV at `audit_path` (trait_key, max_FDR, n_rows).
    """
    tmp = filtered_path.with_suffix(filtered_path.suffix + ".tmp")
    counts: dict[str, int] = {k: 0 for k in trait_key_to_fdr}
    n_total = 0
    try:
        with filtered_path.open() as fin, tmp.open("w") as fout:
            header = fin.readline()
            fout.write(header)
            for line in fin:
                cols = line.rstrip("\n").split("\t")
                tk = cols[11]  # col 12 (0-indexed 11)
                if tk not in trait_key_to_fdr:
                    raise KeyError(
                        f"Unknown trait_key {tk!r} at data row "
                        f"{n_total + 1} (file row {n_total + 2})"
                    )
                cols[10] = repr(trait_key_to_fdr[tk])  # col 11 (0-indexed 10)
                counts[tk] += 1
                n_total += 1
                fout.write("\t".join(cols) + "\n")
    except Exception:
        # Atomic-fail: clean up the *.tmp shard so nothing partial leaks.
        if tmp.exists():
            tmp.unlink()
        raise
    os.replace(str(tmp), str(filtered_path))

    # Emit audit TSV (trait_key, max_FDR, n_rows).
    with audit_path.open("w") as fa:
        fa.write("trait_key\tmax_FDR\tn_rows\n")
        for tk, mf in trait_key_to_fdr.items():
            fa.write(f"{tk}\t{mf!r}\t{counts[tk]}\n")


def main() -> None:
    """CLI entry: harvest all 3 strata in sequence."""
    repo = Path(__file__).resolve().parents[2]
    base = repo / "data" / "processed" / "mtag"
    for stratum in ["EUR", "AFR", "TRANS"]:
        sd = base / stratum
        tk_to_fdr = build_trait_key_to_fdr(sd)
        rewrite_maxfdr_column(
            sd / f"{stratum}_mtag_maxfdr_filtered.txt",
            tk_to_fdr,
            sd / f"{stratum}_mtag_fdr_audit.tsv",
        )
        vals = list(tk_to_fdr.values())
        print(
            f"[harvest] {stratum} OK: K={len(tk_to_fdr)} traits, "
            f"min={min(vals):.3e}, max={max(vals):.3e}"
        )


if __name__ == "__main__":
    main()
