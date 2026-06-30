from pathlib import Path
import unittest

WORKFLOW = Path(".github/workflows/publish-test-pages.yml")


class EmptyMirrorBootstrapWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_does_not_checkout_empty_mirror_with_actions_checkout(self):
        self.assertNotIn("Check out public test mirror", self.text)

    def test_initializes_git_repository(self):
        self.assertIn("git init", self.text)

    def test_detects_existing_main_branch(self):
        self.assertIn("git ls-remote --exit-code --heads origin main", self.text)

    def test_creates_orphan_main_for_empty_repo(self):
        self.assertIn("git checkout --orphan main", self.text)

    def test_pushes_main_on_first_publish(self):
        self.assertIn("git push --set-upstream origin main", self.text)

    def test_excludes_env_from_public_mirror(self):
        self.assertIn("--exclude='.env'", self.text)
        self.assertIn("--exclude='**/.env'", self.text)


if __name__ == "__main__":
    unittest.main()
