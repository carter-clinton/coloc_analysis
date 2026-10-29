"""ta-r4 W3a reproduction targets (D-12b). Fits run through r4_run_finemap; stage repro (not gated).

  bash bin/r4_fire.sh repro <repro_routeC|repro_routeL|repro_k2d_routeC|repro_k2d_routeL> r4_repro_fits
"""


def R4_REPRO_TARGETS(arm):
    if arm not in r4cmd.REPRO_FIT_ARMS:
        raise WorkflowError(f"r4_repro_fits needs one of {sorted(r4cmd.REPRO_FIT_ARMS)}, not {arm}")
    keys = r4cmd.repro_fit_keys(arm)
    unknown = sorted({g for _, _, g in keys} - set(REGION_SAFE_TO_ID))
    if unknown:
        raise WorkflowError(f"{arm}: regions {unknown} are not in {r4paths.regions_csv()}")
    return [r4paths.fit_json(arm, t, a, g) for t, a, g in keys]


rule r4_repro_fits:
    input: lambda w: R4_REPRO_TARGETS(ARM)


# W3b (D-17). SH2B3 R2 known answer: bmi/hypertension/stroke L15 fits (02c4404 code + policy) and the
# Stage-2 asthma/t2d fits (Route L), coloc'd by run_coloc_susie.R at c0f02b6 in the env the R2 fire used
# (la_multitrait_r; path passed as R4_R2_RSCRIPT). The L10/iter-100 measurement is the same script on Route C.
#   R4_R2_RSCRIPT=<la_multitrait_r>/bin/Rscript bash bin/r4_fire.sh repro repro_sh2b3_r2 r4_sh2b3_all
import os

if ARM == "repro_sh2b3_r2":
    SH2B3 = "SH2B3_12q24"
    SH2B3_L15_TRAITS = ("bmi", "hypertension", "stroke")
    R2_COLOC_MANIFEST = "results/multitrait/coloc_manifest_R2.tsv"
    R2_COLOC_SCRIPT = "data/r4/legacy_code/run_coloc_susie_c0f02b6.R"
    R2_COLOC_POLICY = "config/susie_policy.yaml"  # the --policy the R2 dispatcher passed (provenance only)
    with open(Path(workflow.basedir) / R2_COLOC_MANIFEST, newline="") as fh:
        SH2B3_PAIRS = {r["pair_id"]: (r["trait_a"], r["trait_b"]) for r in csv.DictReader(fh, delimiter="\t")
                       if r["base_region"] == SH2B3 and r["ancestry"] == "EUR"}
    if len(SH2B3_PAIRS) != 9:
        raise WorkflowError(f"{R2_COLOC_MANIFEST}: {len(SH2B3_PAIRS)} SH2B3 EUR pairs, expected the 9 R2 pairs")
    SH2B3_COLOC_DIRS = {"r2": "data/r4/results/repro_sh2b3_r2/coloc", "L10": "data/r4/results/repro_sh2b3_L10/coloc"}

    def _sh2b3_fit_arm(config_label, trait):
        if config_label == "L10":
            return "repro_routeC"
        return "repro_sh2b3_r2" if trait in SH2B3_L15_TRAITS else "repro_routeL"

    def _sh2b3_coloc_inputs(config_label):
        def f(w):
            a, b = SH2B3_PAIRS[w.pair_id]
            d = {"manifest": R2_COLOC_MANIFEST, "script": R2_COLOC_SCRIPT}
            for side, t in (("a", a), ("b", b)):
                arm = _sh2b3_fit_arm(config_label, t)
                d[f"fit_{side}"] = r4paths.fit_rds(arm, t, "EUR", SH2B3)
                d[f"json_{side}"] = r4paths.fit_json(arm, t, "EUR", SH2B3)
            return d
        return f

    def _r2_rscript():
        rs = os.environ.get("R4_R2_RSCRIPT", "")
        if not os.path.isfile(rs):
            raise WorkflowError(f"R4_R2_RSCRIPT must name the R2-era Rscript (la_multitrait_r), not {rs!r}")
        return rs

    for _label in SH2B3_COLOC_DIRS:
        rule:
            name: f"r4_sh2b3_{_label}_coloc"
            input: unpack(_sh2b3_coloc_inputs(_label))
            output: f"{SH2B3_COLOC_DIRS[_label]}/{{pair_id}}.json"
            log: f"data/r4/logs/sh2b3_{_label}/{{pair_id}}.log"
            wildcard_constraints: pair_id="|".join(SH2B3_PAIRS)
            params: rscript=lambda w: _r2_rscript(), policy=R2_COLOC_POLICY
            shell:
                "{params.rscript} {input.script} --fit-a {input.fit_a} --fit-b {input.fit_b} --policy {params.policy}"
                " --pair-id {wildcards.pair_id} --manifest {input.manifest} --output {output} > {log} 2>&1"

    rule r4_sh2b3_all:
        input:
            [r4paths.fit_json("repro_sh2b3_r2", t, "EUR", SH2B3) for t in SH2B3_L15_TRAITS],
            [f"{d}/{p}.json" for d in SH2B3_COLOC_DIRS.values() for p in sorted(SH2B3_PAIRS)],
