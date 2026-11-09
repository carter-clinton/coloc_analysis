"""Check R4 input bytes against the committed sha256 manifests before a job reads them.

  python -m ta_r4.verify_inputs --manifest M [--manifest M2 ...] --file F [--file F2 ...]   (cwd = repo root)

Every file must be listed (column `path` or `rel_path`) in one of the manifests and hash to the recorded sha256.
Exit 1 on any failure; every failing file is named.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import sys
from pathlib import Path

from ta_r4 import paths

SUMSTATS = f"{paths.MAN}/sumstats_r4_sha256.tsv"
CATALOGS = f"{paths.MAN}/catalogs_sha256.tsv"
QTL_HARMONIZED = f"{paths.MAN}/qtl_harmonized_sha256.tsv"
CHUNK = 1 << 20
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


class InputIntegrityError(RuntimeError):
    pass


def _key(p) -> str:
    return os.path.normpath(str(p))


def recorded(manifests, repo=".") -> dict:
    out = {}
    for m in manifests:
        try:
            with open(Path(repo) / m, newline="") as fh:
                rd = csv.DictReader(fh, delimiter="\t")
                cols = rd.fieldnames or []
                col = "path" if "path" in cols else "rel_path" if "rel_path" in cols else None
                if col is None or "sha256" not in cols:
                    raise InputIntegrityError(f"{m}: needs a path or rel_path column and a sha256 column")
                for r in rd:
                    k, v = _key(r[col]), r["sha256"]
                    if not SHA_RE.match(v or ""):
                        raise InputIntegrityError(f"{m}: bad sha256 {v!r} for {k}")
                    if out.get(k, v) != v:
                        raise InputIntegrityError(f"{m}: conflicting sha256 records for {k}")
                    out[k] = v
        except OSError as e:
            raise InputIntegrityError(f"manifest {m} unreadable: {e.strerror}") from None
    return out


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def verify(files, manifests, repo=".") -> None:
    files = list(dict.fromkeys(_key(f) for f in files))
    if not files or not manifests:
        raise InputIntegrityError("no files or no manifests to verify against")
    want = recorded(manifests, repo)
    bad = []
    for f in files:
        if f not in want:
            bad.append(f"{f}: not in manifest")
            continue
        try:
            got = sha256_file(Path(repo) / f)
        except OSError as e:
            bad.append(f"{f}: unreadable ({e.strerror})")
            continue
        if got != want[f]:
            bad.append(f"{f}: expected sha256 {want[f]}, observed {got}")
    if bad:
        raise InputIntegrityError(f"{len(bad)} of {len(files)} inputs failed verification: " + "; ".join(bad))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m ta_r4.verify_inputs", description=__doc__)
    ap.add_argument("--manifest", action="append", required=True)
    ap.add_argument("--file", action="append", required=True)
    ap.add_argument("--repo", default=".")
    a = ap.parse_args(argv)
    try:
        verify(a.file, a.manifest, a.repo)
    except InputIntegrityError as e:
        print(f"InputIntegrityError: {e}", file=sys.stderr)
        return 1
    print(f"verify_inputs OK: {len(set(map(_key, a.file)))} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
