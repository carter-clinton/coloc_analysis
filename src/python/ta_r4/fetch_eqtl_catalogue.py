"""Fetch GTEx v8 eQTL/sQTL sumstats + .tbi from the eQTL Catalogue with integrity checks (ta-r4 W2c).

URLs are resolved exactly as qtl_download.smk::_resolve_eqtlcat_url (same YAML keys, same suffix rule).
Every URL is HEADed before any download; a non-200 or a Content-Length < 1 MB aborts. Each file is fetched by
fetch_verified(size=Content-Length, magic=gzip), then checked with `gzip -t` and `tabix -l` + a tabix query.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as _dt
import hashlib
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

from ta_r4.fetch_verified import fetch_verified

DEST = "data/r4/downloads/eqtl_catalogue"
MIN_BYTES = 1 << 20
NO_PUBLISHED = "no published checksum"
COLS = ["qtd", "tissue", "source", "url", "size_bytes", "sha256", "published_md5", "gzip_ok", "tabix_ok",
        "fetched_utc", "tbi_size_bytes", "tbi_sha256"]


def load_cfg(sources_yaml="config/qtl_sources.yaml", qtd_map_yaml="config/eqtl_catalogue_qtd_map.yaml"):
    with open(sources_yaml) as fh:
        sources = (yaml.safe_load(fh) or {}).get("sources", {})
    with open(qtd_map_yaml) as fh:
        qtd_map = yaml.safe_load(fh) or {}
    return sources, qtd_map


def resolve_url(tissue, source_key, sources, qtd_map, suffix=None):
    """Mirror of qtl_download.smk::_resolve_eqtlcat_url."""
    src = sources.get(source_key)
    if not src:
        raise ValueError(f"Unknown QTL source '{source_key}'. Available: {sorted(sources)}")
    base = src.get("ftp_base", "https://ftp.ebi.ac.uk/pub/databases/spot/eQTL/sumstats/")
    study_id, qtd_kind = src.get("study_id"), src.get("qtd_kind")
    if not study_id or not qtd_kind:
        raise ValueError(f"Source '{source_key}' missing study_id or qtd_kind")
    suffix = suffix if suffix is not None else src.get("upstream_suffix")
    if not suffix:
        raise ValueError(f"No upstream_suffix configured for source '{source_key}'")
    tissues = qtd_map.get("tissues", {})
    if tissue not in tissues:
        raise ValueError(f"Tissue '{tissue}' not found in {source_key} QTD map")
    qtd_id = tissues[tissue].get(qtd_kind)
    if qtd_id is None:
        raise ValueError(f"QTD kind '{qtd_kind}' missing for tissue '{tissue}' in {source_key}")
    return f"{base}{study_id}/{qtd_id}/{qtd_id}{suffix}", qtd_id


def resolve_all(source_keys, sources, qtd_map):
    out = []
    for sk in source_keys:
        for tissue in qtd_map.get("tissues", {}):
            url, qtd = resolve_url(tissue, sk, sources, qtd_map)
            out.append({"qtd": qtd, "tissue": tissue, "source": sk, "url": url})
    return out


def head(url, tries=4, wait=15):
    req = urllib.request.Request(url, method="HEAD")
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, int(r.headers.get("Content-Length") or -1)
        except urllib.error.URLError:
            if i == tries - 1:
                raise
            time.sleep(wait * (i + 1))


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for buf in iter(lambda: fh.read(1 << 22), b""):
            h.update(buf)
    return h.hexdigest()


def _get(url, dest_dir, size):
    """fetch_verified into dest_dir; a final file already of the HEAD size (renamed only after verification) is reused."""
    final = Path(dest_dir) / os.path.basename(url)
    if final.is_file() and final.stat().st_size == size:
        return {"path": str(final), "size": size, "sha256": _sha256(final)}
    return fetch_verified(url, dest_dir, size=size, magic=("gzip",))


def fetch_one(item, dest_root, tabix):
    qdir = Path(dest_root) / item["qtd"]
    res = _get(item["url"], qdir, item["size"])
    # fetch_verified wants its own empty dir: stage the index, then move it beside the data file.
    tbi_url = item["url"] + ".tbi"
    tbi_final = qdir / os.path.basename(tbi_url)
    if tbi_final.is_file() and tbi_final.stat().st_size == item["tbi_size"]:
        tres = {"path": str(tbi_final), "size": item["tbi_size"], "sha256": _sha256(tbi_final)}
    else:
        stage = Path(dest_root) / "_tbi_stage" / item["qtd"]
        tres = fetch_verified(tbi_url, stage, size=item["tbi_size"], magic=("gzip",))
        os.replace(tres["path"], tbi_final)
        stage.rmdir()
        tres["path"] = str(tbi_final)
    gzip_ok = subprocess.run(["gzip", "-t", res["path"]], capture_output=True).returncode == 0
    lst = subprocess.run([tabix, "-l", res["path"]], capture_output=True, text=True)
    seqs = lst.stdout.split()
    tabix_ok = False
    if lst.returncode == 0 and seqs:
        q = subprocess.run(f"{tabix} {res['path']} {seqs[0]} | head -1", shell=True, capture_output=True, text=True)
        first = q.stdout.split("\t")
        tabix_ok = q.returncode == 0 and "warning" not in q.stderr.lower() and len(first) > 2
    return {**item, "size_bytes": res["size"], "sha256": res["sha256"], "published_md5": NO_PUBLISHED,
            "gzip_ok": str(gzip_ok).lower(), "tabix_ok": str(tabix_ok).lower(),
            "fetched_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tbi_size_bytes": tres["size"], "tbi_sha256": tres["sha256"], "first_seq": seqs[0] if seqs else ""}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sources", nargs="+", default=["gtex_eqtl", "gtex_sqtl"])
    ap.add_argument("--dest", default=DEST)
    ap.add_argument("--jobs", type=int, default=5)
    ap.add_argument("--tabix", required=True)
    ap.add_argument("--manifest", required=True)
    a = ap.parse_args(argv)

    sources, qtd_map = load_cfg()
    items = resolve_all(a.sources, sources, qtd_map)
    for it in items:
        print(f"RESOLVED\t{it['source']}\t{it['tissue']}\t{it['url']}")
    print(f"RESOLVED_COUNT {len(items)} = {len(qtd_map.get('tissues', {}))} tissues x {len(a.sources)} sources", flush=True)

    bad = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        heads = list(ex.map(lambda it: (head(it["url"]), head(it["url"] + ".tbi")), items))
    for it, ((st, cl), (tst, tcl)) in zip(items, heads):
        it["size"], it["tbi_size"] = cl, tcl
        if st != 200 or cl < MIN_BYTES or tst != 200 or tcl <= 0:
            bad.append((it["url"], st, cl, tst, tcl))
    if bad:
        for b in bad:
            print("HEAD_FAIL", *b, file=sys.stderr)
        return 2
    print(f"HEAD_OK {len(items)} total_bytes {sum(i['size'] + i['tbi_size'] for i in items)}", flush=True)

    man = Path(a.manifest)
    done = set()
    if man.is_file() and man.stat().st_size:
        done = {ln.split("\t")[0] for ln in man.read_text().splitlines()[1:]}
    todo = [it for it in items if it["qtd"] not in done]
    fails = 0
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(fetch_one, it, a.dest, a.tabix): it for it in todo}
        for f in cf.as_completed(futs):
            it = futs[f]
            try:
                row = f.result()
            except Exception as e:  # noqa: BLE001 - report and continue; reconciliation catches gaps
                fails += 1
                print(f"FETCH_FAIL\t{it['qtd']}\t{it['url']}\t{e!r}", file=sys.stderr, flush=True)
                continue
            new = not man.exists() or man.stat().st_size == 0
            with open(man, "a") as fh:
                if new:
                    fh.write("\t".join(COLS) + "\n")
                fh.write("\t".join(str(row[c]) for c in COLS) + "\n")
            print(f"DONE\t{row['qtd']}\t{row['size_bytes']}\tgzip_ok={row['gzip_ok']}\ttabix_ok={row['tabix_ok']}"
                  f"\tfirst_seq={row['first_seq']}", flush=True)
    print(f"FINISHED todo={len(todo)} failed={fails}", flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
