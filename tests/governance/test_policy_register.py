from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from export_portfolio.governance.decision_ledger import Repository
from export_portfolio.intake.initiative import ContractError, DomainRecord


class PolicyRegisterTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.database = Path(temporary.name) / "policies.sqlite3"
        self.repository = Repository(self.database)
        for project_id in ("market-a", "market-b", "unrelated"):
            self.repository.save_record(DomainRecord(project_id, {"target_country": project_id}))
        self.repository.register_policy("common", "regional", "tariff update", {"source": "local bulletin"})
        self.repository.register_policy("other", "local", "other event", {"source": "local filing"})
        self.repository.link_policy_project("market-a", "common", .5)
        self.repository.link_policy_project("market-b", "common", .3)
        self.repository.link_policy_project("unrelated", "other", .1)

    def test_shared_event_revision_targets_related_pending_review_only(self):
        first = self.repository.open_policy_review("review-a", "market-a", "common")
        self.assertEqual(first["policy_revision"], 1)
        self.repository.register_policy("common", "regional", "tariff revised", {"source": "corrected bulletin"})
        impact = Repository(self.database).policy_impact("common")
        self.assertEqual([row["project_id"] for row in impact["projects"]], ["market-a", "market-b"])
        self.assertEqual(impact["reviews"][0]["policy_revision"], 1)
        self.assertEqual(self.repository.policy_impact("other")["revision"], 1)
        with self.assertRaisesRegex(ContractError, "changed before resolution"):
            self.repository.resolve_policy_review("review-a")
        with self.assertRaisesRegex(ContractError, "cannot be overwritten"):
            self.repository.open_policy_review("review-a", "market-a", "common")
        second = self.repository.open_policy_review("review-b", "market-b", "common")
        self.assertEqual(self.repository.resolve_policy_review("review-b")["status"], "resolved")
        self.assertEqual(second["policy_revision"], 2)

    def test_unknown_event_cannot_be_linked(self):
        with self.assertRaisesRegex(ContractError, "unknown policy event"):
            self.repository.link_policy_project("market-a", "unknown", .5)
