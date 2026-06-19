from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SCRIPT = Path(__file__).resolve().parents[1] / "bin" / "rotate-transformation-thread"
loader = importlib.machinery.SourceFileLoader("rotate_transformation_thread", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[loader.name] = module
spec.loader.exec_module(module)

class RotationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config_path = self.root / "posts.json"
        self.config = {
            "rotation_timezone": "America/Los_Angeles",
            "visible_posts": 3,
            "posts": [self.make_post(i, ((i - 1) % 7) + 1, title=f"Article {i}") for i in range(1, 10)],
        }
        self.write_config()

    def tearDown(self):
        self.temp.cleanup()

    def make_post(self, post_id: int, slot: int, title: str | None = None) -> dict[str, object]:
        folder = self.root / "posts" / f"{post_id:03d}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "title.md").write_text((title or f"Article {post_id}") + "\n", encoding="utf-8")
        (folder / "excerpt.md").write_text(f"Summary {post_id}\n", encoding="utf-8")
        (folder / "full-article.md").write_text((f"Full article {post_id}. " * 80).strip() + "\n", encoding="utf-8")
        return {
            "id": post_id,
            "slot": slot,
            "category": "Category",
            "status": "Draft",
            "title_md": f"posts/{post_id:03d}/title.md",
            "excerpt_md": f"posts/{post_id:03d}/excerpt.md",
            "full_article_md": f"posts/{post_id:03d}/full-article.md",
        }

    def write_config(self):
        self.raw = json.dumps(self.config).encode("utf-8")
        self.config_path.write_bytes(self.raw)

    def titles(self, selected_date: date) -> list[str]:
        selection = module.select_posts(self.config, self.raw, selected_date, "America/Los_Angeles", self.config_path)
        return [post["title"] for post in selection.posts]

    def test_monday_uses_slot_one_first_and_fills_from_next_day(self):
        self.assertEqual(self.titles(date(2026, 6, 1)), ["Article 1", "Article 8", "Article 2"])

    def test_tuesday_uses_slot_two_first_and_fills_from_next_day(self):
        self.assertEqual(self.titles(date(2026, 6, 2)), ["Article 2", "Article 9", "Article 3"])

    def test_sunday_wraps_after_slot_seven(self):
        self.assertEqual(self.titles(date(2026, 6, 7)), ["Article 7", "Article 1", "Article 8"])

    def test_week_of_month_rotates_groups_of_three_within_crowded_slot(self):
        self.config["posts"] = [self.make_post(i, 1, title=f"Slot1 {i}") for i in range(1, 7)]
        self.config["posts"].append(self.make_post(7, 2, title="Slot2 7"))
        self.write_config()
        first = module.select_posts(self.config, self.raw, date(2026, 6, 1), "America/Los_Angeles", self.config_path)
        second = module.select_posts(self.config, self.raw, date(2026, 6, 8), "America/Los_Angeles", self.config_path)
        self.assertEqual([post["id"] for post in first.posts], [1,2,3])
        self.assertEqual([post["id"] for post in second.posts], [4,5,6])

    def test_week_groups_wrap_after_available_batches(self):
        self.config["posts"] = [self.make_post(i, 1, title=str(i)) for i in range(1, 5)]
        self.config["posts"].extend([self.make_post(5, 2, title="5"), self.make_post(6, 3, title="6")])
        self.write_config()
        selection = module.select_posts(self.config, self.raw, date(2026, 6, 15), "America/Los_Angeles", self.config_path)
        self.assertEqual([post["id"] for post in selection.posts], [1,2,3])

    def test_render_preserves_featured_over_two_supporting_cards(self):
        selection = module.select_posts(self.config, self.raw, date(2026, 6, 1), "America/Los_Angeles", self.config_path)
        rendered = module.render_layout(selection)
        self.assertEqual(rendered.count('class="thread-featured-post"'), 1)
        self.assertEqual(rendered.count('class="thread-post-card"'), 2)
        self.assertIn('data-thread-request-post-id="1"', rendered)

    def test_absolute_content_refs_are_rooted_at_the_supplied_site_config(self):
        site_root = self.root / "site"
        content_root = site_root / "content"
        config_path = content_root / "transformation-thread-posts.json"
        posts = []

        for post_id in range(1, 10):
            post_root = content_root / "posts" / f"{post_id:03d}"
            post_root.mkdir(parents=True, exist_ok=True)
            (post_root / "title.md").write_text(f"Article {post_id}\n", encoding="utf-8")
            (post_root / "excerpt.md").write_text(f"Summary {post_id}\n", encoding="utf-8")
            (post_root / "full-article.md").write_text(
                (f"Full article {post_id}. " * 80).strip() + "\n", encoding="utf-8"
            )
            posts.append({
                "id": post_id,
                "slot": ((post_id - 1) % 7) + 1,
                "category": "Category",
                "status": "Draft",
                "title_md": f"/content/posts/{post_id:03d}/title.md",
                "excerpt_md": f"/content/posts/{post_id:03d}/excerpt.md",
                "full_article_md": f"/content/posts/{post_id:03d}/full-article.md",
            })

        config = {
            "rotation_timezone": "America/Los_Angeles",
            "visible_posts": 3,
            "posts": posts,
        }
        raw = json.dumps(config).encode("utf-8")
        config_path.write_bytes(raw)

        selection = module.select_posts(
            config, raw, date(2026, 6, 1), "America/Los_Angeles", config_path
        )
        self.assertEqual([post["id"] for post in selection.posts], [1, 8, 2])

    def test_validation_rejects_duplicate_ids(self):
        self.config["posts"][1]["id"] = 1
        self.write_config()
        with self.assertRaises(ValueError):
            module.select_posts(self.config, self.raw, date(2026, 6, 1), "America/Los_Angeles", self.config_path)

    def test_validation_rejects_missing_full_article_markdown(self):
        missing = self.root / self.config["posts"][0]["full_article_md"]
        missing.unlink()
        self.write_config()
        with self.assertRaises(ValueError):
            module.select_posts(self.config, self.raw, date(2026, 6, 1), "America/Los_Angeles", self.config_path)

    def test_validation_rejects_embedded_display_content(self):
        self.config["posts"][0]["body"] = "Embedded content is retired"
        self.write_config()
        with self.assertRaises(ValueError):
            module.select_posts(self.config, self.raw, date(2026, 6, 1), "America/Los_Angeles", self.config_path)

    def test_selection_json_excludes_full_article_content_but_keeps_reference(self):
        selection = self.root / "selection.json"
        partial = self.root / "partial.html"
        partial.write_text('<main><div class="thread-post-layout"><article></article></div></main>', encoding="utf-8")
        module.materialize(self.config_path, selection, partial, date(2026, 6, 1), "America/Los_Angeles")
        payload = json.loads(selection.read_text(encoding="utf-8"))
        visible = payload["visible_posts"][0]
        self.assertNotIn("body", visible)
        self.assertIn("full_article_md", visible)
        self.assertEqual(payload["active_slot"], 1)

    def test_card_renderer_supports_safe_inline_markdown(self):
        first = self.config["posts"][0]
        (self.root / first["title_md"]).write_text("A **useful** title\n", encoding="utf-8")
        self.write_config()
        selection = module.select_posts(self.config, self.raw, date(2026, 6, 1), "America/Los_Angeles", self.config_path)
        rendered = module.render_layout(selection)
        self.assertIn("<strong>useful</strong>", rendered)

    def test_midnight_window_accepts_only_first_thirty_minutes(self):
        tz = ZoneInfo("America/Los_Angeles")
        self.assertTrue(module.in_midnight_window(datetime(2026, 6, 1, 0, 5, tzinfo=tz)))
        self.assertFalse(module.in_midnight_window(datetime(2026, 6, 1, 0, 30, tzinfo=tz)))

    def test_force_bypasses_midnight_window_guard(self):
        tz = ZoneInfo("America/Los_Angeles")
        midday = datetime(2026, 6, 1, 12, 0, tzinfo=tz)
        self.assertTrue(module.should_run(midday, True, True))
        self.assertFalse(module.should_run(midday, True, False))

    def test_marked_html_updates_idempotently(self):
        html_text = '<main><div class="thread-post-layout"><article></article></div></main>'
        selection = module.select_posts(self.config, self.raw, date(2026, 6, 1), "America/Los_Angeles", self.config_path)
        once = module.update_html(html_text, module.render_layout(selection))
        self.assertEqual(once, module.update_html(once, module.render_layout(selection)))

if __name__ == "__main__":
    unittest.main()
