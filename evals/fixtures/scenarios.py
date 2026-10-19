"""Deterministic synthetic models. Uses in-memory SQLite; no live services."""

import hashlib
import json
import sqlite3


def lease(guarded):
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE job(id INTEGER PRIMARY KEY, owner TEXT, generation INTEGER, status TEXT, result TEXT)")
    db.execute("INSERT INTO job VALUES(1, 'A', 1, 'PROCESSING', NULL)")
    steps = [{"action": "A_claim", "row": dict(db.execute("SELECT * FROM job").fetchone())}]
    db.execute("UPDATE job SET owner='B', generation=2 WHERE id=1")
    db.execute("UPDATE job SET status='COMPLETED', result='B-result' WHERE id=1 AND owner='B' AND generation=2")
    steps.append({"action": "B_takeover_and_complete", "row": dict(db.execute("SELECT * FROM job").fetchone())})
    sql = "UPDATE job SET status='COMPLETED', result=? WHERE id=?"
    params = ["A-result", 1]
    if guarded:
        sql += " AND owner=? AND generation=? AND status='PROCESSING'"
        params += ["A", 1]
    affected = db.execute(sql, params).rowcount
    steps.append({"action": "A_resume_complete", "affected": affected, "row": dict(db.execute("SELECT * FROM job").fetchone())})
    db.close()
    return {"guarded": guarded, "steps": steps}


def delivery():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE receipt(receiver INTEGER PRIMARY KEY, status TEXT)")
    db.executemany("INSERT INTO receipt VALUES(?, 'PENDING')", [(i,) for i in range(100)])
    for receiver in range(100):
        try:
            if receiver == 99:
                raise ConnectionError("synthetic downstream failure")
            db.execute("UPDATE receipt SET status='SENT' WHERE receiver=?", (receiver,))
        except ConnectionError:
            continue
    parent_status = "DONE"
    retry_tasks = []
    counts = dict(db.execute("SELECT status, COUNT(*) FROM receipt GROUP BY status").fetchall())
    db.close()
    return {"parent_status": parent_status, "receipt_counts": counts, "retry_tasks": retry_tasks}


def read_health():
    original = b'{"id":"obj-1","value":"original"}'
    stored = {"payload": '{"id":"obj-1","value":"changed"}', "checksum": hashlib.sha256(original).hexdigest()}
    reader_valid = hashlib.sha256(stored["payload"].encode()).hexdigest() == stored["checksum"]
    reconcile_healthy = bool(stored)
    return {"stored": stored, "reader_valid": reader_valid, "reconcile_healthy": reconcile_healthy}


def outbox():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE fact(id INTEGER PRIMARY KEY, kind TEXT)")
    db.execute("CREATE TABLE event(fact_id INTEGER PRIMARY KEY, kind TEXT)")

    def save(kind):
        fact_id = db.execute("INSERT INTO fact(kind) VALUES(?)", (kind,)).lastrowid
        db.commit()
        raise ConnectionError(f"synthetic failure before event insert for {fact_id}")
        # Normal next operation: INSERT event(fact_id, kind), followed by commit.

    errors = []
    for kind in ("notification", "projection", "fulfillment"):
        try:
            save(kind)
        except ConnectionError as exc:
            errors.append(str(exc))
    result = {"fact_count": db.execute("SELECT COUNT(*) FROM fact").fetchone()[0],
              "event_count": db.execute("SELECT COUNT(*) FROM event").fetchone()[0], "errors": errors}
    db.close()
    return result


def lease_free():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE job(id INTEGER PRIMARY KEY, status TEXT, lease TEXT)")
    db.execute("CREATE TABLE effect(job_id INTEGER PRIMARY KEY)")
    db.execute("INSERT INTO job VALUES(1, 'PROCESSING', NULL)")
    db.commit()
    updates = []
    for _ in range(2):
        with db:
            affected = db.execute("UPDATE job SET status='COMPLETED' WHERE id=1 AND status='PROCESSING'").rowcount
            if affected:
                db.execute("INSERT INTO effect VALUES(1)")
            updates.append(affected)
    result = {"completion_updates": updates, "effect_count": db.execute("SELECT COUNT(*) FROM effect").fetchone()[0],
              "lease": db.execute("SELECT lease FROM job").fetchone()[0]}
    db.close()
    return result


def observe():
    return {"lease_plain": lease(False), "lease_guarded": lease(True), "delivery": delivery(),
            "read_health": read_health(), "outbox": outbox(), "lease_free": lease_free()}


if __name__ == "__main__":
    print(json.dumps(observe(), ensure_ascii=False, indent=2, sort_keys=True))
