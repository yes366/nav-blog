import unittest

from scripts.repair_internal_links import repair_url


class RepairInternalLinksTests(unittest.TestCase):
    def test_rewrites_dead_character_library_links(self):
        self.assertEqual(
            repair_url("https://naviya.chat/characters"),
            "https://www.naviya.chat/create",
        )

    def test_rewrites_dead_privacy_link(self):
        self.assertEqual(
            repair_url("https://naviya.chat/privacy"),
            "https://www.naviya.chat/policy",
        )

    def test_normalizes_live_root_links_to_www(self):
        self.assertEqual(
            repair_url("https://naviya.chat/create"),
            "https://www.naviya.chat/create",
        )


if __name__ == "__main__":
    unittest.main()
