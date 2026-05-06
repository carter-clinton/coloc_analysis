# ta-r3 Cowork handoff bundle — pointer

**Bundle:** [ta-r3-cowork-handoff-2026-05-06.zip](ta-r3-cowork-handoff-2026-05-06.zip)
**Compressed size:** 2.3 MB
**Uncompressed size:** ~3.0 MB
**File count:** 159 (158 artifacts + 1 MANIFEST.sha256)
**SHA-256:** `2da0882c69a934ae2406cc381c84d127fe4c4875dc2f9391c0a3044e132b8b84`
**Built:** 2026-05-06 (HPC-side; gsd-orchestrated via Claude Opus 4.7)

## What's inside

Top-level layout:

```
ta-r3-cowork-handoff-2026-05-06/
├── README.md                                 (start here)
├── HPC_DELIVERABLE_2026-05-06.md             (primary handoff brief)
├── MANIFEST.sha256                           (integrity check)
├── phase/                                    (planning artifacts; 5 PLAN + 5 SUMMARY + CONTEXT + 2 VERIFICATION + W2/W4 forensics + md5_baseline)
├── compute/                                  (W1 fits + W2 R1 cache + W3 R2 parity + coloc_summary.tsv + tier_assignments.tsv)
├── code/                                     (W1 fitter + bridge utility + W3 driver + aggregator + regions config + regression test)
├── osf/                                      (OSF amendment + deviations log + audit-V2 review doc)
├── logs/                                     (LSF audit trail: W1/W2/W3/W4 dispatch logs + W1 .err/.out × 27 jobs)
└── manuscript/                               (id-vs-ref-LD.md locked at md5 2a57c1a061f0c66988a55d1d6600efdf)
```

Full file inventory in `MANIFEST.sha256` (159 lines).

## Pulling to local

From any host with HPC ssh access:

```bash
scp <user>@<hpc-host>:/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis/.planning/quick/260506-epz-ta-r3-cowork-handoff/ta-r3-cowork-handoff-2026-05-06.zip ./
```

Or pull via the GitHub remote after the push lands:

```bash
git clone https://github.com/carter-clinton/coloc_analysis.git
cd coloc_analysis
ls .planning/quick/260506-epz-ta-r3-cowork-handoff/
```

## Verifying integrity

After unzipping:

```bash
unzip ta-r3-cowork-handoff-2026-05-06.zip
cd ta-r3-cowork-handoff-2026-05-06
sha256sum -c MANIFEST.sha256
```

All 158 entries should report `OK`. Bundle hash itself: `2da0882c69a934ae2406cc381c84d127fe4c4875dc2f9391c0a3044e132b8b84`.

## Honest-framing reminder

Per [.planning/feedback_original_research_framing.md](../../feedback_original_research_framing.md): every artifact in this bundle frames the work as **"audit-driven re-analysis"** — NOT "fix" / "revision" / "cleanup" / "correction" / "salvage" / "pivot". The Track A id-vs-ref-LD manuscript narrative survives unchanged. Manuscript md5 is byte-identical at phase entry and exit (`2a57c1a061f0c66988a55d1d6600efdf`).
