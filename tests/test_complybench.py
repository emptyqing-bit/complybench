"""ComplyBench unit tests (stdlib unittest; run: python -m unittest discover tests)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from complybench import (Case, OracleRunner, PartialRunner, RandomRunner,
                         aggregate, evaluate, load_cases, markdown_report,
                         run_benchmark)

ROOT = Path(__file__).resolve().parents[1]


class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.case = Case(
            id="c1", incident_type="fire", severity=2,
            roles=("security", "teacher"),
            required_tasks=("a", "b"), max_deadline_min=30,
        )

    def test_oracle_perfect(self):
        tasks = OracleRunner().run(self.case)
        row = evaluate(self.case, tasks)
        self.assertEqual(row["coverage"], 1.0)
        self.assertTrue(row["fully_compliant"])

    def test_partial_penalised(self):
        tasks = PartialRunner().run(self.case)
        row = evaluate(self.case, tasks)
        self.assertLess(row["coverage"], 1.0)
        self.assertGreater(row["violations"], 0)
        self.assertFalse(row["fully_compliant"])

    def test_invalid_deadline_detected(self):
        tasks = [{"id": "a", "required_role": "security", "deadline_min": 0,
                  "requires_approval": False}]
        row = evaluate(self.case, tasks)
        self.assertGreater(row["violations"], 0)

    def test_missing_approval_flag_detected(self):
        tasks = [{"id": "a", "required_role": "security", "deadline_min": 5}]
        row = evaluate(self.case, tasks)
        self.assertGreater(row["violations"], 0)


class TestBenchmark(unittest.TestCase):
    def test_full_pipeline(self):
        cases = load_cases(ROOT / "data" / "sample_cases.json")
        self.assertEqual(len(cases), 4)
        results = run_benchmark(cases, [OracleRunner(), PartialRunner(), RandomRunner()])
        self.assertEqual(len(results), 3)
        report = markdown_report(results)
        self.assertIn("| Runner |", report)
        agg = aggregate(results["oracle"])
        self.assertEqual(agg["full_compliance_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
