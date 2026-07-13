from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1] / "codex-skill"
SKILL_PATH = SKILL_ROOT / "SKILL.md"


class SkillMetadataTests(unittest.TestCase):
    def test_bare_url_trigger_is_at_start_of_description(self) -> None:
        lines = SKILL_PATH.read_text(encoding="utf-8").splitlines()
        description = next(
            line.removeprefix("description: ")
            for line in lines
            if line.startswith("description: ")
        )

        discovery_prefix = description[:180].lower()
        self.assertIn("bare youtube", discovery_prefix)
        self.assertIn("youtube shorts", discovery_prefix)
        self.assertIn("do not ask", discovery_prefix)

    def test_core_skill_stays_concise_and_defers_target_details(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertLessEqual(len(text.splitlines()), 150)
        for reference in (
            "setup.md",
            "model-selection.md",
            "reporting.md",
            "notion.md",
            "obsidian.md",
        ):
            self.assertIn(f"references/{reference}", text)
            self.assertTrue((SKILL_ROOT / "references" / reference).is_file())

    def test_processing_is_local_until_report_is_complete(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")

        self.assertIn('video-to-notes process "VIDEO_URL" --environment local', text)
        self.assertIn("prevents an incomplete report", text)
        self.assertIn("Do not stop after `process`", text)
        self.assertIn("Do not assume the current repository", text)
        self.assertIn("Never substitute web-search snippets", text)

    def test_implicit_invocation_metadata_matches_bare_url_behavior(self) -> None:
        text = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        default_prompt = next(
            line.split(": ", 1)[1].strip('"')
            for line in text.splitlines()
            if line.strip().startswith("default_prompt:")
        )

        self.assertIn("allow_implicit_invocation: true", text)
        self.assertIn("bare video URL", default_prompt)
        self.assertLessEqual(len(default_prompt), 128)


if __name__ == "__main__":
    unittest.main()
