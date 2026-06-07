#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
PARTIAL = (ROOT / "partials/transformation-thread.html").read_text(encoding="utf-8")
HEADERS = [
    (ROOT / "partials/header.html").read_text(encoding="utf-8"),
    (ROOT / "partials/brand-header.html").read_text(encoding="utf-8"),
    (ROOT / "partials/promotion-header.html").read_text(encoding="utf-8"),
]

EXPECTED_LINKS = [
    '/#home',
    '/#services',
    '/#brands',
    '/#promotions',
    '/#blog',
    '/#about',
    '/#contact',
]
EXPECTED_PANEL_IDS = ['home', 'services', 'brands', 'promotions', 'blog', 'about', 'contact']


class SpaBlogPartialTests(unittest.TestCase):
    def test_menu_order_is_consistent_across_partials(self):
        for header in HEADERS:
            positions = [header.index(f'href="{href}"') for href in EXPECTED_LINKS]
            self.assertEqual(positions, sorted(positions))

    def test_panel_order_matches_menu_order(self):
        positions = [INDEX.index(f'id="{panel_id}"') for panel_id in EXPECTED_PANEL_IDS]
        self.assertEqual(positions, sorted(positions))

    def test_blog_uses_portmason_partial_region(self):
        self.assertIn('<!-- PM:TRANSFORMATION-THREAD -->', INDEX)
        self.assertIn('<!-- /PM:TRANSFORMATION-THREAD -->', INDEX)
        self.assertIn('<section class="thread-blog panel" id="blog"', PARTIAL)

    def test_blog_rotation_region_lives_inside_partial(self):
        self.assertIn('<!-- TT:DAILY-ROTATION:START -->', PARTIAL)
        self.assertIn('<!-- TT:DAILY-ROTATION:END -->', PARTIAL)

    def test_counter_selector_and_refinements_remain(self):
        self.assertIn('data-performance-proof', INDEX)
        self.assertIn('data-service-selector', INDEX)
        self.assertIn('assets/js/visual-polish.js', INDEX)
        self.assertIn('assets/js/catalog-carousel.js', INDEX)


if __name__ == "__main__":
    unittest.main()
