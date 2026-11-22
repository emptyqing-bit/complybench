"""Benchmark case loading for ComplyBench."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Case:
    id: str
    incident_type: str
    severity: int
    roles: tuple[str, ...]
    required_tasks: tuple[str, ...]
    max_deadline_min: int = 60
    notes: str = ""

    @classmethod
    def from_dict(cls, raw: dict) -> "Case":
        return cls(
            id=raw["id"],
            incident_type=raw["incident_type"],
            severity=int(raw.get("severity", 1)),
            roles=tuple(raw["roles"]),
            required_tasks=tuple(raw["required_tasks"]),
            max_deadline_min=int(raw.get("max_deadline_min", 60)),
            notes=raw.get("notes", ""),
        )


def load_cases(path: str | Path) -> list[Case]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Case.from_dict(item) for item in raw["cases"]]
