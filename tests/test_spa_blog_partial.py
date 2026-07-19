#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
INDEX = (SITE / "index.html").read_text(encoding="utf-8")
HEADER = (SITE / "partials/header.html").read_text(encoding="utf-8")
HOOK = SITE / "partials/hooks/collection-transformation-thread"

EXPECTED_LINKS = [
    "/#home", "/#services", "/#lab", "/#brands",
    "/#promotions", "/#blog", "/#newsroom", "/#about", "/#contact",
]
EXPECTED_PANEL_IDS = ["home", "services", "lab", "brands", "promotions", "blog", "newsroom", "about", "contact"]


def section_position(section_id: str) -> int:
    match = re.search(rf'<section\b[^>]*\bid="{re.escape(section_id)}"[^>]*>', INDEX)
    if not match:
        raise AssertionError(f"Missing section #{section_id}")
    return match.start()


class SpaBlogCollectionTests(unittest.TestCase):
    def test_menu_order_is_consistent(self):
        positions = [HEADER.index(f'href="{href}"') for href in EXPECTED_LINKS]
        self.assertEqual(positions, sorted(positions))

    def test_panel_order_matches_menu_order(self):
        positions = [section_position(panel_id) for panel_id in EXPECTED_PANEL_IDS]
        self.assertEqual(positions, sorted(positions))

    def test_blog_uses_collection_portmason_region(self):
        self.assertIn("<!-- PM:COLLECTION-TRANSFORMATION-THREAD -->", INDEX)
        self.assertIn("<!-- /PM:COLLECTION-TRANSFORMATION-THREAD -->", INDEX)
        self.assertTrue(HOOK.is_file())
        self.assertTrue(HOOK.stat().st_mode & 0o111)
        subprocess.run(["bash", "-n", str(HOOK)], check=True)

    def test_blog_is_publication_profile_inside_spa(self):
        tag = re.search(r'<section\b[^>]*\bid="blog"[^>]*>', INDEX)
        self.assertIsNotNone(tag)
        rendered = tag.group(0)
        self.assertIn('data-collection-id="transformation-thread"', rendered)
        self.assertIn('data-collection-mode="publication"', rendered)
        self.assertIn('/collections/transformation-thread/collection.json', rendered)
        self.assertNotIn("transformation-thread/index.html", INDEX)

    def test_counter_selector_and_collection_assets_remain(self):
        self.assertIn("data-performance-proof", INDEX)
        self.assertIn('data-collection-id="systems-lab"', INDEX)
        self.assertIn("assets/js/visual-polish.js", INDEX)
        self.assertIn("collections/_system/collection.js", INDEX)
        self.assertIn("collections/_system/collection.css", INDEX)

    def test_full_article_modal_is_rendered_by_collection_system(self):
        for token in [
            "data-collection-modal",
            "data-collection-modal-title",
            "data-collection-modal-body",
            "data-collection-modal-close",
        ]:
            self.assertIn(token, INDEX)
        self.assertIn("collections/transformation-thread/styles.css", INDEX)

    def test_newsroom_is_publication_profile_inside_spa(self):
        tag = re.search(r'<section\b[^>]*\bid="newsroom"[^>]*>', INDEX)
        self.assertIsNotNone(tag)
        rendered = tag.group(0)
        self.assertIn('data-collection-id="newsroom"', rendered)
        self.assertIn('data-collection-mode="publication"', rendered)
        self.assertIn('/collections/newsroom/collection.json', rendered)
        self.assertIn("<!-- PM:COLLECTION-NEWSROOM -->", INDEX)
        self.assertIn("collections/newsroom/styles.css", INDEX)


if __name__ == "__main__":
    unittest.main()
