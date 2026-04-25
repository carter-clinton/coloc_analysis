"""M1 Wave 1 portal sumstats download rules.

Plan: m1-01-portal-fetches-and-aragam-route. One rule per source_tag in
config/download_manifest_m1_portal.tsv; emits a per-source-tag completion
flag at ``{paths.raw_sumstats_v2}/.download_complete.{source_tag}`` so
downstream Wave 2 harmonizer rules gate on the flag rather than on
individual files (harmonize-as-ready policy per D-14).

Path-parameterization (REQ-PATH-PARAMETERIZATION): every disk path is
resolved through ``config["paths"]["raw_sumstats_v2"]``. No
absolute HPC scratch paths appear in this rule file (verified by the
m1-01 path-parameterization grep gate).

Driver: bin/download_sumstats_v2.sh --manifest-stdin (idempotent xargs -P 5
fetch helper, augmented in m1-01-T1 to support the 10-column TSV schema +
DIAMANTE_COOKIE env var + PENDING_* sentinel handling).
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Manifest discovery
#
# The manifest path is resolved relative to the project root (workflow.basedir
# points one directory up from this rules file in the standard Snakemake
# layout: ``workflow/Snakefile`` includes ``src/snakemake/rules/m1_download.smk``).
# We accept either ``workflow.basedir`` (Snakemake context) or fall back to
# the cwd (smoke parsing context outside Snakemake).
# ---------------------------------------------------------------------------

try:
    _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _BASE = Path(os.getcwd())

# Walk up from rules/ directory to find the project root by looking for
# config/pipeline.yaml. This makes the rule robust to whichever Snakefile
# includes it.
def _find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(6):
        if (cur / "config" / "pipeline.yaml").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start

_PROJECT_ROOT = _find_project_root(_BASE)
MANIFEST_PATH = _PROJECT_ROOT / "config" / "download_manifest_m1_portal.tsv"


def _read_source_tags(manifest: Path) -> list[str]:
    """Read source_tag column (column 1) from the manifest TSV, skipping header."""
    if not manifest.is_file():
        return []
    tags: list[str] = []
    with open(manifest, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.rstrip("\r\n")
            if not line:
                continue
            if i == 0:
                # Header
                continue
            tag = line.split("\t", 1)[0]
            if tag:
                tags.append(tag)
    return tags


SOURCE_TAGS = _read_source_tags(MANIFEST_PATH)

# Path-parameterized raw root. ``config`` is the Snakemake configfile dict.
try:
    _RAW_ROOT = config["paths"]["raw_sumstats_v2"]  # type: ignore[name-defined]
except (NameError, KeyError):
    _RAW_ROOT = "data/raw/sumstats_v2"


rule m1_download_portal_row:
    """Fetch a single portal source_tag row via download_sumstats_v2.sh --manifest-stdin.

    Output is a sentinel completion flag (touch file) at
    ``{raw_sumstats_v2}/.download_complete.{source_tag}``. Downstream
    harmonizer rules in Wave 2 (m1-02a / m1-02b) take this flag as input
    so they can fire as each source lands (D-14 harmonize-as-ready).
    """
    output:
        flag=os.path.join(_RAW_ROOT, ".download_complete.{source_tag}"),
    params:
        manifest=str(MANIFEST_PATH),
        tag="{source_tag}",
    conda:
        "../../../envs/m1-download.yml"
    resources:
        mem_mb=2000,
        # Per feedback_lsf_queues: standard queue wall ceiling = 2880 minutes.
        runtime=2880,
    shell:
        r"""
        set -euo pipefail
        grep -P '^{params.tag}\t' {params.manifest} | \
            bash bin/download_sumstats_v2.sh --manifest-stdin
        touch {output.flag}
        """


rule m1_download_all:
    """Aggregate target: depend on every source_tag's completion flag."""
    input:
        flags=expand(
            os.path.join(_RAW_ROOT, ".download_complete.{tag}"),
            tag=SOURCE_TAGS,
        ),
    output:
        sentinel=os.path.join(_RAW_ROOT, ".m1_download_all.complete"),
    shell:
        "touch {output.sentinel}"
