import unittest
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.yt_extractor import normalize_video_id

class TestUrlParser(unittest.TestCase):
    def test_standard_url(self):
        self.assertEqual(normalize_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_shortened_url(self):
        self.assertEqual(normalize_video_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_shorts_url(self):
        self.assertEqual(normalize_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_url_with_query_params(self):
        self.assertEqual(normalize_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&feature=share"), "dQw4w9WgXcQ")

    def test_url_with_tracking_si(self):
        self.assertEqual(normalize_video_id("https://youtu.be/dQw4w9WgXcQ?si=abcdef1234567890"), "dQw4w9WgXcQ")

    def test_mobile_url(self):
        self.assertEqual(normalize_video_id("https://m.youtube.com/watch?v=dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_bare_id(self):
        self.assertEqual(normalize_video_id("dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_invalid_url(self):
        with self.assertRaises(ValueError):
            normalize_video_id("https://notyoutube.com/something")

if __name__ == "__main__":
    unittest.main()
