#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
CSS = (SITE / 'assets/css/styles.css').read_text(encoding='utf-8')


class HeaderViewportTests(unittest.TestCase):
    def test_header_uses_shared_container_width(self):
        header_block = CSS.split('.site-header .container {', 1)[1].split('}', 1)[0]
        self.assertNotIn('width:', header_block)
        self.assertIn('gap: clamp(24px, 3vw, 48px);', header_block)

    def test_initial_header_has_no_hard_rule_or_shadow(self):
        header_block = CSS.split('.site-header {', 1)[1].split('}', 1)[0]
        self.assertIn('border-bottom: 0;', header_block)
        self.assertIn('box-shadow: none;', header_block)

    def test_desktop_nav_uses_responsive_spacing(self):
        nav_block = CSS.split('.nav {', 1)[1].split('}', 1)[0]
        self.assertIn('gap: clamp(16px, 1.6vw, 28px);', nav_block)

    def test_mobile_nav_behavior_is_preserved(self):
        self.assertIn('@media (max-width: 820px)', CSS)
        self.assertIn('overflow-x: auto;', CSS)
        self.assertIn('justify-content: flex-start;', CSS)


if __name__ == '__main__':
    unittest.main()
