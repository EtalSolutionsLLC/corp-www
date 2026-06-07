#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")


class HeaderViewportTests(unittest.TestCase):
    def test_header_uses_shared_invisible_viewport(self):
        self.assertIn(
            ".site-header .container {\n"
            "  width: min(calc(100% - (var(--inner-gutter) * 2)), var(--inner-max));",
            CSS,
        )
        self.assertNotIn(
            ".site-header .container {\n"
            "  width: min(calc(100% - 48px), var(--max));",
            CSS,
        )

    def test_header_boundary_is_natural_not_ruled(self):
        self.assertIn("  border-bottom: 0;\n  box-shadow: none;", CSS)

    def test_nav_spacing_uses_available_room_without_full_width_stretch(self):
        self.assertIn("gap: clamp(16px, 1.6vw, 28px);", CSS)
        self.assertIn("justify-content: flex-end;", CSS)

    def test_mobile_nav_behavior_remains_intact(self):
        self.assertIn("    width: 100%;\n    gap: 10px 16px;\n    justify-content: flex-start;", CSS)
        self.assertIn("    overflow-x: auto;", CSS)


if __name__ == "__main__":
    unittest.main()
