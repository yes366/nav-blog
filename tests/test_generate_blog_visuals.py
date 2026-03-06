import unittest

from scripts.generate_blog_visuals import build_visual_job


class GenerateBlogVisualsTests(unittest.TestCase):
    def test_character_post_uses_reference_mode(self):
        post = {
            "slug": "meet-luna-ai-healer-character-spotlight",
            "title": "Meet Luna: The AI Healer Who Actually Listens",
            "category": "spotlight",
        }
        manifest = {
            "meet-luna-ai-healer-character-spotlight": {
                "mode": "character_reference",
                "reference_image": "../assets/characters/luna.jpg",
            }
        }
        job = build_visual_job(post, manifest)
        self.assertEqual(job["mode"], "character_reference")
        self.assertEqual(job["reference_image"], "../assets/characters/luna.jpg")

    def test_product_post_uses_screenshot_mode(self):
        post = {
            "slug": "best-ai-chat-apps-tabletop-gms",
            "title": "Best AI Chat Apps for Tabletop GMs",
            "category": "comparison",
        }
        manifest = {
            "best-ai-chat-apps-tabletop-gms": {
                "mode": "product_screenshot",
                "screenshot_targets": ["/create", "/chat"],
            }
        }
        job = build_visual_job(post, manifest)
        self.assertEqual(job["mode"], "product_screenshot")
        self.assertEqual(job["screenshot_targets"], ["/create", "/chat"])


if __name__ == "__main__":
    unittest.main()
