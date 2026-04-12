"""Phase 1 pytest fixtures -- toy susie fits + mock LD."""
import json
from pathlib import Path
import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"
FIXTURE_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def fixtures_dir():
    return FIXTURE_DIR
