from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"


class PolicyModalCloseStyleTests(unittest.TestCase):
    def test_privacy_close_is_icon_only_circle(self):
        js = (WWW / "assets/js/policy-modal-close.js").read_text(encoding="utf-8")
        self.assertIn('element.textContent = "×";', js)
        self.assertIn('element.classList.add("modal-close-circle", enhancedClass);', js)
        self.assertIn('hostClass = "policy-modal-close-host"', js)
        self.assertIn('findCloseHost(element)', js)
        self.assertNotIn('Close ×', js)

    def test_privacy_close_uses_fixed_circle_dimensions(self):
        css = (WWW / "assets/css/policy-modal-overrides.css").read_text(encoding="utf-8")
        for token in [
            "width: 32px !important;",
            "height: 32px !important;",
            "border-radius: 50% !important;",
            "aspect-ratio: 1 / 1 !important;",
            "padding: 0 !important;",
        ]:
            self.assertIn(token, css)

    def test_enhancer_observes_inserted_modal_controls_without_attribute_loop(self):
        js = (WWW / "assets/js/policy-modal-close.js").read_text(encoding="utf-8")
        for token in ["new MutationObserver", "childList: true", "subtree: true"]:
            self.assertIn(token, js)
        self.assertNotIn("attributes: true", js)
        self.assertNotIn("attributeFilter", js)


if __name__ == "__main__":
    unittest.main()
