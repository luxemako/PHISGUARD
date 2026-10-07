import unittest

from app.services.url_features import extract_url_features


class URLFeatureTests(unittest.TestCase):
    def test_www_does_not_change_features(self):
        without_www = extract_url_features("https://example.com/login")
        with_www = extract_url_features("https://www.example.com/login")
        self.assertEqual(without_www, with_www)

    def test_login_in_path_is_not_a_domain_warning(self):
        features = extract_url_features("https://printbala.com/app/#/portal/login")
        self.assertEqual(features["has_suspicious_word_in_domain"], 0)
        self.assertEqual(features["has_suspicious_word_in_path"], 1)

    def test_suspicious_domain_keyword_is_detected(self):
        features = extract_url_features("https://secure-login.example.com")
        self.assertEqual(features["has_suspicious_word_in_domain"], 1)

    def test_shortener_requires_domain_boundary(self):
        self.assertEqual(extract_url_features("https://bit.ly/a")["uses_shortener"], 1)
        self.assertEqual(extract_url_features("https://chatgpt.com")["uses_shortener"], 0)
        self.assertEqual(
            extract_url_features("https://notbit.ly.example.com")["uses_shortener"],
            0,
        )

    def test_ipv4_and_ipv6_are_detected(self):
        self.assertEqual(extract_url_features("http://127.0.0.1")["has_ip_address"], 1)
        self.assertEqual(extract_url_features("https://[2001:db8::1]")["has_ip_address"], 1)

    def test_country_code_subdomains(self):
        self.assertEqual(extract_url_features("https://example.co.uk")["subdomain_count"], 0)
        self.assertEqual(extract_url_features("https://shop.example.co.uk")["subdomain_count"], 1)
        self.assertEqual(extract_url_features("https://co.uk")["subdomain_count"], 0)

    def test_typosquatting_is_detected(self):
        self.assertEqual(extract_url_features("https://goolge.com")["has_typosquatting"], 1)
        self.assertEqual(extract_url_features("https://google.com")["has_typosquatting"], 0)

    def test_brand_outside_official_domain_is_detected(self):
        features = extract_url_features("https://google.secure-login.invalid")
        self.assertEqual(features["has_brand_impersonation"], 1)

    def test_path_and_query_features(self):
        features = extract_url_features(
            "https://example.com/download/file.exe?redirect=https%3A%2F%2Fevil.invalid"
        )
        self.assertEqual(features["path_depth"], 2)
        self.assertEqual(features["query_parameter_count"], 1)
        self.assertEqual(features["has_redirect_parameter"], 1)
        self.assertEqual(features["has_suspicious_file_extension"], 1)
        self.assertGreater(features["encoded_character_count"], 0)


if __name__ == "__main__":
    unittest.main()
