#!/usr/bin/env python3
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"


class CatalogLinkTreatmentTests(unittest.TestCase):
    def test_catalog_text_links_do_not_use_focus_border_or_pill(self):
        css = (WWW / "assets/css/action-system.css").read_text(encoding="utf-8")
        focus_block = css.split("008: text catalog links use underline/color focus", 1)[1]
        self.assertIn(".catalog-inline-link:focus-visible", focus_block)
        self.assertIn(".catalog-direction-link:focus-visible", focus_block)
        self.assertIn("box-shadow: none !important;", focus_block)
        self.assertIn("border-color: transparent !important;", focus_block)
        self.assertIn("text-decoration: underline !important;", focus_block)

    def test_catalog_text_links_are_removed_from_shared_focus_box_shadow_rule(self):
        css = (WWW / "assets/css/action-system.css").read_text(encoding="utf-8")
        shared_focus = css.split(".action:focus-visible,", 1)[1].split("}", 1)[0]
        self.assertNotIn(".catalog-inline-link:focus-visible", shared_focus)
        self.assertNotIn(".brand-overview-link:focus-visible", shared_focus)


if __name__ == "__main__":
    unittest.main()
