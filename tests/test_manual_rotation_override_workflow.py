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

    def test_rotation_uses_collection_manifest(self):
        self.assertIn(
            "--collection www/collections/transformation-thread/collection.json",
            self.workflow,
        )
        self.assertNotIn("www/content/transformation-thread", self.workflow)
        self.assertNotIn("www/partials/transformation-thread.html", self.workflow)

    def test_rotation_precedes_generation_and_reporting(self):
        rotate = self.workflow.index("- name: Rotate Transformation Thread selection")
        generate = self.workflow.index("- name: Generate production site HTML")
        report = self.workflow.index("- name: Report blog entry rotation")
        self.assertLess(rotate, generate)
        self.assertLess(generate, report)

    def test_documentation_explains_manual_override(self):
        self.assertIn("Actions → Generate site HTML → Run workflow", self.readme)
        self.assertIn("Scheduled runs retain the local-midnight guard", self.readme)
        self.assertIn("bin/rotate-transformation-thread", self.readme)
        self.assertIn(
            "--collection www/collections/transformation-thread/collection.json",
            self.readme,
        )


if __name__ == "__main__":
    unittest.main()
