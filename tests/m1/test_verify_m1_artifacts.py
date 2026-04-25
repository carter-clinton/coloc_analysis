"""Test the M1 phase-closeout verifier.

Spec: m1-04-qc-reports-inventory-manifest-PLAN.md Task 2 step 3.

The verifier emits ``m1-PHASE-CLOSEOUT.md`` with three tables (Dimension-8,
ROADMAP, REQ) + an overall verdict line. Tests use a 2-trait synthetic
fixture dir to assert each verifier function returns sensible status codes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PYTHON = REPO_ROOT / "src" / "python"
if str(SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(SRC_PYTHON))

import verify_m1_artifacts as v  # noqa: E402


def _write_mini_inventory(yaml_path: Path,
                          harm_dir: Path,
                          parq_dir: Path,
                          munge_dir: Path,
                          qc_dir: Path) -> None:
    """Write a 2-cell mini inventory + ensure all paths resolve."""
    harm_dir.mkdir(parents=True, exist_ok=True)
    parq_dir.mkdir(parents=True, exist_ok=True)
    munge_dir.mkdir(parents=True, exist_ok=True)
    qc_dir.mkdir(parents=True, exist_ok=True)
    keys = ["bmi.EUR.GIANT-UKBB.2018", "stroke.EUR.GIGASTROKE.2022"]
    inv = {"version": "2026-04-M1", "build_target": "GRCh37", "traits": {}}
    for k in keys:
        # Touch fake files so paths resolve.
        h = harm_dir / f"{k}.GRCh37.tsv.bgz"; h.write_bytes(b"\x1f\x8b")
        p = parq_dir / f"{k}.GRCh37.parquet"; p.write_bytes(b"PAR1")
        m = munge_dir / f"{k}.sumstats.gz"; m.write_bytes(b"\x1f\x8b")
        (qc_dir / f"{k}.qc.json").write_text(json.dumps({
            "trait": k.split(".")[0],
            "n_input": 1000,
            "n_output": 980,
            "n_palindromic_dropped": 20,
            "n_maf_below_threshold": 5,
            "lambda_gc": 1.05,
            "qc_status": "PASS",
        }))
        inv["traits"][k] = {
            "trait": k.split(".")[0], "ancestry": k.split(".")[1],
            "consortium": k.split(".")[2], "year": int(k.split(".")[3]),
            "source_url": "https://example.org",
            "doi": "10.0000/test",
            "build": 37,
            "phenotype_lock": "test",
            "harmonized_path": str(h),
            "parquet_path": str(p),
            "munged_path": str(m),
            "n_total": 1000, "n_cases": None, "n_controls": None,
            "sha256_raw": "a" * 64,
            "sha256_harmonized": "b" * 64,
            "ldsc_intercept": 1.05, "ldsc_h2": 0.10,
            "qc_report_path": str(qc_dir / f"{k}.qc.html"),
            "qc_status": "PASS",
            "cohort_overlap_cohorts": ["UKB"],
            "mtag_overlap_correction_required": True,
            "dua_required": False,
            "license": "public_academic",
        }
    yaml_path.write_text(yaml.safe_dump(inv, sort_keys=False))


def _write_sha_manifest(path: Path, n_rows: int = 2) -> None:
    rows = ["relative_path\tsha256\tbytes"]
    for i in range(n_rows):
        rows.append(f"file_{i}.bgz\t{'a' * 64}\t1024")
    path.write_text("\n".join(rows) + "\n")


def _write_warnings(path: Path, sym=0, heur=0) -> None:
    path.write_text(json.dumps({
        "symmetry_warnings": [f"warn{i}" for i in range(sym)],
        "heuristic_warnings": [f"warn{i}" for i in range(heur)],
        "n_traits": 2,
        "n_pairs_filled": 1,
    }))


def test_verify_a_clean_manifests(tmp_path):
    raw = tmp_path / "raw_sha.tsv"; _write_sha_manifest(raw)
    harm = tmp_path / "harm_sha.tsv"; _write_sha_manifest(harm)
    s, e = v.verify_a(raw, harm)
    assert s == "PASS", e


def test_verify_a_bad_sha(tmp_path):
    raw = tmp_path / "raw.tsv"
    raw.write_text("relative_path\tsha256\tbytes\nfoo\tNOT_HEX\t100\n")
    harm = tmp_path / "harm.tsv"; _write_sha_manifest(harm)
    s, e = v.verify_a(raw, harm)
    assert s == "FAIL", e


def test_verify_f_clean(tmp_path):
    w = tmp_path / "w.json"; _write_warnings(w, 0, 0)
    s, e = v.verify_f(w)
    assert s == "PASS", e


def test_verify_f_symmetry_warning_fails(tmp_path):
    w = tmp_path / "w.json"; _write_warnings(w, sym=1)
    s, e = v.verify_f(w)
    assert s == "FAIL", e


def test_verify_h_all_resolve(tmp_path):
    """All inventory paths exist → PASS."""
    inv = tmp_path / "inv.yaml"
    _write_mini_inventory(inv, tmp_path / "harm", tmp_path / "parq",
                          tmp_path / "munge", tmp_path / "qc")
    s, e = v.verify_h(inv)
    assert s == "PASS", e


def test_verify_i_schema_valid(tmp_path):
    inv = tmp_path / "inv.yaml"
    _write_mini_inventory(inv, tmp_path / "harm", tmp_path / "parq",
                          tmp_path / "munge", tmp_path / "qc")
    s, e = v.verify_i(inv)
    assert s == "PASS", e


def test_verify_j_subset_invariant(tmp_path):
    inv = tmp_path / "inv.yaml"
    _write_mini_inventory(inv, tmp_path / "harm", tmp_path / "parq",
                          tmp_path / "munge", tmp_path / "qc")
    keys = tmp_path / "tk.txt"
    keys.write_text("bmi.EUR.GIANT-UKBB.2018\nstroke.EUR.GIGASTROKE.2022\n")
    s, e = v.verify_j(inv, keys, deferred_count=0)
    assert s == "PASS", e
    # The canonical pass-string is in the evidence message.
    assert "dim-j: inventory trait count matches trait_keys.txt" in e


def test_verify_j_trait_keys_not_in_inventory_fails(tmp_path):
    inv = tmp_path / "inv.yaml"
    _write_mini_inventory(inv, tmp_path / "harm", tmp_path / "parq",
                          tmp_path / "munge", tmp_path / "qc")
    keys = tmp_path / "tk.txt"
    keys.write_text("ghost.EUR.NOWHERE.2099\n")
    s, e = v.verify_j(inv, keys, deferred_count=0)
    assert s == "FAIL", e


def test_verify_req_public_data_only_pass(tmp_path):
    inv = tmp_path / "inv.yaml"
    _write_mini_inventory(inv, tmp_path / "harm", tmp_path / "parq",
                          tmp_path / "munge", tmp_path / "qc")
    s, e = v.verify_req_public_data_only(inv)
    assert s == "PASS", e


def test_full_main_emits_closeout_md(tmp_path, monkeypatch):
    """The CLI _main writes a closeout MD with all three tables."""
    inv = tmp_path / "inv.yaml"
    qc_dir = tmp_path / "qc"
    _write_mini_inventory(inv, tmp_path / "harm", tmp_path / "parq",
                          tmp_path / "munge", qc_dir)
    # Pre-create fake Quarto HTMLs so dim-g passes WARN/PASS (not FAIL).
    (qc_dir / "index.html").write_text("<html>ok</html>")
    for k in ("bmi.EUR.GIANT-UKBB.2018", "stroke.EUR.GIGASTROKE.2022"):
        (qc_dir / f"{k}.qc.html").write_text("<html>ok</html>")

    raw_sha = tmp_path / "raw_sha.tsv"; _write_sha_manifest(raw_sha)
    harm_sha = tmp_path / "harm_sha.tsv"; _write_sha_manifest(harm_sha)
    warnings = tmp_path / "w.json"; _write_warnings(warnings)
    keys = tmp_path / "tk.txt"
    keys.write_text("bmi.EUR.GIANT-UKBB.2018\nstroke.EUR.GIGASTROKE.2022\n")
    out = tmp_path / "closeout.md"

    monkeypatch.setattr(sys, "argv", [
        "verify_m1_artifacts.py",
        "--inventory", str(inv),
        "--raw-manifest", str(raw_sha),
        "--harm-manifest", str(harm_sha),
        "--qc-dir", str(qc_dir),
        "--harm-dir", str(tmp_path / "harm"),
        "--munge-dir", str(tmp_path / "munge"),
        "--warnings", str(warnings),
        "--trait-keys", str(keys),
        "--output", str(out),
    ])
    with pytest.raises(SystemExit) as exc:
        v._main()
    # Either PASS (rc 0) or FAIL (rc 1) emit the MD; we just need a valid
    # exit code and a structurally-correct closeout report.
    assert exc.value.code in (0, 1)
    txt = out.read_text()
    assert "Dimension-8 Acceptance Criteria" in txt
    assert "ROADMAP M1 Success Criteria" in txt
    assert "REQ Acceptance Tests" in txt
    assert "Overall M1 Closeout Verdict" in txt
    # dim-j entry is present.
    assert "Inventory count == trait_keys" in txt
