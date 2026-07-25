# Changelog

Internal revision history.

## rev 5.21 — 2026-07-26  (trunk, working toward Preprint v1.1)
- **Determinism scoped** (de-0083): §5 "same SIM → same report" now limited to
  deterministic checks; §7.5 states the three properties explicitly —
  deterministic policy and replayable decision hold, fresh recheck does not
  when a probabilistic sensor participates. Blocking authority stays with the
  policy over a frozen, hashed evidence bundle.
- **Related Work + References** — added MemoHarness (arXiv:2607.14159) and
  AIDE² (Weco AI) as complementary plant-side harness-learning work; §8.3
  cross-reference to AIDE² as RSI Level-1 evidence (Level-2 ignition not achieved).

 Public releases are tagged separately; the first
public release is **v1.0**, built from internal **rev 5.20**.

## rev 5.20 — 2026-07-25  (= public v1.0)
Release-readiness pass (driven by external review):
- Added **Related Work** and **References** sections (LLVM, MLIR, proof-carrying
  code, PagerDuty, CodeRabbit, Claude Security, CRA/EU 2024/2847, LabVIEW/J-Crawler,
  control theory). CodeRabbit flagged as vendor-reported.
- Resolved the **H11 contradiction**: H11 moved to a labeled human-review lane;
  §5 now says "thirteen-plus-one implemented as code, one routed to human review."
- Reduced the **CRA overclaim**: "compliance report" → "compliance evidence
  report"; the agent retrieves versioned requirements and assembles evidence,
  flags applicability/conformity questions for qualified review — it does not certify.
- **Gate 3 determinism precision**: Gates 1–2 deterministic over structured
  artifacts; Gate 3 has a deterministic policy core over frozen analyzer
  evidence while individual sensors may be probabilistic.
- Editorial/technical fixes: §9 count ("Several, plainly"); compiler lowers a
  formal source language (not English); synchronous-remote-call caveat;
  "mature" (not "solved") SAST; "executable consumer is a machine";
  "two diverse sensors"; punctuation.
- Added a short **abstract** to the cover.

## rev 5.19 — 2026-07-25
- §8.3 hardened: control-plane vs data-plane; non-authoritative rationale;
  policy-manipulation → sensor-evasion; diverse ≠ independent sensors;
  semantic-quarantine principle; §8.3.1 "Verification Without Conversation"
  (four message types; stage-progressive evidence; reproducible/snapshotted/
  revalidated).

## rev 5.17–5.18 — 2026-07-25
- Conclusion capstone (control-system framing); §5 explicit plant/controller
  mapping and the two timescales (operational vs adaptation).

## rev 5.16 — 2026-07-25
- §5 Bayesian refinement: the decision procedure is deterministic, the world
  model is not; beliefs vs commitments.

## rev 5.15 — 2026-07-25
- §5: the general law (discover/observe, never decide) and the three
  determinisms (execution / representation / evolution).

## rev 5.13–5.14 — 2026-07-25
- Scout/Sensor/Gate roles codified (§8.1); §9 Seventh limit flipped from
  confession to premise (constrained representations; declared commitments).

## rev 5.10–5.12 — 2026-07-24/25
- §8.3 alignment paragraphs: prompt ≠ gate; output guards + capability denial;
  sensor/router split (eyes may be AI, spine may not).

## rev 5.9 — 2026-07-24
- §8.3 added: the self-improving-agent / AGI stress test.

(Earlier internal revisions 5.0–5.8 covered the FAM, the three gates,
Loop Zero, the Discovery Loop, and the H14 appendix promotion.)
