#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"


class SiteBuildInfoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (SITE / "index.html").read_text(encoding="utf-8")
        cls.footer = (SITE / "partials/footer.html").read_text(encoding="utf-8")
        cls.script = (SITE / "assets/js/site-build-info.js").read_text(encoding="utf-8")
        cls.styles = (SITE / "assets/css/site-build-info.css").read_text(encoding="utf-8")
        cls.hook_path = SITE / "partials/hooks/site-build-meta"
        cls.hook = cls.hook_path.read_text(encoding="utf-8")
        cls.gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        cls.workflow = (ROOT / ".github/workflows/gen-site-html.yml").read_text(encoding="utf-8")

    def test_version_file_declares_current_build(self):
        self.assertEqual("026", (ROOT / "VERSION").read_text(encoding="utf-8").strip())

    def test_html_contains_portmason_build_meta_region(self):
        self.assertIn("<!-- PM:SITE-BUILD-META -->", self.index)
        self.assertIn("<!-- /PM:SITE-BUILD-META -->", self.index)
        self.assertIn('meta name="etal-site-build" content="026"', self.index)
        self.assertIn('ETAL_SITE_BUILD version="026"', self.index)

    def test_footer_copyright_opens_accessible_build_dialog(self):
        for token in [
            "data-site-build-open",
            'aria-controls="site-build-modal"',
            'id="site-build-modal"',
            "data-site-build-modal",
            "data-site-build-close",
            "data-site-build-version",
            "data-site-build-commit",
            "data-site-build-time",
            "data-site-build-target",
        ]:
            self.assertIn(token, self.footer)
        self.assertIn('/assets/css/site-build-info.css', self.footer)
        self.assertIn('/assets/js/site-build-info.js', self.footer)

    def test_browser_controller_fetches_uncached_build_metadata(self):
        self.assertIn('fetch(endpoint, { cache: "no-store" })', self.script)
        self.assertIn('meta[name="etal-site-build"]', self.script)
        self.assertIn("modal.showModal()", self.script)
        self.assertIn("modal.close()", self.script)

    def test_build_metadata_is_artifact_only(self):
        self.assertIn("/www/build-info.json", self.gitignore)
        self.assertIn("/deploy/*/www/build-info.json", self.gitignore)
        self.assertIn('-e GITHUB_ACTIONS=true', self.workflow)
        self.assertIn('-e GITHUB_SHA="${GITHUB_SHA}"', self.workflow)
        self.assertNotIn('git add -f deploy/prd/www', self.workflow)
        self.assertIn('deploy/prd/www/index.html', self.workflow)
        self.assertIn('deploy/prd/www/collections/transformation-thread/generated/selection.json', self.workflow)

    def test_hook_is_executable_and_valid_bash(self):
        self.assertTrue(os.access(self.hook_path, os.X_OK))
        subprocess.run(["bash", "-n", str(self.hook_path)], check=True)

    def test_hook_writes_json_and_deterministic_html(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            site = root / "www"
            site.mkdir()
            (root / "VERSION").write_text("026\n", encoding="utf-8")
            (root / ".env.generated").write_text("DEPLOY_ENV=prd\n", encoding="utf-8")

            environment = os.environ.copy()
            environment["SITE_DIR"] = str(site)
            environment["GITHUB_ACTIONS"] = "true"
            result = subprocess.run(
                [str(self.hook_path)],
                cwd=site,
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertIn('ETAL_SITE_BUILD version="026"', result.stdout)
            self.assertIn('meta name="etal-site-build" content="026"', result.stdout)
            payload = json.loads((site / "build-info.json").read_text(encoding="utf-8"))
            self.assertEqual("026", payload["version"])
            self.assertEqual("github-pages", payload["target"])
            self.assertEqual("Et al Solutions LLC", payload["builder"])
            self.assertTrue(payload["built_at"].endswith("Z"))

    def test_build_modal_uses_site_visual_system(self):
        self.assertIn(".footer-build-trigger", self.styles)
        self.assertIn(".site-build-modal", self.styles)
        self.assertIn(".site-build-modal::backdrop", self.styles)


if __name__ == "__main__":
    unittest.main()
