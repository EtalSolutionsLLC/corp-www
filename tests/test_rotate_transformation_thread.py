from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import shutil
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
        self.manifest = {
            "id": "transformation-thread",
            "mode": "publication",
            "layout": "featured-grid",
            "styleFile": "styles.css",
            "regions": {"section": "COLLECTION-TRANSFORMATION-THREAD"},
            "selection": {
                "strategy": "weekday-week-of-month",
                "visibleItems": 3,
                "timezone": "America/Los_Angeles",
                "outputFile": "generated/selection.json",
            },
        }
        self.collection_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        for item_id in range(1, 10):
            self.write_item(item_id, ((item_id - 1) % 7) + 1)

    def tearDown(self):
        self.temp.cleanup()

    def write_item(
        self,
        item_id: int,
        slot: int,
        title: str | None = None,
        *,
        date_first_displayed: str | None = None,
        display_after: list[str] | None = None,
    ) -> Path:
        folder = self.root / "items" / f"{item_id:03d}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "meta.json").write_text(
            json.dumps({
                "slot": slot,
                "category": "Category",
                "status": "Draft",
                "dateFirstDisplayed": date_first_displayed,
                "displayAfter": display_after or [],
            }),
            encoding="utf-8",
        )
        (folder / "title.md").write_text((title or f"Article {item_id}") + "\n", encoding="utf-8")
        (folder / "excerpt.md").write_text(f"Summary {item_id}\n", encoding="utf-8")
        (folder / "full-article.md").write_text((f"Full article {item_id}. " * 80).strip() + "\n", encoding="utf-8")
        return folder

    def update_meta(self, item_id: int, **changes: object) -> None:
        path = self.root / "items" / f"{item_id:03d}" / "meta.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(changes)
        path.write_text(json.dumps(data), encoding="utf-8")

    def reset_items(self) -> None:
        shutil.rmtree(self.root / "items")

    def context(self):
        return module.collection_context(self.collection_path)

    def selection(self, selected_date: date):
        manifest, _items_root, items, manifest_raw, items_raw = self.context()
        return module.select_items(
            manifest,
            items,
            manifest_raw,
            items_raw,
            selected_date,
            self.collection_path,
        )

    def ids(self, selected_date: date) -> list[int]:
        return [int(item["id"]) for item in self.selection(selected_date).items]

    def test_discovers_build_derived_item_fields_from_directories(self):
        _manifest, items_root, items, _manifest_raw, _items_raw = self.context()
        self.assertEqual(items_root, self.root / "items")
        self.assertEqual([item["id"] for item in items], list(range(1, 10)))
        self.assertEqual(items[0]["slug"], "tt-001")
        self.assertEqual(items[0]["title_md"], "items/001/title.md")
        self.assertEqual(items[0]["excerpt_md"], "items/001/excerpt.md")
        self.assertEqual(items[0]["full_article_md"], "items/001/full-article.md")

    def test_weekday_rotation_and_wrap(self):
        self.assertEqual(self.ids(date(2026, 6, 1)), [1, 8, 2])
        self.assertEqual(self.ids(date(2026, 6, 2)), [2, 9, 3])
        self.assertEqual(self.ids(date(2026, 6, 7)), [7, 1, 8])

    def test_week_of_month_rotates_crowded_slot_batches(self):
        self.reset_items()
        for item_id in range(1, 7):
            self.write_item(item_id, 1, f"Slot1 {item_id}")
        self.write_item(7, 2, "Slot2 7")
        self.assertEqual(self.ids(date(2026, 6, 1)), [1, 2, 3])
        self.assertEqual(self.ids(date(2026, 6, 8)), [4, 5, 6])
        self.assertEqual(self.ids(date(2026, 6, 15)), [1, 2, 3])

    def test_selection_is_markdown_backed_and_safely_hydrated(self):
        (self.root / "items/001/title.md").write_text("**Article** *One*\n", encoding="utf-8")
        item = self.selection(date(2026, 6, 1)).items[0]
        self.assertEqual(item["title"], "Article One")
        self.assertEqual(item["title_html"], "<strong>Article</strong> <em>One</em>")
        self.assertNotIn("full_article", item)

    def test_materialize_writes_selection_and_first_display_history(self):
        output = module.materialize(self.collection_path, None, date(2026, 6, 1))
        self.assertEqual(output, self.root / "generated/selection.json")
        data = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(data["collection"], "transformation-thread")
        self.assertEqual([item["id"] for item in data["visibleItems"]], [1, 8, 2])
        self.assertIn("full_article_md", data["visibleItems"][0])
        self.assertNotIn("full_article", data["visibleItems"][0])
        self.assertEqual(data["visibleItems"][0]["dateFirstDisplayed"], "2026-06-01")
        self.assertEqual(data["visibleItems"][0]["displayAfter"], [])
        self.assertFalse((self.root / "items.json").exists())

        meta = json.loads((self.root / "items/001/meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["dateFirstDisplayed"], "2026-06-01")

        module.materialize(self.collection_path, None, date(2026, 6, 8))
        meta = json.loads((self.root / "items/001/meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["dateFirstDisplayed"], "2026-06-01")

    def test_successor_waits_until_predecessor_was_displayed_in_an_earlier_rotation(self):
        self.reset_items()
        self.write_item(1, 1, "Part 1")
        self.write_item(2, 1, "Part 2", display_after=["001"])
        self.write_item(3, 2, "Independent")

        first = module.materialize(self.collection_path, None, date(2026, 6, 1))
        first_data = json.loads(first.read_text(encoding="utf-8"))
        self.assertEqual([item["id"] for item in first_data["visibleItems"]], [1, 3])
        self.assertNotIn(2, [item["id"] for item in first_data["visibleItems"]])
        self.assertEqual(
            json.loads((self.root / "items/001/meta.json").read_text(encoding="utf-8"))["dateFirstDisplayed"],
            "2026-06-01",
        )
        self.assertIsNone(
            json.loads((self.root / "items/002/meta.json").read_text(encoding="utf-8"))["dateFirstDisplayed"]
        )

        second = module.materialize(self.collection_path, None, date(2026, 6, 8))
        second_data = json.loads(second.read_text(encoding="utf-8"))
        self.assertIn(2, [item["id"] for item in second_data["visibleItems"]])
        self.assertEqual(
            json.loads((self.root / "items/002/meta.json").read_text(encoding="utf-8"))["dateFirstDisplayed"],
            "2026-06-08",
        )

    def test_dependency_validation_rejects_missing_self_and_cycles(self):
        self.update_meta(2, displayAfter=["999"])
        with self.assertRaisesRegex(ValueError, "missing predecessor"):
            self.selection(date(2026, 6, 1))

        self.update_meta(2, displayAfter=["002"])
        with self.assertRaisesRegex(ValueError, "cannot depend on itself"):
            self.selection(date(2026, 6, 1))

        self.update_meta(2, displayAfter=["003"])
        self.update_meta(3, displayAfter=["002"])
        with self.assertRaisesRegex(ValueError, "dependency cycle"):
            self.selection(date(2026, 6, 1))

    def test_date_and_dependency_shapes_are_validated(self):
        self.update_meta(1, dateFirstDisplayed="06/01/2026")
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            self.selection(date(2026, 6, 1))

        self.update_meta(1, dateFirstDisplayed=None, displayAfter=[1])
        with self.assertRaisesRegex(ValueError, "three-digit ids"):
            self.selection(date(2026, 6, 1))

    def test_validation_rejects_missing_markdown_and_embedded_content(self):
        (self.root / "items/001/full-article.md").unlink()
        with self.assertRaises(ValueError):
            self.selection(date(2026, 6, 1))

        self.write_item(1, 1)
        meta_path = self.root / "items/001/meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["body"] = "Embedded content is not allowed"
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.context()

    def test_validation_rejects_noncanonical_directory_and_manifest_registry(self):
        bad = self.root / "items/12"
        bad.mkdir(parents=True)
        (bad / "meta.json").write_text('{"slot": 1, "category": "Bad", "status": "Draft"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.context()
        shutil.rmtree(bad)

        self.manifest["dataFile"] = "items.json"
        self.collection_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.context()

    def test_source_hash_changes_when_metadata_changes(self):
        before = self.selection(date(2026, 6, 1)).source_sha256
        meta_path = self.root / "items/001/meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["category"] = "Updated category"
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        after = self.selection(date(2026, 6, 1)).source_sha256
        self.assertNotEqual(before, after)

    def test_midnight_window_and_force(self):
        tz = ZoneInfo("America/Los_Angeles")
        inside = datetime(2026, 6, 1, 0, 12, tzinfo=tz)
        outside = datetime(2026, 6, 1, 1, 0, tzinfo=tz)
        self.assertTrue(module.should_run(inside, True, False))
        self.assertFalse(module.should_run(outside, True, False))
        self.assertTrue(module.should_run(outside, True, True))


if __name__ == "__main__":
    unittest.main()
