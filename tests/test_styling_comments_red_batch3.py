import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"
PRD = ROOT / "deploy" / "prd" / "www"


class StylingCommentsRedBatch3Tests(unittest.TestCase):
    def read_css(self, root: Path) -> str:
        return (root / "assets/css/viewport-contract.css").read_text(encoding="utf-8")

    def test_brand_card_blue_matches_promotions_card_blue(self):
        for root in (WWW, PRD):
            batch = self.read_css(root).split("017: styling comments in red, batch 3", 1)[1]
            self.assertIn("#brands .catalog-badge", batch)
            self.assertIn("#brands .catalog-details-toggle", batch)
            self.assertIn("color: #2f6bff !important;", batch)
            self.assertIn("border-top-color: #2f6bff !important;", batch)

    def test_explore_decision_card_is_the_clipping_boundary(self):
        for root in (WWW, PRD):
            batch = self.read_css(root).split("017: styling comments in red, batch 3", 1)[1]
            self.assertIn("#explore .explore-question-body.explore-decision-card", batch)
            self.assertIn("overflow: hidden !important;", batch)
            self.assertIn("contain: paint !important;", batch)
            self.assertIn("isolation: isolate !important;", batch)


if __name__ == "__main__":
    unittest.main()
