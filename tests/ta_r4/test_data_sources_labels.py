"""data_sources.yaml study labels agree with trait_manifest.tsv source_study (W3f 15.2, review T1)."""
from __future__ import annotations

import csv
import re

import yaml

from .conftest import REPO_ROOT

SOURCES = REPO_ROOT / "config/ta_r4/data_sources.yaml"
TRAITS = REPO_ROOT / "config/ta_r4/trait_manifest.tsv"
KEY = re.compile(r"sumstats_([a-z0-9]+)_(EUR|AFR)")


def labels():
    """{(trait, ancestry): the parenthesised study label of the sumstats_<trait>_<anc> entry's name}."""
    out = {}
    for k, v in yaml.safe_load(SOURCES.read_text())["sources"].items():
        m = KEY.fullmatch(k)
        if m:
            out[m.groups()] = re.fullmatch(r".*?\((.*)\)", v["name"]).group(1)
    return out


def studies():
    with open(TRAITS, newline="") as fh:
        return {(r["trait"], r["ancestry"]): r["source_study"] for r in csv.DictReader(fh, delimiter="\t")}


def test_afr_t2d_is_t2dggi_suzuki_2024():
    lab = labels()[("t2d", "AFR")]
    assert lab == studies()[("t2d", "AFR")].split(" (", 1)[0] == "T2DGGI AFA, Suzuki 2024"
    assert "DIAMANTE 2022" not in lab


def test_every_label_names_the_trait_manifest_study():
    lab, st = labels(), studies()
    assert len(lab) == 8 and set(lab) <= set(st)
    assert [k for k, v in lab.items() if v not in st[k]] == []
