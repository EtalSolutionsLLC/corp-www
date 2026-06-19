#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"
PRD_WWW = ROOT / "deploy" / "prd" / "www"


class HomeHeroTrustRemovedTests(unittest.TestCase):
    def read(self, root: Path) -> str:
        return (root / "index.html").read_text(encoding="utf-8")

    def assert_home_trust_removed(self, html: str) -> None:
        self.assertNotIn('class="hero-trust"', html)
        self.assertNotIn('<li>Practical A.I.</li>', html)
        self.assertNotIn('<li>Software that fits</li>', html)
        self.assertNotIn('<li>Clear technology judgment</li>', html)
        self.assertIn('class="hero-motion-line"', html)
        self.assertIn('data-home-quick-open', html)

    def test_home_hero_trust_items_are_removed_from_dev_index(self) -> None:
        self.assert_home_trust_removed(self.read(WWW))

    def test_home_hero_trust_items_are_removed_from_prd_index(self) -> None:
        self.assert_home_trust_removed(self.read(PRD_WWW))


if __name__ == "__main__":
    unittest.main()
