#!/usr/bin/env python3
"""Deterministic SHA-256 manifest for a directory tree.

M1 Wave 1 closeout artifact: freezes raw fetch provenance under
data/raw/sumstats_v2/ for OSF-paste verification per D-13.

Usage
-----
    python freeze_sha256_manifest.py \\
        --root data/raw/sumstats_v2 \\
        --out  data/raw/sumstats_v2/sha256_manifest.tsv \\
        --no-mtime

Determinism contract
--------------------
With ``--no-mtime``, two invocations over the same tree produce
byte-identical TSV output. This is the OSF-paste reproducibility
requirement: the manifest committed to ``.planning/amendments/`` must
match a fresh re-run modulo any file additions / deletions.

Skip globs
----------
Defaults skip ``*.partial`` (in-flight curl downloads), ``*.deferred``
(D-06 / D-01 / D-03 placeholder markers from the m1_download driver),
and ``.download_complete*`` (Snakemake source-tag completion flags).
Override via ``--skip-glob``.

Output schema
-------------
Header row + one row per file, sorted lexicographically by relative
path (POSIX style, forward-slash separator regardless of platform):

    relative_path<TAB>sha256<TAB>bytes[<TAB>mtime_unix]

The ``mtime_unix`` column is omitted when ``--no-mtime`` is set.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def sha256_of_file(path: Path) -> str:
    """Return hex SHA-256 of file at *path*. Streams in 1 MiB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _matches_any_glob(p: Path, patterns: list[str]) -> bool:
    name = p.name
    for pat in patterns:
        # Path.match supports glob-style — anchor on basename for robustness.
        if Path(name).match(pat):
            return True
    return False


def freeze(root: Path, out: Path, skip_globs: list[str], with_mtime: bool) -> int:
    """Walk *root*, write deterministic SHA-256 manifest to *out*. Returns row count."""
    files: list[tuple[str, str, int, float | None]] = []
    # rglob returns directories too; we filter to files. Sort applied at end
    # to enforce determinism independent of filesystem walk order.
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if _matches_any_glob(p, skip_globs):
            continue
        rel = p.relative_to(root).as_posix()
        files.append(
            (
                rel,
                sha256_of_file(p),
                p.stat().st_size,
                None if not with_mtime else p.stat().st_mtime,
            )
        )

    files.sort(key=lambda r: r[0])  # lexicographic on POSIX relative_path

    cols = ["relative_path", "sha256", "bytes"]
    if with_mtime:
        cols.append("mtime_unix")

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for rel, digest, size, mtime in files:
            row = [rel, digest, str(size)]
            if with_mtime:
                row.append(f"{mtime:.6f}" if mtime is not None else "")
            fh.write("\t".join(row) + "\n")

    return len(files)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, required=True, help="Directory tree to hash")
    ap.add_argument("--out", type=Path, required=True, help="Output TSV path")
    ap.add_argument("--no-mtime", action="store_true",
                    help="Omit mtime column (required for OSF-paste byte-identical reruns)")
    ap.add_argument(
        "--skip-glob",
        default="*.partial,*.deferred,.download_complete*",
        help="Comma-separated glob patterns matched on basename; defaults skip "
             "in-flight, deferred-placeholder, and Snakemake completion-flag artifacts.",
    )
    args = ap.parse_args(argv)

    if not args.root.is_dir():
        print(f"[freeze_sha256_manifest] ERROR: --root {args.root} not a directory",
              file=sys.stderr)
        return 1

    skips = [s.strip() for s in args.skip_glob.split(",") if s.strip()]
    n_rows = freeze(
        root=args.root,
        out=args.out,
        skip_globs=skips,
        with_mtime=not args.no_mtime,
    )
    print(f"[freeze_sha256_manifest] wrote {n_rows} rows to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
