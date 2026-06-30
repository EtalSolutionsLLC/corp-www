from pathlib import Path
import unittest

WORKFLOW = Path(".github/workflows/publish-test-pages.yml")


class FinalizedTestArtifactWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_uses_pinned_portmason_tooling(self):
        self.assertIn(".portmason-tooling-ref", self.text)
        self.assertIn("ops-and-sops/ops/portmason", self.text)

    def test_finalizes_staged_artifact(self):
        self.assertIn("pm-version build finalize", self.text)
        self.assertIn('--site-dir "${GITHUB_WORKSPACE}/artifact"', self.text)

    def test_records_source_commit_and_test_deployment(self):
        self.assertIn("PM_SOURCE_COMMIT: ${{ github.sha }}", self.text)
        self.assertIn("PM_DEPLOY_ENV: test", self.text)
        self.assertIn("github-pages-test-${{ github.run_id }}-${{ github.run_attempt }}", self.text)

    def test_verifies_required_metadata(self):
        for filename in (
            "build-info.json",
            "deploy-info.json",
            "artifact-manifest.json",
        ):
            self.assertIn(filename, self.text)
        self.assertIn("pm-version deployment verify", self.text)

    def test_publishes_artifact_not_raw_www(self):
        self.assertIn("artifact/ \\", self.text)
        self.assertNotIn('"source/www/" \\\n            mirror/', self.text)

    def test_test_domain_is_deterministic(self):
        self.assertIn("TEST_DOMAIN: www-test.etal.solutions", self.text)
        self.assertIn('> mirror/CNAME', self.text)


if __name__ == "__main__":
    unittest.main()
