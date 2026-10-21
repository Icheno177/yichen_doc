"""Static regression checks for cross-document writing-policy consistency."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WritingPolicyRegressionTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_socrates_is_explicit_request_only_everywhere(self):
        for path in ("SKILL.md", "README.md", "AGENTS.md", "references/WRITING_POLICY.md", "references/SOCRATES_CS_INTEGRATION.md"):
            content = self.read(path).lower()
            self.assertTrue("explicitly request" in content or "explicitly asks" in content or "explicitly requests" in content, path)
            self.assertIn("not enabled by default", content, path)

    def test_no_automatic_socrates_fallback_remains(self):
        content = "\n".join(
            self.read(path)
            for path in ("SKILL.md", "README.md", "AGENTS.md", "references/WRITING_POLICY.md", "references/SOCRATES_CS_INTEGRATION.md")
        ).lower()
        self.assertNotIn("if socrates.cs is unavailable, apply the same questions manually", content)
        self.assertNotIn("\nuse after a draft has", content)

    def test_skill_trigger_covers_requested_deliverables_and_excludes_casual_chat(self):
        content = self.read("SKILL.md").lower().split("---", 2)[1]
        for term in ("research reports", "industry", "company", "investment", "strategy", "resume", "interview", "ppt", "formal emails"):
            self.assertIn(term, content)
        self.assertIn("casual chat", content)

    def test_policy_contains_thesis_evidence_and_resume_safeguards(self):
        content = self.read("references/WRITING_POLICY.md")
        for term in ("genuine, relevant, verifiable support", "Disclose a contradiction", "Missing Data", "Prompt or workflow iteration is not model training", "Bear/Base/Bull"):
            self.assertIn(term, content)

    def test_relative_markdown_links_resolve(self):
        for source in ROOT.rglob("*.md"):
            if ".git" in source.parts:
                continue
            content = source.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if "://" in target or target.startswith("#"):
                    continue
                path = target.split("#", 1)[0]
                self.assertTrue((source.parent / path).exists(), f"{source.relative_to(ROOT)}: {target}")


if __name__ == "__main__":
    unittest.main()
