import unittest
from pathlib import Path

from src.screening import read_financial_data, screen


SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample" / "financial_data.csv"


class ScreeningTests(unittest.TestCase):
    def setUp(self):
        self.rows = read_financial_data(SAMPLE)

    def test_sample_flags_r1_only(self):
        result = screen(self.rows)
        self.assertEqual([r["status"] for r in result["results"]],
                         ["REVIEW", "PASS", "PASS"])
        self.assertEqual(result["results"][0]["calculation"]["difference_pp"], 65.71)
        self.assertFalse(result["results"][0]["source_verified"])

    def test_wrong_unit_conversion_is_data_issue_for_affected_rules(self):
        self.rows[0] = {**self.rows[0], "value_yuan": "123"}
        statuses = [r["status"] for r in screen(self.rows)["results"]]
        self.assertEqual(statuses, ["DATA_ISSUE", "PASS", "PASS"])

    def test_missing_cashflow_only_blocks_r2(self):
        rows = [r for r in self.rows if r["metric"] != "经营活动现金流量净额"]
        statuses = [r["status"] for r in screen(rows)["results"]]
        self.assertEqual(statuses, ["REVIEW", "DATA_ISSUE", "PASS"])

    def test_duplicate_record_is_data_issue(self):
        statuses = [r["status"] for r in screen(self.rows + [self.rows[0]])["results"]]
        self.assertEqual(statuses, ["DATA_ISSUE", "PASS", "PASS"])


if __name__ == "__main__":
    unittest.main()
