#!/usr/bin/env python3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"


class PolicyModalClosePositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.override_css = (WWW / "assets/css/policy-modal-overrides.css").read_text(encoding="utf-8")
        cls.system_css = (WWW / "assets/css/modal-close-system.css").read_text(encoding="utf-8")
        cls.js = (WWW / "assets/js/policy-modal-close.js").read_text(encoding="utf-8")

    def test_close_button_is_pinned_to_upper_right(self):
        for token in [
            "position: absolute !important;",
            "top: 12px !important;",
            "right: 12px !important;",
            "bottom: auto !important;",
            "left: auto !important;",
        ]:
            self.assertIn(token, self.override_css)
            self.assertIn(token, self.system_css)

    def test_policy_close_position_is_restored_after_shared_icon_rule(self):
        relative_rule = self.system_css.index("position: relative !important;")
        late_guard = self.system_css.index("008: keep external policy-modal close control pinned")
        absolute_after_guard = self.system_css.index("position: absolute !important;", late_guard)
        self.assertGreater(late_guard, relative_rule)
        self.assertGreater(absolute_after_guard, late_guard)
        self.assertIn("policy-modal-close-host", self.system_css)
        self.assertIn("policy-modal-close-host", self.js)

    def test_close_button_is_circular_icon_control(self):
        for token in [
            "width: 32px !important;",
            "height: 32px !important;",
            "border-radius: 50% !important;",
            "padding: 0 !important;",
        ]:
            self.assertIn(token, self.override_css)
        self.assertNotIn("padding: 0 11px;", self.override_css)


if __name__ == "__main__":
    unittest.main()
