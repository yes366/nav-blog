import unittest

from scripts.audit_blog_content import classify_issue


class AuditBlogContentTests(unittest.TestCase):
    def test_flags_dead_internal_www_links(self):
        issue = classify_issue(
            slug="sample",
            url="https://www.naviya.chat/features",
            status_code=404,
            similarity_score=0.0,
            image_mode="generated",
        )
        self.assertIn("dead_link", issue["issues"])

    def test_flags_character_images_that_need_reference_art(self):
        issue = classify_issue(
            slug="sample-character",
            url="",
            status_code=200,
            similarity_score=0.0,
            image_mode="character_generated",
        )
        self.assertIn("image_needs_reference", issue["issues"])


if __name__ == "__main__":
    unittest.main()
