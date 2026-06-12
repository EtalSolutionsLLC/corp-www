from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")
CAROUSEL_CSS = (ROOT / "assets/css/carousel.css").read_text(encoding="utf-8")
JS = (ROOT / "assets/js/visual-polish.js").read_text(encoding="utf-8")
EXPLORE_JS = (ROOT / "assets/js/explore-decision-tree.js").read_text(encoding="utf-8")
TREE = (ROOT / "content/explore-decision-tree.json").read_text(encoding="utf-8")

NATIVE_TARGET_BLOCK = """section[id] {
  scroll-margin-top: calc(var(--header-h)); /* + 12px);(*/
}

.panel {
  display: block;
  min-height: auto;
  padding: clamp(42px, 6vh, 76px) 0;
  scroll-margin-top: calc(var(--header-h)); /* + 12px);*/
}

.panel:target {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: stretch;
  min-height: calc(100vh - var(--header-h) - var(--footer-h));
  min-height: calc(100dvh - var(--header-h) - var(--footer-h));
  padding-top: 0;
  padding-bottom: 0;
}
"""


class CorpSiteRefinementTests(unittest.TestCase):
    def test_native_target_contract_is_unchanged(self) -> None:
        self.assertIn(NATIVE_TARGET_BLOCK, CSS)

    def test_guided_service_selector_exists(self) -> None:
        self.assertIn('data-explore-root', INDEX)
        self.assertIn('content/explore-decision-tree.json', INDEX)
        self.assertIn('"pressure"', TREE)
        self.assertIn('"constraint"', TREE)
        self.assertIn('"exposure"', TREE)
        self.assertIn('"move"', TREE)
        self.assertIn('data-explore-result-title', INDEX)
        self.assertIn('renderQuestion', EXPLORE_JS)

    def test_visual_polish_does_not_take_over_anchor_navigation(self) -> None:
        forbidden = [
            'hashchange',
            'pushState',
            'replaceState',
            'scrollIntoView',
            'window.location.hash',
        ]
        for token in forbidden:
            self.assertNotIn(token, JS)

    def test_live_counter_remains_present(self) -> None:
        self.assertIn('data-performance-proof', INDEX)
        self.assertIn('data-performance-transfer', INDEX)
        self.assertIn('data-performance-js', INDEX)
        self.assertIn('data-performance-resources', INDEX)
        self.assertIn('updatePerformanceProof', JS)

    def test_active_menu_decoration_persists(self) -> None:
        self.assertIn('body:has(#about:target) .nav a[href$="#about"]::after', CSS)
        self.assertIn('body:has(#contact:target) .nav a[href$="#contact"]::after', CSS)
        self.assertIn('body:has(#promotions [data-catalog-item]:target) .nav a[href$="#promotions"]::after', CSS)
        self.assertIn('body:has(#blog:target) .nav a[href$="#blog"]::after', CSS)
        self.assertIn('body:has(#brands [data-catalog-item]:target) .nav a[href$="#brands"]::after', CSS)

    def test_native_view_transition_polish_is_declared_without_controller_dependency(self) -> None:
        self.assertIn('@view-transition', CSS)
        self.assertIn('navigation: auto;', CSS)
        self.assertNotIn('document.startViewTransition', EXPLORE_JS)
        self.assertIn('setTrail', EXPLORE_JS)
        self.assertIn('setHidden(result, false)', EXPLORE_JS)

    def test_carousel_keyboard_refinement_is_native_and_accessible(self) -> None:
        self.assertIn('enableCarouselKeyboardRefinement', JS)
        self.assertIn('aria-roledescription', JS)
        self.assertIn('ArrowLeft', JS)
        self.assertIn('ArrowRight', JS)
        self.assertIn('Home', JS)
        self.assertIn('End', JS)
        self.assertIn('overscroll-behavior-inline: contain;', CAROUSEL_CSS)
        self.assertIn('touch-action: pan-x pan-y;', CAROUSEL_CSS)

    def test_no_imported_front_end_library_added(self) -> None:
        self.assertNotIn('import ', JS)
        self.assertNotIn('require(', JS)
        self.assertNotIn('React', JS)
        self.assertNotIn('jquery', JS.lower())


if __name__ == '__main__':
    unittest.main()
