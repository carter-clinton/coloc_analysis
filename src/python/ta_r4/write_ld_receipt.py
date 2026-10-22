"""Write the per-fit LD receipt (D-13). Exit 3 when the declared panel is not the manifest's.

    python -m ta_r4.write_ld_receipt --declared P --arm A --stage S --overlay-files F... \
        --policy POL --panel-manifest M --ancestry ANC --region-safe R --out O [--legacy-any]

--legacy-any (repro arms only): an absent panel is recorded (present false, ld_source_class
missing) and exits 0, because the frozen record's fits ran with that absence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from ta_r4.arms import ARMS
from ta_r4.validate_r4_fits import ManifestError, manifest_row

REPO = Path(__file__).resolve().parents[3]
CLASS = {"real_ld": "real", "identity_matched": "identity_matched", "legacy_any": "legacy_panel"}


class ReceiptError(Exception):
    pass


def _digest(data, algo):
    return hashlib.new(algo, data).hexdigest()


def build_receipt(a):
    if a.arm not in ARMS:
        raise ReceiptError(f"unknown arm {a.arm!r}")
    mode = ARMS[a.arm]["validator_mode"]
    if a.legacy_any != (mode == "legacy_any"):
        raise ReceiptError(f"--legacy-any={a.legacy_any} but {a.arm} validator_mode is {mode}")
    if a.stage != ARMS[a.arm]["stage"]:
        raise ReceiptError(f"--stage {a.stage} but {a.arm} is {ARMS[a.arm]['stage']}")

    declared = Path(a.declared)
    present = declared.is_file() and declared.stat().st_size > 0
    manifest = Path(a.panel_manifest)
    row = None
    if manifest.exists():
        try:
            row = manifest_row(manifest, a.ancestry, a.region_safe)
        except ManifestError as e:
            raise ReceiptError(str(e))
    elif present or not a.legacy_any:
        raise ReceiptError(f"panel manifest absent: {manifest}")

    rc = {"declared": a.declared, "present": present, "md5": None, "sha256": None, "size_bytes": None}
    if present:
        data = declared.read_bytes()
        rc.update(md5=_digest(data, "md5"), sha256=_digest(data, "sha256"), size_bytes=len(data))
        if row is None:
            raise ReceiptError(f"no manifest row ({a.ancestry}, {a.region_safe}) in {manifest}")
        if rc["md5"] != row.get("md5"):
            raise ReceiptError(f"declared md5 {rc['md5']} != manifest md5 {row.get('md5')} ({a.declared})")
    elif not a.legacy_any:
        raise ReceiptError(f"declared panel absent or empty: {a.declared}")

    overlay = b"".join(Path(f).read_bytes() for f in a.overlay_files)
    git = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True)
    if git.returncode != 0:
        raise ReceiptError(f"git rev-parse HEAD failed: {git.stderr.strip()}")
    rc.update(
        arm=a.arm, stage=a.stage, ancestry=a.ancestry, region_safe=a.region_safe,
        overlay_sha256=_digest(overlay, "sha256"), git_sha=git.stdout.strip(),
        policy_sha256=_digest(Path(a.policy).read_bytes(), "sha256"),
        panel_manifest_md5=_digest(manifest.read_bytes(), "md5") if manifest.exists() else None,
        ld_source_class=CLASS[mode] if present else "missing",
    )
    return rc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for k in ("--declared", "--arm", "--stage", "--policy", "--panel-manifest", "--ancestry",
              "--region-safe", "--out"):
        ap.add_argument(k, required=True)
    ap.add_argument("--overlay-files", nargs="+", required=True)
    ap.add_argument("--legacy-any", action="store_true")
    a = ap.parse_args(argv)
    try:
        rc = build_receipt(a)
    except ReceiptError as e:
        print(f"LD_RECEIPT_REFUSED: {e}", file=sys.stderr)
        return 3
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rc, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
