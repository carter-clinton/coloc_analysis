"""extract_aou_self_report.py -- AoU CDR self-reported race sidecar extractor.

Runs INSIDE the AoU Researcher Workbench (BigQuery + WORKSPACE_BUCKET access),
NOT on the local GPFS dev host. Produces the research_id -> self_report sidecar
TSV that ``aou_ld_panel.load_qc_cohort(..., sensitivity=True)`` sources to define
the AFR sensitivity cohort (D-M3-07): genetic-ancestry AFR INTERSECT self-reports
"Black or African American".

WHY THIS EXISTS
---------------
AoU self-reported race lives in the CDR ``person`` table and is reachable only
via BigQuery -- it is NOT shipped as a genomic aux TSV (unlike
``ancestry_preds.tsv`` / ``relatedness_flagged_samples.tsv``). The M3 LD-panel
driver historically referenced a ``self_report`` column the data flow never
provided, so ``sensitivity=True`` silently degraded to the genetic-ancestry-only
predicate (AFR-sens == AFR-primary). This script closes Fault A by extracting the
column the driver now MANDATORILY sources. See
``.planning/debug/m3-W2-afr-sensitivity-selfid-noop.md``.

OUTPUT SCHEMA
-------------
A tab-separated file with exactly two columns and a header::

    research_id<TAB>self_report

* ``research_id`` -- the CDR person_id as a STRING (matches the col key ``s`` /
  ``import_table(key="research_id")`` contract the driver uses for ancestry).
* ``self_report`` -- the person-table self-reported race SOURCE-VALUE CODE
  (``race_source_value`` emitted verbatim), e.g. ``"WhatRaceEthnicity_Black"`` /
  ``"WhatRaceEthnicity_White"``. The driver applies a ``.contains(
  "WhatRaceEthnicity_Black")`` match against the STABLE survey-answer code --
  NOT the human-readable display string, whose concept-name JOIN AoU names
  "Black, African American, or African" and which silently zero-matched
  (confirmed live on C2024Q3R9, 2026-06-08).

STAGING PATH
------------
The controlled-tier ``aux/`` directory under the WGS dataset is READ-ONLY, so the
sidecar is staged in the researcher's OWN ``$WORKSPACE_BUCKET`` and passed to
``load_qc_cohort`` via the ``self_report_table_path=`` override (which wins over
the discover-by-suffix resolver). Default staged path::

    gs://${WORKSPACE_BUCKET}/ld/aux/self_report/self_report.tsv

USAGE (AoU notebook cell or terminal)
-------------------------------------
    python src/python/extract_aou_self_report.py \\
        --out gs://${WORKSPACE_BUCKET}/ld/aux/self_report/self_report.tsv

Then in AOU-1 Cell 4::

    SELF_REPORT_TSV = f"gs://{os.environ['WORKSPACE_BUCKET']}/ld/aux/self_report/self_report.tsv"
    mt_afr_selfid = load_qc_cohort(
        mt_path=os.environ["WGS_ACAF_THRESHOLD_MULTI_HAIL_PATH"],
        ancestry="afr",
        sensitivity=True,
        self_report_table_path=SELF_REPORT_TSV,   # <-- NEW: the MANDATORY sidecar
        force_fresh=True,                          # <-- re-fire fresh (purge first)
    )
"""
from __future__ import annotations

import argparse
import os
import sys


# The person-table self-reported race SOURCE-VALUE CODE the AFR sensitivity
# cohort restricts to. Kept in lockstep with aou_ld_panel.SELF_REPORT_AFR_MATCH
# (the driver applies the .contains() match; this script only emits the raw
# value). We use the stable AoU survey answer CODE, not the human-readable
# display string -- a live C2024Q3R9 `GROUP BY race_source_value` (2026-06-08)
# confirmed the Black answer is coded 'WhatRaceEthnicity_Black' (99,788). The
# display string "Black or African American" is only produced by a fragile
# concept-name JOIN that AoU often names "Black, African American, or African"
# instead -> the old query silently matched ZERO. See
# .planning/debug/m3-W2-afr-sensitivity-selfid-noop.md.
AFR_RACE_SOURCE_VALUE = "WhatRaceEthnicity_Black"


def build_query(cdr_dataset: str) -> str:
    """CDR person-table self-reported race query.

    Emits one row per person: person_id (-> research_id) + the AoU survey answer
    CODE for self-reported race (``race_source_value``), e.g.
    'WhatRaceEthnicity_Black' / 'WhatRaceEthnicity_White'. We emit the raw
    ``race_source_value`` verbatim -- NOT the concept-name JOIN -- because the
    code is release-stable and the driver matches it directly via
    SELF_REPORT_AFR_MATCH. (Earlier we COALESCEd in ``concept.concept_name`` for
    a human-readable string, but that join is fragile: AoU names the Black answer
    concept "Black, African American, or African", which does NOT contain the
    substring the driver matched -> silent zero-match. Confirmed live on
    C2024Q3R9, 2026-06-08.)
    """
    return f"""
        SELECT
          CAST(p.person_id AS STRING) AS research_id,
          p.race_source_value AS self_report
        FROM `{cdr_dataset}.person` AS p
        WHERE p.person_id IS NOT NULL
    """


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--out", required=True,
        help="Output sidecar path. gs:// (staged to WORKSPACE_BUCKET) or local "
             "TSV. Driver consumes this via self_report_table_path=.")
    parser.add_argument(
        "--cdr-dataset", default=None,
        help="BigQuery CDR dataset id (project.dataset). Defaults to "
             "$WORKSPACE_CDR (AoU-bound).")
    parser.add_argument(
        "--project", default=None,
        help="GCP billing project. Defaults to $GOOGLE_PROJECT.")
    args = parser.parse_args(argv)

    cdr = args.cdr_dataset or os.environ.get("WORKSPACE_CDR")
    project = args.project or os.environ.get("GOOGLE_PROJECT")
    if not cdr:
        print("ERROR: --cdr-dataset not given and $WORKSPACE_CDR unset. This "
              "script must run INSIDE the AoU Workbench.", file=sys.stderr)
        return 2
    if not project:
        print("ERROR: --project not given and $GOOGLE_PROJECT unset.",
              file=sys.stderr)
        return 2

    # Lazy imports: these libraries exist on the AoU Workbench, not the GPFS host.
    import pandas as pd  # noqa: F401  (pandas-gbq / read_gbq path)

    query = build_query(cdr)
    print(f"[extract_aou_self_report] querying {cdr}.person via project={project}")
    df = pd.read_gbq(query, project_id=project, dialect="standard")

    # Schema contract: exactly research_id + self_report, research_id as string.
    df = df[["research_id", "self_report"]].copy()
    df["research_id"] = df["research_id"].astype(str)
    n_total = len(df)
    n_afr = int(df["self_report"].fillna("").str.contains(
        AFR_RACE_SOURCE_VALUE, regex=False).sum())
    print(f"[extract_aou_self_report] {n_total} persons; "
          f"{n_afr} self-report contains {AFR_RACE_SOURCE_VALUE!r}")
    if n_afr == 0:
        print("WARNING: zero persons matched the AFR self-report string. The "
              "driver will RAISE on the empty-subset guard. Inspect the person "
              "schema / race source values before staging.", file=sys.stderr)

    # Write the sidecar. gs:// goes through Hail's hadoop_open (available on the
    # Workbench); local paths use plain open. Tab-separated, header, no index.
    out = args.out
    tsv = df.to_csv(sep="\t", index=False)
    if out.startswith("gs://"):
        import hail as hl
        if not hl.utils.java.Env._hc:  # init only if not already initialized
            hl.init(default_reference="GRCh38", quiet=True)
        with hl.hadoop_open(out, "w") as f:
            f.write(tsv)
    else:
        with open(out, "w") as f:
            f.write(tsv)
    print(f"[extract_aou_self_report] wrote sidecar -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
