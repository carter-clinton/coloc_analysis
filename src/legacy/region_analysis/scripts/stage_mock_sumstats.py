#!/usr/bin/env python
import argparse
import gzip
import random
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import yaml
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.utils_logging import get_logger
logger = get_logger()


def load_config(config_path: str) -> Dict:
    with open(config_path, "r") as handle:
        return yaml.safe_load(handle)


def trait_ancestry_pairs(cfg: Dict) -> List[Tuple[str, str]]:
    traits = cfg["traits"]
    ancestries = cfg["ancestries"]
    overrides = cfg.get("trait_ancestries") or {}
    pairs = []
    for trait in traits:
        trait_ancs = overrides.get(trait, ancestries)
        for anc in trait_ancs:
            pairs.append((trait, anc))
    return pairs


def random_variant(chrom: int, pos_start: int) -> Dict[str, object]:
    pos = pos_start + random.randint(0, 1_000_000)
    ref = random.choice(["A", "C", "G", "T"])
    alt = random.choice([b for b in ["A", "C", "G", "T"] if b != ref])
    beta = random.uniform(-0.5, 0.5)
    se = abs(random.gauss(0.05, 0.02))
    z = beta / se if se else 0
    eaf = min(max(random.uniform(0.01, 0.99), 0.01), 0.99)
    return {
        "CHR": chrom,
        "POS": pos,
        "REF": ref,
        "ALT": alt,
        "BETA": beta,
        "SE": se,
        "P": min(max(2 * (1 - abs(z) / 8), 1e-12), 1.0),
        "EAF": eaf,
    }


def make_records(variants_per_chrom: int) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for chrom in (1, 2):
        for idx in range(variants_per_chrom):
            records.append(random_variant(chrom, idx * 100_000))
    return records


def write_table(path: Path, records: Iterable[Dict[str, object]]):
    header = ["CHR", "POS", "REF", "ALT", "BETA", "SE", "P", "EAF"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt") as handle:
        handle.write("\t".join(header) + "\n")
        for row in records:
            handle.write(
                "\t".join(str(row[col]) for col in header)
                + "\n"
            )


def main():
    parser = argparse.ArgumentParser(description="Create tiny GWAS summary statistics for testing.")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--output-dir", default="data_raw/sumstats")
    parser.add_argument("--variants-per-chr", type=int, default=5)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    random.seed(args.seed)
    cfg = load_config(args.config)
    pairs = trait_ancestry_pairs(cfg)
    logger.info(f"Creating mock sumstats for {len(pairs)} trait/ancestry combinations")

    created = []
    for trait, ancestry in pairs:
        records = make_records(args.variants_per_chr)
        out_path = Path(args.output_dir) / f"{trait}.{ancestry}.raw.gz"
        write_table(out_path, records)
        created.append(out_path)

    for path in created:
        logger.info(f"Wrote mock file: {path}")
    logger.info("Done.")


if __name__ == "__main__":
    main()
