"""Run a set of runners over the case set and render a Markdown report."""
from __future__ import annotations

from .cases import Case
from .evaluate import aggregate, evaluate


def run_benchmark(cases: list[Case], runners: list) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}
    for runner in runners:
        rows = []
        for case in cases:
            tasks = runner.run(case)
            row = evaluate(case, tasks)
            row["runner"] = runner.name
            rows.append(row)
        results[runner.name] = rows
    return results


def markdown_report(results: dict[str, list[dict]]) -> str:
    lines = [
        "# ComplyBench report",
        "",
        "| Runner | Cases | Mean coverage | Full compliance | Structural quality | Violations |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, rows in results.items():
        agg = aggregate(rows)
        lines.append(
            f"| {name} | {agg['cases']} | {agg['mean_coverage']:.2%} | "
            f"{agg['full_compliance_rate']:.2%} | {agg['mean_structural_quality']:.1f} | "
            f"{agg['total_violations']} |"
        )
    lines += [
        "",
        "Metrics: coverage = required tasks present; full compliance = 100% coverage "
        "and zero constraint violations; structural quality = share of valid generated tasks.",
        "",
    ]
    return "\n".join(lines)
