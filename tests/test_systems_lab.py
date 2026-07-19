#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
COLLECTION = SITE / "collections/systems-lab"
INDEX = (SITE / "index.html").read_text(encoding="utf-8")
MANIFEST = json.loads((COLLECTION / "collection.json").read_text(encoding="utf-8"))
ITEMS = json.loads((COLLECTION / "items.json").read_text(encoding="utf-8"))
PROFILE_JS = (SITE / "collections/_system/profiles/workspace.js").read_text(encoding="utf-8")
INSTANCE_JS = (COLLECTION / "workspace.js").read_text(encoding="utf-8")
CSS = (COLLECTION / "styles.css").read_text(encoding="utf-8")


class SystemsLabTests(unittest.TestCase):
    def test_portmason_replaces_explore_in_navigation_and_spa(self):
        self.assertIn('href="/#lab">Portmason</a>', INDEX)
        self.assertIn('id="lab"', INDEX)
        self.assertNotIn('href="/#explore"', INDEX)
        self.assertNotIn('id="explore"', INDEX)
        self.assertNotIn('data-explore-root', INDEX)

    def test_lab_is_a_rendered_portmason_collections_workspace(self):
        self.assertIn('<!-- PM:COLLECTION-SYSTEMS-LAB -->', INDEX)
        self.assertIn('<!-- /PM:COLLECTION-SYSTEMS-LAB -->', INDEX)
        tag = '<section class="portmason-workspace panel pm-viewport-target pm-scroll-target collection collection--workspace"'
        self.assertIn(tag, INDEX)
        for token in [
            'data-pm-viewport-align="start"',
            'data-collection-id="systems-lab"',
            'data-collection-mode="workspace"',
            'data-collection-config="/collections/systems-lab/collection.json"',
            'data-workspace-query-parameter="lab"',
        ]:
            self.assertIn(token, INDEX)

    def test_workspace_manifest_and_four_tools_are_data_driven(self):
        self.assertEqual(MANIFEST["mode"], "workspace")
        self.assertEqual(MANIFEST["layout"], "tile-gallery")
        self.assertEqual(MANIFEST["scriptFile"], "workspace.js")
        self.assertEqual(MANIFEST["workspace"]["activation"], "modal")
        self.assertEqual(MANIFEST["workspace"]["initialization"], "on-open")
        model = MANIFEST["presentation"]["platformModel"]
        self.assertEqual(
            [layer["id"] for layer in model["layers"]],
            ["foundations", "operations", "tooling"],
        )
        foundations = model["layers"][0]
        self.assertEqual(foundations["includes"], ["Portmason Collections™"])
        self.assertIn("Foundations define the system", model["relationship"])
        self.assertEqual(len(ITEMS), 4)
        self.assertEqual(
            [item["slug"] for item in ITEMS],
            ["external-signal", "published-interface", "local-capability-match", "page-weight-evidence"],
        )
        for item in ITEMS:
            with self.subTest(item=item["slug"]):
                self.assertTrue((COLLECTION / item["panelFile"]).is_file())
                self.assertTrue(item["demonstrates"])
                self.assertTrue(item["proof"])
                self.assertNotIn("platformFamily", item)
                self.assertIn(f'data-workspace-open="{item["slug"]}"', INDEX)
                self.assertIn(f'data-workspace-panel="{item["slug"]}"', INDEX)

    def test_gallery_uses_one_shared_accessible_workspace_modal(self):
        self.assertEqual(INDEX.count('data-workspace-modal aria-labelledby="systems-lab-workspace-title"'), 1)
        self.assertEqual(INDEX.count('class="workspace-tile"'), 4)
        for token in [
            'data-workspace-close',
            'data-workspace-title',
            'data-workspace-summary',
            'data-workspace-demonstrates',
            'data-workspace-proof',
            'data-workspace-instructions',
            'data-workspace-inputs',
            'data-workspace-outputs',
        ]:
            self.assertIn(token, INDEX)
        for token in [
            'modal.addEventListener("cancel"',
            'modal.addEventListener("keydown"',
            'event.key !== "Tab"',
            'event.target === modal',
            'opener.focus({ preventScroll: true })',
            '!element.closest("[hidden]")',
        ]:
            self.assertIn(token, PROFILE_JS)

    def test_page_weight_tool_reports_pagespeed_visual_load_duration(self):
        panel = (COLLECTION / "tools/page-weight-evidence.html").read_text(encoding="utf-8")
        page_weight = next(item for item in ITEMS if item["slug"] == "page-weight-evidence")

        self.assertIn("page-weight and visual-load", panel)
        self.assertIn("Visual load", panel)
        self.assertIn("Lighthouse Speed Index", panel)
        for token in [
            "data-site-speed-theirs",
            "data-site-speed-ours",
            "data-site-speed-summary",
        ]:
            self.assertIn(token, panel)
        self.assertIn("PageSpeed visual-load duration", page_weight["outputs"])
        self.assertIn('extractAuditValue(payload, "speed-index"', INSTANCE_JS)
        self.assertIn("speedIndexMilliseconds", INSTANCE_JS)
        self.assertIn("formatSeconds", INSTANCE_JS)
        self.assertIn("describeVisualLoad", INSTANCE_JS)
        self.assertNotIn("data-performance-duration", panel)

    def test_platform_explanation_follows_the_approved_vertical_mockup(self):
        for token in [
            "@media (min-width: 1061px)",
            '"intro"',
            '"platform"',
            '"gallery-heading"',
            '"gallery"',
            "grid-template-columns: repeat(12, minmax(0, 1fr));",
            "grid-template-columns: minmax(0, 1fr);",
            "grid-template-columns: repeat(4, minmax(0, 1fr));",
            "max-width: 1280px;",
            "font-size: clamp(3.72rem, 5.25vw, 5.15rem);",
        ]:
            self.assertIn(token, CSS)
        self.assertNotIn('"intro gallery-heading"', CSS)
        self.assertNotIn('"platform gallery"', CSS)

    def test_each_platform_plane_uses_the_same_dedicated_label_column(self):
        for token in [
            ".portmason-platform-layer > .portmason-platform-role",
            "grid-template-columns: minmax(96px, auto) minmax(0, 1fr);",
            "grid-row: 1 / -1;",
            ".portmason-platform-layer h3,",
            ".portmason-platform-includes {",
        ]:
            self.assertIn(token, CSS)
        self.assertNotIn(
            ".portmason-platform-layer--tooling .portmason-platform-role",
            CSS,
        )

    def test_tools_initialize_through_one_instance_adapter_on_open(self):
        self.assertIn('api.registerProfile("workspace"', PROFILE_JS)
        self.assertIn('api.registerInstance("systems-lab"', INSTANCE_JS)
        self.assertIn('activate: function (slug, panel)', INSTANCE_JS)
        self.assertIn('initializedTools: Object.create(null)', INSTANCE_JS)
        self.assertIn('if (state.initializedTools[slug]) return;', INSTANCE_JS)
        for function_name in [
            "wireExternalSignal",
            "wirePublishedInterface",
            "wireLocalModel",
            "initPageSizeComparison",
        ]:
            self.assertIn(function_name, INSTANCE_JS)

    def test_public_api_contracts_are_valid_json(self):
        for rel in ["api/openapi.json", "api/v1/health.json", "api/v1/capabilities.json", "api/endpoints.json"]:
            payload = json.loads((SITE / rel).read_text(encoding="utf-8"))
            self.assertIsInstance(payload, dict)
        openapi = json.loads((SITE / "api/openapi.json").read_text(encoding="utf-8"))
        self.assertEqual(openapi["openapi"], "3.1.0")

    def test_api_endpoint_selector_is_json_configured(self):
        payload = json.loads((SITE / "api/endpoints.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["schemaVersion"], 1)
        self.assertEqual(len(payload["endpoints"]), 6)
        self.assertTrue(all({"label", "route", "fallback"} <= set(item) for item in payload["endpoints"]))
        routes = {item["route"] for item in payload["endpoints"]}
        self.assertIn("/v1/site-deployment", routes)
        self.assertIn("/v1/site-artifact", routes)
        panel = (COLLECTION / "tools/published-interface.html").read_text(encoding="utf-8")
        self.assertIn('/api/endpoints.json', panel)
        self.assertIn('endpointConfigUrl: "api/endpoints.json"', INSTANCE_JS)
        self.assertIn("Loading endpoint contract", panel)
        self.assertNotIn('<option value="/v1/health"', panel)
        self.assertIn("loadEndpointConfig", INSTANCE_JS)
        self.assertIn('document.createElement("option")', INSTANCE_JS)

    def test_local_model_is_explicit_and_browser_local(self):
        panel = (COLLECTION / "tools/local-capability-match.html").read_text(encoding="utf-8")
        self.assertIn("@huggingface/transformers@3.8.1/+esm", INSTANCE_JS)
        self.assertIn('pipeline("feature-extraction"', INSTANCE_JS)
        self.assertIn("Xenova/all-MiniLM-L6-v2", INSTANCE_JS)
        self.assertIn("Text stays local", panel)
        self.assertIn('pooling: "mean"', INSTANCE_JS)
        self.assertIn("normalize: true", INSTANCE_JS)

    def test_portmason_platform_relationship_is_explicit(self):
        for mark in [
            "Portmason Platform™",
            "Portmason Operations™",
            "Portmason Foundations™",
            "Portmason Collections™",
            "Portmason Tooling™",
        ]:
            self.assertIn(mark, INDEX)
        for token in [
            'class="portmason-platform-map"',
            "Foundations define the system",
            "Portmason Collections™</strong>",
            "Build plane",
            "Run plane",
            "Control plane",
            "Each tool demonstrates more than one Portmason capability",
            "Demonstrates",
        ]:
            self.assertIn(token, INDEX)
        self.assertNotIn("portmason-family-strip", INDEX)
        self.assertNotIn("workspace-tile-family", INDEX)
        self.assertNotIn("data-workspace-family", INDEX)
        self.assertIn("platformLayerNames", PROFILE_JS)
        self.assertIn('item.demonstrates || []', PROFILE_JS)
        self.assertIn("Portmason Collections™: workspace profile", PROFILE_JS)
        self.assertNotIn("systems-lab", PROFILE_JS.lower())

    def test_workspace_assets_are_loaded_and_legacy_lab_assets_are_gone(self):
        self.assertIn("collections/systems-lab/styles.css", INDEX)
        self.assertIn("collections/systems-lab/workspace.js", INDEX)
        self.assertNotIn("assets/css/lab.css", INDEX)
        self.assertNotIn("assets/js/systems-lab.js", INDEX)
        self.assertIn(".portmason-platform-map", CSS)
        self.assertIn(".portmason-platform-layer--tooling", CSS)
        self.assertIn(".workspace-tile-demonstrates", CSS)
        self.assertIn(".workspace-gallery", CSS)
        self.assertIn(".workspace-modal-layout", CSS)
        self.assertIn("grid-template-columns: minmax(0, 7fr) minmax(270px, 3fr);", CSS)

    def test_tools_are_examples_not_product_family_definitions(self):
        for item in ITEMS:
            panel = (COLLECTION / item["panelFile"]).read_text(encoding="utf-8")
            self.assertIn("Live systems lab ·", panel)
            self.assertNotIn("Portmason Operations™ ·", panel)
            self.assertNotIn("Portmason Foundations™ ·", panel)
            self.assertNotIn("Portmason Collections™ ·", panel)
            self.assertNotIn("Portmason Tooling™ ·", panel)

    def test_edge_adapter_and_containerized_commands_exist(self):
        worker = ROOT / "edge/capability-api/src/index.js"
        self.assertTrue(worker.is_file())
        self.assertIn("/v1/dependency-status", worker.read_text(encoding="utf-8"))
        for rel in ["edge/capability-api/bin/test", "edge/capability-api/bin/deploy"]:
            path = ROOT / rel
            self.assertTrue(path.stat().st_mode & 0o111)
            subprocess.run(["sh", "-n", str(path)], check=True)


if __name__ == "__main__":
    unittest.main()
