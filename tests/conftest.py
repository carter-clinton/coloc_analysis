"""Root pytest configuration — marker registration + shared test constants."""

import os

# ---------------------------------------------------------------------------
# Contention-safe subprocess wall-clock budget for EVERY R round-trip in the
# m3 R-execution test families (test_stitch_subregions_to_rds,
# test_finemap_loader_contract, test_ld_npz_to_rds).
#
# Each R subprocess that touches reticulate pays a fixed ~66s cold-start
# (embedded Python + numpy + pyliftover import; the 1.2 MB real liftover chain
# parse is only ~1.8s of that). On the shared HPC node (32 cores, many
# concurrent users, OpenBLAS-threaded R) that fixed cost balloons several-fold
# under transient memory/CPU pressure. Tight literal per-call budgets (60-300s)
# left too little headroom over the ~66s floor, so a contention spike raised
# subprocess.TimeoutExpired and pytest reported the (otherwise green) R test as
# FAILED — the m3-W2-stitch-rds-test-failures flake CLASS (transient FAILs in a
# full-suite run; 0 on a clean re-run + green in isolation). A single shared
# budget gives ~13x headroom over the cold-start floor so a wall-clock artifact
# can no longer masquerade as a logic failure. It does NOT relax any assertion:
# a real defect still fails fast (rc!=0 / wrong value); only genuinely-hung R is
# allowed to run longer before timing out. Override via M3_R_SUBPROCESS_TIMEOUT_S.
#
# Lives in the ROOT tests/conftest.py because that is the module pytest imports
# as the bare ``conftest`` (the tests/m3 conftest is shadowed by it under the
# default prepend import mode), giving all three m3 R-exec modules ONE source of
# truth via ``from conftest import R_SUBPROCESS_TIMEOUT_S``.
R_SUBPROCESS_TIMEOUT_S = int(os.environ.get("M3_R_SUBPROCESS_TIMEOUT_S", "900"))


def pytest_configure(config):
    """Register custom markers to avoid PytestUnknownMarkWarning."""
    config.addinivalue_line("markers", "phase4: Phase 4 matched-N cross-ancestry concordance tests")
    config.addinivalue_line("markers", "phase5: Phase 5 pathway + partitioned heritability tests")
    config.addinivalue_line("markers", "phase9: Phase 9 replication in independent cohorts tests")
