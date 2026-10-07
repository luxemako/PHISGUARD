import unittest

from app.services.analyzers import extract_urls
from app.services.risk_engine import (
    analyze_text_rules,
    combine_email_risk,
    risk_level,
)


class RiskEngineTests(unittest.TestCase):
    def test_text_rules_report_multiple_indicators(self):
        result = analyze_text_rules(
            "Urgent: enter your password to claim your free gift."
        )
        self.assertEqual(result["score"], 80)
        self.assertEqual(len(result["warnings"]), 3)

    def test_email_risk_uses_highest_url_score(self):
        score = combine_email_risk(40, [20, 90], 30)
        self.assertEqual(score, 59.0)

    def test_risk_levels(self):
        self.assertEqual(risk_level(29), "low")
        self.assertEqual(risk_level(30), "medium")
        self.assertEqual(risk_level(60), "high")

    def test_url_extraction_deduplicates_and_trims_punctuation(self):
        urls = extract_urls(
            "Open https://example.com/login, then https://example.com/login."
        )
        self.assertEqual(urls, ["https://example.com/login"])


if __name__ == "__main__":
    unittest.main()
