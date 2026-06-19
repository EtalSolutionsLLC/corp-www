#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
CSS = (SITE / "assets/css/styles.css").read_text(encoding="utf-8")
INDEX = (SITE / "index.html").read_text(encoding="utf-8")
HEADER = (SITE / "partials/header.html").read_text(encoding="utf-8")


class BlogNavDecorationTests(unittest.TestCase):
    def test_blog_is_an_spa_target(self):
        self.assertRegex(INDEX, r'<section class="thread-blog panel[^"]*pm-viewport-target[^"]*" id="blog"')
        self.assertIn('<a href="/#blog">Blog</a>', HEADER)

    def test_blog_target_decorates_blog_link(self):
        self.assertIn('body:has(#blog:target) .nav a[href$="#blog"]::after', CSS)
        self.assertIn('body:has(#blog:target) .nav a[href$="#blog"]', CSS)

    def test_blog_has_no_standalone_page(self):
        self.assertFalse((SITE / "transformation-thread/index.html").exists())

    def test_durable_page_override_is_removed(self):
        self.assertNotIn('body[data-brand-name="Blog"]', CSS)
        self.assertNotIn('/transformation-thread/">Blog</a>', HEADER)

    def test_no_navigation_script_is_required(self):
        self.assertNotIn('hashchange', CSS)
        self.assertNotIn('scrollIntoView', CSS)


if __name__ == "__main__":
    unittest.main()
