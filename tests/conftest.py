"""Root pytest configuration — marker registration for all phases."""


def pytest_configure(config):
    """Register custom markers to avoid PytestUnknownMarkWarning."""
    config.addinivalue_line("markers", "phase4: Phase 4 matched-N cross-ancestry concordance tests")
    config.addinivalue_line("markers", "phase5: Phase 5 pathway + partitioned heritability tests")
    config.addinivalue_line("markers", "phase9: Phase 9 replication in independent cohorts tests")
