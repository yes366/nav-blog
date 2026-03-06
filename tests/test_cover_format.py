import unittest

from scripts.generate_blog_visuals import COVER_RATIO, COVER_SIZE, build_cover_output_path


class CoverFormatTests(unittest.TestCase):
    def test_cover_ratio_is_21_by_9(self):
        self.assertEqual(COVER_RATIO, (21, 9))
        self.assertEqual(COVER_SIZE, (2100, 900))

    def test_cover_output_path_uses_cover_suffix(self):
        self.assertEqual(
            str(build_cover_output_path("best-ai-chat-apps-2026")),
            "content/blog/images/best-ai-chat-apps-2026-cover.jpg",
        )


if __name__ == "__main__":
    unittest.main()
