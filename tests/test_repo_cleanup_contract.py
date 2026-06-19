#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "bin/cleanup-root"
README = (ROOT / "README.md").read_text(encoding="utf-8")


class RepoCleanupContractTests(unittest.TestCase):
    def test_cleanup_script_is_valid_bash(self):
        subprocess.run(["bash", "-n", str(SCRIPT)], check=True)

    def test_cleanup_preserves_portmason_contract_and_deploy_snapshots(self):
        script = SCRIPT.read_text(encoding="utf-8")
        for token in [
            '".project_timestamp"', '".env"', '".env.generated"',
            '"config.generated.json"', '"VERSION"', '"deploy"',
            "-path './deploy' -prune", 'deploy|deploy/*',
        ]:
            self.assertIn(token, script)

    def test_cleanup_covers_every_legacy_collection_location(self):
        script = SCRIPT.read_text(encoding="utf-8")
        for path in [
            "www/catalogs",
            "www/content/transformation-thread",
            "www/content/transformation-thread-posts.json",
            "www/content/transformation-thread-selection.json",
            "www/assets/css/carousel.css",
            "www/assets/css/transformation-thread.css",
            "www/assets/js/catalog-carousel.js",
            "www/assets/js/transformation-thread.js",
            "www/partials/catalog-brands-full-list.html",
            "www/partials/catalog-promotions-full-list.html",
            "www/partials/catalog-promotions-hero-teaser.html",
            "www/partials/transformation-thread.html",
            "tests/portmason",
        ]:
            self.assertIn(path, script)

    def test_documentation_declares_root_snapshot_and_collection_boundaries(self):
        self.assertIn("repository root is the authoritative working source", README)
        self.assertIn("preserved snapshot", README)
        self.assertIn("bin/cleanup-root --dry-run", README)
        self.assertIn("Collection data and configuration belong only under `collections/`", README)
        self.assertNotIn("transformation-thread/index.html", README)


if __name__ == "__main__":
    unittest.main()
