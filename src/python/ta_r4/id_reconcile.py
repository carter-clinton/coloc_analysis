"""Completeness by identity (W3f 15.7b, F4 F6): reconcile the observed ids against the expected set, and the
simulation harness's replicate index (simulate_coloc_r4.R stable_index)."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Sequence


@dataclass
class Reconciliation:
    missing: list = field(default_factory=list)
    extra: list = field(default_factory=list)
    duplicated: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.missing or self.extra or self.duplicated)

    def summary(self, n=10) -> str:
        parts = [f"missing={len(self.missing)} extra={len(self.extra)} duplicated={len(self.duplicated)}"]
        for name, ids in (("missing", self.missing), ("extra", self.extra), ("duplicated", self.duplicated)):
            if ids:
                parts.append(f"{name}: " + ", ".join(map(str, ids[:n])) + (" ..." if len(ids) > n else ""))
        return "; ".join(parts)


def _sorted(ids):
    return sorted(ids, key=lambda x: (type(x).__name__, x))


def reconcile(expected: Iterable, observed: Sequence) -> Reconciliation:
    """missing = expected not observed; extra = observed not expected; duplicated = observed more than once.
    The expected ids must be unique."""
    exp = list(expected)
    if len(set(exp)) != len(exp):
        raise ValueError("expected ids are not unique")
    seen = Counter(observed)
    return Reconciliation(missing=_sorted(set(exp) - set(seen)), extra=_sorted(set(seen) - set(exp)),
                          duplicated=_sorted(k for k, c in seen.items() if c > 1))


def stable_index(cfg: dict, region, scenario, gen, rep) -> int:
    """1-based position of (region, scenario, gen_panel, rep) in the sorted cartesian list (simulate_coloc_r4.R:91-97;
    codepoint order equals R's radix order for these ASCII ids)."""
    dims = [sorted(cfg["regions"]), sorted(cfg["scenarios"]), sorted(cfg["gen_panels"])]
    at = []
    for d, x in zip(dims, (region, scenario, gen)):
        if x not in d:
            raise ValueError(f"STABLE_INDEX: unknown ({region}, {scenario}, {gen})")
        at.append(d.index(x))
    reps = int(cfg["reps"])
    if not 1 <= rep <= reps:
        raise ValueError(f"STABLE_INDEX: rep {rep} outside 1..{reps}")
    return (at[0] * len(dims[1]) * len(dims[2]) + at[1] * len(dims[2]) + at[2]) * reps + int(rep)
