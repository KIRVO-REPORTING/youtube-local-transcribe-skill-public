from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ytlt.runtime import JavascriptRuntime, doctor, is_youtube_url, youtube_ydl_options


class RuntimeTests(unittest.TestCase):
    def test_youtube_url_detection(self) -> None:
        self.assertTrue(is_youtube_url("https://www.youtube.com/watch?v=abc"))
        self.assertTrue(is_youtube_url("https://youtu.be/abc"))
        self.assertFalse(is_youtube_url("https://www.bilibili.com/video/BV1"))

    def test_youtube_options_enable_detected_runtime(self) -> None:
        runtime = JavascriptRuntime(name="node", path="/opt/node", version="v24.0.0")

        with patch("ytlt.runtime.detect_javascript_runtimes", return_value=[runtime]):
            options = youtube_ydl_options("https://www.youtube.com/watch?v=abc")

        self.assertEqual(options["js_runtimes"], {"node": {"path": "/opt/node"}})

    def test_youtube_options_fail_early_without_runtime(self) -> None:
        with patch("ytlt.runtime.detect_javascript_runtimes", return_value=[]):
            with self.assertRaises(RuntimeError) as raised:
                youtube_ydl_options("https://www.youtube.com/watch?v=abc")

        self.assertIn("Node.js 22+", str(raised.exception))

    def test_non_youtube_options_do_not_require_runtime(self) -> None:
        with patch("ytlt.runtime.detect_javascript_runtimes", return_value=[]):
            self.assertEqual(youtube_ydl_options("https://example.com/video"), {})

    def test_doctor_reports_ready_base_runtime_without_config(self) -> None:
        runtime = JavascriptRuntime(name="node", path="/opt/node", version="v24.0.0")
        with tempfile.TemporaryDirectory() as tmp, patch(
            "ytlt.runtime.detect_javascript_runtimes", return_value=[runtime]
        ), patch("ytlt.runtime._package_version", side_effect=lambda name: "1.0"), patch(
            "ytlt.runtime.resolve_ffmpeg_path", return_value="/opt/ffmpeg"
        ), patch(
            "ytlt.runtime.sys.version_info", (3, 12, 0)
        ):
            payload = doctor(Path(tmp))

        self.assertTrue(payload["ready"])
        self.assertFalse(payload["configured"])
        self.assertTrue(payload["warnings"])


if __name__ == "__main__":
    unittest.main()
