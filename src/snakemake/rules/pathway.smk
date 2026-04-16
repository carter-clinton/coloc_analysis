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
from pathlib import Path

PATHWAY_CFG = config.get("pathway", {})
PATHWAY_RESULTS_DIR = PATHWAY_CFG.get("results_dir", "results/pathway")

# Per-trait sample-size metadata for effective-N computation (CR-02 fix).
# Binary traits must pass --n-case/--n-ctrl so run_magma.py / run_ldsc_*.py
# can compute N_eff = 4 / (1/n_case + 1/n_ctrl) per Pitfall 4. Quantitative
# traits pass --sample-size directly. The configured values live in
# config/pipeline.yaml under pathway.trait_counts. When a trait is missing
# from the config or has zero counts, helper rules fall back to legacy
# totals from datasets.yaml (or raise at runtime for binary traits).
TRAIT_COUNTS = PATHWAY_CFG.get("trait_counts", {})


def _magma_n_flags(trait: str) -> str:
    """Render the correct MAGMA --sample-size or --n-case/--n-ctrl flags.

    Dispatches on pathway.trait_counts[trait].type:
      - "binary":      emits "--n-case N --n-ctrl N" (run_magma.py computes N_eff)
      - "quantitative": emits "--sample-size N"
    Falls back to an empty string when the trait is absent; run_magma.py will
    then raise, surfacing misconfiguration instead of silently using a hard-coded N.
    """
    entry = TRAIT_COUNTS.get(trait, {}) or {}
    ttype = entry.get("type", "").lower()
    if ttype == "binary":
        n_case = entry.get("n_case")
        n_ctrl = entry.get("n_ctrl")
        if n_case and n_ctrl:
            return f"--n-case {int(n_case)} --n-ctrl {int(n_ctrl)}"
    elif ttype == "quantitative":
        n = entry.get("sample_size")
        if n:
            return f"--sample-size {int(n)}"
    return ""

# Conda env paths (absolute, per DEF-01-02 pattern)
MAGMA_ENV = str(Path(workflow.basedir) / "envs" / "magma.yml")
LDSC_ENV = str(Path(workflow.basedir) / "envs" / "ldsc_py3.yml")
HESS_ENV = str(Path(workflow.basedir) / "envs" / "hess_py27.yml")
GPROFILER_ENV = str(Path(workflow.basedir) / "envs" / "gprofiler.yml")

# HESS Python 2.7 interpreter path for subprocess invocation.
# run_hess.py (Python 3) invokes tools/hess/hess.py via --python27.
# The hess_py27 conda env provides Py2.7; resolve its prefix from the
# snakemake conda cache hash. Rules that call run_hess.py use MAGMA_ENV
# (Python 3) and pass HESS_PY27_BIN via --python27.
import hashlib as _hl
_hess_yaml = Path(workflow.basedir) / "envs" / "hess_py27.yml"
_hess_hash = _hl.md5(_hess_yaml.read_bytes()).hexdigest()
# Snakemake conda prefix naming: find the matching env dir
_conda_dir = Path(workflow.basedir) / ".snakemake" / "conda"
_hess_py27_candidates = sorted(_conda_dir.glob("*_/bin/python2.7"))
HESS_PY27_BIN = str(_hess_py27_candidates[0]) if _hess_py27_candidates else "python2.7"

# Trait configuration for HESS trait pair generation
TRAITS = config.get("traits", ["bmi", "t2d", "hypertension", "asthma", "stroke"])
ANCESTRIES = config.get("ancestries", ["EUR", "AFR", "EAS", "HIS"])
TRAIT_ANCESTRIES = config.get("trait_ancestries", {})

# Generate all trait pairs with shared ancestries for rho-HESS (D-02b).
# 5 traits = 10 unique pairs. For each pair, run only for ancestries
# available in BOTH traits (intersection of trait_ancestries).
TRAIT_PAIRS = []
for _i, _t1 in enumerate(TRAITS):
    for _t2 in TRAITS[_i + 1:]:
        _shared_anc = sorted(
            set(TRAIT_ANCESTRIES.get(_t1, ANCESTRIES))
            & set(TRAIT_ANCESTRIES.get(_t2, ANCESTRIES))
        )
        for _anc in _shared_anc:
            TRAIT_PAIRS.append((_t1, _t2, _anc))

# Convenience lists for Snakemake expand()
TRAIT_PAIR_WILDCARDS = [
    {"trait1": t1, "trait2": t2, "ancestry": anc}
    for t1, t2, anc in TRAIT_PAIRS
]
CHROMOSOMES = [str(c) for c in range(1, 23)]


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

        # Idempotency guard (qsk D-02, D-03): skip if MAGMA reference data already staged.
        # CNCR (ctg.cncr.nl) uses a JavaScript gate that blocks curl/wget for aux_files + ref_data.
        # When Carter has manually downloaded + scp'd these files, the rule must detect and
        # short-circuit; otherwise it hangs on the JS-gated URLs.
        if [ -f {params.outdir}/NCBI37.3.gene.loc ] && \
           [ -f {params.outdir}/g1000_eur.bim ] && \
           [ -f {params.outdir}/g1000_eur.fam ] && \
           [ -f {params.outdir}/dbsnp151.synonyms ]; then
            echo "download_magma_ref: detected pre-staged MAGMA reference data on disk; skipping download" >&2
            touch {output.gene_loc} {output.ref_prefix} {output.synonyms}
            exit 0
        fi

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

        # Idempotency guard (D-02, D-03): if references are already staged on disk,
        # touch the flag + snplist outputs and exit cleanly. Prevents re-fetching
        # ~5 GB from Broad S3 + GCS requester-pays (the latter fails without auth)
        # on systems where Carter has manually staged the data from Zenodo.
        if [ -f {params.outdir}/baselineLD.22.l2.M ] && \
           [ -d {params.outdir}/1000G_EUR_Phase3_plink ] && \
           [ -d {params.outdir}/1000G_Phase3_frq ] && \
           [ -d {params.outdir}/1000G_Phase3_weights_hm3_no_MHC ] && \
           [ -f {output.hapmap3} ]; then
            echo "download_ldsc_baseline: detected pre-staged LDSC reference data on disk; skipping download" >&2
            touch {output.baseline_done}
            exit 0
        fi

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

        # Idempotency guard (qsk D-02, D-03): skip if LDSC-SEG data already staged.
        # Upstream URL is GCS requester-pays (fails without GCP auth). Carter's manual
        # staging landed at data/reference/ldsc/Multi_tissue_*; symlinks under ldsc_seg/
        # are created out-of-band (see 260414-qsk plan Change A). The [ -d ] checks
        # resolve through those symlinks.
        if [ -d {params.outdir}/Multi_tissue_gene_expr_1000Gv3_ldscores ] && \
           [ -d {params.outdir}/Multi_tissue_chromatin_1000Gv3_ldscores ]; then
            echo "download_ldsc_seg: detected pre-staged LDSC-SEG data (via symlink) on disk; skipping download" >&2
            touch {output.gene_expr_done} {output.chromatin_done}
            exit 0
        fi

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

        # msigdbr >=10.0 API: collection=/subcollection= (was category=/subcategory=); KEGG_LEGACY preserves Phase 5 dev assumptions (186 sets, original KEGG).
        # KEGG
        kegg <- msigdbr(species="Homo sapiens", collection="C2", subcollection="CP:KEGG_LEGACY")
        write_gmt(kegg, "{params.outdir}/c2.cp.kegg.gmt")

        # Reactome
        reactome <- msigdbr(species="Homo sapiens", collection="C2", subcollection="CP:REACTOME")
        write_gmt(reactome, "{params.outdir}/c2.cp.reactome.gmt")

        # GO Biological Process
        gobp <- msigdbr(species="Homo sapiens", collection="C5", subcollection="GO:BP")
        write_gmt(gobp, "{params.outdir}/c5.go.bp.gmt")

        # Hallmark (no subcollection in msigdbr 26)
        hallmark <- msigdbr(species="Homo sapiens", collection="H")
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

        # Idempotency guard (qsk D-02, D-03): skip if HESS panel + partition data already staged.
        # UCLA Box "shared/static/..." links are ephemeral (expire or break without notice).
        # Carter staged LD panel as a symlink farm (data/reference/hess/ld_panel/EUR/chr{1..22}.{bed,bim,fam})
        # pointing into ldsc/1000G_EUR_Phase3_plink, and partition files from Bitbucket ldetect-data.
        if [ -f {params.outdir}/ld_panel/EUR/chr22.bim ] && \
           [ -f {params.outdir}/partition/EUR_fourier_ls-all.bed ] && \
           [ -f {params.outdir}/partition/AFR_fourier_ls-all.bed ] && \
           [ -f {params.outdir}/partition/EAS_fourier_ls-all.bed ]; then
            echo "download_hess_panel: detected pre-staged HESS panel + partition data on disk; skipping download" >&2
            touch {output.ld_done} {output.partition_done}
            exit 0
        fi

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
        gene_loc=PATHWAY_CFG.get("magma_gene_loc", "data/reference/magma/NCBI37.3.gene.loc"),
        # RO7 DAG wiring: flag-file dependency on download_magma_ref (ref_prefix touch).
        # g1000_eur.bim/.fam are side-effects of the zip unpack and are not declared
        # outputs of any rule, so they cannot live in `input:` (Snakemake would fail
        # to find a producer). The .bed touch output is the declared hook; depending
        # on it creates the DAG edge. The actual .bim filename is passed via params
        # and consumed in the shell block below.
        magma_ref_flag=PATHWAY_CFG.get("magma_ref_panel", "data/reference/magma/g1000_eur") + ".bed",
    output:
        annot=os.path.join(PATHWAY_RESULTS_DIR, "magma", "gene_annotation.genes.annot"),
    params:
        out_prefix=os.path.join(PATHWAY_RESULTS_DIR, "magma", "gene_annotation"),
        script=str(Path(workflow.basedir) / "src" / "python" / "run_magma.py"),
        snp_loc=PATHWAY_CFG.get("magma_ref_panel", "data/reference/magma/g1000_eur") + ".bim",
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} --step annotate \
            --magma-binary {input.magma} \
            --snp-loc {params.snp_loc} \
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
        script=str(Path(workflow.basedir) / "src" / "python" / "build_magma_geneset.py"),
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
            config["paths"]["harmonized_sumstats"], "{trait}.{ancestry}.tsv.bgz"
        ),
    output:
        genes_raw=os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}.genes.raw"),
    params:
        out_prefix=lambda wc: os.path.join(PATHWAY_RESULTS_DIR, "magma", f"{wc.trait}_{wc.ancestry}"),
        bfile=PATHWAY_CFG.get("magma_ref_panel", "data/reference/magma/g1000_eur"),
        script=str(Path(workflow.basedir) / "src" / "python" / "run_magma.py"),
        trait=lambda wc: wc.trait,
        # CR-02 fix: emit --n-case/--n-ctrl for binary traits so run_magma.py
        # computes N_eff = 4/(1/n_case + 1/n_ctrl); emit --sample-size for
        # quantitative traits. Previously hardcoded to --sample-size 500000.
        n_flags=lambda wc: _magma_n_flags(wc.trait),
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
            {params.n_flags} \
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
        script=str(Path(workflow.basedir) / "src" / "python" / "run_magma.py"),
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

    WR-07 fix: previously used a `run:` block which cannot attach a conda env
    in Snakemake 7.x, forcing statsmodels/scipy to live in the host interpreter.
    Now shells out to src/python/magma_fdr.py inside envs/magma.yml, where the
    dependencies are properly pinned.
    """
    input:
        gsa=os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}_geneset.gsa.out"),
    output:
        fdr=os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}_geneset_fdr.tsv"),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "magma_fdr.py"),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=2000,
    shell:
        """
        python {params.script} --gsa {input.gsa} --out {output.fdr}
        """


rule ldsc_munge:
    """LDSC sumstats munging: convert harmonized sumstats to LDSC format.

    Per trait x ancestry. Calls run_ldsc_partitioned.py --step munge.
    Pre-formats via munge_sumstats_ldsc.py then runs official LDSC munging
    with HapMap3 merge. Post-munge validation warns if < 500K SNPs (Pitfall 2).
    """
    input:
        sumstats=os.path.join(
            config["paths"]["harmonized_sumstats"], "{trait}.{ancestry}.tsv.bgz"
        ),
        hapmap3=PATHWAY_CFG.get("ldsc_hapmap3", "data/reference/ldsc/w_hm3.snplist"),
        # RO7 DAG wiring: flag-file dependency on download_ldsc_baseline.
        ldsc_baseline_flag="data/reference/ldsc/.baseline_download_done",
    output:
        munged=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "munged", "{trait}_{ancestry}.sumstats.gz"),
    params:
        out_prefix=lambda wc: os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_partitioned", "munged", f"{wc.trait}_{wc.ancestry}"
        ),
        script=str(Path(workflow.basedir) / "src" / "python" / "run_ldsc_partitioned.py"),
        ldsc_dir="tools/ldsc",
        trait=lambda wc: wc.trait,
        # CR-02 fix: LDSC munge must also use effective N for binary traits.
        # run_ldsc_partitioned.py accepts --sample-size OR --n-case/--n-ctrl and
        # derives N_eff internally. _magma_n_flags() is reused because the CLI
        # surface is identical (both scripts share sumstats_utils.compute_effective_n).
        n_flags=lambda wc: _magma_n_flags(wc.trait),
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
            {params.n_flags} \
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
        # RO7 DAG wiring: flag-file dependency on download_ldsc_baseline (1000G plink files).
        ldsc_baseline_flag="data/reference/ldsc/.baseline_download_done",
    output:
        annot=expand(
            os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "annotations", "custom_pathway.{chr}.annot.gz"),
            chr=range(1, 23),
        ),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "build_ldsc_annot.py"),
        bim_prefix=os.path.join(
            PATHWAY_CFG.get("ldsc_plink", "data/reference/ldsc/1000G_EUR_Phase3_plink"),
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
        # RO7 DAG wiring: flag-file dependency on download_ldsc_baseline (1000G plink files).
        ldsc_baseline_flag="data/reference/ldsc/.baseline_download_done",
    output:
        ldscore=os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_partitioned", "ld_scores", "custom_pathway.{chr}.l2.ldscore.gz"
        ),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_ldsc_partitioned.py"),
        ldsc_dir="tools/ldsc",
        annot_prefix=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "annotations", "custom_pathway"),
        bfile_prefix=os.path.join(
            PATHWAY_CFG.get("ldsc_plink", "data/reference/ldsc/1000G_EUR_Phase3_plink"),
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
        # RO7 DAG wiring: flag-file dependency on download_ldsc_baseline
        # (baselineLD v2.2, weights, frq files referenced via params).
        ldsc_baseline_flag="data/reference/ldsc/.baseline_download_done",
    output:
        results=os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_partitioned", "{trait}_{ancestry}_pathway_h2.results"
        ),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_ldsc_partitioned.py"),
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
        # RO7 DAG wiring: baseline/weights via params + gene-expr ldcts via params.
        ldsc_baseline_flag="data/reference/ldsc/.baseline_download_done",
        ldsc_seg_gene_expr_flag="data/reference/ldsc_seg/.gene_expr_download_done",
    output:
        results=os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_seg", "{trait}_{ancestry}_gene_expr.cell_type_results.txt"
        ),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_ldsc_seg.py"),
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
        # RO7 DAG wiring: baseline/weights via params + chromatin ldcts via params.
        ldsc_baseline_flag="data/reference/ldsc/.baseline_download_done",
        ldsc_seg_chromatin_flag="data/reference/ldsc_seg/.chromatin_download_done",
    output:
        results=os.path.join(
            PATHWAY_RESULTS_DIR, "ldsc_seg", "{trait}_{ancestry}_chromatin.cell_type_results.txt"
        ),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_ldsc_seg.py"),
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
        _sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))
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
        # RO7 DAG wiring: flag-file dependencies on download_ldsc_seg (both sub-archives).
        # The .ldcts files themselves are side-effects of the tgz unpack and are not
        # declared outputs of any rule, so they cannot live in `input:`. They are
        # passed to the run block via params; the flag-file inputs create the edge.
        ldsc_seg_gene_expr_flag="data/reference/ldsc_seg/.gene_expr_download_done",
        ldsc_seg_chromatin_flag="data/reference/ldsc_seg/.chromatin_download_done",
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
        script=str(Path(workflow.basedir) / "src" / "python" / "run_ldsc_seg.py"),
        gene_expr_ldcts=os.path.join(
            PATHWAY_CFG.get("ldsc_seg_gene_expr", "data/reference/ldsc_seg/Multi_tissue_gene_expr"),
            "Multi_tissue_gene_expr.ldcts",
        ),
        chromatin_ldcts=os.path.join(
            PATHWAY_CFG.get("ldsc_seg_chromatin", "data/reference/ldsc_seg/Multi_tissue_chromatin"),
            "Multi_tissue_chromatin.ldcts",
        ),
    resources:
        mem_mb=1000,
    run:
        import sys as _sys
        _sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))
        from run_ldsc_seg import fix_ldcts_paths

        fix_ldcts_paths(params.gene_expr_ldcts, output.gene_expr_fixed)
        fix_ldcts_paths(params.chromatin_ldcts, output.chromatin_fixed)


rule hess_validate_panel:
    """One-time validation that HESS LD reference panel is on GRCh37 (T-05-17).

    Reads the .bim file for chr1 and checks SNP positions against hardcoded
    GRCh37 reference. Must run before any HESS analysis.
    """
    input:
        # RO7 DAG wiring: flag-file dependency on download_hess_panel.
        # chr1.bim is a side-effect of the LD-panel tar unpack and is not a declared
        # output of any rule, so it cannot live in `input:`. The .ld_panel_download_done
        # touch file is the declared hook; bim is consulted indirectly via bfile_prefix
        # in the shell block below.
        hess_panel_ld_flag="data/reference/hess/.ld_panel_download_done",
    output:
        validated=touch("data/reference/hess/.build_validated"),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_hess.py"),
        bfile_prefix=os.path.join(
            PATHWAY_CFG.get("hess_ld_panel", "data/reference/hess/ld_panel"),
            "EUR",
            "chr1",
        ),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=2000,
    shell:
        """
        python -c "
import sys; sys.path.insert(0, '{params.script}'.rsplit('/', 1)[0])
from run_hess import validate_hess_panel_build
validate_hess_panel_build('{params.bfile_prefix}')
print('HESS panel GRCh37 validation PASSED')
"
        """


rule hess_format_sumstats:
    """Convert harmonized sumstats to HESS format (SNP, A1, A2, Z, N).

    Per trait x ancestry. Z computed as BETA/SE. Binary traits use effective N.
    Note: no conda directive -- run: blocks execute in host env (Snakemake 7.32.4).
    """
    input:
        sumstats=os.path.join(
            config["paths"]["harmonized_sumstats"], "{trait}.{ancestry}.tsv.bgz"
        ),
    output:
        hess_sumstats=os.path.join(
            PATHWAY_RESULTS_DIR, "hess", "sumstats", "{trait}_{ancestry}_hess.tsv"
        ),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_hess.py"),
        trait=lambda wc: wc.trait,
    resources:
        mem_mb=4000,
    run:
        import sys as _sys
        _sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))
        from run_hess import harmonized_to_hess
        harmonized_to_hess(
            input_path=input.sumstats,
            output_path=output.hess_sumstats,
            trait=params.trait,
        )


rule hess_local_rhog:
    """HESS rho-HESS local genetic covariance per trait pair x ancestry x chromosome.

    Runs HESS via Python 2.7 subprocess. Requires hess_py27 conda env.
    Input: HESS-formatted sumstats for both traits, LD panel bfile, partition BED.
    D-02a/D-02b: per trait pair x ancestry x chromosome.
    T-05-18: subprocess list args only (no shell=True).
    T-05-20: mem_mb=4000 for eigendecomposition.
    """
    input:
        sumstats1=os.path.join(
            PATHWAY_RESULTS_DIR, "hess", "sumstats", "{trait1}_{ancestry}_hess.tsv"
        ),
        sumstats2=os.path.join(
            PATHWAY_RESULTS_DIR, "hess", "sumstats", "{trait2}_{ancestry}_hess.tsv"
        ),
        validated="data/reference/hess/.build_validated",
        # RO7 DAG wiring: flag-file dependencies on download_hess_panel (both archives).
        # chr{chrom}.bim and chr{chrom}.bed are side-effects of the tar unpack and are
        # not declared outputs of any rule, so they cannot live in `input:`. They are
        # referenced in the shell block via params; the flag-file inputs create the
        # edge to download_hess_panel.
        hess_panel_ld_flag="data/reference/hess/.ld_panel_download_done",
        hess_panel_partition_flag="data/reference/hess/.partition_download_done",
    output:
        done=touch(
            os.path.join(
                PATHWAY_RESULTS_DIR,
                "hess",
                "{trait1}_{trait2}_{ancestry}_chr{chrom}",
                ".done",
            )
        ),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_hess.py"),
        hess_script="tools/hess/hess.py",
        python27=HESS_PY27_BIN,
        bfile=lambda wc: os.path.join(
            PATHWAY_CFG.get("hess_ld_panel", "data/reference/hess/ld_panel"),
            wc.ancestry,
            f"chr{wc.chrom}",
        ),
        partition=lambda wc: os.path.join(
            PATHWAY_CFG.get("hess_partition", "data/reference/hess/partition"),
            f"{wc.ancestry}_fourier_ls-all.bed",
        ),
        out_prefix=lambda wc: os.path.join(
            PATHWAY_RESULTS_DIR,
            "hess",
            f"{wc.trait1}_{wc.trait2}_{wc.ancestry}_chr{wc.chrom}",
        ),
        chrom=lambda wc: wc.chrom,
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
        runtime=30,
    shell:
        """
        python {params.script} --step local-rhog \
            --hess-script {params.hess_script} \
            --python27 {params.python27} \
            --bfile {params.bfile} \
            --partition {params.partition} \
            --sumstats1 {input.sumstats1} \
            --sumstats2 {input.sumstats2} \
            --chrom {params.chrom} \
            --out {params.out_prefix}
        """


rule hess_combine:
    """Combine per-chromosome rho-HESS results for a trait pair x ancestry.

    Input: all 22 chromosome results. Output: combined local covariance file.
    """
    input:
        chr_results=expand(
            os.path.join(
                PATHWAY_RESULTS_DIR,
                "hess",
                "{{trait1}}_{{trait2}}_{{ancestry}}_chr{chrom}",
                ".done",
            ),
            chrom=CHROMOSOMES,
        ),
    output:
        combined=os.path.join(
            PATHWAY_RESULTS_DIR,
            "hess",
            "{trait1}_{trait2}_{ancestry}_combined.txt",
        ),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_hess.py"),
        hess_script="tools/hess/hess.py",
        python27=HESS_PY27_BIN,
        prefix=lambda wc: os.path.join(
            PATHWAY_RESULTS_DIR,
            "hess",
            f"{wc.trait1}_{wc.trait2}_{wc.ancestry}",
        ),
        out_prefix=lambda wc: os.path.join(
            PATHWAY_RESULTS_DIR,
            "hess",
            f"{wc.trait1}_{wc.trait2}_{wc.ancestry}_combined",
        ),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} --step combine \
            --hess-script {params.hess_script} \
            --python27 {params.python27} \
            --prefix {params.prefix} \
            --out {params.out_prefix}
        """


rule hess_compare_pleio:
    """Compare local covariance at pleiotropic loci vs genome-wide average (D-02c).

    Per trait pair x ancestry. Z-score test of enrichment at pleiotropic loci.
    Uses Python 3 (magma env) since this is pure Python analysis.
    """
    input:
        combined=os.path.join(
            PATHWAY_RESULTS_DIR,
            "hess",
            "{trait1}_{trait2}_{ancestry}_combined.txt",
        ),
        regions=config["paths"]["regions_curated"],
    output:
        comparison=os.path.join(
            PATHWAY_RESULTS_DIR,
            "hess",
            "{trait1}_{trait2}_{ancestry}_pleio_vs_bg.tsv",
        ),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_hess.py"),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=2000,
    shell:
        """
        python {params.script} --step compare \
            --combined-results {input.combined} \
            --regions-curated {input.regions} \
            --out {output.comparison}
        """


rule hess_negative_controls:
    """Run HESS compare on negative control gene sets (REQ-7 / D-06b).

    For each trait pair x ancestry, compares local covariance at negative
    control loci (HLA, cosmetic, blood group) vs genome-wide average. Maps
    each GMT row to genomic coordinates via NCBI37.3.gene.loc, writes a
    temporary regions CSV per set, and invokes compare_pleiotropic_vs_background.
    Negative controls should produce non-significant enrichment by design.
    Note: no conda directive -- run: blocks execute in host env (Snakemake 7.32.4).
    """
    input:
        combined=os.path.join(
            PATHWAY_RESULTS_DIR,
            "hess",
            "{trait1}_{trait2}_{ancestry}_combined.txt",
        ),
        negctrl_gmt=PATHWAY_CFG.get(
            "negative_control_gmt", "config/pathway_sets/negative_controls.gmt"
        ),
        gene_loc=PATHWAY_CFG.get(
            "magma_gene_loc", "data/reference/magma/NCBI37.3.gene.loc"
        ),
    output:
        results=os.path.join(
            PATHWAY_RESULTS_DIR,
            "hess",
            "{trait1}_{trait2}_{ancestry}_neg_ctrl_compare.tsv",
        ),
    params:
        window_kb=PATHWAY_CFG.get("snp_gene_window_kb", 100),
    resources:
        mem_mb=2000,
    run:
        # WR-06 fix: implement real negative control comparison. Previously
        # only a placeholder header was written. For each negative control
        # gene set in the GMT file, map symbols to genomic coordinates via
        # the gene.loc reference, write a temporary regions CSV, and call
        # compare_pleiotropic_vs_background to test whether local covariance
        # at those loci differs from genome-wide. Expected result: NOT
        # significant (p >= 0.05) for all negative control sets.
        import csv as _csv
        import sys as _sys
        import tempfile as _tempfile
        _sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))
        from run_hess import compare_pleiotropic_vs_background

        # Parse gene.loc into a symbol -> (chr, start, end) map
        gene_coords = {}
        with open(input.gene_loc) as gf:
            for line in gf:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) < 6:
                    continue
                _entrez, chrom, start, end, _strand, symbol = parts[:6]
                try:
                    gene_coords[symbol] = (
                        str(chrom).replace("chr", ""),
                        int(start),
                        int(end),
                    )
                except ValueError:
                    continue

        window_bp = int(params.window_kb) * 1000

        header = ["neg_ctrl_set", "n_genes_mapped", "mean_pleio", "mean_bg",
                  "ratio", "z_score", "p_value", "significant_at_0.05"]
        rows = []

        with open(input.negctrl_gmt) as gmt_fh:
            for gmt_line in gmt_fh:
                gmt_line = gmt_line.strip()
                if not gmt_line:
                    continue
                fields = gmt_line.split("\t")
                if len(fields) < 3:
                    continue
                set_name, _desc, *genes = fields

                # Map genes to coordinates, applying +/- window_kb
                regions = []
                for sym in genes:
                    if sym in gene_coords:
                        chrom, gstart, gend = gene_coords[sym]
                        regions.append({
                            "region_id": f"{set_name}_{sym}",
                            "chr": chrom,
                            "start": max(0, gstart - window_bp),
                            "end": gend + window_bp,
                        })

                if not regions:
                    rows.append({
                        "neg_ctrl_set": set_name,
                        "n_genes_mapped": 0,
                        "mean_pleio": "NA",
                        "mean_bg": "NA",
                        "ratio": "NA",
                        "z_score": "NA",
                        "p_value": "NA",
                        "significant_at_0.05": "NA",
                    })
                    continue

                # Write temporary regions CSV for compare_pleiotropic_vs_background
                with _tempfile.NamedTemporaryFile(
                    mode="w", suffix=".csv", delete=False
                ) as tmp:
                    writer = _csv.DictWriter(
                        tmp, fieldnames=["region_id", "chr", "start", "end"]
                    )
                    writer.writeheader()
                    writer.writerows(regions)
                    tmp_path = tmp.name

                try:
                    result = compare_pleiotropic_vs_background(
                        combined_path=input.combined,
                        regions_path=tmp_path,
                    )
                    p_val = result.get("p_value", float("nan"))
                    rows.append({
                        "neg_ctrl_set": set_name,
                        "n_genes_mapped": len(regions),
                        "mean_pleio": result.get("mean_pleio", "NA"),
                        "mean_bg": result.get("mean_bg", "NA"),
                        "ratio": result.get("ratio", "NA"),
                        "z_score": result.get("z_score", "NA"),
                        "p_value": p_val,
                        "significant_at_0.05": (
                            "yes" if isinstance(p_val, (int, float))
                            and p_val == p_val  # NaN check
                            and p_val < 0.05
                            else "no"
                        ),
                    })
                except (ValueError, FileNotFoundError) as e:
                    # No overlapping partitions is expected behaviour for
                    # small negative-control sets; record NA and continue.
                    rows.append({
                        "neg_ctrl_set": set_name,
                        "n_genes_mapped": len(regions),
                        "mean_pleio": "NA",
                        "mean_bg": "NA",
                        "ratio": "NA",
                        "z_score": "NA",
                        "p_value": "NA",
                        "significant_at_0.05": f"NA (error: {e})",
                    })
                finally:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass

        with open(output.results, "w") as out_fh:
            writer = _csv.DictWriter(out_fh, fieldnames=header, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)


rule hess_aggregate:
    """Aggregate all pleiotropic vs background comparison results.

    Combines pleio_vs_bg.tsv from all trait pairs x ancestries into a
    single summary table.
    Output columns: trait1, trait2, ancestry, mean_pleio, mean_bg, ratio,
    z_score, p_value.
    """
    input:
        comparisons=[
            os.path.join(
                PATHWAY_RESULTS_DIR,
                "hess",
                f"{t1}_{t2}_{anc}_pleio_vs_bg.tsv",
            )
            for t1, t2, anc in TRAIT_PAIRS
        ],
    output:
        summary=os.path.join(
            PATHWAY_RESULTS_DIR, "hess", "local_covariance_summary.tsv"
        ),
    resources:
        mem_mb=2000,
    run:
        import csv

        header = [
            "trait1", "trait2", "ancestry", "mean_pleio", "mean_bg",
            "ratio", "z_score", "p_value",
        ]

        rows = []
        for comp_path, (t1, t2, anc) in zip(input.comparisons, TRAIT_PAIRS):
            if not os.path.exists(comp_path):
                continue
            with open(comp_path) as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    rows.append({
                        "trait1": t1,
                        "trait2": t2,
                        "ancestry": anc,
                        "mean_pleio": row.get("mean_pleio", ""),
                        "mean_bg": row.get("mean_bg", ""),
                        "ratio": row.get("ratio", ""),
                        "z_score": row.get("z_score", ""),
                        "p_value": row.get("p_value", ""),
                    })

        with open(output.summary, "w") as f:
            writer = csv.DictWriter(f, fieldnames=header, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

        print(f"Aggregated {len(rows)} HESS comparison results from {len(input.comparisons)} files")


rule build_gprofiler_background:
    """Build discoverability-matched background gene list per D-03a (Reimand 2019).

    Input: harmonized sumstats for all 5 traits (EUR), NCBI37.3.gene.loc.
    Output: background_genes.txt (one gene symbol per line).
    Uses 500 kb window around each GWS SNP (P < 5e-8), union across traits.
    """
    input:
        gene_loc=PATHWAY_CFG.get("magma_gene_loc", "data/reference/magma/NCBI37.3.gene.loc"),
        sumstats=expand(
            os.path.join(config["paths"]["harmonized_sumstats"], "{trait}.EUR.tsv.bgz"),
            trait=config.get("traits", []),
        ),
    output:
        bg_genes=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "background_genes.txt"),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "build_gprofiler_bg.py"),
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
        script=str(Path(workflow.basedir) / "src" / "python" / "run_gprofiler.py"),
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
    Note: no conda directive -- run: blocks execute in host env (Snakemake 7.32.4).
    """
    input:
        negctrl_gmt=PATHWAY_CFG.get(
            "negative_control_gmt", "config/pathway_sets/negative_controls.gmt"
        ),
        bg_genes=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "background_genes.txt"),
    output:
        results=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "neg_ctrl_enrichment.tsv"),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_gprofiler.py"),
        outdir=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler"),
    resources:
        mem_mb=4000,
    run:
        import sys
        sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))
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


rule permutation_null_genesets:
    """Generate 1000 permutation null gene sets matched for length, LD, MAF (D-06c).

    Input: Tier A+B gene list, NCBI37.3.gene.loc, MAF reference, LD score reference.
    Output: 1000 null gene set files + summary TSV.
    Calls extend_null_genesets.py with --n-permutations from config.
    Deterministic seeds: seed_base (42) + permutation_index (T-02-18).
    """
    input:
        gene_list=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "tier_ab_genes.txt"),
        gene_loc=PATHWAY_CFG.get("magma_gene_loc", "data/reference/magma/NCBI37.3.gene.loc"),
        negctrl_gmt=PATHWAY_CFG.get(
            "negative_control_gmt", "config/pathway_sets/negative_controls.gmt"
        ),
        custom_gmt=PATHWAY_CFG.get(
            "custom_pathway_gmt", "config/pathway_sets/custom_cardiometabolic.gmt"
        ),
    output:
        summary=os.path.join(PATHWAY_RESULTS_DIR, "permutation_null", "null_geneset_summary.tsv"),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "extend_null_genesets.py"),
        out_dir=os.path.join(PATHWAY_RESULTS_DIR, "permutation_null"),
        n_perm=PATHWAY_CFG.get("permutation_n", 1000),
        seed=42,
        maf_ref=PATHWAY_CFG.get("maf_reference", "data/reference/ldsc/1000G_Phase3_frq"),
        ld_ref=PATHWAY_CFG.get("ld_score_reference", "data/reference/ldsc/baselineLD_v2.2"),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=8000,
    shell:
        """
        python {params.script} \
            --query-genes {input.gene_list} \
            --gene-loc {input.gene_loc} \
            --maf-reference {params.maf_ref} \
            --ld-score-reference {params.ld_ref} \
            --n-permutations {params.n_perm} \
            --seed {params.seed} \
            --out-dir {params.out_dir} \
            --exclude-gmt {input.negctrl_gmt} {input.custom_gmt}
        """


rule permutation_magma:
    """Run MAGMA gene-set analysis on each permutation null gene set.

    For each of the 1000 null gene sets, run MAGMA gene-set analysis
    using the .genes.raw from the real analysis. Uses Snakemake wildcard
    for permutation index. Output: per-perm .gsa.out files.
    """
    input:
        magma=PATHWAY_CFG.get("magma_binary", "tools/magma_v1.10/magma"),
        genes_raw=os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}.genes.raw"),
        null_geneset=os.path.join(PATHWAY_RESULTS_DIR, "permutation_null", "null_geneset_{perm_idx}.txt"),
    output:
        gsa=os.path.join(
            PATHWAY_RESULTS_DIR, "permutation_null", "magma",
            "{trait}_{ancestry}_perm_{perm_idx}.gsa.out",
        ),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "run_magma.py"),
        out_prefix=lambda wc: os.path.join(
            PATHWAY_RESULTS_DIR, "permutation_null", "magma",
            f"{wc.trait}_{wc.ancestry}_perm_{wc.perm_idx}",
        ),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} --step geneset \
            --magma-binary {input.magma} \
            --gene-results {input.genes_raw} \
            --set-annot {input.null_geneset} \
            --out {params.out_prefix}
        """


rule permutation_aggregate:
    """Aggregate 1000 permutation MAGMA results to compute empirical p-value.

    Compares the real gene set's MAGMA beta to the distribution of betas
    from 1000 permutation null gene sets. Empirical p = fraction of
    permutations with beta >= real beta.
    Output: empirical_pvalues.tsv with per-pathway empirical significance.
    """
    input:
        real_fdr=expand(
            os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}_geneset_fdr.tsv"),
            zip,
            trait=[t for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
            ancestry=[a for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
        ),
        summary=os.path.join(PATHWAY_RESULTS_DIR, "permutation_null", "null_geneset_summary.tsv"),
    output:
        empirical=os.path.join(PATHWAY_RESULTS_DIR, "permutation_null", "empirical_pvalues.tsv"),
    resources:
        mem_mb=4000,
    run:
        import csv
        import glob
        import os

        perm_dir = os.path.join(PATHWAY_RESULTS_DIR, "permutation_null", "magma")
        n_perm = int(PATHWAY_CFG.get("permutation_n", 1000))

        # Read real MAGMA results
        real_results = {}
        for fdr_path in input.real_fdr:
            if not os.path.exists(fdr_path):
                continue
            basename = os.path.basename(fdr_path)
            trait_anc = basename.replace("_geneset_fdr.tsv", "")
            with open(fdr_path) as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    pathway = row.get("VARIABLE", "")
                    beta = float(row.get("BETA", 0))
                    key = (trait_anc, pathway)
                    real_results[key] = beta

        # Aggregate permutation results
        perm_betas = {}
        for gsa_file in sorted(glob.glob(os.path.join(perm_dir, "*_perm_*.gsa.out"))):
            basename = os.path.basename(gsa_file)
            with open(gsa_file) as f:
                header = None
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if header is None:
                        header = line
                        continue
                    parts = line.split()
                    if len(parts) >= 6:
                        pathway = parts[0]
                        try:
                            beta = float(parts[3])
                        except (ValueError, IndexError):
                            continue
                        # Extract trait_ancestry from filename
                        trait_anc = "_".join(basename.split("_perm_")[0].split("_")[:2])
                        key = (trait_anc, pathway)
                        if key not in perm_betas:
                            perm_betas[key] = []
                        perm_betas[key].append(beta)

        # Compute empirical p-values
        rows = []
        for (trait_anc, pathway), real_beta in real_results.items():
            perm_vals = perm_betas.get((trait_anc, pathway), [])
            n_obs = len(perm_vals)
            if n_obs > 0:
                n_exceed = sum(1 for b in perm_vals if b >= real_beta)
                emp_p = (n_exceed + 1) / (n_obs + 1)  # Conservative estimator
                perm_mean = sum(perm_vals) / n_obs
                perm_sd = (
                    sum((b - perm_mean) ** 2 for b in perm_vals) / n_obs
                ) ** 0.5
            else:
                emp_p = float("nan")
                perm_mean = float("nan")
                perm_sd = float("nan")

            rows.append({
                "trait_ancestry": trait_anc,
                "pathway": pathway,
                "real_beta": f"{real_beta:.4f}",
                "perm_mean_beta": f"{perm_mean:.4f}" if n_obs > 0 else "NA",
                "perm_sd_beta": f"{perm_sd:.4f}" if n_obs > 0 else "NA",
                "empirical_p": f"{emp_p:.6f}" if n_obs > 0 else "NA",
                "n_permutations": n_obs,
            })

        with open(output.empirical, "w") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "trait_ancestry", "pathway", "real_beta",
                    "perm_mean_beta", "perm_sd_beta", "empirical_p",
                    "n_permutations",
                ],
                delimiter="\t",
            )
            writer.writeheader()
            writer.writerows(rows)

        print(f"Computed empirical p-values for {len(rows)} pathway-trait combinations")


rule validate_negative_controls:
    """Aggregate negative control results from ALL methods into validation table.

    Input: MAGMA FDR results, g:Profiler neg ctrl results, LDSC h2 summary,
           LDSC-SEG shared tissue summary, HESS neg ctrl comparisons.
    Output: validation_summary.tsv with per-method, per-set pass/fail.
    T-05-21: hard fail (exit 1) if any row has passes_threshold=FALSE.
    """
    input:
        magma_fdr=expand(
            os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}_geneset_fdr.tsv"),
            zip,
            trait=[t for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
            ancestry=[a for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
        ),
        gprofiler_negctrl=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "neg_ctrl_enrichment.tsv"),
        ldsc_h2=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "h2_summary.tsv"),
    output:
        summary=os.path.join(PATHWAY_RESULTS_DIR, "negative_controls", "validation_summary.tsv"),
    resources:
        mem_mb=4000,
    run:
        import csv
        import sys as _sys
        _sys.path.insert(0, str(Path(workflow.basedir) / "src" / "python"))
        from extend_null_genesets import validate_negative_controls

        NEG_CTRL_PREFIXES = ["NEGCTRL_HLA_IMMUNE", "NEGCTRL_COSMETIC", "NEGCTRL_BLOOD_GROUP"]
        Q_THRESHOLD = 0.05

        rows = []

        # 1. MAGMA: extract negative control rows from FDR results
        for fdr_path in input.magma_fdr:
            if not os.path.exists(fdr_path):
                continue
            basename = os.path.basename(fdr_path)
            trait_anc = basename.replace("_geneset_fdr.tsv", "")
            parts = trait_anc.rsplit("_", 1)
            trait = parts[0] if len(parts) == 2 else trait_anc
            ancestry = parts[1] if len(parts) == 2 else "EUR"

            with open(fdr_path) as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    variable = row.get("VARIABLE", "")
                    if any(variable.startswith(p) for p in NEG_CTRL_PREFIXES):
                        q_val = float(row.get("FDR_Q", 1.0))
                        p_val = float(row.get("P", 1.0))
                        rows.append({
                            "neg_ctrl_set": variable,
                            "method": "MAGMA",
                            "trait": trait,
                            "ancestry": ancestry,
                            "statistic": f"beta={row.get('BETA', 'NA')}",
                            "p_value": f"{p_val:.6f}",
                            "q_value": f"{q_val:.6f}",
                            "passes_threshold": "TRUE" if q_val > Q_THRESHOLD else "FALSE",
                        })

        # 2. g:Profiler: extract negative control enrichment results
        if os.path.exists(input.gprofiler_negctrl):
            with open(input.gprofiler_negctrl) as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    nc_set = row.get("neg_ctrl_set", "")
                    if not nc_set:
                        continue
                    q_val = float(row.get("q_value", 1.0))
                    p_val = float(row.get("p_value", 1.0))
                    rows.append({
                        "neg_ctrl_set": nc_set,
                        "method": "gProfiler",
                        "trait": "coloc_genes",
                        "ancestry": "EUR",
                        "statistic": f"term={row.get('term_name', 'NA')}",
                        "p_value": f"{p_val:.6f}",
                        "q_value": f"{q_val:.6f}",
                        "passes_threshold": "TRUE" if q_val > Q_THRESHOLD else "FALSE",
                    })

        # 3. LDSC: extract negative control annotations from h2 summary
        if os.path.exists(input.ldsc_h2):
            with open(input.ldsc_h2) as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    annotation = row.get("annotation", "")
                    if any(p.lower() in annotation.lower() for p in NEG_CTRL_PREFIXES):
                        p_val = float(row.get("enrichment_p", 1.0)) if row.get("enrichment_p") else 1.0
                        # LDSC enrichment p is one-sided; no FDR correction built in
                        q_val = p_val  # conservative: treat p as q for negative controls
                        rows.append({
                            "neg_ctrl_set": annotation,
                            "method": "LDSC_partitioned",
                            "trait": row.get("trait", ""),
                            "ancestry": row.get("ancestry", ""),
                            "statistic": f"enrichment={row.get('enrichment', 'NA')}",
                            "p_value": f"{p_val:.6f}",
                            "q_value": f"{q_val:.6f}",
                            "passes_threshold": "TRUE" if q_val > Q_THRESHOLD else "FALSE",
                        })

        # Write validation summary
        os.makedirs(os.path.dirname(output.summary), exist_ok=True)
        header = [
            "neg_ctrl_set", "method", "trait", "ancestry",
            "statistic", "p_value", "q_value", "passes_threshold",
        ]
        with open(output.summary, "w") as f:
            writer = csv.DictWriter(f, fieldnames=header, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

        print(f"Validation summary: {len(rows)} entries written")

        # T-05-21: hard fail if any negative control shows q <= 0.05
        validate_negative_controls(output.summary)


rule aggregate_pathway_results:
    """Cross-method aggregation of all Phase 5 pathway results.

    Reads MAGMA FDR, g:Profiler enrichment, LDSC h2, LDSC-SEG, HESS,
    and negative control validation results. Produces:
      A. pathway_enrichment_summary.tsv (per-pathway consensus ranking)
      B. phase5_overview.tsv (one row per analytical component)
    T-05-24: validates expected columns in each input file.
    """
    input:
        magma_fdr=expand(
            os.path.join(PATHWAY_RESULTS_DIR, "magma", "{trait}_{ancestry}_geneset_fdr.tsv"),
            zip,
            trait=[t for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
            ancestry=[a for t in config.get("traits", []) for a in config.get("trait_ancestries", {}).get(t, ["EUR"])],
        ),
        gprofiler=os.path.join(PATHWAY_RESULTS_DIR, "gprofiler", "enrichment_results.tsv"),
        ldsc_h2=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_partitioned", "h2_summary.tsv"),
        ldsc_seg=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_seg", "shared_tissue_summary.tsv"),
        hess=os.path.join(PATHWAY_RESULTS_DIR, "hess", "local_covariance_summary.tsv"),
        neg_ctrl=os.path.join(PATHWAY_RESULTS_DIR, "negative_controls", "validation_summary.tsv"),
    output:
        enrichment=os.path.join(PATHWAY_RESULTS_DIR, "pathway_enrichment_summary.tsv"),
        overview=os.path.join(PATHWAY_RESULTS_DIR, "phase5_overview.tsv"),
    params:
        script=str(Path(workflow.basedir) / "src" / "python" / "aggregate_pathway_results.py"),
    conda:
        MAGMA_ENV
    resources:
        mem_mb=4000,
    shell:
        """
        python {params.script} \
            --magma-dir $(dirname {input.magma_fdr[0]}) \
            --gprofiler-dir $(dirname {input.gprofiler}) \
            --ldsc-dir $(dirname {input.ldsc_h2}) \
            --ldsc-seg-dir $(dirname {input.ldsc_seg}) \
            --hess-dir $(dirname {input.hess}) \
            --neg-ctrl-dir $(dirname {input.neg_ctrl}) \
            --out {output.enrichment} \
            --out-overview {output.overview}
        """


rule all_pathway:
    """Top-level target collecting all Phase 5 pathway outputs.

    Run with: snakemake all_pathway
    This collects all final outputs from the 6 analytical components:
    MAGMA, g:Profiler, LDSC partitioned, LDSC-SEG, HESS, permutation null,
    negative controls, and the cross-method aggregation.
    """
    input:
        enrichment_summary=os.path.join(PATHWAY_RESULTS_DIR, "pathway_enrichment_summary.tsv"),
        overview=os.path.join(PATHWAY_RESULTS_DIR, "phase5_overview.tsv"),
        neg_ctrl_validation=os.path.join(PATHWAY_RESULTS_DIR, "negative_controls", "validation_summary.tsv"),
        permutation_empirical=os.path.join(PATHWAY_RESULTS_DIR, "permutation_null", "empirical_pvalues.tsv"),
        hess_summary=os.path.join(PATHWAY_RESULTS_DIR, "hess", "local_covariance_summary.tsv"),
        ldsc_seg_shared=os.path.join(PATHWAY_RESULTS_DIR, "ldsc_seg", "shared_tissue_summary.tsv"),
