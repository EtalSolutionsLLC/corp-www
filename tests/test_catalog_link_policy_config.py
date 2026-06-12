#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CatalogLinkPolicyConfigTests(unittest.TestCase):
    def load_items(self, catalog: str):
        return json.loads((ROOT / 'catalogs' / catalog / 'items.json').read_text(encoding='utf-8'))

    def test_promotions_open_external_booking_links_in_new_tab(self):
        for item in self.load_items('promotions'):
            action = item['primaryAction']
            self.assertIs(action.get('openInNewTab'), True)

    def test_brands_keep_current_mailto_actions_in_same_tab(self):
        for item in self.load_items('brands'):
            action = item['primaryAction']
            self.assertTrue(action['href'].startswith('mailto:'))
            self.assertIs(action.get('openInNewTab'), False)

    def test_rendered_promotion_links_include_safe_new_tab_attributes(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        start = html.index('id="promotions"')
        end = html.index('id="blog"', start)
        promotions_html = html[start:end]
        self.assertEqual(promotions_html.count('target="_blank" rel="noopener noreferrer"'), 4)

    def test_footer_loads_privacy_close_button_override_after_shared_modal(self):
        footer = (ROOT / 'partials' / 'footer.html').read_text(encoding='utf-8')
        shared = footer.index('assets/js/policy-modal.js')
        override = footer.index('/assets/js/policy-modal-close.js')
        self.assertLess(shared, override)
        self.assertIn('/assets/css/policy-modal-overrides.css', footer)


if __name__ == '__main__':
    unittest.main()
