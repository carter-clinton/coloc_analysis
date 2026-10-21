"""tests/ta_r4 (a package named ``ta_r4``) must not shadow src/python/ta_r4, and must not
break the tests/m3 ``from conftest import ...`` imports (W0a hand-off, W0b1 orchestrator fix)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_PKG = REPO_ROOT / "src" / "python" / "ta_r4"


def test_source_modules_resolve():
    import ta_r4.arms
    import ta_r4.paths
    from ta_r4.arms import ARMS  # noqa: F401
    from ta_r4.paths import result_dirs  # noqa: F401

    for mod in (ta_r4.paths, ta_r4.arms):
        assert Path(mod.__file__).resolve().parent == SRC_PKG, mod.__file__


def test_m3_conftest_import_still_works():
    probe = "tests/m3/test_ld_npz_to_rds.py::test_bm_to_npz_omitted_allele_freq_is_all_nan_and_warns"
    r4 = "tests/ta_r4/test_storage_on_rs1.py::test_check_function_rejects_share_target"
    for order in ((r4, probe), (probe, r4)):
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *order],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=300,
        )
        assert res.returncode == 0, res.stdout[-3000:] + res.stderr[-2000:]
        assert "2 passed" in res.stdout, res.stdout[-2000:]
