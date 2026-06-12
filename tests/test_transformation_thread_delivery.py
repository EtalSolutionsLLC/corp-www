#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class TransformationThreadDeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.posts = json.loads((ROOT / "content/transformation-thread-posts.json").read_text(encoding="utf-8"))["posts"]
        cls.partial = (ROOT / "partials/transformation-thread.html").read_text(encoding="utf-8")
        cls.index = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.footer = (ROOT / "partials/footer.html").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets/js/transformation-thread.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets/css/transformation-thread.css").read_text(encoding="utf-8")
        cls.modal = (ROOT / "assets/css/modal-close-system.css").read_text(encoding="utf-8")

    def resolve(self, ref: str) -> Path:
        return ROOT / ref.lstrip("/")

    def test_every_post_has_permanent_id_repeating_slot_and_markdown_refs(self):
        self.assertEqual([post["id"] for post in self.posts], list(range(1, len(self.posts) + 1)))
        self.assertEqual([post["slot"] for post in self.posts], [1,2,3,4,5,6,7,1,2])
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

    def test_full_articles_do_not_render_into_blog_cards(self):
        for post in self.posts:
            article = self.resolve(post["full_article_md"]).read_text(encoding="utf-8").strip()
            self.assertNotIn(article, self.partial)
            self.assertNotIn(article, self.index)

    def test_rendered_cards_have_definitive_request_ids(self):
        self.assertIn("data-thread-request-post-id=", self.partial)
        self.assertIn("data-thread-post-id=", self.partial)
        self.assertIn("data-thread-slot=", self.partial)

    def test_request_action_fetches_full_article_markdown_only_on_request(self):
        for token in ["data-thread-blog", "data-thread-article-modal", "data-thread-article-title", "data-thread-article-body", "data-thread-article-close"]:
            self.assertIn(token, self.partial)
        for token in ["data-thread-request-post-id", "loadPosts", "loadText", "post.title_md", "post.full_article_md", "renderMarkdown", "showModal"]:
            self.assertIn(token, self.js)
        self.assertNotIn("post.body", self.js)

    def test_markdown_renderer_disables_raw_html_by_using_dom_text_nodes(self):
        self.assertIn("document.createTextNode", self.js)
        self.assertIn("textContent", self.js)
        self.assertNotIn("innerHTML", self.js)

    def test_delivery_assets_load_from_footer(self):
        self.assertIn("/assets/css/transformation-thread.css", self.footer)
        self.assertIn("/assets/js/transformation-thread.js", self.footer)
        self.assertIn("/assets/css/transformation-thread.css", self.index)
        self.assertIn("/assets/js/transformation-thread.js", self.index)

    def test_article_modal_uses_sitewide_circle_close_standard(self):
        self.assertIn("thread-article-modal-close modal-close-circle", self.partial)
        self.assertIn(".thread-article-modal-close", self.modal)
        self.assertIn(".thread-article-modal {", self.css)

if __name__ == "__main__":
    unittest.main()
