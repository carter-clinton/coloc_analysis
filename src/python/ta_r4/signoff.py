"""Carter sign-off parser / recorder / verifier (PLAN-INDEX §B.15, §D; threat T-r4-W0b1-01).

A reply is valid only if its first non-empty line is exactly ``carter-approved YYYY-MM-DD``
and every following non-empty line is ``key: value`` for exactly the checkpoint's required
keys. The auto-mode response ``approved`` therefore always raises SignoffError ("WAIT:").
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PHASE_DIR = REPO_ROOT / ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission"
SIGNOFF_DIR = PHASE_DIR / "signoffs"

BRANCHES = ("NON_INFORMATIVE", "NO_SYSTEMATIC_DIFFERENCE", "HETEROGENEOUS",
            "INFLATION_SUPPORTED", "DEFLATION")
TEXT, FLOAT, INT, SHA256, DATE, OSF_URL = "text", "float", "int", "sha256", "date", "osf_url"

SCHEMAS: dict[str, dict] = {
    "W2c-T4": {"keys": {"ukb_native": ("native", "hm3"),
                        "qtl_scope": ("full", "tissues_frozen", "eqtl_only",
                                      "tissues_frozen+eqtl_only")},
               "dynamic": True},
    "W3b-T3": {"keys": {"instructions": TEXT}},
    "W4a-T3": {"keys": {"p12_primary": FLOAT, "kappa_cut": FLOAT, "n_both_min": INT,
                        "partial_rule.ci_pos_mcnemar_ns": BRANCHES,
                        "partial_rule.ci_pos_mcnemar_opposite": BRANCHES,
                        "partial_rule.ci_neg_mcnemar_ns": BRANCHES,
                        "partial_rule.ci_neg_mcnemar_opposite": BRANCHES,
                        "confirmatory_sha256": SHA256,
                        "draft": ("approved",)}},
    "W4b-T3": {"keys": {"posted": ("yes",)}},
    "W7-T3": {"keys": {"instructions": TEXT}},
    "W8b-T3": {"keys": {"instructions": TEXT}},
    "W9-T1": {"keys": {"venue": TEXT}},
    "W9-T4": {"keys": {"journal": TEXT, "submitted_date": DATE, "manuscript_id": TEXT,
                       "osf_url": OSF_URL}},
}

TOKEN_RE = re.compile(r"^carter-approved (\d{4}-\d{2}-\d{2})$")
LINE_RE = re.compile(r"^([A-Za-z0-9_.+-]+):(.*)$")
DYNAMIC_RE = re.compile(r"^trait\.[A-Za-z0-9_]+\.(EUR|AFR)\.[A-Za-z0-9_]+$")


class SignoffError(ValueError):
    """Message always starts with "WAIT:" — re-present the checkpoint, record nothing."""

    def __init__(self, msg):
        super().__init__(f"WAIT: {msg}")


def canonical_sha256(obj) -> str:
    """sha256 of a YAML/JSON-like object, independent of key order and formatting."""
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _date(value, what):
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        raise SignoffError(f"{what} {value!r} is not a valid YYYY-MM-DD date") from None


def _check_value(key, value, rule):
    if isinstance(rule, tuple):
        ok = value in rule
    elif rule == FLOAT:
        ok = re.fullmatch(r"[0-9.eE+-]+", value) is not None and _is_float(value)
    elif rule == INT:
        ok = re.fullmatch(r"[0-9]+", value) is not None
    elif rule == SHA256:
        ok = re.fullmatch(r"[0-9a-f]{64}", value) is not None
    elif rule == DATE:
        ok = re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is not None and _is_date(value)
    elif rule == OSF_URL:
        ok = re.fullmatch(r"https://osf\.io/\S+", value) is not None
    else:
        ok = True
    if not ok:
        allowed = " | ".join(rule) if isinstance(rule, tuple) else rule
        raise SignoffError(f"{key}: {value!r} is not allowed (expected {allowed})")


def _is_float(v):
    try:
        float(v)
        return True
    except ValueError:
        return False


def _is_date(v):
    try:
        dt.date.fromisoformat(v)
        return True
    except ValueError:
        return False


def parse_signoff(raw, checkpoint_id, *, min_date, today, extra_required=()):
    """Return {"date": "YYYY-MM-DD", "fields": {key: value}} or raise SignoffError."""
    if checkpoint_id not in SCHEMAS:
        raise SignoffError(f"unknown checkpoint id {checkpoint_id!r}")
    schema = SCHEMAS[checkpoint_id]
    extra = list(extra_required)
    if extra and not schema.get("dynamic"):
        raise SignoffError(f"{checkpoint_id} takes no extra required keys")
    for k in extra:
        if not DYNAMIC_RE.match(k):
            raise SignoffError(f"extra key {k!r} is not trait.<trait>.<EUR|AFR>.<field>")
    required = dict(schema["keys"], **{k: TEXT for k in extra})

    lines = [ln.rstrip() for ln in str(raw).splitlines() if ln.strip()]
    if not lines:
        raise SignoffError("empty reply")
    m = TOKEN_RE.match(lines[0])
    if not m:
        raise SignoffError(
            f"first line must be exactly 'carter-approved YYYY-MM-DD', got {lines[0][:60]!r}")
    token = _date(m.group(1), "token date")
    if token > _date(today, "today") + dt.timedelta(days=1):
        raise SignoffError(f"token date {token} is in the future")
    if token < _date(min_date, "min_date"):
        raise SignoffError(f"token date {token} is before {min_date}")

    fields = {}
    for ln in lines[1:]:
        lm = LINE_RE.match(ln)
        if not lm:
            raise SignoffError(f"line is not 'key: value': {ln[:60]!r}")
        key, value = lm.group(1), lm.group(2).strip()
        if key not in required:
            raise SignoffError(f"unknown key {key!r} for {checkpoint_id}")
        if key in fields:
            raise SignoffError(f"duplicate key {key!r}")
        if not value:
            raise SignoffError(f"empty value for {key!r}")
        _check_value(key, value, required[key])
        fields[key] = value
    missing = [k for k in required if k not in fields]
    if missing:
        raise SignoffError(f"missing required keys for {checkpoint_id}: {', '.join(missing)}")
    return {"date": token.isoformat(), "fields": fields}


class _LiteralDumper(yaml.SafeDumper):
    pass


def _str_rep(dumper, data):
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


_LiteralDumper.add_representer(str, _str_rep)


def _sha(raw):
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def record_signoff(checkpoint_id, raw, *, min_date, signoff_dir=SIGNOFF_DIR, extra_required=(),
                   today=None):
    """Parse ``raw`` and write <signoff_dir>/<checkpoint_id>.yaml; never overwrites."""
    today = today or dt.date.today()
    parsed = parse_signoff(raw, checkpoint_id, min_date=min_date, today=today,
                           extra_required=extra_required)
    path = Path(signoff_dir) / f"{checkpoint_id}.yaml"
    if path.exists():
        raise SignoffError(f"{path} already exists; refusing to overwrite")
    rec = {
        "checkpoint_id": checkpoint_id,
        "raw": raw,
        "raw_sha256": _sha(raw),
        "token_date": parsed["date"],
        "min_date": _date(min_date, "min_date").isoformat(),
        "extra_required": list(extra_required),
        "fields": parsed["fields"],
        "recorded_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    text = yaml.dump(rec, Dumper=_LiteralDumper, sort_keys=False, allow_unicode=True)
    if yaml.safe_load(text)["raw"] != raw:
        raise SignoffError("raw reply does not round-trip through YAML; refusing to record")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x") as fh:
        fh.write(text)
    return path


def verify_signoff(checkpoint_id, *, signoff_dir=SIGNOFF_DIR, today=None):
    """Re-parse a recorded sign-off, check its sha256 and fields; return the fields."""
    path = Path(signoff_dir) / f"{checkpoint_id}.yaml"
    if not path.exists():
        raise SignoffError(f"no sign-off recorded at {path}")
    try:
        rec = yaml.safe_load(path.read_text())
        raw = rec["raw"]
        if not isinstance(raw, str) or _sha(raw) != rec["raw_sha256"]:
            raise SignoffError(f"{path}: raw_sha256 does not match raw")
        if rec.get("checkpoint_id", checkpoint_id) != checkpoint_id:
            raise SignoffError(f"{path}: records {rec['checkpoint_id']!r}")
        parsed = parse_signoff(raw, checkpoint_id, min_date=rec["min_date"],
                               today=today or dt.date.today(),
                               extra_required=rec.get("extra_required") or ())
    except (KeyError, TypeError, yaml.YAMLError) as exc:
        raise SignoffError(f"{path}: malformed sign-off record ({exc!r})") from None
    if parsed["date"] != rec["token_date"] or parsed["fields"] != rec["fields"]:
        raise SignoffError(f"{path}: recorded fields/date differ from the raw reply")
    return parsed["fields"]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m ta_r4.signoff")
    sub = ap.add_subparsers(dest="cmd", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("checkpoint_id")
    rec.add_argument("--raw-file", required=True)
    rec.add_argument("--min-date", required=True)
    rec.add_argument("--extra-required", nargs="*", default=[])
    rec.add_argument("--signoff-dir", default=str(SIGNOFF_DIR))
    ver = sub.add_parser("verify")
    ver.add_argument("checkpoint_id")
    ver.add_argument("--signoff-dir", default=str(SIGNOFF_DIR))
    args = ap.parse_args(argv)
    try:
        if args.cmd == "record":
            with open(args.raw_file, encoding="utf-8", newline="") as fh:
                raw = fh.read()
            path = record_signoff(args.checkpoint_id, raw, min_date=args.min_date,
                                  signoff_dir=args.signoff_dir,
                                  extra_required=args.extra_required)
            print(f"recorded {path} raw_sha256={_sha(raw)}")
        else:
            fields = verify_signoff(args.checkpoint_id, signoff_dir=args.signoff_dir)
            print(json.dumps(fields, sort_keys=True))
    except SignoffError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
