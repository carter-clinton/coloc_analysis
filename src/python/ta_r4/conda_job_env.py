"""The Snakemake job env built from an env yaml: `<prefix>/<md5(realpath(prefix) + yaml bytes)>_` (Snakemake 7.32.4
snakemake/deployment/conda.py Env.hash / Env.address). The pin file is not in the hash; a post-deploy script is, so
its presence is refused."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path


def job_env_dir(yml, prefix):
    yml = Path(yml)
    deploy = yml.with_suffix(".post-deploy.sh")
    if deploy.exists():
        raise RuntimeError(f"{deploy} exists: a post-deploy script enters Snakemake's env hash; job_env_dir does not model it")
    h = hashlib.md5()
    h.update(os.path.realpath(prefix).encode())
    h.update(yml.read_bytes())
    return Path(prefix) / (h.hexdigest() + "_")
