from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "gen-site-html.yml"


class ManualRotationOverrideWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.prd_readme = (ROOT / "deploy" / "prd" / "README.md").read_text(encoding="utf-8")

    def test_workflow_dispatch_exposes_optional_rotation_date(self):
        self.assertIn("rotation_date:", self.workflow)
        self.assertIn("required: false", self.workflow)
        self.assertIn("type: string", self.workflow)
        self.assertIn("YYYY-MM-DD", self.workflow)

    def test_manual_dispatch_forces_rotation_and_accepts_date_override(self):
        self.assertIn('WORKFLOW_EVENT: ${{ github.event_name }}', self.workflow)
        self.assertIn("ROTATION_DATE: ${{ github.event.inputs.rotation_date || '' }}", self.workflow)
        self.assertIn('if [[ "$WORKFLOW_EVENT" == "workflow_dispatch" ]]', self.workflow)
        self.assertIn("rotation_args+=(--force)", self.workflow)
        self.assertIn('rotation_args+=(--date "$ROTATION_DATE")', self.workflow)

    def test_scheduled_runs_keep_local_midnight_guard(self):
        self.assertIn("rotation_args+=(--require-local-midnight-window)", self.workflow)
        self.assertIn("Scheduled Transformation Thread rotation with local-midnight guard", self.workflow)

    def test_workflow_uses_tracked_root_rotation_script(self):
        self.assertIn('../../bin/rotate-transformation-thread "${rotation_args[@]}"', self.workflow)

    def test_rotation_uses_explicit_production_paths(self):
        for expected in [
            "--config www/content/transformation-thread-posts.json",
            "--selection www/content/transformation-thread-selection.json",
            "--partial www/partials/transformation-thread.html",
        ]:
            self.assertIn(expected, self.workflow)

    def test_rotation_precedes_generation_and_reporting(self):
        rotate = self.workflow.index("- name: Rotate Transformation Thread selection")
        generate = self.workflow.index("- name: Generate production site HTML")
        report = self.workflow.index("- name: Report blog entry rotation")
        self.assertLess(rotate, generate)
        self.assertLess(generate, report)

    def test_documentation_explains_manual_override(self):
        for readme in [self.readme, self.prd_readme]:
            self.assertIn("Actions → Generate site HTML → Run workflow", readme)
            self.assertIn("Manual runs bypass the local-midnight guard", readme)
            self.assertIn("--config www/content/transformation-thread-posts.json", readme)
        self.assertIn("bin/rotate-transformation-thread", self.readme)
        self.assertIn("../../bin/rotate-transformation-thread", self.prd_readme)


if __name__ == "__main__":
    unittest.main()
