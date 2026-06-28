#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_HOOK = ROOT / "www/partials/hooks/site-build-meta"
FINALIZE_HOOK = ROOT / "www/partials/hooks/zz-site-build-finalize"


def shared_portmason() -> Path:
    configured = os.environ.get("PORTMASON_SHARE", "").strip()
    if configured:
        return Path(configured).resolve()

    pm_version = shutil.which("pm-version")
    if pm_version:
        return Path(pm_version).resolve().parent

    raise RuntimeError("PORTMASON_SHARE is not set and pm-version is not on PATH")


class SharedSiteBuildToolingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.portmason = shared_portmason()
        cls.pm_version = cls.portmason / "pm-version"
        cls.processor = cls.portmason / "pm-process-site-partials"

        for path in [cls.pm_version, cls.processor, cls.portmason / "pm-helpers"]:
            if not path.exists():
                raise RuntimeError(f"Required shared Portmason file is missing: {path}")

    @staticmethod
    def create_version_root(root: Path) -> None:
        for name, value in [
            ("RELEASE_VERSION", "1.0.0\n"),
            ("BUILD_NUMBER", "034\n"),
            ("VERSION", "034\n"),
        ]:
            (root / name).write_text(value, encoding="utf-8")

    def test_meta_hook_resolves_shared_pm_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_version_root(root)

            site = root / "www"
            hooks = site / "partials/hooks"
            hooks.mkdir(parents=True)
            shutil.copy2(META_HOOK, hooks / "site-build-meta")
            os.chmod(hooks / "site-build-meta", 0o755)

            (site / "index.html").write_text(
                "<!doctype html>\n"
                "<html><head>\n"
                "<!-- PM:SITE-BUILD-META -->\n"
                "<!-- /PM:SITE-BUILD-META -->\n"
                "</head><body></body></html>\n",
                encoding="utf-8",
            )

            environment = os.environ.copy()
            environment.update(
                {
                    "SITE_DIR": str(site),
                    "REPO_ROOT": str(root),
                    "PM_VERSION_ROOT": str(root),
                    "PORTMASON_SHARE": str(self.portmason),
                    "PM_DEFER_SITE_BUILD_FINALIZE": "true",
                }
            )

            result = subprocess.run(
                ["python3", str(self.processor)],
                cwd=site,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            rendered = (site / "index.html").read_text(encoding="utf-8")
            self.assertIn('ETAL_SITE_RELEASE version="1.0.0" build="034"', rendered)
            self.assertIn('meta name="etal-site-build" content="034"', rendered)
            self.assertNotIn("Required version file is missing", rendered)
            self.assertNotIn("[INFO]", rendered)

    def test_finalize_hook_resolves_shared_pm_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.create_version_root(root)

            site = root / "www"
            hooks = site / "partials/hooks"
            hooks.mkdir(parents=True)
            shutil.copy2(FINALIZE_HOOK, hooks / "zz-site-build-finalize")
            os.chmod(hooks / "zz-site-build-finalize", 0o755)
            (site / "index.html").write_text("<!doctype html><title>test</title>\n", encoding="utf-8")

            environment = os.environ.copy()
            environment.update(
                {
                    "SITE_DIR": str(site),
                    "REPO_ROOT": str(root),
                    "PM_VERSION_ROOT": str(root),
                    "PORTMASON_SHARE": str(self.portmason),
                    "PM_SOURCE_COMMIT": "0123456789abcdef0123456789abcdef01234567",
                    "PM_SOURCE_DIRTY": "false",
                    "PM_OFFICIAL_BUILD": "true",
                    "PM_DEPLOY_ENV": "github-pages",
                    "PM_DEPLOYMENT_ID": "github-pages-unit-test",
                    "PM_BUILT_AT": "2026-06-28T01:00:00Z",
                    "PM_DEPLOYED_AT": "2026-06-28T01:01:00Z",
                }
            )

            result = subprocess.run(
                [str(hooks / "zz-site-build-finalize")],
                cwd=site,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            build = json.loads((site / "build-info.json").read_text(encoding="utf-8"))
            deployment = json.loads((site / "deploy-info.json").read_text(encoding="utf-8"))
            manifest = json.loads((site / "artifact-manifest.json").read_text(encoding="utf-8"))

            self.assertEqual("034", build["buildNumber"])
            self.assertEqual("github-pages", deployment["environment"])
            self.assertEqual("github-pages-unit-test", deployment["deploymentId"])
            self.assertEqual(build["artifactSha256"], deployment["artifactSha256"])
            self.assertEqual(build["artifactSha256"], manifest["artifactSha256"])


if __name__ == "__main__":
    unittest.main()
