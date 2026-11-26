"""The R4 Snakemake --conda-prefix, read from its single source of truth: the R4_CONDA_PREFIX= line of bin/r4_fire.sh."""
from __future__ import annotations

import re
from pathlib import Path

FIRE_SCRIPT = Path(__file__).resolve().parents[3] / "bin/r4_fire.sh"
_LINE = re.compile(r"^R4_CONDA_PREFIX=(\S+)$")


def r4_conda_prefix(fire_script=FIRE_SCRIPT):
    found = [m.group(1) for m in map(_LINE.match, Path(fire_script).read_text().splitlines()) if m]
    if len(found) != 1:
        raise RuntimeError(f"{fire_script}: {len(found)} R4_CONDA_PREFIX= assignment lines, want exactly 1")
    return found[0]
