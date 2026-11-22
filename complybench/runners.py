"""Plan runners: deterministic baselines and an optional real LLM runner.

A runner maps a Case to a list of generated task dicts:
    {"id", "required_role", "deadline_min", "requires_approval"}
"""
from __future__ import annotations

import json
import random
import urllib.request
from typing import Protocol

from .cases import Case


class Runner(Protocol):
    name: str

    def run(self, case: Case) -> list[dict]: ...


def _task(task_id: str, role: str, deadline: int = 10, approval: bool = False) -> dict:
    return {"id": task_id, "required_role": role,
            "deadline_min": deadline, "requires_approval": approval}


class OracleRunner:
    """Upper bound: returns exactly the required tasks with valid roles."""
    name = "oracle"

    def run(self, case: Case) -> list[dict]:
        return [_task(t, case.roles[i % len(case.roles)])
                for i, t in enumerate(case.required_tasks)]


class PartialRunner:
    """Drops the last required task and assigns an invalid role to the first.

    Deterministic ablation baseline showing how the metrics respond to
    missing tasks and role violations.
    """
    name = "partial-ablation"

    def run(self, case: Case) -> list[dict]:
        tasks = [_task(t, case.roles[0]) for t in case.required_tasks[:-1]]
        if tasks:
            tasks[0]["required_role"] = "nonexistent-role"
        return tasks


class RandomRunner:
    """Random subset of required tasks with random deadlines (seeded)."""
    name = "random-subset"

    def __init__(self, seed: int = 7):
        self.rng = random.Random(seed)

    def run(self, case: Case) -> list[dict]:
        keep = [t for t in case.required_tasks if self.rng.random() > 0.3]
        return [_task(t, case.roles[0], deadline=self.rng.choice([0, 5, 90]))
                for t in keep]


class LLMRunner:
    """Real LLM baseline via any OpenAI-compatible endpoint.

    `guided=False`: prompt with the incident only (naive generation).
    `guided=True`: prompt also lists valid roles and required constraints.
    """

    def __init__(self, base_url: str, model: str, api_key: str = "",
                 guided: bool = False, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.guided = guided
        self.timeout = timeout
        self.name = f"llm:{model}:{'guided' if guided else 'naive'}"

    def _prompt(self, case: Case) -> str:
        base = (
            "Generate an emergency-response workflow for a campus incident.\n"
            f"Incident type: {case.incident_type}; severity: {case.severity}/3.\n"
            "Return a JSON array of tasks, each with keys: id, required_role, "
            "deadline_min, requires_approval. JSON only."
        )
        if self.guided:
            base += (
                f"\nValid roles: {', '.join(case.roles)}."
                f"\nEvery deadline must be between 1 and {case.max_deadline_min} minutes."
                "\nTasks that require sign-off must set requires_approval=true."
            )
        return base

    def run(self, case: Case) -> list[dict]:
        body = json.dumps({
            "model": self.model, "stream": False,
            "messages": [{"role": "user", "content": self._prompt(case)}],
        }).encode()
        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions", data=body,
            headers={"Content-Type": "application/json",
                     **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {})},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            text = json.loads(resp.read().decode())["choices"][0]["message"]["content"]
        start, end = text.find("["), text.rfind("]")
        if start < 0 or end < 0:
            return []
        try:
            tasks = json.loads(text[start:end + 1])
            return [t for t in tasks if isinstance(t, dict) and t.get("id")]
        except ValueError:
            return []
