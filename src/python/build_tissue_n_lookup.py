#!/usr/bin/env python3
"""Build tissue -> N sample size lookup for GTEx v8 eQTL data (Phase 2).

Primary approach: parse eQTL Catalogue dataset_metadata.tsv (if provided).
Fallback: hardcoded dict of GTEx v8 tissue sample sizes from
https://gtexportal.org/home/tissueSummaryPage (49 tissues, range 73-706).

Output: JSON mapping tissue name -> sample size integer.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


# GTEx v8 tissue sample sizes from GTEx Portal (49 tissues with >= 70 samples).
# Source: https://gtexportal.org/home/tissueSummaryPage
# These are the RNA-seq sample counts per tissue used for eQTL calling.
GTEX_V8_TISSUE_N_FALLBACK = {
    "Adipose_Subcutaneous": 581,
    "Adipose_Visceral_Omentum": 469,
    "Adrenal_Gland": 233,
    "Artery_Aorta": 387,
    "Artery_Coronary": 213,
    "Artery_Tibial": 584,
    "Brain_Amygdala": 129,
    "Brain_Anterior_cingulate_cortex_BA24": 147,
    "Brain_Caudate_basal_ganglia": 194,
    "Brain_Cerebellar_Hemisphere": 175,
    "Brain_Cerebellum": 209,
    "Brain_Cortex": 205,
    "Brain_Frontal_Cortex_BA9": 175,
    "Brain_Hippocampus": 165,
    "Brain_Hypothalamus": 170,
    "Brain_Nucleus_accumbens_basal_ganglia": 202,
    "Brain_Putamen_basal_ganglia": 170,
    "Brain_Spinal_cord_cervical_c-1": 126,
    "Brain_Substantia_nigra": 114,
    "Breast_Mammary_Tissue": 396,
    "Cells_Cultured_fibroblasts": 483,
    "Cells_EBV-transformed_lymphocytes": 147,
    "Colon_Sigmoid": 318,
    "Colon_Transverse": 368,
    "Esophagus_Gastroesophageal_Junction": 330,
    "Esophagus_Mucosa": 497,
    "Esophagus_Muscularis": 465,
    "Heart_Atrial_Appendage": 372,
    "Heart_Left_Ventricle": 386,
    "Kidney_Cortex": 73,
    "Liver": 208,
    "Lung": 515,
    "Minor_Salivary_Gland": 144,
    "Muscle_Skeletal": 706,
    "Nerve_Tibial": 532,
    "Ovary": 167,
    "Pancreas": 305,
    "Pituitary": 237,
    "Prostate": 221,
    "Skin_Not_Sun_Exposed_Suprapubic": 517,
    "Skin_Sun_Exposed_Lower_leg": 605,
    "Small_Intestine_Terminal_Ileum": 174,
    "Spleen": 227,
    "Stomach": 324,
    "Testis": 322,
    "Thyroid": 574,
    "Uterus": 129,
    "Vagina": 141,
    "Whole_Blood": 670,
}


def build_tissue_n_lookup(
    metadata_path: Optional[str] = None,
) -> dict:
    """Build tissue -> N lookup dict.

    Parameters
    ----------
    metadata_path : str, optional
        Path to eQTL Catalogue dataset_metadata.tsv. If None, uses fallback.

    Returns
    -------
    dict
        Mapping of tissue_name -> sample_size (int).
    """
    if metadata_path and Path(metadata_path).exists():
        try:
            df = pd.read_csv(metadata_path, sep="\t")
            # eQTL Catalogue metadata has columns like:
            # dataset_id, study_label, tissue_label, sample_size, etc.
            if "tissue_label" in df.columns and "sample_size" in df.columns:
                lookup = {}
                for _, row in df.iterrows():
                    tissue = str(row["tissue_label"])
                    n = int(row["sample_size"])
                    lookup[tissue] = n
                if lookup:
                    logger.info(
                        "Built tissue N lookup from metadata: %d tissues", len(lookup)
                    )
                    return lookup
            logger.warning(
                "Metadata TSV missing required columns, falling back to hardcoded"
            )
        except Exception as e:
            logger.warning("Failed to parse metadata TSV (%s), using fallback", e)

    logger.info("Using hardcoded GTEx v8 tissue N fallback (%d tissues)", len(GTEX_V8_TISSUE_N_FALLBACK))
    return dict(GTEX_V8_TISSUE_N_FALLBACK)


def main():
    parser = argparse.ArgumentParser(
        description="Build tissue -> N sample size lookup JSON"
    )
    parser.add_argument(
        "--metadata",
        default=None,
        help="Path to eQTL Catalogue dataset_metadata.tsv (optional)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON path for tissue N lookup",
    )

    args = parser.parse_args()

    lookup = build_tissue_n_lookup(metadata_path=args.metadata)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(lookup, f, indent=2, sort_keys=True)

    print(f"[build_tissue_n_lookup] wrote {len(lookup)} tissues to {args.output}")


if __name__ == "__main__":
    main()
