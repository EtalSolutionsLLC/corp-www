from pathlib import Path
import unittest

WORKFLOW = Path(".github/workflows/publish-test-pages.yml")

class DeterministicTestMirrorWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_no_runtime_inputs(self):
        self.assertIn("workflow_dispatch:", self.text)
        self.assertNotIn("inputs:", self.text)

    def test_fixed_target(self):
        self.assertIn("TARGET_REPOSITORY: EtalSolutionsLLC/corp-www-test-pages", self.text)

    def test_fixed_source_is_www(self):
        self.assertIn("SOURCE_PATH: www", self.text)
        self.assertNotIn("SOURCE_PATH: deploy/dev/www", self.text)

    def test_no_cname(self):
        self.assertIn("rm -f mirror/CNAME", self.text)

if __name__ == "__main__":
    unittest.main()
