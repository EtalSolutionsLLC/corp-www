#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"


class CatalogLinkPolicyConfigTests(unittest.TestCase):
    def load_items(self, collection_id: str):
        return json.loads(
            (SITE / "collections" / collection_id / "items.json").read_text(encoding="utf-8")
        )

    def section_html(self, section_id: str, next_section_id: str) -> str:
        html = (SITE / "index.html").read_text(encoding="utf-8")
        start_match = re.search(rf'<section\b[^>]*\bid="{re.escape(section_id)}"[^>]*>', html)
        end_match = re.search(rf'<section\b[^>]*\bid="{re.escape(next_section_id)}"[^>]*>', html)
        self.assertIsNotNone(start_match)
        self.assertIsNotNone(end_match)
        return html[start_match.start():end_match.start()]

    def test_promotions_open_external_booking_links_in_new_tab(self):
        for item in self.load_items("promotions"):
            self.assertIs(item["primaryAction"].get("openInNewTab"), True)

    def test_brands_keep_current_mailto_actions_in_same_tab(self):
        for item in self.load_items("brands"):
            action = item["primaryAction"]
            self.assertTrue(action["href"].startswith("mailto:"))
            self.assertIs(action.get("openInNewTab"), False)

    def test_rendered_promotion_links_include_safe_new_tab_attributes(self):
        promotions_html = self.section_html("promotions", "blog")
        expected = sum(
            1
            for item in self.load_items("promotions")
            if item.get("primaryAction", {}).get("openInNewTab")
        )
        self.assertEqual(
            promotions_html.count('target="_blank" rel="noopener noreferrer"'),
            expected,
        )

    def test_footer_loads_privacy_close_button_override_after_shared_modal(self):
        footer = (SITE / "partials" / "footer.html").read_text(encoding="utf-8")
        shared = footer.index("assets/js/policy-modal.js")
        override = footer.index("/assets/js/policy-modal-close.js")
        self.assertLess(shared, override)
        self.assertIn("/assets/css/policy-modal-overrides.css", footer)


if __name__ == "__main__":
    unittest.main()
