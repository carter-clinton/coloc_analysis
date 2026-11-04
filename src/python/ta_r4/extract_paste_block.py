"""The R4 amendment's public text: the text strictly between the two marker lines (W4a/W4b; checker W4).

extract(path)              -> the public text (markers excluded); raises MarkerError unless each marker line
                              occurs exactly once and START precedes END.
render_confirmatory(rules) -> the confirmatory-analysis sentences, rendered from decision_rules.yaml so the
                              amendment cannot drift from the config. Carter-locked cut-offs stay symbolic.
CLI: python -m ta_r4.extract_paste_block --in FINAL --out PUBLIC
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

START_MARKER = "--- PASTE INTO OSF FROM HERE ---"
END_MARKER = "--- PASTE ENDS HERE ---"


class MarkerError(ValueError):
    pass


def extract(path) -> str:
    text = Path(path).read_bytes().decode("utf-8")
    lines = text.splitlines(keepends=True)
    starts = [i for i, ln in enumerate(lines) if ln.rstrip("\r\n") == START_MARKER]
    ends = [i for i, ln in enumerate(lines) if ln.rstrip("\r\n") == END_MARKER]
    if len(starts) != 1 or len(ends) != 1:
        raise MarkerError(f"{path}: expected one start and one end marker line, found {len(starts)} and {len(ends)}")
    if starts[0] >= ends[0]:
        raise MarkerError(f"{path}: end marker (line {ends[0] + 1}) precedes start marker (line {starts[0] + 1})")
    return "".join(lines[starts[0] + 1: ends[0]])


def _fmt(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (list, tuple)):
        return ", ".join(_fmt(x) for x in v)
    return str(v)


def render_confirmatory(rules) -> str:
    """Confirmatory row set, clusters, subsets, statistics, category rules and precedence, from the yaml."""
    c = rules["confirmatory"]
    cat = c["categories"]
    rows = ", ".join(f"{k} = {_fmt(v)}" for k, v in c["rows"].items())
    both = "; ".join(f"{k}: {v}" for k, v in c["both_have_cs"].items())
    ci = c["ci"]
    mk = c["mcnemar_kappa"]
    lines = [
        f"- Contrasts: {_fmt(c['contrasts'])}; reference arm {c['reference_arm']}.",
        f"- Row set: pair-manifest rows with {rows}.",
        f"- Bootstrap clusters: {c['clusters']}.",
        f"- Both-have-CS subset per contrast ({both}).",
        f"- Confidence interval: {ci['statistic']} on the {ci['subset']} subset by {ci['method']}, "
        f"{rules['bootstrap_B']} resamples, seed {rules['bootstrap_seed']}, level {rules['ci_level']}.",
        f"- McNemar test and Cohen's kappa: on the {mk['subset']} subset; a call is {mk['call']} "
        f"(threshold_primary = {rules['threshold_primary']}; region statistic for coloc_susie rows = "
        f"{rules['region_stat_coloc_susie']}).",
        f"- n_both: the size of the {c['n_both']['subset']} subset.",
        f"- Categories (alpha = {rules['alpha']}): n_both_ok: {cat['n_both_ok']}. ci: {cat['ci']}. "
        f"mcnemar: {cat['mcnemar']}. kappa_ok: {cat['kappa_ok']}.",
        f"- Classifier precedence (first match wins): {_fmt(rules['precedence'])}.",
        f"- Never classifier inputs: {'; '.join(str(x) for x in c['excluded_from_classifier'])}.",
    ]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        text = extract(a.src)
    except MarkerError as e:
        print(f"extract_paste_block: {e}", file=sys.stderr)
        return 2
    out = Path(a.out)
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_bytes(text.encode("utf-8"))
    tmp.replace(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
