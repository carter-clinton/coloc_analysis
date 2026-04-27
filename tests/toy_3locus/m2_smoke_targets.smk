"""REQ-SNAKEMAKE-CI extension — M2 smoke targets.

Adds at least one M2 rule (residcov_slice on synthetic 3x3 matrix) to the
existing toy 3-locus pipeline so REQ-SNAKEMAKE-CI is preserved end-to-end.
Smoke must finish < 15 minutes per REQ-SNAKEMAKE-CI acceptance.

Plan: m2-05-class1-novelty-and-closeout-PLAN.md (Wave 5 Task 2).
"""
import os

# Resolve paths relative to project root (tests/toy_3locus/Snakefile.test runs
# from the repo root; this rule is included from Snakefile.test).
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(workflow.basedir), ".."))
_SMOKE_OUT_DIR = os.path.join(_PROJECT_ROOT, "tests/toy_3locus/m2_smoke_out")


rule m2_smoke_residcov_slice:
    """Smoke test of build_mtag_residcov_slice.slice_for_stratum on a synthetic 3x3 matrix.

    Uses the in-memory pure-function form (slice_for_stratum) of the M2
    Wave 2 helper to exercise the bare-numeric residcov + sidecar trait_order
    contract end-to-end without needing the full M2 inventory or matrix.

    Acceptance:
      - residcov.txt exists, parses via np.loadtxt to a 3x3 matrix
      - residcov.trait_order.json exists with trait_order key + 3-trait list
      - Total wall < 1 minute (synthetic data)
    """
    output:
        residcov=os.path.join(_SMOKE_OUT_DIR, "EUR/residcov.txt"),
        sidecar=os.path.join(_SMOKE_OUT_DIR, "EUR/residcov.trait_order.json"),
    params:
        out_dir=os.path.join(_SMOKE_OUT_DIR, "EUR"),
        project_root=_PROJECT_ROOT,
    shell:
        r"""
        set -euo pipefail
        mkdir -p {params.out_dir}
        # Use the project-wide python (smoke_dev or magma_helpers); the M2
        # build_mtag_residcov_slice helper has only numpy + pandas deps.
        cd {params.project_root}
        python -c "
import sys, os, json
sys.path.insert(0, 'src/python')
from pathlib import Path
import numpy as np
from build_mtag_residcov_slice import slice_for_stratum

# Synthetic 3-trait LDSC matrix (PSD by construction)
keys = ['toy_a.EUR.SYN.2020', 'toy_b.EUR.SYN.2020', 'toy_c.EUR.SYN.2020']
M = np.array([[1.0, 0.1, 0.2], [0.1, 1.0, 0.15], [0.2, 0.15, 1.0]])

out_dir = Path('{params.out_dir}')
out_dir.mkdir(parents=True, exist_ok=True)

sliced, trait_order = slice_for_stratum(
    matrix=M,
    full_keys=keys,
    stratum_keys=keys,
    out_dir=out_dir,
)
assert sliced.shape == (3, 3), f'expected (3,3) got {{sliced.shape}}'
assert trait_order == keys, f'trait_order mismatch: {{trait_order}} vs {{keys}}'

# Round-trip via np.loadtxt to confirm bare-numeric Pitfall 2 invariant
loaded = np.loadtxt(out_dir / 'residcov.txt')
assert loaded.shape == (3, 3), f'round-trip shape mismatch: {{loaded.shape}}'
assert np.allclose(loaded, M), 'round-trip values do not match'

# Sidecar JSON contract
sidecar = json.loads((out_dir / 'residcov.trait_order.json').read_text())
assert sidecar['trait_order'] == keys, f'sidecar trait_order mismatch'
assert sidecar['K'] == 3, f'sidecar K mismatch: {{sidecar[\"K\"]}}'
print('m2_smoke_residcov_slice: PASS (3x3 synthetic round-trip + sidecar)')
"
        test -s {output.residcov}
        test -s {output.sidecar}
        """
