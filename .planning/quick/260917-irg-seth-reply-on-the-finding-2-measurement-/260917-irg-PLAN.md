---
phase: quick-260917-irg
plan: 01
type: execute
wave: 1
depends_on: []            # ordering vs quick-260917-f68 is ENFORCED by the Task 1 pre-flight (osf md5 pin + clean tracked tree), never by a HEAD pin
mode: quick
branch: m3-W2-aou-deltas
worktree: none            # GPFS: no worktree. Scratch lives OUTSIDE the repo.
autonomous: true
push: false
requirements: ["irg-D1", "irg-D2", "irg-D3", "irg-D4", "irg-D5", "irg-D6", "irg-D7", "irg-D8"]

# DOCS ONLY. Exactly three deliverable paths, plus this PLAN and its SUMMARY.
files_modified:
  - .planning/osf_deviations.md                                                                                     # 2026-09-03 entry only: 10 exact-once sites (S1-S10)
  - .planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md   # NEW (D7)
  - .planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md                                         # NEW (D8)
  - .planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-PLAN.md                          # this file (committed in Task 3)
  - .planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SUMMARY.md                       # NEW (Task 3)

files_frozen:
  - .planning/osf_deviations.md lines 1-566, and every line of the 2026-09-03 entry outside S1-S10
  - .planning/amendments/**          # posted OSF bodies
  - .planning/STATE.md, .planning/HANDOFF.json, .planning/DECISIONS.md   # close-out is the ORCHESTRATOR's
  - .planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md  # its stale "UNSENT" header is reported, not fixed
  - src/**, tests/**, config/**, workflow/**
  - every enforcer script under .planning/quick/** (run them, never edit them)

must_haves:
  truths:
    - "The 2026-09-03 entry reports Finding 2's design-corrected result as evidence, not as a side of 0.05: under either chr15 treatment AT MOST weak evidence of between-region heterogeneity beyond measured clustering, p = 0.0326 (drop 00060__sub13) and p = 0.0517 (drop 00060__sub12) stated as -log10 p 1.49 and 1.29, the same evidence, p = 0.2171 dropping both, magnitude unidentified, not robustly distinguishable from a clustering-only explanation (D1)"
    - "'At most' is justified in the text by the five NA regions carrying deff 1.0 (no correction), so a fuller correction lowers phi (D1)"
    - "Every disposition sentence carrying 'NOT ESTABLISHED' survives word for word; normalized 'not established' count 6 -> 7 and 'drafted — not posted' 4 -> 5; the Status line is byte-unchanged (D1, standing rule)"
    - "No normalized 'straddl', 'coin' or 'artifact of analytic choice' remains in the entry outside the historical 260908-uer correction paragraph (after :1029, :1032) and the new (10e) note (after :1096, :1097, :1099)"
    - "Both windows are reported and neither is selected; 'interchangeable' is scoped to equally defensible handling choices made in advance, not statistically equivalent; design effects 1.096 / 1.359 sit in the same paragraph as both p-values; choosing a window now is named post-hoc selection (D2)"
    - "(10a) carries 719 of 2521 = 28.52% of pairs in clusters of size >= 2 (303 clusters) and 1,802 of 2521 (71.48%) singletons, defined distinctly from 573 of 2521 = 22.73% dual-anchored, both on the per-region SUM basis; ICC_hat 0.728930 is scoped to those 719 pairs with its denominator and said not to describe the singletons (D3)"
    - "§(7)'s reviewer accounting carries the provenance verified against the record: the between-window hypothesis was the reviewer's and was wrong; the within-window mechanism and c=2 simulation were ours, quoted from 260904-dgi CONTENT-SPEC.md:45-56; the measurement confirmed clustering exists (ICC 0.73) without showing it accounts for the dispersion; Rao-Scott was proposed by neither party (§(10c) cross-referenced) (D4)"
    - "No 36%/64% share, no 'universal', no 'no geometric predicate' in osf_deviations.md; §(10d) (Finding 1) is byte-identical (D5)"
    - "(10e) does not appear to deny what it records: it says it does not record his acceptance of THE SCOPING DECIDED HERE (W1), and its FRAMING bullet names §(2) as the third restatement the frozen 2026-09-08 note aligned, since that note's parenthetical says §(7) and §(7) carried the design effect, never the straddle (W7)"
    - "A dated '#### (10e) REVIEWER RESPONSE 2026-09-17 — framing corrected, provenance corrected, scope stated' is the last #### heading and records what changed and why; the 260908-uer correction paragraph is byte-identical (D6)"
    - "No superseded literal (1.652, 0.0366, 1.564, 0.0556, 1.969) is added to osf_deviations.md, and each occurs 0 times in the bank file, the courier file and the courier paste block"
    - "The bank file is a provenance header plus the scratch reply byte-for-byte inside a 4-backtick fence (D7); the courier is an UNSENT status header plus the scratch draft byte-for-byte, and its point-2 replacement sentence occurs exactly once, normalized, in the disclosure's §(10b) conclusion (D8)"
    - "Only the three deliverable paths change (+ PLAN/SUMMARY); lines 1-850 of osf_deviations.md keep their positions (live docs cite it by line up to :739); the uer guard, vqq --live verifier and u9p ledger checks give an identical line-normalized PASS/FAIL multiset before and after"
  artifacts:
    - path: ".planning/osf_deviations.md"
      provides: "the amended 2026-09-03 entry"
      contains: "#### (10e) REVIEWER RESPONSE 2026-09-17 — framing corrected, provenance corrected, scope stated"
      md5_after: "6ba5ad5365b64a2482eafea75168b8ae"   # 88393 B, 1124 lines, from base 714454a5b23d979396f1d8c6fc1104d4
    - path: ".planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md"
      provides: "the reviewer's reply as received, with provenance header"
      md5: "9b4df61d9e2097b88e1ff523c1e6d27d"   # 9400 B, 78 lines
    - path: ".planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md"
      provides: "the reply courier, UNSENT"
      md5: "a92d9ec21ebb26b39ae8df99696b2abf"   # 5763 B, 86 lines
  key_links:
    - from: ".planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md point 2"
      to: ".planning/osf_deviations.md §(10b) THE CONCLUSION"
      via: "the same replacement sentence, normalized"
      enforcer: "irg_guard.py G06-D8-sentence (RED control N13)"
    - from: ".planning/osf_deviations.md §(7) PROVENANCE sub-bullet"
      to: ".planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/CONTENT-SPEC.md:45-56"
      via: "two verbatim quotes"
      enforcer: "irg_guard.py G06-D4-quote (RED control N15)"
    - from: ".planning/osf_deviations.md §(10e)"
      to: ".planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md"
      via: "repo path cited in (10e)"
---

<objective>
Amend the DRAFTED — NOT POSTED 2026-09-03 tail disclosure after the external reviewer's
2026-09-17 reply, exactly as Carter decided (D1-D8), and bank the reply and our UNSENT answer.

Purpose: the entry currently carries Finding 2's conclusion with a threshold framing ("straddle",
"coin-flip", "artifact of analytic choice") that the reviewer showed reports which side of 0.05 two
near-identical results fell on instead of the evidence. The entry also leaves the ICC without its
denominator, and it lacks the corrected provenance of the within-window mechanism. The disposition
stays: Finding 2 is NOT ESTABLISHED.

Output: one commit with the three deliverable files (osf entry amended at 10 sites, reply banked,
courier banked), then one commit with this PLAN and its SUMMARY. The executor writes neither
STATE.md, HANDOFF.json nor DECISIONS.md, contacts nobody and posts nothing.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/osf_deviations.md (the 2026-09-03 entry: base :567-1057)
@.planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/CONTENT-SPEC.md (:45-56)

## Every shell block in this plan starts with this preamble (shell state does not persist)

```bash
REPO=/gpfs_common/share01/clintonlab/ckclinto/coloc_analysis
TD=.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-
IN=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/irg
X=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/irg-exec
REPLY=$IN/SETH-REPLY-2026-09-17-as-pasted.txt
DRAFT=$IN/SETH-PASTE-3-reply-to-finding2-review-DRAFT.txt
SPEC=$REPO/.planning/quick/260904-dgi-correct-the-tail-disclosure-after-advers/CONTENT-SPEC.md
BANK=$TD/260917-irg-SETH-REPLY-finding2-review-as-received.md
COURIER=.planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md
U=.planning/quick/260908-uer-correct-the-rao-scott-table-the-pooled-r/guard.py
V=.planning/quick/260916-vqq-stage-c-nan-error-posture-options-draft-/260916-vqq-verify.py
N=.planning/quick/260814-u9p-bank-seth-prefix-test-reply-third-body-e/260814-u9p-verify.sh
cd "$REPO"
norm_enf() { grep -E '^(PASS|FAIL|RESULT)' "$1" | sed -E 's/\[[^]]*\]//g; s/:[0-9]+(-[0-9]+)?//g' | LC_ALL=C sort; }
```

## Pins (measured at plan time, 2026-09-17; HEAD moved 29a7f68 -> 57a3105 -> d880170 during planning as quick-260917-f68 committed and closed out. HEAD is NOT pinned; only the osf md5 and a clean tracked tree are.)

| object | pin |
|---|---|
| `.planning/osf_deviations.md` BEFORE | md5 `714454a5b23d979396f1d8c6fc1104d4`, 1057 lines |
| `$REPLY` (as pasted, NOT byte-verified vs the original) | md5 `537391c10bdc4cb0dcca91af84c8bd3d`, 8316 B, 60 lines |
| `$DRAFT` — RE-PINNED 2026-09-17 after the orchestrator applied flags 1-3 (opening line scoped to §2/§4/§5; point 1 restates the share metrics; point 2 says "everywhere they carry the conclusion" and that the 2026-09-08 note keeps its wording). Its point-2 replacement sentence is byte-unchanged, so S8 still matches. | md5 `042fe4798429f30fa5b4bbb59dee9419`, 4587 B, 67 lines |
| embedded `irg_apply.py` / `irg_guard.py` / `irg_negctl.py` | md5 in each BEGIN marker below |
| osf_deviations.md AFTER | md5 `6ba5ad5365b64a2482eafea75168b8ae`, 88393 B, 1124 lines |
| bank file AFTER | md5 `9b4df61d9e2097b88e1ff523c1e6d27d`, 9400 B, 78 lines |
| courier AFTER | md5 `a92d9ec21ebb26b39ae8df99696b2abf`, 5763 B, 86 lines |

## The ten sites (all text is VERBATIM in the embedded `irg_apply.py`; nothing is retyped)

| id | base lines | after lines | gist | decision |
|---|---|---|---|---|
| S1 | 608-609, in place 2->2 | 608-609 | status-block discharge bullet: "two INTERCHANGEABLE treatments ... straddle p = 0.05" -> "either treatment of the chr15 overlap carries AT MOST WEAK evidence (p 0.0326 / p 0.0517; p 0.2171 dropping both)" | D1 |
| S2 | 665-670, in place 6->6 | 665-670 | §(2) heterogeneity bullet: STRADDLING / "artifact of analytic choice" -> at most weak evidence beyond measured clustering, not robustly distinguishable from a clustering-only explanation | D1 |
| S3 | insert after 857 (+11) | 858-868 | §(7) reviewer accounting: PROVENANCE (i)-(iv), two quotes from `260904-dgi` CONTENT-SPEC.md:45-56 | D4 |
| S4 | 878-882 (5->7) | 889-895 | §(8) FINDING 2 IS NOT ESTABLISHED bullet: "straddle p = 0.05" -> at most weak, same evidence, p 0.2171 | D1 |
| S5 | insert after 937 (+5) | 951-955 | (10a) new bullet: 719 of 2521 = 28.52% in clusters >= 2 (303), 1,802 (71.48%) singletons, distinct from 22.73% dual-anchored, per-region SUM | D3 |
| S6 | 941 (1->3) | 959-961 | (10a) ICC_hat 0.728930 scoped to the 719 pairs, denominator attached, singletons excluded | D3 |
| S7 | 980-986 (7->13) | 1000-1012 | (10b) "THE DECISIVE OBSERVATION IS THE STRADDLE" -> "REPORT THE EVIDENCE, NOT WHICH SIDE OF A THRESHOLD IT FELL ON": interchangeable scoped, 1.096 vs 1.359, -log10 1.49 vs 1.29, neither selected, post-hoc selection, at most weak via deff 1.0 | D1, D2 |
| S8 | 990-995 (6->7) | 1016-1022 | (10b) THE CONCLUSION blockquote: NOT ESTABLISHED kept word for word + the courier's replacement sentence + direction | D1, D8 |
| S9 | 1030-1031 (2->2) | 1057-1058 | (10b) WHAT WAS NOT SHOWN: "rests on the straddle" -> "rests on the design-corrected evidence being at most weak under either treatment of the overlap" | D1 |
| S10 | append after base 1057 (+40 lines) | 1086-1124 (the guard's census prints this insert as `insert base 1059-1058 -> after 1086-1125`: base index 1058 and after index 1125 are the `split()` trailing empty element) | new `#### (10e) REVIEWER RESPONSE 2026-09-17 — framing corrected, provenance corrected, scope stated`; includes the W1 scoping sentence and the W7 clause naming §(2) as the third aligned restatement | D6 |

UNTOUCHED BY DESIGN (D6): the `260908-uer` correction paragraph (base :997-1007, after :1024-1034)
keeps "the p-value straddle ... previously 0.0366 vs 0.0556" and "The three restatements of the
straddle"; its words and numbers are history, and (10e) explains the change.

## Decision coverage

| D | where | full? |
|---|---|---|
| D1 evidence framing, "at most" justified, NOT ESTABLISHED kept | S1 S2 S4 S7 S8 S9 (10e) | Full |
| D2 both windows, neither selected, interchangeable scoped, 1.096/1.359 beside p, post-hoc | S7 (10e) | Full |
| D3 22.73% vs 28.52% / 71.48%, per-region SUM, ICC scoped | S5 S6 (10e) | Full |
| D4 provenance (verified, see below) | S3 (10e) | Full |
| D5 no share / "universal" / "no geometric predicate"; Finding 1 untouched | guard G07 | Full |
| D6 (10e) + in-place alignment, uer log untouched | S10, guard G08 | Full |
| D7 bank reply verbatim + provenance header | irg_apply.py BANK_HEADER, guard G09 | Full |
| D8 courier in 260916 format, sentence == disclosure | irg_apply.py COURIER_HEADER, guard G06-D8/G10 | Full |

## D4 — verified against the record at plan time (no STOP)

- (i) Between-window hypothesis = the reviewer's, and wrong: osf `:851-855` *"His **SPECIFIC** mechanism
  (sub-window replication) **does** remain unable to create dispersion and **stays dead**"* (his own
  framing, `260908-n48` CONTENT-SPEC.md `:49-52`); `HANDOFF.json` key `seth_conceded_NARROWED_2026_09_04`
  *"His non-independence hypothesis is DEAD ... that simulation tested BETWEEN-window duplication ONLY"*.
- (ii) Within-window mechanism + c=2 simulation = ours: `260904-dgi` CONTENT-SPEC.md `:1-3` (our
  5-reviewer adversarial review) and `:46-48` *"The operative dependence is WITHIN-window: pairs sharing
  an occluding deletion do not flip independently"*, `:51` *"c=2, ICC 1.0  -> mean phi 2.032"*. No record
  before 2026-09-04 shows the reviewer naming within-window structure (searched `.planning/debug/2609*`,
  `.planning/quick/2608[23]*`, `2609*`, STATE.md, HANDOFF.json). The only credit to him is the 260916
  courier §6 (`:77-79`), which he quotes and declines. The entry never carried that credit (0 hits for
  `credit`).
- (iii) Clustering exists without accounting for the dispersion: §(10a) `:940` ICC 0.728930; §(10b)
  `:1025-1030` "does not reproduce", "FAILURE TO EXCLUDE, NOT a demonstration".
- (iv) Rao-Scott proposed by neither party: §(10c) `:1039-1040`.
- Nuance (does not block): the record is mixed on who owned the GENERAL principle (`260903-ict`
  calls it "Seth's"; a 09-04 HANDOFF note says "ours to overreach"; `260908-n48` adopted his framing
  that it was his). D4 does not touch it, and §(7) `:853-855` is unchanged.

## KNOWN AND DELIBERATELY NOT ACTED ON (D8 "everything else in the draft stays"). Do not fix these.

These are reported to the orchestrator for Carter. They are not executor work:
1-3. ✅ **RESOLVED UPSTREAM 2026-09-17.** Flags 1-3 (the "everywhere they appear" overstatement, the "everything except §3" scoping, and the share-metric mismatch) were applied by the orchestrator to `$DRAFT` itself, which is re-pinned at md5 `042fe4798429f30fa5b4bbb59dee9419`. Point 1 now states his metric on the POOLED 1.360 (36%), the same metric on the effective deffs 1.19 / 1.26 (19% and 26%), the removal-share reading (32% and 42%), and that therefore no share goes into the disclosure. All six of those figures were re-derived at plan time and are arithmetically correct at the stated precision. The point-2 replacement sentence is byte-unchanged, so S8 still matches it exactly.
4. `.planning/debug/260916-COURIER-...-UNSENT.md` is still headed UNSENT, but the reviewer quotes its §5-§6. STILL OPEN; that file is frozen by this plan.
5. The pasted reply's first line opens "Seth —". It is banked verbatim and not interpreted. STILL OPEN by design.

## Enforcers this plan runs (read-only) and their plan-time behaviour on a scratch clone at 57a3105

| enforcer | BEFORE | AFTER (simulated file) |
|---|---|---|
| `$U` (uer guard) | 38/40, exit 1 (FROZEN-1-531 vs f650dd8; HANDOFF 1.988 pin) | identical multiset |
| `$V --live` (vqq) | RESULT RED, same 10 reds | identical multiset |
| `bash $N ledger` (u9p append-only vs 50dc51d) | ALL PASS | ALL PASS |
</context>

<tasks>

<task type="auto">
  <name>Task 1: Pre-flight, extract the embedded scripts, build in scratch, prove the guard (GREEN + 42 RED controls), capture BEFORE state</name>
  <files>(scratch only: $X/**; no repo file is written in this task)</files>
  <action>
Run each numbered step; any STOP ends the task and the plan, and you report the exact output.

1. PRE-FLIGHT (STOP on any mismatch):
   - `git rev-parse --abbrev-ref HEAD` == `m3-W2-aou-deltas`. Do not check out anything.
   - `git status --porcelain --untracked-files=no` prints NOTHING. Then `echo rc=$?` must be 0. Empty output alone is not proof, so print `git status --porcelain --untracked-files=no | wc -l` == 0 as well.
   - `md5sum .planning/osf_deviations.md` == `714454a5b23d979396f1d8c6fc1104d4` and `wc -l` == 1057. If f68 (or anyone) changed it: STOP. Do not re-derive the sites.
   - `md5sum "$REPLY" "$DRAFT"` == the pins; `test -f "$SPEC"`.
   - `$BANK` and `$COURIER` do NOT exist, and `git ls-files -- "$BANK" "$COURIER"` prints nothing.
   - `$X` does not exist (or is empty): `mkdir -p "$X"`; `cp .planning/osf_deviations.md "$X/base_osf.md"`; md5 re-checked on the copy.
2. EXTRACT the three embedded scripts from THIS PLAN, and never retype them:
```bash
python3 - "$REPO/$TD/260917-irg-PLAN.md" "$X" <<'PY'
import hashlib, os, re, sys
plan = open(sys.argv[1], encoding="utf-8").read()
pat = re.compile(r"<!-- BEGIN EMBEDDED (\S+) md5=([0-9a-f]{32}) -->\n````python\n(.*?)````\n<!-- END EMBEDDED \1 -->", re.S)
found = pat.findall(plan)
names = sorted(f[0] for f in found)
if names != ["irg_apply.py", "irg_guard.py", "irg_negctl.py"]:
    print("STOP: embedded set", names); sys.exit(2)
for name, pin, body in found:
    b = body.encode("utf-8"); got = hashlib.md5(b).hexdigest()
    if got != pin:
        print("STOP: md5", name, got, "!= pin", pin); sys.exit(2)
    open(os.path.join(sys.argv[2], name), "wb").write(b)
    print("extracted", name, got, len(b), "B")
PY
```
3. CAPTURE BEFORE (real tree, before any edit):
   - `git status --porcelain --untracked-files=all | LC_ALL=C sort > "$X/status_before.txt"`
   - `python3 "$U" > "$X/enf_before_uer.txt" 2>&1; echo "uer exit=$?" >> "$X/enf_before_uer.txt"`
   - `python3 "$V" --live > "$X/enf_before_vqq.txt" 2>&1; echo "vqq exit=$?" >> "$X/enf_before_vqq.txt"`
   - `bash "$N" ledger > "$X/enf_before_u9p.txt" 2>&1; echo "u9p exit=$?" >> "$X/enf_before_u9p.txt"`
   - Record each file's last two lines. Exit codes 1/1/0 are EXPECTED at plan time; what matters is before == after in Task 2. Each file must be non-empty (`test -s`).
4. BUILD in scratch: `python3 "$X/irg_apply.py" "$X/base_osf.md" "$REPLY" "$DRAFT" "$X/out"` exits 0, prints `applied S1` ... `applied S10`, and the three `wrote` lines carry EXACTLY md5 `6ba5ad5365b64a2482eafea75168b8ae` (88393 B, 1124 lines), `9b4df61d9e2097b88e1ff523c1e6d27d` (9400 B, 78 lines), `a92d9ec21ebb26b39ae8df99696b2abf` (5763 B, 86 lines). Any other md5 or an exit of 2: STOP.
5. GUARD, GREEN on the build: `python3 "$X/irg_guard.py" "$X/base_osf.md" "$X/out/osf_deviations.md" "$X/out/bank.md" "$X/out/courier.md" "$REPLY" "$DRAFT" "$SPEC" > "$X/guard_scratch.txt"; echo exit=$?` → exit 0 and last line `RESULT GREEN  122/122 PASS`. Check the enumerations in the output against these plan-time values:
   - G03 framing: `straddl` at 1029 and 1032 (uer-correction-log); `straddl` at 1096, 1097 and 1108, `coin` at 1097, `artifact of analytic choice` at 1099 (all (10e); 1108 is the W7 clause's "never the straddle").
   - G03b: `interchangeab` at 1001 (S7-scoped) and at 1097, 1110, 1113 ((10e)); `equally defensible` at 1001 (S7) and at 1097, 1114 ((10e)).
   - G04: 5 occurrences. Four are `explanat` as the negated hypothesis label (blocks @665, @889, @1016, @1086); one is `accounts for` negated by "without showing that it" (@858).
   - G05-cluster-arith is PARSED from the AFTER text, and its detail line must read: `parsed {1: 1802, 2: 239, 3: 40, 4: 12, 5: 4, 6: 5, 7: 1, 8: 2} -> pairs 2521, singletons 1802, in clusters>=2 719, k(c>=2) 303, sum c^2 3767 (want 2521 / 1802 / 719 / 303 / 3767)`.
   - G04c (courier paste block): 3 occurrences — `carries x% of the excess` as a **quoted attribution**, `explanat` as the negated hypothesis label, `accounts for` negated by "without showing it". G07c: `36%` on 2 lines, each attributed ("your 36%" / "not 36%"); `64%` count 0.
   - census, quoted LITERALLY as the guard prints it (compare byte for byte; the `insert base 1059-1058` and
     `after 1086-1125` forms are the `split()` trailing-element artifact, not an off-by-one):
     `census: replace base 608-609 -> after 608-609; replace base 665-670 -> after 665-670; insert base 858-857 -> after 858-868; replace base 878-882 -> after 889-895; insert base 938-937 -> after 951-955; replace base 941-941 -> after 959-961; replace base 980-986 -> after 1000-1012; replace base 990-995 -> after 1016-1022; replace base 1030-1031 -> after 1057-1058; insert base 1059-1058 -> after 1086-1125`
6. GUARD, RED on the unedited file (sanity: it can see the old state): run the same command with `"$X/base_osf.md"` as BOTH base and after → exit 1, with FAILs in at least G03-framing, G06-D1, G06-D2, G06-D3, G06-D4, G06-D8-sentence and G06-D6-heading.
7. NEGATIVE CONTROLS: `python3 "$X/irg_negctl.py" "$X" "$X/base_osf.md" "$X/out/osf_deviations.md" "$X/out/bank.md" "$X/out/courier.md" "$REPLY" "$DRAFT" "$SPEC" "$X/negwork" > "$X/negctl.txt"; echo exit=$?` → exit 0, `POSITIVE CONTROL (unmutated): FAIL ids = [] -> GREEN`, 42 control lines each ending `OK` (ids N01-N42; they print in DEFINITION order, not numeric order), and `NEGCTL RESULT: ALL CONTROLS OBSERVED RED`. N06 must print `literal line-grep 'straddl' on the mutated line: 0`, which proves the normalized guard catches what a literal grep misses.
  </action>
  <verify>
    <automated>X=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/irg-exec; test "$(md5sum < "$X/out/osf_deviations.md" | cut -d' ' -f1)" = 6ba5ad5365b64a2482eafea75168b8ae && tail -1 "$X/guard_scratch.txt" | grep -q -- 'RESULT GREEN  122/122 PASS' && grep -q -- 'NEGCTL RESULT: ALL CONTROLS OBSERVED RED' "$X/negctl.txt" && test "$(grep -c -- '  OK' "$X/negctl.txt")" -eq 42 && test -s "$X/enf_before_vqq.txt" && echo T1-OK</automated>
  </verify>
  <done>Pre-flight passed. Scripts extracted with matching md5s. Scratch build md5s equal the pins. Guard GREEN 122/122 on the build and RED on the unedited file. 42/42 negative controls observed RED plus a GREEN positive control. BEFORE state captured. No repo file touched.</done>
</task>

<task type="auto">
  <name>Task 2: Install the three files, re-verify on the real tree (md5, guard, enforcers BEFORE == AFTER, path scope with a RED probe), commit the three deliverables</name>
  <files>.planning/osf_deviations.md, .planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md, .planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md</files>
  <action>
1. Re-check that `.planning/osf_deviations.md` is still `714454a5b23d979396f1d8c6fc1104d4` (a concurrent writer is the failure this catches). If not: STOP.
2. INSTALL by copy, never by hand edit: `cp "$X/out/osf_deviations.md" .planning/osf_deviations.md`; `cp "$X/out/bank.md" "$BANK"`; `cp "$X/out/courier.md" "$COURIER"`. `md5sum` on the three repo paths must equal `6ba5ad53…`, `9b4df61d…` and `a92d9ec2…` in full (pins table).
3. GUARD ON THE REAL PATHS: `python3 "$X/irg_guard.py" "$X/base_osf.md" .planning/osf_deviations.md "$BANK" "$COURIER" "$REPLY" "$DRAFT" "$SPEC" > "$X/guard_real.txt"; echo exit=$?` → exit 0, `RESULT GREEN  122/122 PASS`.
4. ENFORCERS AFTER: rerun the three commands of Task 1 step 3 into `enf_after_{uer,vqq,u9p}.txt`. For each, `diff <(norm_enf "$X/enf_before_X.txt") <(norm_enf "$X/enf_after_X.txt")` must print NOTHING, and `echo rc=$?` must be 0. Also compare the trailing `exit=` lines, which must be equal. If any multiset differs: restore with `git checkout -- .planning/osf_deviations.md` and `rm -- "$BANK" "$COURIER"`, then STOP and report the diff.
5. PATH SCOPE (G13): `git status --porcelain --untracked-files=all | LC_ALL=C sort > "$X/status_after.txt"`. Then:
   - `LC_ALL=C comm -23 "$X/status_before.txt" "$X/status_after.txt"` prints NOTHING (nothing vanished).
   - `LC_ALL=C comm -13 "$X/status_before.txt" "$X/status_after.txt"` prints EXACTLY these 3 lines:
     ` M .planning/osf_deviations.md`
     `?? .planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md`
     `?? .planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md`
   - This implies no change under `.planning/amendments/`, STATE.md, HANDOFF.json, DECISIONS.md, `src/` or `tests/`. Assert it explicitly anyway: `git status --porcelain -- .planning/amendments .planning/STATE.md .planning/HANDOFF.json .planning/DECISIONS.md src tests | wc -l` == 0.
   - RED CONTROL for this check: `touch src/python/__irg_negctl_probe.py`, recompute `comm -13` → it MUST now show a 4th line `?? src/python/__irg_negctl_probe.py`, and the explicit `wc -l` MUST be 1 (observed RED). Then `rm -- src/python/__irg_negctl_probe.py` and recompute: back to exactly the 3 lines, with `wc -l` == 0 (GREEN again). Record both observations.
6. COMMIT (explicit paths only; never `git add -A` or `.`):
   - `git add -- .planning/osf_deviations.md "$BANK" "$COURIER"`
   - `git diff --cached --name-only | LC_ALL=C sort` == exactly those 3 paths (sorted). Anything else staged: `git restore --staged` the extra paths and STOP.
   - `git commit -m "docs(quick-260917-irg): Finding 2 stated as evidence, not a side of 0.05 — at most weak under either chr15 treatment (p 0.0326 / 0.0517 = -log10 1.49 / 1.29, the same evidence; p 0.2171 dropping both); still NOT ESTABLISHED" -m "Per Carter D1-D8 after the reviewer's 2026-09-17 reply. 2026-09-03 entry, 10 exact-once sites: framing aligned in place (status bullet, §(2), §(8), §(10b)); both windows reported and neither selected; 'interchangeable' scoped; (10a) 28.52% in clusters (719/2521, 303) vs 22.73% dual-anchored, ICC scoped to those 719 pairs; §(7) provenance corrected and verified against 260904-dgi CONTENT-SPEC.md:45-56; new (10e). The 260908-uer correction note is untouched. Reviewer reply banked as received (not byte-verified); reply courier banked UNSENT. Guard 122/122, 42/42 RED controls; uer/vqq/u9p enforcers unchanged. DRAFTED — NOT POSTED." -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"`
   - If the commit fails with `invalid object` / `Error building trees` (GPFS object loss): STOP and report verbatim. Do not retry and do not attempt recovery.
7. POST-COMMIT: `git show --stat --format=%H HEAD` lists exactly the 3 files. `git show HEAD:.planning/osf_deviations.md | md5sum` == `6ba5ad5365b64a2482eafea75168b8ae`, and the same holds for the other two blobs. `git status --porcelain --untracked-files=no | wc -l` == 0.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis; X=/gpfs_common/share01/clintonlab/ckclinto/tmp/claude-410819/-gpfs-common-share01-clintonlab-ckclinto-coloc-analysis/bd0cb7c3-ba8e-44b1-97ab-b232115ba092/scratchpad/irg-exec; TD=.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-; BANK=$TD/260917-irg-SETH-REPLY-finding2-review-as-received.md; COURIER=.planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md; norm_enf() { grep -E '^(PASS|FAIL|RESULT)' "$1" | sed -E 's/\[[^]]*\]//g; s/:[0-9]+(-[0-9]+)?//g' | LC_ALL=C sort; }; test "$(git show HEAD:.planning/osf_deviations.md | md5sum | cut -d' ' -f1)" = 6ba5ad5365b64a2482eafea75168b8ae && test "$(git show "HEAD:$BANK" | md5sum | cut -d' ' -f1)" = 9b4df61d9e2097b88e1ff523c1e6d27d && test "$(git show "HEAD:$COURIER" | md5sum | cut -d' ' -f1)" = a92d9ec21ebb26b39ae8df99696b2abf && test "$(git show --name-only --format= HEAD | wc -l)" -eq 3 && tail -1 "$X/guard_real.txt" | grep -q -- 'RESULT GREEN  122/122 PASS' && for e in uer vqq u9p; do diff <(norm_enf "$X/enf_before_$e.txt") <(norm_enf "$X/enf_after_$e.txt") > /dev/null || exit 1; done && echo T2-OK</automated>
  </verify>
  <done>The three files are committed with the pinned md5s. The guard is GREEN on the real tree. The uer, vqq --live and u9p ledger multisets are identical before and after. Exactly three status lines are new, and the src/ probe was observed RED then GREEN. The tracked tree is clean. Nothing was posted or sent.</done>
</task>

<task type="auto">
  <name>Task 3: Write the SUMMARY and commit PLAN + SUMMARY</name>
  <files>.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SUMMARY.md, .planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-PLAN.md</files>
  <action>
1. Write `$TD/260917-irg-SUMMARY.md` with the Write tool. Frontmatter: task `260917-irg`, branch, date 2026-09-17, docs_only true, pushed false, status COMPLETE. Body, measured and never copied from this plan:
   - the Task 2 commit hash;
   - the three md5s as measured;
   - the S1-S10 site table with after-line ranges from the guard census;
   - the guard result line;
   - the G03 and G04 enumerations verbatim from `$X/guard_real.txt`;
   - the negctl table (42 lines + positive control) verbatim from `$X/negctl.txt`;
   - the three enforcer BEFORE/AFTER last lines;
   - the G13 scope observation, including the probe RED then GREEN;
   - the "KNOWN AND DELIBERATELY NOT ACTED ON" list, copied from this plan's context;
   - one line: "STATE.md / HANDOFF.json / DECISIONS.md not written — orchestrator close-out."
   If the harness REFUSES the SUMMARY write, do not work around it (no heredoc, no python write). Hand the SUMMARY text back, commit nothing in this task, and say so.
2. `git add -- "$TD/260917-irg-PLAN.md" "$TD/260917-irg-SUMMARY.md"`; `git diff --cached --name-only | LC_ALL=C sort` == exactly those 2 paths; `git commit -m "docs(quick-260917-irg): PLAN + SUMMARY — reviewer-reply amendment to the tail disclosure (still DRAFTED — NOT POSTED)" -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"`. Same GPFS STOP rule as Task 2.
3. Hand back: both commit hashes, the three md5s, `RESULT GREEN  122/122 PASS`, `42/42 RED`, the enforcer equality, and the five KNOWN items. Do not push. Contact nobody.
  </action>
  <verify>
    <automated>cd /gpfs_common/share01/clintonlab/ckclinto/coloc_analysis; TD=.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-; COMMITTED="$(git show --name-only --format= HEAD | LC_ALL=C sort | tr '\n' ' ')"; if [ "$COMMITTED" = "$TD/260917-irg-PLAN.md $TD/260917-irg-SUMMARY.md " ]; then test -f "$TD/260917-irg-SUMMARY.md" && test "$(git status --porcelain --untracked-files=no | wc -l)" -eq 0 && echo T3-OK-committed; else test ! -f "$TD/260917-irg-SUMMARY.md" && test "$(git status --porcelain --untracked-files=no | wc -l)" -eq 0 && git log --oneline -1 | grep -q 260917-irg && echo T3-OK-handed-back; fi</automated>
  </verify>
  <done>EITHER the PLAN+SUMMARY commit exists and the tracked tree is clean (`T3-OK-committed`), OR the harness refused the SUMMARY write, no SUMMARY file was left behind, the Task 2 commit is still HEAD and the tracked tree is clean, and the SUMMARY text is in the hand-back (`T3-OK-handed-back`). Both are sanctioned; nothing else is. No push, no contact.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| chat paste -> repo | the reviewer's reply arrived via Carter's paste; it is not byte-verifiable against the original |
| agent -> reviewer-facing record | `.planning/osf_deviations.md` is the methods record a referee will read |
| agent -> outside parties | OSF and the reviewer; no agent crosses this boundary |
| this task -> other tasks' enforcers | live documents cite osf_deviations.md by line number; three enforcers read it |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-irg-01 | T | osf entry text | mitigate | md5-pinned base; scripted exact-once replacements; guard G12 census (only planned sites), G08 frozen regions, G14 positions; pinned output md5 |
| T-irg-02 | R | provenance / credit claims (D4) | mitigate | verified against the record before writing (context §D4); G06-D4-quote requires both quotes to exist in CONTENT-SPEC.md:45-56 |
| T-irg-03 | T | banked reply fidelity | accept | cannot be verified against the original; the header says "not byte-verified" and records the scratch md5; G09 proves byte identity to the scratch file |
| T-irg-04 | E | posting / sending | mitigate | no OSF or reviewer contact in any task; the Status line is byte-guarded (G02); the courier header is guarded as NOT SENT (G10) |
| T-irg-05 | T | line citations + neighbouring enforcers | mitigate | G14 freezes lines 1-850 (max live citation :739); uer/vqq/u9p multisets compared before/after |
| T-irg-06 | I | overclaim (clustering "explains" Finding 2) | mitigate | G04 negation/label enumeration + positive-claim regex; RED controls N09, N10 |
</threat_model>

<verification>
- `irg_guard.py` GREEN 122/122 on both scratch and real paths, and RED on the unedited file.
- `irg_negctl.py`: positive control GREEN; N01-N42 each observed RED on the expected check ids.
- Enforcers (uer guard, vqq --live, u9p ledger): line-normalized PASS/FAIL/RESULT multisets identical before and after.
- Path scope: exactly three new status lines; the `src/` probe observed RED then GREEN.
- Committed blob md5s equal the pins; tracked tree clean after each commit.
</verification>

<success_criteria>
- Finding 2 still reads NOT ESTABLISHED everywhere it did. The reasons are now stated as evidence (at most weak; 0.0326 and 0.0517 are the same evidence; 0.2171 with both windows dropped). No window is selected.
- The ICC's denominator and the 22.73% / 28.52% distinction are in §(10a). The corrected provenance is in §(7). (10e) records the change.
- The reply is banked as received, and the reply courier is banked UNSENT with a sentence matching the disclosure.
- No superseded literal is added, no share figure appears, and Finding 1 is untouched. Status: DRAFTED — NOT POSTED.
</success_criteria>

<output>
After completion, create `.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SUMMARY.md` (Task 3).
</output>

## EMBEDDED FILES — extract with Task 1 step 2; never retype

<!-- BEGIN EMBEDDED irg_apply.py md5=c2db4d804b10dffb1bac567f95450285 -->
````python
#!/usr/bin/env python3
"""irg_apply.py - quick-260917-irg. Builds the three output files from pinned inputs.

Every new text block is carried here VERBATIM, one source line per list item. Each
replacement is EXACT-ONCE: the old text must occur exactly once in the working text at
the moment it is applied, or the script exits 2 and writes nothing.

usage: irg_apply.py OSF_IN REPLY_TXT DRAFT_TXT OUT_DIR
writes OUT_DIR/osf_deviations.md, OUT_DIR/bank.md, OUT_DIR/courier.md (never inside the repo)
"""
import hashlib, os, sys

PIN_OSF = "714454a5b23d979396f1d8c6fc1104d4"
PIN_REPLY = "537391c10bdc4cb0dcca91af84c8bd3d"
PIN_DRAFT = "042fe4798429f30fa5b4bbb59dee9419"
FENCE = "`" * 4


def J(*lines):
    return "\n".join(lines) + "\n"


EDITS = [
    # ---- S1 - status-block discharge bullet, base :608-609 (2 lines -> 2 lines) ----
    ("S1",
     J("  chi-square can be corrected for it directly, and under that correction **two INTERCHANGEABLE",
       "  treatments of the chr15 window overlap straddle p = 0.05** (**0.0326** vs **0.0517**)."),
     J("  chi-square can be corrected for it directly, and under that correction **either treatment of the",
       "  chr15 overlap carries AT MOST WEAK evidence** (p 0.0326 / p 0.0517; p 0.2171 dropping both).")),
    # ---- S2 - section (2) heterogeneity bullet, base :665-670 (6 lines -> 6 lines) ----
    ("S2",
     J("  §(10)). **Corrected for the measured design effect, two interchangeable treatments of the chr15",
       "  overlap give p 0.0326 and p 0.0517 — STRADDLING 0.05 — so the between-region heterogeneity is",
       "  NOT ESTABLISHED.** The **DIRECTION** remains positive under every treatment (**phi > 1.2",
       "  throughout**), but the **magnitude is unidentified** and the **significance is an artifact of",
       "  analytic choice**. A bare \"1.99x\" overstates what was identified; so does any claim of",
       "  significance."),
     J("  §(10)). **Under the measured design effect, either treatment of the chr15 overlap carries AT MOST",
       "  WEAK evidence of heterogeneity beyond measured clustering (p 0.0326 / p 0.0517; p 0.2171 dropping",
       "  both), so the between-region heterogeneity is NOT ESTABLISHED.** The **DIRECTION** remains",
       "  positive under every treatment (**phi > 1.2 throughout**), but the **magnitude is unidentified**",
       "  and the dispersion is **not robustly distinguishable from a clustering-only explanation**. A bare",
       "  \"1.99x\" overstates what was identified; so does any claim of significance.")),
    # ---- S3 - section (7) reviewer accounting, INSERT after base :857 (D4) ----
    ("S3",
     J("    question settled.** It cost more than the specific error did.",
       "  - ⭐ **THE pairs-per-deletion DISTRIBUTION HAS NOW BEEN MEASURED (2026-09-08) — see §(10).**"),
     J("    question settled.** It cost more than the specific error did.",
       "  - ⚠ **PROVENANCE, CORRECTED 2026-09-17 at the reviewer's own request (§(10e)).** Stated as he",
       "    stated it, and checked against the record before it was written: **(i)** the **BETWEEN-window**",
       "    hypothesis (same-parent sub-window replication) was **his, and it was wrong** — the bullet above;",
       "    **(ii)** the **WITHIN-window** mechanism and the **c=2 simulation** were **ours**, in",
       "    `260904-dgi`'s `CONTENT-SPEC.md:45-56`: *\"The operative dependence is WITHIN-window: pairs sharing",
       "    an occluding deletion do not flip independently\"* and *\"c=2, ICC 1.0 -> mean phi 2.032\"*;",
       "    **(iii)** the measurement **confirmed that within-window clustering EXISTS** (ICC 0.73, §(10a))",
       "    **without showing that it accounts for the dispersion** (§(10b)); **(iv)** the **Rao-Scott test",
       "    was proposed by NEITHER party** (§(10c)). Our courier of the §(10) result credited him with",
       "    pointing at within-window structure; **he declined that credit, the record agrees with him, and",
       "    the credit never entered this entry.**",
       "  - ⭐ **THE pairs-per-deletion DISTRIBUTION HAS NOW BEEN MEASURED (2026-09-08) — see §(10).**")),
    # ---- S4 - section (8) epistemic status, base :878-882 (5 lines -> 6 lines) ----
    ("S4",
     J("- ⭐ **FINDING 2 IS NOT ESTABLISHED (recorded 2026-09-08).** The between-region heterogeneity in",
       "  POST-filter rate does **not** survive the **measured** within-window design effect combined with",
       "  **defensible** handling of the chr15 window overlap: two interchangeable overlap treatments",
       "  **straddle p = 0.05** (**0.0326** vs **0.0517**). ⭐ **FINDING 1 IS UNCHANGED** and **Finding 3's",
       "  status is unchanged.** Full statement, caveats and the measurement behind it: **§(10)**."),
     J("- ⭐ **FINDING 2 IS NOT ESTABLISHED (recorded 2026-09-08).** Corrected for the **measured**",
       "  within-window design effect, the between-region heterogeneity in POST-filter rate carries **at most",
       "  weak evidence** under either **defensible** treatment of the chr15 window overlap (**p 0.0326** /",
       "  **p 0.0517**, the same evidence; **p 0.2171** dropping both windows), is **not robustly",
       "  distinguishable from a clustering-only explanation**, and its **magnitude is unidentified**.",
       "  ⭐ **FINDING 1 IS UNCHANGED** and **Finding 3's status is unchanged.** Full statement, caveats and",
       "  the measurement behind it: **§(10)**.")),
    # ---- S5 - (10a) INSERT the clustered-fraction bullet after base :937 (D3) ----
    ("S5",
     J("  `chr15:91246748:CT:C`; **52 clusters span more than one region**.",
       "- **c_mean 1.1976** — but the quantity a design effect actually depends on is the **SIZE-WEIGHTED**"),
     J("  `chr15:91246748:CT:C`; **52 clusters span more than one region**.",
       "- **Pairs in clusters of size >= 2: 719 of 2521 = 28.52%**, in **303** clusters; the other **1,802 of",
       "  2521 (71.48%)** are **singletons**. ⚠ **This is NOT the 22.73% above, and the two must not be",
       "  conflated:** 22.73% counts pairs anchored by **two** deletions (dual-anchored); 28.52% counts pairs",
       "  whose anchoring deletion anchors **at least one other pair**. Reading 22.73% as the clustered",
       "  fraction would understate it. Both are on the **per-region SUM** basis (SCOPE CAVEAT (1)).",
       "- **c_mean 1.1976** — but the quantity a design effect actually depends on is the **SIZE-WEIGHTED**")),
    # ---- S6 - (10a) ICC_hat scope, base :940-941 (2 lines -> 4 lines) (D3) ----
    ("S6",
     J("- **ICC_hat = 0.728930** — ANOVA over the **k=303** clusters of size >= 2 (**N=719**,",
       "  c0=2.371745)."),
     J("- **ICC_hat = 0.728930** — ANOVA over the **k=303** clusters of size >= 2 (**N=719**,",
       "  c0=2.371745). ⚠ **SCOPE: this ICC describes those 719 pairs (28.52% of 2521) ONLY** — among pairs",
       "  sharing an anchoring deletion, PRE/POST status is highly correlated. It does **not** describe the",
       "  **1,802 singletons (71.48%)**, and it must not be quoted as a tail-wide ICC without that denominator.")),
    # ---- S7 - (10b) the decisive-observation paragraph, base :980-986 (D1, D2) ----
    ("S7",
     J("⭐ **THE DECISIVE OBSERVATION IS THE STRADDLE, NOT THE DESIGN EFFECT.** Dropping `sub13` and",
       "dropping `sub12` are **INTERCHANGEABLE** choices: the two windows overlap by **6,000,001 bp**",
       "(SCOPE CAVEAT (3)) and **neither is privileged**. After the design correction they land at",
       "**p 0.0326** and **p 0.0517** — **STRADDLING 0.05**. **A coin-flip between two equally defensible",
       "analyses moves the result across the significance threshold.** This separation appears **ONLY",
       "after the correction**, because sub12 and sub13 carry **different measured design effects (1.096",
       "vs 1.359)**; **uncorrected they are indistinguishable (1.988 vs 1.992)**."),
     J("⭐ **REPORT THE EVIDENCE, NOT WHICH SIDE OF A THRESHOLD IT FELL ON.** Dropping `sub13` and dropping",
       "`sub12` are interchangeable **only as equally defensible handling choices made in advance**: both",
       "were on record before either design-corrected p-value existed (the drop-`sub13` headline since",
       "2026-09-02, the drop-`sub12` mirror in `260904-dgi`'s sensitivity table), the two windows overlap by",
       "**6,000,001 bp** (SCOPE CAVEAT (3)) and **neither is privileged**. They are **NOT statistically",
       "equivalent**: sub12 and sub13 carry **different measured design effects (1.096 vs 1.359)**, which is",
       "why the two analyses separate **ONLY after the correction** (**p 0.0326** dropping `sub13`,",
       "**p 0.0517** dropping `sub12`; **uncorrected they are indistinguishable (1.988 vs 1.992)**). In",
       "evidence units they are **the same evidence**: -log10 p **1.49** vs **1.29**. ⛔ **Both are reported",
       "and NEITHER is selected:** choosing either window now that both p-values are known, by ICC precision",
       "or any other criterion, would be **post-hoc selection**. The evidence is also **AT MOST weak**: the",
       "**five NA regions carry deff 1.0**, i.e. no correction (CONSERVATISM DISCLOSURE below), so a fuller",
       "correction would lower phi.")),
    # ---- S8 - (10b) THE CONCLUSION blockquote, base :990-995 (D1) ----
    ("S8",
     J("> The between-region heterogeneity in POST-filter rate is **NOT ESTABLISHED**. It is not robust to",
       "> the measured within-window design effect combined with defensible handling of the chr15 window",
       "> overlap: two interchangeable overlap treatments straddle p = 0.05 after correction (**0.0326** vs",
       "> **0.0517**), and correcting for clustering while dropping both overlapping windows gives",
       "> **p = 0.2171**. The **DIRECTION** is positive under every treatment (**phi > 1.2 throughout**), but",
       "> the **magnitude is unidentified** and the **significance is an artifact of analytic choice**."),
     J("> The between-region heterogeneity in POST-filter rate is **NOT ESTABLISHED**. Under either",
       "> treatment of the chr15 window overlap, the design-corrected dispersion carries **at most weak",
       "> evidence** of between-region heterogeneity beyond measured clustering: **p = 0.0326** dropping",
       "> `00060__sub13` and **p = 0.0517** dropping `00060__sub12` (-log10 p **1.49** and **1.29**, the same",
       "> evidence), and **p = 0.2171** with both chr15 windows dropped. The **magnitude is unidentified**,",
       "> and the dispersion is **not robustly distinguishable from a clustering-only explanation**. The",
       "> **DIRECTION** is positive under every treatment (**phi > 1.2 throughout**).")),
    # ---- S9 - (10b) WHAT WAS NOT SHOWN, last sentence, base :1030-1031 ----
    ("S9",
     J("reported as one.** The retraction rests on **the straddle**, not on the design effect's point",
       "value."),
     J("reported as one.** The retraction rests on **the design-corrected evidence being at most weak under",
       "either treatment of the overlap**, not on the design effect's point value.")),
    # ---- S10 - APPEND (10e) after base :1057, the last line of the file (D6) ----
    ("S10",
     J("- ⛔ **The status is unchanged: DRAFTED — NOT POSTED.** **Discharging the last open item is NOT",
       "  authorization to post.** The posting decision is **Carter's alone**."),
     J("- ⛔ **The status is unchanged: DRAFTED — NOT POSTED.** **Discharging the last open item is NOT",
       "  authorization to post.** The posting decision is **Carter's alone**.",
       "",
       "#### (10e) REVIEWER RESPONSE 2026-09-17 — framing corrected, provenance corrected, scope stated",
       "",
       "The project's external reviewer answered the §(10) result on **2026-09-17**. His reply is banked as",
       "received (pasted into the session; **not byte-verified** against the original) at",
       "`.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md`.",
       "He **accepted the disposition as stated**, objected to the sentence that carried it, and declined a",
       "credit. **The disposition does not change: Finding 2 is NOT ESTABLISHED.** Every site that carried",
       "the old framing was aligned in this edit (the discharge bullet in the status block, §(2), §(8) and",
       "§(10b)), following the precedent of the `260908-uer` correction note above.",
       "",
       "- ⚠ **FRAMING — the \"straddle\" is withdrawn as a reading of the evidence.** This entry had said that",
       "  two interchangeable overlap treatments \"straddle p = 0.05\", that \"a coin-flip between two equally",
       "  defensible analyses\" moves the result across the threshold, and that the significance \"is an",
       "  artifact of analytic choice\". The two design-corrected p-values, **0.0326** and **0.0517**, are",
       "  **1.49** and **1.29** in -log10 p: **the same evidence**. That they fall on opposite sides of a",
       "  threshold is a property of the **threshold**, not of the data, and reporting which side each fell",
       "  on is the calibrate-to-a-threshold error run in reverse. The aligned sites now report the evidence:",
       "  **at most weak** under either treatment, **p 0.2171** with both chr15 windows dropped, magnitude",
       "  unidentified, and not robustly distinguishable from a clustering-only explanation. **\"At most\"**",
       "  because the five NA regions carry deff 1.0, so a fuller correction lowers phi. ⚠ The `260908-uer`",
       "  correction note keeps its original wording and numbers: it records what that edit did. ⚠ Its",
       "  parenthetical names the three restatements it then aligned as the discharge bullet, §(7) and §(8);",
       "  the third was in fact **§(2)** — §(7) carried the design effect, never the straddle. The note is",
       "  left exactly as written because it is the historical record; this clause is the correction.",
       "- ⚠ **\"INTERCHANGEABLE\" — scoped, and NO window is selected.** The reviewer also argued that, given",
       "  their different design effects (**1.096** vs **1.359**), the better-corrected window is determinable",
       "  from the data. **Declined:** both p-values are now known, so choosing either window, by ICC",
       "  precision or any other criterion, would be **post-hoc selection**. \"Interchangeable\" now means",
       "  **equally defensible handling choices made in advance**, **not statistically equivalent**, and both",
       "  analyses stay reported. **This entry does not record his acceptance of the scoping decided here.**",
       "- ⚠ **SCOPE — two quantities separated, and the ICC's denominator attached (§(10a)).** **22.73%**",
       "  (573 of 2521) of pairs are dual-anchored; **28.52%** (719 of 2521, in 303 clusters) are in clusters",
       "  of size >= 2; the other **1,802 (71.48%)** are singletons, which the ICC does not describe.",
       "- ⚠ **PROVENANCE — corrected in §(7)'s reviewer accounting.** Our courier of the §(10) result",
       "  credited the reviewer with pointing at within-window structure. **He declined the credit, and the",
       "  record agrees with him:** the within-window mechanism and its simulation were ours.",
       "- **Finding 1's text is unchanged.**",
       "- ⛔ **The status is unchanged: DRAFTED — NOT POSTED.** A reviewer response is **NOT authorization to",
       "  post.** The posting decision is **Carter's alone**.")),
]

BANK_HEADER = J(
    "# Reviewer reply 2026-09-17 — Finding 2 review (AS RECEIVED, ⛔ NOT BYTE-VERIFIED)",
    "",
    "**Received:** 2026-09-17, pasted by Carter into the session. **Not byte-verified** against the",
    "original message; chat rendering may have altered blank lines or other whitespace.",
    "**Scratch source:** `SETH-REPLY-2026-09-17-as-pasted.txt`, md5 `537391c10bdc4cb0dcca91af84c8bd3d`,",
    "8316 B, 60 lines. The fenced block below is that file byte-for-byte, first line included.",
    "**Replies to:** our courier of the §(10) measurement result, drafted as",
    "`.planning/debug/260916-COURIER-TO-SETH-measurement-result-UNSENT.md` (its §3-§6 are the sections he",
    "cites; whether the text sent was byte-identical to that draft is not recorded here).",
    "**Recorded in:** `.planning/osf_deviations.md`, 2026-09-03 entry, §(10e) (quick `260917-irg`).",
    "**Our reply:** `.planning/debug/260917-COURIER-TO-SETH-finding2-review-reply-UNSENT.md` (UNSENT).",
    "⛔ This is correspondence. Some of its figures and wording were deliberately NOT carried into the",
    "disclosure (§(10e)); never copy from here into the record.",
    "",
    "---",
    "")

COURIER_HEADER = J(
    "# Courier to Seth — reply to his 2026-09-17 Finding 2 review (⛔ UNSENT)",
    "",
    "**Status:** DRAFTED 2026-09-17, **NOT SENT**. No agent contacts Seth — Carter sends it.",
    "**Replies to:** `.planning/quick/260917-irg-seth-reply-on-the-finding-2-measurement-/260917-irg-SETH-REPLY-finding2-review-as-received.md`",
    "(as pasted; not byte-verified).",
    "**Uses only the corrected Rao-Scott table** (pooled rate estimated from the subset under test, quick",
    "`260908-uer`). No superseded fixed-rate figure appears below.",
    "**Source of every disclosure number:** `.planning/osf_deviations.md`, the 2026-09-03 tail-disclosure",
    "entry, §(7), §(10a), §(10b) and §(10e), as amended by quick `260917-irg`. Point 1's shares and",
    "effective design effects are computed from the §(10b) table and are deliberately NOT in the disclosure.",
    "**Point 2's indented replacement sentence** is word-for-word the §(10b) conclusion (markdown aside).",
    "**Scratch source:** `SETH-PASTE-3-reply-to-finding2-review-DRAFT.txt`, md5",
    "`042fe4798429f30fa5b4bbb59dee9419`, 4587 B; the paste block below is that file byte-for-byte.",
    "**Disclosure status:** still DRAFTED — NOT POSTED. Posting is Carter's decision.",
    "",
    "---",
    "")


def md5b(b):
    return hashlib.md5(b).hexdigest()


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        return 2
    osf_in, reply_p, draft_p, out = sys.argv[1:]
    osf_b = open(osf_in, "rb").read()
    reply_b = open(reply_p, "rb").read()
    draft_b = open(draft_p, "rb").read()
    for name, b, pin in (("osf", osf_b, PIN_OSF), ("reply", reply_b, PIN_REPLY), ("draft", draft_b, PIN_DRAFT)):
        if md5b(b) != pin:
            print("STOP: input %s md5 %s != pin %s" % (name, md5b(b), pin))
            return 2
    d = os.path.abspath(out)
    while True:
        if os.path.isdir(os.path.join(d, ".git")):
            print("STOP: OUT_DIR is inside a git work tree (%s); outputs go to scratch only" % d)
            return 2
        if os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    t = osf_b.decode("utf-8")
    for sid, old, new in EDITS:
        n = t.count(old)
        if n != 1:
            print("STOP: %s old text occurs %d times (want exactly 1)" % (sid, n))
            return 2
        if sid == "S10" and not t.endswith(old):
            print("STOP: S10 anchor is not at EOF")
            return 2
        t = t.replace(old, new, 1)
        print("applied %s" % sid)
    for sid, old, new in EDITS:
        if t.count(new) != 1:
            print("STOP: %s new text occurs %d times after all edits (want 1)" % (sid, t.count(new)))
            return 2
    reply_t = reply_b.decode("utf-8")
    draft_t = draft_b.decode("utf-8")
    for name, body in (("reply", reply_t), ("draft", draft_t)):
        if FENCE in body or not body.endswith("\n"):
            print("STOP: %s contains a 4-backtick fence or lacks a final newline" % name)
            return 2
    bank = BANK_HEADER + FENCE + "\n" + reply_t + FENCE + "\n"
    courier = COURIER_HEADER + FENCE + "\n" + draft_t + FENCE + "\n"
    os.makedirs(out, exist_ok=True)
    for fn, body in (("osf_deviations.md", t), ("bank.md", bank), ("courier.md", courier)):
        p = os.path.join(out, fn)
        with open(p, "wb") as fh:
            fh.write(body.encode("utf-8"))
        print("wrote %s md5 %s %d B %d lines" % (p, md5b(body.encode("utf-8")), len(body.encode("utf-8")),
                                               body.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
````
<!-- END EMBEDDED irg_apply.py -->

<!-- BEGIN EMBEDDED irg_guard.py md5=566ce551c9f4076e7c3495968947d14d -->
````python
#!/usr/bin/env python3
"""irg_guard.py - quick-260917-irg standing-rule guard. stdlib only; reads, never writes.

usage: irg_guard.py BASE_OSF AFTER_OSF BANK COURIER REPLY_TXT DRAFT_TXT DGI_CONTENT_SPEC
exit 0 = every check PASS; exit 1 = any FAIL. Prints one PASS/FAIL line per check id,
plus the enumerations the standing rules require (framing phrases, 'explain' family).

Phrase and literal checks run on NORMALIZED text: markdown * _ ` removed, whitespace runs
collapsed to one space, lowercased. A literal line-grep is blind to bolded or line-wrapped
phrases; every check here is proven able to fail by irg_negctl.py.
"""
import difflib, hashlib, math, re, sys

BANNED = ["1.652", "0.0366", "1.564", "0.0556", "1.969"]
ENTRY_HEAD = "## 2026-09-03 — AFR native-panel DEFINED-ROW TAIL disclosure"
STATUS_LINE = ("- **Status:** DRAFTED — NOT POSTED; placement and posting are Carter's. No agent has "
               "contacted")
UER_ANCHOR = "an earlier draft of this table estimated the pooled rate once from all 21 regions"
S7_ANCHOR = "report the evidence, not which side of a threshold it fell on"
E10_HEAD = "#### (10e) REVIEWER RESPONSE 2026-09-17 — framing corrected, provenance corrected, scope stated"
# base line numbers (1-based) the edit may replace, and base line numbers AFTER which it may insert
ALLOWED_REPLACED = {608, 609, 665, 666, 667, 668, 669, 670, 878, 879, 880, 881, 882, 941,
                    980, 981, 982, 983, 984, 985, 986, 990, 991, 992, 993, 994, 995, 1030, 1031}
# census observed in simulation: replace 608-609; replace 665-670; insert after 857; replace 878-882;
# insert after 937; replace 941; replace 980-986; replace 990-995; replace 1030-1031; insert after 1058 (EOF)
ALLOWED_INSERT_AFTER = {857, 937, 1058}   # 1058 = EOF (split() trailing element)
POSITION_FROZEN_UPTO = 850          # live docs cite this file by line number up to :739
POSITION_EXEMPT = {608, 609, 665, 666, 667, 668, 669, 670}   # in-place, line-count-preserving
DISPOSITIONS = [  # word-for-word disposition sentences that must survive (normalized)
    "heterogeneity — measured, but not established.",
    "is recorded below as not established.",
    "so the between-region heterogeneity is not established.",
    "finding 2 is not established (recorded 2026-09-08).",
    "#### (10b) finding 2 is not established",
    "the between-region heterogeneity in post-filter rate is not established.",
]


def norm(s):
    s = re.sub(r"[*_`]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.lower()


def unquote(s):  # drop markdown blockquote prefixes before normalizing
    return re.sub(r"(?m)^> ?", "", s)


def md5(b):
    return hashlib.md5(b).hexdigest()


def line_of(text, char_idx):
    return text.count("\n", 0, char_idx) + 1


def norm_hits(text, phrase, first_line=1):
    """(normalized substring hits) -> list of 1-based line numbers in `text` (offset by first_line-1)."""
    out, idx = [], []
    prev_sp = False
    for i, ch in enumerate(text):
        if ch in "*_`":
            continue
        if ch.isspace():
            if prev_sp:
                continue
            out.append(" "); idx.append(i); prev_sp = True
        else:
            out.append(ch.lower()); idx.append(i); prev_sp = False
    n = "".join(out); p = norm(phrase); res = []; k = n.find(p)
    while k >= 0:
        res.append(line_of(text, idx[k]) + first_line - 1)
        k = n.find(p, k + 1)
    return res


def paragraph_span(lines, anchor):
    """1-based inclusive (start, end) of the blank-line-delimited paragraph whose normalized text has anchor."""
    start = None
    spans = []
    for i, ln in enumerate(lines + [""], start=1):
        if ln.strip() == "":
            if start is not None:
                spans.append((start, i - 1)); start = None
        elif start is None:
            start = i
    hits = [s for s in spans if norm(unquote("\n".join(lines[s[0] - 1:s[1]]))).find(norm(anchor)) >= 0]
    return hits


def extract_fence(body):
    ls = body.split("\n")
    f = [i for i, ln in enumerate(ls) if ln == "`" * 4]
    if len(f) != 2:
        return None, len(f)
    return "\n".join(ls[f[0] + 1:f[1]]) + "\n", 2


def replacement_sentence(draft):
    m = re.search(r"The replacement, in substance:\n(.*?)\nThree differences", draft, re.S)
    return norm(m.group(1)) if m else None


NUM_RE = re.compile(r"(?<![\w.:/])\d[\d,]*(?:\.\d+)?(?![\w])")
STRUCT_RE = [
    r"\.planning/[^\s`)]+", r"\b20\d\d-\d\d-\d\d\b", r"\b26\d{4}-[a-z0-9]{3}\b", r"\.md:\d+-\d+", r"§\(\d+[a-e]?\)", r"§\d+",
    r"\(\d+[a-e]\)", r"scope caveat \(\d\)", r"-log10", r"c=2", r"c ?~ ?\d", r">= ?2", r"(?m)^\s*\d+\. ",
    r"\b[0-9a-f]{32}\b", r"1\.99x", r"finding \d",
    # the two metric formulas the courier states, pinned by exact text: their "- 1" terms are
    # notation, not claims. Reword either formula and the bare 1 reappears as unreconciled.
    r"\(deff - 1\)/\(phi - 1\)", r"\(phi_unc - phi_corr\)/\(phi_unc - 1\)",
]


def record_values(base_n, spec_n):
    """value -> True when the value is anchored in the record (base entry or the dgi spec)."""
    anchors = {
        "0.0326": "1.675 | 0.0326", "0.0517": "1.579 | 0.0517", "0.2171": "1.241 | 0.2171",
        "1.096": "(1.096 vs 1.359)", "1.359": "(1.096 vs 1.359)", "1.988": "| 1.988 |",
        "1.992": "| 1.992 |", "1.675": "| 1.675 |", "1.579": "| 1.579 |", "573": "npairsdualanchored 573",
        "719": "n=719", "303": "k=303", "2521": "3767/2521", "1802": "{1: 1802,", "0.728930": "icchat = 0.728930",
        "6000001": "6,000,001 bp", "1.0": "deff = 1.0", "1.2": "phi > 1.2 throughout", "0.05": "p = 0.05",
        "1.99": "observed 1.99", "21": "21 regions", "276": "regionidsselected = 276", "2.371745": "c0=2.371745",
    }
    ok = {v: (a in base_n) for v, a in anchors.items()}
    ok["2.032"] = "mean phi 2.032" in spec_n
    return ok


def derived_values():
    d = {
        "1.49": "%.2f" % -math.log10(0.0326), "1.29": "%.2f" % -math.log10(0.0517),
        "22.73": "%.2f" % (100 * 573 / 2521), "28.52": "%.2f" % (100 * 719 / 2521),
        "71.48": "%.2f" % (100 * 1802 / 2521), "0.73": "%.2f" % 0.728930, "0.729": "%.3f" % 0.728930,
        "1.360": "%.3f" % 1.360272,
        "32": "%d" % round(100 * (1.988 - 1.675) / (1.988 - 1)), "42": "%d" % round(100 * (1.992 - 1.579) / (1.992 - 1)),
        "1.19": "%.2f" % (1.988 / 1.675), "1.26": "%.2f" % (1.992 / 1.579),
        "19": "%d" % round(100 * (1.19 - 1) / (1.988 - 1)), "26": "%d" % round(100 * (1.26 - 1) / (1.992 - 1)),
    }
    return {k: (k == v) for k, v in d.items()}


def classify_numbers(text, allowed, label, results, cid):
    t = text.lower()
    for pat in STRUCT_RE:
        t = re.sub(pat, " ", t)
    bad = []
    for m in NUM_RE.finditer(t):
        tok = m.group(0).replace(",", "")
        if not allowed.get(tok, False):
            bad.append(tok)
    results.append((cid, not bad, "%s: unreconciled numeric tokens %s" % (label, sorted(set(bad))) if bad
                    else "%s: every numeric token reconciled" % label))


def run(base_p, after_p, bank_p, courier_p, reply_p, draft_p, spec_p):
    R = []
    base = open(base_p, encoding="utf-8").read()
    after = open(after_p, encoding="utf-8").read()
    bank = open(bank_p, encoding="utf-8").read()
    courier = open(courier_p, encoding="utf-8").read()
    reply_b = open(reply_p, "rb").read(); reply = reply_b.decode("utf-8")
    draft_b = open(draft_p, "rb").read(); draft = draft_b.decode("utf-8")
    spec_lines = open(spec_p, encoding="utf-8").read().split("\n")
    spec_n = norm("\n".join(spec_lines[44:56]))           # CONTENT-SPEC.md:45-56
    BL = base.split("\n"); AL = after.split("\n")
    if base.count(ENTRY_HEAD) != 1 or after.count(ENTRY_HEAD) != 1:
        R.append(("G00-entry-head", False, "entry heading count base %d after %d (want 1/1)"
                  % (base.count(ENTRY_HEAD), after.count(ENTRY_HEAD))))
        return R
    R.append(("G00-entry-head", True, "2026-09-03 entry heading present once in base and after"))
    b_entry0 = base.index(ENTRY_HEAD); a_entry0 = after.index(ENTRY_HEAD)
    b_entry = base[b_entry0:]; a_entry = after[a_entry0:]
    a_entry_first = line_of(after, a_entry0)
    base_n = norm(unquote(b_entry)); after_n = norm(unquote(a_entry))
    paste, nf = extract_fence(courier)
    bank_body, nbf = extract_fence(bank)

    # G01 - banned superseded literals: no increase in osf; zero in both new files and the paste block
    for lit in BANNED:
        b, a = norm(base).count(lit), norm(after).count(lit)
        R.append(("G01-osf-" + lit, a <= b, "osf normalized count base %d after %d" % (b, a)))
        for nm, body in (("bank", bank), ("courier", courier), ("paste", paste or "")):
            c = norm(body).count(lit)
            R.append(("G01-%s-%s" % (nm, lit), c == 0, "%s count %d" % (nm, c)))

    # G02 - status line and every NOT ESTABLISHED survive
    R.append(("G02-status-line", STATUS_LINE in after and after.count(STATUS_LINE) == base.count(STATUS_LINE) == 1,
              "exact status line present once"))
    for ph in ("drafted — not posted", "not established"):
        b, a = norm(base).count(ph), norm(after).count(ph)
        R.append(("G02-count-" + ph.split()[0], a >= b, "'%s' base %d after %d" % (ph, b, a)))
    for s in DISPOSITIONS:
        R.append(("G02-disposition", s in norm(after), "word-for-word: %r" % s))

    # regions in AFTER (1-based line numbers)
    uer = paragraph_span(AL, UER_ANCHOR); s7 = paragraph_span(AL, S7_ANCHOR)
    e10 = [i + 1 for i, ln in enumerate(AL) if ln == E10_HEAD]
    R.append(("G03-regions", len(uer) == 1 and len(s7) == 1 and len(e10) == 1,
              "uer paragraph %s, S7 paragraph %s, (10e) heading lines %s" % (uer, s7, e10)))
    uer = uer[0] if len(uer) == 1 else (0, -1); s7 = s7[0] if len(s7) == 1 else (0, -1)
    e10s = e10[0] if len(e10) == 1 else 10 ** 9
    in_uer = lambda n: uer[0] <= n <= uer[1]
    in_s7 = lambda n: s7[0] <= n <= s7[1]
    in_e10 = lambda n: n >= e10s

    # G03 - removed framing: only in the historical uer correction paragraph or the new (10e) note
    print("  enumeration G03 (framing phrases in the 2026-09-03 entry, AFTER):")
    for ph in ("straddl", "coin", "artifact of analytic choice"):
        for n in norm_hits(a_entry, ph, a_entry_first):
            where = "uer-correction-log" if in_uer(n) else ("(10e)" if in_e10(n) else "ELSEWHERE")
            print("    %-28s line %4d  %s" % (ph, n, where))
            R.append(("G03-framing", where != "ELSEWHERE", "%r at line %d -> %s" % (ph, n, where)))
    for ph in ("interchangeab", "equally defensible"):
        for n in norm_hits(a_entry, ph, a_entry_first):
            where = "S7-scoped" if in_s7(n) else ("(10e)" if in_e10(n) else "ELSEWHERE")
            print("    %-28s line %4d  %s" % (ph, n, where))
            R.append(("G03b-scoped", where != "ELSEWHERE", "%r at line %d -> %s" % (ph, n, where)))

    # G12 - changed-line census: only the planned sites move
    sm = difflib.SequenceMatcher(None, BL, AL, autojunk=False)
    changed_after = []
    census = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        census.append("%s base %d-%d -> after %d-%d" % (tag, i1 + 1, i2, j1 + 1, j2))
        if tag in ("replace", "delete"):
            ok = all((k + 1) in ALLOWED_REPLACED for k in range(i1, i2))
        else:
            ok = i1 in ALLOWED_INSERT_AFTER
        R.append(("G12-census", ok, "%s base %d-%d -> after %d-%d" % (tag, i1 + 1, i2, j1 + 1, j2)))
        if tag in ("replace", "insert"):
            changed_after.append((j1 + 1, "\n".join(AL[j1:j2])))
    print("  census: " + "; ".join(census))

    # G14 - line positions frozen up to :850 (live docs cite by line number); S1/S2 are in place
    moved = [k + 1 for k in range(POSITION_FROZEN_UPTO) if (k + 1) not in POSITION_EXEMPT and BL[k] != AL[k]]
    R.append(("G14-positions", not moved, "lines 1-%d identical except in-place S1/S2; moved %s"
              % (POSITION_FROZEN_UPTO, moved[:5])))

    # G04 - nothing says or implies clustering EXPLAINS Finding 2
    print("  enumeration G04 ('explain' family in new/changed text):")
    for first, blk in changed_after:
        bn = norm(unquote(blk))
        for m in re.finditer(r"explain|explanat|accounts? for|reproduc", bn):
            pre = bn[max(0, m.start() - 60):m.start()]
            ok = pre.endswith("not robustly distinguishable from a clustering-only ") or re.search(r"without showing (that )?it $", pre) is not None
            kind = "hypothesis-label (negated)" if "clustering-only" in pre[-20:] else ("negated" if ok else "NOT NEGATED")
            print("    block@%d: ...%s[%s]  %s" % (first, pre[-45:], m.group(0), kind))
            R.append(("G04-explain", ok, "block@%d %r -> %s" % (first, pre[-40:] + m.group(0), kind)))
    pos = r"clustering\s+(alone\s+)?(explains|accounts for|reproduces)|explained by\s+(the\s+)?(within-window\s+)?clustering"
    b, a = len(re.findall(pos, base_n)), len(re.findall(pos, after_n))
    R.append(("G04-positive-claim", a <= b and a == 0, "positive 'clustering explains' forms base %d after %d" % (b, a)))

    # G04c - the courier is new text too: every explain-family or share claim in the paste block
    # must be the negated hypothesis label, negated outright, or a double-quoted attribution.
    print("  enumeration G04c ('explain' family + share claims in the courier paste block):")
    for ln in (paste or "").split("\n"):
        lnn = norm(ln)
        for m in re.finditer(r"explain|explanat|accounts? for|reproduc|carries \S+% of the excess", lnn):
            pre = lnn[:m.start()]
            qs = [i for i, ch in enumerate(lnn) if ch == '"']
            quoted = any(qs[k] < m.start() and m.end() <= qs[k + 1] for k in range(0, len(qs) - 1, 2))
            label = pre.endswith("not robustly distinguishable from a clustering-only ")
            negated = re.search(r"without showing (that )?it $", pre) is not None
            kind = ("hypothesis-label (negated)" if label else "negated" if negated
                    else "quoted attribution" if quoted else "NOT NEGATED")
            print("    %-26s %s" % (m.group(0), kind))
            R.append(("G04c-courier", label or negated or quoted, "%r -> %s" % (m.group(0), kind)))
    pshare = [ln for ln in (paste or "").split("\n") if "36%" in ln]
    R.append(("G07c-courier-share",
              all(("your 36%" in norm(ln)) or ("not 36%" in norm(ln)) for ln in pshare) and (paste or "").count("64%") == 0,
              "36%% appears on %d line(s), each attributed; 64%% count %d" % (len(pshare), (paste or "").count("64%"))))

    # G05 - numeric reconciliation of every changed block and of the courier paste block
    rec = record_values(base_n, spec_n); der = derived_values()
    R.append(("G05-record-anchors", all(rec.values()), "record anchors missing: %s" % [k for k, v in rec.items() if not v]))
    R.append(("G05-derived", all(der.values()), "derived recompute mismatches: %s" % [k for k, v in der.items() if not v]))
    # PARSED from the AFTER text rather than hardcoded: the cluster-size distribution bullet is the
    # only place the panel's own dict appears, and every D3 figure must follow from THAT dict.
    dm = re.findall(r"\{1: \d+(?:, \d+: \d+)*\}", after)
    if len(dm) != 1:
        R.append(("G05-cluster-arith", False, "cluster-size distribution dict found %d time(s) in AFTER (want 1)" % len(dm)))
    else:
        dist = {int(c): int(k) for c, k in re.findall(r"(\d+): (\d+)", dm[0])}
        n_pairs = sum(c * k for c, k in dist.items())
        singles = dist.get(1, 0)
        clustered = sum(c * k for c, k in dist.items() if c >= 2)
        kcl = sum(k for c, k in dist.items() if c >= 2)
        sum_c2 = sum(c * c * k for c, k in dist.items())
        R.append(("G05-cluster-arith",
                  n_pairs == 2521 and singles == 1802 and n_pairs - singles == 719 and clustered == 719
                  and kcl == 303 and sum_c2 == 3767,
                  "parsed %s -> pairs %d, singletons %d, in clusters>=2 %d, k(c>=2) %d, sum c^2 %d"
                  " (want 2521 / 1802 / 719 / 303 / 3767)" % (dm[0], n_pairs, singles, clustered, kcl, sum_c2)))
    osf_allowed = {k: True for k, v in rec.items() if v}
    osf_allowed.update({k: True for k in ("1.49", "1.29", "22.73", "28.52", "71.48", "0.73") if der[k]})
    for first, blk in changed_after:
        classify_numbers(blk, osf_allowed, "osf block@%d" % first, R, "G05-osf")
    reviewer_n = norm(reply)
    courier_allowed = dict(osf_allowed)
    courier_allowed.update({k: True for k, v in der.items() if v})
    courier_allowed.update({k: (k in reviewer_n) for k in ("36", "64", "0.03", "22.7", "28.5")})
    classify_numbers(paste or "", courier_allowed, "courier paste block", R, "G05-courier")

    # G06 - decisions present (D1-D4, D6) and the courier sentence matches the disclosure
    rs = replacement_sentence(draft)
    R.append(("G06-D8-sentence", rs is not None and after_n.count(rs) == 1 and norm(paste or "").count(rs) == 1,
              "draft replacement sentence: osf x%d, paste x%d" % (after_n.count(rs or "\0"), norm(paste or "").count(rs or "\0"))))
    need = [
        ("G06-D1", "at most weak", 5), ("G06-D1", "-log10 p 1.49 and 1.29, the same evidence", 1),
        ("G06-D1", "five na regions carry deff 1.0", 2), ("G06-D1", "not robustly distinguishable from a clustering-only explanation", 4),
        ("G06-D2", "post-hoc selection", 2), ("G06-D2", "not statistically equivalent", 2),
        ("G06-D2", "equally defensible handling choices made in advance", 2), ("G06-D2", "neither is selected", 1),
        ("G06-D3", "pairs in clusters of size >= 2: 719 of 2521 = 28.52%", 1), ("G06-D3", "1,802 of 2521 (71.48%)", 1),
        ("G06-D3", "this icc describes those 719 pairs (28.52% of 2521) only", 1),
        ("G06-D3", "does not describe the 1,802 singletons (71.48%)", 1), ("G06-D3", "per-region sum basis (scope caveat (1))", 1),
        ("G06-D4", "was his, and it was wrong", 1), ("G06-D4", "c=2 simulation were ours", 1),
        ("G06-D4", "confirmed that within-window clustering exists (icc 0.73", 1),
        ("G06-D4", "without showing that it accounts for the dispersion", 1),
        ("G06-D4", "rao-scott test was proposed by neither party", 1), ("G06-D4", "he declined that credit", 1),
        # W1: the (10e) scoping bullet must not appear to deny that he accepted the disposition.
        ("G06-W1", "does not record his acceptance of the scoping decided here", 1),
        # W7: (10e) must name the third aligned restatement, because the frozen note mis-names it.
        ("G06-W7", "the third was in fact §(2) — §(7) carried the design effect, never the straddle", 1),
    ]
    for cid, ph, k in need:
        R.append((cid, after_n.count(ph) >= k, "%r x%d (need >= %d)" % (ph, after_n.count(ph), k)))
    R.append(("G06-W1-old", "does not record the reviewer's acceptance of this disposition" not in after_n,
              "the superseded W1 sentence is absent"))
    for q in ("the operative dependence is within-window: pairs sharing an occluding deletion do not flip independently",
              "c=2, icc 1.0 -> mean phi 2.032"):
        R.append(("G06-D4-quote", q in spec_n and q in after_n, "quote in CONTENT-SPEC:45-56 %s, in osf %s" % (q in spec_n, q in after_n)))
    s7n = norm("\n".join(AL[s7[0] - 1:s7[1]])) if s7[1] >= s7[0] else ""
    R.append(("G06-D2-adjacent", all(x in s7n for x in ("1.096 vs 1.359", "0.0326", "0.0517")),
              "design effects sit in the same paragraph as both p-values"))
    heads = [i + 1 for i, ln in enumerate(AL) if ln.startswith("#### ")]
    d10 = [i + 1 for i, ln in enumerate(AL) if ln.startswith("#### (10d)")]
    R.append(("G06-D6-heading", len(e10) == 1 and heads and heads[-1] == e10[0] and d10 and d10[0] < e10[0],
              "(10e) heading once, last '#### ' heading, after (10d)"))
    e10n = norm(after[after.find(E10_HEAD):]) if E10_HEAD in after else ""
    for q in ("straddle p = 0.05", "a coin-flip between two equally defensible analyses", "is an artifact of analytic choice"):
        R.append(("G06-D6-quote-fidelity", q in base_n and ('"%s"' % q) in e10n,
                  "(10e) quotes, in double quotes, removed framing that existed in base: %r" % q))

    # G07 - D5: no share figure, no 'universal', no 'no geometric predicate'; Finding 1 text unchanged
    share = r"(?<![\d.])(36|64)\s*%"
    R.append(("G07-share", len(re.findall(share, norm(after))) == len(re.findall(share, norm(base))) == 0, "36%/64% in osf"))
    for ph in ("universal", "no geometric predicate"):
        R.append(("G07-" + ph.split()[0], norm(after).count(ph) == norm(base).count(ph) == 0, "%r in osf" % ph))
    b10d = base[base.index("#### (10d)"):]
    a10d = after[after.index("#### (10d)"):after.index(E10_HEAD)] if E10_HEAD in after else ""
    R.append(("G07-finding1-10d", a10d == b10d + "\n", "(10d) section byte-identical"))

    # G08 - frozen: lines 1..566, the uer correction paragraph, the (10b) table
    R.append(("G08-head566", BL[:566] == AL[:566], "lines 1-566 byte-identical"))
    bu = paragraph_span(BL, UER_ANCHOR)
    R.append(("G08-uer-paragraph", len(bu) == 1 and BL[bu[0][0] - 1:bu[0][1]] == AL[uer[0] - 1:uer[1]],
              "uer correction paragraph byte-identical (historical; numbers untouched)"))
    bt = [ln for ln in BL if ln.startswith("| ")]
    at = [ln for ln in AL if ln.startswith("| ")]
    R.append(("G08-table", bt == at, "(10b) table rows byte-identical"))

    # G09 - bank file: provenance header + byte-verbatim fenced body
    R.append(("G09-bank-fence", nbf == 2 and bank_body is not None and bank_body.encode("utf-8") == reply_b,
              "exactly 2 fence lines; fenced body == scratch reply bytes"))
    R.append(("G09-bank-header", md5(reply_b) in bank and ("%d B, %d lines" % (len(reply_b), reply.count("\n"))) in bank
              and "not byte-verified" in norm(bank.split("`" * 4)[0]),
              "header carries md5 %s, %d B, %d lines, not byte-verified" % (md5(reply_b), len(reply_b), reply.count("\n"))))

    # G10 - courier: status header + byte-verbatim paste block
    R.append(("G10-courier-status", "**Status:** DRAFTED 2026-09-17, **NOT SENT**. No agent contacts Seth — Carter sends it." in courier,
              "status header present"))
    R.append(("G10-courier-fence", nf == 2 and paste is not None and paste.encode("utf-8") == draft_b,
              "exactly 2 fence lines; paste block == scratch draft bytes"))
    R.append(("G10-courier-header", md5(draft_b) in courier and ("%d B" % len(draft_b)) in courier,
              "header carries draft md5 and byte count"))
    return R


def main():
    if len(sys.argv) != 8:
        print(__doc__)
        return 2
    R = run(*sys.argv[1:])
    fails = [r for r in R if not r[1]]
    for cid, ok, detail in R:
        print("%s  %-24s %s" % ("PASS" if ok else "FAIL", cid, detail))
    print("\nRESULT %s  %d/%d PASS" % ("GREEN" if not fails else "RED", len(R) - len(fails), len(R)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
````
<!-- END EMBEDDED irg_guard.py -->

<!-- BEGIN EMBEDDED irg_negctl.py md5=584d4df53807fe5618ba14d1e38b1fa3 -->
````python
#!/usr/bin/env python3
"""irg_negctl.py - quick-260917-irg. Proves every irg_guard.py check family can go RED.

usage: irg_negctl.py GUARD_DIR BASE_OSF AFTER_OSF BANK COURIER REPLY_TXT DRAFT_TXT DGI_CONTENT_SPEC WORK_DIR
Positive control first (unmutated -> all PASS), then each mutation must (a) change the text
exactly once and (b) turn EVERY expected check id RED. exit 0 only if all of that holds.
WORK_DIR must be outside the repo (scratch).
"""
import os, sys

GUARD_DIR = sys.argv[1]
sys.path.insert(0, GUARD_DIR)
import irg_guard as G  # noqa: E402

base_p, after_p, bank_p, courier_p, reply_p, draft_p, spec_p, work = sys.argv[2:10]
A0 = open(after_p, encoding="utf-8").read()
B0 = open(bank_p, encoding="utf-8").read()
C0 = open(courier_p, encoding="utf-8").read()

# (control id, file to mutate: osf|bank|courier, old, new, expected RED check ids)
CONTROLS = [
    ("N01", "osf", "run in reverse.", "run in reverse (**0.0366**).", ["G01-osf-0.0366"]),
    ("N02", "courier", "Seth — taken in order.", "Seth — taken in order. 1.652", ["G01-paste-1.652", "G01-courier-1.652"]),
    ("N03", "bank", "One objection to the", "One 1.969 objection to the", ["G01-bank-1.969"]),
    ("N04", "osf", "- **Status:** DRAFTED — NOT POSTED;", "- **Status:** DRAFTED — POSTED;", ["G02-status-line"]),
    ("N05", "osf", "> The between-region heterogeneity in POST-filter rate is **NOT ESTABLISHED**. Under either",
     "> The between-region heterogeneity in POST-filter rate is **ESTABLISHED**. Under either", ["G02-disposition"]),
    ("N06", "osf", "weak evidence** under either **defensible**",
     "weak evidence** (the two **STRAD**DLE the threshold) under either **defensible**", ["G03-framing"]),
    ("N07", "osf", "(p 0.0326 / p 0.0517; p 0.2171 dropping both).\n  **Finding 2",
     "(a coin\n  flip; p 0.0326 / p 0.0517; p 0.2171 dropping both).\n  **Finding 2", ["G03-framing", "G14-positions"]),
    ("N08", "osf", "the between-region heterogeneity in POST-filter rate carries **at most",
     "the between-region heterogeneity in POST-filter rate (interchangeably) carries **at most", ["G03b-scoped"]),
    ("N09", "osf", "singletons, which the ICC does not describe.",
     "singletons, which the ICC does not describe. Within-window clustering explains the dispersion.",
     ["G04-explain", "G04-positive-claim"]),
    ("N10", "osf", "is **not robustly\n  distinguishable from a clustering-only explanation**, and its",
     "is **a clustering-only explanation**, and its", ["G04-explain"]),
    ("N11", "osf", "719 of 2521 = 28.52%**", "719 of 2521 = 28.5%**", ["G05-osf", "G06-D3"]),
    ("N12", "osf", "-log10 p **1.49** vs **1.29**", "-log10 p **1.48** vs **1.29**", ["G05-osf"]),
    ("N13", "courier", "(-log10 p 1.49 and 1.29, the same", "(-log10 p 1.49 and 1.30, the same",
     ["G06-D8-sentence", "G05-courier", "G10-courier-fence"]),
    ("N14", "osf", "or any other criterion, would be **post-hoc selection**. The evidence",
     "or any other criterion, would be **selection**. The evidence", ["G06-D2"]),
    ("N15", "osf", "an occluding deletion do not flip independently\"*", "an occluding deletion do not flip together\"*",
     ["G06-D4-quote"]),
    ("N16", "osf", "analyses stay reported.", "analyses stay reported; clustering carries 36% of the excess.", ["G07-share"]),
    ("N17", "osf", "- **Finding 1's text is unchanged.**", "- **Finding 1's text is unchanged; it is universal.**", ["G07-universal"]),
    ("N18", "osf", "It is **COUNTING, NOT INFERENCE**", "It is **COUNTING, not inference**", ["G07-finding1-10d"]),
    ("N19", "osf", "not independently verifiable from the NC-State node", "not independently verifiable from the NC-state node",
     ["G08-head566", "G14-positions", "G12-census"]),
    ("N27", "osf", "## 2026-09-03 — AFR native-panel", "## 2026-09-03 — AFR native panel", ["G00-entry-head"]),
    ("N20", "osf", "previously 0.0366 vs 0.0556", "previously 0.0366 vs 0.0557", ["G08-uer-paragraph", "G12-census"]),
    ("N21", "osf", "  both), so the between-region heterogeneity is NOT ESTABLISHED.**",
     "  both),\n  so the between-region heterogeneity is NOT ESTABLISHED.**", ["G14-positions"]),
    ("N22", "osf", "NEITHER fired.**", "NEITHER fired!**", ["G12-census"]),
    ("N23", "bank", "Finding 1\tThe result. Untouched.", "Finding 1 The result. Untouched.", ["G09-bank-fence"]),
    ("N24", "courier", "Seth — taken in order", "Seth - taken in order", ["G10-courier-fence"]),
    ("N25", "osf", "#### (10e) REVIEWER RESPONSE 2026-09-17", "#### (10e) REVIEWER RESPONSE, 2026-09-17",
     ["G06-D6-heading", "G03-regions"]),
    ("N26", "osf", "| 1.241                | 0.2171     |", "| 1.242                | 0.2171     |", ["G08-table", "G12-census"]),
    ("N28", "courier", "So no share goes", "Clustering carries 36% of the excess. So no share goes",
     ["G04c-courier", "G07c-courier-share", "G10-courier-fence"]),
    ("N29", "courier", 'One phrase, "clustering carries X% of the excess", supports',
     "One phrase, clustering carries X% of the excess, supports", ["G04c-courier", "G10-courier-fence"]),
    ("N30", "courier", "Your 36% is (deff", "The 36% is (deff", ["G07c-courier-share", "G10-courier-fence"]),
    # --- W2: the parsed cluster-size distribution, plus controls for ids that had none ---
    ("N31", "osf", "`{1: 1802, 2: 239, 3: 40, 4: 12, 5: 4, 6: 5, 7: 1, 8: 2}`",
     "`{1: 1802, 2: 240, 3: 40, 4: 12, 5: 4, 6: 5, 7: 1, 8: 2}`", ["G05-cluster-arith", "G12-census"]),
    ("N32", "osf", "carry **different measured design effects (1.096 vs 1.359)**, which is",
     "carry **different measured design effects**, which is", ["G06-D2-adjacent"]),
    ("N33", "osf", "- **Finding 1's text is unchanged.**",
     "- **Finding 1's text is unchanged; no geometric predicate is claimed.**", ["G07-no"]),
    ("N34", "courier", "**Status:** DRAFTED 2026-09-17, **NOT SENT**.", "**Status:** drafted 2026-09-17, **NOT SENT**.",
     ["G10-courier-status"]),
    ("N35", "bank", "8316 B, 60 lines", "8316 B, 61 lines", ["G09-bank-header"]),
    ("N39", "osf", "does not record his acceptance of the scoping decided here",
     "does not record the reviewer's acceptance of this disposition", ["G06-W1", "G06-W1-old"]),
    ("N40", "osf", "the third was in fact **§(2)** — §(7) carried", "the third was in fact **§(7)** — §(7) carried",
     ["G06-W7"]),
    # --- base-mutating controls: these are the only way to falsify the base-relative checks ---
    ("N36", "base", "  c0=2.371745).", "  c0 = 2.371745).", ["G05-record-anchors"]),
    ("N37", "base", "**Finding 2 — between-region heterogeneity in the POST-filter rate — is recorded below as",
     "**Finding 2 — NOT ESTABLISHED, NOT ESTABLISHED — is recorded below as", ["G02-count-not"]),
    ("N38", "base", "- ⛔ **The status is unchanged: DRAFTED — NOT POSTED.** **Discharging the last open item is NOT",
     "- ⛔ **The status is unchanged: DRAFTED — NOT POSTED. DRAFTED — NOT POSTED. DRAFTED — NOT POSTED.**"
     " **Discharging the last open item is NOT",
     ["G02-count-drafted"]),
    ("N41", "osf", "hypothesis (same-parent sub-window replication) was **his, and it was wrong** — the bullet above;",
     "hypothesis (same-parent sub-window replication) was **his** — the bullet above;", ["G06-D4"]),
    ("N42", "courier", "`042fe4798429f30fa5b4bbb59dee9419`, 4587 B", "`042fe4798429f30fa5b4bbb59dee9418`, 4587 B",
     ["G10-courier-header"]),
]


BASE0 = open(base_p, encoding="utf-8").read()


def run_with(a, b, c, tag, base=None):
    """base=None -> the real base file; otherwise a mutated copy written into the work dir.
    Mutating the base is how the base-relative checks (count >= base, record anchors) are controlled."""
    d = os.path.join(work, tag)
    os.makedirs(d, exist_ok=True)
    paths = []
    for fn, body in (("osf.md", a), ("bank.md", b), ("courier.md", c)):
        p = os.path.join(d, fn)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(body)
        paths.append(p)
    bp = base_p
    if base is not None:
        bp = os.path.join(d, "base.md")
        with open(bp, "w", encoding="utf-8") as fh:
            fh.write(base)
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        R = G.run(bp, paths[0], paths[1], paths[2], reply_p, draft_p, spec_p)
    return sorted({cid for cid, ok, _ in R if not ok})


def main():
    bad = 0
    red0 = run_with(A0, B0, C0, "positive")
    print("POSITIVE CONTROL (unmutated): FAIL ids = %s -> %s" % (red0, "GREEN" if not red0 else "NOT GREEN"))
    bad += bool(red0)
    for cid, which, old, new, expect in CONTROLS:
        a, b, c, base = A0, B0, C0, None
        src = {"osf": a, "bank": b, "courier": c, "base": BASE0}[which]
        n = src.count(old)
        if n != 1:
            print("%s  INVALID CONTROL: old text occurs %d times in %s" % (cid, n, which))
            bad += 1
            continue
        mut = src.replace(old, new, 1)
        if which == "osf":
            a = mut
        elif which == "bank":
            b = mut
        elif which == "courier":
            c = mut
        else:
            base = mut
        red = run_with(a, b, c, cid, base)
        missing = [e for e in expect if e not in red]
        lit = ""
        if cid == "N06":
            line = [ln for ln in a.split("\n") if "DLE the threshold" in ln][0]
            lit = " | literal line-grep 'straddl' on the mutated line: %d (normalized guard RED)" % line.lower().count("straddl")
        print("%s  %-8s expect RED %s -> observed RED %s  %s%s" % (cid, which, expect, red,
                                                               "OK" if not missing else "MISSING %s" % missing, lit))
        bad += bool(missing)
    print("\nNEGCTL RESULT: %s" % ("ALL CONTROLS OBSERVED RED" if not bad else "%d PROBLEM(S)" % bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
````
<!-- END EMBEDDED irg_negctl.py -->
