"""The R4 amendment's public text (W4a/W4b; checker W4).

The public text is extract(<amendment>): the text strictly between the two marker lines. Every scan below
covers the WHOLE extract. Banned words and internal paths are literal properties of public text, so a text
scan is the right instrument here (PLAN-INDEX §B.3 exception)."""
from __future__ import annotations

import re
import subprocess
import sys

import pytest
import yaml

from ta_r4 import extract_paste_block as epb
from ta_r4.r4_lock_gate import LOCKED_PATHS

from .conftest import REPO_ROOT

AMD = REPO_ROOT / ".planning/amendments"
DRAFT = AMD / "osf-amendment-r4-DRAFT.md"
FINAL = AMD / "osf-amendment-r4-FINAL.md"
PUBLIC = AMD / "osf-amendment-r4-PUBLIC.md"
RULES = REPO_ROOT / "config/ta_r4/decision_rules.yaml"

FRAMING = re.compile(r"\b(pivot|revision|salvage|audit-driven)\b", re.IGNORECASE)
INTERNAL = (".planning/", "/rs1/", "/gpfs", "/share/", "data/r4", "signoffs/", "DEC-20", "Pre-Paste",
            "do NOT paste")
CHECKLIST = re.compile(r"^\s*[-*] \[[ xX]\]", re.MULTILINE)
OSF_PREREG_CLAIM = re.compile(r"pre-?registered\s+(on|at|with|in)\s+(the\s+)?OSF", re.IGNORECASE)
PARAGRAPHS = "abcdefghijklm"


def framing_violations(text):
    return sorted({m.group(0) for m in FRAMING.finditer(text)})


def internal_violations(text, final=False):
    bad = [s for s in INTERNAL if s in text]
    if final and "CARTER-LOCK" in text:
        bad.append("CARTER-LOCK")
    if CHECKLIST.search(text):
        bad.append("markdown checklist item")
    return bad


def missing_paragraphs(text):
    return [p for p in PARAGRAPHS if not re.search(rf"^\({p}\) ", text, re.MULTILINE)]


def confirmatory_problem(text, rules):
    rendered = epb.render_confirmatory(rules)
    return [] if rendered in text else ["render_confirmatory(rules) is not verbatim in the extract"]


def frozen_path_needles():
    """LOCKED_PATHS as the public text names them: the phase-directory entry by its manifests/ suffix."""
    return [p if not p.startswith(".planning/") else "manifests/" + p.split("/manifests/", 1)[1]
            for p in LOCKED_PATHS]


def _rules():
    return yaml.safe_load(RULES.read_text())


def _write(tmp_path, body, name="a.md"):
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


S, E = epb.START_MARKER, epb.END_MARKER


# ------------------------------------------------------------------ extract()

def test_extract_returns_text_strictly_between_markers(tmp_path):
    p = _write(tmp_path, f"head `{S}` mention\nx\n{S}\nline 1\n\nline 2\n{E}\ntail\n")
    assert epb.extract(p) == "line 1\n\nline 2\n"


@pytest.mark.parametrize("body", [
    f"a\n{E}\nb\n",                       # start missing
    f"a\n{S}\nb\n",                       # end missing
    f"{S}\na\n{S}\nb\n{E}\n",             # start duplicated
    f"{S}\na\n{E}\nb\n{E}\n",             # end duplicated
    f"x\n{E}\nbody\n{S}\ny\n",            # end before start (negative control)
])
def test_extract_raises_on_bad_markers(tmp_path, body):
    with pytest.raises(epb.MarkerError):
        epb.extract(_write(tmp_path, body))


def test_extract_and_cli_are_byte_deterministic(tmp_path):
    p = _write(tmp_path, f"pre\n{S}\nα – “quoted” \t tab\nend line\n{E}\npost\n")
    a, b = epb.extract(p), epb.extract(p)
    assert a == b
    out1, out2 = tmp_path / "o1.md", tmp_path / "o2.md"
    for out in (out1, out2):
        r = subprocess.run([sys.executable, "-m", "ta_r4.extract_paste_block", "--in", str(p), "--out", str(out)],
                           cwd=REPO_ROOT / "src/python", capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
    assert out1.read_bytes() == out2.read_bytes() == a.encode("utf-8")


def test_cli_refuses_bad_markers(tmp_path):
    p = _write(tmp_path, f"{E}\nx\n{S}\n")
    out = tmp_path / "o.md"
    r = subprocess.run([sys.executable, "-m", "ta_r4.extract_paste_block", "--in", str(p), "--out", str(out)],
                       cwd=REPO_ROOT / "src/python", capture_output=True, text=True)
    assert r.returncode != 0 and not out.exists()


# ------------------------------------------------------------------ scanners (negative controls)

def test_framing_scan_catches_a_banned_word(tmp_path):
    p = _write(tmp_path, f"{S}\nThis study is a Pivot from earlier work.\n{E}\n")
    assert framing_violations(epb.extract(p)) == ["Pivot"]


def test_internal_scan_catches_an_internal_path(tmp_path):
    p = _write(tmp_path, f"{S}\nSee .planning/x for details.\n{E}\n")
    assert internal_violations(epb.extract(p)) == [".planning/"]


def test_internal_scan_catches_a_checklist_and_a_placeholder_in_final(tmp_path):
    p = _write(tmp_path, f"{S}\n- [ ] do it\nkappa ‹CARTER-LOCK: kappa_cut›\n{E}\n")
    assert internal_violations(epb.extract(p), final=True) == ["CARTER-LOCK", "markdown checklist item"]
    assert internal_violations(epb.extract(p), final=False) == ["markdown checklist item"]


def test_confirmatory_check_fails_on_a_changed_cluster_rule():
    text = epb.extract(DRAFT)
    rules = _rules()
    assert confirmatory_problem(text, rules) == []
    rules["confirmatory"]["clusters"] = "row_id of the confirmatory rows"
    assert confirmatory_problem(text, rules), "a changed cluster rule must render text the extract lacks"


def test_render_confirmatory_reads_the_yaml():
    rules = _rules()
    out = epb.render_confirmatory(rules)
    for needle in (str(rules["confirmatory"]["clusters"]), str(rules["threshold_primary"]), str(rules["alpha"]),
                   str(rules["bootstrap_B"]), str(rules["bootstrap_seed"]), "n_both >= n_both_min"):
        assert needle in out
    sf = rules["confirmatory"]["region_signflip"]
    for needle in (sf["d_r"], sf["statistic"], sf["p"], sf["monte_carlo"], f"k <= {sf['exact_max_k']}",
                   f"n_regions_min = {rules['confirmatory']['n_regions_min']}", "row-level McNemar test (descriptive",
                   "n_regions >= n_regions_min"):
        assert needle in out, needle
    assert epb.render_confirmatory(rules) == out


@pytest.mark.parametrize("path, value", [(("confirmatory", "n_regions_min"), 6),
                                         (("confirmatory", "region_signflip", "exact_max_k"), 19)])
def test_confirmatory_check_fails_on_a_changed_signflip_rule(path, value):
    text = epb.extract(DRAFT)
    rules = _rules()
    assert confirmatory_problem(text, rules) == []
    d = rules
    for k in path[:-1]:
        d = d[k]
    d[path[-1]] = value
    assert confirmatory_problem(text, rules), f"{path} = {value} must render text the extract lacks"


# ------------------------------------------------------------------ the DRAFT

def test_draft_extract_framing():
    assert framing_violations(epb.extract(DRAFT)) == []


def test_draft_extract_internal_content():
    assert internal_violations(epb.extract(DRAFT)) == []


def test_draft_extract_has_paragraphs_a_to_m():
    assert missing_paragraphs(epb.extract(DRAFT)) == []


def test_draft_extract_carries_the_rendered_confirmatory_block():
    assert confirmatory_problem(epb.extract(DRAFT), _rules()) == []


def test_draft_extract_names_every_frozen_path():
    text = epb.extract(DRAFT)
    assert [n for n in frozen_path_needles() if f"`{n}`" not in text] == []


def test_draft_extract_makes_no_osf_preregistration_claim():
    text = epb.extract(DRAFT)
    assert OSF_PREREG_CLAIM.search(text) is None
    assert "analysis locked in commit" in text
    assert OSF_PREREG_CLAIM.search("R4 was pre-registered on OSF.")   # the pattern itself discriminates


# ------------------------------------------------------------------ FINAL / PUBLIC (W4b)

def _need(path):
    if not path.exists():
        pytest.skip(f"{path.name} does not exist yet (written in W4b)")


def test_final_extract_scans():
    _need(FINAL)
    text = epb.extract(FINAL)
    assert framing_violations(text) == []
    assert internal_violations(text, final=True) == []
    assert missing_paragraphs(text) == []
    assert confirmatory_problem(text, _rules()) == []
    assert [n for n in frozen_path_needles() if f"`{n}`" not in text] == []
    assert OSF_PREREG_CLAIM.search(text) is None


def test_public_is_extract_of_final():
    _need(PUBLIC)
    _need(FINAL)
    pub = PUBLIC.read_text(encoding="utf-8")
    assert PUBLIC.read_bytes() == epb.extract(FINAL).encode("utf-8")
    assert framing_violations(pub) == [] and internal_violations(pub, final=True) == []
