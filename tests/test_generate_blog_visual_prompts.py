import unittest

from scripts.generate_blog_visuals import build_prompt


class GenerateBlogVisualPromptsTests(unittest.TestCase):
    def test_build_prompt_appends_negative_rules(self):
        prompt = build_prompt({
            "slug": "character-ai-alternative-2026",
            "title": "Best Character AI Alternatives in 2026",
            "mode": "generated_editorial",
            "prompt": "Editorial cover art",
        })
        self.assertIn("no watermark", prompt)
        self.assertIn("no text", prompt)
        self.assertIn("Editorial cover art", prompt)


if __name__ == "__main__":
    unittest.main()
