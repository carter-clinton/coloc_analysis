"""Regression gate for quick-260505-1mq M2 derived-consumer refresh.

Pins the load-bearing post-refresh invariants for the four consumer outputs
that were previously stale w.r.t. the real-scalar `_mtag_maxfdr_filtered.txt`
written by quick-260429-w2a. Failure of any case here means a future refresh
of the MTAG-FDR scalars did NOT propagate to its downstream consumers --
exactly the failure mode this gate exists to prevent.

Invariants (all three RED before quick-260505-1mq lands; GREEN after):

1. results/novelty/joint_signal_novel.tsv mtime is newer than every
   _mtag_maxfdr_filtered.txt mtime (consumer was rebuilt after source).

2. data/processed/mtcojo/{stratum}/mtcojo_eligible_targets.delta.tsv exists
   per stratum (delta-sidecar marker captures the eligibility re-evaluation
   even when the diff is empty -- preserved-as-marker per quick-260505-1mq
   PLAN.md Task 4 spec).

3. data/processed/mtcojo/{stratum}/mtcojo_sensitivity.tsv mtime is newer than
   mtcojo_eligible_targets.tsv mtime per stratum (sensitivity table was
   re-aggregated AFTER eligibility refresh).

Tests intentionally use file-freshness rather than content-level joins,
because (a) the consumer outputs are gitignored bytes (multi-GB), (b) the
join semantics in call_class1_novelty.py span MTAG OR CPASSOC branches so a
stroke-only rsid could be retained via the CPASSOC path, and (c) the
freshness invariant directly matches the goal of this quick task: rebuild
each consumer after the source was rewritten.

Plan reference: .planning/quick/260505-1mq-refresh-m2-derived-consumers-after-mtag-/260505-1mq-PLAN.md
"""
from __future__ import annotations

from pathlib import Path

import pytest

_STRATA = ("EUR", "AFR", "TRANS")


def _mtime(path: Path) -> float:
    if not path.exists():
        pytest.fail(f"Required file missing: {path}")
    return path.stat().st_mtime


def test_joint_signal_novel_consumer_freshness(project_root: Path) -> None:
    """results/novelty/joint_signal_novel.tsv must be newer than every
    _mtag_maxfdr_filtered.txt that feeds it.
    """
    consumer = project_root / "results" / "novelty" / "joint_signal_novel.tsv"
    sources = [
        project_root
        / "data"
        / "processed"
        / "mtag"
        / s
        / f"{s}_mtag_maxfdr_filtered.txt"
        for s in _STRATA
    ]
    consumer_mtime = _mtime(consumer)
    for src in sources:
        src_mtime = _mtime(src)
        assert consumer_mtime > src_mtime, (
            f"Consumer {consumer.name} (mtime={consumer_mtime}) is NOT newer "
            f"than source {src} (mtime={src_mtime}). Consumer was not rebuilt "
            f"after MTAG-FDR real-scalar refresh."
        )


def test_mtcojo_eligibility_delta_sidecars_exist(project_root: Path) -> None:
    """Per-stratum mtcojo_eligible_targets.delta.tsv must exist (preserved as
    marker even when delta is empty -- per PLAN.md Task 4 spec).
    """
    for stratum in _STRATA:
        delta = (
            project_root
            / "data"
            / "processed"
            / "mtcojo"
            / stratum
            / "mtcojo_eligible_targets.delta.tsv"
        )
        assert delta.exists(), (
            f"Missing delta sidecar for stratum {stratum}: {delta}. "
            f"Task 4 must emit this file per PLAN.md spec, even when the "
            f"pre-vs-post eligibility lists are byte-identical."
        )


def test_mtcojo_consumers_newer_than_source(project_root: Path) -> None:
    """For each stratum, BOTH mtcojo_eligible_targets.tsv AND
    mtcojo_sensitivity.tsv mtimes must exceed the corresponding
    _mtag_maxfdr_filtered.txt mtime (both downstream consumers rebuilt
    against real-scalar source).
    """
    for stratum in _STRATA:
        source = (
            project_root
            / "data"
            / "processed"
            / "mtag"
            / stratum
            / f"{stratum}_mtag_maxfdr_filtered.txt"
        )
        eligible = (
            project_root
            / "data"
            / "processed"
            / "mtcojo"
            / stratum
            / "mtcojo_eligible_targets.tsv"
        )
        sensitivity = (
            project_root
            / "data"
            / "processed"
            / "mtcojo"
            / stratum
            / "mtcojo_sensitivity.tsv"
        )
        source_mtime = _mtime(source)
        eligible_mtime = _mtime(eligible)
        sensitivity_mtime = _mtime(sensitivity)
        assert eligible_mtime > source_mtime, (
            f"{stratum}: eligible_targets (mtime={eligible_mtime}) is NOT "
            f"newer than source {source.name} (mtime={source_mtime}). "
            f"Task 4 did not refresh eligibility after MTAG-FDR real-scalar "
            f"propagation."
        )
        assert sensitivity_mtime > source_mtime, (
            f"{stratum}: sensitivity (mtime={sensitivity_mtime}) is NOT "
            f"newer than source {source.name} (mtime={source_mtime}). "
            f"Task 5 did not re-aggregate sensitivity after MTAG-FDR "
            f"real-scalar propagation."
        )
