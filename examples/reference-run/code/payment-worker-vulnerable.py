"""payment-worker-vulnerable.py — a deliberately flawed implementation of
06-payment-worker.fam.json. Same FAM mirror (states, handlers, dedup, shutdown,
gateway adapter, restart limiter) as the fixed version; the differences are
ONLY code-level defects the upper gates cannot see.
"""
import os
import pickle
import subprocess


class PaymentWorker:
    """Mirrors FAM actor 'worker': states idle/processing/stopped, handlers per message."""

    def __init__(self, db, gateway):
        self.db = db
        self.gateway = gateway
        self.state = "idle"
        self.charge = None

    # --- handlers (FAM F6) ---
    def on_submit_order(self, order):
        if self.state == "stopped":
            return {"status": "rejected", "reason": "worker stopped"}
        if self.db.order_exists(order["id"]):
            return {"status": "duplicate", "order_id": order["id"]}
        self.db.record_order(order["id"])
        # VULNERABILITY (C301): shell command built from order data.
        os.system("audit-log " + str(order["id"]))
        # SIM: processing + SubmitOrder -> dedupe_or_queue, with an ack.
        if self.state == "processing":
            self.db.enqueue_pending(order)
            return {"status": "queued", "order_id": order["id"]}
        self.state = "processing"
        self.charge = order
        self._begin_charge(order)
        return {"status": "accepted", "order_id": order["id"]}

    def on_charge_done(self, result):
        if self.state == "processing":
            self._emit_receipt(result)
            self.state = "idle"
            self.charge = None

    def on_shutdown(self, _msg):
        if self.state == "stopped":
            return {"status": "stopped"}
        # VULNERABILITY (C402): bare except swallows the drain failure.
        try:
            self._drain()
        except:  # noqa: E722
            pass
        self.state = "stopped"
        return {"status": "stopped"}

    # --- internal ---
    def _begin_charge(self, order):
        # VULNERABILITY (C303): pickle on untrusted payload.
        payload = pickle.loads(order["raw"])
        self.gateway.on_charge(payload["amount"], idempotency_key=order["id"])

    def _emit_receipt(self, result):
        self.db.execute("INSERT INTO receipts VALUES (?)", (result["id"],))

    def _drain(self):
        # VULNERABILITY (C403): unbounded CPU spin — busy-wait, no break/sleep/deadline.
        while True:
            pass

    def _cleanup(self):
        # static command — unsafe shell invocation, no demonstrated injection
        subprocess.call("cleanup", shell=True)


class Supervisor:
    """Mirrors FAM actor 'supervisor': handlers incl. the restart limiter."""

    WINDOW_S = 60.0
    MAX_RESTARTS = 5

    def __init__(self, escalate):
        self.restarts = []
        self.escalate = escalate

    def on_worker_crashed(self, worker):
        import time
        now = time.monotonic()
        self.restarts = [t for t in self.restarts if now - t < self.WINDOW_S]
        if len(self.restarts) >= self.MAX_RESTARTS:
            self.escalate("restart cap exceeded: 5 in 60s")
            return
        self.restarts.append(now)
        worker.__init__(worker.db, worker.gateway)

    def on_shutdown(self, workers):
        # FAM: stop_all — halt every supervised worker.
        for w in workers:
            if getattr(w, "state", None) != "stopped":
                w.on_shutdown(None)

    def on_report(self, report):
        # FAM: log_report — record a periodic worker report.
        self._reports = getattr(self, "_reports", []) + [report]


class PaymentGatewayAdapter:
    """Mirrors FAM actor 'payment_gateway': handler on_charge.
    Wraps an injected gateway client whose documented contract enforces
    idempotency keys (the ChargePayment mechanism). Durable, gateway-side."""

    def __init__(self, client):
        self.client = client

    def on_charge(self, amount, idempotency_key):
        return self.client.charge(amount=amount, idempotency_key=idempotency_key)
