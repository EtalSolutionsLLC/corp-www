from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
INDEX = (SITE / "index.html").read_text(encoding="utf-8")
CSS = (SITE / "assets/css/styles.css").read_text(encoding="utf-8")
JS = (SITE / "assets/js/visual-polish.js").read_text(encoding="utf-8")


class VisualPolishTests(unittest.TestCase):
    def test_visual_polish_script_is_loaded(self) -> None:
        self.assertIn('assets/js/visual-polish.js', INDEX)

    def test_performance_proof_markup_exists(self) -> None:
        self.assertIn('data-performance-proof', INDEX)
        self.assertIn('data-performance-transfer', INDEX)
        self.assertIn('data-performance-js', INDEX)
        self.assertIn('data-performance-resources', INDEX)

    def test_native_target_panel_contract_remains_intact(self) -> None:
        self.assertIn('.panel:target {', CSS)
        self.assertIn('min-height: calc(100dvh - var(--header-h) - var(--footer-h));', CSS)
        self.assertIn('justify-content: center;', CSS)

    def test_visual_polish_does_not_override_anchor_navigation(self) -> None:
        forbidden = ['hashchange', 'pushState', 'replaceState', 'scrollIntoView', 'window.location.hash']
        for token in forbidden:
            self.assertNotIn(token, JS)

    def test_team_voice_applies_to_primary_www_copy(self) -> None:
        self.assertIn('We help smaller organizations choose the right technology', INDEX)
        self.assertIn('We help smaller organizations modernize', INDEX)
        self.assertNotIn('I help smaller organizations choose the right technology', INDEX)
        self.assertNotIn('I help smaller organizations modernize', INDEX)


if __name__ == '__main__':
    unittest.main()
