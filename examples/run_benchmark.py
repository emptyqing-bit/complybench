"""Run the sample benchmark offline and print a Markdown report.

Usage (repository root): python examples/run_benchmark.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from complybench import (OracleRunner, PartialRunner, RandomRunner,
                         load_cases, markdown_report, run_benchmark)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    cases = load_cases(root / "data" / "sample_cases.json")
    runners = [OracleRunner(), PartialRunner(), RandomRunner(seed=7)]
    results = run_benchmark(cases, runners)
    print(markdown_report(results))

    # To benchmark a real LLM instead, add:
    #   from complybench import LLMRunner
    #   runners.append(LLMRunner("http://localhost:11434", "qwen2.5", guided=True))


if __name__ == "__main__":
    main()
