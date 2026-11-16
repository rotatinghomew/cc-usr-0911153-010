from __future__ import annotations

import json
import sqlite3
from typing import Any

from export_portfolio.intake.initiative import ContractError, canonical_json, stable_hash, utc_now


def prepare_policies(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE IF NOT EXISTS policy_events(
        event_id TEXT PRIMARY KEY, scope TEXT NOT NULL, revision INTEGER NOT NULL,
        description TEXT NOT NULL, evidence_json TEXT NOT NULL, updated_at TEXT NOT NULL
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS project_policy_links(
        project_id TEXT NOT NULL, event_id TEXT NOT NULL, exposure REAL NOT NULL,
        PRIMARY KEY(project_id,event_id), FOREIGN KEY(event_id) REFERENCES policy_events(event_id)
    )""")
    connection.execute("""CREATE TABLE IF NOT EXISTS diligence_reviews(
        review_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, project_version INTEGER NOT NULL,
        policy_event_id TEXT NOT NULL, policy_revision INTEGER NOT NULL,
        evidence_hash TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','resolved')),
        opened_at TEXT NOT NULL, resolved_at TEXT,
        FOREIGN KEY(policy_event_id) REFERENCES policy_events(event_id)
    )""")


def register_event(connection: sqlite3.Connection, event_id: str, scope: str,
                   description: str, evidence: dict[str, Any]) -> int:
    prepare_policies(connection)
    if not all(isinstance(value, str) and value.strip() for value in (event_id, scope, description)):
        raise ContractError("policy evidence needs an event identity and scope")
    if not isinstance(evidence, dict):
        raise ContractError("policy evidence must be an object")
    body = canonical_json(evidence)
    previous = connection.execute("SELECT * FROM policy_events WHERE event_id=?", (event_id,)).fetchone()
    if previous:
        if previous["scope"] != scope:
            raise ContractError("policy event scope cannot be reassigned")
        if previous["description"] == description and previous["evidence_json"] == body:
            return previous["revision"]
        revision = previous["revision"] + 1
        connection.execute("UPDATE policy_events SET revision=?,description=?,evidence_json=?,updated_at=? WHERE event_id=?",
                           (revision, description, body, utc_now(), event_id))
        return revision
    connection.execute("INSERT INTO policy_events VALUES(?,?,?,?,?,?)",
                       (event_id, scope, 1, description, body, utc_now()))
    return 1


def link_project(connection: sqlite3.Connection, project_id: str, event_id: str, exposure: float) -> None:
    prepare_policies(connection)
    if type(exposure) not in (float, int) or not 0 <= exposure <= 1:
        raise ContractError("policy exposure must be between zero and one")
    if not connection.execute("SELECT 1 FROM records WHERE record_id=?", (project_id,)).fetchone():
        raise ContractError("unknown project")
    if not connection.execute("SELECT 1 FROM policy_events WHERE event_id=?", (event_id,)).fetchone():
        raise ContractError("unknown policy event")
    row = connection.execute("SELECT exposure FROM project_policy_links WHERE project_id=? AND event_id=?",
                             (project_id, event_id)).fetchone()
    if row:
        if row[0] != exposure:
            raise ContractError("changing project exposure requires a new review")
        return
    connection.execute("INSERT INTO project_policy_links VALUES(?,?,?)", (project_id, event_id, exposure))


def open_review(connection: sqlite3.Connection, review_id: str, project_id: str, event_id: str) -> dict[str, Any]:
    prepare_policies(connection)
    link = connection.execute("SELECT exposure FROM project_policy_links WHERE project_id=? AND event_id=?",
                              (project_id, event_id)).fetchone()
    project = connection.execute("SELECT version,fingerprint FROM records WHERE record_id=?", (project_id,)).fetchone()
    event = connection.execute("SELECT revision,evidence_json FROM policy_events WHERE event_id=?", (event_id,)).fetchone()
    if link is None or project is None or event is None:
        raise ContractError("review requires project and shared policy evidence")
    evidence_hash = stable_hash({"project": project[1], "event": event_id,
                                 "revision": event[0], "scope_evidence": json.loads(event[1]),
                                 "exposure": link[0]})
    previous = connection.execute("SELECT * FROM diligence_reviews WHERE review_id=?", (review_id,)).fetchone()
    if previous:
        if (previous["project_id"], previous["policy_event_id"], previous["evidence_hash"]) != (
                project_id, event_id, evidence_hash):
            raise ContractError("existing diligence review cannot be overwritten")
        return dict(previous)
    connection.execute("INSERT INTO diligence_reviews VALUES(?,?,?,?,?,?,'pending',?,NULL)",
                       (review_id, project_id, project[0], event_id, event[0], evidence_hash, utc_now()))
    return dict(connection.execute("SELECT * FROM diligence_reviews WHERE review_id=?", (review_id,)).fetchone())


def resolve_review(connection: sqlite3.Connection, review_id: str) -> dict[str, Any]:
    prepare_policies(connection)
    review = connection.execute("SELECT * FROM diligence_reviews WHERE review_id=?", (review_id,)).fetchone()
    if review is None:
        raise ContractError("unknown diligence review")
    if review["status"] == "resolved":
        return dict(review)
    project = connection.execute("SELECT version FROM records WHERE record_id=?", (review["project_id"],)).fetchone()
    event = connection.execute("SELECT revision FROM policy_events WHERE event_id=?", (review["policy_event_id"],)).fetchone()
    if (project[0], event[0]) != (review["project_version"], review["policy_revision"]):
        raise ContractError("diligence evidence changed before resolution")
    connection.execute("UPDATE diligence_reviews SET status='resolved',resolved_at=? WHERE review_id=?",
                       (utc_now(), review_id))
    return dict(connection.execute("SELECT * FROM diligence_reviews WHERE review_id=?", (review_id,)).fetchone())


def policy_impact(connection: sqlite3.Connection, event_id: str) -> dict[str, Any]:
    prepare_policies(connection)
    event = connection.execute("SELECT * FROM policy_events WHERE event_id=?", (event_id,)).fetchone()
    if event is None:
        raise ContractError("unknown policy event")
    links = [dict(row) for row in connection.execute(
        "SELECT * FROM project_policy_links WHERE event_id=? ORDER BY project_id", (event_id,))]
    reviews = [dict(row) for row in connection.execute(
        "SELECT * FROM diligence_reviews WHERE policy_event_id=? ORDER BY opened_at,review_id", (event_id,))]
    return {"event_id": event_id, "scope": event["scope"], "revision": event["revision"],
            "projects": links, "reviews": reviews}
