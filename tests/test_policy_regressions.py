from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PolicyRegressionTests(unittest.TestCase):
    def read(self, rel):
        return (ROOT / rel).read_text(encoding="utf-8")

    def test_all_local_markdown_links_resolve(self):
        for source in ROOT.rglob("*.md"):
            if ".git" in source.parts or "node_modules" in source.parts:
                continue
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", source.read_text(encoding="utf-8")):
                if "://" in link or link.startswith("#"):
                    continue
                target = link.split("#", 1)[0]
                self.assertTrue((source.parent / target).exists(), f"{source.relative_to(ROOT)}: {link}")

    def test_writing_rules_preserve_evidence_and_truthfulness(self):
        policy = self.read("references/WRITING_POLICY.md")
        for phrase in ("source grade", "ASSUMPTION", "Unknown numeric inputs remain blank", "Prompt or workflow iteration is not model training", "Bear/Base/Bull"):
            self.assertIn(phrase, policy)

    def test_skill_selects_only_requested_formats(self):
        skill = self.read("SKILL.md")
        self.assertIn("Select only the output formats the user needs", skill)
        self.assertIn("DOCX", skill); self.assertIn("PPTX", skill); self.assertIn("XLSX", skill); self.assertIn("HTML", skill)

    def test_legacy_research_references_remain(self):
        for path in ("references/ANTI_AI_WRITING.md", "references/STYLE_SPEC.md", "references/EVIDENCE_RULES.md", "references/RESEARCH_WORKFLOW.md", "references/REPORT_PATTERNS.md", "references/QUANTITATIVE_METHODS.md"):
            self.assertTrue((ROOT / path).is_file(), path)


if __name__ == "__main__":
    unittest.main()
