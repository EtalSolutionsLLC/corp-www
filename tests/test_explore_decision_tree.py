#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")
EXPLORE_CSS = (ROOT / "assets/css/explore.css").read_text(encoding="utf-8")
ACTION_CSS = (ROOT / "assets/css/action-system.css").read_text(encoding="utf-8")
JS = (ROOT / "assets/js/explore-decision-tree.js").read_text(encoding="utf-8")
COMPARE_JS = (ROOT / "assets/js/site-size-compare.js").read_text(encoding="utf-8")
VISUAL_JS = (ROOT / "assets/js/visual-polish.js").read_text(encoding="utf-8")
TREE = json.loads((ROOT / "content/explore-decision-tree.json").read_text(encoding="utf-8"))
EXPLORE_PARTIAL = (ROOT / "partials/explore.html").read_text(encoding="utf-8")
BLOG_PARTIAL = (ROOT / "partials/transformation-thread.html").read_text(encoding="utf-8")
HEADERS = [(ROOT / "partials" / name).read_text(encoding="utf-8") for name in ["header.html", "brand-header.html", "promotion-header.html"]]

class ExploreDecisionTreeTests(unittest.TestCase):
    def test_nav_and_panel_order_include_explore(self):
        links = ['/#home','/#services','/#explore','/#brands','/#promotions','/#blog','/#about','/#contact']
        panels = ['home','services','explore','brands','promotions','blog','about','contact']
        for header in HEADERS:
            positions = [header.index(f'href="{href}"') for href in links]
            self.assertEqual(positions, sorted(positions))
        positions = [INDEX.index(f'id="{panel}"') for panel in panels]
        self.assertEqual(positions, sorted(positions))

    def test_explore_is_portmason_partial(self):
        self.assertIn('<!-- PM:EXPLORE -->', INDEX)
        self.assertIn('<!-- /PM:EXPLORE -->', INDEX)
        start = INDEX.index('<!-- PM:EXPLORE -->\n') + len('<!-- PM:EXPLORE -->\n')
        end = INDEX.index('<!-- /PM:EXPLORE -->', start)
        self.assertEqual(INDEX[start:end], EXPLORE_PARTIAL)

    def test_counter_moved_into_quiet_explore_strip(self):
        home_end = INDEX.index('</section>', INDEX.index('id="home"'))
        self.assertNotIn('data-performance-proof', INDEX[:home_end])
        self.assertIn('explore-proof-strip', EXPLORE_PARTIAL)
        self.assertIn('data-performance-proof', EXPLORE_PARTIAL)
        self.assertEqual(INDEX.count('data-performance-proof'), 1)

    def test_counter_copy_is_plain_english(self):
        self.assertIn('A quick size check', EXPLORE_PARTIAL)
        self.assertIn('What this shows:', EXPLORE_PARTIAL)
        self.assertIn('your browser can see being downloaded when you opened this site just now', EXPLORE_PARTIAL)
        self.assertIn('Why it matters:', EXPLORE_PARTIAL)
        self.assertIn('<dt>Data downloaded</dt>', EXPLORE_PARTIAL)
        self.assertIn('<dt>JavaScript downloaded</dt>', EXPLORE_PARTIAL)
        self.assertIn('<dt>Files loaded</dt>', EXPLORE_PARTIAL)
        self.assertNotIn('Observed transfer', EXPLORE_PARTIAL)
        self.assertNotIn('Loaded resources', EXPLORE_PARTIAL)

    def test_live_counter_uses_current_network_transfer_entries(self):
        self.assertIn('getEntriesByType("navigation")', VISUAL_JS)
        self.assertIn('getEntriesByType("resource")', VISUAL_JS)
        self.assertIn('entry && entry.transferSize', VISUAL_JS)
        self.assertNotIn('encodedBodySize', VISUAL_JS)

    def test_site_size_compare_is_client_only_two_call_pagespeed_check(self):
        self.assertIn('assets/js/site-size-compare.js', INDEX)
        self.assertIn('data-site-size-self-url="https://www.etal.solutions/"', EXPLORE_PARTIAL)
        self.assertIn('data-site-size-config-url="config.generated.json"', EXPLORE_PARTIAL)
        self.assertIn('Promise.allSettled([', COMPARE_JS)
        self.assertIn('runPageSpeed(theirUrl, "Your homepage", apiKey)', COMPARE_JS)
        self.assertIn('runPageSpeed(selfUrl, "This homepage", apiKey)', COMPARE_JS)
        self.assertIn('strategy: "desktop"', COMPARE_JS)
        self.assertIn('category: "performance"', COMPARE_JS)
        self.assertIn('key: apiKey', COMPARE_JS)
        self.assertIn('hostConfig.PAGESPEED_APIKEY', COMPARE_JS)
        self.assertIn('audits["total-byte-weight"]', COMPARE_JS)
        self.assertIn('2.86 * 1024 * 1024', COMPARE_JS)
        self.assertNotIn('/api/', COMPARE_JS)

    def test_site_size_compare_copy_is_factual_and_source_linked(self):
        self.assertIn('Google PageSpeed will run the same desktop page-size check for your site and ours', EXPLORE_PARTIAL)
        self.assertIn('Google PageSpeed checked both homepages using the same desktop test.', EXPLORE_PARTIAL)
        self.assertIn('Typical desktop homepage', EXPLORE_PARTIAL)
        self.assertIn('2.86 MB', EXPLORE_PARTIAL)
        self.assertIn('HTTP Archive, 2025 Web Almanac', EXPLORE_PARTIAL)
        self.assertIn('target="_blank"', EXPLORE_PARTIAL)
        self.assertIn('rel="noopener noreferrer"', EXPLORE_PARTIAL)

    def test_mesh_cards_are_complete(self):
        self.assertEqual(TREE['start'], 'pressure')
        self.assertEqual(TREE['order'], ['pressure','constraint','exposure','move'])
        self.assertEqual(len(TREE['cards']), 4)
        for card_key in TREE['order']:
            self.assertEqual(len(TREE['cards'][card_key]['options']), 4)
        self.assertEqual(4 ** 4, 256)
        for option in TREE['cards']['move']['options']:
            self.assertTrue(option['complete'])

    def test_progressive_thread_path_is_present(self):
        self.assertIn('data-explore-trail', EXPLORE_PARTIAL)
        self.assertIn('data-explore-question-body', EXPLORE_PARTIAL)
        self.assertIn('data-explore-stage="pressure"', EXPLORE_PARTIAL)
        for stage in ['pressure','constraint','exposure','move','brief']:
            self.assertIn(f'data-explore-trail-step="{stage}"', EXPLORE_PARTIAL)
        self.assertIn('.explore-thread::before', EXPLORE_CSS)
        self.assertIn('.explore-thread-node', EXPLORE_CSS)
        self.assertIn('setTrail', JS)
        self.assertIn('setHidden(questionBody, true)', JS)
        self.assertIn('setHidden(result, false)', JS)

    def test_controller_is_native_contextual_and_reversible(self):
        for token in ['fetch(source', 'encodeURIComponent(body)', 'data-explore-back', 'data-explore-reset', 'showingResult', 'setTrail("brief")', 'setHidden(result, false)', 'window.localStorage', 'recordSelection', 'weights.routes']:
            self.assertIn(token, JS)
        for forbidden in ['React', 'Vue', 'jQuery', 'scrollIntoView', 'hashchange', 'pushState', 'replaceState', 'window.location.hash']:
            self.assertNotIn(forbidden, JS)

    def test_true_alternating_themes_after_explore(self):
        expected = [('home','dark'),('services','light'),('explore','dark'),('brands','light'),('promotions','dark'),('blog','light'),('about','dark'),('contact','light')]
        for section_id, theme in expected:
            tag = re.search(rf'<section[^>]+id="{section_id}"[^>]*>', INDEX)
            self.assertIsNotNone(tag, section_id)
            self.assertIn(f'data-theme="{theme}"', tag.group(0))
        self.assertIn('data-theme="light"', BLOG_PARTIAL)

    def test_shared_action_system_is_loaded(self):
        self.assertIn('assets/css/action-system.css', INDEX)
        self.assertIn('--action-pill-radius', ACTION_CSS)
        self.assertIn('.action-primary', ACTION_CSS)
        self.assertIn('.action-secondary', ACTION_CSS)
        self.assertIn('.action-tertiary', ACTION_CSS)
        self.assertIn('.choice-card', EXPLORE_CSS)

    def test_explore_uses_one_primary_card_not_dashboard_columns(self):
        self.assertIn('explore-path-card', EXPLORE_PARTIAL)
        self.assertNotIn('explore-workbench', EXPLORE_PARTIAL)
        self.assertNotIn('grid-template-columns: minmax(190px, 0.68fr)', EXPLORE_CSS)

    def test_tools_are_stacked_with_horizontal_internal_layouts(self):
        self.assertIn('class="explore-tool-stack"', EXPLORE_PARTIAL)
        self.assertIn('class="explore-path-card explore-tool explore-tool-guided"', EXPLORE_PARTIAL)
        self.assertIn('class="explore-performance-tool explore-tool"', EXPLORE_PARTIAL)
        self.assertNotIn('class="explore-tools-grid"', EXPLORE_PARTIAL)
        self.assertNotIn('class="explore-measurement-stack"', EXPLORE_PARTIAL)
        self.assertIn('.explore-tool-stack {', EXPLORE_CSS)
        self.assertIn('.explore-performance-tool {', EXPLORE_CSS)
        self.assertIn('grid-template-columns: minmax(0, 0.93fr) minmax(0, 1.07fr);', EXPLORE_CSS)
        self.assertIn('grid-template-columns: repeat(3, minmax(0, 1fr));', EXPLORE_CSS)
        self.assertIn('.explore-tool-guided::before', EXPLORE_CSS)
        self.assertIn('.explore-performance-tool::before', EXPLORE_CSS)
        self.assertIn('content: "LIVE";', EXPLORE_CSS)

    def test_subtitle_moves_into_guided_material_and_tools_have_breathing_room(self):
        intro_start = EXPLORE_PARTIAL.index('<header class="explore-intro">')
        intro_end = EXPLORE_PARTIAL.index('</header>', intro_start)
        intro = EXPLORE_PARTIAL[intro_start:intro_end]
        self.assertNotIn('Follow the signal', intro)
        self.assertIn('class="explore-guide-copy"', EXPLORE_PARTIAL)
        self.assertIn('Answer four practical questions.', EXPLORE_PARTIAL)
        self.assertIn('gap: 44px;', EXPLORE_CSS)

    def test_explore_title_row_is_compact_and_tools_are_visually_distinct(self):
        self.assertIn('class="explore-title-row"', EXPLORE_PARTIAL)
        self.assertIn('class="explore-title-divider"', EXPLORE_PARTIAL)
        self.assertIn('.explore-title-row {', EXPLORE_CSS)
        self.assertIn('.explore-tool-guided {', EXPLORE_CSS)
        self.assertIn('.explore-performance-tool {', EXPLORE_CSS)
        self.assertIn('.explore-tool::after', EXPLORE_CSS)
        self.assertIn('rgba(0,255,178,0.20)', EXPLORE_CSS)
        self.assertIn('rgba(99,138,255,0.28)', EXPLORE_CSS)

    def test_guided_path_state_updates_are_immediate(self):
        self.assertNotIn('document.startViewTransition', JS)
        self.assertIn('setTrail(key)', JS)
        self.assertIn('setTrail("brief")', JS)
        self.assertNotIn('data-explore-progress', EXPLORE_PARTIAL)
        self.assertIn('setHidden(questionBody, true)', JS)
        self.assertIn('setHidden(result, false)', JS)

    def test_explore_boundary_is_safe_and_material_rails_are_labeled(self):
        self.assertIn('#explore:target {', EXPLORE_CSS)
        self.assertIn('justify-content: flex-start;', EXPLORE_CSS)
        self.assertIn('scroll-margin-top: 0;', EXPLORE_CSS)
        self.assertIn('transform: none;', EXPLORE_CSS)
        self.assertNotIn('transform: translateY(-24px);', EXPLORE_CSS)
        self.assertNotIn('transform: translateY(-28px);', EXPLORE_CSS)
        self.assertIn('height: 6px;', EXPLORE_CSS)
        self.assertIn('class="explore-material-label explore-material-label-guided"', EXPLORE_PARTIAL)
        self.assertIn('data-explore-mesh-help', EXPLORE_PARTIAL)
        self.assertIn('class="explore-material-label explore-material-label-performance">A quick size check</span>', EXPLORE_PARTIAL)

    def test_guided_tool_uses_spacious_two_tier_mockup_composition(self):
        self.assertIn('grid-template-areas:', EXPLORE_CSS)
        self.assertIn('"head trail"', EXPLORE_CSS)
        self.assertIn('"question question"', EXPLORE_CSS)
        self.assertIn('grid-template-columns: repeat(3, minmax(0, 1fr));', EXPLORE_CSS)
        self.assertIn('class="explore-guide-texture"', EXPLORE_PARTIAL)
        self.assertIn('.explore-guide-texture {', EXPLORE_CSS)

    def test_002_titles_are_inside_colored_rails_with_contrast_text(self):
        override = EXPLORE_CSS[EXPLORE_CSS.index('/* 002 Explore in-rail labels and expanded negative space */'):]
        self.assertIn('.explore-tool::before {', override)
        self.assertIn('height: 24px;', override)
        self.assertIn('.explore-material-label {', override)
        self.assertIn('top: 0;', override)
        self.assertIn('background: transparent;', override)
        self.assertIn('color: #ffffff;', override)
        self.assertIn('.explore-material-label-performance {', override)
        self.assertIn('color: #06162a;', override)

    def test_002_guided_tool_uses_more_intentional_negative_space(self):
        override = EXPLORE_CSS[EXPLORE_CSS.index('/* 002 Explore in-rail labels and expanded negative space */'):]
        self.assertIn('gap: 44px;', override)
        self.assertIn('min-height: 380px;', override)
        self.assertIn('row-gap: 28px;', override)
        self.assertIn('padding: 18px 0 0 42px;', override)
        self.assertIn('margin-top: 20px;', override)
        self.assertIn('min-height: 60px;', override)
        self.assertIn('opacity: 0.16;', override)

    def test_guided_path_changes_material_theme_by_stage(self):
        for stage in ['pressure','constraint','exposure','move','brief']:
            self.assertIn(f'.explore-section[data-explore-stage="{stage}"]', EXPLORE_CSS)
        self.assertIn('--explore-stage-accent: #9b5de5;', EXPLORE_CSS)
        self.assertIn('--explore-stage-accent: #00ffb2;', EXPLORE_CSS)
        self.assertIn('.explore-thread::after', EXPLORE_CSS)
        self.assertIn('width: var(--explore-thread-fill);', EXPLORE_CSS)

    def test_pagespeed_config_uses_exact_identity_variable_name(self):
        self.assertIn('hostConfig.PAGESPEED_APIKEY', COMPARE_JS)
        self.assertIn('hostConfig.pagespeedApiKey', COMPARE_JS)
        self.assertIn('after adding PAGESPEED_APIKEY', COMPARE_JS)
        self.assertNotIn('hostConfig.PAGESPEED_API ||', COMPARE_JS)

    def test_pagespeed_failures_identify_which_homepage_failed(self):
        self.assertIn('runPageSpeed(url, label, apiKey)', COMPARE_JS)
        self.assertIn('label + " could not be checked. "', COMPARE_JS)
        self.assertIn('"Your homepage"', COMPARE_JS)
        self.assertIn('"This homepage"', COMPARE_JS)
        self.assertIn('readApiMessage', COMPARE_JS)

    def test_003_adaptive_mesh_has_four_cards_four_edges_and_256_routes(self):
        self.assertEqual(TREE['version'], '3.1')
        self.assertEqual(len(TREE['order']), 4)
        self.assertEqual(4 ** len(TREE['order']), 256)
        self.assertIn('Guided path', EXPLORE_PARTIAL)
        self.assertIn('class="explore-mesh-board"', EXPLORE_PARTIAL)
        self.assertIn('class="explore-route-panel"', EXPLORE_PARTIAL)

    def test_003_mesh_records_local_anonymous_edge_weights(self):
        for token in ['etal.explore.mesh.v1', 'recordExposure', 'recordSelection', 'edgeSignal', 'weights.routes', 'window.localStorage']:
            self.assertIn(token, JS)
        self.assertNotIn('fetch("/api/', JS)

    def test_003_mesh_produces_explainable_guidance_brief(self):
        for token in ['data-explore-result-insight', 'data-explore-result-why', 'data-explore-result-move', 'data-explore-route-summary', 'data-explore-local-weight']:
            self.assertIn(token, EXPLORE_PARTIAL)
        for token in ['pressure.summary', 'constraint.summary', 'exposure.insight', 'exposure.why', 'move.move']:
            self.assertIn(token, JS)
        self.assertIn('/* 003 Adaptive Guidance Mesh */', EXPLORE_CSS)

    def test_004_nested_mesh_board_places_card_and_route_panel_explicitly(self):
        override = EXPLORE_CSS[EXPLORE_CSS.index('/* 004 Mesh board layout stabilization */'):]
        self.assertIn('grid-template-areas: "card route";', override)
        self.assertIn('.explore-question-body.explore-decision-card {', override)
        self.assertIn('grid-area: card;', override)
        self.assertIn('.explore-route-panel {', override)
        self.assertIn('grid-area: route;', override)
        self.assertIn('minmax(260px, 0.32fr)', override)

    def test_004_route_panel_does_not_collapse_into_vertical_word_strip(self):
        override = EXPLORE_CSS[EXPLORE_CSS.index('/* 004 Mesh board layout stabilization */'):]
        self.assertIn('overflow-wrap: normal;', override)
        self.assertIn('word-break: normal;', override)
        self.assertIn('hyphens: none;', override)
        self.assertIn('@media (max-width: 1120px)', override)
        self.assertIn('grid-template-areas:', override)
        self.assertIn('"card"', override)
        self.assertIn('"route";', override)

    def test_005_uses_card_terminology_and_removes_redundant_ruler_counter(self):
        self.assertIn('cards', TREE)
        self.assertNotIn('plates', TREE)
        self.assertNotIn('data-explore-progress', EXPLORE_PARTIAL)
        self.assertNotIn('Plate', EXPLORE_PARTIAL)
        self.assertNotIn('plate', JS.lower())
        self.assertNotIn('plate', json.dumps(TREE).lower())
        self.assertIn('Card 1 of 4', EXPLORE_PARTIAL)

    def test_005_mesh_help_opens_explanatory_modal(self):
        for token in ['data-explore-mesh-help', 'data-explore-mesh-modal', 'data-explore-mesh-modal-close']:
            self.assertIn(token, EXPLORE_PARTIAL)
        self.assertIn('A clear way to think through a complex problem.', EXPLORE_PARTIAL)
        self.assertIn('Nothing is submitted unless you decide to start a conversation.', EXPLORE_PARTIAL)
        self.assertIn('showModal', JS)
        self.assertIn('openMeshModal', JS)
        self.assertIn('.explore-mesh-modal {', EXPLORE_CSS)

    def test_005_completed_ruler_nodes_and_route_boxes_return_to_previous_cards(self):
        for card in ['pressure', 'constraint', 'exposure', 'move', 'brief']:
            self.assertIn(f'data-explore-jump-to="{card}"', EXPLORE_PARTIAL)
        for token in ['trailActions', 'goToCard', 'data-explore-route-jump', 'explore-route-return']:
            self.assertIn(token, JS)
        self.assertIn('path = path.slice(0, cardIndex);', JS)
        self.assertIn('history = tree.order.slice(0, cardIndex);', JS)
        self.assertIn('.explore-route-return {', EXPLORE_CSS)
        self.assertIn('.explore-thread-action:not(:disabled)', EXPLORE_CSS)


    def test_009_explore_surface_language_is_plain_and_action_row_is_balanced(self):
        self.assertIn('Answer four practical questions.', EXPLORE_PARTIAL)
        self.assertIn('Your choices stay anonymous in this browser.', EXPLORE_PARTIAL)
        self.assertIn('data-explore-result-link hidden', EXPLORE_PARTIAL)
        self.assertIn('class="action action-primary explore-conversation-action"', EXPLORE_PARTIAL)
        self.assertIn('.explore-guide-actions .explore-conversation-action {', EXPLORE_CSS)
        self.assertIn('width: auto;', EXPLORE_CSS)
        self.assertIn('setHidden(resultLink, true)', JS)
        self.assertIn('setHidden(resultLink, false)', JS)
        for phrase in ['Follow the signal', 'Route signal', 'Your emerging route', 'Adaptive guidance mesh', 'neural networks']:
            self.assertNotIn(phrase, EXPLORE_PARTIAL)

    def test_010_question_state_is_stable_and_actions_share_equal_sections(self):
        self.assertIn('class="explore-tertiary-actions"', EXPLORE_PARTIAL)
        self.assertIn('/* 010 Explore stable question card, balanced actions, and close-cropped tool rails */', EXPLORE_CSS)
        self.assertIn('.explore-section:not([data-explore-stage="brief"]) .explore-path-card {', EXPLORE_CSS)
        self.assertIn('height: 500px;', EXPLORE_CSS)
        self.assertIn('grid-template-rows: auto auto minmax(0, 1fr) auto auto;', EXPLORE_CSS)
        self.assertIn('.explore-tertiary-actions {', EXPLORE_CSS)
        self.assertIn('width: 290px;', EXPLORE_CSS)
        self.assertIn('min-height: 56px;', EXPLORE_CSS)
        self.assertIn('height: 17px;', EXPLORE_CSS)

    def test_hero_has_laptop_fold_compaction(self):
        self.assertIn('@media (min-width: 900px) and (max-height: 880px)', CSS)
        self.assertIn('body:not(:has(section:target)) #home { padding-top: 24px; padding-bottom: 24px; }', CSS)
        self.assertNotIn('data-performance-proof', INDEX[INDEX.index('id="home"'):INDEX.index('id="services"')])

if __name__ == '__main__':
    unittest.main()


def test_explore_integrated_rail_titles_and_grouped_actions():
    css = (ROOT / "assets/css/explore.css").read_text()
    assert "/* 011 Explore integrated rail titles and grouped result actions */" in css
    assert ".explore-material-label {" in css
    assert "background: transparent;" in css
    assert "gap: 46px;" in css
    assert ".explore-tertiary-actions {" in css
    assert "display: flex;" in css
    assert "gap: 20px;" in css


def test_explore_rail_titles_are_legible_and_primary_action_is_restrained():
    css = (ROOT / "assets/css/explore.css").read_text()
    assert "/* 012 Explore readable rail titles and restrained primary action */" in css
    assert "background: rgba(4, 14, 31, 0.24);" in css
    assert "color: rgba(241, 247, 255, 0.96);" in css
    assert "min-height: 50px;" in css
    assert "padding: 10px 22px;" in css
