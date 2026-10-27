"""Verified download: stream to <name>.part, check size/md5/sha256/magic, rename only if all pass."""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
import tarfile
import urllib.parse
import urllib.request
from pathlib import Path

DOWNLOADS_ROOT = "data/r4/downloads"
CHUNK = 1 << 20
MAGIC = {"gzip": b"\x1f\x8b", "bzip2": b"BZh", "zip": b"PK\x03\x04"}
MANIFEST_COLS = ["source", "url", "file", "size_bytes", "md5", "sha256", "fetched_utc"]


class VerificationError(RuntimeError):
    pass


def _check_dest(dest_dir, downloads_root, name):
    root = Path(downloads_root).resolve()
    dest = Path(dest_dir).resolve()
    if root not in dest.parents:
        raise ValueError(f"dest_dir {dest} is not under {root}")
    if dest.exists():
        stray = [p.name for p in dest.iterdir() if p.name != name + ".part"]
        if stray:
            raise ValueError(f"dest_dir {dest} is not empty: {sorted(stray)[:5]}")
    return dest


def fetch_verified(url, dest_dir, md5=None, sha256=None, size=None, magic=("gzip",), *,
                   name=None, downloads_root=DOWNLOADS_ROOT, ssl_context=None):
    if not url.startswith("https://"):
        raise ValueError(f"url must start with https://: {url}")
    name = name or os.path.basename(urllib.parse.urlparse(url).path)
    if not name or name in (".", ".."):
        raise ValueError(f"cannot derive a file name from {url}")
    dest = _check_dest(dest_dir, downloads_root, name)
    unknown = set(magic) - set(MAGIC) - {"tar"}
    if unknown:
        raise ValueError(f"unknown magic kinds {sorted(unknown)}")

    dest.mkdir(parents=True, exist_ok=True)
    part = dest / (name + ".part")
    h_md5, h_sha, n, head = hashlib.md5(), hashlib.sha256(), 0, b""
    try:
        with urllib.request.urlopen(url, context=ssl_context, timeout=120) as resp, open(part, "wb") as out:
            while True:
                buf = resp.read(CHUNK)
                if not buf:
                    break
                if len(head) < 4:
                    head = (head + buf)[:4]
                h_md5.update(buf)
                h_sha.update(buf)
                out.write(buf)
                n += len(buf)
        got = {"md5": h_md5.hexdigest(), "sha256": h_sha.hexdigest(), "size": n}
        if size is not None and n != int(size):
            raise VerificationError(f"size mismatch: got {n}, expected {size}")
        if md5 is not None and got["md5"] != md5.lower():
            raise VerificationError(f"md5 mismatch: got {got['md5']}, expected {md5}")
        if sha256 is not None and got["sha256"] != sha256.lower():
            raise VerificationError(f"sha256 mismatch: got {got['sha256']}, expected {sha256}")
        for kind in magic:
            if kind == "tar":
                if not tarfile.is_tarfile(part):
                    raise VerificationError("tar check failed: tarfile.is_tarfile is False")
            elif not head.startswith(MAGIC[kind]):
                raise VerificationError(f"magic check failed: expected {kind}, first bytes {head!r}")
    except BaseException:
        part.unlink(missing_ok=True)
        raise
    final = dest / name
    os.replace(part, final)
    return {"path": str(final), **got, "magic": list(magic)}


def append_manifest(manifest, source, url, result):
    manifest = Path(manifest)
    new = not manifest.exists() or manifest.stat().st_size == 0
    row = [source, url, Path(result["path"]).name, str(result["size"]), result["md5"], result["sha256"],
           _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")]
    with open(manifest, "a") as fh:
        if new:
            fh.write("\t".join(MANIFEST_COLS) + "\n")
        fh.write("\t".join(row) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True)
    ap.add_argument("--dest-dir", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--md5")
    ap.add_argument("--sha256")
    ap.add_argument("--size", type=int)
    ap.add_argument("--magic", default="gzip", help="comma list of gzip,bzip2,zip,tar")
    ap.add_argument("--name")
    ap.add_argument("--manifest")
    a = ap.parse_args(argv)
    res = fetch_verified(a.url, a.dest_dir, md5=a.md5, sha256=a.sha256, size=a.size,
                         magic=tuple(a.magic.split(",")), name=a.name)
    if a.manifest:
        append_manifest(a.manifest, a.source, a.url, res)
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
