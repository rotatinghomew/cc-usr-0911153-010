from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from export_portfolio.intake.initiative import ContractError, DomainRecord
from export_portfolio.governance.decision_ledger import Repository
from export_portfolio.governance.risk_attribution import (
    ATTRIBUTION_BUCKETS,
    project_stress_loss,
)
from export_portfolio.optimization.constrained_selection import shock


def make_project(project_id: str, *, state: str = "screening", country: str = "th", revenue: float = 100.0) -> DomainRecord:
    return DomainRecord(
        project_id,
        {
            "product_family": "robot",
            "target_country": country,
            "scenario_proof": 0.8,
            "standard_gap": 0.2,
            "partner_strength": 0.8,
            "localization_effort": 10,
            "delivery_capacity": 4,
            "expected_revenue": revenue,
            "currency_risk": 0.2,
            "policy_risk": 0.2,
            "support_cost": 5,
            "dependency_count": 2,
        },
        state,
    )


class AttributionFixture:
    """四个项目覆盖四类归因桶：
    p-decided : scaling（已决），observed 共同事件 + 已决评审 -> shared_observed
    p-bounded : diligence（待决），bounded 联系只有上下界 -> shared_bounded
    p-unknown : screening，unidentified 联系，缺共同观测 -> unidentified
    p-alone   : screening，无任何共同事件 -> project_specific
    """

    def __init__(self, repository: Repository):
        self.repo = repository
        self.records = {
            "p-decided": make_project("p-decided", state="scaling", country="th"),
            "p-bounded": make_project("p-bounded", state="diligence", country="vn"),
            "p-unknown": make_project("p-unknown", state="screening", country="id"),
            "p-alone": make_project("p-alone", state="screening", country="my"),
        }
        for record in self.records.values():
            repository.save_record(record)
        # 共同政策事件（单一事件身份），各自一份冲击证据。
        repository.register_policy("evt-tariff", "regional", "asean tariff revision", {"source": "bulletin"})
        repository.register_policy("evt-license", "local", "local licensing note", {"source": "filing"})
        repository.register_policy_shock("evt-tariff", "observed", policy_delta=0.3, currency_delta=0.3)
        repository.register_policy_shock("evt-license", "bounded", policy_delta=0.15, currency_delta=0.1)

    def wire(self) -> None:
        repo = self.repo
        # 已决项目：固定敞口 + link + 走完评审并决议。
        repo.link_policy_project("p-decided", "evt-tariff", 0.6)
        repo.register_association_judgment(
            "p-decided", "evt-tariff", "observed", exposure=0.6,
            lower_bound=0.6, upper_bound=0.6, evidence_ref="bulletin#42",
            rationale="resolved shared tariff exposure",
        )
        repo.open_policy_review("rev-decided", "p-decided", "evt-tariff")
        repo.resolve_policy_review("rev-decided")

        # 待决项目：只有上下界的联系，没有评审决议。
        repo.register_association_judgment(
            "p-bounded", "evt-tariff", "bounded", lower_bound=0.2, upper_bound=0.5,
            rationale="shared tariff channel suspected, exposure range only",
        )

        # 无法辨识：登记联系但缺少可归因的共同观测（evt-license 无冲击强度落到该项目的确认）。
        repo.register_association_judgment(
            "p-unknown", "evt-license", "unidentified",
            rationale="no common observation available to confirm linkage",
        )
        # p-alone 不登记任何共同事件。


class RiskAttributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "attribution.sqlite3"
        self.repo = Repository(self.database)
        self.fixture = AttributionFixture(self.repo)
        self.fixture.wire()

    def test_four_buckets_are_exhaustive_and_disjoint(self):
        self.assertEqual(
            set(ATTRIBUTION_BUCKETS),
            {"project_specific", "shared_observed", "shared_bounded", "unidentified"},
        )
        report = self.repo.risk_attribution()
        details = {row["record_id"]: row for row in report["project_details"]}
        self.assertEqual(set(details), set(self.fixture.records))
        # 每个项目的桶集合互斥：有金额的桶不重叠，unidentified 只承载不确定性。
        for row in details.values():
            names = list(row["buckets"])
            self.assertEqual(len(names), len(set(names)))

    def test_decided_project_attributes_observed_common_shock(self):
        report = self.repo.risk_attribution()
        row = next(item for item in report["project_details"] if item["record_id"] == "p-decided")
        observed = row["buckets"]["shared_observed"]
        self.assertGreater(observed["stress_loss"], 0.0)
        self.assertEqual(observed["events"][0]["event_id"], "evt-tariff")
        self.assertEqual(observed["events"][0]["policy_revision"], 1)
        # 已决项目标记为冻结口径。
        self.assertEqual(row["decision_status"], "decided")

    def test_pending_project_keeps_bounded_range_not_point_estimate(self):
        report = self.repo.risk_attribution()
        row = next(item for item in report["project_details"] if item["record_id"] == "p-bounded")
        bounded = row["buckets"]["shared_bounded"]
        self.assertGreater(bounded["stress_loss_low"], 0.0)
        self.assertGreaterEqual(bounded["stress_loss_high"], bounded["stress_loss_low"])
        self.assertEqual(bounded["events"][0]["grade"], "bounded")
        self.assertTrue(row["buckets"]["unidentified"]["uncertainty_retained"])
        # 待决项目不应被提前计入已观测共同冲击。
        self.assertEqual(row["buckets"]["shared_observed"]["stress_loss"], 0.0)
        self.assertEqual(row["decision_status"], "open")

    def test_unidentifiable_link_retains_uncertainty_without_invented_loss(self):
        report = self.repo.risk_attribution()
        row = next(item for item in report["project_details"] if item["record_id"] == "p-unknown")
        unidentified = row["buckets"]["unidentified"]
        self.assertEqual(unidentified["stress_loss"], 0.0)
        self.assertTrue(unidentified["uncertainty_retained"])
        self.assertEqual(unidentified["events"][0]["grade"], "unidentified")
        self.assertEqual(row["buckets"]["shared_observed"]["stress_loss"], 0.0)
        self.assertEqual(row["buckets"]["shared_bounded"]["stress_loss_high"], 0.0)

    def test_project_without_shared_evidence_is_project_specific(self):
        report = self.repo.risk_attribution()
        row = next(item for item in report["project_details"] if item["record_id"] == "p-alone")
        # 无共同事件：共同冲击总损失为零，不臆造共同暴露，也不产生无法辨识金额。
        self.assertEqual(row["total_stress_loss"], 0.0)
        self.assertEqual(row["buckets"]["shared_observed"]["stress_loss"], 0.0)
        self.assertEqual(row["buckets"]["unidentified"]["events"], [])

    def test_bucket_split_reconciles_to_project_total(self):
        report = self.repo.risk_attribution()
        for row in report["project_details"]:
            buckets = row["buckets"]
            recomposed = (
                buckets["project_specific"]["stress_loss"]
                + buckets["shared_observed"]["stress_loss"]
                + buckets["shared_bounded"]["stress_loss"]
            )
            self.assertTrue(row["reconciles"])
            self.assertAlmostEqual(recomposed, row["total_stress_loss"], places=9)

    def test_portfolio_contributions_sum_to_total_and_share_to_one(self):
        report = self.repo.risk_attribution()
        total = report["portfolio_stress_loss"]["total"]
        summed = sum(item["total_stress_loss"] for item in report["project_contributions"])
        self.assertAlmostEqual(summed, total, places=9)
        share = sum(item["contribution_share"] for item in report["project_contributions"])
        if total > 0:
            self.assertAlmostEqual(share, 1.0, places=9)

    def test_common_shock_is_counted_once_per_event_at_portfolio_level(self):
        report = self.repo.risk_attribution()
        tariff_events = [item for item in report["shared_events"] if item["event_id"] == "evt-tariff"]
        self.assertEqual(len(tariff_events), 1)
        # 同一事件下挂多个受影响项目，但事件身份只有一个，不重复计为独立证据。
        impacted = {entry["record_id"] for entry in tariff_events[0]["projects"]}
        self.assertEqual(impacted, {"p-decided", "p-bounded"})
        # 同一事件对已决/待决项目分别落 observed 与 bounded 金额。
        self.assertGreater(tariff_events[0]["observed_stress_loss"], 0.0)
        self.assertGreater(tariff_events[0]["bounded_stress_loss_high"], 0.0)

    def test_stress_loss_uses_exposure_scaling(self):
        record = self.fixture.records["p-decided"]
        full = shock(record, 0.3, 0.3)
        decline = full["base_value"] - full["shocked_value"]
        self.assertAlmostEqual(
            project_stress_loss(record, 0.3, 0.3, 0.6), decline * 0.6, places=9
        )
        self.assertEqual(project_stress_loss(record, 0.3, 0.3, 0.0), 0.0)

    def test_applicability_scope_separates_open_and_frozen_projects(self):
        report = self.repo.risk_attribution()
        applicability = report["applicability"]
        self.assertIn("p-bounded", applicability["open_projects"])
        self.assertIn("p-unknown", applicability["open_projects"])
        self.assertIn("p-alone", applicability["open_projects"])
        self.assertEqual(applicability["decided_projects_frozen"], ["p-decided"])
        self.assertIn("does not reopen", applicability["scope"])

    # ---- 合约校验 -------------------------------------------------

    def test_observed_association_requires_fixed_exposure_within_bounds(self):
        with self.assertRaisesRegex(ContractError, "fixed exposure"):
            self.repo.register_association_judgment(
                "p-alone", "evt-tariff", "observed", rationale="missing exposure"
            )
        with self.assertRaisesRegex(ContractError, "within its bounds"):
            self.repo.register_association_judgment(
                "p-alone", "evt-tariff", "observed", exposure=0.9,
                lower_bound=0.1, upper_bound=0.5, rationale="out of bounds",
            )

    def test_bounded_association_cannot_claim_fixed_exposure(self):
        with self.assertRaisesRegex(ContractError, "cannot claim a fixed exposure"):
            self.repo.register_association_judgment(
                "p-alone", "evt-tariff", "bounded", exposure=0.4,
                lower_bound=0.2, upper_bound=0.6, rationale="no point estimate",
            )

    def test_bounds_must_be_ordered(self):
        with self.assertRaisesRegex(ContractError, "lower bound cannot exceed"):
            self.repo.register_association_judgment(
                "p-alone", "evt-tariff", "bounded",
                lower_bound=0.8, upper_bound=0.2, rationale="bad range",
            )

    def test_unidentified_association_carries_no_exposure(self):
        with self.assertRaisesRegex(ContractError, "carries no exposure"):
            self.repo.register_association_judgment(
                "p-alone", "evt-license", "unidentified", exposure=0.3,
                rationale="must stay unknown",
            )

    def test_shock_requires_known_event_and_unit_interval(self):
        with self.assertRaisesRegex(ContractError, "unknown policy event"):
            self.repo.register_policy_shock("nope", "observed", 0.1, 0.1)
        with self.assertRaisesRegex(ContractError, "observed or bounded"):
            self.repo.register_policy_shock("evt-tariff", "guess", 0.1, 0.1)
        with self.assertRaisesRegex(ContractError, "between zero and one"):
            self.repo.register_policy_shock("evt-tariff", "observed", 1.5, 0.1)

    def test_unknown_project_or_event_rejected(self):
        with self.assertRaisesRegex(ContractError, "unknown project"):
            self.repo.register_association_judgment(
                "ghost", "evt-tariff", "unidentified", rationale="no project"
            )
        with self.assertRaisesRegex(ContractError, "unknown policy event"):
            self.repo.register_association_judgment(
                "p-alone", "ghost", "unidentified", rationale="no event"
            )

    def test_rationale_is_required(self):
        with self.assertRaisesRegex(ContractError, "rationale is required"):
            self.repo.register_association_judgment(
                "p-alone", "evt-tariff", "unidentified", rationale="   "
            )


class EvidenceCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "correction.sqlite3"
        self.repo = Repository(self.database)
        self.fixture = AttributionFixture(self.repo)
        self.fixture.wire()

    def test_correction_flags_pending_reviews_and_projects_but_freezes_decided(self):
        # 待决项目再开一个未决议评审。
        self.repo.link_policy_project("p-bounded", "evt-tariff", 0.4)
        self.repo.open_policy_review("rev-bounded", "p-bounded", "evt-tariff")
        impact = self.repo.evidence_correction_impact("evt-tariff")

        pending_ids = {item["project_id"] for item in impact["affected_open_reviews_and_projects"]}
        self.assertIn("p-bounded", pending_ids)
        frozen = {item["project_id"] for item in impact["frozen_decided_reviews"]}
        self.assertEqual(frozen, {"p-decided"})
        self.assertTrue(impact["single_evidence_identity"])
        # 已决评审固定在修订 1，即便事件随后修订也不改写。
        frozen_item = next(item for item in impact["frozen_decided_reviews"] if item["project_id"] == "p-decided")
        self.assertEqual(frozen_item["fixed_policy_revision"], 1)

    def test_revised_event_blocks_pending_review_but_keeps_resolved_review(self):
        self.repo.link_policy_project("p-bounded", "evt-tariff", 0.4)
        review = self.repo.open_policy_review("rev-bounded", "p-bounded", "evt-tariff")
        self.assertEqual(review["policy_revision"], 1)
        # 补报/纠正证据 -> 事件修订号前进。
        new_revision = self.repo.register_policy(
            "evt-tariff", "regional", "asean tariff corrected", {"source": "bulletin-v2"}
        )
        self.assertEqual(new_revision, 2)
        with self.assertRaisesRegex(ContractError, "changed before resolution"):
            self.repo.resolve_policy_review("rev-bounded")
        # 历史已决评审仍可解析为已决状态，不被重算推翻。
        decided = self.repo.resolve_policy_review("rev-decided")
        self.assertEqual(decided["status"], "resolved")

    def test_correction_impact_lists_project_without_review(self):
        # p-unknown 对 evt-license 有联系判断但没有评审。
        impact = self.repo.evidence_correction_impact("evt-license")
        no_review = [item for item in impact["affected_open_reviews_and_projects"] if item["review_id"] is None]
        self.assertTrue(any(item["project_id"] == "p-unknown" for item in no_review))

    def test_unknown_event_correction_rejected(self):
        with self.assertRaisesRegex(ContractError, "unknown policy event"):
            self.repo.evidence_correction_impact("missing-event")

    def test_recomputation_does_not_change_project_stage(self):
        before = {name: record.state for name, record in self.fixture.records.items()}
        self.repo.register_policy(
            "evt-tariff", "regional", "asean tariff corrected again", {"source": "bulletin-v3"}
        )
        self.repo.risk_attribution()
        after = {name: self.repo.get_record(name).state for name in before}
        self.assertEqual(before, after)


class BoardIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / "board.sqlite3"
        self.output = self.root / "book"

    def test_attribution_is_written_into_board_bundle(self):
        from export_portfolio.portfolio_office import Application
        from export_portfolio.board.portfolio_book import verify_bundle

        app = Application(self.database)
        fixture = AttributionFixture(app.repository)
        fixture.wire()
        report = app.risk_attribution()

        # 用最小 fixture 触发一次 bundle 导出，携带归因材料。
        records = list(fixture.records.values())
        decisions = {}
        for record in records:
            _, decision = app.process(record)
            decisions[record.record_id] = decision
        snapshot = app.repository.snapshot()
        from export_portfolio.board.portfolio_book import export_bundle
        manifest = export_bundle(
            self.output, app.repository.list_records(), decisions, snapshot,
            app.repository.event_rows(), report,
        )
        self.assertIn("risk-attribution.json", manifest["files"])
        on_disk = json.loads((self.output / "risk-attribution.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk["attribution_hash"], report["attribution_hash"])
        self.assertEqual(verify_bundle(self.output), [])

    def test_application_exposes_attribution_and_correction(self):
        from export_portfolio.portfolio_office import Application

        app = Application(self.database)
        fixture = AttributionFixture(app.repository)
        fixture.wire()
        self.assertIn("portfolio_stress_loss", app.risk_attribution())
        impact = app.evidence_correction_impact("evt-tariff")
        self.assertEqual(impact["event_id"], "evt-tariff")


if __name__ == "__main__":
    unittest.main()
