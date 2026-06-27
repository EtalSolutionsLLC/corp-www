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
        cls.meta_hook_path = SITE / "partials/hooks/site-build-meta"
        cls.finalize_hook_path = SITE / "partials/hooks/zz-site-build-finalize"
        cls.version_tool = ROOT / "bin/pm-version"
        cls.gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        cls.workflow = (ROOT / ".github/workflows/gen-site-html.yml").read_text(encoding="utf-8")

    def test_authoritative_version_files_are_explicit_and_compatible(self):
        self.assertEqual("1.0.0", (ROOT / "RELEASE_VERSION").read_text(encoding="utf-8").strip())
        build = (ROOT / "BUILD_NUMBER").read_text(encoding="utf-8").strip()
        self.assertEqual("034", build)
        self.assertEqual(build, (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        self.assertEqual(build, (ROOT / "deploy/prd/BUILD_NUMBER").read_text(encoding="utf-8").strip())
        self.assertEqual("1.0.0", (ROOT / "deploy/prd/RELEASE_VERSION").read_text(encoding="utf-8").strip())

    def test_html_contains_release_build_and_finalize_regions(self):
        self.assertIn("<!-- PM:SITE-BUILD-META -->", self.index)
        self.assertIn("<!-- /PM:SITE-BUILD-META -->", self.index)
        self.assertIn("<!-- PM:ZZ-SITE-BUILD-FINALIZE -->", self.index)
        self.assertIn("<!-- /PM:ZZ-SITE-BUILD-FINALIZE -->", self.index)
        self.assertIn('meta name="etal-site-release" content="1.0.0"', self.index)
        self.assertIn('meta name="etal-site-build" content="034"', self.index)
        self.assertIn('meta name="etal-site-deploy-info" content="/deploy-info.json"', self.index)
        self.assertIn('ETAL_SITE_RELEASE version="1.0.0" build="034"', self.index)

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

    def test_version_tool_and_hooks_are_executable_and_valid_bash(self):
        for path in [self.version_tool, self.meta_hook_path, self.finalize_hook_path]:
            self.assertTrue(os.access(path, os.X_OK), path)
            subprocess.run(["bash", "-n", str(path)], check=True)

    def _create_version_root(self, root: Path) -> None:
        (root / "RELEASE_VERSION").write_text("1.0.0\n", encoding="utf-8")
        (root / "BUILD_NUMBER").write_text("034\n", encoding="utf-8")
        (root / "VERSION").write_text("034\n", encoding="utf-8")
        snapshot = root / "deploy/prd"
        snapshot.mkdir(parents=True)
        (snapshot / "RELEASE_VERSION").write_text("1.0.0\n", encoding="utf-8")
        (snapshot / "BUILD_NUMBER").write_text("034\n", encoding="utf-8")
        (snapshot / "VERSION").write_text("034\n", encoding="utf-8")

    def test_pm_version_owns_release_and_build_transitions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._create_version_root(root)
            environment = os.environ.copy()
            environment["PM_VERSION_ROOT"] = str(root)

            result = subprocess.run(
                [str(self.version_tool), "build", "allocate", "--allow-local"],
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual("035", result.stdout.strip())
            for path in [root / "BUILD_NUMBER", root / "VERSION", root / "deploy/prd/BUILD_NUMBER", root / "deploy/prd/VERSION"]:
                self.assertEqual("035", path.read_text(encoding="utf-8").strip())

            result = subprocess.run(
                [str(self.version_tool), "release", "bump", "minor"],
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual("1.1.0", result.stdout.strip())
            self.assertEqual("1.1.0", (root / "RELEASE_VERSION").read_text(encoding="utf-8").strip())
            self.assertEqual("1.1.0", (root / "deploy/prd/RELEASE_VERSION").read_text(encoding="utf-8").strip())

    def test_pm_version_finalizes_and_verifies_exact_artifact_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._create_version_root(root)
            site = root / "www"
            site.mkdir()
            (site / "index.html").write_text("<!doctype html><title>test</title>\n", encoding="utf-8")
            (site / "asset.txt").write_text("exact bytes\n", encoding="utf-8")

            environment = os.environ.copy()
            environment.update(
                {
                    "PM_VERSION_ROOT": str(root),
                    "PM_SOURCE_COMMIT": "0123456789abcdef0123456789abcdef01234567",
                    "PM_OFFICIAL_BUILD": "true",
                    "PM_BUILT_AT": "2026-06-27T20:00:00Z",
                    "PM_DEPLOYED_AT": "2026-06-27T20:05:00Z",
                }
            )
            subprocess.run(
                [
                    str(self.version_tool),
                    "build",
                    "finalize",
                    "--site-dir",
                    str(site),
                    "--environment",
                    "prd",
                    "--deployment-id",
                    "prd-035-test",
                ],
                env=environment,
                check=True,
            )

            build = json.loads((site / "build-info.json").read_text(encoding="utf-8"))
            deployment = json.loads((site / "deploy-info.json").read_text(encoding="utf-8"))
            manifest = json.loads((site / "artifact-manifest.json").read_text(encoding="utf-8"))

            self.assertEqual("1.0.0", build["releaseVersion"])
            self.assertEqual("034", build["buildNumber"])
            self.assertEqual("034", build["buildId"])
            self.assertTrue(build["officialBuild"])
            self.assertEqual(64, len(build["artifactSha256"]))
            self.assertEqual(build["artifactSha256"], deployment["artifactSha256"])
            self.assertEqual(build["artifactSha256"], manifest["artifactSha256"])
            self.assertEqual("prd", deployment["environment"])
            self.assertEqual("verified", deployment["verification"])
            for path in [site / "build-info.json", site / "deploy-info.json", site / "artifact-manifest.json"]:
                self.assertEqual(0o644, path.stat().st_mode & 0o777)

            result = subprocess.run(
                [str(self.version_tool), "deployment", "verify", "--site-dir", str(site)],
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual("verified", result.stdout.strip())

    def test_meta_hook_emits_deterministic_release_and_build_html(self):
        environment = os.environ.copy()
        environment["SITE_DIR"] = str(SITE)
        result = subprocess.run(
            [str(self.meta_hook_path)],
            cwd=SITE,
            env=environment,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn('ETAL_SITE_RELEASE version="1.0.0" build="034"', result.stdout)
        self.assertIn('meta name="etal-site-release" content="1.0.0"', result.stdout)
        self.assertIn('meta name="etal-site-build" content="034"', result.stdout)
        self.assertIn('meta name="etal-site-deploy-info" content="/deploy-info.json"', result.stdout)

    def test_workflow_gates_before_allocation_and_finalizes_before_upload(self):
        rotate = self.workflow.index("- name: Rotate Transformation Thread selection")
        allocate = self.workflow.index("- name: Allocate immutable site build")
        generate = self.workflow.index("- name: Generate production site HTML")
        verify = self.workflow.index("- name: Verify Pages artifact readability")
        upload = self.workflow.index("- name: Upload GitHub Pages artifact")
        self.assertLess(rotate, allocate)
        self.assertLess(allocate, generate)
        self.assertLess(generate, verify)
        self.assertLess(verify, upload)
        self.assertIn("should_build=false", self.workflow)
        self.assertIn("No artifact will be built or deployed for this guard run.", self.workflow)
        self.assertIn("needs.generate.outputs.should_deploy == 'true'", self.workflow)
        self.assertIn("bin/pm-version build allocate --ci", self.workflow)
        self.assertIn("PM_DEFER_SITE_BUILD_FINALIZE=true", self.workflow)
        self.assertIn("../../bin/pm-version build finalize", self.workflow)
        self.assertIn("../../bin/pm-version deployment verify", self.workflow)
        self.assertIn("deploy-info.json", self.workflow)
        self.assertIn("artifact-manifest.json", self.workflow)
        self.assertIn('find "$artifact_root" -type f ! -readable -print', self.workflow)
        self.assertIn('tar -C "$artifact_root" -cf /dev/null .', self.workflow)

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
