import unittest

from scripts.generate_blog_visuals import build_generate_request


class GenerateBlogVisualRequestTests(unittest.TestCase):
    def test_generated_editorial_request_disables_watermark(self):
        request = build_generate_request(
            {
                "slug": "best-ai-apps-creative-writing-2026",
                "title": "Best AI Apps for Creative Writing in 2026",
                "mode": "generated_editorial",
                "prompt": "Premium editorial illustration",
            }
        )
        self.assertEqual(request["watermark"], False)
        self.assertEqual(request["size"], "2048x2048")
        self.assertIn("no watermark", request["prompt"])


if __name__ == "__main__":
    unittest.main()
