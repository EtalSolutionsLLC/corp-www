import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"


class StylingCommentsRedTests(unittest.TestCase):
    def read(self, rel):
        return (WWW / rel).read_text(encoding="utf-8")

    def test_home_quick_summary_trigger_has_no_decorative_arrow_span(self):
        html = self.read("index.html")
        self.assertIn("Need the short version? Read this in 60 seconds.</button>", html)
        self.assertNotIn('Need the short version? Read this in 60 seconds. <span aria-hidden="true">→</span>', html)

    def test_solutions_et_al_summary_copy_is_shorter(self):
        html = self.read("index.html")
        data = json.loads(self.read("collections/brands/items.json"))
        self.assertIn("Technology guidance for real operations.", html)
        self.assertIn("Technology guidance for real operations.", [item["title"] for item in data])
        self.assertNotIn("Focused technology guidance for real operational problems.", html)

    def test_viewport_contract_contains_styling_overrides(self):
        css = self.read("assets/css/viewport-contract.css")
        self.assertIn("015: styling comments in red", css)
        self.assertIn("#promotions .catalog-page-head h2", css)
        self.assertIn("white-space: nowrap", css)
        self.assertIn("#about .about-card", css)
        self.assertIn("border-left: 5px", css)
        self.assertIn("#brands .catalog-panel-summary h2", css)
        self.assertIn("#home .home-quick-summary-trigger span", css)


if __name__ == "__main__":
    unittest.main()
