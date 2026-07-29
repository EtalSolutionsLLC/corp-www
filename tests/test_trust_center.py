from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "www"
TRUST = (SITE / "trust/index.html").read_text(encoding="utf-8")
TRUST_CSS = (SITE / "assets/css/trust-center.css").read_text(encoding="utf-8")
SITE_CSS = (SITE / "assets/css/styles.css").read_text(encoding="utf-8")
HEADER = (SITE / "partials/header.html").read_text(encoding="utf-8")
FOOTER = (SITE / "partials/footer.html").read_text(encoding="utf-8")
TRUST_HEADER = (SITE / "partials/trust-header.html").read_text(encoding="utf-8")

TRUST_TARGETS = (
    "trust-top",
    "trust-responsibility",
    "trust-controls",
    "trust-reviewnudge",
    "trust-operations",
    "trust-documents",
    "trust-contact",
)


class TrustCenterTests(unittest.TestCase):
    def test_trust_center_is_public_and_linked_from_shared_navigation(self):
        self.assertTrue((SITE / "trust/index.html").is_file())
        self.assertIn('href="/trust/#trust-top"', HEADER)
        self.assertIn('href="/trust/?nav=corp#trust-top"', FOOTER)
        self.assertNotIn("login", TRUST.lower())

    def test_company_and_product_responsibilities_are_separate(self):
        self.assertIn("Et al Solutions LLC operates its products", TRUST)
        self.assertIn("How payment works", TRUST)
        self.assertIn("Et al Solutions LLC sells the subscription", TRUST)
        self.assertIn("Customers enter payment details on a", TRUST)
        self.assertIn("Stripe-hosted Checkout page", TRUST)
        self.assertIn("securely collect and transmit payment information directly to Stripe", TRUST)
        self.assertIn("https://docs.stripe.com/payments/checkout", TRUST)
        self.assertIn("https://docs.stripe.com/security/guide", TRUST)
        self.assertIn('id="trust-reviewnudge"', TRUST)
        self.assertIn("How ReviewNudge handles information", TRUST)
        self.assertIn("ReviewNudge is a product and service of Et al Solutions LLC", TRUST)

    def test_trust_claims_include_important_limits(self):
        self.assertIn("No internet service can promise immunity from attack", TRUST)
        self.assertIn("does not currently publish a ReviewNudge uptime SLA", TRUST)
        self.assertIn("does not publish a recovery point objective or recovery time objective", TRUST)
        self.assertIn("not the complete card number or security code", TRUST)

    def test_support_issue_path_is_sanitized_and_private(self):
        self.assertIn("private GitHub repository", TRUST)
        self.assertIn("raw support transcripts are excluded from such records", TRUST)
        self.assertIn("Feature requests", TRUST)

    def test_formal_summary_and_operations_copy_reflect_current_controls(self):
        self.assertIn("Trust, security, and operational information", TRUST)
        self.assertIn("Applicable agreements and published policies remain authoritative", TRUST)
        self.assertIn("independent multi-region availability monitoring", TRUST)
        self.assertIn("Failures affecting at least two regions generate an operational alert", TRUST)

    def test_canonical_documents_are_linked(self):
        for filename in (
            "et-al-solutions-llc-privacy-policy.html",
            "et-al-solutions-llc-data-processing-addendum.html",
            "et-al-solutions-llc-subprocessor-list.html",
        ):
            self.assertIn(filename, TRUST)

    def test_sections_alternate_and_dark_sections_share_the_brand_rail(self):
        themes = [
            'data-theme="dark"',
            'data-theme="light"',
            'data-theme="dark"',
            'data-theme="light"',
            'data-theme="dark"',
            'data-theme="light"',
            'data-theme="dark"',
        ]
        positions = []
        start = 0
        for theme in themes:
            position = TRUST.find(theme, start)
            self.assertGreater(position, -1)
            positions.append(position)
            start = position + len(theme)
        self.assertEqual(positions, sorted(positions))
        self.assertIn('border-image: linear-gradient(180deg, #123bff, #00ffb2) 1;', TRUST_CSS)

    def test_sections_use_shared_viewport_navigation_contract(self):
        self.assertIn('/assets/css/viewport-contract.css', TRUST)
        self.assertGreater(
            TRUST.index('/assets/css/viewport-contract.css'),
            TRUST.index('/assets/css/trust-center.css'),
        )
        self.assertIn('/assets/js/viewport-targets.js', TRUST)

        for target_id in TRUST_TARGETS:
            with self.subTest(target_id=target_id):
                match = re.search(rf'<section[^>]+id="{target_id}"[^>]*>', TRUST)
                self.assertIsNotNone(match)
                tag = match.group(0)
                self.assertIn("pm-viewport-target", tag)
                self.assertIn("pm-scroll-target", tag)

                section_start = match.end()
                section_end = TRUST.find("</section>", section_start)
                section = TRUST[section_start:section_end]
                self.assertIn("pm-viewport-target__inner", section)

        self.assertIn('href="#trust-top"', TRUST_HEADER)
        self.assertNotIn('/trust/#trust-home', TRUST_HEADER)

    def test_cross_document_menu_swap_does_not_crossfade(self):
        self.assertNotIn("navigation: auto;", SITE_CSS)
        self.assertNotIn("view-transition-name: corp-site-header", SITE_CSS)
        self.assertNotIn("view-transition-name: corp-site-footer", SITE_CSS)

    def test_mobile_layout_collapses_to_one_column(self):
        self.assertIn("@media (max-width: 640px)", TRUST_CSS)
        self.assertIn(".trust-grid--four", TRUST_CSS)
        self.assertIn("grid-template-columns: 1fr;", TRUST_CSS)


if __name__ == "__main__":
    unittest.main()
