from __future__ import annotations

import importlib.machinery
import importlib.util
import json
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
import sys
sys.modules[loader.name] = module
spec.loader.exec_module(module)


class RotationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = {
            "rotation_epoch": "2026-06-01",
            "rotation_timezone": "America/Los_Angeles",
            "visible_posts": 3,
            "posts": [
                {
                    "title": f"Article {index}",
                    "category": "Category",
                    "status": "Draft",
                    "summary": f"Summary {index}",
                    "url": f"mailto:test@example.com?subject=Article%20{index}",
                }
                for index in range(7)
            ],
        }
        self.raw = json.dumps(self.config).encode("utf-8")

    def test_seven_day_cycle_features_each_article_once(self) -> None:
        titles = []
        for day in range(1, 8):
            selection = module.select_posts(self.config, self.raw, date(2026, 6, day), "America/Los_Angeles")
            titles.append(selection.posts[0]["title"])
        self.assertEqual(titles, [f"Article {index}" for index in range(7)])

    def test_cycle_wraps_supporting_articles(self) -> None:
        selection = module.select_posts(self.config, self.raw, date(2026, 6, 7), "America/Los_Angeles")
        self.assertEqual([post["title"] for post in selection.posts], ["Article 6", "Article 0", "Article 1"])

    def test_midnight_window_accepts_only_first_thirty_minutes(self) -> None:
        tz = ZoneInfo("America/Los_Angeles")
        self.assertTrue(module.in_midnight_window(datetime(2026, 6, 1, 0, 5, tzinfo=tz)))
        self.assertFalse(module.in_midnight_window(datetime(2026, 6, 1, 0, 30, tzinfo=tz)))
        self.assertFalse(module.in_midnight_window(datetime(2026, 6, 1, 23, 59, tzinfo=tz)))

    def test_force_bypasses_midnight_window_guard(self) -> None:
        tz = ZoneInfo("America/Los_Angeles")
        midday = datetime(2026, 6, 1, 12, 0, tzinfo=tz)
        self.assertFalse(module.should_run(midday, require_local_midnight_window=True, force=False))
        self.assertTrue(module.should_run(midday, require_local_midnight_window=True, force=True))
        self.assertTrue(module.should_run(midday, require_local_midnight_window=False, force=False))

    def test_initial_html_without_markers_is_wrapped(self) -> None:
        html = '''<main>\n        <div class="thread-post-layout" aria-label="Transformation Thread article list">\n          <article></article>\n          <div><div></div></div>\n        </div>\n</main>'''
        selection = module.select_posts(self.config, self.raw, date(2026, 6, 1), "America/Los_Angeles")
        updated = module.update_html(html, module.render_layout(selection))
        self.assertEqual(updated.count(module.START_MARKER), 1)
        self.assertEqual(updated.count(module.END_MARKER), 1)
        self.assertIn("Article 0", updated)

    def test_marked_html_updates_idempotently(self) -> None:
        html = '''<main>\n        <div class="thread-post-layout" aria-label="Transformation Thread article list">\n          <article></article>\n        </div>\n</main>'''
        selection = module.select_posts(self.config, self.raw, date(2026, 6, 1), "America/Los_Angeles")
        once = module.update_html(html, module.render_layout(selection))
        twice = module.update_html(once, module.render_layout(selection))
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
