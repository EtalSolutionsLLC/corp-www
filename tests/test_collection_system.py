#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
COLLECTIONS = SITE / "collections"
INDEX = (SITE / "index.html").read_text(encoding="utf-8")


class CollectionSystemTests(unittest.TestCase):
    def test_only_registered_collections_and_system_live_at_collection_root(self):
        actual = {path.name for path in COLLECTIONS.iterdir() if path.is_dir()}
        self.assertEqual(actual, {"_system", "brands", "promotions", "transformation-thread"})

    def test_every_collection_has_one_manifest_data_file_and_style_file(self):
        for collection_id in ["brands", "promotions", "transformation-thread"]:
            with self.subTest(collection_id=collection_id):
                directory = COLLECTIONS / collection_id
                manifest = json.loads((directory / "collection.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["id"], collection_id)
                self.assertIn(manifest["mode"], {"catalog", "publication"})
                self.assertTrue((directory / manifest["dataFile"]).is_file())
                self.assertTrue((directory / manifest["styleFile"]).is_file())
                self.assertTrue(manifest["regions"])
                self.assertTrue(manifest.get("presentation"))

    def test_catalog_and_publication_are_profiles_of_one_system(self):
        modes = {
            collection_id: json.loads((COLLECTIONS / collection_id / "collection.json").read_text(encoding="utf-8"))["mode"]
            for collection_id in ["brands", "promotions", "transformation-thread"]
        }
        self.assertEqual(modes, {
            "brands": "catalog",
            "promotions": "catalog",
            "transformation-thread": "publication",
        })
        controller = (COLLECTIONS / "_system/collection.js").read_text(encoding="utf-8")
        self.assertIn('[data-collection-carousel]', controller)
        self.assertIn('[data-collection][data-collection-mode="publication"]', controller)

    def test_all_collection_regions_are_rendered_by_executable_hooks(self):
        expected = {
            "COLLECTION-STYLES": "collection-styles",
            "COLLECTION-BRANDS": "collection-brands",
            "COLLECTION-PROMOTIONS": "collection-promotions",
            "COLLECTION-PROMOTIONS-HERO-TEASER": "collection-promotions-hero-teaser",
            "COLLECTION-TRANSFORMATION-THREAD": "collection-transformation-thread",
        }
        for marker, hook_name in expected.items():
            with self.subTest(marker=marker):
                self.assertIn(f"<!-- PM:{marker} -->", INDEX)
                hook = SITE / "partials/hooks" / hook_name
                self.assertTrue(hook.is_file())
                self.assertTrue(hook.stat().st_mode & 0o111)
                subprocess.run(["bash", "-n", str(hook)], check=True)

    def test_shared_system_files_are_present_and_collection_assets_load(self):
        for path in [
            COLLECTIONS / "_system/collection.js",
            COLLECTIONS / "_system/collection.css",
            COLLECTIONS / "_system/collection.schema.json",
            COLLECTIONS / "_system/render-collection",
        ]:
            self.assertTrue(path.is_file(), path)
        for href in [
            "collections/_system/collection.css",
            "collections/_system/collection.js",
            "collections/brands/styles.css",
            "collections/promotions/styles.css",
            "collections/transformation-thread/styles.css",
        ]:
            self.assertIn(href, INDEX)
        self.assertLess(
            INDEX.index("collections/_system/collection.css"),
            INDEX.index("collections/brands/styles.css"),
        )
        self.assertIn("<!-- PM:COLLECTION-STYLES -->", INDEX)

    def test_catalog_section_copy_is_manifest_owned(self):
        brands = json.loads((COLLECTIONS / "brands/collection.json").read_text(encoding="utf-8"))
        promotions = json.loads((COLLECTIONS / "promotions/collection.json").read_text(encoding="utf-8"))
        self.assertEqual(brands["presentation"]["title"], "Focused brands, one strong foundation.")
        self.assertEqual(promotions["presentation"]["title"], "Focused promotions for practical progress.")
        for title in [brands["presentation"]["title"], promotions["presentation"]["title"]]:
            self.assertIn(title, INDEX)
        marker_only = INDEX.split("<!-- PM:COLLECTION-BRANDS -->", 1)[0]
        self.assertNotIn(brands["presentation"]["title"], marker_only)

    def test_no_legacy_collection_implementation_remains(self):
        forbidden = [
            SITE / "catalogs",
            SITE / "content/transformation-thread",
            SITE / "content/transformation-thread-posts.json",
            SITE / "content/transformation-thread-selection.json",
            SITE / "assets/css/carousel.css",
            SITE / "assets/css/transformation-thread.css",
            SITE / "assets/js/catalog-carousel.js",
            SITE / "assets/js/transformation-thread.js",
            SITE / "partials/catalog-brands-full-list.html",
            SITE / "partials/catalog-promotions-full-list.html",
            SITE / "partials/catalog-promotions-hero-teaser.html",
            SITE / "partials/transformation-thread.html",
        ]
        for path in forbidden:
            self.assertFalse(path.exists(), path)

    def test_non_collection_content_remains_outside_collection_registry(self):
        self.assertTrue((SITE / "content/explore-decision-tree.json").is_file())
        self.assertEqual(
            {path.name for path in (SITE / "content").iterdir()},
            {"explore-decision-tree.json"},
        )


if __name__ == "__main__":
    unittest.main()
