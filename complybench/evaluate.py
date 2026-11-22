"""Evaluation metrics for regulation-constrained workflow generation."""
from __future__ import annotations

from .cases import Case


def task_coverage(case: Case, tasks: list[dict]) -> float:
    """Share of required tasks present in the generated plan."""
    if not case.required_tasks:
        return 0.0
    generated = {t.get("id") for t in tasks}
    matched = sum(1 for t in case.required_tasks if t in generated)
    return matched / len(case.required_tasks)


def constraint_violations(case: Case, tasks: list[dict]) -> list[str]:
    """Structural/regulatory violations of generated tasks."""
    problems: list[str] = []
    for t in tasks:
        tid = t.get("id", "?")
        if t.get("required_role") not in case.roles:
            problems.append(f"{tid}: invalid role {t.get('required_role')}")
        deadline = t.get("deadline_min")
        if not isinstance(deadline, (int, float)) or not 1 <= deadline <= case.max_deadline_min:
            problems.append(f"{tid}: deadline {deadline} outside 1..{case.max_deadline_min}")
        if not isinstance(t.get("requires_approval"), bool):
            problems.append(f"{tid}: requires_approval must be a boolean")
    return problems


def full_compliance(case: Case, tasks: list[dict]) -> bool:
    """Case-level full constraint compliance: coverage 100% and no violations."""
    return task_coverage(case, tasks) == 1.0 and not constraint_violations(case, tasks)


def structural_quality(case: Case, tasks: list[dict]) -> float:
    """0-100 structural score: valid roles, deadlines and approval flags."""
    if not tasks:
        return 0.0
    good = len(tasks) - len(constraint_violations(case, tasks))
    return round(100 * good / len(tasks), 2)


def evaluate(case: Case, tasks: list[dict]) -> dict:
    return {
        "case": case.id,
        "coverage": round(task_coverage(case, tasks), 4),
        "violations": len(constraint_violations(case, tasks)),
        "fully_compliant": full_compliance(case, tasks),
        "structural_quality": structural_quality(case, tasks),
    }


def aggregate(rows: list[dict]) -> dict:
    if not rows:
        return {"cases": 0}
    n = len(rows)
    return {
        "cases": n,
        "mean_coverage": round(sum(r["coverage"] for r in rows) / n, 4),
        "full_compliance_rate": round(sum(1 for r in rows if r["fully_compliant"]) / n, 4),
        "mean_structural_quality": round(sum(r["structural_quality"] for r in rows) / n, 2),
        "total_violations": sum(r["violations"] for r in rows),
    }
