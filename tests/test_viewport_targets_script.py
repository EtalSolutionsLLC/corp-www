#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"
JS = (WWW / "assets/js/viewport-targets.js").read_text(encoding="utf-8")
INDEX = (WWW / "index.html").read_text(encoding="utf-8")


class ViewportTargetsScriptTests(unittest.TestCase):
    def test_script_is_plain_browser_javascript(self) -> None:
        self.assertNotIn("import ", JS)
        self.assertNotIn("require(", JS)
        self.assertNotIn("jquery", JS.lower())

    def test_script_updates_contract_variables(self) -> None:
        for token in [
            "--pm-header-height",
            "--pm-footer-height",
            "--pm-visible-panel-height",
            "--header-h",
            "--footer-h",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, JS)

    def test_script_supports_exact_hash_alignment(self) -> None:
        self.assertIn("hashchange", JS)
        self.assertIn("decodeURIComponent", JS)
        self.assertIn("window.scrollTo", JS)
        self.assertIn("const targetRect = target.getBoundingClientRect();", JS)
        self.assertIn("window.pageYOffset + delta", JS)

    def test_script_controls_same_document_hash_clicks(self) -> None:
        self.assertIn('document.addEventListener("click"', JS)
        self.assertIn('event.target.closest("a[href]")', JS)
        self.assertIn("sameDocumentHashLink", JS)
        self.assertIn("event.preventDefault()", JS)
        self.assertIn("window.history.pushState", JS)

    def test_script_realigns_even_when_hash_does_not_change(self) -> None:
        self.assertIn("popstate", JS)
        self.assertIn("alignmentDelays", JS)
        self.assertIn("runAlignmentPasses", JS)
        self.assertIn("requestHashAlignment();", JS)


    def test_script_centers_short_inner_content_in_live_slot(self) -> None:
        self.assertIn('querySelector(":scope > .pm-viewport-target__inner")', JS)
        self.assertIn("const slot = visibleSlotBounds();", JS)
        self.assertIn("const subjectCenter = subjectRect.top + (subjectRect.height / 2);", JS)
        self.assertIn("delta = subjectCenter - slot.center;", JS)
        self.assertIn("subjectRect.height <= slot.height", JS)


    def test_script_updates_primary_nav_for_controlled_hash_navigation(self) -> None:
        self.assertIn("function updatePrimaryNavigation", JS)
        self.assertIn('document.querySelectorAll(".site-header .nav a[href]")', JS)
        self.assertIn('link.setAttribute("aria-current", "page")', JS)
        self.assertIn('document.body.classList.toggle("has-js-active-nav", hasActiveLink)', JS)


    def test_script_uses_live_chrome_edges_and_self_correcting_delta(self) -> None:
        self.assertIn("function visibleSlotBounds", JS)
        self.assertIn("headerRect.bottom", JS)
        self.assertIn("footerRect.top", JS)
        self.assertIn("window.pageYOffset + delta", JS)

    def test_script_honors_explicit_start_alignment(self) -> None:
        self.assertIn("function alignmentMode", JS)
        self.assertIn('getAttribute("data-pm-viewport-align")', JS)
        self.assertIn('alignmentMode(target) === "start"', JS)

    def test_script_realigns_after_fonts_and_chrome_settle(self) -> None:
        self.assertIn("document.fonts.ready.then(requestHashAlignment)", JS)
        self.assertIn("function requestChromeMeasurement", JS)
        self.assertIn("new ResizeObserver(requestChromeMeasurement)", JS)

    def test_script_loads_before_visual_polish(self) -> None:
        self.assertLess(INDEX.index("assets/js/viewport-targets.js"), INDEX.index("assets/js/visual-polish.js"))


if __name__ == "__main__":
    unittest.main()
