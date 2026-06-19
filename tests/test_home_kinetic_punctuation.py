from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"


class HomeKineticPunctuationTests(unittest.TestCase):
    def test_period_is_inside_the_width_reserving_token(self) -> None:
        html = (SITE / "index.html").read_text(encoding="utf-8")
        expected = (
            '<span class="hero-kinetic-token"><span data-kinetic-word>useful</span>'
            '<span class="hero-kinetic-period" aria-hidden="true">.</span></span>'
        )
        self.assertIn(expected, html)
        self.assertNotIn('<span data-kinetic-word>useful</span>.', html)

    def test_width_is_reserved_after_punctuation_not_between_word_and_period(self) -> None:
        css = (SITE / "assets/css/viewport-contract.css").read_text(encoding="utf-8")
        self.assertIn(".hero-kinetic-token", css)
        self.assertIn("min-width: 12ch !important;", css)
        self.assertIn("#home .hero-motion-line [data-kinetic-word]", css)
        self.assertIn("min-width: 0 !important;", css)
        self.assertIn(".hero-kinetic-period", css)


if __name__ == "__main__":
    unittest.main()
