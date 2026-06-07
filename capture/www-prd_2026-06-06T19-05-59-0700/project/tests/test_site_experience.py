from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SCRIPT = ROOT / "assets" / "js" / "site-experience.js"
STYLES = ROOT / "assets" / "css" / "styles.css"
PROMOTIONS = ROOT / "catalogs" / "promotions" / "items.json"


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.performance_proofs = 0
        self.reveals = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if "data-performance-proof" in values:
            self.performance_proofs += 1
        if "data-reveal" in values:
            self.reveals += 1


class SiteExperienceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.html = INDEX.read_text(encoding="utf-8")
        self.script = SCRIPT.read_text(encoding="utf-8")
        self.styles = STYLES.read_text(encoding="utf-8")

    def test_primary_spa_sections_remain_available(self) -> None:
        parser = IdCollector()
        parser.feed(self.html)
        self.assertTrue({"home", "about", "services", "promotions", "brands", "contact"}.issubset(parser.ids))

    def test_live_performance_proof_is_wired_once(self) -> None:
        parser = IdCollector()
        parser.feed(self.html)
        self.assertEqual(parser.performance_proofs, 1)
        self.assertIn('data-performance-value="transfer"', self.html)
        self.assertIn('data-performance-value="javascript"', self.html)
        self.assertIn('data-performance-value="resources"', self.html)
        self.assertIn('assets/js/site-experience.js', self.html)

    def test_progressive_enhancement_and_reduced_motion_are_present(self) -> None:
        self.assertIn('prefers-reduced-motion: reduce', self.styles)
        self.assertIn('[data-reveal]', self.styles)
        self.assertIn('IntersectionObserver', self.script)

    def test_public_corp_copy_uses_team_voice(self) -> None:
        self.assertNotIn('I help small businesses', self.html)
        self.assertNotIn('I built this company', self.html)
        self.assertNotIn('My approach combines', self.html)
        promotions = PROMOTIONS.read_text(encoding="utf-8")
        self.assertNotIn('"I identify the recurring tasks', promotions)
        self.assertNotIn('"I evaluate the current delivery process', promotions)
        self.assertNotIn('"I help you find simple ways', promotions)
        self.assertNotIn('"I review the way the business', promotions)


if __name__ == "__main__":
    unittest.main()
