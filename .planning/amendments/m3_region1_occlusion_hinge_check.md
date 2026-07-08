> Hinge check, 2026-07-07 (quick-260707-w78). Resolves the exclude-vs-flag panel-policy
> "hinge fact" named in Seth's scientific-review memo (`m3_nan_conditioning_scientific_review.md`).
> Read-only NC-State investigation; no perimeter access, no spend, no code, no loop contact.
> m3-06 stays HELD; `condition_ld_matrix.py` stays FROZEN.

# Region-1 occlusion hinge check — do occluded variants survive into the harmonized AFR sumstats?

## Why this exists

The scientific-review memo resolved the region-1 NaN **mechanism** = overlapping-deletion
occlusion (a deletion's REF interval physically covers a SNP partner's POS → the base is
uncallable on the deletion haplotype → ~100% correlated missingness → **structurally
undefined** pairwise `r`, not `0/0`). That killed `NaN→0`: there is no "true r" to
substitute. It left one **open decision** — how the panel should carry an occluded locus:

- **Exclude** the occluded record, or
- **Flag** the locus (keep the record, mark the entry structurally-undefined, propagate).

Seth's memo named the fact that decides it: *do the occluded variants survive into the
harmonized GWAS sumstats, and under what key?* Three cases:

1. **Absent from sumstats** → plain Exclude is clean/correct (panel made consistent with sumstats).
2. **Present in sumstats** → plain panel-only Exclude creates a panel↔sumstats **asymmetry**
   (sumstats tests a variant the panel dropped) → must Flag, or Exclude from **both** in lockstep.
3. **Representation differs** (panel vs sumstats normalize the indel differently) → a
   join-key problem that normalization must precede.

This memo runs that check on the one region-1 occlusion locus whose positions are in the
committed record (the 3-record tangle).

## Method (reproducible)

- **The join key is `(CHR, POS)`-only.** `src/R/regularization/snp_id_bridge.R:110-121`
  builds the panel↔sumstats lookup on `(CHR, POS)` and keeps the FIRST record on a
  multi-allelic collision. REF/ALT are **not** in the key → what decides exclude-vs-flag
  is purely **whether a sumstats variant sits at the occluded SNP's position**.
- **Build discrepancy.** The AoU panel is GRCh38; the harmonized sumstats
  (`data/processed/sumstats_harmonized/{trait}.{ANC}.tsv.bgz`) are GRCh37.
  `src/scripts/ld_npz_to_rds.R:162-198` does the GRCh38→GRCh37 liftover at `.rds`-conversion
  time. So the occluded GRCh38 positions must be lifted before comparison.
- **Liftover** (m3-r-ld `pyliftover`, chain `data/external/liftover/hg38ToHg19.over.chain.gz`,
  `pos-1` in / `+1` out — identical convention to `ld_npz_to_rds.R`):

  | occlusion tangle (GRCh38 chr1) | → GRCh37 chr1 | role (inferred) |
  |---|---|---|
  | 5922716 | **5982776** | occluding deletion anchor |
  | 5922718 | **5982778** | occluded SNP |
  | 5922724 | **5982784** | occluded SNP #2 |

  (Roles are inferred from position geometry; the occluded-SNP REF/ALT are in the still-blocked
  geometry verdict — see Limitations.)
- **Scan.** `zcat | awk` (CHR/POS columns auto-detected) over every
  `data/processed/sumstats_harmonized/*.AFR*.tsv.bgz` at GRCh37 chr1:5982600-5983000.

## Evidence (verbatim window rows, GRCh37 chr1)

**`asthma.AFR.tsv.bgz`** (`CHR POS REF ALT BETA SE P EAF N SNP_ID …`):
```
1  5982602  GTTTT  G  -0.19139   0.22063  0.3857  0.01578  7793   rs548490067   (insertion, neighbor)
1  5982752  T      C   0.019951  0.031087 0.521   0.2094   32658  rs11120783    (SNP, MAF 0.21, common neighbor)
1  5982778  G      A  -0.033014  0.12225  0.7871  0.01448  24154  rs182965575   <-- OCCLUDED SNP, PRESENT
1  5982951  AG     A   0.11683   0.15162  0.441   0.01404  17952  rs563943267   (deletion, neighbor)
1  5982964  G      A   0.016697  0.027106 0.5379  0.3448   32658  rs10864245    (SNP, MAF 0.34, common neighbor)
```
**`t2d.AFR.tsv.bgz`**: `1 5982778 G A 0.0574 0.0407 0.159 0.0138 118004.813 1:5982778` → **PRESENT** (real β/SE).
**`bmi / hdl / ldl / tc / tg` (GLGC/PAGE)**: all carry `rs182965575` at 5982778 (A/G orientation, EAF ~0.0141).
**`stroke.AFR.tsv.bgz` + `stroke.AFR.GIGASTROKE…`**: 5982778 **absent** (only 5982752 / 5982964).

**Occluded-SNP presence: `rs182965575` @ GRCh37 chr1:5982778 (G/A, MAF ~0.014) is present in 7 of 9 AFR
sumstats files — every trait except stroke.** The occluding deletion anchor (5982776) and the second
occluded SNP (5982784) are **absent** from all AFR sumstats.

## Result → this is Seth's "present" case

The occluding *deletion* is not in the GWAS, but the **occluded SNP is a real, testable variant
present across the majority of AFR traits**, with genuine β/SE — **callable in the GWAS cohorts,
uncallable in the AoU AFR LD reference**. That is exactly the asymmetry case (2).

1. **`NaN→0` is definitively wrong, with concrete harm.** Zeroing would tell SuSiE that
   `rs182965575` has `r = 0` with its common same-locus neighbors `rs11120783` (MAF 0.21) and
   `rs10864245` (MAF 0.34) — a fabricated LD value for a variant whose true LD is *undefined*.
   Credible-set placement would act on the lie.
2. **Plain panel-only Exclude is unsafe** — it orphans `rs182965575` (present in sumstats, gone
   from the panel) → the `(CHR,POS)` join drops it or the fine-mapper errors.
3. **Recommended policy: exclude-in-lockstep across panel AND sumstats, with a provenance manifest
   — not panel-only, not flag.** The variant's LD is genuinely undefined, so it *cannot be validly
   fine-mapped at this locus regardless* → Flag and Exclude **converge on the same fit** (the
   fine-mapper cannot use an undefined LD row either way). Flag pays for that with
   `.npz→.rds→fit` flag-propagation machinery and Seth's "a flag nothing reads is worse than
   useless" risk. Lockstep-exclude is the simpler, honest realization, provided the provenance
   manifest logs exactly what was dropped and why (variant + occluding deletion + span + locus)
   so the removal is auditable — preserving the testable-variant paper-trail without the machinery.

## Implications for the two remaining Carter policy calls

- **Scope → upstream, all 276.** `rs182965575` is a generic dbSNP variant present across many
  GWAS; the occlusion originates in the AoU AFR `.bim` geometry (systemic — region 1 alone has 7
  occluding deletions). The fix belongs at **panel build** (identify occluded records via `.bim`
  REF-span geometry) paired with a **lockstep sumstats-side drop** at the m3-04 harmonization step.
- **Amendment.** The scoped OSF amendment-update should describe **exclusion + provenance**, never
  zeroing.

## Limitations (stated plainly)

- **Partial.** Only the committed 3-record tangle was checked; the **5 direct occlusion pairs live
  in the still-uncommitted `m3_region1_nan_geometry_verdict.md`** (blocked on a base64/fenced
  transfer; anchor SHA-256 `4543dcf4…` / 5012 B). Finding **even one** present occluded variant is
  sufficient to reject the clean "absent" branch and mandate lockstep handling; the full list would
  add cases, not change the policy.
- **Position-only.** Matched on the `(CHR,POS)` join key; allele orientation was not verified (the
  panel's occluded-SNP REF/ALT are in the blocked verdict) — irrelevant to the exclude decision,
  relevant only to effect-sign later.

## Cross-references

- Mechanism + hold: `.planning/amendments/m3_nan_conditioning_scientific_review.md` (`3516c18`).
- Full occluded list (blocked): `m3_region1_nan_geometry_verdict.md` (anchor `4543dcf4…`).
- Posted OSF amendment (NaN→0 premise now refuted): `.planning/amendments/osf-amendment-afr-native-ld-nan-psd-2026-07-03.md`.
- Backlog: ROADMAP `999.1` (LD NaN policy). Join code: `snp_id_bridge.R`, `ld_npz_to_rds.R`,
  `refit_sh2b3_psd_regularized.R:106,137`.
- Open Carter calls: (1) exclude-in-lockstep [this memo's recommendation], (2) upstream all-276,
  (3) pre-registered scoped amendment-update.

## Reproduce

```bash
# 1. liftover (m3-r-ld pyliftover, same chain/convention as ld_npz_to_rds.R)
/rs1/researchers/c/ckclinto/conda_envs/m3-r-ld/bin/python - <<'PY'
from pyliftover import LiftOver
lo = LiftOver('data/external/liftover/hg38ToHg19.over.chain.gz')
for p in (5922716, 5922718, 5922724):
    print(p, '->', lo.convert_coordinate('chr1', p-1)[0][1] + 1)   # 5982776/5982778/5982784
PY
# 2. scan AFR sumstats at the lifted window
for f in data/processed/sumstats_harmonized/*.AFR*.tsv.bgz; do
  echo "### $f"; zcat "$f" | awk 'NR==1{for(i=1;i<=NF;i++)h[$i]=i;
    cc=(h["CHR"]?h["CHR"]:1); pc=(h["POS"]?h["POS"]:(h["BP"]?h["BP"]:2)); next}
    {c=$cc; sub(/^chr/,"",c); if(c=="1"){if($pc>=5982600&&$pc<=5983000)print; if($pc>5983000)exit}
     else if(c+0>1&&c!="X"&&c!="Y")exit}'
done
```
