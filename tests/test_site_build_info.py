#!/usr/bin/env python3
from __future__ import annotations

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
        cls.gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        cls.workflow = (ROOT / ".github/workflows/portmason-setup-and-deploy.yml").read_text(encoding="utf-8")
        cls.release = (ROOT / "RELEASE_VERSION").read_text(encoding="utf-8").strip()
        cls.build = (ROOT / "BUILD_NUMBER").read_text(encoding="utf-8").strip()

    def test_authoritative_version_files_are_valid(self):
        self.assertRegex(self.release, r"^\d+\.\d+\.\d+$")
        self.assertRegex(self.build, r"^\d{3,}$")

    def test_versioning_has_no_site_specific_customization(self):
        custom_paths = [
            ROOT / "bin/pm-version",
            SITE / "partials/hooks/site-build-meta",
            SITE / "partials/hooks/zz-site-build-finalize",
        ]
        for path in custom_paths:
            self.assertFalse(path.exists(), path)

        for page in SITE.rglob("*.html"):
            html = page.read_text(encoding="utf-8")
            self.assertNotIn("PM:SITE-BUILD-META", html, page)
            self.assertNotIn("PM:ZZ-SITE-BUILD-FINALIZE", html, page)
            self.assertNotIn("ETAL_SITE_RELEASE", html, page)

    def test_footer_copyright_opens_accessible_identity_dialog(self):
        for token in [
            "data-site-build-open",
            'aria-controls="site-build-modal"',
            'id="site-build-modal"',
            "data-site-build-modal",
            "data-site-build-close",
            "data-site-release-version",
            "data-site-build-version",
            "data-site-build-commit",
            "data-site-build-time",
            "data-site-artifact-sha",
            "data-site-deploy-environment",
            "data-site-deployment-id",
            "data-site-deployed-time",
            "data-site-deployment-verification",
            "data-site-build-warning",
        ]:
            self.assertIn(token, self.footer)
        self.assertIn("Build identity", self.footer)
        self.assertIn("Deployment", self.footer)
        self.assertIn('/assets/css/site-build-info.css', self.footer)
        self.assertIn('/assets/js/site-build-info.js', self.footer)

    def test_build_dialog_identifies_registered_and_claimed_marks(self):
        self.assertIn("A.I. Fusion℠ and SIMPLIFAI℠", self.footer)
        self.assertIn("registered with the California Secretary of State", self.footer)
        for mark in [
            "Portmason Platform™",
            "Portmason Operations™",
            "Portmason Foundations™",
            "Portmason Collections™",
            "Portmason Tooling™",
        ]:
            self.assertIn(mark, self.footer)
        self.assertNotIn("®", self.footer)
        self.assertNotIn("Patent Pending", self.footer)

    def test_browser_controller_fetches_and_verifies_both_records(self):
        self.assertIn('fetch(url, { cache: "no-store" })', self.script)
        self.assertIn('etal-site-build-info', self.script)
        self.assertIn('etal-site-deploy-info', self.script)
        self.assertIn("Promise.allSettled", self.script)
        self.assertIn('"artifactSha256"', self.script)
        self.assertIn("Build and deployment metadata disagree", self.script)
        self.assertIn("modal.showModal()", self.script)
        self.assertIn("modal.close()", self.script)

    def test_generated_identity_records_are_artifact_only(self):
        for path in [
            "/www/build-info.json",
            "/www/deploy-info.json",
            "/www/artifact-manifest.json",
            "/deploy/*/www/build-info.json",
            "/deploy/*/www/deploy-info.json",
            "/deploy/*/www/artifact-manifest.json",
        ]:
            self.assertIn(path, self.gitignore)

    def test_pages_workflow_delegates_build_lifecycle_to_pm_setup(self):
        checkout = self.workflow.index("- name: Check out project")
        install = self.workflow.index("- name: Install Portmason tooling")
        setup = self.workflow.index("- name: Run Portmason setup")
        upload = self.workflow.index("- name: Upload GitHub Pages artifact")
        deploy = self.workflow.index("- name: Deploy GitHub Pages")
        self.assertLess(checkout, install)
        self.assertLess(install, setup)
        self.assertLess(setup, upload)
        self.assertLess(upload, deploy)
        self.assertIn("DEPLOY_DIR: site/deploy/prd", self.workflow)
        self.assertIn("PAGES_SITE_DIR: site/deploy/prd/www", self.workflow)
        self.assertIn('working-directory: ${{ env.DEPLOY_DIR }}', self.workflow)
        self.assertIn("\n          pm-setup\n", self.workflow)
        self.assertIn("PM_OFFICIAL_BUILD: \"true\"", self.workflow)
        self.assertIn("PM_SOURCE_COMMIT: ${{ github.sha }}", self.workflow)
        self.assertIn("PM_SOURCE_DIRTY: \"false\"", self.workflow)
        self.assertIn("uses: actions/upload-pages-artifact@v3", self.workflow)
        self.assertIn("path: ${{ env.PAGES_SITE_DIR }}", self.workflow)
        self.assertIn("uses: actions/deploy-pages@v4", self.workflow)
        self.assertNotIn("- name: Resolve runtime outputs", self.workflow)
        self.assertNotIn("- name: Persist static-site container image", self.workflow)
        self.assertNotIn("uses: actions/upload-artifact@v4", self.workflow)
        self.assertNotIn("Rotate Transformation Thread selection", self.workflow)
        self.assertNotIn("pm-version build allocate", self.workflow)
        self.assertNotIn("pm-version build finalize", self.workflow)

    def test_build_modal_uses_site_visual_system(self):
        self.assertIn(".footer-build-trigger", self.styles)
        self.assertIn(".site-build-modal", self.styles)
        self.assertIn(".site-build-modal::backdrop", self.styles)
        self.assertIn(".site-build-section", self.styles)
        self.assertIn(".site-build-warning", self.styles)

    def test_build_modal_has_exactly_one_scroll_owner(self):
        modal_block = self.styles.split(".site-build-modal {", 1)[1].split("}", 1)[0]
        shell_block = self.styles.split(".site-build-modal-shell {", 1)[1].split("}", 1)[0]
        self.assertIn("overflow: hidden;", modal_block)
        self.assertNotIn("overflow-y: auto;", modal_block)
        self.assertIn("overflow-y: auto;", shell_block)
        self.assertIn("overscroll-behavior: contain;", shell_block)
        self.assertIn("scrollbar-gutter: stable;", shell_block)


if __name__ == "__main__":
    unittest.main()
