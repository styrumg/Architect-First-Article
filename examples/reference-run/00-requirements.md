# Requirements: payment worker (worked example)

> The prose the coding agent was given — deliberately written like a real
> ticket: clear on the happy path, vague on failure.

## Ticket

We need a worker that processes payment orders.

- It pulls orders off a queue and charges the customer.
- On success it emits a receipt.
- If a worker dies it should be restarted — but don't let it flap forever, cap it.
- Never double-charge, even if the queue redelivers.
- There should be a clean shutdown for deploys.

## Left open (on purpose)

Delivery semantics, idempotency, the numeric restart cap, what happens to an
in-flight charge on shutdown, and what "clean" means. The agent must resolve
these via Loop Zero / explicit declaration — see `03-decision-memory.jsonl`.
