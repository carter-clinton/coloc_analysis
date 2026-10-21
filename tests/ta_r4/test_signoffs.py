"""Conditional code-level sentinels: a configuration state that needs Carter's judgement
requires a recorded, valid sign-off whose values equal that state (B1, PLAN-INDEX §D).

Each check takes a repo root and returns a list of problems ([] = OK). Fixture repos
exercise every check; the final tests apply them to the real repo (vacuous until the
phase creates the guarded files)."""
from __future__ import annotations

import csv
import datetime as dt
import re
import subprocess
from pathlib import Path

import pytest
import yaml

from ta_r4.signoff import SignoffError, canonical_sha256, record_signoff, verify_signoff

from .conftest import REPO_ROOT

PHASE_REL = ".planning/phases/ta-r4-head-to-head-reanalysis-and-submission"
SIGNOFF_REL = f"{PHASE_REL}/signoffs"
SENTINEL_REL = f"{PHASE_REL}/OSF-R4-POSTED.json"
LOCKABLE = ("coloc_priors", "decision_rules", "simulation")
PARTIAL_KEYS = ("ci_pos_mcnemar_ns", "ci_pos_mcnemar_opposite", "ci_neg_mcnemar_ns",
                "ci_neg_mcnemar_opposite")
W9_LINE = re.compile(r"^\s*- \[x\] ta-r4-W9-submission-prep-PLAN\.md", re.MULTILINE)


def _verify(repo, cid):
    """(fields, problems)."""
    try:
        return verify_signoff(cid, signoff_dir=Path(repo) / SIGNOFF_REL), []
    except SignoffError as exc:
        return None, [f"{cid}: {exc}"]


def _same(a, b):
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)


def _load(path):
    return yaml.safe_load(path.read_text()) or {}


def check_all_signoffs_verify(repo):
    sdir = Path(repo) / SIGNOFF_REL
    if not sdir.is_dir():
        return []
    return [p for f in sorted(sdir.glob("*.yaml")) for p in _verify(repo, f.stem)[1]]


def _carter_cells(repo):
    """{trait.<trait>.<ancestry>.<field>: value} for every cell whose <field>_source is Carter's."""
    path = Path(repo) / "config/ta_r4/trait_manifest.tsv"
    if not path.exists():
        return {}
    out = {}
    with path.open() as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            for col, src in row.items():
                if col.endswith("_source") and str(src).startswith("Carter "):
                    field = col[: -len("_source")]
                    out[f"trait.{row['trait']}.{row['ancestry']}.{field}"] = (row[field], src)
    return out


def check_review_decisions(repo):
    rd_path = Path(repo) / "config/ta_r4/review_decisions.yaml"
    if not rd_path.exists():
        return []
    fields, probs = _verify(repo, "W2c-T4")
    if probs:
        return probs
    rec = _load(Path(repo) / SIGNOFF_REL / "W2c-T4.yaml")
    rd = _load(rd_path)
    for key in ("ukb_native", "qtl_scope"):
        if not _same(rd.get(key), fields[key]):
            probs.append(f"review_decisions {key}={rd.get(key)!r} != W2c-T4 {fields[key]!r}")
    signed = {k: v for k, v in fields.items() if k.startswith("trait.")}
    facts = rd.get("trait_facts") or {}
    if set(facts) != set(signed):
        probs.append(f"review_decisions trait_facts keys {sorted(facts)} != W2c-T4 {sorted(signed)}")
    for k, v in signed.items():
        if k in facts and not _same(facts[k], v):
            probs.append(f"review_decisions {k}={facts[k]!r} != W2c-T4 {v!r}")
    cells = _carter_cells(repo)
    for k, (val, src) in cells.items():
        if k not in signed:
            probs.append(f"trait_manifest {k} sourced {src!r} has no W2c-T4 field")
        elif not _same(val, signed[k]):
            probs.append(f"trait_manifest {k}={val!r} != W2c-T4 {signed[k]!r}")
        elif src != f"Carter {rec['token_date']}":
            probs.append(f"trait_manifest {k} source {src!r} != 'Carter {rec['token_date']}'")
    for k in signed:
        if k not in cells:
            probs.append(f"W2c-T4 {k} has no Carter-sourced trait_manifest cell")
    return probs


def check_locks(repo):
    cfg = {n: Path(repo) / f"config/ta_r4/{n}.yaml" for n in LOCKABLE}
    loaded = {n: _load(p) for n, p in cfg.items() if p.exists()}
    if not any(d.get("locked") is True for d in loaded.values()):
        return []
    fields, probs = _verify(repo, "W4a-T3")
    if probs:
        return probs
    for n in ("coloc_priors", "decision_rules"):
        if n not in loaded:
            probs.append(f"a config is locked but config/ta_r4/{n}.yaml is missing")
    pri, dr = loaded.get("coloc_priors", {}), loaded.get("decision_rules", {})
    expect = {"p12_primary": pri.get("p12_primary"), "kappa_cut": dr.get("kappa_cut"),
              "n_both_min": dr.get("n_both_min")}
    for k in PARTIAL_KEYS:
        expect[f"partial_rule.{k}"] = (dr.get("partial_rule") or {}).get(k)
    for k, v in expect.items():
        if not _same(v, fields[k]):
            probs.append(f"locked config {k}={v!r} != W4a-T3 {fields[k]!r}")
    if "confirmatory" not in dr:
        probs.append("decision_rules.yaml has no confirmatory block")
    elif canonical_sha256(dr["confirmatory"]) != fields["confirmatory_sha256"]:
        probs.append("decision_rules confirmatory block sha256 != W4a-T3 confirmatory_sha256")
    return probs


def check_osf_sentinel(repo):
    tracked = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--error-unmatch", SENTINEL_REL],
        capture_output=True, text=True,
    ).returncode == 0
    return _verify(repo, "W4b-T3")[1] if tracked else []


def check_venue_overlay(repo):
    if not (Path(repo) / "docs/manuscript/r4/submission/venue_overlay.yaml").exists():
        return []
    return _verify(repo, "W9-T1")[1]


def check_w9_roadmap(repo):
    roadmap = Path(repo) / ".planning/ROADMAP.md"
    if not roadmap.exists() or not W9_LINE.search(roadmap.read_text()):
        return []
    return _verify(repo, "W9-T4")[1]


CHECKS = (check_all_signoffs_verify, check_review_decisions, check_locks, check_osf_sentinel,
          check_venue_overlay, check_w9_roadmap)


# ---------------------------------------------------------------- fixtures

TODAY = dt.date.today().isoformat()
CONF = {"contrasts": ["A1_matched_vs_A3_1kg", "A2_identity_vs_A3_1kg"], "reference_arm": "A3_1kg",
        "rows": {"row_class": "primary", "ancestry": "EUR"}}
DR = {"alpha": 0.025, "kappa_cut": 0.6, "n_both_min": 10, "confirmatory": CONF,
      "partial_rule": {k: "HETEROGENEOUS" for k in PARTIAL_KEYS}, "locked": True}
PRI = {"p1": 1e-4, "p2": 1e-4, "p12_primary": 5e-6, "p12_sensitivity": 1e-5, "locked": True}


def _w4a_raw(kappa="0.6", conf=CONF):
    lines = [f"carter-approved {TODAY}", "p12_primary: 5e-6", f"kappa_cut: {kappa}", "n_both_min: 10"]
    lines += [f"partial_rule.{k}: HETEROGENEOUS" for k in PARTIAL_KEYS]
    lines += [f"confirmatory_sha256: {canonical_sha256(conf)}", "draft: approved"]
    return "\n".join(lines) + "\n"


@pytest.fixture
def repo(tmp_path):
    (tmp_path / SIGNOFF_REL).mkdir(parents=True)
    (tmp_path / "config/ta_r4").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    return tmp_path


def _sign(repo, cid, raw, extra=()):
    record_signoff(cid, raw, min_date="2026-10-01", signoff_dir=repo / SIGNOFF_REL,
                   extra_required=extra)


def _write_locked(repo, dr=DR, pri=PRI):
    (repo / "config/ta_r4/decision_rules.yaml").write_text(yaml.safe_dump(dr))
    (repo / "config/ta_r4/coloc_priors.yaml").write_text(yaml.safe_dump(pri))


def test_empty_fixture_is_clean(repo):
    assert [p for c in CHECKS for p in c(repo)] == []


def test_locked_without_signoff_fails(repo):
    _write_locked(repo)
    assert check_locks(repo)


def test_locked_with_matching_signoff_passes(repo):
    _write_locked(repo)
    _sign(repo, "W4a-T3", _w4a_raw())
    assert check_locks(repo) == []
    assert check_all_signoffs_verify(repo) == []


def test_locked_kappa_mismatch_fails(repo):
    _write_locked(repo)
    _sign(repo, "W4a-T3", _w4a_raw(kappa="0.7"))
    assert any("kappa_cut" in p for p in check_locks(repo))


def test_confirmatory_block_edit_fails(repo):
    _sign(repo, "W4a-T3", _w4a_raw())
    edited = dict(DR, confirmatory=dict(CONF, reference_arm="A3_ukb"))
    _write_locked(repo, dr=edited)
    assert any("confirmatory" in p for p in check_locks(repo))


def test_simulation_lock_alone_triggers(repo):
    (repo / "config/ta_r4/simulation.yaml").write_text("locked: true\n")
    assert check_locks(repo)


def test_tampered_signoff_file_fails(repo):
    _sign(repo, "W7-T3", f"carter-approved {TODAY}\ninstructions: go\n")
    f = repo / SIGNOFF_REL / "W7-T3.yaml"
    f.write_text(f.read_text().replace("instructions: go", "instructions: GO"))
    assert check_all_signoffs_verify(repo)


TM_HEADER = ["trait", "ancestry", "type", "type_source", "sdY", "sdY_source", "N_median",
             "source_study", "evidence"]


def _write_tm(repo, sdy="1.0", src=None):
    src = src or f"Carter {TODAY}"
    rows = [TM_HEADER,
            ["bmi", "EUR", "quant", "Yengo 2018", sdy, src, "681275", "Yengo", "x"],
            ["t2d", "EUR", "cc", "DIAMANTE", "", "", "898130", "DIAMANTE", "y"]]
    (repo / "config/ta_r4/trait_manifest.tsv").write_text("\n".join("\t".join(r) for r in rows) + "\n")


def _w2c(repo, sdy="1.0"):
    key = "trait.bmi.EUR.sdY"
    _sign(repo, "W2c-T4", f"carter-approved {TODAY}\nukb_native: native\nqtl_scope: full\n{key}: {sdy}\n",
          extra=[key])
    rd = {"ukb_native": "native", "qtl_scope": "full", "trait_facts": {key: sdy},
          "signoff": "signoffs/W2c-T4.yaml"}
    (repo / "config/ta_r4/review_decisions.yaml").write_text(yaml.safe_dump(rd))


def test_review_decisions_without_signoff_fails(repo):
    (repo / "config/ta_r4/review_decisions.yaml").write_text("ukb_native: native\nqtl_scope: full\n")
    assert check_review_decisions(repo)


def test_review_decisions_consistent_passes(repo):
    _w2c(repo)
    _write_tm(repo)
    assert check_review_decisions(repo) == []
    assert check_all_signoffs_verify(repo) == []


def test_trait_manifest_cell_edited_after_signoff_fails(repo):
    _w2c(repo)
    _write_tm(repo, sdy="1.1")
    assert any("trait.bmi.EUR.sdY" in p for p in check_review_decisions(repo))


def test_trait_manifest_missing_carter_cell_fails(repo):
    _w2c(repo)
    _write_tm(repo, src="Yengo 2018")
    assert any("no Carter-sourced" in p for p in check_review_decisions(repo))


def test_review_decisions_value_mismatch_fails(repo):
    _w2c(repo)
    _write_tm(repo)
    rd = repo / "config/ta_r4/review_decisions.yaml"
    rd.write_text(rd.read_text().replace("ukb_native: native", "ukb_native: hm3"))
    assert any("ukb_native" in p for p in check_review_decisions(repo))


def test_w9_checked_without_signoff_fails(repo):
    (repo / ".planning/ROADMAP.md").write_text("- [x] ta-r4-W9-submission-prep-PLAN.md — venue\n")
    assert check_w9_roadmap(repo)
    (repo / ".planning/ROADMAP.md").write_text("- [ ] ta-r4-W9-submission-prep-PLAN.md — venue\n")
    assert check_w9_roadmap(repo) == []


def test_w9_checked_with_signoff_passes(repo):
    (repo / ".planning/ROADMAP.md").write_text("- [x] ta-r4-W9-submission-prep-PLAN.md — venue\n")
    _sign(repo, "W9-T4", f"carter-approved {TODAY}\njournal: J\nsubmitted_date: {TODAY}\n"
                         "manuscript_id: M-1\nosf_url: https://osf.io/az52u\n")
    assert check_w9_roadmap(repo) == []


def test_venue_overlay_requires_w9t1(repo):
    v = repo / "docs/manuscript/r4/submission/venue_overlay.yaml"
    v.parent.mkdir(parents=True)
    v.write_text("venue: X\n")
    assert check_venue_overlay(repo)
    _sign(repo, "W9-T1", f"carter-approved {TODAY}\nvenue: X\n")
    assert check_venue_overlay(repo) == []


def test_tracked_osf_sentinel_requires_w4b(repo):
    s = repo / SENTINEL_REL
    s.write_text("{}\n")
    assert check_osf_sentinel(repo) == []          # untracked: not live
    subprocess.run(["git", "-C", str(repo), "add", SENTINEL_REL], check=True)
    assert check_osf_sentinel(repo)
    _sign(repo, "W4b-T3", f"carter-approved {TODAY}\nposted: yes\n")
    assert check_osf_sentinel(repo) == []


# ---------------------------------------------------------------- real repo

@pytest.mark.parametrize("check", CHECKS, ids=lambda c: c.__name__)
def test_real_repo(check):
    assert check(REPO_ROOT) == []
