"""Coloc coverage (B2): observed coloc JSONs == expected (admissible row x production arm x p12 key, plus
A1_<ANC> matched/allvars) for one ancestry. Globs only the result dirs the expected paths live in, all of
which are in paths.result_dirs('coloc'); reproduction arms are never counted."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from ta_r4 import paths
from ta_r4.arms import production_arms
from ta_r4.commands import P12_KEYS

A1_VARSETS = ("matched", "allvars")


def expected_ids(manifest, ancestry, p12_keys=P12_KEYS, arms=None, a1_varsets=A1_VARSETS) -> set[str]:
    arms = production_arms(ancestry) if arms is None else list(arms)
    rows = manifest[(manifest.ancestry == ancestry) & (manifest.admissible == "true")].row_id
    out = set()
    for rid in rows:
        for k in p12_keys:
            out.update(paths.coloc_json(a, rid, k) for a in arms)
            out.update(paths.coloc_json(f"A1_{ancestry}", rid, k, v) for v in a1_varsets)
    return out


def check(expected, repo) -> tuple[set[str], set[str]]:
    dirs = sorted({str(Path(p).parent) for p in expected})
    allowed = set(paths.result_dirs("coloc"))
    stray = [d for d in dirs if d not in allowed]
    if stray:
        raise ValueError(f"expected paths outside paths.result_dirs('coloc'): {stray}")
    observed = {str(f.relative_to(repo)) for d in dirs for f in (Path(repo) / d).glob("*.json")}
    return set(expected) - observed, observed - set(expected)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m ta_r4.coloc_coverage", description=__doc__)
    ap.add_argument("--ancestry", required=True, choices=("EUR", "AFR"))
    ap.add_argument("--repo", required=True)
    ap.add_argument("--manifest", help="default: <repo>/config/ta_r4/pair_manifest.tsv")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    man = pd.read_csv(a.manifest or repo / "config/ta_r4/pair_manifest.tsv", sep="\t", dtype=str,
                      keep_default_na=False)
    exp = expected_ids(man, a.ancestry)
    missing, extra = check(exp, repo)
    print(f"missing={len(missing)} extra={len(extra)} expected={len(exp)}")
    for tag, s in (("MISSING", missing), ("EXTRA", extra)):
        for p in sorted(s)[:20]:
            print(f"{tag} {p}", file=sys.stderr)
        if len(s) > 20:
            print(f"{tag} ... {len(s) - 20} more", file=sys.stderr)
    return 1 if missing or extra else 0


if __name__ == "__main__":
    sys.exit(main())
