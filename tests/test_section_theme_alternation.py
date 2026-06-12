#!/usr/bin/env python3
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / 'index.html').read_text(encoding='utf-8')
BLOG_PARTIAL = (ROOT / 'partials/transformation-thread.html').read_text(encoding='utf-8')
CSS = (ROOT / 'assets/css/styles.css').read_text(encoding='utf-8')
THEME_CSS = (ROOT / 'assets/css/theme-rhythm.css').read_text(encoding='utf-8')


class SectionThemeAlternationTests(unittest.TestCase):
    def section_tag(self, section_id: str) -> str:
        match = re.search(rf'<section[^>]+id="{re.escape(section_id)}"[^>]*>', INDEX)
        self.assertIsNotNone(match, f'Missing section #{section_id}')
        return match.group(0)

    def test_menu_aligned_sections_alternate_dark_and_light(self):
        expected = [
            ('home', 'dark'),
            ('services', 'light'),
            ('explore', 'dark'),
            ('brands', 'light'),
            ('promotions', 'dark'),
            ('blog', 'light'),
            ('about', 'dark'),
            ('contact', 'light'),
        ]
        for section_id, theme in expected:
            with self.subTest(section_id=section_id):
                self.assertIn(f'data-theme="{theme}"', self.section_tag(section_id))

    def test_services_and_contact_classes_match_theme(self):
        self.assertIn('class="section-light panel" id="services" data-theme="light"', INDEX)
        self.assertIn('class="section-light panel" id="contact" data-theme="light"', INDEX)

    def test_blog_partial_declares_light_theme(self):
        self.assertIn('class="thread-blog panel" id="blog" data-theme="light"', BLOG_PARTIAL)

    def test_light_services_have_readable_overrides(self):
        self.assertIn('.section-light .service-line span,', CSS)
        self.assertIn('.section-light .step {', CSS)
        self.assertIn('.section-light .step p {', CSS)

    def test_menu_aligned_root_bands_are_explicit(self):
        self.assertIn('--corp-light-band: #f7f7fa;', THEME_CSS)
        self.assertIn('#services[data-theme="light"],', THEME_CSS)
        self.assertIn('#brands[data-theme="light"],', THEME_CSS)
        self.assertIn('#blog[data-theme="light"],', THEME_CSS)
        self.assertIn('#contact[data-theme="light"] {', THEME_CSS)
        self.assertIn('#home[data-theme="dark"],', THEME_CSS)
        self.assertIn('#explore[data-theme="dark"],', THEME_CSS)
        self.assertIn('#promotions[data-theme="dark"],', THEME_CSS)
        self.assertIn('#about[data-theme="dark"] {', THEME_CSS)

    def test_theme_rhythm_layer_loads_after_generated_catalog_styles(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn('assets/css/theme-rhythm.css', html)
        self.assertGreater(html.index('assets/css/theme-rhythm.css'), html.index('catalogs/brands/brands.css'))
        self.assertGreater(html.index('assets/css/theme-rhythm.css'), html.index('assets/css/carousel.css'))

    def test_brands_visible_band_is_durably_light(self):
        self.assertIn('/* Durable visible Brands correction', THEME_CSS)
        self.assertIn('html body #brands.brand-catalog-section.catalog-home-section.section-light[data-theme="light"] {', THEME_CSS)
        self.assertIn('linear-gradient(180deg, #f8f9fc 0%, #f2f5fb 100%) !important;', THEME_CSS)
        self.assertIn('border-top-color: #123bff !important;', THEME_CSS)
        self.assertIn('color: #091427 !important;', THEME_CSS)

    def test_blog_identity_is_theme_neutral_orange_thread_rail(self):
        self.assertIn('/* The Transformation Thread identity is a single orange editorial rail.', CSS)
        self.assertIn('.thread-blog[data-theme="light"] {', CSS)
        self.assertIn('.thread-blog[data-theme="dark"] {', CSS)
        self.assertIn('.thread-blog-masthead::before {', CSS)
        self.assertIn('.thread-blog-masthead::after {', CSS)
        self.assertIn('background: radial-gradient(circle, var(--thread-accent)', CSS)
        self.assertIn('border-left: 0;', CSS)
        self.assertIn('background: transparent;', CSS)

    def test_blog_light_theme_does_not_use_grey_masthead_surface(self):
        override = CSS[CSS.index('/* Menu-aligned band contract and Transformation Thread editorial rail */'):]
        self.assertIn('.thread-blog[data-theme="light"] .thread-blog-masthead,', override)
        self.assertIn('background: transparent;', override)
        self.assertIn('--thread-surface: rgba(255, 255, 255, 0.92);', override)


if __name__ == '__main__':
    unittest.main()
