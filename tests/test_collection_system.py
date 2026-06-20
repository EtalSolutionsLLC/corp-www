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

COLLECTION_IDS = ["brands", "promotions", "systems-lab", "transformation-thread"]


class CollectionSystemTests(unittest.TestCase):
    def test_only_registered_collections_and_system_live_at_collection_root(self):
        actual = {path.name for path in COLLECTIONS.iterdir() if path.is_dir() and path.name != "__pycache__"}
        self.assertEqual(actual, {"_system", *COLLECTION_IDS})

    def test_every_collection_has_manifest_data_and_style(self):
        for collection_id in COLLECTION_IDS:
            with self.subTest(collection_id=collection_id):
                directory = COLLECTIONS / collection_id
                manifest = json.loads((directory / "collection.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["id"], collection_id)
                self.assertIn(manifest["mode"], {"catalog", "publication", "workspace"})
                self.assertTrue((directory / manifest["dataFile"]).is_file())
                self.assertTrue((directory / manifest["styleFile"]).is_file())
                if manifest.get("scriptFile"):
                    self.assertTrue((directory / manifest["scriptFile"]).is_file())
                self.assertTrue(manifest["regions"])
                self.assertTrue(manifest.get("presentation"))

    def test_catalog_publication_and_workspace_are_profiles_of_one_system(self):
        modes = {
            collection_id: json.loads((COLLECTIONS / collection_id / "collection.json").read_text(encoding="utf-8"))["mode"]
            for collection_id in COLLECTION_IDS
        }
        self.assertEqual(modes, {
            "brands": "catalog",
            "promotions": "catalog",
            "systems-lab": "workspace",
            "transformation-thread": "publication",
        })

        core = (COLLECTIONS / "_system/collection.js").read_text(encoding="utf-8")
        for token in [
            "function registerProfile(mode, profile)",
            "function loadCollectionContext(root)",
            "function initCollection(root)",
            'querySelectorAll("[data-collection]")',
            "initAll(document)",
        ]:
            self.assertIn(token, core)

        for mode in ["catalog", "publication", "workspace"]:
            profile = (COLLECTIONS / f"_system/profiles/{mode}.js").read_text(encoding="utf-8")
            self.assertIn(f'api.registerProfile("{mode}"', profile)

    def test_all_collection_regions_are_rendered_by_executable_hooks(self):
        expected = {
            "COLLECTION-STYLES": "collection-styles",
            "COLLECTION-SCRIPTS": "collection-scripts",
            "COLLECTION-SYSTEMS-LAB": "collection-systems-lab",
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

    def test_shared_system_contracts_and_assets_are_loaded(self):
        for relative_path in [
            "_system/collection.js",
            "_system/collection.css",
            "_system/collection.schema.json",
            "_system/item-base.schema.json",
            "_system/catalog-item.schema.json",
            "_system/publication-item.schema.json",
            "_system/workspace-item.schema.json",
            "_system/render-collection",
        ]:
            self.assertTrue((COLLECTIONS / relative_path).is_file(), relative_path)

        for href in [
            "collections/_system/collection.css",
            "collections/brands/styles.css",
            "collections/promotions/styles.css",
            "collections/systems-lab/styles.css",
            "collections/transformation-thread/styles.css",
            "collections/_system/collection.js",
            "collections/_system/profiles/catalog.js",
            "collections/_system/profiles/publication.js",
            "collections/_system/profiles/workspace.js",
            "collections/systems-lab/workspace.js",
        ]:
            self.assertIn(href, INDEX)

        self.assertLess(
            INDEX.index("collections/_system/collection.css"),
            INDEX.index("collections/systems-lab/styles.css"),
        )
        self.assertLess(
            INDEX.index("collections/_system/collection.js"),
            INDEX.index("collections/_system/profiles/workspace.js"),
        )

    def test_manifest_schema_formally_supports_all_profiles(self):
        schema = json.loads((COLLECTIONS / "_system/collection.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "Portmason Collections Manifest")
        self.assertEqual(schema["properties"]["mode"]["enum"], ["catalog", "publication", "workspace"])
        self.assertIn("workspace", schema["properties"])
        self.assertIn("scriptFile", schema["properties"])
        presentation = schema["properties"]["presentation"]["properties"]
        self.assertIn("platformModel", presentation)
        layer_ids = presentation["platformModel"]["properties"]["layers"]["items"]["properties"]["id"]["enum"]
        self.assertEqual(layer_ids, ["foundations", "operations", "tooling"])

    def test_catalog_section_copy_is_manifest_owned(self):
        brands = json.loads((COLLECTIONS / "brands/collection.json").read_text(encoding="utf-8"))
        promotions = json.loads((COLLECTIONS / "promotions/collection.json").read_text(encoding="utf-8"))
        self.assertEqual(brands["presentation"]["title"], "Focused brands, one strong foundation.")
        self.assertEqual(promotions["presentation"]["title"], "Focused promotions for practical progress.")
        for title in [brands["presentation"]["title"], promotions["presentation"]["title"]]:
            self.assertIn(title, INDEX)

    def test_no_legacy_collection_or_lab_implementation_remains(self):
        forbidden = [
            SITE / "catalogs",
            SITE / "content/transformation-thread",
            SITE / "content/transformation-thread-posts.json",
            SITE / "content/transformation-thread-selection.json",
            SITE / "assets/css/carousel.css",
            SITE / "assets/css/transformation-thread.css",
            SITE / "assets/css/lab.css",
            SITE / "assets/js/catalog-carousel.js",
            SITE / "assets/js/transformation-thread.js",
            SITE / "assets/js/systems-lab.js",
            SITE / "assets/js/site-size-compare.js",
            SITE / "partials/lab.html",
            SITE / "partials/catalog-brands-full-list.html",
            SITE / "partials/catalog-promotions-full-list.html",
            SITE / "partials/catalog-promotions-hero-teaser.html",
            SITE / "partials/transformation-thread.html",
        ]
        for path in forbidden:
            self.assertFalse(path.exists(), path)

    def test_non_collection_contracts_remain_outside_collection_registry(self):
        self.assertTrue((SITE / "api/v1/capabilities.json").is_file())
        self.assertFalse((SITE / "content/explore-decision-tree.json").exists())


if __name__ == "__main__":
    unittest.main()
