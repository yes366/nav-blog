import unittest

from scripts.validate_blog_quality import find_inline_image_refs, is_generated_cover_policy


class ValidateBlogQualityTests(unittest.TestCase):
    def test_find_inline_image_refs_detects_markdown_images(self):
        refs = find_inline_image_refs(
            "hello\n![hero](./images/sample.jpg)\nworld\n![chart](./images/chart.jpg)"
        )
        self.assertEqual(refs, ["./images/sample.jpg", "./images/chart.jpg"])

    def test_generated_cover_policy_requires_generated_editorial(self):
        self.assertTrue(is_generated_cover_policy({"mode": "generated_editorial"}))
        self.assertFalse(is_generated_cover_policy({"mode": "product_screenshot"}))


if __name__ == "__main__":
    unittest.main()
