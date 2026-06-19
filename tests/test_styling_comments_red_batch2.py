import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"


class StylingCommentsRedBatch2Tests(unittest.TestCase):
    def read(self, rel: str) -> str:
        return (WWW / rel).read_text(encoding="utf-8")

    def test_catalog_details_links_have_no_oval_focus_or_border_treatment(self):
        css = self.read("assets/css/viewport-contract.css")
        batch = css.split("016: styling comments in red, batch 2", 1)[1]
        self.assertIn(".catalog-details-toggle", batch)
        self.assertIn("border: 0 !important;", batch)
        self.assertIn("border-radius: 0 !important;", batch)
        self.assertIn("box-shadow: none !important;", batch)
        self.assertIn("outline: none !important;", batch)
        self.assertIn("text-decoration: underline !important;", batch)

    def test_brand_cards_are_compacted_for_above_fold_ctas(self):
        css = self.read("assets/css/viewport-contract.css")
        batch = css.split("016: styling comments in red, batch 2", 1)[1]
        self.assertIn("#brands .catalog-item-panels", batch)
        self.assertIn("min-height: clamp(330px, calc(100dvh - 365px), 420px) !important;", batch)
        self.assertIn("#brands .catalog-panel-summary", batch)
        self.assertIn("justify-content: flex-start !important;", batch)
        self.assertIn("#brands .catalog-details-toggle", batch)
        self.assertIn("margin-top: 10px !important;", batch)

    def test_brand_copy_is_shortened_in_data_and_rendered_pages(self):
        data = json.loads(self.read("collections/brands/items.json"))
        by_id = {item["id"]: item for item in data}
        self.assertEqual(
            by_id["solutions-et-al"]["summary"],
            "Clear technical direction, practical systems, and implementation support without extra ceremony.",
        )
        self.assertEqual(by_id["25th-hour"]["title"], "Reclaimed time, used with intention.")
        self.assertLessEqual(len(by_id["simplifai"]["summary"]), 125)

        html = self.read("index.html")
        self.assertIn("Clear technical direction, practical systems, and implementation support without extra ceremony.", html)
        self.assertIn("Reclaimed time, used with intention.", html)
        self.assertNotIn("without unnecessary ceremony", html)
        self.assertNotIn("Helping people use reclaimed time with intention.", html)

    def test_explore_material_clips_child_overflow(self):
        css = self.read("assets/css/viewport-contract.css")
        batch = css.split("016: styling comments in red, batch 2", 1)[1]
        self.assertIn("#explore .explore-tool", batch)
        self.assertIn("#explore .explore-path-card", batch)
        self.assertIn("overflow: hidden !important;", batch)


if __name__ == "__main__":
    unittest.main()
