"""Unit tests for ta_r4.signoff: auto-mode's bare "approved" can never be recorded (B1)."""
from __future__ import annotations

import datetime as dt
import subprocess
import sys

import pytest
import yaml

from ta_r4.signoff import SCHEMAS, SignoffError, parse_signoff, record_signoff, verify_signoff

from .conftest import REPO_ROOT

TODAY = dt.date(2026, 10, 21)
MIN = dt.date(2026, 10, 1)
SHA = "a" * 64

W4A = f"""carter-approved 2026-10-21
p12_primary: 5e-6
kappa_cut: 0.6
n_both_min: 10
partial_rule.ci_pos_mcnemar_ns: HETEROGENEOUS
partial_rule.ci_pos_mcnemar_opposite: HETEROGENEOUS
partial_rule.ci_neg_mcnemar_ns: HETEROGENEOUS
partial_rule.ci_neg_mcnemar_opposite: DEFLATION
confirmatory_sha256: {SHA}
draft: approved
"""


def _p(raw, cid="W3b-T3", **kw):
    kw.setdefault("min_date", MIN)
    kw.setdefault("today", TODAY)
    return parse_signoff(raw, cid, **kw)


def test_schemas_cover_every_checkpoint():
    assert set(SCHEMAS) == {"W2c-T4", "W3b-T3", "W4a-T3", "W4b-T3", "W7-T3", "W8b-T3", "W9-T1", "W9-T4"}
    assert "ukb_native" not in SCHEMAS["W4a-T3"]["keys"]


def test_valid_w3b():
    out = _p("carter-approved 2026-10-21\ninstructions: proceed as drafted\n")
    assert out == {"date": "2026-10-21", "fields": {"instructions": "proceed as drafted"}}


def test_valid_w4a():
    out = _p(W4A, "W4a-T3")
    assert out["fields"]["kappa_cut"] == "0.6"
    assert out["fields"]["partial_rule.ci_neg_mcnemar_opposite"] == "DEFLATION"


def test_valid_w2c_with_dynamic_keys():
    raw = ("carter-approved 2026-10-21\nukb_native: hm3\nqtl_scope: tissues_frozen+eqtl_only\n"
           "trait.hypertension.EUR.type: cc\n")
    out = _p(raw, "W2c-T4", extra_required=["trait.hypertension.EUR.type"])
    assert out["fields"]["trait.hypertension.EUR.type"] == "cc"
    with pytest.raises(SignoffError, match="^WAIT:"):
        _p(raw, "W2c-T4", extra_required=["trait.hypertension.EUR.type", "trait.t2d.EUR.sdY"])


def test_valid_w9t4():
    raw = ("carter-approved 2026-10-21\njournal: X\nsubmitted_date: 2026-10-20\n"
           "manuscript_id: AB-1\nosf_url: https://osf.io/az52u\n")
    assert _p(raw, "W9-T4")["fields"]["osf_url"] == "https://osf.io/az52u"


@pytest.mark.parametrize("raw", [
    "approved",
    "Approved.",
    "approved\ninstructions: x\n",
    "carter-approved\ninstructions: x\n",
    "carter-approved 2026-13-01\ninstructions: x\n",
    "Carter-approved 2026-10-21\ninstructions: x\n",
    "carter-approved 2026-10-21 ok\ninstructions: x\n",
    "carter-approved 2026-10-23\ninstructions: x\n",     # after today + 1 day
    "carter-approved 2026-09-30\ninstructions: x\n",     # before min_date
    "carter-approved 2026-10-21\n",                      # missing required key
    "carter-approved 2026-10-21\ninstructions:\n",       # empty value
    "carter-approved 2026-10-21\ninstructions: x\ninstructons: y\n",   # unknown key
    "carter-approved 2026-10-21\ninstructions: x\ninstructions: y\n",  # duplicate key
    "carter-approved 2026-10-21\ninstructions x\n",      # not key: value
    "",
])
def test_rejections(raw):
    with pytest.raises(SignoffError, match="^WAIT:"):
        _p(raw)


def test_tomorrow_is_allowed():
    assert _p("carter-approved 2026-10-22\ninstructions: x\n")["date"] == "2026-10-22"


@pytest.mark.parametrize("key,bad", [
    ("partial_rule.ci_pos_mcnemar_ns", "MAYBE"),
    ("confirmatory_sha256", "A" * 64),
    ("confirmatory_sha256", "a" * 63),
    ("draft", "yes"),
])
def test_w4a_enum_violations(key, bad):
    raw = "\n".join(f"{key}: {bad}" if ln.startswith(key + ":") else ln for ln in W4A.splitlines())
    with pytest.raises(SignoffError, match="^WAIT:"):
        _p(raw, "W4a-T3")


@pytest.mark.parametrize("cid,raw", [
    ("W2c-T4", "carter-approved 2026-10-21\nukb_native: both\nqtl_scope: full\n"),
    ("W2c-T4", "carter-approved 2026-10-21\nukb_native: native\nqtl_scope: some\n"),
    ("W4b-T3", "carter-approved 2026-10-21\nposted: no\n"),
])
def test_other_enum_violations(cid, raw):
    with pytest.raises(SignoffError, match="^WAIT:"):
        _p(raw, cid)


def test_unknown_checkpoint():
    with pytest.raises(SignoffError, match="^WAIT:"):
        _p("carter-approved 2026-10-21\ninstructions: x\n", "W5a-T1")


def test_record_and_verify_roundtrip(tmp_path):
    raw = "carter-approved " + dt.date.today().isoformat() + "\ninstructions: run it\n"
    path = record_signoff("W7-T3", raw, min_date="2026-10-01", signoff_dir=tmp_path)
    assert path == tmp_path / "W7-T3.yaml"
    rec = yaml.safe_load(path.read_text())
    assert rec["raw"] == raw
    assert set(rec) >= {"raw", "raw_sha256", "token_date", "fields", "recorded_utc"}
    assert verify_signoff("W7-T3", signoff_dir=tmp_path) == {"instructions": "run it"}
    with pytest.raises(SignoffError, match="^WAIT:"):
        record_signoff("W7-T3", raw, min_date="2026-10-01", signoff_dir=tmp_path)


def test_record_refuses_bare_approved(tmp_path):
    with pytest.raises(SignoffError, match="^WAIT:"):
        record_signoff("W3b-T3", "approved", min_date="2026-10-01", signoff_dir=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_verify_detects_one_char_edit(tmp_path):
    raw = "carter-approved " + dt.date.today().isoformat() + "\ninstructions: run it\n"
    path = record_signoff("W8b-T3", raw, min_date="2026-10-01", signoff_dir=tmp_path)
    text = path.read_text()
    assert "run it" in text
    path.write_text(text.replace("run it", "run iT"))
    with pytest.raises(SignoffError, match="^WAIT:"):
        verify_signoff("W8b-T3", signoff_dir=tmp_path)


def test_verify_missing(tmp_path):
    with pytest.raises(SignoffError, match="^WAIT:"):
        verify_signoff("W9-T1", signoff_dir=tmp_path)


def _cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "ta_r4.signoff", *args],
        cwd=REPO_ROOT / "src" / "python", capture_output=True, text=True, timeout=60,
    )


def test_cli_record_bare_approved_exits_1(tmp_path):
    raw = tmp_path / "raw.txt"
    raw.write_text("approved\n")
    sdir = tmp_path / "signoffs"
    res = _cli("record", "W3b-T3", "--raw-file", str(raw), "--min-date", "2026-10-01",
               "--signoff-dir", str(sdir))
    assert res.returncode == 1
    assert "WAIT:" in res.stderr + res.stdout
    assert not (sdir / "W3b-T3.yaml").exists()


def test_cli_record_then_verify(tmp_path):
    raw = tmp_path / "raw.txt"
    raw.write_text("carter-approved " + dt.date.today().isoformat() + "\nvenue: Neutral\n")
    sdir = tmp_path / "signoffs"
    res = _cli("record", "W9-T1", "--raw-file", str(raw), "--min-date", "2026-10-01",
               "--signoff-dir", str(sdir))
    assert res.returncode == 0, res.stderr
    assert _cli("verify", "W9-T1", "--signoff-dir", str(sdir)).returncode == 0
    res = _cli("verify", "W9-T4", "--signoff-dir", str(sdir))
    assert res.returncode == 1 and "WAIT:" in res.stderr
