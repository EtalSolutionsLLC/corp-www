#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class HomeQuickSummaryModalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.footer = (ROOT / "partials/footer.html").read_text(encoding="utf-8")
        cls.styles = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")
        cls.modal_css = (ROOT / "assets/css/home-quick-summary.css").read_text(encoding="utf-8")
        cls.modal_system = (ROOT / "assets/css/modal-close-system.css").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets/js/home-quick-summary.js").read_text(encoding="utf-8")

    def test_inline_details_disclosure_is_retired(self):
        self.assertNotIn('<details class="quick-summary">', self.index)
        self.assertNotIn(".quick-summary summary", self.styles)
        self.assertNotIn(".quick-summary p", self.styles)

    def test_homepage_retains_compact_trigger(self):
        self.assertIn("data-home-quick-open", self.index)
        self.assertIn("In a hurry? Read the 60-second version.", self.index)
        self.assertIn('aria-controls="home-quick-summary-modal"', self.index)

    def test_summary_content_is_delivered_in_standard_dialog(self):
        for token in [
            'class="home-quick-summary-modal"',
            'id="home-quick-summary-modal"',
            "data-home-quick-modal",
            "data-home-quick-close",
            "Lighter technology. Clearer next steps.",
            "Explore your situation",
            "Start a conversation",
        ]:
            self.assertIn(token, self.index)

    def test_modal_uses_shared_circle_close_control(self):
        self.assertIn("home-quick-summary-modal-close modal-close-circle", self.index)
        self.assertIn(".home-quick-summary-modal-close", self.modal_system)

    def test_footer_loads_isolated_modal_assets(self):
        self.assertIn("/assets/css/home-quick-summary.css", self.footer)
        self.assertIn("/assets/js/home-quick-summary.js", self.footer)
        self.assertIn("/assets/css/home-quick-summary.css", self.index)
        self.assertIn("/assets/js/home-quick-summary.js", self.index)

    def test_dialog_supports_open_close_outside_click_and_action_close(self):
        for token in [
            'typeof modal.showModal === "function"',
            "openButton.addEventListener",
            "closeButton.addEventListener",
            "if (event.target === modal) closeSummary();",
            '[data-home-quick-modal-action]',
        ]:
            self.assertIn(token, self.js)

    def test_modal_has_responsive_top_layer_layout(self):
        for token in [
            ".home-quick-summary-modal {",
            ".home-quick-summary-modal::backdrop",
            ".home-quick-summary-grid {",
            "@media (max-width: 680px)",
        ]:
            self.assertIn(token, self.modal_css)

    def test_no_blanket_panel_padding_rule_was_added_for_design_guideline(self):
        self.assertNotIn("/* Half-inch viewport padding rule */", self.styles)
        self.assertNotIn("--viewport-half-inch", self.styles)

if __name__ == "__main__":
    unittest.main()
