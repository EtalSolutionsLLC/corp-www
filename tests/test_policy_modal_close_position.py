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

    def test_policy_override_pins_close_button_to_upper_right(self):
        for token in [
            "position: absolute !important;",
            "top: 12px !important;",
            "right: 12px !important;",
            "bottom: auto !important;",
            "left: auto !important;",
        ]:
            self.assertIn(token, self.override_css)

    def test_shared_system_keeps_policy_close_in_canonical_corner_rule(self):
        start = self.system_css.index(".home-quick-summary-shell > .home-quick-summary-modal-close")
        end = self.system_css.index(".policy-modal-close-host {", start)
        corner_rule = self.system_css[start:end]
        for token in [
            ".policy-modal-close-host > .policy-modal-close-enhanced",
            ".policy-modal-close-enhanced[data-policy-modal-close-enhanced]",
            "position: absolute !important;",
            "top: var(--modal-close-inset) !important;",
            "right: var(--modal-close-inset) !important;",
            "bottom: auto !important;",
            "left: auto !important;",
        ]:
            self.assertIn(token, corner_rule)
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
