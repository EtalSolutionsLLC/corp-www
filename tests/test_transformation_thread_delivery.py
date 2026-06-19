#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
COLLECTION = SITE / "collections" / "transformation-thread"


class TransformationThreadDeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((COLLECTION / "collection.json").read_text(encoding="utf-8"))
        cls.posts = json.loads((COLLECTION / "items.json").read_text(encoding="utf-8"))
        cls.selection = json.loads((COLLECTION / "generated/selection.json").read_text(encoding="utf-8"))
        cls.index = (SITE / "index.html").read_text(encoding="utf-8")
        cls.js = (SITE / "collections/_system/collection.js").read_text(encoding="utf-8")
        cls.css = (COLLECTION / "styles.css").read_text(encoding="utf-8")
        cls.modal = (SITE / "assets/css/modal-close-system.css").read_text(encoding="utf-8")

    def resolve(self, ref: str) -> Path:
        return COLLECTION / ref

    def test_collection_manifest_owns_publication_and_rotation_policy(self):
        self.assertEqual(self.manifest["id"], "transformation-thread")
        self.assertEqual(self.manifest["mode"], "publication")
        self.assertEqual(self.manifest["dataFile"], "items.json")
        self.assertEqual(self.manifest["selection"]["outputFile"], "generated/selection.json")
        self.assertEqual(self.manifest["selection"]["timezone"], "America/New_York")
        self.assertEqual(self.manifest["selection"]["visibleItems"], 3)

    def test_every_post_has_permanent_id_repeating_slot_and_markdown_refs(self):
        self.assertEqual([post["id"] for post in self.posts], list(range(1, len(self.posts) + 1)))
        self.assertEqual([post["slot"] for post in self.posts], [1, 2, 3, 4, 5, 6, 7, 1, 2])
        for post in self.posts:
            self.assertNotIn("title", post)
            self.assertNotIn("summary", post)
            self.assertNotIn("body", post)
            for field in ["title_md", "excerpt_md", "full_article_md"]:
                self.assertTrue(post[field].endswith(".md"))
                self.assertTrue(self.resolve(post[field]).is_file())

    def test_every_existing_post_has_a_complete_full_article(self):
        for post in self.posts:
            article = self.resolve(post["full_article_md"]).read_text(encoding="utf-8").strip()
            self.assertGreaterEqual(len(article), 500, f"Post {post['id']} full article is too short")

    def test_title_excerpt_and_full_article_markdown_files_are_non_empty(self):
        for post in self.posts:
            for field in ["title_md", "excerpt_md", "full_article_md"]:
                self.assertTrue(self.resolve(post[field]).read_text(encoding="utf-8").strip())

    def test_generated_selection_is_collection_owned_and_materialized(self):
        self.assertEqual(self.selection["collection"], "transformation-thread")
        self.assertEqual(len(self.selection["visibleItems"]), 3)
        for item in self.selection["visibleItems"]:
            self.assertIn(f'data-collection-item-id="{item["id"]}"', self.index)
            self.assertNotIn(
                self.resolve(next(p["full_article_md"] for p in self.posts if p["id"] == item["id"]))
                .read_text(encoding="utf-8")
                .strip(),
                self.index,
            )

    def test_request_action_fetches_full_article_markdown_only_on_request(self):
        for token in [
            'data-collection-mode="publication"',
            "data-collection-open-item",
            "data-collection-modal",
            "data-collection-modal-title",
            "data-collection-modal-body",
            "data-collection-modal-close",
        ]:
            self.assertIn(token, self.index)
        for token in [
            "initPublication",
            "loadCollection",
            "loadText",
            "item.title_md",
            "item.full_article_md",
            "renderMarkdown",
            "openItem",
        ]:
            self.assertIn(token, self.js)
        self.assertNotIn("item.body", self.js)

    def test_markdown_renderer_uses_dom_text_nodes_for_untrusted_text(self):
        publication = self.js[self.js.index("function initPublication"):]
        self.assertIn("document.createTextNode", publication)
        self.assertIn("textContent", publication)
        self.assertNotIn("article.innerHTML", publication)

    def test_delivery_assets_load_from_the_spa_entry_point(self):
        self.assertIn("collections/transformation-thread/styles.css", self.index)
        self.assertIn("collections/_system/collection.css", self.index)
        self.assertIn("collections/_system/collection.js", self.index)

    def test_article_modal_uses_sitewide_circle_close_standard(self):
        self.assertIn("thread-article-modal-close modal-close-circle", self.index)
        self.assertIn(".thread-article-modal-close", self.modal)
        self.assertIn(".thread-article-modal {", self.css)


if __name__ == "__main__":
    unittest.main()
