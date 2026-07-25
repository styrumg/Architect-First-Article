# Worked example: a payment worker through the three gates

A complete, staged pass through the pipeline described in the paper, using a
small three-actor system (payment `worker`, its `supervisor`, and a
`payment_gateway`). The full SIM/FAM schemas and the curated knowledgebase are
intentionally held back until cold-test validation (see the paper, Section 10);
this example exists to show the pipeline *runs* and *catches* things.

## The story, in order

| # | File | What happens |
|---|------|--------------|
| 0 | `00-requirements.md` | The thin prose ticket — happy path clear, failure vague. |
| 1 | `01-sim-initial.json` | The agent's first SIM draft: fire-and-forget `ChargePayment`, weak dedup, no restart bound. |
| 2 | `02-gate1-initial-report.json` | **Gate 1 BLOCK** (H3a blocking: payment command at-most-once with no ack) + high findings (H4 restart bound, H13 supervision). |
| 3 | `03-decision-memory.jsonl` | Loop Zero / review: each gap resolved and recorded (delivery semantics, restart cap, shutdown drain, gateway-enforced dedup). |
| 4 | `04-sim-passing.json` | Revised SIM: ack'd at-least-once with idempotent receivers **and** a named dedup mechanism, gateway-enforced idempotency, bounded restart, `supervised_by`, dependencies declared. |
| 5 | `05-gate1-passing-report.json` | **Gate 1 SOUND** (0 blocking, 0 high; one medium H14 note requiring an explicit compensating-control decision for the safety-path dependency (answered in `03-decision-memory.jsonl`)). |
| 6 | `06-payment-worker.fam.json` | The FAM lowered from the passing SIM — same states/events, element-level `trace`, guards with code locations, `derived_from` → `04-sim-passing.json`. |
| 7 | `07-gate2-report.json` | **Gate 2 SOUND** — all six check families report (F1 completeness, F2 block/property, F3 lowering integrity + traceability, F4 port match, F5 guards located, F6 handlers named). |
| 8 | `code/payment-worker-vulnerable.py` → `08-gate3-vulnerable-report.json` | A full FAM implementation (same handlers, restart limiter, gateway-side idempotency adapter, durable order-ID dedup, terminal `stopped` shutdown state with a declared drain-timeout policy) with deliberate **code-level** defects → **Gate 3 BLOCK** (2 blocking shell invocations, pickle, bare `except`, CPU spin). |
| 9 | `code/payment-worker-fixed.py` → `09-gate3-fixed-report.json` | The same design with the defects removed → **Gate 3 SOUND** (0 findings). |

## The point

Each gate catches what the others can't. Gate 1 blocks the fire-and-forget
payment before any design exists. Gate 2 verifies the design's tables are total
and traceable to the approved intent. Gate 3 shows that an *approved design can
still produce bad code* — the vulnerable and fixed files implement the **same**
FAM; only the emission differs. The agent proposes; the gates dispose; the
decision memory remembers why.

The two SIM files and the two code files are deliberately two rounds of the
same artifacts: that is the loop working, not four different systems.
