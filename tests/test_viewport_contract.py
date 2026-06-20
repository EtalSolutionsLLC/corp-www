#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"

PRIMARY_TARGETS = ["home", "services", "lab", "brands", "promotions", "blog", "about", "contact"]


class ViewportContractTests(unittest.TestCase):
    def read(self, rel: str, root: Path = WWW) -> str:
        return (root / rel).read_text(encoding="utf-8")

    def test_viewport_contract_is_loaded_after_section_css(self) -> None:
        index = self.read("index.html")
        lab_pos = index.index('href="collections/systems-lab/styles.css"')
        rhythm_pos = index.index('href="assets/css/theme-rhythm.css"')
        contract_pos = index.index('href="assets/css/viewport-contract.css"')
        self.assertGreater(contract_pos, lab_pos)
        self.assertGreater(contract_pos, rhythm_pos)

    def test_deploy_snapshots_are_not_part_of_root_contract_assertions(self) -> None:
        self.assertTrue((ROOT / "deploy" / "prd").is_dir())

    def test_contract_declares_header_footer_bounded_slot(self) -> None:
        css = self.read("assets/css/viewport-contract.css")
        self.assertIn("--pm-header-height", css)
        self.assertIn("--pm-footer-height", css)
        self.assertIn("--pm-visible-panel-height", css)
        self.assertIn("calc(100dvh - var(--pm-header-height) - var(--pm-footer-height))", css)
        self.assertIn("scroll-padding-top: var(--pm-scroll-clearance) !important;", css)

    def test_target_class_names_do_not_use_section_language(self) -> None:
        css = self.read("assets/css/viewport-contract.css")
        self.assertIn(".pm-viewport-target", css)
        self.assertIn(".pm-viewport-target__inner", css)
        self.assertNotIn("pm-viewport-section", css)

    def test_targeted_panels_fill_visible_slot_and_center_short_content(self) -> None:
        css = self.read("assets/css/viewport-contract.css")
        target_block = css.split(".pm-viewport-target:target,", 1)[1].split("}", 1)[0]
        self.assertIn("min-height: var(--pm-visible-panel-height) !important;", target_block)
        self.assertIn("display: grid !important;", target_block)
        self.assertIn("align-items: center !important;", target_block)
        self.assertIn("padding-top: var(--pm-viewport-block) !important;", target_block)
        self.assertIn("padding-bottom: var(--pm-viewport-block) !important;", target_block)


    def test_viewport_target_padding_is_reduced_for_live_slot_alignment(self) -> None:
        css = self.read("assets/css/viewport-contract.css")
        self.assertIn("--pm-viewport-block: clamp(16px, 2.1vw, 29px);", css)
        self.assertIn("--pm-viewport-block-tight: clamp(12px, 1.6vw, 22px);", css)
        self.assertIn("--pm-hero-block: clamp(13px, 1.9vw, 26px);", css)


    def test_viewport_target_inner_preserves_header_container_width(self) -> None:
        css = self.read("assets/css/viewport-contract.css")
        inner_block = css.split(".pm-viewport-target > .pm-viewport-target__inner", 1)[1].split("}", 1)[0]
        self.assertIn("width: min(calc(100% - (var(--inner-gutter) * 2)), var(--inner-max)) !important;", inner_block)
        self.assertIn("max-width: var(--inner-max);", inner_block)
        self.assertIn("margin-left: auto;", inner_block)
        self.assertIn("margin-right: auto;", inner_block)
        self.assertNotIn("width: 100%;", inner_block)


    def test_js_active_nav_state_overrides_stale_target_decoration(self) -> None:
        css = self.read("assets/css/viewport-contract.css")
        self.assertIn('body.has-js-active-nav .site-header .nav a:not([aria-current="page"])', css)
        self.assertIn('.site-header .nav a[aria-current="page"]', css)
        self.assertIn("color: #b8cdff !important;", css)
        self.assertIn("opacity: 1 !important;", css)

    def test_primary_nav_targets_are_explicit_viewport_targets(self) -> None:
        index = self.read("index.html")
        for target_id in PRIMARY_TARGETS:
            with self.subTest(target_id=target_id):
                match = re.search(rf'<section[^>]+id="{target_id}"[^>]*>', index)
                self.assertIsNotNone(match)
                tag = match.group(0)
                self.assertIn("pm-viewport-target", tag)
                self.assertIn("pm-scroll-target", tag)

    def test_viewport_script_is_loaded_and_measures_live_chrome(self) -> None:
        index = self.read("index.html")
        js = self.read("assets/js/viewport-targets.js")
        self.assertIn('assets/js/viewport-targets.js', index)
        self.assertLess(index.index('assets/js/viewport-targets.js'), index.index('assets/js/visual-polish.js'))
        self.assertIn('getBoundingClientRect().height', js)
        self.assertIn('window.visualViewport', js)
        self.assertIn('--pm-visible-panel-height', js)
        self.assertIn('--header-h', js)
        self.assertIn('--footer-h', js)

    def test_catalog_and_lab_heights_are_neutralized_inside_targets(self) -> None:
        css = self.read("assets/css/viewport-contract.css")
        self.assertIn(".catalog-item-panels,", css)
        self.assertIn(".workspace-tile,", css)
        self.assertIn(".workspace-tool-panel,", css)
        self.assertIn("min-height: auto !important;", css)
        self.assertIn("#lab.pm-viewport-target:target", css)
        self.assertIn("transform: none !important;", css)


if __name__ == "__main__":
    unittest.main()
