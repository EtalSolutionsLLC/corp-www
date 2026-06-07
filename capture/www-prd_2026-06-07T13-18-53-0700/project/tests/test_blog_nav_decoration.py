#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")
BLOG_HTML = (ROOT / "transformation-thread/index.html").read_text(encoding="utf-8")


class BlogNavDecorationTests(unittest.TestCase):
    def test_blog_page_declares_durable_page_marker(self):
        self.assertIn('<body data-brand-name="Blog">', BLOG_HTML)

    def test_blog_marker_decorates_blog_link(self):
        self.assertIn('body[data-brand-name="Blog"] .nav a[href="/transformation-thread/"]::after', CSS)
        self.assertIn('body[data-brand-name="Blog"] .nav a[href="/transformation-thread/"] {', CSS)

    def test_blog_marker_clears_spa_home_fallback(self):
        self.assertIn('body[data-brand-name="Blog"] .nav a[href$="#home"]::after', CSS)
        self.assertIn('body[data-brand-name="Blog"] .nav a[href$="#home"] {', CSS)

    def test_no_new_navigation_script_is_required(self):
        self.assertNotIn('hashchange', CSS)
        self.assertNotIn('scrollIntoView', CSS)


if __name__ == "__main__":
    unittest.main()
