"""GWAS Catalog v_lock_M2 manifest row tests (REQ-CATALOG-VERSION-LOCK, D-M2-05).

Pitfall 10: SHA-256 hashes the .zip BYTES, NOT the unpacked TSV.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = PROJECT_ROOT / "data" / "catalogs" / "catalog_lock_manifest.tsv"
CATALOG_ZIP = PROJECT_ROOT / "data" / "catalogs" / "gwas-catalog-associations-full.zip"

_KEY = "gwas_catalog.v_lock_M2"


pytestmark = pytest.mark.skipif(
    not MANIFEST.exists(),
    reason="data/catalogs/catalog_lock_manifest.tsv missing",
)


def _row_for_key(key: str) -> dict | None:
    """Return dict of header->value for the row whose first column == key."""
    with open(MANIFEST) as fh:
        header = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            cols = line.rstrip("\n").split("\t")
            if cols and cols[0] == key:
                return dict(zip(header, cols))
    return None


def test_v_lock_M2_row_exists():
    """A row keyed gwas_catalog.v_lock_M2 must exist (Wave 0 Task 5)."""
    row = _row_for_key(_KEY)
    assert row is not None, f"Missing {_KEY} row in {MANIFEST}"


def test_sha256_is_64_hex():
    """SHA-256 column is exactly 64 hex chars and matches the .zip bytes (Pitfall 10)."""
    row = _row_for_key(_KEY)
    assert row is not None
    sha = row.get("sha256", "")
    assert re.fullmatch(r"[0-9a-fA-F]{64}", sha), f"Bad SHA-256: {sha!r}"
    if CATALOG_ZIP.exists():
        h = hashlib.sha256()
        with open(CATALOG_ZIP, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        assert h.hexdigest() == sha.lower(), (
            "Manifest SHA-256 must match recomputed sha256sum of the .zip bytes (Pitfall 10)"
        )
