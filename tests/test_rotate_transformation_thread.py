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
        self.collection_path = self.root / "collection.json"
        self.items_path = self.root / "items.json"
        self.manifest = {
            "id": "transformation-thread",
            "mode": "publication",
            "layout": "featured-grid",
            "dataFile": "items.json",
            "styleFile": "styles.css",
            "regions": {"section": "COLLECTION-TRANSFORMATION-THREAD"},
            "selection": {
                "strategy": "weekday-week-of-month",
                "visibleItems": 3,
                "timezone": "America/Los_Angeles",
                "outputFile": "generated/selection.json",
            },
        }
        self.items = [self.make_item(i, ((i - 1) % 7) + 1) for i in range(1, 10)]
        self.write_collection()

    def tearDown(self):
        self.temp.cleanup()

    def make_item(self, item_id: int, slot: int, title: str | None = None) -> dict[str, object]:
        folder = self.root / "items" / f"{item_id:03d}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "title.md").write_text((title or f"Article {item_id}") + "\n", encoding="utf-8")
        (folder / "excerpt.md").write_text(f"Summary {item_id}\n", encoding="utf-8")
        (folder / "full-article.md").write_text((f"Full article {item_id}. " * 80).strip() + "\n", encoding="utf-8")
        return {
            "id": item_id,
            "slug": f"tt-{item_id:03d}",
            "slot": slot,
            "category": "Category",
            "status": "Draft",
            "title_md": f"items/{item_id:03d}/title.md",
            "excerpt_md": f"items/{item_id:03d}/excerpt.md",
            "full_article_md": f"items/{item_id:03d}/full-article.md",
        }

    def write_collection(self):
        self.manifest_raw = json.dumps(self.manifest).encode("utf-8")
        self.items_raw = json.dumps(self.items).encode("utf-8")
        self.collection_path.write_bytes(self.manifest_raw)
        self.items_path.write_bytes(self.items_raw)

    def selection(self, selected_date: date):
        return module.select_items(
            self.manifest,
            self.items,
            self.manifest_raw,
            self.items_raw,
            selected_date,
            self.collection_path,
        )

    def ids(self, selected_date: date) -> list[int]:
        return [int(item["id"]) for item in self.selection(selected_date).items]

    def test_weekday_rotation_and_wrap(self):
        self.assertEqual(self.ids(date(2026, 6, 1)), [1, 8, 2])
        self.assertEqual(self.ids(date(2026, 6, 2)), [2, 9, 3])
        self.assertEqual(self.ids(date(2026, 6, 7)), [7, 1, 8])

    def test_week_of_month_rotates_crowded_slot_batches(self):
        self.items = [self.make_item(i, 1, f"Slot1 {i}") for i in range(1, 7)]
        self.items.append(self.make_item(7, 2, "Slot2 7"))
        self.write_collection()
        self.assertEqual(self.ids(date(2026, 6, 1)), [1, 2, 3])
        self.assertEqual(self.ids(date(2026, 6, 8)), [4, 5, 6])
        self.assertEqual(self.ids(date(2026, 6, 15)), [1, 2, 3])

    def test_selection_is_markdown_backed_and_safely_hydrated(self):
        (self.root / "items/001/title.md").write_text("**Article** *One*\n", encoding="utf-8")
        self.write_collection()
        item = self.selection(date(2026, 6, 1)).items[0]
        self.assertEqual(item["title"], "Article One")
        self.assertEqual(item["title_html"], "<strong>Article</strong> <em>One</em>")
        self.assertNotIn("full_article", item)

    def test_materialize_writes_generated_selection_only(self):
        output = module.materialize(self.collection_path, None, date(2026, 6, 1))
        self.assertEqual(output, self.root / "generated/selection.json")
        data = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(data["collection"], "transformation-thread")
        self.assertEqual([item["id"] for item in data["visibleItems"]], [1, 8, 2])
        self.assertIn("full_article_md", data["visibleItems"][0])
        self.assertNotIn("full_article", data["visibleItems"][0])

    def test_validation_rejects_duplicate_ids_missing_markdown_and_embedded_content(self):
        self.items[1]["id"] = 1
        self.write_collection()
        with self.assertRaises(ValueError):
            self.selection(date(2026, 6, 1))

        self.items = [self.make_item(i, ((i - 1) % 7) + 1) for i in range(1, 10)]
        (self.root / self.items[0]["full_article_md"]).unlink()
        self.write_collection()
        with self.assertRaises(ValueError):
            self.selection(date(2026, 6, 1))

        self.items[0]["body"] = "Embedded content is not allowed"
        self.write_collection()
        with self.assertRaises(ValueError):
            self.selection(date(2026, 6, 1))

    def test_validation_rejects_slug_or_path_escape(self):
        self.items[0]["slug"] = "wrong"
        self.write_collection()
        with self.assertRaises(ValueError):
            self.selection(date(2026, 6, 1))

        self.items[0]["slug"] = "tt-001"
        self.items[0]["title_md"] = "../escape.md"
        self.write_collection()
        with self.assertRaises(ValueError):
            self.selection(date(2026, 6, 1))

    def test_midnight_window_and_force(self):
        tz = ZoneInfo("America/Los_Angeles")
        inside = datetime(2026, 6, 1, 0, 12, tzinfo=tz)
        outside = datetime(2026, 6, 1, 1, 0, tzinfo=tz)
        self.assertTrue(module.should_run(inside, True, False))
        self.assertFalse(module.should_run(outside, True, False))
        self.assertTrue(module.should_run(outside, True, True))


if __name__ == "__main__":
    unittest.main()
