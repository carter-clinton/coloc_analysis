"""Unit tests for harmonize_bbj.py + validate_replication_sumstats.py
(Plan 09-02 Task 5)."""
import json
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from harmonize_bbj import extract_bbj_zip, harmonize_bbj_sumstats  # noqa: E402
from validate_replication_sumstats import (  # noqa: E402
    check_liftover_qc,
    validate_schema,
)


def test_extract_bbj_zip(tmp_path, mock_bbj_sumstats):
    """Zip extractor discovers the .tsv payload, skips README."""
    zp = tmp_path / "hum0197.v3.BBJ.T2D.v1.zip"
    with zipfile.ZipFile(zp, "w") as zf:
        zf.write(mock_bbj_sumstats, arcname="BBJ.T2D.v1.tsv")
        zf.writestr("README.txt", "schema doc - ignore")
    out_dir = tmp_path / "extracted"
    extracted = extract_bbj_zip(zp, out_dir)
    assert extracted.exists()
    assert extracted.name.lower().endswith((".tsv", ".txt"))
    assert "readme" not in extracted.name.lower()


def test_extract_bbj_zip_no_tsv_raises(tmp_path):
    zp = tmp_path / "empty.zip"
    with zipfile.ZipFile(zp, "w") as zf:
        zf.writestr("README.txt", "no payload")
    with pytest.raises(ValueError, match="no .tsv/.txt"):
        extract_bbj_zip(zp, tmp_path / "out")


def test_bbj_canonical(mock_bbj_sumstats, tmp_path, canonical_schema, monkeypatch):
    import sumstats_utils as SU

    monkeypatch.setattr(
        SU,
        "liftover_to_grch37",
        lambda df, cf: (
            df.assign(CHR=df["CHR"].astype(str)),
            {"n_input": len(df), "n_lifted": len(df), "n_dropped": 0, "drop_rate": 0.0},
        ),
    )
    out = tmp_path / "bbj_t2d.tsv.gz"
    qc_out = tmp_path / "bbj_t2d.qc.json"
    qc = harmonize_bbj_sumstats(
        mock_bbj_sumstats,
        out,
        Path("/dev/null"),
        "t2d",
        "T2D",
        qc_out=qc_out,
    )
    df = pd.read_csv(out, sep="\t", compression="gzip")
    for col in canonical_schema:
        assert col in df.columns, f"missing {col}"
    assert qc["cohort"] == "bbj_hum0197_v3"
    assert qc["trait_code"] == "T2D"
    assert qc_out.exists()
    # BBJ fixture Beta=0.08
    assert (df["BETA"] == 0.08).all()


def test_validate_schema_accepts_canonical(tmp_path):
    """Validator accepts files with all 10 canonical columns."""
    df = pd.DataFrame({
        "CHR": [1], "BP": [1000], "SNP": ["rs1"],
        "EA": ["A"], "OA": ["G"],
        "BETA": [0.1], "SE": [0.02], "P": [0.01],
        "EAF": [0.3], "N": [1000],
    })
    p = tmp_path / "ok.tsv.gz"
    df.to_csv(p, sep="\t", index=False, compression="gzip")
    res = validate_schema(p)
    assert res["valid"] is True
    assert res["missing"] == []


def test_validate_schema_rejects_missing_column(tmp_path):
    df = pd.DataFrame({
        "CHR": [1], "BP": [1000], "SNP": ["rs1"],
        "EA": ["A"], "OA": ["G"],
        "BETA": [0.1], "SE": [0.02],
        # P is missing!
        "EAF": [0.3], "N": [1000],
    })
    p = tmp_path / "bad.tsv.gz"
    df.to_csv(p, sep="\t", index=False, compression="gzip")
    res = validate_schema(p)
    assert res["valid"] is False
    assert "P" in res["missing"]


def test_check_liftover_qc_passes_at_threshold(tmp_path):
    qc = tmp_path / "qc.json"
    qc.write_text(json.dumps({"drop_rate": 0.05}))
    assert check_liftover_qc(qc, max_drop=0.05) is True


def test_check_liftover_qc_fails_above_threshold(tmp_path):
    qc = tmp_path / "qc.json"
    qc.write_text(json.dumps({"drop_rate": 0.06}))
    assert check_liftover_qc(qc, max_drop=0.05) is False
