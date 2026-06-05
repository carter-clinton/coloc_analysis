# Wave 2 — Full-Genome AoU LD Reference Panel: Scope, Audit, Gates & Run Sheet

**Status:** scoped + pre-fire-audited NCSU-side (2026-06-04). NOT yet fired (Carter holds every AoU $ trigger).
**Prepared autonomously after Gate C PASS.** HEAD `c6c32b3` on `origin/m3-W2-aou-deltas`.

---

## 0. Terminology (read first — there is a numbering collision)

Two schemes are in play and they collide on "Wave 2":
- **Phase-plan scheme** (older `m3-02-W2-*` docs): **W2 = the 10-region dev fire**; **W4 = the 322-cell production fire**.
- **Resume-point scheme** (this doc, post-Gate-C): **"Wave 2" = the full-genome production rebuild** (= phase-plan's W4).

This plan uses the resume-point meaning. So **what you are firing is the production (phase-plan W4) genome-wide LD build, and the 10-region dev fire is its mandatory predecessor gate.**

---

## 1. Scope (authoritative)

- **Region set = `config/ld_regions.tsv`** (NOT the 13-row `regions_curated_grch38.csv`, which is the pre-reframe candidate-locus set). 322 rows = **161 unique M2 regions × 2 ancestries** (AFR + EUR), GRCh38-native. Locked by D-M3-02 / D-M3-09. (`region_id_mapping.tsv` is only a human-alias table.)
- **Cohorts in the production loop: AFR-primary (`mt_afr_qc`) + EUR (`mt_eur_qc`) = 322 cells.** The self-ID cohort (`mt_afr_pca_selfid_qc`) is **sensitivity-only** (dev-10 + targeted loci); it escalates to a full genome-wide fire ONLY if dev-10 self-ID-vs-PCA LD r < 0.995 (D-M3-07).
- **Region size profile** (median ~9 Mb, max ~102 Mb — these are NOT 2 Mb windows):
  | region_class | n regions | Path-A route | n cells (×2 anc) |
  |---|---|---|---|
  | small (≤5 Mb) | 45 | A.1 `to_numpy` full `.npz` | 90 |
  | medium (5–25 Mb*) | 80 | A.2 `sparsify`+`to_numpy` lower-tri `.npz` | 160 |
  | large (25–50 Mb) | 28 | A.3 `BlockMatrix.write` `.bm` | 56 |
  | xlarge (>50 Mb) | 8 | A.3 `.bm` | 16 |

  *The manifest labels "medium" up to 25 Mb — see HIGH-1 below; the fixed driver now routes by **span** for OOM safety, so 86 of these cells (>10 Mb) now correctly go to A.3, not A.2.

- **Params:** internal MAF 0.005; **export MAF 0.005** (NOT the spec's 0.01 — Q6, preserves AFR rare-allele signal; Claude's-discretion, overrideable). call_rate≥0.95 / HWE≥1e-6 (variant), call_rate≥0.98 / het±3SD (sample), KING 0.0442. Signed Pearson **r** (not r²) float32. **Per-region radius = span + 500 kb** (capped at 50 Mb — see HIGH-3). GRCh38 compute; GRCh37 liftover is one-shot NCSU-side.
- **Output:** per region — A.1/A.2 → `{region_id}.npz`; A.3 → `bm/{region_id}.bm` + `{region_id}.variant_ids.tsv` + `.rsids.tsv`. Written to `gs://${WORKSPACE_BUCKET}/ld/{AFR_aou,EUR_aou}/`.
- **Egress:** 44 export requests (22 chr × 2 anc) via the AoU Workbench Files UI; each a Carter human action; ~2–5 business-day AoU SLA each → ~3–4 weeks. Audit-logged to `.planning/amendments/aou-egress-audit-log.md`.
- **Wave 3/4 (NCSU-side):** `gsutil cp` → A.3 `.bm` densified by `bm_to_npz.py` → `ld_npz_to_rds.R` (npz→rds + GRCh38→GRCh37) → Snakemake `build_ld_rds_aou_afr` into the fine-mapping DAG.
- **Compute/cost: ≈ 1,117 cluster-hours (AFR+EUR), ~5–7 wall days** at AoU concurrency (D-M3-09). **Dollar cost UNCONFIRMED against AoU credits — must be checked before firing.**

---

## 2. Pre-fire audit (NCSU-side, 2026-06-04) — findings & status

A two-agent audit of the Wave 2 compute path found the following. **The one fire-crashing bug is FIXED; the rest are flagged for your decision.**

### ✅ FIXED — HIGH-1: `to_numpy()` driver-OOM routing (commit `c6c32b3`)
`compute_region_ld` routed by `region_class` first; the manifest classes regions up to 25 Mb as "medium", but Paths A.1/A.2 end in `BlockMatrix.to_numpy()` — an O(n_var²) **driver-side dense collect**. **86 of 322 cells** (largest 23.7 Mb → ~225 GB dense float32) would have OOM'd the driver — including the **dev-10 set's `m2_region_00006` (17.7 Mb)**, i.e. the *first* dev fire would have crashed. Fixed via a pure `_route_region_path()` helper with a hard span veto (any A.1/A.2 with span > 10 Mb → A.3 BlockMatrix write). Verified by 3 pure tests (suite 128 passed). This is the same driver-collect hazard class as the cohort-build bug we fixed at Gate B.

### 🚩 FLAGGED — needs your decision (NOT auto-fixed):

- **HIGH-3 (scientific call): xlarge radius cap → banded LD.** The 16 xlarge cells (span >50 Mb, e.g. `m2_region_00120` 101.7 Mb) have `radius_bp = 50 Mb < span`, so `hl.ld_matrix` structurally zeroes all variant pairs >50 Mb apart. This contradicts the Q2 "radius = span" intent, but is arguably fine (long-range LD ≈ 0 at >50 Mb). **It ships silently** (A.3, no crash). **Decide:** (a) accept the 50 Mb band with a documented SuSiE caveat (recommended — full-radius LD over a 100 Mb region is computationally intractable, ~10¹² entries), (b) subdivide xlarge regions for LD, or (c) exclude them. A guard test pins that only these 16 cells are banded, so any new banded region surfaces. **Recommendation: (a)**, document the caveat; revisit only if a fine-mapped signal lands in an xlarge region.
- **MED-4 (catastrophe-class): A.3 `.bm` write has no populated-validation.** Given the m3-W1 empty-MT catastrophe (`_SUCCESS` on empty contents), a `BlockMatrix.write` that finalizes empty would ship silently. 36 A.3 regions/ancestry exposed. **Recommend fixing before the fire** (add a non-empty assertion after `.bm` write, analogous to `_assert_checkpoint_nonempty`). ~30 min NCSU-side.
- **MED-6 (catastrophe-class): idempotency skips on existence, not validity.** `_existing_region_npz` short-circuits if `{region_id}.npz` exists — a corrupt/truncated `.npz` from a websocket-drop is never re-driven. Same blind spot as the original `_has_checkpoint`. **Recommend fixing** (validate `.npz` is non-trivially-sized / loadable before skip) — cheap, and directly echoes [[feedback_aou_success_marker_not_evidence_of_data]].
- **MED-5: swallowed A.3 sidecar-upload failure** → orphan `.bm` without `variant_ids.tsv` (breaks `bm_to_npz.py` post-egress). Low-cost fix: check `_upload_to_gcs` return value in the A.3 branch.
- **Manifest mismatch (root of HIGH-1):** `build_ld_region_manifest.CLASS_MEDIUM_MAX_MB=25` vs driver `PATH_A2_MAX_MB=10`. The driver fix makes this safe, but reconciling the manifest classes would make the labels honest. Optional.
- **Coverage gap:** no live Path-A.2/A.3 tests (only A.1). The dev-10 fire will exercise A.3 for the first time — watch it. A hail-gated A.2/A.3 fixture test is a good follow-up.

---

## 3. Gate sequence (do these IN ORDER)

### 🔴 GATE 0 — AoU egress classification ruling (HARD GATE, before ANY compute)
The variant×variant LD matrices must be **classified for egress by AoU, in writing**, before any Dataproc spend (spec R1 / Q12 — "the classification ruling is the critical hard-gate row"). **Unverified whether this ruling exists yet.** Confirm it's in hand (or file the request) before firing anything. The §13/§7 framing (each LD entry computed from all n≥60k AFR / n≥130k EUR participants → clears the ≥20-person floor) is the argument, but the *ruling* is the gate.

### 🟠 GATE 1 — Pre-fire readiness (mostly NCSU-side; some need you)
- [x] HIGH-1 OOM routing fix landed + tested (`c6c32b3`).
- [ ] **Decide HIGH-3** (radius/banding) — recommend accept + document.
- [ ] **Decide MED-4 / MED-6** (catastrophe-class) — recommend fix before fire (~1 hr NCSU-side; I can do these on your word).
- [ ] **Cluster preset:** reconcile DESIGN-DELTA's 16× n1-highmem-16 (256 vCPU, ~$19/hr) vs the post-Gate-C 24× n2-standard-16 (384 vCPU). Pick one; non-preemptible; "Software to install = Hail".
- [ ] **CDR pin** confirm (v8, no v8→v9 migration mid-flight).
- [ ] **Cost/credit confirmation:** convert ~1,117 cluster-h to AoU credit-dollars, confirm against your balance + a cap (spec R3). Carter-only.

### 🟡 GATE 2 — dev-10 fire + validation (the rigor gate; cheap; catches remaining bugs)
This is the Wave-2-scheme equivalent of the Gate C smoke for the LD step. **Do NOT skip — rigor over speed.**
- Fire `config/ld_regions_dev.tsv` (10 regions) on AFR (+ EUR if cheap), production AOU-2 notebook, `USE_DEV_SUBSET=True`.
- Run AOU-4 Checks 1–4 → validation memo (self-review + OSF post per spec §9).
- **Q10 halt-check:** if any dev-10 region shows >50% variant drop at MAF 0.005 vs 0.01 → halt at your checkpoint.
- **D-M3-07 trigger:** if dev-10 self-ID-vs-PCA LD r < 0.995 at lead loci → escalate self-ID to a full genome-wide fire.
- Watch the **first A.3 region** live (BlockMatrix write + sidecars) — it's never run before.

### 🟢 GATE 3 — full production 322-cell fire
Only after Gates 0–2 pass. AFR + EUR, all 161 regions, staged (priority batch → remainder), idempotent resume on websocket drop. ~1,117 cluster-h, ~5–7 wall days. Then 44 per-chromosome egress requests.

---

## 4. Run sheet (when Gates 0–1 are clear)

**Cluster:** recreate a Dataproc cluster ("Software to install = Hail"), your chosen preset (256 or 384 vCPU), n2-standard-16/highmem master, non-preemptible.
```bash
# 1. Clone + pull the fixed branch (the OOM fix MUST be present)
cd ~ && git clone https://github.com/carter-clinton/coloc_analysis.git coloc_analysis 2>/dev/null; \
  cd ~/coloc_analysis && git fetch origin && git checkout m3-W2-aou-deltas && git pull origin m3-W2-aou-deltas
git log --oneline -1   # expect c6c32b3 or later (contains the HIGH-1 OOM fix)
# 2. (sanity, NCSU-equivalent) the cohort MTs from Gate C persist in the bucket:
#    gs://$WORKSPACE_BUCKET/ld/{mt_afr_qc.mt, mt_afr_pca_selfid_qc.mt, mt_eur_qc.mt}
```
- Open the **production** `AOU-2_per_region_ld.ipynb` (NOT the chr22-smoke template).
- **GATE 2:** set `USE_DEV_SUBSET = True` (→ `ld_regions_dev.tsv`), Restart Kernel & Run All. Verify: per-region `.npz`/`.bm` written, the first A.3 region's `.bm` + 2 sidecar TSVs present and non-empty, AOU-4 Checks pass, Q10 + D-M3-07 checks evaluated.
- **GATE 3:** set `USE_DEV_SUBSET = False` (→ full 322 cells), fire in staged batches; monitor driver gather time on the large EUR regions (the collectDArray scaling watch-point); use idempotent resume on any websocket drop.
- Egress: per-chromosome export requests via the Files UI; log each to `aou-egress-audit-log.md`.

**PASS gate per fire:** every region returns `status ∈ {ok, skipped_few_variants, skipped_idempotent}` (no exceptions); A.3 `.bm` dirs + sidecars present + non-empty; no driver OOM; cohort MTs untouched.

---

## 5. Open decisions for Carter (consolidated)

1. **[HARD] GATE 0 egress classification ruling** — in hand? If not, file before any spend.
2. **Cost ceiling / credit balance** — confirm ~1,117 cluster-h fits credits + set a cap.
3. **HIGH-3 radius/banding** on the 16 xlarge cells — accept+document (rec) / subdivide / exclude.
4. **MED-4 + MED-6 catastrophe-class fixes** — fix before fire? (rec yes; ~1 hr; say the word and I'll do them.)
5. **Cluster preset** — 256 vs 384 vCPU.
6. **Export MAF** — keep 0.005 (rec, AFR rare-allele signal) or revert to 0.01.
7. **Self-ID escalation** — pre-bless the auto-escalate (<0.995 trigger) or require a manual checkpoint.
8. **CDR pin** — confirm v8 stable.

## 6. Working-tree note (unrelated to Wave 2, but flag)
At session start the working tree had **59 unstaged tracked-file deletions** (config/, envs/, docs/legacy/, data/). I restored the 5 Wave-2-critical config files (`ld_regions*.tsv`, `region_id_mapping.tsv`, `regions_curated_grch38.csv`, `envs/ld_build.yml`). **~54 deletions remain** (m1/m2 envs, pathway configs, legacy docs) — recoverable from HEAD. Decide whether that's an intentional cleanup (commit it) or accidental (`git checkout -- .`). Not Wave-2-blocking.
