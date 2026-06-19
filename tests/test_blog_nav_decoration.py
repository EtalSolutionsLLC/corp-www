#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
HEADER = (ROOT / "partials/header.html").read_text(encoding="utf-8")
BLOG_REDIRECT = (ROOT / "transformation-thread/index.html").read_text(encoding="utf-8")


class BlogNavDecorationTests(unittest.TestCase):
    def test_blog_is_an_spa_target(self):
        self.assertRegex(INDEX, r'<section class="thread-blog panel[^"]*pm-viewport-target[^"]*" id="blog"')
        self.assertIn('<a href="/#blog">Blog</a>', HEADER)

    def test_blog_target_decorates_blog_link(self):
        self.assertIn('body:has(#blog:target) .nav a[href$="#blog"]::after', CSS)
        self.assertIn('body:has(#blog:target) .nav a[href$="#blog"]', CSS)

    def test_blog_route_is_compatibility_redirect(self):
        self.assertIn('window.location.replace("/#blog")', BLOG_REDIRECT)
        self.assertIn('url=/#blog', BLOG_REDIRECT)

    def test_durable_page_override_is_removed(self):
        self.assertNotIn('body[data-brand-name="Blog"]', CSS)
        self.assertNotIn('/transformation-thread/">Blog</a>', HEADER)

    def test_no_navigation_script_is_required(self):
        self.assertNotIn('hashchange', CSS)
        self.assertNotIn('scrollIntoView', CSS)


if __name__ == "__main__":
    unittest.main()
