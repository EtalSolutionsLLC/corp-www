from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "www/collections/transformation-thread/styles.css").read_text(encoding="utf-8")


class BlogAlignmentTests(unittest.TestCase):
    def test_showcase_and_article_column_align_from_the_top(self) -> None:
        self.assertIn("align-items: start;", CSS)
        self.assertIn("align-self: start;", CSS)
        self.assertIn("align-content: start;", CSS)
        self.assertIn("grid-template-rows: auto auto;", CSS)
        self.assertIn("margin: 0;", CSS)

    def test_featured_article_does_not_push_its_link_to_the_card_floor(self) -> None:
        self.assertIn(".thread-featured-post {", CSS)
        self.assertIn("justify-content: flex-start;", CSS)
        self.assertIn(".thread-featured-post .thread-post-link {", CSS)
        featured_link = CSS.split(".thread-featured-post .thread-post-link {", 1)[1].split("}", 1)[0]
        self.assertIn("margin-top: 0.45rem;", featured_link)
        self.assertNotIn("margin-top: auto;", featured_link)

    def test_collection_stylesheet_has_one_primary_layout_definition(self) -> None:
        # Each selector appears once at the base layer and once in the responsive layer.
        self.assertEqual(CSS.count(".thread-blog-showcase {"), 2)
        self.assertEqual(CSS.count(".thread-post-layout {"), 2)


if __name__ == "__main__":
    unittest.main()
