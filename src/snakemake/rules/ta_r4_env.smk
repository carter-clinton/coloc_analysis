"""ta-r4 job-environment probes: solve each pinned env once and record its tool versions."""

R4_ENV_PROBES = ("plink", "qtl_processing", "python_stats")


rule r4_env_probe_plink:
    output: "data/r4/logs/env_probe/plink.txt"
    conda: str(Path(workflow.basedir) / "envs" / "plink.yml")
    shell: "(command -v plink; plink --version; plink2 --version; bcftools --version | head -1) > {output}"


rule r4_env_probe_qtl_processing:
    output: "data/r4/logs/env_probe/qtl_processing.txt"
    conda: str(Path(workflow.basedir) / "envs" / "qtl_processing.yml")
    shell:
        "(command -v python; python -c 'import sys,pysam,pandas,pyliftover;"
        "print(sys.version.split()[0], pysam.__version__, pandas.__version__)'; tabix --version | head -1) > {output}"


rule r4_env_probe_python_stats:
    output: "data/r4/logs/env_probe/python_stats.txt"
    conda: str(Path(workflow.basedir) / "envs" / "python_stats.yml")
    shell:
        "(command -v python; python -c 'import sys,numpy,pandas,scipy;"
        "print(sys.version.split()[0], numpy.__version__, pandas.__version__, scipy.__version__)';"
        " snakemake --version) > {output}"


rule r4_env_probe_all:
    input: expand("data/r4/logs/env_probe/{name}.txt", name=R4_ENV_PROBES)
    output: touch("data/r4/logs/env_probe/all.ok")
