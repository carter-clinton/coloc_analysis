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

### ✅ RESOLVED — fixed/decided NCSU-side (Carter greenlight, commit `c11949e`):

- **HIGH-3 (scientific call): xlarge radius cap → banded LD — ACCEPTED + DOCUMENTED.** The 16 xlarge cells (span >50 Mb, e.g. `m2_region_00120` 101.7 Mb) have `radius_bp = 50 Mb < span`, so `hl.ld_matrix` zeroes variant pairs >50 Mb apart. **Accepted** (full-radius LD over a 100 Mb region is intractable, ~10¹² entries, and long-range LD ≈ 0 at >50 Mb). Documented at the `ld_matrix` call + here; **downstream (SuSiE-RSS / `ld_npz_to_rds.R`) must treat xlarge-region LD as 50-Mb-banded.** Guard test pins that only those 16 cells are banded, so any new banded region in a regenerated manifest surfaces. Revisit only if a fine-mapped signal lands in an xlarge region.
- **MED-4 (catastrophe-class): A.3 `.bm` populated-validation — FIXED.** New `_assert_blockmatrix_written` re-reads the `.bm` metadata and asserts `shape == (n_var, n_var)`; raises on empty/corrupt. Called in both A.3 branches. Closes the m3-W1-class "_SUCCESS on empty contents" hole for Path A.3. Hail-gated A.3 coverage test added.
- **MED-6 (catastrophe-class): idempotency validity — FIXED.** `_existing_region_npz` now requires `size >= _MIN_REGION_NPZ_BYTES` (256 B) before short-circuiting — a 0-byte/truncated `.npz` from a websocket-drop is no longer treated as "done". Pure regression test added.
- **MED-5: swallowed A.3 sidecar-upload failure — FIXED.** The A.3 GCS branch now raises if `_upload_to_gcs` returns None, instead of shipping an orphan `.bm` that `bm_to_npz.py` can't ingest.
- **Coverage gap — ADDRESSED.** Added Hail-gated Path-A.2 (sparsify lower-tri) + A.3 (`.bm` + sidecars + MED-4 guard) smoke tests — first coverage of those paths; they run on the dev fire.
- **Manifest mismatch (root of HIGH-1):** `build_ld_region_manifest.CLASS_MEDIUM_MAX_MB=25` vs driver `PATH_A2_MAX_MB=10`. LEFT as-is — the HIGH-1 span-veto makes it safe and `region_class` is now advisory; regenerating the manifest just to relabel isn't worth it. (Noted only.)

---

## 3. Gate sequence (do these IN ORDER)

### 🔴 GATE 0 — AoU egress classification ruling (HARD GATE, before ANY compute)
The variant×variant LD matrices must be **classified for egress by AoU, in writing**, before any Dataproc spend (spec R1 / Q12 — "the classification ruling is the critical hard-gate row"). **Unverified whether this ruling exists yet.** Confirm it's in hand (or file the request) before firing anything. The §13/§7 framing (each LD entry computed from all n≥60k AFR / n≥130k EUR participants → clears the ≥20-person floor) is the argument, but the *ruling* is the gate.

### 🟠 GATE 1 — Pre-fire readiness (mostly NCSU-side; some need you)
- [x] HIGH-1 OOM routing fix landed + tested (`c6c32b3`).
- [x] **HIGH-3 decided** — accepted + documented (`c11949e`).
- [x] **MED-4 / MED-5 / MED-6 fixed** + tested (`c11949e`); A.2/A.3 coverage tests added.
- [ ] **Cluster preset:** reconcile DESIGN-DELTA's 16× n1-highmem-16 (256 vCPU, ~$19/hr) vs the post-Gate-C 24× n2-standard-16 (384 vCPU). Pick one; non-preemptible; "Software to install = Hail". *(Carter)*
- [ ] **CDR pin** confirm (v8, no v8→v9 migration mid-flight). *(Carter)*
- [ ] **Cost/credit confirmation:** convert ~1,117 cluster-h to AoU credit-dollars, confirm against your balance + a cap (spec R3). *(Carter only)*

**All NCSU-side pre-fire code work is DONE.** GATE 1 now needs only the three Carter-only items above. Remaining gates are operational (egress ruling, dev-10 fire, production).

### 🟣 GATE 1.5 — GENOME-WIDE COHORT REBUILD (prerequisite for ALL LD compute)
**The cohort MTs in the bucket are chr22-ONLY** — Gate C's smoke run overwrote the production
`mt_{ancestry}_qc.mt` paths with chr22-only data (the final checkpoint isn't interval-isolated).
AOU-2 reads those MTs directly, and the dev-10 / production regions span all autosomes — so
**LD compute cannot run until the cohorts are rebuilt genome-wide.** Run the **production**
`AOU-1_template.ipynb` (it calls `load_qc_cohort` with NO `interval_filter` → genome-wide; do
NOT use the chr22-smoke template). This is the first full-scale run of the now-fixed pipeline
(the m3-W1 catastrophe was the *failed* genome-wide attempt; Gate C proved the fixes correct on
chr22). Builds genome-wide `mt_afr_qc` + `mt_afr_pca_selfid_qc` + `mt_eur_qc` (overwrites the
chr22 versions; intermediates are interval-suffixed so no collision). **Watch the EUR Phase-3
`aggregate_cols`/`collectDArray` gather** (221K samples × genome-wide partitions — the scaling
watch-point). PASS = 3 MTs with genome-wide variant counts (millions, not 283K) + non-zero
samples + du-floor real GB + `_assert_checkpoint_nonempty` silent. This is internal (no egress),
so it's gated on GATE 1 (cluster/cost/CDR) but NOT on GATE 0.

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
- **GATE 1.5 (FIRST):** open the **production** `AOU-1_template.ipynb` (genome-wide; NOT the chr22-smoke template), Restart Kernel & Run All → genome-wide `mt_afr_qc` / `mt_afr_pca_selfid_qc` / `mt_eur_qc`. Confirm genome-wide variant counts (millions) before proceeding. THEN:
- Open the **production** `AOU-2_per_region_ld.ipynb` (NOT the chr22-smoke template).
- **GATE 2:** set `USE_DEV_SUBSET = True` (→ `ld_regions_dev.tsv`), Restart Kernel & Run All. Verify: per-region `.npz`/`.bm` written, the first A.3 region's `.bm` + 2 sidecar TSVs present and non-empty, AOU-4 Checks pass, Q10 + D-M3-07 checks evaluated.
- **GATE 3:** set `USE_DEV_SUBSET = False` (→ full 322 cells), fire in staged batches; monitor driver gather time on the large EUR regions (the collectDArray scaling watch-point); use idempotent resume on any websocket drop.
- Egress: per-chromosome export requests via the Files UI; log each to `aou-egress-audit-log.md`.

**PASS gate per fire:** every region returns `status ∈ {ok, skipped_few_variants, skipped_idempotent}` (no exceptions); A.3 `.bm` dirs + sidecars present + non-empty; no driver OOM; cohort MTs untouched.

---

## 5. Open decisions for Carter (consolidated)

Resolved (Carter greenlight 2026-06-04, fixes in `c11949e`): HIGH-3 (accept+document), MED-4/5/6 (fixed). Still open:

1. **[HARD] GATE 0 egress classification ruling** — in hand? If not, file before any spend.
2. **Cost ceiling / credit balance** — confirm ~1,117 cluster-h fits credits + set a cap.
3. **Cluster preset** — 256 vs 384 vCPU.
4. **Export MAF** — keep 0.005 (rec, AFR rare-allele signal) or revert to 0.01.
5. **Self-ID escalation** — pre-bless the auto-escalate (<0.995 trigger) or require a manual checkpoint.
6. **CDR pin** — confirm v8 stable.

## 6. Working-tree note (unrelated to Wave 2, but flag)
At session start the working tree had **59 unstaged tracked-file deletions** (config/, envs/, docs/legacy/, data/). I restored the 5 Wave-2-critical config files (`ld_regions*.tsv`, `region_id_mapping.tsv`, `regions_curated_grch38.csv`, `envs/ld_build.yml`). **~54 deletions remain** (m1/m2 envs, pathway configs, legacy docs) — recoverable from HEAD. Decide whether that's an intentional cleanup (commit it) or accidental (`git checkout -- .`). Not Wave-2-blocking.
