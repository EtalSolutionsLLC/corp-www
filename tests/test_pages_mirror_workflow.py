from pathlib import Path
import unittest

WORKFLOW = Path(".github/workflows/publish-pages-mirror.yml")


class PagesMirrorWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_is_manual_only(self):
        self.assertIn("workflow_dispatch:", self.text)
        self.assertNotIn("\n  push:", self.text)

    def test_publication_requires_dedicated_secret(self):
        self.assertIn("secrets.PAGES_MIRROR_TOKEN", self.text)

    def test_mirror_is_replaced_not_layered(self):
        self.assertIn("rsync -a --delete", self.text)

    def test_cname_is_environment_specific(self):
        self.assertIn("rm -f mirror/CNAME", self.text)
        self.assertIn("CUSTOM_DOMAIN", self.text)

    def test_source_checkout_does_not_persist_credentials(self):
        self.assertIn("persist-credentials: false", self.text)

    def test_static_artifact_is_sanitized(self):
        for marker in (".env", "*.pem", "*.key", "symbolic links"):
            self.assertIn(marker, self.text)


if __name__ == "__main__":
    unittest.main()
