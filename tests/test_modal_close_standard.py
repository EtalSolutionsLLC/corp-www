#!/usr/bin/env python3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"


class ModalCloseStandardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = (SITE / "index.html").read_text(encoding="utf-8")
        cls.footer = (SITE / "partials/footer.html").read_text(encoding="utf-8")
        cls.collection = (SITE / "collections/_system/collection.js").read_text(encoding="utf-8")
        cls.policy = (SITE / "assets/js/policy-modal-close.js").read_text(encoding="utf-8")
        cls.system = (SITE / "assets/css/modal-close-system.css").read_text(encoding="utf-8")
        cls.action = (SITE / "assets/css/action-system.css").read_text(encoding="utf-8")
        cls.promotions = (SITE / "collections/promotions/styles.css").read_text(encoding="utf-8")
        cls.brands = (SITE / "collections/brands/styles.css").read_text(encoding="utf-8")
        cls.cookie = (SITE / "assets/css/cookie-consent-overrides.css").read_text(encoding="utf-8")

    def test_final_modal_close_system_loads_after_policy_override(self):
        self.assertLess(self.footer.index('/assets/css/policy-modal-overrides.css'), self.footer.index('/assets/css/modal-close-system.css'))
        self.assertIn('/assets/css/modal-close-system.css', self.index)

    def test_collection_detail_closer_is_icon_only(self):
        self.assertIn('closeButton.textContent = "×";', self.collection)
        self.assertIn('catalog-detail-close modal-close-circle', self.collection)
        self.assertNotIn('Close ×', self.collection)

    def test_collection_existing_closers_are_normalized(self):
        for token in [
            'function normalizeModalCloseControl(control)',
            'control.textContent = "×";',
            '[data-collection-detail-close], [data-collection-overview-close]',
        ]:
            self.assertIn(token, self.collection)

    def test_policy_closer_is_icon_only(self):
        self.assertIn('element.textContent = "×";', self.policy)
        self.assertNotIn('Close ×', self.policy)

    def test_every_known_modal_family_is_in_shared_circle_standard(self):
        for selector in [
            '.catalog-detail-close', '.catalog-overview-close', '.policy-modal-close-enhanced',
            '.explore-mesh-modal-close', '.thread-article-modal-close',
            '.home-quick-summary-modal-close', '#cc-main .pm__close-btn',
        ]:
            self.assertIn(selector, self.system)
        self.assertIn('border-radius: 50% !important;', self.system)
        self.assertIn('aspect-ratio: 1 / 1 !important;', self.system)

    def test_component_sources_no_longer_define_close_pills(self):
        overview = self.brands[self.brands.index('.catalog-overview-close {'):self.brands.index('.catalog-overview-close:hover,')]
        self.assertIn('border-radius: 50%;', overview)
        self.assertNotIn('border-radius: 999px;', overview)
        detail = self.promotions[self.promotions.index('.catalog-detail-modal .catalog-detail-close {'):self.promotions.index('.catalog-detail-modal .catalog-detail-close:hover,')]
        self.assertIn('border-radius: 50%;', detail)
        self.assertNotIn('border-radius: 999px;', detail)
        self.assertIn('#cc-main .pm__close-btn', self.cookie)

    def test_action_system_does_not_reapply_pill_geometry(self):
        block = self.action[self.action.index('.catalog-details-toggle {'):self.action.index('.thread-post-link:hover,')]
        self.assertIn('border-radius: var(--action-pill-radius);', block)
        self.assertIn('border-radius: 50%;', block)


if __name__ == '__main__':
    unittest.main()
