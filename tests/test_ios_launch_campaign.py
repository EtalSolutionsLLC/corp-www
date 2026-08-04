#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
PRESS_RELEASE = "/?release=nr-002#newsroom"


class IosLaunchCampaignTests(unittest.TestCase):
    def test_homepage_hero_uses_the_iphone_campaign(self) -> None:
        items = json.loads((SITE / "collections/promotions/items.json").read_text(encoding="utf-8"))
        hero = items[0]["hero"]
        self.assertEqual(hero["label"], "ReviewNudge for iPhone")
        self.assertEqual(hero["action"]["href"], PRESS_RELEASE)

        rendered = subprocess.run(
            [str(SITE / "collections/_system/render-collection"), "promotions", "heroTeaser"],
            cwd=SITE,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertIn("Your review workflow is coming with you.", rendered)
        self.assertIn(f'href="{PRESS_RELEASE}"', rendered)
        self.assertNotIn("data-collection-detail-open", rendered)
        self.assertIn('data-target="2026-08-10T23:59:59-07:00"', rendered)
        self.assertIn("App Store link will appear here as soon as it’s live.", rendered)

    def test_press_release_deep_link_opens_the_release(self) -> None:
        publication = (SITE / "collections/_system/profiles/publication.js").read_text(encoding="utf-8")
        self.assertIn('searchParams.get("release")', publication)
        self.assertIn('requestedRelease.match(/^nr-(\\d+)$/i)', publication)
        self.assertIn('openItem(Number(match[1]))', publication)

    def test_first_visit_power_up_starts_on_august_10_pacific(self) -> None:
        browser = (SITE / "assets/js/visual-polish.js").read_text(encoding="utf-8")
        self.assertIn("function enableIosLaunchCampaign()", browser)
        self.assertIn("2026-08-10T00:00:00-07:00", browser)
        self.assertIn("corp-www-ios-app-store-reveal-2026-08-10", browser)
        self.assertIn('get("app_store_preview") === "powering-up"', browser)
        self.assertIn('setAttribute("data-powering-up", "true")', browser)

    def test_release_has_no_draft_placeholders(self) -> None:
        release = (SITE / "collections/newsroom/items/002/full-article.md").read_text(encoding="utf-8")
        self.assertIn("media@etal.solutions", release)
        self.assertNotIn("[your preferred contact email]", release)
        self.assertNotIn("said a spokesperson", release)


if __name__ == "__main__":
    unittest.main()
