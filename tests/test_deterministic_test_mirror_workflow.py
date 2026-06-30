from pathlib import Path
import unittest

WORKFLOW = Path(".github/workflows/publish-test-pages.yml")


class DeterministicTestMirrorWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_has_no_runtime_inputs(self):
        self.assertIn("workflow_dispatch:", self.text)
        self.assertNotIn("inputs:", self.text)

    def test_test_target_is_fixed(self):
        self.assertIn(
            "TARGET_REPOSITORY: EtalSolutionsLLC/corp-www-test-pages",
            self.text,
        )

    def test_dev_artifact_is_fixed(self):
        self.assertIn("SOURCE_PATH: deploy/dev/www", self.text)

    def test_test_publish_never_writes_cname(self):
        self.assertIn("rm -f mirror/CNAME", self.text)
        self.assertNotIn("custom_domain", self.text)

    def test_publication_requires_dedicated_secret(self):
        self.assertIn("secrets.PAGES_MIRROR_TOKEN", self.text)

    def test_mirror_is_replaced_not_layered(self):
        self.assertIn("rsync -a --delete", self.text)


if __name__ == "__main__":
    unittest.main()
