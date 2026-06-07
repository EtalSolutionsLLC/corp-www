#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PolicyModalClosePositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / "assets/css/policy-modal-overrides.css").read_text(encoding="utf-8")

    def test_close_button_is_pinned_to_upper_right(self):
        self.assertIn("position: absolute !important;", self.css)
        self.assertIn("top: 12px !important;", self.css)
        self.assertIn("right: 12px !important;", self.css)
        self.assertIn("bottom: auto !important;", self.css)
        self.assertIn("left: auto !important;", self.css)

    def test_icon_button_dimensions_are_cleared(self):
        self.assertIn("width: auto !important;", self.css)
        self.assertIn("height: auto !important;", self.css)
        self.assertIn("max-width: none !important;", self.css)
        self.assertIn("aspect-ratio: auto !important;", self.css)

    def test_pill_geometry_is_preserved(self):
        self.assertIn("border-radius: 999px;", self.css)
        self.assertIn("padding: 0 11px;", self.css)


if __name__ == "__main__":
    unittest.main()
