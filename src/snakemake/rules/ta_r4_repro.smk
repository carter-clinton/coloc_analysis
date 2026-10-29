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
