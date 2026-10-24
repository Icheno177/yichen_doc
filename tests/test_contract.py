from pathlib import Path
import json
import unittest

from yichen_doc.content import load_content, validate_content

ROOT = Path(__file__).resolve().parents[1]


class ContentContractTests(unittest.TestCase):
    def test_sample_contract_is_valid(self):
        data = load_content(ROOT / "examples" / "sample_research.json")
        self.assertEqual(data["schema_version"], "1.0")

    def test_unknown_source_is_rejected(self):
        data = json.loads((ROOT / "examples" / "sample_research.json").read_text(encoding="utf-8"))
        data["sections"][0]["blocks"][0]["source_ids"] = ["S-UNKNOWN"]
        with self.assertRaisesRegex(ValueError, "unknown source"):
            validate_content(data, ROOT / "examples")

    def test_chart_series_length_must_match_categories(self):
        data = json.loads((ROOT / "examples" / "sample_research.json").read_text(encoding="utf-8"))
        data["sections"][0]["blocks"][3]["series"][0]["values"] = [1]
        with self.assertRaisesRegex(ValueError, "series length"):
            validate_content(data, ROOT / "examples")

    def test_excel_formula_must_be_explicit(self):
        data = json.loads((ROOT / "examples" / "sample_research.json").read_text(encoding="utf-8"))
        data["calculations"][0]["excel_formula"] = "Inputs!C2-Inputs!C3"
        with self.assertRaisesRegex(ValueError, "start with"):
            validate_content(data, ROOT / "examples")


if __name__ == "__main__":
    unittest.main()
