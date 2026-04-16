#!/usr/bin/env python3
"""Create synthetic bootstrap fixtures for testing compute_tier_a_retention.R.

Fixture design:
  - 1 trait (test_trait) with 5 AFR Tier A loci (locusA..locusE)
  - 5 bootstraps
  - Bootstrap results:
    b1: locusA=Tier_A, locusB=Tier_A, locusC=not, locusD=Tier_A, locusE=not  -> 3/5=0.6
    b2: locusA=Tier_A, locusB=not,    locusC=Tier_A, locusD=Tier_A, locusE=not -> 3/5=0.6
    b3: locusA=Tier_A, locusB=Tier_A, locusC=not, locusD=not, locusE=Tier_A   -> 3/5=0.6
    b4: locusA=not,    locusB=Tier_A, locusC=Tier_A, locusD=Tier_A, locusE=not -> 3/5=0.6
    b5: locusA=Tier_A, locusB=not,    locusC=not, locusD=Tier_A, locusE=Tier_A -> 3/5=0.6
  => All 5 bootstraps have retention=0.6, so mean=0.6, CI=[0.6, 0.6]

  Tier A = PP.H4 >= 0.8 AND at_least_one_qtl_coloc_pph4 >= 0.8

  Sign agreement: all loci have lead_sign_agree=1 (sanity check)

Also creates a synthetic tier_assignments.tsv with 5 AFR Tier A loci for test_trait.
Also creates a "full_eur" directory simulating Phase 2 unmatched concordance at 0.8.
"""
import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# Tier A pattern per bootstrap: which loci are Tier A
# Each bootstrap has exactly 3/5 = 0.6 retention
TIER_A_PATTERN = {
    1: ["locusA", "locusB", "locusD"],
    2: ["locusA", "locusC", "locusD"],
    3: ["locusA", "locusB", "locusE"],
    4: ["locusB", "locusC", "locusD"],
    5: ["locusA", "locusD", "locusE"],
}

ALL_LOCI = ["locusA", "locusB", "locusC", "locusD", "locusE"]
TRAIT = "test_trait"


def write_coloc_summary(path, locus, is_tier_a, sign_agree=1):
    """Write a coloc_summary.tsv matching run_matched_coloc.R output schema."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pph4 = 0.92 if is_tier_a else 0.30
    qtl_pph4 = 0.85 if is_tier_a else 0.20
    with open(path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        # Match the schema from 04-02: signal_id, pph4, pph3, pph2, pph1, pph0,
        # cs_afr_size, cs_eur_size, lead_variant_afr, lead_variant_eur, lead_sign_agree
        w.writerow([
            "signal_id", "pph4", "pph3", "pph2", "pph1", "pph0",
            "cs_afr_size", "cs_eur_size", "lead_variant_afr", "lead_variant_eur",
            "lead_sign_agree"
        ])
        # GWAS signal row
        w.writerow([
            "L1_L1", pph4, 0.03, 0.02, 0.01, 0.02,
            5, 4, f"{locus}_rs1", f"{locus}_rs1", sign_agree
        ])
        # QTL signal row (determines Tier A jointly with GWAS pph4)
        w.writerow([
            "L1_L2", qtl_pph4, 0.05, 0.03, 0.02, 0.05,
            5, 3, f"{locus}_rs2", f"{locus}_rs2", sign_agree
        ])


def write_tier_assignments(path):
    """Write synthetic tier_assignments.tsv with 5 AFR Tier A loci."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["trait", "ancestry", "region_id", "tier", "pph4", "gene"])
        for locus in ALL_LOCI:
            w.writerow([TRAIT, "AFR", locus, "A", 0.92, f"GENE_{locus}"])
        # Add some non-AFR and non-Tier-A rows to test filtering
        w.writerow([TRAIT, "EUR", "locusF", "A", 0.88, "GENE_locusF"])
        w.writerow([TRAIT, "AFR", "locusG", "B", 0.65, "GENE_locusG"])


def write_unmatched_coloc(path, locus, is_tier_a):
    """Write Phase 2 unmatched (full EUR N) coloc summary for D-02d baseline."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pph4 = 0.90 if is_tier_a else 0.25
    qtl_pph4 = 0.88 if is_tier_a else 0.15
    with open(path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow([
            "signal_id", "pph4", "pph3", "pph2", "pph1", "pph0",
            "cs_afr_size", "cs_eur_size", "lead_variant_afr", "lead_variant_eur",
            "lead_sign_agree"
        ])
        w.writerow([
            "L1_L1", pph4, 0.03, 0.02, 0.01, 0.02,
            5, 4, f"{locus}_rs1", f"{locus}_rs1", 1
        ])
        w.writerow([
            "L1_L2", qtl_pph4, 0.05, 0.03, 0.02, 0.05,
            5, 3, f"{locus}_rs2", f"{locus}_rs2", 1
        ])


def main():
    # Create bootstrap coloc summaries
    for b_idx, tier_a_loci in TIER_A_PATTERN.items():
        for locus in ALL_LOCI:
            is_ta = locus in tier_a_loci
            path = os.path.join(
                BASE, "coloc", TRAIT, locus,
                f"bootstrap_{b_idx}", "coloc_summary.tsv"
            )
            write_coloc_summary(path, locus, is_ta)

    # Create tier assignments
    write_tier_assignments(os.path.join(BASE, "tier_assignments.tsv"))

    # Create unmatched (full EUR) coloc for D-02d
    # 4/5 loci are Tier A at full N => unmatched concordance = 0.8
    unmatched_tier_a = ["locusA", "locusB", "locusC", "locusD"]
    for locus in ALL_LOCI:
        is_ta = locus in unmatched_tier_a
        path = os.path.join(
            BASE, "full_eur_coloc", TRAIT, locus, "coloc_summary.tsv"
        )
        write_unmatched_coloc(path, locus, is_ta)

    print(f"Created fixtures in {BASE}")
    print(f"  - {len(TIER_A_PATTERN)} bootstraps x {len(ALL_LOCI)} loci = "
          f"{len(TIER_A_PATTERN) * len(ALL_LOCI)} coloc summaries")
    print(f"  - Tier assignments: {len(ALL_LOCI)} AFR Tier A loci")
    print(f"  - Unmatched coloc: {len(ALL_LOCI)} loci (4 Tier A at full N)")


if __name__ == "__main__":
    main()
