from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
INDEX = (SITE / "index.html").read_text(encoding="utf-8")
CSS = (SITE / "assets/css/styles.css").read_text(encoding="utf-8")
COLLECTION_CSS = (SITE / "collections/_system/collection.css").read_text(encoding="utf-8")
JS = (SITE / "assets/js/visual-polish.js").read_text(encoding="utf-8")
COLLECTION_CORE = (SITE / "collections/_system/collection.js").read_text(encoding="utf-8")
LAB_JS = (SITE / "collections/systems-lab/workspace.js").read_text(encoding="utf-8")


class CorpSiteRefinementTests(unittest.TestCase):
    def test_portmason_workspace_is_the_primary_interactive_showcase(self):
        self.assertIn('data-collection-id="systems-lab"', INDEX)
        self.assertIn('data-collection-mode="workspace"', INDEX)
        self.assertIn("See the systems in action", INDEX)
        self.assertIn("Portmason Platform™", INDEX)
        self.assertIn("initCollection(root)", COLLECTION_CORE)
        self.assertIn("runExternalStatus", LAB_JS)
        self.assertIn("runPublishedRequest", LAB_JS)
        self.assertIn("runLocalModel", LAB_JS)

    def test_visual_polish_does_not_take_over_anchor_navigation(self):
        for token in ["hashchange", "pushState", "replaceState", "scrollIntoView", "window.location.hash"]:
            self.assertNotIn(token, JS)

    def test_live_counter_remains_present(self):
        for token in ["data-performance-proof", "data-performance-transfer", "data-performance-js", "data-performance-resources"]:
            self.assertIn(token, INDEX)
        self.assertIn("updatePerformanceProof", JS)

    def test_active_menu_decoration_persists(self):
        for token in ["#about", "#contact", "#promotions", "#blog", "#brands"]:
            self.assertIn(token, CSS)

    def test_carousel_keyboard_refinement_is_native_and_accessible(self):
        for token in ["enableCarouselKeyboardRefinement", "aria-roledescription", "ArrowLeft", "ArrowRight", "Home", "End"]:
            self.assertIn(token, JS)
        self.assertIn("overscroll-behavior-inline: contain;", COLLECTION_CSS)


if __name__ == "__main__":
    unittest.main()
