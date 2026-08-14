# Seth — reply to UPDATE #2, 2026-08-14 (couriered by Carter, banked verbatim)

> Provenance: Seth = methodologist agent (Claude Science), no repo/perimeter access;
> all exchange couriered by Carter. Received 2026-08-14 ~12:00 EDT, banked by
> quick-260814-guk. Body below is verbatim as received.

---

Seth — reply to UPDATE #2, 2026-08-14
Two defects fixed, one correction I accept, one BLOCKING transcription fix, and one substantive disagreement about how a consequence is being framed.

BLOCKING — the md5 in the adjudication card is not a valid hash
The card Carter will run quotes the short-body hash as c19e8b2ad7cd6a45fee1d668d8a9cf9. That string is 31 hex characters. An md5 is 32. It cannot match anything — the comparison will fail silently and the STOP-truncated branch will never fire, which is precisely the branch that protects the record.

Correct value, as reported from the OSF API:

c19be8b2ad7cd6a45fee1d668d8a9cf9      (32 chars; the 'b' at index 3 is the dropped char)

Please fix this in the card before Carter runs it. I flagged it in my last reply and it came back through unchanged, so I am escalating it rather than restating it politely. If it helps, the safest formulation for the card is to not pre-list the short hash at all: have Carter report wc -c and md5sum of the download, and adjudicate against the two known-good anchors (28ecdb31 / 425d925a). Any size other than 9,758 or 9,907 is a STOP by itself, no hash comparison required — a byte count cannot be mistranscribed into a false pass.

R1 — I accept your correction, and it weakens my own argument
You verified the anomaly gate (clause (d), with BRANCH_AFR_OCC_DEFERRED) is in your canonical block as well as mine. So my claim that a truncated body might leave the ceiling unregistered was wrong: the gate is promised under either lineage, and the download resolves which body is public, not whether the method was pre-registered. That materially lowers the urgency I asserted for R1 — I overstated it, and the correction is yours, not mine.

Keeping it as a fire gate is still right, but for the narrower reason: we should not bank output while the public record's contents are unknown. That is a records-integrity argument, not a "we might be executing an unregistered method" argument. I withdraw the stronger claim.

R3 — the important one: the ceiling was genuinely not wired
This is the finding of the exchange. An unconditional exclude at any count is exactly what clause (d) prohibits, and it would have silently excluded arbitrarily many variants per region with no defer, no disclosure, and no way to distinguish "5 occlusions" from "a substrate failure." The fix as described is right on all four properties I care about: module constant not CLI-tunable (it is registered text, so it must not be a runtime knob), strict > matching "exceeds", scaled by measured n_var, and defer-not-exclude with nothing written or uploaded. The mutation test reddening exactly the boundary case is the right proof.

Ceiling at the pinned cap, for the runbook: 60 variants at n_var 120,000 (51 at region-1's 102,421). Region 1 sits 10x under.

R4 — the fix is right; "nothing scientific is lost" is the part I disagree with
Wiring --max-n-var (default 120,000, YAML-pinned to the consumer) is the correct remediation, and deferring in seconds instead of grinding hours before an OOM is a real improvement. Two things I want on the record, though, because I think the framing understates a limitation:

1. ~29 deferred regions is a 10.5% coverage gap, not a no-op.

deferred (est. at the 120k cap) : 29 / 276 = 10.5% of regions
bankable target                 : ~247 regions
largest deferred span           : 48.5 Mb

The argument "the consumer could not convert nor egress them anyway, so nothing is lost" is true as a statement about this pipeline as currently built — it is not true as a statement about the science. Those 29 regions contain real loci with real association signal, and a genome-wide AFR scan that silently covers 247/276 regions has a 10.5% ancestry-specific coverage hole. That is exactly the kind of gap that, undisclosed, becomes a reviewer question we cannot answer later: "why does your AFR panel omit the largest regions?"

So I would ask for two things, neither blocking the fire:

Disclose it as a coverage limitation, not just an internal deferral status. It belongs in the methods/limitations text alongside the occlusion disclosure — "N regions exceeding n_var X were not converted in square mode; affected span M Mb" with the actual post-fire numbers.
Note the remedy path exists so the gap is bounded rather than permanent: the producer already supports banded mode (--r gz with an --ld-window-* bound), and large regions can be split into overlapping sub-windows. Neither needs to happen before this fire. But the limitation should be recorded as deferred with a known remedy, not as nothing lost.

2. Swapping Stage B's worst case to the largest square-feasible region (m2_region_00071, 20.8 Mb) is correct — testing an infeasible region would have measured the gate, not the pipeline. Good call. Note the consequence for the cost model: wall-time extrapolated from Stage B now covers only the feasible class, so the per-region cost gate should be read as cost-per-bankable-region, not cost-per-region-of-276.

R2, R5 — accepted as verified
R2: status "ok" + banked .npz being the falsification by construction is exactly what I wanted, and the gsutil cat check for 6 lines (header + 5 records) is the ground-truth validation. R5: closed.

Taking you up on the offer
Yes — if the download shows a short body, send me your canonical 9,758-byte block (28ecdb31) and I will review it as the re-post body. I would also like the 149-byte diff against my 9,907 lineage whenever convenient, independent of the download outcome: if the two bodies differ in substance rather than formatting, that is worth knowing before either is cited again, and it is the one thing I still cannot see from here.

Nothing else blocking from my side. An agent never fires it — agreed and unchanged.
