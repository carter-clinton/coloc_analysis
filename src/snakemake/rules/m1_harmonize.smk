"""M1 Wave 2a — continuous-trait harmonizer rules.

Plan: m1-02a-harmonizers-continuous-traits. Authors four families of
harmonize-as-ready rules (D-14):

* harmonize_yengo : 4 codepaths — yengo2018, loh2022_eur, loh2022_afr, page2019_afr
* harmonize_glgc  : 15 cells (LDL × 6 ancestries + HDL/TG/TC × 3 ancestries)
* harmonize_wuttke: 3 codepaths — wuttke2019_trans, wuttke2019_eur, morris2019_afr
* harmonize_magic : 6 ancestries — TRANS / EUR / AFR / EAS / SAS / HIS

Each rule emits dual artifacts per D-09 (.tsv.bgz + .tbi + .parquet)
plus a .qc.json sidecar. D-16 filename convention:
``<trait>.<ancestry>.<consortium>.<year>.GRCh37.<ext>``.

W8 fix (option A — universal ``.deferred`` guard): the params lambda
calls ``m1_raw_glob.resolve_raw_for`` which returns
``DEFERRED_SENTINEL == "__DEFERRED__"`` when an upstream ``.deferred``
marker is present in the resolved target_dir. Each shell prelude
branches on that string and emits its own ``.deferred`` output marker
without invoking the harmonizer body. This single choke-point closes
Loh-EUR, Loh-AFR (PENDING_D01_ACCESSION sentinels from m1-01 N1 fix),
AND any future PENDING_* deferral path symmetrically.

Path-parameterization (REQ-PATH-PARAMETERIZATION): every disk path is
resolved through ``config["paths"]["raw_sumstats_v2"]``,
``config["paths"]["harmonized_sumstats"]``, and
``config["paths"]["harmonized_parquet"]``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project-root + src/python discovery (so resolve_raw_for is importable from
# the rule's params lambda regardless of how Snakemake is invoked).
# ---------------------------------------------------------------------------
try:
    _BASE = Path(workflow.basedir)  # type: ignore[name-defined]
except NameError:
    _BASE = Path(os.getcwd())


def _find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(6):
        if (cur / "config" / "pipeline.yaml").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start


_PROJECT_ROOT = _find_project_root(_BASE)
_SRC_PYTHON = _PROJECT_ROOT / "src" / "python"
if str(_SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(_SRC_PYTHON))

from m1_raw_glob import resolve_raw_for, DEFERRED_SENTINEL  # noqa: E402

# Path-parameterized roots (config-driven; no absolute scratch paths).
try:
    _RAW = config["paths"]["raw_sumstats_v2"]            # type: ignore[name-defined]
    _HARM = config["paths"]["harmonized_sumstats"]       # type: ignore[name-defined]
    _PARQ = config["paths"]["harmonized_parquet"]        # type: ignore[name-defined]
    _QC = config["paths"]["qc_log"]                      # type: ignore[name-defined]
except (NameError, KeyError):
    _RAW = "data/raw/sumstats_v2"
    _HARM = "data/processed/sumstats_harmonized"
    _PARQ = "data/processed/sumstats_harmonized_parquet"
    _QC = "data/processed/sumstats_harmonized/qc_log"

CHAIN_B38_TO_B37 = "data/external/liftover/hg38ToHg19.over.chain.gz"

# Shared shell prelude — universal .deferred guard. Inserted at the top
# of every harmonize rule's shell body via Python f-string formatting.
_DEFERRED_GUARD = r"""
        if [ "{params.raw}" = "__DEFERRED__" ]; then
            mkdir -p $(dirname {output.tsv_bgz})
            touch {output.tsv_bgz}.deferred
            touch {output.tsv_bgz}
            touch {output.tbi}
            touch {output.parquet}
            mkdir -p $(dirname {output.qc_json})
            echo '{{"deferred": true}}' > {output.qc_json}
            echo "DEFERRED: upstream marker present"
            exit 0
        fi
"""


# ===========================================================================
# harmonize_yengo : Yengo 2018 GIANT+UKBB BMI EUR
# ===========================================================================

rule harmonize_yengo_bmi_eur:
    # No flag-file input: m1-01 fired downloads directly via
    # bin/download_sumstats_v2.sh so .download_complete sentinels do not
    # exist. resolve_raw_for() handles deferred routing via .deferred
    # marker -> DEFERRED_SENTINEL, which the universal guard catches.
    output:
        tsv_bgz=os.path.join(_HARM, "bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz"),
        tbi=os.path.join(_HARM, "bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz.tbi"),
        parquet=os.path.join(_PARQ, "bmi.EUR.GIANT-UKBB.2018.GRCh37.parquet"),
        qc_json=os.path.join(_QC, "bmi.EUR.GIANT-UKBB.2018.qc.json"),
    params:
        raw=lambda wc: resolve_raw_for("GIANT2018_BMI_EUR", "EUR"),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=8000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_yengo.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --variant yengo2018 \
            --trait bmi --ancestry EUR --consortium GIANT-UKBB --year 2018
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


rule harmonize_loh_bmi_eur:
    input:
        chain=CHAIN_B38_TO_B37,
    output:
        tsv_bgz=os.path.join(_HARM, "bmi.EUR.GIANT-23andMe.2022.GRCh37.tsv.bgz"),
        tbi=os.path.join(_HARM, "bmi.EUR.GIANT-23andMe.2022.GRCh37.tsv.bgz.tbi"),
        parquet=os.path.join(_PARQ, "bmi.EUR.GIANT-23andMe.2022.GRCh37.parquet"),
        qc_json=os.path.join(_QC, "bmi.EUR.GIANT-23andMe.2022.qc.json"),
    params:
        raw=lambda wc: resolve_raw_for("Loh2022_BMI_EUR", "EUR"),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=8000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_yengo.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --variant loh2022_eur \
            --chain {input.chain} \
            --trait bmi --ancestry EUR --consortium GIANT-23andMe --year 2022
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


rule harmonize_loh_bmi_afr:
    input:
        chain=CHAIN_B38_TO_B37,
    output:
        tsv_bgz=os.path.join(_HARM, "bmi.AFR.GIANT-23andMe.2022.GRCh37.tsv.bgz"),
        tbi=os.path.join(_HARM, "bmi.AFR.GIANT-23andMe.2022.GRCh37.tsv.bgz.tbi"),
        parquet=os.path.join(_PARQ, "bmi.AFR.GIANT-23andMe.2022.GRCh37.parquet"),
        qc_json=os.path.join(_QC, "bmi.AFR.GIANT-23andMe.2022.qc.json"),
    params:
        raw=lambda wc: resolve_raw_for("Loh2022_BMI_AFR", "AFR"),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=8000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_yengo.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --variant loh2022_afr \
            --chain {input.chain} \
            --trait bmi --ancestry AFR --consortium GIANT-23andMe --year 2022
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


rule harmonize_yengo_bmi_afr_page:
    """PAGE 2019 BMI-AFR (Wojcik) — variant=page2019_afr."""
    output:
        tsv_bgz=os.path.join(_HARM, "bmi.AFR.PAGE.2019.GRCh37.tsv.bgz"),
        tbi=os.path.join(_HARM, "bmi.AFR.PAGE.2019.GRCh37.tsv.bgz.tbi"),
        parquet=os.path.join(_PARQ, "bmi.AFR.PAGE.2019.GRCh37.parquet"),
        qc_json=os.path.join(_QC, "bmi.AFR.PAGE.2019.qc.json"),
    params:
        raw=lambda wc: resolve_raw_for("PAGE2019_BMI_AFR", "AFR"),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=8000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_yengo.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --variant page2019_afr \
            --trait bmi --ancestry AFR --consortium PAGE --year 2019
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


# ===========================================================================
# harmonize_glgc : 15 cells (LDL × 6 + HDL/TG/TC × 3 each)
# ===========================================================================
#
# GLGC inputs already landed pre-Wave-1 (no portal flag dependency). The
# wildcard rule pattern below resolves the raw input via a directory glob
# rather than the portal-manifest helper since GLGC is not in
# config/download_manifest_m1_portal.tsv.
# ---------------------------------------------------------------------------

GLGC_LIPIDS = ["LDL", "HDL", "TG", "TC"]
GLGC_ANCESTRIES = {
    "LDL": ["TRANS", "EUR", "AFR", "EAS", "SAS", "HIS"],  # 6
    "HDL": ["TRANS", "EUR", "AFR"],                       # 3
    "TG":  ["TRANS", "EUR", "AFR"],                       # 3
    "TC":  ["TRANS", "EUR", "AFR"],                       # 3
}


def _glgc_raw_glob(wildcards):
    """Resolve the single raw GLGC file under data/raw/sumstats_v2/GLGC2021/<lipid>/<ancestry>/."""
    d = Path(_RAW) / "GLGC2021" / wildcards.lipid / wildcards.ancestry
    if (d / ".deferred").exists():
        return DEFERRED_SENTINEL
    matches = sorted(d.glob("*.gz"))
    if len(matches) == 1:
        return str(matches[0])
    if len(matches) == 0:
        return DEFERRED_SENTINEL
    raise AssertionError(
        f"GLGC raw glob: expected exactly 1 file at {d}, found {len(matches)}: {matches}"
    )


rule harmonize_glgc_lipids:
    """Wildcard-expanded GLGC harmonizer for {lipid}.{ancestry}."""
    output:
        tsv_bgz=os.path.join(
            _HARM, "{lipid_lc}.{ancestry}.GLGC.2021.GRCh37.tsv.bgz"
        ),
        tbi=os.path.join(
            _HARM, "{lipid_lc}.{ancestry}.GLGC.2021.GRCh37.tsv.bgz.tbi"
        ),
        parquet=os.path.join(
            _PARQ, "{lipid_lc}.{ancestry}.GLGC.2021.GRCh37.parquet"
        ),
        qc_json=os.path.join(
            _QC, "{lipid_lc}.{ancestry}.GLGC.2021.qc.json"
        ),
    wildcard_constraints:
        lipid_lc="ldl|hdl|tg|tc",
        ancestry="TRANS|EUR|AFR|EAS|SAS|HIS",
    params:
        raw=lambda wc: _glgc_raw_glob(
            type("W", (), {"lipid": wc.lipid_lc.upper(),
                            "ancestry": wc.ancestry})()
        ),
        subtype=lambda wc: wc.lipid_lc.upper(),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=12000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_glgc.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --subtype {params.subtype} \
            --ancestry {wildcards.ancestry} \
            --consortium GLGC --year 2021
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


# Aggregate target: depend on every (lipid, ancestry) pair per D-04 fanout.
def _glgc_all_outputs() -> list[str]:
    out: list[str] = []
    for lipid in GLGC_LIPIDS:
        for anc in GLGC_ANCESTRIES[lipid]:
            out.append(os.path.join(
                _HARM, f"{lipid.lower()}.{anc}.GLGC.2021.GRCh37.tsv.bgz"
            ))
    return out


rule harmonize_glgc_all:
    input:
        _glgc_all_outputs(),


# ===========================================================================
# harmonize_wuttke : Wuttke 2019 TRANS + EUR; Morris 2019 AFR companion
# ===========================================================================

rule harmonize_wuttke_egfr_trans:
    output:
        tsv_bgz=os.path.join(_HARM, "egfr.TRANS.CKDGen.2019.GRCh37.tsv.bgz"),
        tbi=os.path.join(_HARM, "egfr.TRANS.CKDGen.2019.GRCh37.tsv.bgz.tbi"),
        parquet=os.path.join(_PARQ, "egfr.TRANS.CKDGen.2019.GRCh37.parquet"),
        qc_json=os.path.join(_QC, "egfr.TRANS.CKDGen.2019.qc.json"),
    params:
        raw=lambda wc: _wuttke_raw_glob("TRANS"),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=8000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_wuttke.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --variant wuttke2019_trans --ancestry TRANS \
            --consortium CKDGen --year 2019
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


rule harmonize_wuttke_egfr_eur:
    output:
        tsv_bgz=os.path.join(_HARM, "egfr.EUR.CKDGen.2019.GRCh37.tsv.bgz"),
        tbi=os.path.join(_HARM, "egfr.EUR.CKDGen.2019.GRCh37.tsv.bgz.tbi"),
        parquet=os.path.join(_PARQ, "egfr.EUR.CKDGen.2019.GRCh37.parquet"),
        qc_json=os.path.join(_QC, "egfr.EUR.CKDGen.2019.qc.json"),
    params:
        raw=lambda wc: _wuttke_raw_glob("EUR"),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=8000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_wuttke.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --variant wuttke2019_eur --ancestry EUR \
            --consortium CKDGen --year 2019
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


def _wuttke_raw_glob(ancestry: str) -> str:
    """Resolve the single Wuttke / Morris raw file."""
    d = Path(_RAW) / "CKDGen2019" / "eGFR" / ancestry
    if (d / ".deferred").exists():
        return DEFERRED_SENTINEL
    matches = sorted(d.glob("*.gz"))
    if len(matches) == 1:
        return str(matches[0])
    if len(matches) == 0:
        return DEFERRED_SENTINEL
    raise AssertionError(
        f"Wuttke raw glob: expected exactly 1 file at {d}, found {len(matches)}: {matches}"
    )


rule harmonize_morris_egfr_afr:
    """Morris 2019 AFR companion — same Wuttke header convention."""
    output:
        tsv_bgz=os.path.join(_HARM, "egfr.AFR.CKDGen.2019.GRCh37.tsv.bgz"),
        tbi=os.path.join(_HARM, "egfr.AFR.CKDGen.2019.GRCh37.tsv.bgz.tbi"),
        parquet=os.path.join(_PARQ, "egfr.AFR.CKDGen.2019.GRCh37.parquet"),
        qc_json=os.path.join(_QC, "egfr.AFR.CKDGen.2019.qc.json"),
    params:
        raw=lambda wc: _wuttke_raw_glob("AFR"),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=8000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_wuttke.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --variant morris2019_afr --ancestry AFR \
            --consortium CKDGen --year 2019
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


rule harmonize_wuttke_all:
    input:
        os.path.join(_HARM, "egfr.TRANS.CKDGen.2019.GRCh37.tsv.bgz"),
        os.path.join(_HARM, "egfr.EUR.CKDGen.2019.GRCh37.tsv.bgz"),
        os.path.join(_HARM, "egfr.AFR.CKDGen.2019.GRCh37.tsv.bgz"),


# ===========================================================================
# harmonize_magic : 6 ancestries (TRANS / EUR / AFR / EAS / SAS / HIS)
# ===========================================================================

MAGIC_ANCESTRIES = ["TRANS", "EUR", "AFR", "EAS", "SAS", "HIS"]


def _magic_raw_glob(ancestry: str) -> str:
    """Resolve the single MAGIC raw file under data/raw/sumstats_v2/MAGIC2021/HbA1c/<ancestry>/."""
    d = Path(_RAW) / "MAGIC2021" / "HbA1c" / ancestry
    if (d / ".deferred").exists():
        return DEFERRED_SENTINEL
    matches = sorted(d.glob("*.gz"))
    if len(matches) == 1:
        return str(matches[0])
    if len(matches) == 0:
        return DEFERRED_SENTINEL
    raise AssertionError(
        f"MAGIC raw glob: expected exactly 1 file at {d}, found {len(matches)}: {matches}"
    )


rule harmonize_magic_hba1c:
    """Wildcard-expanded MAGIC harmonizer; ancestry token resolves the raw file."""
    output:
        tsv_bgz=os.path.join(
            _HARM, "hba1c.{ancestry}.MAGIC.2021.GRCh37.tsv.bgz"
        ),
        tbi=os.path.join(
            _HARM, "hba1c.{ancestry}.MAGIC.2021.GRCh37.tsv.bgz.tbi"
        ),
        parquet=os.path.join(
            _PARQ, "hba1c.{ancestry}.MAGIC.2021.GRCh37.parquet"
        ),
        qc_json=os.path.join(
            _QC, "hba1c.{ancestry}.MAGIC.2021.qc.json"
        ),
    wildcard_constraints:
        ancestry="TRANS|EUR|AFR|EAS|SAS|HIS",
    params:
        raw=lambda wc: _magic_raw_glob(wc.ancestry),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=8000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_magic.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --ancestry {wildcards.ancestry} \
            --consortium MAGIC --year 2021
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


rule harmonize_magic_all:
    input:
        expand(
            os.path.join(_HARM, "hba1c.{ancestry}.MAGIC.2021.GRCh37.tsv.bgz"),
            ancestry=MAGIC_ANCESTRIES,
        ),


# ===========================================================================
# Aggregate Wave 2a target — every continuous-trait harmonizer output.
# ===========================================================================

rule m1_harmonize_continuous_all:
    input:
        # Yengo / Loh / PAGE BMI
        os.path.join(_HARM, "bmi.EUR.GIANT-UKBB.2018.GRCh37.tsv.bgz"),
        os.path.join(_HARM, "bmi.EUR.GIANT-23andMe.2022.GRCh37.tsv.bgz"),
        os.path.join(_HARM, "bmi.AFR.GIANT-23andMe.2022.GRCh37.tsv.bgz"),
        os.path.join(_HARM, "bmi.AFR.PAGE.2019.GRCh37.tsv.bgz"),
        # GLGC lipids
        _glgc_all_outputs(),
        # Wuttke / Morris eGFR
        os.path.join(_HARM, "egfr.TRANS.CKDGen.2019.GRCh37.tsv.bgz"),
        os.path.join(_HARM, "egfr.EUR.CKDGen.2019.GRCh37.tsv.bgz"),
        os.path.join(_HARM, "egfr.AFR.CKDGen.2019.GRCh37.tsv.bgz"),
        # MAGIC HbA1c
        expand(
            os.path.join(_HARM, "hba1c.{ancestry}.MAGIC.2021.GRCh37.tsv.bgz"),
            ancestry=MAGIC_ANCESTRIES,
        ),
    output:
        sentinel=os.path.join(_HARM, ".m1_harmonize_continuous_all.complete"),
    shell:
        "touch {output.sentinel}"


# ===========================================================================
# Wave 2b — case-control harmonizers
# ===========================================================================
#
# Plan reference: m1-02b-harmonizers-case-control-traits-PLAN.md.
# Each rule prepends the universal `_DEFERRED_GUARD` so when an upstream
# `.deferred` marker is present in the resolved target_dir, the rule
# emits its own `.deferred` placeholder + qc_json sentinel and exits 0.
# ---------------------------------------------------------------------------

# ===========================================================================
# harmonize_diamante : T2D × {TRANS, EUR, EAS, SAS} ; AFR/HIS DEFERRED
# ===========================================================================

DIAMANTE_RELEASED_ANCESTRIES = ["TRANS", "EUR", "EAS", "SAS"]
DIAMANTE_DEFERRED_ANCESTRIES = ["AFR", "HIS"]


rule harmonize_diamante_t2d:
    """Per-ancestry DIAMANTE T2D harmonizer for the released strata."""
    output:
        tsv_bgz=os.path.join(
            _HARM, "t2d.{ancestry}.DIAMANTE.2022.GRCh37.tsv.bgz"
        ),
        tbi=os.path.join(
            _HARM, "t2d.{ancestry}.DIAMANTE.2022.GRCh37.tsv.bgz.tbi"
        ),
        parquet=os.path.join(
            _PARQ, "t2d.{ancestry}.DIAMANTE.2022.GRCh37.parquet"
        ),
        qc_json=os.path.join(
            _QC, "t2d.{ancestry}.DIAMANTE.2022.qc.json"
        ),
    wildcard_constraints:
        ancestry="TRANS|EUR|EAS|SAS",
    params:
        raw=lambda wc: resolve_raw_for(
            f"DIAMANTE2022_T2D_{wc.ancestry}", wc.ancestry
        ),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=12000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_diamante.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --trait t2d --ancestry {wildcards.ancestry} \
            --consortium DIAMANTE --year 2022
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


rule harmonize_deferred_diamante_afr:
    """SUMSTATS-UPGRADE.tsv row 8: DIAMANTE AFR dua_pending."""
    output:
        deferred=os.path.join(
            _HARM, "t2d.AFR.DIAMANTE.2022.GRCh37.tsv.bgz.deferred"
        ),
    shell:
        r"""
        mkdir -p $(dirname {output.deferred})
        cat > {output.deferred} <<EOF
Status: DEFERRED
Trait: t2d, Ancestry: AFR, Consortium: DIAMANTE, Year: 2022
Reason: SUMSTATS-UPGRADE.tsv row 8 status=dua_pending; DIAGRAM gate on manuscript acceptance
Recheck: quarterly per m1-CONTEXT.md Deferred Ideas
EOF
        """


rule harmonize_deferred_diamante_his:
    """SUMSTATS-UPGRADE.tsv row 11: DIAMANTE HIS dua_pending."""
    output:
        deferred=os.path.join(
            _HARM, "t2d.HIS.DIAMANTE.2022.GRCh37.tsv.bgz.deferred"
        ),
    shell:
        r"""
        mkdir -p $(dirname {output.deferred})
        cat > {output.deferred} <<EOF
Status: DEFERRED
Trait: t2d, Ancestry: HIS, Consortium: DIAMANTE, Year: 2022
Reason: SUMSTATS-UPGRADE.tsv row 11 status=dua_pending; DIAGRAM gate on manuscript acceptance
Recheck: quarterly per m1-CONTEXT.md Deferred Ideas
EOF
        """


rule harmonize_diamante_all:
    input:
        expand(
            os.path.join(_HARM, "t2d.{ancestry}.DIAMANTE.2022.GRCh37.tsv.bgz"),
            ancestry=DIAMANTE_RELEASED_ANCESTRIES,
        ),
        expand(
            os.path.join(
                _HARM, "t2d.{ancestry}.DIAMANTE.2022.GRCh37.tsv.bgz.deferred"
            ),
            ancestry=DIAMANTE_DEFERRED_ANCESTRIES,
        ),


# ===========================================================================
# harmonize_gigastroke : stroke × {TRANS, EUR, AFR, EAS}  (D-02 lock)
# ===========================================================================

GIGASTROKE_ANCESTRIES = ["TRANS", "EUR", "AFR", "EAS"]


rule harmonize_gigastroke_stroke:
    """Per-ancestry GIGASTROKE all-stroke harmonizer."""
    output:
        tsv_bgz=os.path.join(
            _HARM, "stroke.{ancestry}.GIGASTROKE.2022.GRCh37.tsv.bgz"
        ),
        tbi=os.path.join(
            _HARM, "stroke.{ancestry}.GIGASTROKE.2022.GRCh37.tsv.bgz.tbi"
        ),
        parquet=os.path.join(
            _PARQ, "stroke.{ancestry}.GIGASTROKE.2022.GRCh37.parquet"
        ),
        qc_json=os.path.join(
            _QC, "stroke.{ancestry}.GIGASTROKE.2022.qc.json"
        ),
    wildcard_constraints:
        ancestry="TRANS|EUR|AFR|EAS",
    params:
        raw=lambda wc: resolve_raw_for(
            f"GIGASTROKE2022_stroke_{wc.ancestry}", wc.ancestry
        ),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=12000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_gigastroke.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --trait stroke --ancestry {wildcards.ancestry} \
            --consortium GIGASTROKE --year 2022
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


rule harmonize_gigastroke_all:
    input:
        expand(
            os.path.join(_HARM, "stroke.{ancestry}.GIGASTROKE.2022.GRCh37.tsv.bgz"),
            ancestry=GIGASTROKE_ANCESTRIES,
        ),


# ===========================================================================
# harmonize_aragam : CAD × {TRANS, EUR, EAS}  (+ AFR via D-03 branch)
# ===========================================================================
#
# Aragam ZIP unpack (m1-01) yields 3 files:
#   - CAD_GWAS_primary_discovery_meta.tsv  (TRANS)
#   - CAD_GWAS_SEX_STRATIFIED.txt.gz       (EUR sex-stratified)
#   - CAD_GWAS_BBJ_meta.tsv                (EAS)
# AFR is absent (D-03 branch (b)); the Klarin 2018 fallback row remains
# DEFERRED (PENDING_D03_FALLBACK_RESOLUTION). When Carter locates the
# Klarin file, switch the harmonize_aragam_cad_afr rule's input
# resolution to point at the staged Klarin path and add
# `--klarin-fallback` to the shell.
# ---------------------------------------------------------------------------

ARAGAM_RAW_FILES = {
    "TRANS": "CAD_GWAS_primary_discovery_meta.tsv",
    "EUR":   "CAD_GWAS_SEX_STRATIFIED.txt.gz",
    "EAS":   "CAD_GWAS_BBJ_meta.tsv",
}


def _aragam_raw_glob(ancestry: str) -> str:
    """Resolve the unzipped Aragam ZIP file for the given ancestry."""
    d = Path(_RAW) / "Aragam2022" / "CAD"
    if (d / ".deferred").exists():
        return DEFERRED_SENTINEL
    fname = ARAGAM_RAW_FILES.get(ancestry)
    if fname is None:
        return DEFERRED_SENTINEL
    target = d / fname
    if not target.exists():
        return DEFERRED_SENTINEL
    return str(target)


rule harmonize_aragam_cad:
    """Per-ancestry Aragam harmonizer (TRANS / EUR / EAS)."""
    output:
        tsv_bgz=os.path.join(
            _HARM, "cad.{ancestry}.Aragam.2022.GRCh37.tsv.bgz"
        ),
        tbi=os.path.join(
            _HARM, "cad.{ancestry}.Aragam.2022.GRCh37.tsv.bgz.tbi"
        ),
        parquet=os.path.join(
            _PARQ, "cad.{ancestry}.Aragam.2022.GRCh37.parquet"
        ),
        qc_json=os.path.join(
            _QC, "cad.{ancestry}.Aragam.2022.qc.json"
        ),
    wildcard_constraints:
        ancestry="TRANS|EUR|EAS",
    params:
        raw=lambda wc: _aragam_raw_glob(wc.ancestry),
    conda:
        "../../../envs/m1-harmonize.yml"
    resources:
        mem_mb=16000,
        runtime=2880,
    shell:
        _DEFERRED_GUARD + r"""
        python src/python/harmonize_aragam.py \
            --input {params.raw} \
            --output {output.tsv_bgz}.tmp.tsv.gz \
            --parquet {output.parquet} \
            --qc-json {output.qc_json} \
            --trait cad --ancestry {wildcards.ancestry} \
            --consortium CARDIoGRAM-C4D-MVP --year 2022
        zcat {output.tsv_bgz}.tmp.tsv.gz | bgzip -c > {output.tsv_bgz}
        tabix -s 1 -b 2 -e 2 -S 1 -f {output.tsv_bgz}
        rm -f {output.tsv_bgz}.tmp.tsv.gz
        """


rule harmonize_deferred_aragam_cad_afr:
    """D-03 branch (b): CAD-AFR DEFERRED on Klarin 2018 fallback resolution.

    SUMSTATS-UPGRADE.tsv row 23 → MVP-CHARGE-Klarin (PENDING_D03_FALLBACK_RESOLUTION).
    When Carter locates the Klarin file (KP4CD / Zenodo / DUA), replace this
    rule with a harmonize_aragam_cad_afr_klarin rule using
    harmonize_aragam_klarin2018().
    """
    output:
        deferred=os.path.join(
            _HARM, "cad.AFR.MVP-Klarin.2018.GRCh37.tsv.bgz.deferred"
        ),
    shell:
        r"""
        mkdir -p $(dirname {output.deferred})
        cat > {output.deferred} <<EOF
Status: DEFERRED
Trait: cad, Ancestry: AFR, Consortium: MVP-CHARGE-Klarin, Year: 2018
Reason: D-03 branch (b) — Aragam ZIP lacks AFR file; Klarin 2018 MVP-AFR-CAD fallback PENDING_D03_FALLBACK_RESOLUTION (KP4CD / Zenodo / DUA path unresolved as of m1-01)
Recheck: when Carter locates the Klarin file, replace this rule with harmonize_aragam_cad_afr_klarin
EOF
        """


rule harmonize_aragam_all:
    input:
        expand(
            os.path.join(_HARM, "cad.{ancestry}.Aragam.2022.GRCh37.tsv.bgz"),
            ancestry=["TRANS", "EUR", "EAS"],
        ),
        os.path.join(_HARM, "cad.AFR.MVP-Klarin.2018.GRCh37.tsv.bgz.deferred"),
