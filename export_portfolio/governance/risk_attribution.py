from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from export_portfolio.intake.initiative import (
    ContractError,
    DomainRecord,
    canonical_json,
    stable_hash,
    utc_now,
)
from export_portfolio.optimization.constrained_selection import shock

# 关联风险归因的四类桶：穷尽且互斥。
# project_specific  单项目自身波动，没有任何关联证据
# shared_observed   有共同政策事件证据、且已通过尽调评审固定的共同冲击
# shared_bounded    共同事件存在但联系只有上下界（待决/未评审），只能给区间
# unidentified      缺少共同观测，关联完全无法辨识，显式保留不确定性
ATTRIBUTION_BUCKETS = (
    "project_specific",
    "shared_observed",
    "shared_bounded",
    "unidentified",
)

# 项目尽调阶段：尚未作出最终结论的阶段，新风险证据必须进入这些项目的判断。
OPEN_STATES = ("screening", "diligence", "sandbox", "launching")
# 已经作出阶段性决策的阶段：历史决策保持当时依据，不因重算改变阶段。
DECIDED_STATES = ("scaling", "holding")


@dataclass(frozen=True)
class AssociationJudgment:
    project_id: str
    event_id: str
    grade: str
    exposure: float
    lower_bound: float
    upper_bound: float
    evidence_ref: str
    rationale: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "event_id": self.event_id,
            "grade": self.grade,
            "exposure": self.exposure,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "evidence_ref": self.evidence_ref,
            "rationale": self.rationale,
        }


def prepare_attribution(connection) -> None:
    """关联归因所需的表结构。复用 policy_events/project_policy_links/diligence_reviews，
    不复制政策证据本身，避免同一次市场冲击被登记成多份独立证据。"""
    from export_portfolio.governance.policy_register import prepare_policies

    prepare_policies(connection)
    # 同一事件的冲击强度只有一份；grade 记录证据支持程度。
    connection.execute(
        """CREATE TABLE IF NOT EXISTS policy_event_shocks(
            event_id TEXT PRIMARY KEY,
            grade TEXT NOT NULL CHECK(grade IN ('observed','bounded')),
            policy_delta REAL NOT NULL,
            currency_delta REAL NOT NULL,
            shock_json TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(event_id) REFERENCES policy_events(event_id)
        )"""
    )
    # 项目-事件联系：observed 为固定敞口；bounded 只有上下界，敞口在评审前可在界内修订。
    connection.execute(
        """CREATE TABLE IF NOT EXISTS project_association_judgments(
            project_id TEXT NOT NULL,
            event_id TEXT NOT NULL,
            grade TEXT NOT NULL CHECK(grade IN ('observed','bounded','unidentified')),
            exposure REAL,
            lower_bound REAL NOT NULL,
            upper_bound REAL NOT NULL,
            evidence_ref TEXT NOT NULL,
            rationale TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            PRIMARY KEY(project_id, event_id),
            FOREIGN KEY(event_id) REFERENCES policy_events(event_id),
            FOREIGN KEY(project_id) REFERENCES records(record_id)
        )"""
    )


def _unit_interval(value: Any, name: str) -> float:
    if type(value) not in (float, int) or isinstance(value, bool):
        raise ContractError(f"{name} must be a finite number between zero and one")
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ContractError(f"{name} must be between zero and one")
    return number


def register_event_shock(
    connection,
    event_id: str,
    grade: str,
    policy_delta: float,
    currency_delta: float,
) -> None:
    """把一次市场冲击固定在单一事件身份上。observed/bounded 是证据支持程度，
    不允许把同一冲击拆成多个事件重复登记。"""
    prepare_attribution(connection)
    if grade not in ("observed", "bounded"):
        raise ContractError("event shock grade must be observed or bounded")
    policy_delta = _unit_interval(policy_delta, "policy_delta")
    currency_delta = _unit_interval(currency_delta, "currency_delta")
    if not connection.execute(
        "SELECT 1 FROM policy_events WHERE event_id=?", (event_id,)
    ).fetchone():
        raise ContractError("unknown policy event")
    body = canonical_json(
        {
            "grade": grade,
            "policy_delta": policy_delta,
            "currency_delta": currency_delta,
        }
    )
    connection.execute(
        """INSERT INTO policy_event_shocks VALUES(?,?,?,?,?,?)
        ON CONFLICT(event_id) DO UPDATE SET grade=excluded.grade,
            policy_delta=excluded.policy_delta, currency_delta=excluded.currency_delta,
            shock_json=excluded.shock_json, updated_at=excluded.updated_at""",
        (
            event_id,
            grade,
            policy_delta,
            currency_delta,
            body,
            utc_now(),
        ),
    )


def register_association(
    connection,
    project_id: str,
    event_id: str,
    grade: str,
    *,
    exposure: float | None = None,
    lower_bound: float | None = None,
    upper_bound: float | None = None,
    evidence_ref: str = "",
    rationale: str = "",
) -> AssociationJudgment:
    """登记项目与共同事件的联系判断。

    observed：必须给出固定 exposure，且落在界内；用于已有共同观测、证据可复核的联系。
    bounded：只给 [lower_bound, upper_bound]，exposure 留空，反映只有上下界的联系。
    unidentified：显式登记无法辨识的关联，界为 [0,0]，保留不确定性而不是假设独立。
    """
    prepare_attribution(connection)
    if grade not in ("observed", "bounded", "unidentified"):
        raise ContractError("association grade must be observed, bounded or unidentified")
    if not connection.execute(
        "SELECT 1 FROM records WHERE record_id=?", (project_id,)
    ).fetchone():
        raise ContractError("unknown project")
    if not connection.execute(
        "SELECT 1 FROM policy_events WHERE event_id=?", (event_id,)
    ).fetchone():
        raise ContractError("unknown policy event")
    if not rationale.strip():
        raise ContractError("association rationale is required")
    reference = evidence_ref.strip() or event_id

    if grade == "observed":
        if exposure is None:
            raise ContractError("observed association requires a fixed exposure")
        exposure_value = _unit_interval(exposure, "exposure")
        low = _unit_interval(lower_bound if lower_bound is not None else exposure_value, "lower_bound")
        high = _unit_interval(upper_bound if upper_bound is not None else exposure_value, "upper_bound")
        if not low <= exposure_value <= high:
            raise ContractError("observed exposure must sit within its bounds")
    elif grade == "bounded":
        if exposure is not None:
            raise ContractError("bounded association cannot claim a fixed exposure")
        low = _unit_interval(lower_bound if lower_bound is not None else 0.0, "lower_bound")
        high = _unit_interval(upper_bound if upper_bound is not None else 1.0, "upper_bound")
        if low > high:
            raise ContractError("lower bound cannot exceed upper bound")
        exposure_value = None
    else:  # unidentified：缺少共同观测，不给敞口也不给界
        if exposure is not None or lower_bound is not None or upper_bound is not None:
            raise ContractError("unidentified association carries no exposure or bounds")
        low = high = 0.0
        exposure_value = None

    connection.execute(
        """INSERT INTO project_association_judgments VALUES(?,?,?,?,?,?,?,?,?)
        ON CONFLICT(project_id, event_id) DO UPDATE SET grade=excluded.grade,
            exposure=excluded.exposure, lower_bound=excluded.lower_bound,
            upper_bound=excluded.upper_bound, evidence_ref=excluded.evidence_ref,
            rationale=excluded.rationale, recorded_at=excluded.recorded_at""",
        (
            project_id,
            event_id,
            grade,
            exposure_value,
            low,
            high,
            reference,
            " ".join(rationale.split()),
            utc_now(),
        ),
    )
    return AssociationJudgment(
        project_id, event_id, grade, exposure_value if exposure_value is not None else 0.0,
        low, high, reference, " ".join(rationale.split()),
    )


def _load_records(connection) -> dict[str, DomainRecord]:
    import json

    rows = connection.execute("SELECT * FROM records").fetchall()
    return {
        row["record_id"]: DomainRecord(
            record_id=row["record_id"],
            payload=json.loads(row["payload_json"]),
            state=row["state"],
            version=row["version"],
            occurred_at=row["occurred_at"],
            source=row["source"],
        )
        for row in rows
    }


def _resolved_event_revisions(connection) -> dict[tuple[str, str], int]:
    """每个项目-事件对，已决尽调评审所固定的政策修订号。历史决策口径以此为准。"""
    rows = connection.execute(
        "SELECT project_id, policy_event_id, policy_revision FROM diligence_reviews WHERE status='resolved'"
    ).fetchall()
    return {(row["project_id"], row["policy_event_id"]): row["policy_revision"] for row in rows}


def _project_event_links(connection) -> dict[tuple[str, str], float]:
    rows = connection.execute("SELECT project_id, event_id, exposure FROM project_policy_links").fetchall()
    return {(row["project_id"], row["event_id"]): float(row["exposure"]) for row in rows}


def project_stress_loss(record: DomainRecord, policy_delta: float, currency_delta: float, exposure: float) -> float:
    """项目在一次冲击下的压力损失（价值下降量，非负）。

    复用 constrained_selection.shock 的口径，再按项目对该事件的敞口折算，
    保证同一事件在组合层只按各项目敞口计一次，不把冲击重复计为多份独立证据。"""
    full = shock(record, currency_delta, policy_delta)
    decline = max(0.0, full["base_value"] - full["shocked_value"])
    return decline * _unit_interval(exposure, "exposure")


def _bucket_for(
    project_id: str,
    event_id: str,
    grade: str,
    resolved: Mapping[tuple[str, str], int],
) -> str:
    if grade == "unidentified":
        return "unidentified"
    if (project_id, event_id) in resolved:
        # 已决评审固定了证据版本，共同冲击可被证据支持。
        return "shared_observed"
    if grade == "observed":
        # 有固定敞口与共同观测，但尽调尚未决议：只能作为有界联系提示，不能提前当成已证实共同冲击。
        return "shared_bounded"
    return "shared_bounded"


def attribute_project(
    connection,
    record: DomainRecord,
    shocks: Mapping[str, dict[str, Any]],
    judgments: Mapping[str, list[AssociationJudgment]],
    resolved: Mapping[tuple[str, str], int],
    links: Mapping[tuple[str, str], float],
) -> dict[str, Any]:
    """单项目归因：把总压力损失拆到四个桶，四桶之和与总损失精确对账。"""
    project_events = {item.event_id: item for item in judgments.get(record.record_id, ())}

    observed_loss = 0.0
    bounded_loss_low = 0.0
    bounded_loss_high = 0.0
    observed_events: list[dict[str, Any]] = []
    bounded_events: list[dict[str, Any]] = []
    unidentified_events: list[dict[str, Any]] = []

    for event_id, judgment in project_events.items():
        shock_spec = shocks.get(event_id)
        if shock_spec is None:
            # 登记了联系但缺少冲击观测：归入无法辨识，保留不确定性。
            unidentified_events.append(
                judgment.as_dict() | {"reason": "no shared shock observation registered"}
            )
            continue
        policy_delta = float(shock_spec["policy_delta"])
        currency_delta = float(shock_spec["currency_delta"])
        bucket = _bucket_for(record.record_id, event_id, judgment.grade, resolved)

        if bucket == "shared_observed":
            exposure = links.get((record.record_id, event_id), judgment.exposure)
            loss = project_stress_loss(record, policy_delta, currency_delta, exposure)
            observed_loss += loss
            observed_events.append(
                judgment.as_dict()
                | {
                    "bucket": bucket,
                    "exposure": exposure,
                    "stress_loss": loss,
                    "policy_revision": resolved[(record.record_id, event_id)],
                }
            )
        elif bucket == "shared_bounded":
            low_loss = project_stress_loss(record, policy_delta, currency_delta, judgment.lower_bound)
            high_loss = project_stress_loss(record, policy_delta, currency_delta, judgment.upper_bound)
            bounded_loss_low += low_loss
            bounded_loss_high += high_loss
            bounded_events.append(
                judgment.as_dict()
                | {
                    "bucket": bucket,
                    "stress_loss_low": low_loss,
                    "stress_loss_high": high_loss,
                }
            )
        else:
            unidentified_events.append(
                judgment.as_dict() | {"reason": "shared observation missing or unidentifiable"}
            )

    # 总压力损失 = 项目所关联的每个独立事件在满敞口下损失之和。
    # 每个事件身份只计一次（不把同一次冲击拆成多份独立证据）；与四桶拆分共用同一 shock 口径，
    # 因此四桶之和与总损失精确对账。没有任何关联证据的项目，其共同冲击总损失为零，
    # 波动只可能是单项目自身波动，无法辨识的关联保留为不确定性而不臆造金额。
    covered_event_ids = {
        event_id
        for event_id, judgment in project_events.items()
        if event_id in shocks and judgment.grade != "unidentified"
    }
    total_loss = 0.0
    for event_id in covered_event_ids:
        spec = shocks[event_id]
        total_loss += project_stress_loss(
            record, float(spec["policy_delta"]), float(spec["currency_delta"]), 1.0
        )

    # 有界部分给区间（点估计取上下界中值）；项目特有部分是总损失扣除可归属共同冲击后的残差，
    # 残差非负：observed 用固定敞口、bounded 用上界折算，均不超过满敞口总损失。
    bounded_mid = (bounded_loss_low + bounded_loss_high) / 2.0
    attributed_known = observed_loss + bounded_mid
    project_specific_loss = max(0.0, total_loss - attributed_known)
    unidentified_note = bool(unidentified_events)

    return {
        "record_id": record.record_id,
        "state": record.state,
        "decision_status": "decided" if record.state in DECIDED_STATES else "open",
        "total_stress_loss": total_loss,
        "buckets": {
            "project_specific": {
                "stress_loss": project_specific_loss,
                "evidence": "residual movement not attributable to any registered shared event",
            },
            "shared_observed": {
                "stress_loss": observed_loss,
                "events": observed_events,
            },
            "shared_bounded": {
                "stress_loss_low": bounded_loss_low,
                "stress_loss_high": bounded_loss_high,
                "stress_loss": bounded_mid,
                "events": bounded_events,
            },
            "unidentified": {
                "stress_loss": 0.0,
                "events": unidentified_events,
                "uncertainty_retained": unidentified_note or bool(bounded_events),
            },
        },
        "reconciles": _close(
            total_loss,
            project_specific_loss + observed_loss + bounded_mid,
        ),
    }


def _close(left: float, right: float, tolerance: float = 1e-9) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def load_attribution_inputs(connection) -> tuple[
    dict[str, DomainRecord],
    dict[str, dict[str, Any]],
    dict[str, list[AssociationJudgment]],
    dict[tuple[str, str], int],
    dict[tuple[str, str], float],
]:
    prepare_attribution(connection)
    records = _load_records(connection)

    shock_rows = connection.execute("SELECT * FROM policy_event_shocks").fetchall()
    shocks = {
        row["event_id"]: {
            "event_id": row["event_id"],
            "grade": row["grade"],
            "policy_delta": row["policy_delta"],
            "currency_delta": row["currency_delta"],
        }
        for row in shock_rows
    }

    judgment_rows = connection.execute(
        "SELECT * FROM project_association_judgments ORDER BY project_id, event_id"
    ).fetchall()
    judgments: dict[str, list[AssociationJudgment]] = {}
    for row in judgment_rows:
        judgment = AssociationJudgment(
            project_id=row["project_id"],
            event_id=row["event_id"],
            grade=row["grade"],
            exposure=float(row["exposure"]) if row["exposure"] is not None else 0.0,
            lower_bound=float(row["lower_bound"]),
            upper_bound=float(row["upper_bound"]),
            evidence_ref=row["evidence_ref"],
            rationale=row["rationale"],
        )
        judgments.setdefault(row["project_id"], []).append(judgment)

    resolved = _resolved_event_revisions(connection)
    links = _project_event_links(connection)
    return records, shocks, judgments, resolved, links


def attribute_portfolio(connection) -> dict[str, Any]:
    """组合层关联风险归因。只解释和复核现有暴露，不挑选项目、不改预算。"""
    records, shocks, judgments, resolved, links = load_attribution_inputs(connection)
    if not records:
        raise ContractError("no projects available for attribution")

    project_rows = [
        attribute_project(connection, record, shocks, judgments, resolved, links)
        for record in sorted(records.values(), key=lambda item: item.record_id)
    ]

    def sum_bucket(name: str, key: str = "stress_loss") -> float:
        return sum(row["buckets"][name][key] for row in project_rows)

    portfolio_total = sum(row["total_stress_loss"] for row in project_rows)
    observed_total = sum_bucket("shared_observed")
    bounded_mid_total = sum_bucket("shared_bounded")
    bounded_low_total = sum_bucket("shared_bounded", "stress_loss_low")
    bounded_high_total = sum_bucket("shared_bounded", "stress_loss_high")
    specific_total = sum_bucket("project_specific")

    # 共同冲击在组合层按事件去重归集：同一 event_id 只出现一次，列出受影响项目及其桶级判断。
    # 同一事件对已决项目可能是 observed、对待决项目可能是 bounded，因此事件条目同时承载两类金额。
    shared_event_view: dict[str, dict[str, Any]] = {}
    for row in project_rows:
        for event in row["buckets"]["shared_observed"]["events"]:
            entry = shared_event_view.setdefault(
                event["event_id"],
                {
                    "event_id": event["event_id"],
                    "projects": [],
                    "observed_stress_loss": 0.0,
                    "bounded_stress_loss_low": 0.0,
                    "bounded_stress_loss_high": 0.0,
                },
            )
            entry["projects"].append({"record_id": row["record_id"], "bucket": "shared_observed"})
            entry["observed_stress_loss"] += event["stress_loss"]
        for event in row["buckets"]["shared_bounded"]["events"]:
            entry = shared_event_view.setdefault(
                event["event_id"],
                {
                    "event_id": event["event_id"],
                    "projects": [],
                    "observed_stress_loss": 0.0,
                    "bounded_stress_loss_low": 0.0,
                    "bounded_stress_loss_high": 0.0,
                },
            )
            entry["projects"].append({"record_id": row["record_id"], "bucket": "shared_bounded"})
            entry["bounded_stress_loss_low"] += event["stress_loss_low"]
            entry["bounded_stress_loss_high"] += event["stress_loss_high"]

    contributions = [
        {
            "record_id": row["record_id"],
            "state": row["state"],
            "decision_status": row["decision_status"],
            "total_stress_loss": row["total_stress_loss"],
            "contribution_share": (row["total_stress_loss"] / portfolio_total) if portfolio_total > 0 else 0.0,
            "project_specific_loss": row["buckets"]["project_specific"]["stress_loss"],
            "shared_observed_loss": row["buckets"]["shared_observed"]["stress_loss"],
            "shared_bounded_loss": row["buckets"]["shared_bounded"]["stress_loss"],
            "shared_bounded_loss_low": row["buckets"]["shared_bounded"]["stress_loss_low"],
            "shared_bounded_loss_high": row["buckets"]["shared_bounded"]["stress_loss_high"],
            "uncertainty_retained": row["buckets"]["unidentified"]["uncertainty_retained"],
        }
        for row in project_rows
    ]

    open_projects = [row["record_id"] for row in project_rows if row["decision_status"] == "open"]
    decided_projects = [row["record_id"] for row in project_rows if row["decision_status"] == "decided"]

    return {
        "generated_for": "related-risk attribution of existing portfolio exposure",
        "bucket_definitions": {
            "project_specific": "single-project movement with no registered shared evidence",
            "shared_observed": "common shock supported by shared policy evidence fixed in a resolved review",
            "shared_bounded": "common-event link known only through lower/upper bounds, review not resolved",
            "unidentified": "no common observation; association cannot be identified, uncertainty retained",
        },
        "portfolio_stress_loss": {
            "total": portfolio_total,
            "project_specific": specific_total,
            "shared_observed": observed_total,
            "shared_bounded_mid": bounded_mid_total,
            "shared_bounded_low": bounded_low_total,
            "shared_bounded_high": bounded_high_total,
            "unidentified": 0.0,
        },
        "shared_events": sorted(shared_event_view.values(), key=lambda item: item["event_id"]),
        "project_contributions": sorted(
            contributions, key=lambda item: (-item["total_stress_loss"], item["record_id"])
        ),
        "project_details": project_rows,
        "applicability": {
            "open_projects": open_projects,
            "decided_projects_frozen": decided_projects,
            "scope": (
                "Attribution feeds pending diligence and board materials. Decided projects keep the basis "
                "and stage recorded at decision time; recomputation does not reopen or re-stage them. "
                "No portfolio re-selection or budget reallocation is performed."
            ),
            "bounded_interpretation": (
                "shared_bounded and unidentified amounts are ranges or retained uncertainty, not point estimates; "
                "do not net them against observed losses as if independent."
            ),
        },
        "attribution_hash": stable_hash(
            {"projects": project_rows, "shocks": shocks, "resolved": sorted(resolved.items())}
        ),
    }


def evidence_correction_impact(connection, event_id: str) -> dict[str, Any]:
    """补报/纠正某个市场的证据时，指出受影响的关联判断与待审项目。

    同一次市场冲击只有一个 event_id：这里只沿该事件追溯，不会把它重复计成多份证据。
    已决（resolved）评审与已决项目保持当时依据，不列入受影响待办，只作冻结提示。"""
    prepare_attribution(connection)
    event = connection.execute(
        "SELECT event_id, scope, revision FROM policy_events WHERE event_id=?", (event_id,)
    ).fetchone()
    if event is None:
        raise ContractError("unknown policy event")

    review_rows = connection.execute(
        "SELECT * FROM diligence_reviews WHERE policy_event_id=? ORDER BY review_id", (event_id,)
    ).fetchall()
    judgment_rows = connection.execute(
        "SELECT * FROM project_association_judgments WHERE event_id=? ORDER BY project_id", (event_id,)
    ).fetchall()

    affected_open: list[dict[str, Any]] = []
    frozen_decided: list[dict[str, Any]] = []
    for review in review_rows:
        record = connection.execute(
            "SELECT state FROM records WHERE record_id=?", (review["project_id"],)
        ).fetchone()
        item = {
            "review_id": review["review_id"],
            "project_id": review["project_id"],
            "status": review["status"],
            "fixed_policy_revision": review["policy_revision"],
            "current_event_revision": event["revision"],
            "project_state": record["state"] if record else None,
        }
        if review["status"] == "resolved":
            frozen_decided.append(item)
        else:
            affected_open.append(item)

    # 登记了联系但还没有评审的项目：证据变化直接影响其待审判断。
    reviewed_projects = {row["project_id"] for row in review_rows}
    for row in judgment_rows:
        if row["project_id"] not in reviewed_projects:
            record = connection.execute(
                "SELECT state FROM records WHERE record_id=?", (row["project_id"],)
            ).fetchone()
            affected_open.append(
                {
                    "review_id": None,
                    "project_id": row["project_id"],
                    "status": "no-review",
                    "fixed_policy_revision": None,
                    "current_event_revision": event["revision"],
                    "project_state": record["state"] if record else None,
                    "association_grade": row["grade"],
                }
            )

    return {
        "event_id": event_id,
        "scope": event["scope"],
        "current_revision": event["revision"],
        "single_evidence_identity": True,
        "affected_open_reviews_and_projects": affected_open,
        "frozen_decided_reviews": frozen_decided,
        "duplicate_count_guard": (
            "One event_id carries one shock record and one evidence chain; linked projects share it, "
            "so the shock is counted once rather than as independent evidence per project."
        ),
    }
