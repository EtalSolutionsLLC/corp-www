#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
COLLECTION = SITE / "collections" / "transformation-thread"


class TransformationThreadDeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((COLLECTION / "collection.json").read_text(encoding="utf-8"))
        cls.posts = []
        for item_dir in sorted(path for path in (COLLECTION / "items").iterdir() if path.is_dir()):
            meta = json.loads((item_dir / "meta.json").read_text(encoding="utf-8"))
            item_id = int(item_dir.name)
            cls.posts.append({
                **meta,
                "id": item_id,
                "slug": f"tt-{item_id:03d}",
                "title_md": f"items/{item_dir.name}/title.md",
                "excerpt_md": f"items/{item_dir.name}/excerpt.md",
                "full_article_md": f"items/{item_dir.name}/full-article.md",
            })
        cls.selection = json.loads((COLLECTION / "generated/selection.json").read_text(encoding="utf-8"))
        cls.index = (SITE / "index.html").read_text(encoding="utf-8")
        cls.index_text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", cls.index)))
        cls.js = (SITE / "collections/_system/profiles/publication.js").read_text(encoding="utf-8")
        cls.css = (COLLECTION / "styles.css").read_text(encoding="utf-8")
        cls.modal = (SITE / "assets/css/modal-close-system.css").read_text(encoding="utf-8")

    def resolve(self, ref: str) -> Path:
        return COLLECTION / ref

    def test_collection_manifest_owns_publication_and_rotation_policy(self):
        self.assertEqual(self.manifest["id"], "transformation-thread")
        self.assertEqual(self.manifest["mode"], "publication")
        self.assertNotIn("dataFile", self.manifest)
        self.assertEqual(self.manifest["selection"]["outputFile"], "generated/selection.json")
        self.assertEqual(self.manifest["selection"]["timezone"], "America/New_York")
        self.assertEqual(self.manifest["selection"]["visibleItems"], 3)

    def test_every_post_has_directory_derived_identity_and_complete_source_files(self):
        self.assertEqual([post["id"] for post in self.posts], list(range(1, len(self.posts) + 1)))
        self.assertEqual([post["slot"] for post in self.posts[:7]], [1, 2, 3, 4, 5, 6, 7])
        for post in self.posts:
            self.assertIsInstance(post["slot"], int)
            self.assertGreaterEqual(post["slot"], 1)
            meta = json.loads(self.resolve(f"items/{post['id']:03d}/meta.json").read_text(encoding="utf-8"))
            self.assertNotIn("id", meta)
            self.assertNotIn("slug", meta)
            self.assertNotIn("title_md", meta)
            self.assertIn("dateFirstDisplayed", meta)
            self.assertTrue(meta["dateFirstDisplayed"] is None or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", meta["dateFirstDisplayed"]))
            self.assertIsInstance(meta["displayAfter"], list)
            for predecessor in meta["displayAfter"]:
                self.assertRegex(predecessor, r"^[0-9]{3}$")
            for field in ["title_md", "excerpt_md", "full_article_md"]:
                self.assertTrue(post[field].endswith(".md"))
                self.assertTrue(self.resolve(post[field]).is_file())
                self.assertTrue(self.resolve(post[field]).read_text(encoding="utf-8").strip())

    def test_three_part_series_has_ordered_display_dependencies(self):
        posts_by_id = {post["id"]: post for post in self.posts}
        self.assertEqual(posts_by_id[10]["displayAfter"], [])
        self.assertEqual(posts_by_id[11]["displayAfter"], ["010"])
        self.assertEqual(posts_by_id[12]["displayAfter"], ["011"])

    def test_every_existing_post_has_a_complete_full_article(self):
        for post in self.posts:
            article = self.resolve(post["full_article_md"]).read_text(encoding="utf-8").strip()
            self.assertGreaterEqual(len(article), 500, f"Post {post['id']} full article is too short")

    def test_generated_selection_is_collection_owned_and_build_time_materialized(self):
        self.assertEqual(self.selection["collection"], "transformation-thread")
        self.assertEqual(len(self.selection["visibleItems"]), 3)
        posts_by_id = {post["id"]: post for post in self.posts}
        for item in self.selection["visibleItems"]:
            item_id = item["id"]
            self.assertIn(f'data-collection-item-id="{item_id}"', self.index)
            self.assertIn(
                f'<template data-collection-article-template data-collection-item-id="{item_id}">',
                self.index,
            )
            article = self.resolve(posts_by_id[item_id]["full_article_md"]).read_text(encoding="utf-8")
            candidate = next(
                line.strip(" >#*-\t")
                for line in article.splitlines()
                if line.strip() and not re.match(r"^\s*(#|>|[-*]\s|\d+\.\s)", line)
            )
            self.assertIn(candidate[:50], self.index_text)

    def test_browser_profile_only_opens_build_rendered_templates(self):
        for token in [
            'data-collection-mode="publication"',
            "data-collection-open-item",
            "data-collection-modal",
            "data-collection-modal-title",
            "data-collection-modal-body",
            "data-collection-modal-close",
            "data-collection-article-template",
        ]:
            self.assertIn(token, self.index)
        for token in [
            "initPublication",
            "findTemplate",
            "copyChildren",
            "template.content",
            "cloneNode(true)",
            "openItem",
        ]:
            self.assertIn(token, self.js)
        for token in ["window.fetch", "loadCollection", "loadText", "renderMarkdown", "item.full_article_md"]:
            self.assertNotIn(token, self.js)

    def test_template_copy_avoids_runtime_html_parsing(self):
        self.assertIn("replaceChildren", self.js)
        self.assertIn("textContent", self.js)
        self.assertNotIn("innerHTML", self.js)

    def test_delivery_assets_load_from_the_spa_entry_point(self):
        self.assertIn("collections/transformation-thread/styles.css", self.index)
        self.assertIn("collections/_system/collection.css", self.index)
        self.assertIn("collections/_system/collection.js", self.index)

    def test_collection_styles_do_not_leak_markdown_rules_into_the_site(self):
        self.assertNotIn("/* Start markdown styles */", self.css)
        forbidden_selectors = [
            "body",
            "h1, h2, h3, h4, h5, h6",
            "h1",
            "h2",
            "h3",
            "h4",
            "p",
            "a",
            "a:hover",
            "ul, ol",
            "li",
            "blockquote",
            "code",
            "pre",
            "pre code",
            "table",
            "th, td",
            "tr:nth-child(even)",
        ]
        for selector in forbidden_selectors:
            with self.subTest(selector=selector):
                self.assertIsNone(
                    re.search(rf"(?m)^{re.escape(selector)}\s*\{{", self.css),
                    f"Unscoped selector leaked from the collection stylesheet: {selector}",
                )
        self.assertIn(".thread-article-modal-body p,", self.css)
        self.assertIn(".thread-article-modal-body a {", self.css)

    def test_article_modal_uses_sitewide_circle_close_standard(self):
        self.assertIn("thread-article-modal-close modal-close-circle", self.index)
        self.assertIn(".thread-article-modal-close", self.modal)
        self.assertIn(".thread-article-modal {", self.css)


if __name__ == "__main__":
    unittest.main()
