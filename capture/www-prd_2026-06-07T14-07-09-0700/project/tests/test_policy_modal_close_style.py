from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class PolicyModalCloseStyleTests(unittest.TestCase):
    def test_privacy_close_uses_same_label_as_catalog_details(self):
        js = (ROOT / "assets/js/policy-modal-close.js").read_text(encoding="utf-8")
        self.assertIn('element.textContent = "Close ×";', js)
        self.assertIn('element.classList.add("catalog-detail-close", enhancedClass);', js)

    def test_privacy_close_clears_icon_button_dimensions(self):
        css = (ROOT / "assets/css/policy-modal-overrides.css").read_text(encoding="utf-8")
        self.assertIn("width: auto !important;", css)
        self.assertIn("height: auto !important;", css)
        self.assertIn("aspect-ratio: auto !important;", css)
        self.assertIn("white-space: nowrap !important;", css)

    def test_enhancer_observes_inserted_modal_controls_without_attribute_loop(self):
        js = (ROOT / "assets/js/policy-modal-close.js").read_text(encoding="utf-8")
        self.assertIn("new MutationObserver", js)
        self.assertIn("childList: true", js)
        self.assertIn("subtree: true", js)
        self.assertNotIn("attributes: true", js)
        self.assertNotIn("attributeFilter", js)

if __name__ == "__main__":
    unittest.main()
