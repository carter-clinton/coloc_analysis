# results/

**Not tracked in git** — everything under this directory is regeneratable
Snakemake output and is `.gitignore`d.

## Expected layout (post-Phase-0)

```
results/
├── phase_00_infra/          # harmonized sumstats, QC reports
├── phase_01_finemap/        # SuSiE-RSS credible sets per trait × ancestry
├── phase_02_coloc/          # coloc.susie pairwise + 3-way QTL colocs
│   ├── gtex_v8/             # eQTL/sQTL coloc
│   ├── ukb_ppp/             # pQTL coloc (DUA-gated)
│   ├── decode/              # pQTL coloc (DUA-gated)
│   └── onek1k/              # single-cell eQTL coloc
├── phase_05_pathway/        # MAGMA, g:Profiler, LDSC partitioned h2, HESS
├── phase_09_replication/    # FinnGen / GBMI / MVP / AoU / BBJ replication
├── phase_03_mr/             # T2: bidirectional MR (IVW/Egger/WM/PRESSO/CAUSE)
├── phase_04_matched_n/      # T2: matched-N cross-ancestry concordance
├── phase_08_prs/            # T2: PRS-CSx discrimination + calibration + DCA
└── tier_reports/            # T1_review.md, T2_review.md decision checkpoints
```

Legacy results from the prior analysis remain at
`/rs1/researchers/c/ckclinto/coloc_analysis/{region_analysis,genome_wide}/results/`
and are symlinked as `results/legacy/` (see Plan A step A0).
