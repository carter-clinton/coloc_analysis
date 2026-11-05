"""JSON `credible_sets` == the `.fit.rds` `$sets$cs` that coloc.susie reads (quick-261102-log, D-28 unfreeze).

The impure-set fixture is the e2e fixture region fitted on the A2_identity panel: identity LD gives every
multi-variant set purity 0, so the unfiltered `susie_get_cs(fit)` list is longer than `fit$sets$cs`.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from unittest import mock

import pytest

from .conftest import REPO_ROOT
from .test_frozen_script_armed_e2e import (ANC, FROZEN_REL, PAYLOAD, REGION, RSCRIPT, TRAIT, _ok, _run,
                                           _write_manifest, build_fixture, fit_arm)

from ta_r4 import commands, paths

pytestmark = pytest.mark.r4_heavy

ARM = "A2_identity"

#: DIFFERENTIAL SUBSTRATE: run_susie_rss.R before the JSON credible-set fix. Never re-pin.
PRE_FIX_REF = "656529a"


def _fit(root, script_text=None):
    a3 = build_fixture(root)
    a2 = paths.panel_path(ARM, REGION, ANC)
    _ok(_run([RSCRIPT, PAYLOAD, "--in", root / a3, "--out", root / a2], root))
    _write_manifest(root, ARM, a2, REGION)
    if script_text is not None:
        link = root / FROZEN_REL
        link.unlink()
        link.write_text(script_text)
        real = commands.fit_command

        def pre_fix_argv(*a, **k):  # the substrate predates --cap-after-ld-restriction (W3f N1)
            cmd = real(*a, **k)
            i = cmd.index("--cap-after-ld-restriction")
            return cmd[:i] + cmd[i + 2:]

        with mock.patch.object(commands, "fit_command", pre_fix_argv):
            r = fit_arm(root, ARM)
    else:
        r = fit_arm(root, ARM)
    _ok(r["fit"])
    rds = root / paths.fit_rds(ARM, TRAIT, ANC, REGION)
    p = _ok(_run([RSCRIPT, "-e",
                  f'suppressMessages(library(susieR)); f <- readRDS("{rds}"); v <- readRDS("{root / a3}")$variants; '
                  'pos <- setNames(paste(v$CHR, v$POS, sep = ":"), v$SNP_ID); '
                  'sets <- lapply(unname(f$sets$cs), function(x) I(sort(unname(pos[names(x)])))); '
                  'cat(jsonlite::toJSON(list(sets = sets, n_unfiltered = length(susie_get_cs(f)$cs)), '
                  'auto_unbox = TRUE))'], root))
    return {"json": r["json"], "rds": json.loads(p.stdout), "md5": hashlib.md5(rds.read_bytes()).hexdigest()}


@pytest.fixture(scope="module")
def fitted(tmp_path_factory):
    return _fit(tmp_path_factory.mktemp("cs_fixed"))


def test_fixture_has_an_impure_set(fitted):
    assert fitted["rds"]["n_unfiltered"] > len(fitted["rds"]["sets"])


def test_json_credible_sets_equal_fit_sets(fitted):
    js = [sorted(f"{v['CHR']}:{v['POS']}" for v in s) for s in fitted["json"]["credible_sets"].values()]
    assert js == [sorted(s) for s in fitted["rds"]["sets"]]


def test_fit_rds_unchanged_by_the_fix(fitted, tmp_path):
    pre = subprocess.run(["git", "show", f"{PRE_FIX_REF}:{FROZEN_REL}"], cwd=REPO_ROOT, capture_output=True,
                         text=True, check=True).stdout
    old = _fit(tmp_path, script_text=pre)
    assert old["rds"]["n_unfiltered"] > len(old["rds"]["sets"])
    assert old["md5"] == fitted["md5"]
