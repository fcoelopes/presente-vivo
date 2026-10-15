import os
import tempfile
import unittest

with tempfile.TemporaryDirectory() as _unused:
    pass

os.environ.setdefault("ADMIN_USER", "ci-admin")
os.environ.setdefault("ADMIN_PASSWORD", "ci-secret")
os.environ.setdefault("PUBLIC_BASE_URL", "https://presente.arc.tec.br")
_TEST_DIRECTORY = tempfile.TemporaryDirectory()
os.environ["DB_PATH"] = os.path.join(_TEST_DIRECTORY.name, "presentes.sqlite3")

from app.main import connect, qr, tag


class PremiumTagTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = "abcDEF1234567890"
        with connect() as c:
            c.execute(
                """INSERT INTO gifts
                (id, theme, recipient, sender, teaser, message, voice_url,
                 photo_url, extra_messages, created_at, enabled)
                VALUES (?, ?, ?, ?, ?, ?, '', '', '', '', 1)""",
                (cls.key, "amor", 'Juliana </script><script>alert(1)</script>',
                 "Carlos", "Alguns sentimentos não cabem no papel...",
                 "Uma carta de Natal")
            )

    def test_premium_tag_reuses_existing_link(self):
        response = tag(self.key)
        content = response.body.decode()
        self.assertIn("tag-premium.css", content)
        self.assertIn("tag-premium.js", content)
        self.assertIn("Baixar SVG", content)
        self.assertIn("abcDEF1234567890", content)
        self.assertNotIn("</script><script>alert", content)
        self.assertIn("u003c", content)

    def test_qr_png(self):
        response = qr(self.key)
        self.assertEqual(response.media_type, "image/png")


if __name__ == "__main__":
    unittest.main()
