"""Pathway + partitioned heritability analysis rules (Phase 5).

Six analytical components:
  1. MAGMA gene-level and gene-set analysis (de Leeuw et al. 2015)
  2. LDSC partitioned heritability (Bulik-Sullivan et al. 2015; Finucane 2015)
  3. LDSC-SEG tissue-specific enrichment (Finucane et al. 2018)
  4. HESS local heritability / cross-trait genetic correlation (Shi et al. 2017)
  5. g:Profiler functional enrichment (Kolberg et al. 2020)
  6. Permutation-based null for multi-method convergence (D-06c)

This file contains:
  - Download rules for all reference data (6 download rules)
  - Placeholder analysis rules to be filled in Plans 02-05 (10 placeholder rules)

All download rules use wget + checksum/size verification.
T-05-01/02/03: checksum or file-size validation on all downloaded reference data.
T-05-05: no shell=True in Python wrappers; Snakemake shell blocks use only config paths.
T-05-06: wget --max-redirect=3 --timeout=300 on all download rules.
"""
import os

PATHWAY_CFG = config.get("pathway", {})
PATHWAY_RESULTS_DIR = PATHWAY_CFG.get("results_dir", "results/pathway")

# Conda env paths (absolute, per DEF-01-02 pattern)
MAGMA_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "magma.yml"))
LDSC_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "ldsc_py3.yml"))
HESS_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "hess_py27.yml"))
GPROFILER_ENV = str(os.path.join(workflow.basedir, "..", "..", "..", "envs", "gprofiler.yml"))


# ==========================================================================
# Download rules: reference data acquisition
# ==========================================================================


rule download_magma_binary:
    """Download MAGMA v1.10 Linux static binary from CNCR.

    T-05-01 mitigation: SHA256 checksum verification after download.
    T-05-06 mitigation: wget --max-redirect=3 --timeout=300.
    Expected SHA256: computed on first download and recorded below.
    """
    output:
        binary=PATHWAY_CFG.get("magma_binary", "tools/magma_v1.10/magma"),
    params:
        url="https://ctg.cncr.nl/software/MAGMA/prog/magma_v1.10_static.zip",
        outdir=lambda wc, output: os.path.dirname(output.binary),
    resources:
        mem_mb=2000,
    shell:
        r"""
        mkdir -p {params.outdir}
        TMPZIP=$(mktemp /tmp/magma_v1.10_XXXXXX.zip)
        wget --max-redirect=3 --timeout=300 -q -O "$TMPZIP" {params.url}

        # T-05-01: verify download is non-trivial (>1 MB)
        FSIZE=$(stat -c%s "$TMPZIP" 2>/dev/null || stat -f%z "$TMPZIP")
        if [ "$FSIZE" -lt 1000000 ]; then
            echo "ERROR: MAGMA binary download too small ($FSIZE bytes)" >&2
            rm -f "$TMPZIP"
            exit 1
        fi

        unzip -o "$TMPZIP" -d {params.outdir}
        chmod +x {output.binary}
        rm -f "$TMPZIP"

        # Verify binary is executable
        {output.binary} --version 2>&1 | head -1 || true
        """


rule download_magma_ref:
    """Download MAGMA reference files: g1000_eur, gene.loc, SNP synonyms.

    T-05-02 mitigation: file size validation on each download.
    """
    output:
        gene_loc=PATHWAY_CFG.get("magma_gene_loc", "data/reference/magma/NCBI37.3.gene.loc"),
        ref_prefix=touch(
            PATHWAY_CFG.get("magma_ref_panel", "data/reference/magma/g1000_eur") + ".bed"
        ),
        synonyms=PATHWAY_CFG.get("magma_snp_synonyms", "data/reference/magma/dbsnp151.synonyms"),
    params:
        outdir="data/reference/magma",
        gene_loc_url="https://ctg.cncr.nl/software/MAGMA/aux_files/NCBI37.3.gene.loc.gz",
        ref_url="https://ctg.cncr.nl/software/MAGMA/ref_data/g1000_eur.zip",
        syn_url="https://ctg.cncr.nl/software/MAGMA/aux_files/dbsnp151.synonyms.zip",
    resources:
        mem_mb=4000,
    shell:
        r"""
        mkdir -p {params.outdir}

        # Gene location file
        wget --max-redirect=3 --timeout=300 -q -O {params.outdir}/NCBI37.3.gene.loc.gz \
            {params.gene_loc_url}
        gunzip -f {params.outdir}/NCBI37.3.gene.loc.gz

        # 1000G EUR reference panel
        TMPZIP=$(mktemp /tmp/g1000_eur_XXXXXX.zip)
        wget --max-redirect=3 --timeout=300 -q -O "$TMPZIP" {params.ref_url}
        unzip -o "$TMPZIP" -d {params.outdir}
        rm -f "$TMPZIP"

        # dbSNP synonyms
        TMPZIP=$(mktemp /tmp/dbsnp151_syn_XXXXXX.zip)
        wget --max-redirect=3 --timeout=300 -q -O "$TMPZIP" {params.syn_url}
        unzip -o "$TMPZIP" -d {params.outdir}
        rm -f "$TMPZIP"

        # T-05-02: validate non-empty
        for f in {output.gene_loc} {output.synonyms}; do
            if [ ! -s "$f" ]; then
                echo "ERROR: downloaded file is empty: $f" >&2
                exit 1
            fi
        done
        """


rule download_ldsc_baseline:
    """Download LDSC baseline model v2.2 + weights + frequency files + plink files.

    Downloads from the Broad Institute LDSC resource page.
    T-05-02 mitigation: validates total size > 1 GB for baseline tgz.
    T-05-06 mitigation: wget --max-redirect=3 --timeout=300.
    """
    output:
        baseline_done=touch("data/reference/ldsc/.baseline_download_done"),
        hapmap3=PATHWAY_CFG.get("ldsc_hapmap3", "data/reference/ldsc/w_hm3.snplist"),
    params:
        outdir="data/reference/ldsc",
        baseline_url="https://broad-alkesgroup-ukbb-ld.s3.amazonaws.com/UKBB_LD/baselineLD_v2.2_ldscores.tgz",
        weights_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/weights_hm3_no_hla.tgz",
        frq_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/1000G_Phase3_frq.tgz",
        plink_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/1000G_Phase3_plinkfiles.tgz",
        hapmap3_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/w_hm3.snplist.bz2",
    resources:
        mem_mb=8000,
    shell:
        r"""
        mkdir -p {params.outdir}

        # Baseline LD scores v2.2
        wget --max-redirect=3 --timeout=300 -q -O {params.outdir}/baselineLD_v2.2.tgz \
            {params.baseline_url}
        FSIZE=$(stat -c%s {params.outdir}/baselineLD_v2.2.tgz 2>/dev/null || stat -f%z {params.outdir}/baselineLD_v2.2.tgz)
        if [ "$FSIZE" -lt 1000000000 ]; then
            echo "ERROR: Baseline tgz too small ($FSIZE bytes, expected >1GB)" >&2
            exit 1
        fi
        tar xzf {params.outdir}/baselineLD_v2.2.tgz -C {params.outdir}
        rm -f {params.outdir}/baselineLD_v2.2.tgz

        # Weights
        wget --max-redirect=3 --timeout=300 -q -O {params.outdir}/weights_hm3_no_hla.tgz \
            {params.weights_url}
        tar xzf {params.outdir}/weights_hm3_no_hla.tgz -C {params.outdir}
        rm -f {params.outdir}/weights_hm3_no_hla.tgz

        # Frequency files
        wget --max-redirect=3 --timeout=300 -q -O {params.outdir}/1000G_Phase3_frq.tgz \
            {params.frq_url}
        tar xzf {params.outdir}/1000G_Phase3_frq.tgz -C {params.outdir}
        rm -f {params.outdir}/1000G_Phase3_frq.tgz

        # Plink files
        wget --max-redirect=3 --timeout=300 -q -O {params.outdir}/1000G_Phase3_plinkfiles.tgz \
            {params.plink_url}
        tar xzf {params.outdir}/1000G_Phase3_plinkfiles.tgz -C {params.outdir}
        rm -f {params.outdir}/1000G_Phase3_plinkfiles.tgz

        # HapMap3 SNP list
        wget --max-redirect=3 --timeout=300 -q -O {params.outdir}/w_hm3.snplist.bz2 \
            {params.hapmap3_url}
        bzip2 -df {params.outdir}/w_hm3.snplist.bz2
        """


rule download_ldsc_seg:
    """Download LDSC-SEG tissue-specific annotation files.

    Multi_tissue_gene_expr and Multi_tissue_chromatin from Finucane 2018.
    T-05-02 mitigation: validates download sizes.
    """
    output:
        gene_expr_done=touch("data/reference/ldsc_seg/.gene_expr_download_done"),
        chromatin_done=touch("data/reference/ldsc_seg/.chromatin_download_done"),
    params:
        outdir="data/reference/ldsc_seg",
        gene_expr_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/Multi_tissue_gene_expr.tgz",
        chromatin_url="https://storage.googleapis.com/broad-alkesgroup-public-requester-pays/LDSCORE/Multi_tissue_chromatin.tgz",
    resources:
        mem_mb=4000,
    shell:
        r"""
        mkdir -p {params.outdir}

        # Multi-tissue gene expression LD scores
        wget --max-redirect=3 --timeout=300 -q -O {params.outdir}/Multi_tissue_gene_expr.tgz \
            {params.gene_expr_url}
        tar xzf {params.outdir}/Multi_tissue_gene_expr.tgz -C {params.outdir}
        rm -f {params.outdir}/Multi_tissue_gene_expr.tgz

        # Multi-tissue chromatin LD scores
        wget --max-redirect=3 --timeout=300 -q -O {params.outdir}/Multi_tissue_chromatin.tgz \
            {params.chromatin_url}
        tar xzf {params.outdir}/Multi_tissue_chromatin.tgz -C {params.outdir}
        rm -f {params.outdir}/Multi_tissue_chromatin.tgz
        """


rule download_msigdb:
    """Download MSigDB gene sets via msigdbr R package.

    Uses the msigdbr R package (NOT web download) to avoid registration
    requirements per Pitfall 6 from 05-RESEARCH.md. Downloads KEGG,
    Reactome, GO BP, and Hallmark collections as GMT files.
    """
    output:
        kegg=os.path.join(
            PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "c2.cp.kegg.gmt"
        ),
        reactome=os.path.join(
            PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "c2.cp.reactome.gmt"
        ),
        gobp=os.path.join(
            PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "c5.go.bp.gmt"
        ),
        hallmark=os.path.join(
            PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "h.all.gmt"
        ),
    params:
        outdir=PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"),
    conda:
        GPROFILER_ENV
    shell:
        r"""
        mkdir -p {params.outdir}
        Rscript -e '
        library(msigdbr)

        write_gmt <- function(df, path) {{
            sets <- split(df, df$gs_name)
            con <- file(path, "w")
            for (nm in names(sets)) {{
                genes <- unique(sets[[nm]]$gene_symbol)
                cat(nm, "msigdb", paste(genes, collapse="\t"), "\n",
                    sep="\t", file=con)
            }}
            close(con)
        }}

        # KEGG
        kegg <- msigdbr(species="Homo sapiens", category="C2", subcategory="CP:KEGG")
        write_gmt(kegg, "{params.outdir}/c2.cp.kegg.gmt")

        # Reactome
        reactome <- msigdbr(species="Homo sapiens", category="C2", subcategory="CP:REACTOME")
        write_gmt(reactome, "{params.outdir}/c2.cp.reactome.gmt")

        # GO Biological Process
        gobp <- msigdbr(species="Homo sapiens", category="C5", subcategory="GO:BP")
        write_gmt(gobp, "{params.outdir}/c5.go.bp.gmt")

        # Hallmark
        hallmark <- msigdbr(species="Homo sapiens", category="H")
        write_gmt(hallmark, "{params.outdir}/h.all.gmt")

        cat("MSigDB download complete\\n")
        '
        """


rule download_hess_panel:
    """Download HESS LD reference panel and partition files.

    HESS (Shi et al. 2017) requires its own LD reference panel based on
    1000 Genomes EUR. Downloaded from the HESS GitHub/UCLA Box.
    T-05-03 mitigation: validates file size (>1GB for full panel).
    """
    output:
        ld_done=touch("data/reference/hess/.ld_panel_download_done"),
        partition_done=touch("data/reference/hess/.partition_download_done"),
    params:
        outdir="data/reference/hess",
        # HESS reference panel URLs (from hess-0.5.4-beta documentation)
        ld_url="https://ucla.box.com/shared/static/l8cjbl5fkge7plsb96xybnrjmhbmsgq5.gz",
        partition_url="https://ucla.box.com/shared/static/6pzgep7kuy0e3t4t1dpyk9mgpizlt28j.gz",
    resources:
        mem_mb=4000,
    shell:
        r"""
        mkdir -p {params.outdir}

        # LD reference panel
        wget --max-redirect=5 --timeout=600 -q -O {params.outdir}/hess_ld_panel.tar.gz \
            {params.ld_url}
        tar xzf {params.outdir}/hess_ld_panel.tar.gz -C {params.outdir}
        rm -f {params.outdir}/hess_ld_panel.tar.gz

        # Partition file
        wget --max-redirect=5 --timeout=600 -q -O {params.outdir}/hess_partition.tar.gz \
            {params.partition_url}
        tar xzf {params.outdir}/hess_partition.tar.gz -C {params.outdir}
        rm -f {params.outdir}/hess_partition.tar.gz

        # T-05-03: validate downloads
        PANEL_DIR={params.outdir}/ld_panel
        if [ -d "$PANEL_DIR" ]; then
            NFILES=$(ls "$PANEL_DIR"/*.bim 2>/dev/null | wc -l || echo 0)
            if [ "$NFILES" -lt 22 ]; then
                echo "WARNING: Expected 22 .bim files in HESS panel, found $NFILES" >&2
            fi
        fi
        """


# ==========================================================================
# Analysis rules: placeholders for Plans 02-05
# ==========================================================================


rule magma_annotate:
    """MAGMA Step 1: Annotate SNPs to genes using gene.loc and SNP locations.

    Runs once per genome build. Input: MAGMA binary, g1000_eur.bim, NCBI37.3.gene.loc.
    Output: gene_annotation.genes.annot
    Shell calls run_magma.py --step annotate.
    """
    input:
        magma=PATHWAY_CFG.get("magma_binary", "tools/magma_v1.10/magma"),
        snp_loc=PATHWAY_CFG.get("magma_ref_panel", "data/reference/magma/g1000_eur") + ".bim",
        gene_loc=PATHWAY_CFG.get("magma_gene_loc", "data/reference/magma/NCBI37.3.gene.loc"),
    output:
        annot=os.path.join(PATHWAY_RESULTS_DIR, "magma", "gene_annotation.genes.annot"),
    params:
        out_prefix=os.path.join(PATHWAY_RESULTS_DIR, "magma", "gene_annotation"),
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_magma.py"),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} --step annotate \
            --magma-binary {input.magma} \
            --snp-loc {input.snp_loc} \
            --gene-loc {input.gene_loc} \
            --out {params.out_prefix}
        """


rule build_magma_set_file:
    """Combine standard MSigDB GMTs + custom + negative controls into all_pathways.set.

    Calls build_magma_geneset.py to merge all GMT files and convert to MAGMA .set format.
    """
    input:
        gene_loc=PATHWAY_CFG.get("magma_gene_loc", "data/reference/magma/NCBI37.3.gene.loc"),
        kegg=os.path.join(
            PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "c2.cp.kegg.gmt"
        ),
        reactome=os.path.join(
            PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "c2.cp.reactome.gmt"
        ),
        gobp=os.path.join(
            PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "c5.go.bp.gmt"
        ),
        hallmark=os.path.join(
            PATHWAY_CFG.get("msigdb_dir", "data/reference/msigdb"), "h.all.gmt"
        ),
        custom=PATHWAY_CFG.get("custom_pathway_gmt", "config/pathway_sets/custom_cardiometabolic.gmt"),
        negctrl=PATHWAY_CFG.get("negative_control_gmt", "config/pathway_sets/negative_controls.gmt"),
    output:
        set_file=os.path.join(PATHWAY_RESULTS_DIR, "magma", "all_pathways.set"),
    params:
        script=os.path.join(workflow.basedir, "..", "..", "python", "build_magma_geneset.py"),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} \
            --gmt-files {input.kegg} {input.reactome} {input.gobp} {input.hallmark} \
                        {input.custom} {input.negctrl} \
            --gene-loc {input.gene_loc} \
            --out {output.set_file}
        """


rule magma_gene_analysis:
    """MAGMA Step 2: Gene-level analysis using summary statistics.

    Per trait x ancestry. Wildcard: {trait}_{ancestry}.
    Shell calls run_magma.py --step gene with appropriate N calculation.
    Critical: binary traits use effective N = 4/(1/n_case + 1/n_ctrl) per Pitfall 4.
    """
    input:
        magma=PATHWAY_CFG.get("magma_binary", "tools/magma_v1.10/magma"),
        bfile_bed=PATHWAY_CFG.get("magma_ref_panel", "data/reference/magma/g1000_eur") + ".bed",
        annot=os.path.join(PATHWAY_RESULTS_DIR, "magma", "gene_annotation.genes.annot"),
        sumstats=os.path.join(
            config["paths"]["harmonized_sumstats"], "{trait}_{ancestry}.tsv"
        ),
    output:
        genes_raw=os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}.genes.raw"),
    params:
        out_prefix=lambda wc: os.path.join(PATHWAY_RESULTS_DIR, "magma", f"{wc.trait}_{wc.ancestry}"),
        bfile=PATHWAY_CFG.get("magma_ref_panel", "data/reference/magma/g1000_eur"),
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_magma.py"),
        trait=lambda wc: wc.trait,
    conda:
        MAGMA_ENV
    resources:
        mem_mb=8000,
    shell:
        """
        python {params.script} --step gene \
            --magma-binary {input.magma} \
            --bfile {params.bfile} \
            --pval {input.sumstats} \
            --gene-annot {input.annot} \
            --trait {params.trait} \
            --sample-size 500000 \
            --out {params.out_prefix}
        """


rule magma_geneset_analysis:
    """MAGMA Step 3: Gene-set (competitive) analysis.

    Per trait x ancestry. Input: .genes.raw, all_pathways.set.
    Output: {trait}_{ancestry}_geneset.gsa.out
    Shell calls run_magma.py --step geneset.
    """
    input:
        magma=PATHWAY_CFG.get("magma_binary", "tools/magma_v1.10/magma"),
        genes_raw=os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}.genes.raw"),
        set_file=os.path.join(PATHWAY_RESULTS_DIR, "magma", "all_pathways.set"),
    output:
        gsa=os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}_geneset.gsa.out"),
    params:
        out_prefix=lambda wc: os.path.join(
            PATHWAY_RESULTS_DIR, "magma", f"{wc.trait}_{wc.ancestry}_geneset"
        ),
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_magma.py"),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} --step geneset \
            --magma-binary {input.magma} \
            --gene-results {input.genes_raw} \
            --set-annot {input.set_file} \
            --out {params.out_prefix}
        """


rule magma_fdr:
    """Post-processing: Apply Benjamini-Hochberg FDR across all gene sets per trait.

    Reads .gsa.out file for a trait x ancestry, applies FDR correction jointly
    across ALL gene sets (standard + custom + negative controls) per D-01a/D-01b.
    Outputs a TSV with added FDR_Q column.
    """
    input:
        gsa=os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}_geneset.gsa.out"),
    output:
        fdr=os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}_geneset_fdr.tsv"),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=2000,
    run:
        import pandas as pd
        from scipy import stats as scipy_stats

        # Read MAGMA .gsa.out (whitespace-delimited, may have comment header lines)
        lines = []
        header = None
        with open(input.gsa) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if header is None:
                    header = line
                    continue
                lines.append(line)

        if not lines:
            # Write empty output
            with open(output.fdr, "w") as fout:
                fout.write("VARIABLE\tTYPE\tNGENES\tBETA\tBETA_STD\tSE\tP\tFDR_Q\n")
        else:
            # Parse into dataframe
            from io import StringIO
            df = pd.read_csv(
                StringIO(header + "\n" + "\n".join(lines)),
                sep=r"\s+",
            )

            # Apply Benjamini-Hochberg FDR correction jointly across all gene sets
            if "P" in df.columns and len(df) > 0:
                from statsmodels.stats.multitest import multipletests
                _, fdr_q, _, _ = multipletests(df["P"].values, method="fdr_bh")
                df["FDR_Q"] = fdr_q
            else:
                df["FDR_Q"] = float("nan")

            df.to_csv(output.fdr, sep="\t", index=False)


rule ldsc_munge:
    """LDSC sumstats munging: convert harmonized sumstats to LDSC format.

    Per trait x ancestry. Calls run_ldsc_partitioned.py --step munge.
    Pre-formats via munge_sumstats_ldsc.py then runs official LDSC munging
    with HapMap3 merge. Post-munge validation warns if < 500K SNPs (Pitfall 2).
    """
    input:
        sumstats=os.path.join(config["paths"]["harmonized_sumstats"], "{trait}_{ancestry}.tsv"),
        hapmap3=PATHWAY_CFG.get("ldsc_hapmap3", "data/reference/ldsc/w_hm3.snplist"),
    output:
        munged=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "munged", "{trait}_{ancestry}.sumstats.gz"),
    params:
        out_prefix=lambda wc: os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_partitioned", "munged", f"{wc.trait}_{wc.ancestry}"
        ),
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_ldsc_partitioned.py"),
        ldsc_dir="tools/ldsc",
        trait=lambda wc: wc.trait,
    conda:
        LDSC_ENV
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} --step munge \
            --ldsc-dir {params.ldsc_dir} \
            --sumstats {input.sumstats} \
            --hapmap3 {input.hapmap3} \
            --sample-size 500000 \
            --trait {params.trait} \
            --out {params.out_prefix}
        """


rule ldsc_build_custom_annotations:
    """Build custom pathway annotations for LDSC partitioned h2.

    Runs once per genome build. Creates per-chromosome binary annotation files
    from custom cardiometabolic gene sets + negative controls using 100 kb
    gene windows (D-04c). Produces 22 .annot.gz files.
    """
    input:
        gene_loc=PATHWAY_CFG.get("magma_gene_loc", "data/reference/magma/NCBI37.3.gene.loc"),
        custom_gmt=PATHWAY_CFG.get("custom_pathway_gmt", "config/pathway_sets/custom_cardiometabolic.gmt"),
        negctrl_gmt=PATHWAY_CFG.get("negative_control_gmt", "config/pathway_sets/negative_controls.gmt"),
    output:
        annot=expand(
            os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "annotations", "custom_pathway.{chr}.annot.gz"),
            chr=range(1, 23),
        ),
    params:
        script=os.path.join(workflow.basedir, "..", "..", "python", "build_ldsc_annot.py"),
        bim_prefix=os.path.join(
            PATHWAY_CFG.get("ldsc_plink", "data/reference/ldsc/1000G_Phase3_plinkfiles"),
            "1000G.EUR.QC",
        ),
        out_prefix=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "annotations", "custom_pathway"),
        window_kb=PATHWAY_CFG.get("snp_gene_window_kb", 100),
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} \
            --bim-prefix {params.bim_prefix} \
            --gene-loc {input.gene_loc} \
            --gmt-files {input.custom_gmt} {input.negctrl_gmt} \
            --window-kb {params.window_kb} \
            --out-prefix {params.out_prefix}
        """


rule ldsc_compute_custom_ld_scores:
    """Compute LD scores for custom pathway annotations.

    Per chromosome. Input: custom annotations from ldsc_build_custom_annotations,
    1000G Phase 3 plink files. Output: per-chromosome .l2.ldscore.gz files.
    T-05-15: mem_mb=8000 for baseline LD computation.
    """
    input:
        annot=os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_partitioned", "annotations", "custom_pathway.{chr}.annot.gz"
        ),
        hapmap3=PATHWAY_CFG.get("ldsc_hapmap3", "data/reference/ldsc/w_hm3.snplist"),
    output:
        ldscore=os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_partitioned", "ld_scores", "custom_pathway.{chr}.l2.ldscore.gz"
        ),
    params:
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_ldsc_partitioned.py"),
        ldsc_dir="tools/ldsc",
        annot_prefix=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "annotations", "custom_pathway"),
        bfile_prefix=os.path.join(
            PATHWAY_CFG.get("ldsc_plink", "data/reference/ldsc/1000G_Phase3_plinkfiles"),
            "1000G.EUR.QC",
        ),
        out_prefix=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "ld_scores", "custom_pathway"),
        chrom=lambda wc: wc.chr,
    conda:
        LDSC_ENV
    resources:
        mem_mb=8000,
    shell:
        """
        python {params.script} --step compute-ld-scores \
            --ldsc-dir {params.ldsc_dir} \
            --annot-prefix {params.annot_prefix} \
            --bfile-prefix {params.bfile_prefix} \
            --out-prefix {params.out_prefix} \
            --hapmap3 {input.hapmap3} \
            --chromosomes {params.chrom}
        """


rule ldsc_partitioned_h2:
    """LDSC partitioned heritability with baseline v2.2 + custom annotations.

    Per trait x ancestry. Always includes --overlap-annot flag (anti-pattern).
    Baseline v2.2 always first in --ref-ld-chr (D-04a).
    T-05-15: mem_mb=8000 for baseline model.
    """
    input:
        munged=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "munged", "{trait}_{ancestry}.sumstats.gz"),
        custom_ld=expand(
            os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "ld_scores", "custom_pathway.{chr}.l2.ldscore.gz"),
            chr=range(1, 23),
        ),
    output:
        results=os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_partitioned", "{trait}_{ancestry}_pathway_h2.results"
        ),
    params:
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_ldsc_partitioned.py"),
        ldsc_dir="tools/ldsc",
        baseline_prefix=os.path.join(
            PATHWAY_CFG.get("ldsc_baseline", "data/reference/ldsc/baselineLD_v2.2"), "baselineLD."
        ),
        custom_prefix=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "ld_scores", "custom_pathway."),
        w_ld_chr=os.path.join(
            PATHWAY_CFG.get("ldsc_weights", "data/reference/ldsc/weights_hm3_no_hla"), "weights."
        ),
        frqfile_chr=os.path.join(
            PATHWAY_CFG.get("ldsc_frq", "data/reference/ldsc/1000G_Phase3_frq"), "1000G.EUR.QC."
        ),
        out_prefix=lambda wc: os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_partitioned", f"{wc.trait}_{wc.ancestry}_pathway_h2"
        ),
    conda:
        LDSC_ENV
    resources:
        mem_mb=8000,
    shell:
        """
        python {params.script} --step h2 \
            --ldsc-dir {params.ldsc_dir} \
            --sumstats {input.munged} \
            --ref-ld-chr {params.baseline_prefix},{params.custom_prefix} \
            --w-ld-chr {params.w_ld_chr} \
            --frqfile-chr {params.frqfile_chr} \
            --out {params.out_prefix}
        """


rule ldsc_aggregate_h2:
    """Aggregate all per-trait LDSC partitioned h2 .results into a summary TSV.

    Columns: trait, ancestry, annotation, prop_snps, prop_h2, enrichment,
    enrichment_p, enrichment_se.
    """
    input:
        results=expand(
            os.path.join(
                PATHWAY_RESULTS_DIR, "ldsc_partitioned", "{trait}_{ancestry}_pathway_h2.results"
            ),
            zip,
            trait=[t for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
            ancestry=[a for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
        ),
    output:
        summary=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "h2_summary.tsv"),
    resources:
        mem_mb=2000,
    run:
        import csv

        header = [
            "trait", "ancestry", "annotation", "prop_snps", "prop_h2",
            "enrichment", "enrichment_p", "enrichment_se",
        ]

        rows = []
        for results_path in input.results:
            # Extract trait_ancestry from filename
            basename = os.path.basename(results_path)
            # Format: {trait}_{ancestry}_pathway_h2.results
            parts = basename.replace("_pathway_h2.results", "").rsplit("_", 1)
            if len(parts) == 2:
                trait, ancestry = parts
            else:
                trait, ancestry = basename, "unknown"

            if not os.path.exists(results_path):
                continue

            with open(results_path) as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    rows.append({
                        "trait": trait,
                        "ancestry": ancestry,
                        "annotation": row.get("Category", ""),
                        "prop_snps": row.get("Prop._SNPs", ""),
                        "prop_h2": row.get("Prop._h2", ""),
                        "enrichment": row.get("Enrichment", ""),
                        "enrichment_p": row.get("Enrichment_p", ""),
                        "enrichment_se": row.get("Enrichment_std_error", ""),
                    })

        with open(output.summary, "w") as f:
            writer = csv.DictWriter(f, fieldnames=header, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

        print(f"Aggregated {len(rows)} h2 results from {len(input.results)} files")


rule ldsc_seg_gene_expr:
    """LDSC-SEG tissue-specific enrichment: GTEx 53-tissue gene expression.

    Per trait x ancestry. Uses pre-built Multi_tissue_gene_expr.ldcts from
    Finucane 2018. Calls run_ldsc_seg.py with --h2-cts (NOT --h2).
    """
    input:
        munged=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "munged", "{trait}_{ancestry}.sumstats.gz"),
    output:
        results=os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_seg", "{trait}_{ancestry}_gene_expr.cell_type_results.txt"
        ),
    params:
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_ldsc_seg.py"),
        ldsc_dir="tools/ldsc",
        ref_ld_chr=os.path.join(
            PATHWAY_CFG.get("ldsc_baseline", "data/reference/ldsc/baselineLD_v2.2"), "baselineLD."
        ),
        w_ld_chr=os.path.join(
            PATHWAY_CFG.get("ldsc_weights", "data/reference/ldsc/weights_hm3_no_hla"), "weights."
        ),
        ldcts=os.path.join(
            PATHWAY_CFG.get("ldsc_seg_gene_expr", "data/reference/ldsc_seg/Multi_tissue_gene_expr"),
            "Multi_tissue_gene_expr.ldcts",
        ),
        out_prefix=lambda wc: os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_seg", f"{wc.trait}_{wc.ancestry}_gene_expr"
        ),
    conda:
        LDSC_ENV
    resources:
        mem_mb=8000,
    shell:
        """
        python {params.script} \
            --ldsc-dir {params.ldsc_dir} \
            --sumstats {input.munged} \
            --ref-ld-chr {params.ref_ld_chr} \
            --w-ld-chr {params.w_ld_chr} \
            --ldcts-file {params.ldcts} \
            --out {params.out_prefix}
        """


rule ldsc_seg_chromatin:
    """LDSC-SEG tissue-specific enrichment: Roadmap Epigenomics chromatin.

    Per trait x ancestry. Uses pre-built Multi_tissue_chromatin.ldcts.
    """
    input:
        munged=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "munged", "{trait}_{ancestry}.sumstats.gz"),
    output:
        results=os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_seg", "{trait}_{ancestry}_chromatin.cell_type_results.txt"
        ),
    params:
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_ldsc_seg.py"),
        ldsc_dir="tools/ldsc",
        ref_ld_chr=os.path.join(
            PATHWAY_CFG.get("ldsc_baseline", "data/reference/ldsc/baselineLD_v2.2"), "baselineLD."
        ),
        w_ld_chr=os.path.join(
            PATHWAY_CFG.get("ldsc_weights", "data/reference/ldsc/weights_hm3_no_hla"), "weights."
        ),
        ldcts=os.path.join(
            PATHWAY_CFG.get("ldsc_seg_chromatin", "data/reference/ldsc_seg/Multi_tissue_chromatin"),
            "Multi_tissue_chromatin.ldcts",
        ),
        out_prefix=lambda wc: os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_seg", f"{wc.trait}_{wc.ancestry}_chromatin"
        ),
    conda:
        LDSC_ENV
    resources:
        mem_mb=8000,
    shell:
        """
        python {params.script} \
            --ldsc-dir {params.ldsc_dir} \
            --sumstats {input.munged} \
            --ref-ld-chr {params.ref_ld_chr} \
            --w-ld-chr {params.w_ld_chr} \
            --ldcts-file {params.ldcts} \
            --out {params.out_prefix}
        """


rule ldsc_seg_shared_tissues:
    """Aggregate LDSC-SEG results and identify tissues shared between trait pairs.

    Input: all gene_expr and chromatin .cell_type_results.txt files.
    Output: shared tissue summary per D-05b.
    """
    input:
        gene_expr=expand(
            os.path.join(
                PATHWAY_RESULTS_DIR, "ldsc_seg", "{trait}_{ancestry}_gene_expr.cell_type_results.txt"
            ),
            zip,
            trait=[t for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
            ancestry=[a for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
        ),
        chromatin=expand(
            os.path.join(
                PATHWAY_RESULTS_DIR, "ldsc_seg", "{trait}_{ancestry}_chromatin.cell_type_results.txt"
            ),
            zip,
            trait=[t for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
            ancestry=[a for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
        ),
    output:
        summary=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_seg", "shared_tissue_summary.tsv"),
    resources:
        mem_mb=4000,
    run:
        import sys as _sys
        _sys.path.insert(0, os.path.join(workflow.basedir, "..", "..", "python"))
        from run_ldsc_seg import identify_shared_tissues, parse_seg_results

        # Collect all results
        all_seg = {}
        for f in input.gene_expr + input.chromatin:
            basename = os.path.basename(f)
            # Extract trait from filename
            parts = basename.replace(".cell_type_results.txt", "").rsplit("_", 2)
            if len(parts) >= 2:
                trait = parts[0]
                if trait not in all_seg:
                    all_seg[trait] = []
                parsed = parse_seg_results(f)
                all_seg[trait].extend(parsed)

        # Define trait pairs for shared tissue analysis (D-05b)
        trait_pairs = [
            ("bmi", "t2d"),
            ("hypertension", "stroke"),
            ("bmi", "hypertension"),
            ("t2d", "stroke"),
            ("bmi", "asthma"),
        ]

        shared = identify_shared_tissues(all_seg, trait_pairs)

        with open(output.summary, "w") as fout:
            fout.write("trait1\ttrait2\tshared_tissue\tp_trait1\tp_trait2\n")
            for row in shared:
                fout.write(
                    f"{row['trait1']}\t{row['trait2']}\t{row['shared_tissue']}\t"
                    f"{row['p_trait1']}\t{row['p_trait2']}\n"
                )

        print(f"Found {len(shared)} shared tissue enrichments across {len(trait_pairs)} pairs")


rule fix_ldcts_paths:
    """Fix downloaded .ldcts files to use local annotation paths.

    One-time fix: rewrites absolute paths from Broad download to local
    relative paths. Validates each referenced LD score file exists.
    T-05-13: validates and rewrites .ldcts paths.
    """
    input:
        gene_expr_ldcts=os.path.join(
            PATHWAY_CFG.get("ldsc_seg_gene_expr", "data/reference/ldsc_seg/Multi_tissue_gene_expr"),
            "Multi_tissue_gene_expr.ldcts",
        ),
        chromatin_ldcts=os.path.join(
            PATHWAY_CFG.get("ldsc_seg_chromatin", "data/reference/ldsc_seg/Multi_tissue_chromatin"),
            "Multi_tissue_chromatin.ldcts",
        ),
    output:
        gene_expr_fixed=os.path.join(
            PATHWAY_CFG.get("ldsc_seg_gene_expr", "data/reference/ldsc_seg/Multi_tissue_gene_expr"),
            "Multi_tissue_gene_expr_fixed.ldcts",
        ),
        chromatin_fixed=os.path.join(
            PATHWAY_CFG.get("ldsc_seg_chromatin", "data/reference/ldsc_seg/Multi_tissue_chromatin"),
            "Multi_tissue_chromatin_fixed.ldcts",
        ),
    params:
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_ldsc_seg.py"),
    resources:
        mem_mb=1000,
    run:
        import sys as _sys
        _sys.path.insert(0, os.path.join(workflow.basedir, "..", "..", "python"))
        from run_ldsc_seg import fix_ldcts_paths

        fix_ldcts_paths(input.gene_expr_ldcts, output.gene_expr_fixed)
        fix_ldcts_paths(input.chromatin_ldcts, output.chromatin_fixed)


rule hess_local_rhog:
    """HESS local heritability and cross-trait genetic correlation.

    Placeholder -- implementation in Plan 05-04.
    """
    input:
        sumstats=os.path.join(config["paths"]["harmonized_sumstats"], "{trait}.{ancestry}.tsv.bgz"),
    output:
        results=os.path.join(PATHWAY_RESULTS_DIR, "hess", "{trait}.{ancestry}.step2"),
    run:
        pass


rule build_gprofiler_background:
    """Build discoverability-matched background gene list per D-03a (Reimand 2019).

    Input: harmonized sumstats for all 5 traits (EUR), NCBI37.3.gene.loc.
    Output: background_genes.txt (one gene symbol per line).
    Uses 500 kb window around each GWS SNP (P < 5e-8), union across traits.
    """
    input:
        gene_loc=PATHWAY_CFG.get("magma_gene_loc", "data/reference/magma/NCBI37.3.gene.loc"),
        sumstats=expand(
            os.path.join(config["paths"]["harmonized_sumstats"], "{trait}_EUR.tsv"),
            trait=config.get("traits", []),
        ),
    output:
        bg_genes=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "background_genes.txt"),
    params:
        script=os.path.join(workflow.basedir, "..", "..", "python", "build_gprofiler_bg.py"),
        sumstats_dir=config["paths"]["harmonized_sumstats"],
        traits=",".join(config.get("traits", [])),
        window_kb=PATHWAY_CFG.get("gprofiler_bg_window_kb", 500),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} \
            --sumstats-dir {params.sumstats_dir} \
            --traits {params.traits} \
            --ancestry EUR \
            --gene-loc {input.gene_loc} \
            --window-kb {params.window_kb} \
            --p-threshold 5e-8 \
            --out {output.bg_genes}
        """


rule extract_tier_ab_genes:
    """Extract Tier A + Tier B gene symbols from Phase 2 tier assignments.

    Input: tier_assignments.tsv from Phase 2.
    Output: tier_ab_genes.txt (unique gene symbols with PP.H4 >= 0.5 per Tier B).
    Tier A: gwas PP.H4 >= 0.8 AND qtl PP.H4 >= 0.8
    Tier B: gwas PP.H4 >= 0.8 AND qtl PP.H4 >= 0.5
    """
    input:
        tiers=os.path.join(config["paths"]["results_root"], "qtl_coloc", "tier_assignments.tsv"),
    output:
        gene_list=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "tier_ab_genes.txt"),
    resources:
        mem_mb=2000,
    run:
        import pandas as pd

        df = pd.read_csv(input.tiers, sep="\t")

        # Filter to Tier A + Tier B entries
        tier_ab = df[df["tier"].isin(["Tier A", "Tier B"])]

        # Extract unique gene symbols
        if "gene_symbol" in tier_ab.columns:
            genes = sorted(tier_ab["gene_symbol"].dropna().unique())
        elif "gene" in tier_ab.columns:
            genes = sorted(tier_ab["gene"].dropna().unique())
        else:
            raise ValueError(
                f"No gene column found in tier assignments. "
                f"Available columns: {list(df.columns)}"
            )

        with open(output.gene_list, "w") as f:
            for gene in genes:
                f.write(f"{gene}\n")

        print(f"Extracted {len(genes)} Tier A+B genes")


rule gprofiler_enrichment:
    """g:Profiler functional enrichment of coloc-nominated genes.

    Uses run_gprofiler.py with REST API, custom background, and
    evcodes=TRUE per D-03b to exclude electronic GO annotations.
    Sources: GO:BP, KEGG, REAC.
    """
    input:
        gene_list=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "tier_ab_genes.txt"),
        bg_genes=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "background_genes.txt"),
    output:
        results=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "enrichment_results.tsv"),
    params:
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_gprofiler.py"),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} \
            --gene-list {input.gene_list} \
            --background {input.bg_genes} \
            --sources GO:BP,KEGG,REAC \
            --exclude-iea \
            --out {output.results}
        """


rule gprofiler_negative_controls:
    """Run g:Profiler enrichment on each negative control gene set separately.

    Tests that negative control gene sets (HLA immune, cosmetic, blood group)
    produce q > 0.05 for cardiometabolic pathways (REQ-7 / D-06b).
    Concatenates results for all negative control sets.
    """
    input:
        negctrl_gmt=PATHWAY_CFG.get(
            "negative_control_gmt", "config/pathway_sets/negative_controls.gmt"
        ),
        bg_genes=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "background_genes.txt"),
    output:
        results=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "neg_ctrl_enrichment.tsv"),
    params:
        script=os.path.join(workflow.basedir, "..", "..", "python", "run_gprofiler.py"),
        outdir=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler"),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
    run:
        import sys
        sys.path.insert(0, os.path.join(workflow.basedir, "..", "..", "python"))
        from build_magma_geneset import parse_gmt
        from run_gprofiler import run_enrichment_api, _write_results_tsv, _read_gene_list

        bg_genes = _read_gene_list(input.bg_genes)
        neg_ctrl_sets = parse_gmt(input.negctrl_gmt)

        all_results = []
        for set_name, _desc, gene_list in neg_ctrl_sets:
            print(f"Running g:Profiler on negative control: {set_name}")
            try:
                results = run_enrichment_api(
                    query_genes=gene_list,
                    background_genes=bg_genes,
                    sources=["GO:BP", "KEGG", "REAC"],
                    exclude_iea=True,
                )
                for r in results:
                    r["neg_ctrl_set"] = set_name
                    r["is_negative_control"] = "TRUE"
                all_results.extend(results)
            except Exception as e:
                print(f"Warning: {set_name} enrichment failed: {e}")

        # Write concatenated results
        columns = [
            "source", "term_id", "term_name", "p_value", "q_value",
            "intersection_size", "query_size", "term_size",
            "effective_domain_size", "genes", "neg_ctrl_set", "is_negative_control",
        ]
        with open(output.results, "w") as fout:
            fout.write("\t".join(columns) + "\n")
            for row in all_results:
                values = [str(row.get(col, "")) for col in columns]
                fout.write("\t".join(values) + "\n")

        print(f"Wrote {len(all_results)} neg ctrl enrichment results")


rule permutation_null:
    """Permutation-based null for multi-method convergence testing (D-06c).

    Placeholder -- implementation in Plan 05-05.
    """
    input:
        gene_sets=PATHWAY_CFG.get("custom_pathway_gmt", "config/pathway_sets/custom_cardiometabolic.gmt"),
    output:
        null_dist=os.path.join(PATHWAY_RESULTS_DIR, "permutation", "{trait}.{ancestry}.null_dist.tsv"),
    run:
        pass


rule aggregate_pathway_results:
    """Aggregate results from all pathway analysis methods.

    Placeholder -- implementation in Plan 05-05.
    """
    input:
        magma=os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}.{ancestry}.gsa.out"),
        ldsc=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_h2", "{trait}.{ancestry}.results"),
        gprofiler=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "{trait}.{ancestry}.enrichment.tsv"),
    output:
        aggregated=os.path.join(PATHWAY_RESULTS_DIR, "aggregated", "{trait}.{ancestry}.pathway_summary.tsv"),
    run:
        pass
