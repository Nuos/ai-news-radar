"""Offline regression checks for fork setup; no network or secrets."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

spec = importlib.util.spec_from_file_location("fork_setup", Path(__file__).resolve().parents[1] / "scripts/fork_setup.py")
fork_setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fork_setup)


class ForkSetupTests(unittest.TestCase):
    def fixture(self, root):
        for name in fork_setup.CONFIG_PATHS:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            content = 'SITE = "https://news.learnprompt.pro"\n'
            if name == "skills/radar/SKILL.md":
                content = "BASE_URL=https://news.Nuos.pro/data\nhttps://raw.githubusercontent.com/LearnPrompt/ai-news-radar/master/data/latest-24h.json\n"
            path.write_text(content, encoding="utf-8")
        (root / "README.md").write_text("# Upstream documentation\n", encoding="utf-8")

    def test_configure_is_idempotent_and_preserves_upstream_readme(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / "CNAME").write_text("news.learnprompt.pro")
            self.assertTrue(fork_setup.configure(root, fork_setup.DEFAULT_SITE, fork_setup.DEFAULT_REPOSITORY))
            self.assertFalse((root / "CNAME").exists())
            self.assertTrue((root / ".nojekyll").exists())
            skill = (root / "skills/radar/SKILL.md").read_text()
            self.assertIn("BASE_URL=https://nuos.github.io/ai-news-radar/data", skill)
            self.assertIn("raw.githubusercontent.com/Nuos/ai-news-radar", skill)
            self.assertEqual(fork_setup.configure(root, fork_setup.DEFAULT_SITE, fork_setup.DEFAULT_REPOSITORY), [])
            self.assertTrue((root / "README.md").read_text().endswith("# Upstream documentation\n"))

    def test_reject_custom_domain_without_writing(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / "CNAME").write_text("my.example.org")
            before = (root / "index.html").read_bytes()
            with self.assertRaises(ValueError):
                fork_setup.configure(root, fork_setup.DEFAULT_SITE, fork_setup.DEFAULT_REPOSITORY)
            self.assertEqual((root / "index.html").read_bytes(), before)

    def test_reject_invalid_url(self):
        for url in ("http://example.org", "https://a:b@example.org", "https://example.org/?token=a", "https://example.org/\"bad"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                fork_setup.normalize_site(url)

    def test_timestamp_requires_timezone(self):
        self.assertIsNotNone(fork_setup.timestamp("2026-09-22T10:00:00Z").tzinfo)
        with self.assertRaises(ValueError):
            fork_setup.timestamp("2026-09-22T10:00:00")


if __name__ == "__main__":
    unittest.main()
