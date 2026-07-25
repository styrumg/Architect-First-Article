"""payment-worker-fixed.py — the corrected implementation of
06-payment-worker.fam.json, after Gate 3's blocking findings were resolved.
Same FAM mirror as the vulnerable version; only code-level quality differs.
"""
import json
import time


class PaymentWorker:
    """Mirrors FAM actor 'worker': states idle/processing/stopped, handlers per message."""

    def __init__(self, db, gateway, audit):
        self.db = db                # durable order store (unique order_id constraint)
        self.gateway = gateway      # PaymentGatewayAdapter (gateway-side idempotency)
        self.audit = audit
        self.state = "idle"
        self.charge = None

    # --- handlers (FAM F6) ---
    def on_submit_order(self, order):
        # SIM: stopped rejects; durable order-ID dedup BEFORE charging.
        if self.state == "stopped":
            return {"status": "rejected", "reason": "worker stopped"}
        if self.db.order_exists(order["id"]):
            return {"status": "duplicate", "order_id": order["id"]}
        self.db.record_order(order["id"])          # unique constraint — concurrent dups can't both pass
        self.audit.log("order_received", order_id=order["id"])
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
        # SIM: monotonic stopped state; repeated shutdown returns the same ack.
        if self.state == "stopped":
            return {"status": "stopped"}
        # drain before stop, with an explicit force-stop policy at the deadline.
        try:
            self._drain()
        except DrainError as exc:
            # declared policy: force-stop after the drain deadline, parking the charge.
            self.audit.log("force_stop_after_drain_timeout", error=str(exc))
            self._park_charge()
        self.state = "stopped"
        return {"status": "stopped"}

    # --- internal ---
    def _begin_charge(self, order):
        payload = json.loads(order["raw"])   # strict JSON, not pickle
        self.gateway.on_charge(payload["amount"], idempotency_key=order["id"])

    def _emit_receipt(self, result):
        self.db.execute("INSERT INTO receipts VALUES (?)", (result["id"],))

    def _drain(self, timeout_s=5.0):
        deadline = time.monotonic() + timeout_s
        while self.charge is not None and time.monotonic() < deadline:
            time.sleep(0.05)
        if self.charge is not None:
            raise DrainError("charge still in flight at drain deadline")

    def _park_charge(self):
        # declared drain-timeout policy: persist the in-flight charge for later reconciliation
        if self.charge is not None:
            self.db.execute("UPDATE orders SET status='parked' WHERE id=?", (self.charge["id"],))
            self.charge = None


class DrainError(Exception):
    pass


class Supervisor:
    """Mirrors FAM actor 'supervisor': handlers incl. the restart limiter."""

    WINDOW_S = 60.0
    MAX_RESTARTS = 5

    def __init__(self, escalate):
        self.restarts = []
        self.escalate = escalate

    def on_worker_crashed(self, worker):
        now = time.monotonic()
        self.restarts = [t for t in self.restarts if now - t < self.WINDOW_S]
        if len(self.restarts) >= self.MAX_RESTARTS:
            self.escalate("restart cap exceeded: 5 in 60s")
            return
        self.restarts.append(now)
        worker.__init__(worker.db, worker.gateway, worker.audit)

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
