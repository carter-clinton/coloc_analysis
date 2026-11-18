"""r4 variant catalog: one row per normalized CHR:POS:REF:ALT (DEC-2026-11-17-ta-r4-catalog-unique-allele-key).

Line-level: kept lines are the input lines, byte-identical, in input order; every dropped line is returned with the
SNP_ID of the row kept for its key and its class (exact = same CHR/POS/REF/ALT bytes as the kept row, else case_ws).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
from pathlib import Path

COLUMNS = ("CHR", "POS", "REF", "ALT", "SNP_ID")
DROPPED_HEADER = "CHR\tPOS\tREF\tALT\tSNP_ID\tkept_SNP_ID\tclass\n"
_RSID = re.compile(r"rs([0-9]+)")
_CHRPOS = re.compile(r"[0-9XYMT]+:[0-9]+")


def _fields(line, lineno):
    rows = list(csv.reader([line.rstrip("\r\n")], delimiter="\t", quoting=csv.QUOTE_NONE))
    return rows[0] if rows else []


def _norm_chr(c):
    c = c.strip()
    for pre in ("chr", "CHR"):
        if c.startswith(pre):
            return c[len(pre):]
    return c


def _rank(row, lineno):
    """Sort key of the choice rule: lower wins."""
    snp = row["SNP_ID"]
    m = _RSID.fullmatch(snp)
    if m:
        form, rsnum = 0, int(m.group(1))
    elif _CHRPOS.fullmatch(snp):
        form, rsnum = 1, 0
    elif snp:
        form, rsnum = 2, 0
    else:
        form, rsnum = 3, 0
    normalized = row["raw4"] == row["norm4"]
    return (form, rsnum, 0 if normalized else 1, snp, lineno)


def unique_allele_key(lines):
    """Return (kept_lines, dropped_rows, stats); dropped_rows are (line, kept_SNP_ID, class)."""
    lines = list(lines)
    if not lines:
        raise ValueError("line 1: empty catalog (no header)")
    header = _fields(lines[0], 1)
    missing = [c for c in COLUMNS if c not in header]
    if missing:
        raise ValueError(f"line 1: header lacks {missing}")
    col = {c: header.index(c) for c in COLUMNS}
    width = max(col.values()) + 1

    groups = {}
    rows = []
    for i, line in enumerate(lines[1:], start=2):
        f = _fields(line, i)
        if len(f) < width:
            raise ValueError(f"line {i}: {len(f)} fields, need {width} ({line!r})")
        raw4 = tuple(f[col[c]] for c in ("CHR", "POS", "REF", "ALT"))
        pos_s = raw4[1].strip()
        if not re.fullmatch(r"[0-9]+", pos_s):
            raise ValueError(f"line {i}: non-integer POS {raw4[1]!r}")
        key = (_norm_chr(raw4[0]), int(pos_s), raw4[2].strip().upper(), raw4[3].strip().upper())
        norm4 = (key[0], str(key[1]), key[2], key[3])
        row = {"line": line, "lineno": i, "raw4": raw4, "norm4": norm4, "SNP_ID": f[col["SNP_ID"]], "key": key}
        rows.append(row)
        groups.setdefault(key, []).append(row)

    keep = set()
    winner = {}
    n_groups_2 = n_groups_3plus = 0
    for key, g in groups.items():
        best = min(g, key=lambda r: _rank(r, r["lineno"]))
        keep.add(best["lineno"])
        winner[key] = best
        if len(g) == 2:
            n_groups_2 += 1
        elif len(g) > 2:
            n_groups_3plus += 1

    kept = [lines[0]]
    dropped = []
    n_exact = n_case = 0
    for r in rows:
        if r["lineno"] in keep:
            kept.append(r["line"])
            continue
        w = winner[r["key"]]
        cls = "exact" if r["raw4"] == w["raw4"] else "case_ws"
        if cls == "exact":
            n_exact += 1
        else:
            n_case += 1
        dropped.append((r["line"], w["SNP_ID"], cls))

    kept_chrpos = {(r["key"][0], r["key"][1]) for r in rows if r["lineno"] in keep}
    stats = {
        "n_raw": len(rows),
        "n_kept": len(kept) - 1,
        "n_dropped_exact": n_exact,
        "n_dropped_case_ws": n_case,
        "n_groups_2": n_groups_2,
        "n_groups_3plus": n_groups_3plus,
        "n_chrpos_extra_kept": len(kept) - 1 - len(kept_chrpos),
    }
    return kept, dropped, stats


def _write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    with open(part, "w", newline="") as fh:
        fh.write(text)
    os.replace(part, path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dropped", required=True)
    a = ap.parse_args(argv)
    with open(a.inp, newline="") as fh:
        lines = fh.readlines()
    kept, dropped, stats = unique_allele_key(lines)
    body = "".join(line.rstrip("\r\n") + f"\t{snp}\t{cls}\n" for line, snp, cls in dropped)
    _write(a.dropped, DROPPED_HEADER + body)
    _write(a.out, "".join(kept))
    print(json.dumps(stats, sort_keys=True))


if __name__ == "__main__":
    main()
