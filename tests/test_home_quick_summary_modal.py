#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"

class HomeQuickSummaryModalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (SITE / "index.html").read_text(encoding="utf-8")
        cls.footer = (SITE / "partials/footer.html").read_text(encoding="utf-8")
        cls.styles = (SITE / "assets/css/styles.css").read_text(encoding="utf-8")
        cls.modal_css = (SITE / "assets/css/home-quick-summary.css").read_text(encoding="utf-8")
        cls.modal_system = (SITE / "assets/css/modal-close-system.css").read_text(encoding="utf-8")
        cls.js = (SITE / "assets/js/home-quick-summary.js").read_text(encoding="utf-8")

    def test_inline_details_disclosure_is_retired(self):
        self.assertNotIn('<details class="quick-summary">', self.index)
        self.assertNotIn(".quick-summary summary", self.styles)
        self.assertNotIn(".quick-summary p", self.styles)

    def test_homepage_retains_compact_trigger(self):
        self.assertIn("data-home-quick-open", self.index)
        self.assertIn("Need the short version? Read this in 60 seconds.", self.index)
        self.assertIn('aria-controls="home-quick-summary-modal"', self.index)

    def test_summary_content_is_delivered_in_standard_dialog(self):
        for token in [
            'class="home-quick-summary-modal"',
            'id="home-quick-summary-modal"',
            "data-home-quick-modal",
            "data-home-quick-close",
            "Better decisions. Lighter systems. Clearer next steps.",
            "See the systems in action",
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
