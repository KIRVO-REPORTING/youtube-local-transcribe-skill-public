from __future__ import annotations

import unittest

from ytlt.reporting import render_summary


class ReportingTests(unittest.TestCase):
    def test_timestamped_key_points_render_as_source_video_links(self) -> None:
        source_url = "https://www.bilibili.com/video/BV123/?spm_id_from=test&t=9"
        summary = """Summary

Short summary.

Key Points

- [01:24-02:44] Install the dock animation.
"""

        rendered = render_summary(summary, source_url)

        self.assertIn('class="timestamp-link"', rendered)
        self.assertIn("spm_id_from=test&amp;t=84", rendered)
        self.assertIn(">[01:24-02:44]</a> Install the dock animation.", rendered)

    def test_timestamped_key_points_support_hour_format(self) -> None:
        summary = """Key Points

- [01:02:03-01:04:00] Long video chapter.
"""

        rendered = render_summary(summary, "https://www.youtube.com/watch?v=abc")

        self.assertIn("watch?v=abc&amp;t=3723", rendered)
        self.assertIn("t=3723", rendered)


if __name__ == "__main__":
    unittest.main()
