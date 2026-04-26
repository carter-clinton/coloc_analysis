# M2 Wave 2 Task 3 — residcov.txt + trait_order.json fire log

**Generated:** 2026-04-26
**Plan:** m2-02-mtag-3-strata
**Decision:** D-M2-10 corrected (bare-numeric residcov.txt + sidecar JSON)

## Per-stratum residcov slice — all 3 strata clear `_MIN_PER_STRATUM=3` floor (D-M2-Q6)

| Stratum | K  | residcov.txt sha256 (first 16) | trait_order_head                                                                            |
| ------- | -- | ------------------------------ | ------------------------------------------------------------------------------------------- |
| EUR     | 8  | `60f568370a005045...`          | bmi.EUR.GIANT-UKBB.2018, egfr.EUR.CKDGen.2019, hdl.EUR.GLGC.2021                            |
| AFR     | 6  | `1b141a78edb89dea...`          | bmi.AFR.PAGE.2019, hdl.AFR.GLGC.2021, ldl.AFR.GLGC.2021                                     |
| TRANS   | 7  | `3086779043340db2...`          | cad.TRANS.Aragam.2022, egfr.TRANS.CKDGen.2019, hdl.TRANS.GLGC.2021                          |

## Invariants verified

For each stratum:

- `data/processed/mtag/{stratum}/residcov.txt` exists, K×K square, np.loadtxt round-trip OK
- `data/processed/mtag/{stratum}/residcov.trait_order.json` sidecar contains:
  - `trait_order` (list[str], canonical order matching residcov.txt rows/cols)
  - `K` (int, == matrix dim)
  - `stratum` (str)
  - `matrix_path` (str, source M2 LDSC matrix)
  - `inventory_path` (str, source trait_inventory.yaml)
  - `dropped_for_missing_matrix_row` (list[str], empty since all per-stratum keys present in matrix)
  - `_MIN_PER_STRATUM` (int, 3 per D-M2-Q6)
- `data/processed/mtag/{stratum}/skipped_traits.tsv` header-only file
  (no per-trait skips; all keys had a matching matrix row)
- residcov.txt first byte ∈ `{-, 0..9, ., space, tab, newline}` — Pitfall 2 bare-numeric
- Diagonal == 1.0 — LDSC self-pair convention preserved
- Symmetric within machine precision (`R == R.T` to atol 1e-10)
- No NaN in any per-stratum slice (cross-stratum NaN cells in the M2
  26×26 matrix involve `stroke.AFR × {egfr.EUR, hdl.EUR, sbp.EUR, ldl.HIS}`
  + `tc.EUR × tg.TRANS` — all of these mix strata and never appear inside
  a single per-stratum slice)

## EUR slice details (densest stratum)

```
data/processed/mtag/EUR/residcov.trait_order.json
{
  "trait_order": [
    "bmi.EUR.GIANT-UKBB.2018",
    "egfr.EUR.CKDGen.2019",
    "hdl.EUR.GLGC.2021",
    "ldl.EUR.GLGC.2021",
    "sbp.EUR.Evangelou-ICBP-UKBB.2018",
    "stroke.EUR.GIGASTROKE.2022",
    "tc.EUR.GLGC.2021",
    "tg.EUR.GLGC.2021"
  ],
  "K": 8,
  "stratum": "EUR",
  ...
}
```

Note: GLGC EUR within-cohort lipid pair intercepts (HDL/LDL/TC/TG) fall
in [-0.575, +0.402] per Wave 1 SUMMARY — flagged as informative
(Pitfall 8 expectation of ~1.0 does not hold; methodological note in OSF
follow-up). MTAG consumes these verbatim per D-M2-10 universal-correction
policy.

## Hand-off

Task 4 (production MTAG fire) consumes:

- `data/processed/mtag/EUR/residcov.txt` (8×8) + sidecar
- `data/processed/mtag/AFR/residcov.txt` (6×6) + sidecar
- `data/processed/mtag/TRANS/residcov.txt` (7×7) + sidecar
- 26 munged `.sumstats.gz` files at `data/processed/ldsc_overlap/munged/`
  (subset to per-stratum K via sidecar trait_order)
- `tools/mtag/mtag.py` (pinned commit `9e17f3cf`, env `m2-mtag.yml`)

The 3 MTAG fires can run in parallel since they share no DAG dependencies.

## Pitfall checklist

- [x] Pitfall 1 — `--overlap` NOT used; rule uses literal `--residcov_path`
- [x] Pitfall 2 — residcov.txt is bare-numeric (verified via first-byte check)
- [x] Pitfall 7 — sidecar JSON encodes the trait_order alignment contract
