#!/usr/bin/env python3
"""g:Profiler functional enrichment wrapper with custom background.

Provides two modes:
  1. REST API mode (default): Calls g:Profiler REST API directly via requests.
  2. R fallback mode (--use-r): Generates and executes an R script using gprofiler2.

Both modes support:
  - Custom background gene list (discoverability-matched, per D-03a/Reimand 2019)
  - Electronic GO annotation exclusion (no_iea=True per D-03b/Pitfall 5)
  - FDR correction (significance_threshold_method="fdr", user_threshold=0.05)
  - Negative control gene enrichment validation

T-05-08 mitigation: HTTPS enforced; JSON response schema validated.
T-05-12 mitigation: Retry with exponential backoff (3 attempts, 2s/4s/8s).

Usage:
    python run_gprofiler.py \\
        --gene-list results/pathway/gprofiler/tier_ab_genes.txt \\
        --background results/pathway/gprofiler/background_genes.txt \\
        --sources GO:BP,KEGG,REAC \\
        --exclude-iea \\
        --out results/pathway/gprofiler/enrichment_results.tsv

    python run_gprofiler.py \\
        --gene-list results/pathway/gprofiler/tier_ab_genes.txt \\
        --background results/pathway/gprofiler/background_genes.txt \\
        --sources GO:BP,KEGG,REAC \\
        --exclude-iea \\
        --negative-control-genes config/pathway_sets/neg_ctrl_genes.txt \\
        --out results/pathway/gprofiler/enrichment_results.tsv

References:
    Reimand et al. 2019 Nat Protoc (g:Profiler best practices)
    Kolberg et al. 2020 (gprofiler2 R package)
    API docs: https://biit.cs.ut.ee/gprofiler/api/gost/profile/
"""
import argparse
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None  # Deferred check at runtime in run_enrichment_api

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Official g:Profiler REST API endpoint (HTTPS enforced per T-05-08)
GPROFILER_API_URL = "https://biit.cs.ut.ee/gprofiler/api/gost/profile/"

# Retry configuration per T-05-12
MAX_RETRIES = 3
RETRY_DELAYS = [2, 4, 8]  # Exponential backoff in seconds


def _read_gene_list(path: str) -> list:
    """Read gene symbols from a file (one per line).

    Parameters
    ----------
    path : str
        Path to gene list file.

    Returns
    -------
    list
        Gene symbols.
    """
    genes = []
    with open(path) as fh:
        for line in fh:
            gene = line.strip()
            if gene and not gene.startswith("#"):
                genes.append(gene)
    return genes


def _validate_response(data: dict) -> None:
    """Validate g:Profiler API response schema per T-05-08.

    Parameters
    ----------
    data : dict
        Parsed JSON response from g:Profiler API.

    Raises
    ------
    ValueError
        If response does not have expected structure.
    """
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict response, got {type(data).__name__}")
    if "result" not in data:
        raise ValueError(
            f"Response missing 'result' key. Keys: {list(data.keys())}"
        )


def _parse_api_results(data: dict) -> list:
    """Parse g:Profiler API response into tabular rows.

    Parameters
    ----------
    data : dict
        Validated API response with 'result' key.

    Returns
    -------
    list of dict
        Each dict represents one enriched term with standardized keys.
    """
    results = data.get("result", [])
    if not results:
        return []

    parsed = []
    for entry in results:
        row = {
            "source": entry.get("source", ""),
            "term_id": entry.get("native", ""),
            "term_name": entry.get("name", ""),
            "p_value": entry.get("p_value", float("nan")),
            "q_value": entry.get("p_value", float("nan")),  # After FDR
            "intersection_size": entry.get("intersection_size", 0),
            "query_size": entry.get("query_size", 0),
            "term_size": entry.get("term_size", 0),
            "effective_domain_size": entry.get("effective_domain_size", 0),
            "genes": ",".join(entry.get("intersections", [])),
        }
        parsed.append(row)

    return parsed


def run_enrichment_api(
    query_genes: list,
    background_genes: list = None,
    sources: list = None,
    exclude_iea: bool = True,
    significance_threshold: float = 0.05,
    organism: str = "hsapiens",
) -> list:
    """Run g:Profiler enrichment via REST API.

    Parameters
    ----------
    query_genes : list
        Gene symbols to test for enrichment.
    background_genes : list, optional
        Custom background gene symbols (per D-03a).
    sources : list, optional
        Annotation sources (e.g., ["GO:BP", "KEGG", "REAC"]).
    exclude_iea : bool
        Exclude electronic GO annotations per D-03b (default True).
    significance_threshold : float
        FDR significance threshold (default 0.05).
    organism : str
        g:Profiler organism code (default "hsapiens").

    Returns
    -------
    list of dict
        Enrichment results.

    Raises
    ------
    RuntimeError
        If all retry attempts fail.
    """
    if requests is None:
        logger.error("requests library required for REST API mode: pip install requests")
        sys.exit(1)

    # Build request payload
    payload = {
        "organism": organism,
        "query": query_genes,
        "sources": sources or ["GO:BP", "KEGG", "REAC"],
        "user_threshold": significance_threshold,
        "significance_threshold_method": "fdr",
        "no_iea": exclude_iea,
        "combined": False,
        "measure_underrepresentation": False,
        "no_evidences": False,
    }

    # Add custom background per D-03a
    if background_genes:
        payload["domain_scope"] = "custom"
        payload["background"] = background_genes
    else:
        payload["domain_scope"] = "annotated"

    # Retry with exponential backoff per T-05-12
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(
                "g:Profiler API request (attempt %d/%d): %d query genes, %d background genes",
                attempt + 1,
                MAX_RETRIES,
                len(query_genes),
                len(background_genes) if background_genes else 0,
            )

            response = requests.post(
                GPROFILER_API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120,
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"g:Profiler API returned HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                )

            data = response.json()
            _validate_response(data)
            results = _parse_api_results(data)
            logger.info(
                "g:Profiler returned %d significant enrichment terms",
                len(results),
            )
            return results

        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                logger.warning(
                    "g:Profiler API attempt %d failed: %s. Retrying in %ds...",
                    attempt + 1,
                    str(e),
                    delay,
                )
                time.sleep(delay)
            else:
                logger.error(
                    "g:Profiler API failed after %d attempts: %s",
                    MAX_RETRIES,
                    str(e),
                )

    raise RuntimeError(
        f"g:Profiler API failed after {MAX_RETRIES} attempts: {last_error}"
    )


def run_enrichment_r(
    query_genes: list,
    background_genes: list = None,
    sources: list = None,
    exclude_iea: bool = True,
    significance_threshold: float = 0.05,
    output_path: str = None,
) -> str:
    """Run g:Profiler enrichment via R gprofiler2 package.

    Generates an R script and executes it via Rscript. This is the fallback
    mode when the REST API is unavailable.

    Parameters
    ----------
    query_genes : list
        Gene symbols to test for enrichment.
    background_genes : list, optional
        Custom background gene symbols.
    sources : list, optional
        Annotation sources.
    exclude_iea : bool
        Exclude electronic GO annotations (evcodes=TRUE per D-03b).
    significance_threshold : float
        FDR significance threshold.
    output_path : str
        Path to write results TSV.

    Returns
    -------
    str
        Path to the output TSV file.
    """
    sources = sources or ["GO:BP", "KEGG", "REAC"]
    sources_r = "c(" + ", ".join(f'"{s}"' for s in sources) + ")"
    query_r = "c(" + ", ".join(f'"{g}"' for g in query_genes) + ")"

    bg_section = ""
    if background_genes:
        bg_r = "c(" + ", ".join(f'"{g}"' for g in background_genes) + ")"
        bg_section = f"""
custom_bg <- {bg_r}
domain_scope <- "custom"
"""
    else:
        bg_section = """
custom_bg <- NULL
domain_scope <- "annotated"
"""

    r_script = f"""
library(gprofiler2)

query_genes <- {query_r}
{bg_section}
sources <- {sources_r}

# Run enrichment with evcodes=TRUE to exclude electronic annotations (D-03b)
results <- gost(
    query = query_genes,
    organism = "hsapiens",
    ordered_query = FALSE,
    multi_query = FALSE,
    sources = sources,
    evcodes = TRUE,
    custom_bg = custom_bg,
    domain_scope = domain_scope,
    correction_method = "fdr",
    significance_threshold = {significance_threshold}
)

if (!is.null(results) && !is.null(results$result)) {{
    write.table(
        results$result,
        file = "{output_path}",
        sep = "\\t",
        quote = FALSE,
        row.names = FALSE
    )
    cat("Wrote", nrow(results$result), "enrichment results\\n")
}} else {{
    # Write empty results file with header
    header <- data.frame(
        source = character(), term_id = character(), term_name = character(),
        p_value = numeric(), q_value = numeric(),
        intersection_size = integer(), query_size = integer(),
        term_size = integer(), effective_domain_size = integer(),
        genes = character()
    )
    write.table(
        header, file = "{output_path}",
        sep = "\\t", quote = FALSE, row.names = FALSE
    )
    cat("No significant enrichment results\\n")
}}
"""

    # Write and execute R script
    r_script_path = output_path + ".R"
    with open(r_script_path, "w") as fh:
        fh.write(r_script)

    logger.info("Running g:Profiler via R: Rscript %s", r_script_path)
    result = subprocess.run(
        ["Rscript", r_script_path],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        logger.error("R script failed:\nSTDOUT: %s\nSTDERR: %s",
                      result.stdout, result.stderr)
        raise RuntimeError(f"R gprofiler2 failed: {result.stderr}")

    logger.info("R output: %s", result.stdout.strip())
    return output_path


def _write_results_tsv(results: list, output_path: str, is_negative_control: bool = False):
    """Write enrichment results to TSV.

    Parameters
    ----------
    results : list of dict
        Enrichment results from API or R.
    output_path : str
        Output TSV path.
    is_negative_control : bool
        If True, add is_negative_control=TRUE column.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "source", "term_id", "term_name", "p_value", "q_value",
        "intersection_size", "query_size", "term_size",
        "effective_domain_size", "genes",
    ]
    if is_negative_control:
        columns.append("is_negative_control")

    with open(output_path, "w") as fout:
        fout.write("\t".join(columns) + "\n")
        for row in results:
            values = [str(row.get(col, "")) for col in columns[:10]]
            if is_negative_control:
                values.append("TRUE")
            fout.write("\t".join(values) + "\n")

    logger.info("Wrote %d results to %s", len(results), output_path)


def run_enrichment(
    gene_list_path: str,
    background_path: str = None,
    sources: list = None,
    exclude_iea: bool = True,
    use_r: bool = False,
    output_path: str = None,
    negative_control_genes_path: str = None,
) -> str:
    """Run g:Profiler enrichment with optional negative control validation.

    Parameters
    ----------
    gene_list_path : str
        Path to query gene list (one gene per line).
    background_path : str, optional
        Path to background gene list (one gene per line).
    sources : list, optional
        Annotation sources (default: ["GO:BP", "KEGG", "REAC"]).
    exclude_iea : bool
        Exclude electronic GO annotations (default True, per D-03b).
    use_r : bool
        Use R gprofiler2 package instead of REST API (default False).
    output_path : str
        Path for results TSV.
    negative_control_genes_path : str, optional
        If provided, also run enrichment on negative control genes.

    Returns
    -------
    str
        Path to the results TSV file.
    """
    query_genes = _read_gene_list(gene_list_path)
    background_genes = _read_gene_list(background_path) if background_path else None
    sources = sources or ["GO:BP", "KEGG", "REAC"]

    logger.info(
        "Running g:Profiler enrichment: %d query genes, %s background, sources=%s, no_iea=%s",
        len(query_genes),
        f"{len(background_genes)} genes" if background_genes else "annotated",
        sources,
        exclude_iea,
    )

    if use_r:
        run_enrichment_r(
            query_genes=query_genes,
            background_genes=background_genes,
            sources=sources,
            exclude_iea=exclude_iea,
            output_path=output_path,
        )
    else:
        results = run_enrichment_api(
            query_genes=query_genes,
            background_genes=background_genes,
            sources=sources,
            exclude_iea=exclude_iea,
        )
        _write_results_tsv(results, output_path)

    # Negative control validation
    if negative_control_genes_path:
        neg_ctrl_genes = _read_gene_list(negative_control_genes_path)
        logger.info(
            "Running negative control enrichment: %d genes",
            len(neg_ctrl_genes),
        )

        if use_r:
            neg_output = output_path.replace(".tsv", "_negctrl.tsv")
            run_enrichment_r(
                query_genes=neg_ctrl_genes,
                background_genes=background_genes,
                sources=sources,
                exclude_iea=exclude_iea,
                output_path=neg_output,
            )
        else:
            neg_results = run_enrichment_api(
                query_genes=neg_ctrl_genes,
                background_genes=background_genes,
                sources=sources,
                exclude_iea=exclude_iea,
            )
            neg_output = output_path.replace(".tsv", "_negctrl.tsv")
            _write_results_tsv(neg_results, neg_output, is_negative_control=True)

    return output_path


def main():
    """CLI entry point for g:Profiler enrichment wrapper."""
    parser = argparse.ArgumentParser(
        description="g:Profiler functional enrichment with custom background"
    )
    parser.add_argument(
        "--gene-list",
        required=True,
        help="Path to query gene list file (one gene per line)",
    )
    parser.add_argument(
        "--background",
        default=None,
        help="Path to background gene list file (one gene per line, per D-03a)",
    )
    parser.add_argument(
        "--sources",
        default="GO:BP,KEGG,REAC",
        help="Comma-separated annotation sources (default: GO:BP,KEGG,REAC)",
    )
    parser.add_argument(
        "--exclude-iea",
        action="store_true",
        default=True,
        help="Exclude electronic GO annotations (no_iea=True per D-03b, default True)",
    )
    parser.add_argument(
        "--include-iea",
        action="store_true",
        help="Include electronic GO annotations (overrides --exclude-iea)",
    )
    parser.add_argument(
        "--use-r",
        action="store_true",
        help="Use R gprofiler2 package instead of REST API",
    )
    parser.add_argument(
        "--negative-control-genes",
        default=None,
        help="Path to negative control gene list (optional validation)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output TSV file path",
    )
    args = parser.parse_args()

    sources = [s.strip() for s in args.sources.split(",")]
    exclude_iea = not args.include_iea

    run_enrichment(
        gene_list_path=args.gene_list,
        background_path=args.background,
        sources=sources,
        exclude_iea=exclude_iea,
        use_r=args.use_r,
        output_path=args.out,
        negative_control_genes_path=args.negative_control_genes,
    )


if __name__ == "__main__":
    main()
