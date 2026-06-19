#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"


class HomeHeroFoldFitTests(unittest.TestCase):
    def read_css(self, root: Path = WWW) -> str:
        return (root / "assets/css/viewport-contract.css").read_text(encoding="utf-8")

    def read_index(self, root: Path = WWW) -> str:
        return (root / "index.html").read_text(encoding="utf-8")

    def test_home_hero_places_motion_independent_from_promotion(self) -> None:
        css = self.read_css()
        self.assertIn("014: home motion independence and kinetic-word stability", css)
        self.assertIn('"headline promotion"', css)
        self.assertIn('"support promotion"', css)
        self.assertIn('"motion promotion" !important;', css)
        self.assertIn("#home .catalog-hero-card", css)
        self.assertIn("grid-area: promotion !important;", css)
        self.assertIn("#home .hero-motion-cluster", css)
        self.assertIn("grid-area: motion !important;", css)
        self.assertIn("background: transparent !important;", css)
        self.assertIn("box-shadow: none !important;", css)

    def test_home_hero_motion_cluster_is_outside_support_block(self) -> None:
        html = self.read_index()
        support_start = html.index('<div class="hero-support">')
        support_end = html.index('<div class="hero-motion-cluster">')
        support_block = html[support_start:support_end]
        self.assertIn('class="hero-sub"', support_block)
        self.assertIn('class="hero-actions"', support_block)
        self.assertNotIn('class="hero-motion-line"', support_block)
        self.assertIn('<div class="hero-motion-cluster">', html)

    def test_home_hero_motion_line_is_larger_and_stable(self) -> None:
        css = self.read_css()
        self.assertIn('#home .hero-motion-line', css)
        self.assertIn('font-size: clamp(1.48rem, 2.18vw, 2.08rem) !important;', css)
        self.assertIn('white-space: nowrap !important;', css)
        self.assertIn('min-height: 1.04em !important;', css)
        self.assertIn('#home .hero-motion-line [data-kinetic-word]', css)
        self.assertIn('min-width: 12ch !important;', css)
        self.assertIn('#home .hero-motion-line [data-kinetic-word].is-changing', css)
        self.assertIn('transform: none !important;', css)

    def test_root_has_exactly_one_motion_cluster(self) -> None:
        self.assertEqual(self.read_index().count('<div class="hero-motion-cluster">'), 1)


if __name__ == "__main__":
    unittest.main()
