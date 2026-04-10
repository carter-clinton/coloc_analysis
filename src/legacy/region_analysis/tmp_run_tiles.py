import csv
import subprocess
from pathlib import Path
plan = list(csv.DictReader(open("results/fine_mapping/ld_build_plan.tsv"), delimiter="\t"))
todo = [row for row in plan if row["ancestry"] == "TRANS" and row["ld_rds_expected"] and not Path(row["ld_rds_expected"]).exists()]
print(f"building {len(todo)} tiles")
for row in todo:
    chrom = row["chr"]
    variant_file = f"data_processed/ld_reference/variants/{row[region_safe]}.tsv"
    cmd = [
        "python3", "scripts/build_ld_rds.py",
        "--vcf", f"data_raw/1kg/vcf/chr{chrom}.vcf.gz",
        "--samples", row["samples_file"],
        "--chrom", chrom,
        "--start", row["start"],
        "--end", row["end"],
        "--region-id", row["region_id"],
        "--ancestry", row["ancestry"],
        "--output", row["ld_rds_expected"],
        "--rscript", "/share/clintonlab/ckclinto/admix_map/.conda/admix_map_r/bin/Rscript",
        "--variant-list", variant_file,
    ]
    print("Running", " ".join(cmd))
    subprocess.run(cmd, check=True)
print("done")
