"""ta-r4 fit rule (D-13, D-28): receipt + md5 gate, the FROZEN run_susie_rss.R armed by flags, validator.

The script's exit code is not trusted (it exits 0 on silent identity fallbacks); validate_r4_fits is.
Commands come from ta_r4.commands, which the e2e tests run as-is.
"""

import shlex

from ld_panel import resolve_ld_path
from ta_r4 import commands as r4cmd

PYTHON_BIN = sys.executable
_R4_LEGACY = ARMS[ARM]["validator_mode"] == "legacy_any"


def _r4_fit_inputs(w):
    gate = gate_input(w)  # OSF gate first: production refuses before any path is resolved
    d = {
        "gate": gate,
        "sumstats": r4paths.sumstats_path(w.trait, w.ancestry, ARM),
        "variants": r4paths.catalog_path(ARMS[ARM]["route"], w.region),
        "policy": ARMS[ARM]["policy"],
        "script": ARMS[ARM]["script"],
    }
    if not _R4_LEGACY:
        # {region_safe} templates only: the curated->M2 crosswalk is deliberately not applied.
        ld = str(resolve_ld_path(region_id=w.region, ancestry=w.ancestry, config=config, region_safe=w.region))
        declared = r4paths.panel_path(ARM, w.region, w.ancestry)
        if ld != declared:
            raise WorkflowError(f"resolved panel {ld} != declared {declared} ({ARM} {w.ancestry} {w.region})")
        d["ld_matrix"] = ld
        d["panel_manifest"] = r4paths.panel_manifest_path(ARM, w.ancestry)
    return d


rule r4_run_finemap:
    input:
        unpack(_r4_fit_inputs),
    output:
        json=r4paths.fit_json(ARM, "{trait}", "{ancestry}", "{region}"),
        fit=r4paths.fit_rds(ARM, "{trait}", "{ancestry}", "{region}"),
        receipt=r4paths.ld_receipt_json(ARM, "{trait}", "{ancestry}", "{region}"),
    log:
        ld_z_consistency=f"data/r4/logs/{ARM}/finemap/{{trait}}.{{ancestry}}.{{region}}.estimate_s.log",
    wildcard_constraints:
        trait="[a-z0-9]+",
        ancestry="EUR|AFR",
        region="[A-Za-z0-9_]+",
    conda:
        str(Path(workflow.basedir) / "envs" / "r_coloc.yml")
    threads: 1
    resources:
        mem_mb=config["resources"]["default_mem_mb"],
    params:
        check=lambda w, input: "true" if _R4_LEGACY else shlex.join(["test", "-s", input.ld_matrix]),
        receipt=lambda w: shlex.join(r4cmd.receipt_command(ARM, w.trait, w.ancestry, w.region)),
        fit=lambda w: shlex.join(r4cmd.fit_command(ARM, w.trait, w.ancestry, w.region, config,
                                                   region_id=REGION_SAFE_TO_ID[w.region])),
        validate=lambda w: shlex.join(r4cmd.validate_command(ARM, w.trait, w.ancestry, w.region)),
    shell:
        r"""
        set -euo pipefail
        {params.check}
        {params.receipt}
        {params.fit}
        {params.validate}
        {PYTHON_BIN} -c "import json,sys; d=json.load(open(sys.argv[1])); st=d.get('status'); EARLY=('no_variants','too_many_variants'); na=('NA_EARLY_EXIT' if st in EARLY else 'ABSENT'); vd=('early_exit:'+str(st) if st in EARLY else ('ld_fields_present' if 'ld_matrix' in d else 'ALARM_LD_FIELDS_MISSING')); vcp=('variant_catalog_fallback' in d); vcv=d.get('variant_catalog_fallback'); ozv=d.get('ld_overlap_zero_fallback'); cause=('key_absent' if not vcp else ('path1_variant_catalog_empty_subset' if (vcv and not ozv) else ('path2_ld_overlap_zero_NO_NUMERIC_CAUSE' if (vcv and ozv) else ('path2_ld_overlap_zero_RETRY' if ozv else 'none')))); print('region', sys.argv[2], 'ancestry', sys.argv[3], 'status', st, 'ld_receipt_verdict', vd, 'ld_z_consistency_s', (d.get('d3b_ld_z_consistency_s') if 'd3b_ld_z_consistency_s' in d else na), 'ld_source_mismatch_flag', (d.get('ld_source_mismatch_flag') if 'ld_source_mismatch_flag' in d else na), 'ld_matrix', (d.get('ld_matrix') if 'ld_matrix' in d else na), 'ld_file_declared', (d.get('ld_file_declared') if 'ld_file_declared' in d else na), 'ld_authoritative', (d.get('ld_authoritative') if 'ld_authoritative' in d else na), 'variant_catalog_fallback', (d.get('variant_catalog_fallback') if 'variant_catalog_fallback' in d else na), 'ld_overlap_zero_fallback', (d.get('ld_overlap_zero_fallback') if 'ld_overlap_zero_fallback' in d else na), 'variant_catalog_fallback_cause', cause, 'ld_allele_aware', (d.get('ld_allele_aware') if 'ld_allele_aware' in d else na), 'ld_allele_exact', (d.get('ld_allele_exact') if 'ld_allele_exact' in d else na), 'ld_allele_flipped', (d.get('ld_allele_flipped') if 'ld_allele_flipped' in d else na), 'ld_allele_dropped_palindromic', (d.get('ld_allele_dropped_palindromic') if 'ld_allele_dropped_palindromic' in d else na), 'ld_allele_dropped_mismatch', (d.get('ld_allele_dropped_mismatch') if 'ld_allele_dropped_mismatch' in d else na), 'ld_allele_dropped_ambiguous', (d.get('ld_allele_dropped_ambiguous') if 'ld_allele_dropped_ambiguous' in d else na), 'ld_allele_dropped_unusable', (d.get('ld_allele_dropped_unusable') if 'ld_allele_dropped_unusable' in d else na), 'ld_allele_catalog_join', (d.get('ld_allele_catalog_join') if 'ld_allele_catalog_join' in d else na))" {output.json} {wildcards.region} {wildcards.ancestry} > {log.ld_z_consistency} || true
        """
