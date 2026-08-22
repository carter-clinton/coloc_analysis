"""THE ONE PINNED PLACE for the two POSTED occlusion-gate ceilings.

PUBLIC RECORD (the authority these two numbers derive from)
-----------------------------------------------------------
OSF file ``mk7ze`` — https://osf.io/mk7ze — posted 2026-08-22T02:58:55Z on the
parent registration ``az52u`` ("AFR occlusion gate — recalibration to a site-basis
ceiling with a companion multiplicity condition"). The project copy of the posted
text lives at
``.planning/amendments/osf-amendment-occlusion-gate-recalibration-2026-08-20.md``;
its marker-exclusive paste block is 22,945 B / md5
``13a49f543cabcc27ce9f1e589783c060`` and is what was uploaded.

WHAT THE AMENDMENT'S SLOT_LEDGER CALLS THEM
-------------------------------------------
``CEILING_3X_MEDIAN_PCT   = 0.5056%``  -> ``OCCLUSION_SITE_FRACTION_CEILING``
``INFLATION_CEILING_3X_X  = 3.42x``    -> ``OCCLUSION_INFLATION_CEILING``

DERIVATIONS (both by the SAME rule — three times a MEDIAN)
-----------------------------------------------------------
* the site-fraction ceiling is 3x the 21-region site-basis MEDIAN of 0.1685%
  (site basis), giving 1.87x margin over the observed site-basis maximum 0.2698%.
* the companion inflation ceiling is 3x the inflation MEDIAN of 1.14x. It is
  DELIBERATELY NOT anchored on the sample MEAN of 1.18x: the amendment says so in
  as many words ("The companion gate is NOT anchored on it. The gate's anchor is
  the MEDIAN, 1.14x, chosen because the site-fraction ceiling is anchored on a
  median too and the two ceilings must be derived by the same rule"). 1.18x is the
  reported summary figure and region 1's own measured inflation — neither is the
  gate anchor.

THE UNITS TRAP, STATED ONCE
----------------------------
The CODE holds a BARE FRACTION (``0.005056``). The AMENDMENT prints a PERCENTAGE
(``0.5056%``). They are the same quantity 100x apart. Every consumer compares a
bare fraction ``occ_sites / n_sites`` against ``OCCLUSION_SITE_FRACTION_CEILING``;
anything that renders it for a human multiplies by 100 and appends ``%``.

THE STANDING RULE
------------------
A CHANGE HERE REQUIRES A NEW POSTED OSF AMENDMENT FIRST — pre-registration
precedes execution, and the executed rule must be the pre-registered rule. Editing
a number in this file to make a region pass is scientific misconduct dressed as a
one-character diff.

THE NAMED ENFORCER
-------------------
``tests/m3/test_occlusion_gate_constants.py``. It parses the amendment's own
SLOT_LEDGER lines and asserts that RENDERING each constant reproduces the posted
string byte for byte (a must-be-identity transform, never a float tolerance), and
it pins the paste block's size and md5. Both halves carry negative controls. If
you are reading this because that test went red: re-read the standing rule above
before touching anything.

NO OTHER SYMBOLS, NO IMPORTS. This module must stay importable from anywhere with
zero dependencies of its own, so the producer's import of it is free and can never
fail for an unrelated reason.
"""

#: Condition (i) of the posted clause (d): a region DEFERS when its occluded-SITE
#: fraction ``occ_sites / n_sites`` is STRICTLY GREATER than this. A bare fraction
#: (the amendment prints it as 0.5056%).
OCCLUSION_SITE_FRACTION_CEILING: float = 0.005056

#: Condition (ii) of the posted clause (d): a region DEFERS when its own row/site
#: inflation at occluded sites, ``occ_rows / occ_sites``, is STRICTLY GREATER than
#: this. Dimensionless (the amendment prints it as 3.42x).
OCCLUSION_INFLATION_CEILING: float = 3.42
