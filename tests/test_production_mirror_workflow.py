from pathlib import Path
import unittest

WORKFLOW = Path(".github/workflows/publish-production-pages.yml")


class ProductionMirrorWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_is_manual_only(self):
        self.assertIn("workflow_dispatch:", self.text)
        self.assertNotIn("\n  push:", self.text)
        self.assertNotIn("\n  schedule:", self.text)

    def test_targets_etal_production_repository(self):
        self.assertIn(
            "TARGET_REPOSITORY: EtalSolutionsLLC/www.etal.solutions",
            self.text,
        )
        self.assertNotIn("www.simplifai.team", self.text)

    def test_uses_production_domain(self):
        self.assertIn("PRODUCTION_DOMAIN: www.etal.solutions", self.text)
        self.assertIn('> mirror/CNAME', self.text)

    def test_uses_prd_artifact(self):
        self.assertIn("SOURCE_PATH: deploy/prd/www", self.text)
        self.assertIn("PM_DEPLOY_ENV: prd", self.text)
        self.assertIn("--environment prd", self.text)

    def test_requires_dedicated_production_token(self):
        self.assertIn("PRODUCTION_PAGES_MIRROR_TOKEN", self.text)

    def test_finalizes_and_verifies_before_push(self):
        finalize = self.text.index("pm-version build finalize")
        verify = self.text.index("pm-version deployment verify")
        push = self.text.index("git push --set-upstream origin main")
        self.assertLess(finalize, verify)
        self.assertLess(verify, push)

    def test_rejects_stale_portmason_bootstrap(self):
        self.assertIn(
            '. "${PORTMASON_SHARE}/pm-helpers" --minimal >&2',
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
