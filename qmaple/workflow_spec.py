"""Workflow specification loading and lightweight validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_REGION_ANNOTATIONS = {
    "required_qubits": int,
    "circuit_depth": int,
    "requires_fast_feedback": bool,
    "preferred_connectivity": str,
    "scalability_target": str,
    "shot_volume": int,
}

ALLOWED_CONNECTIVITY = {"all_to_all", "broadcast", "grid", "reconfigurable"}
ALLOWED_SCALABILITY = {"low", "medium", "high"}


@dataclass(frozen=True)
class WorkflowRegion:
    """A predefined execution region in a workflow."""

    id: str
    label: str
    region_type: str
    dependencies: list[str]
    annotations: dict[str, Any]


@dataclass(frozen=True)
class WorkflowSpec:
    """A workflow-level container for execution regions."""

    workflow_id: str
    description: str
    annotations: dict[str, Any]
    regions: list[WorkflowRegion]


def load_workflow_spec(path: str | Path) -> WorkflowSpec:
    """Load a workflow specification from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_workflow_spec(data)


def parse_workflow_spec(data: dict[str, Any]) -> WorkflowSpec:
    """Validate and convert raw workflow data."""

    if not isinstance(data, dict):
        raise ValueError("Workflow specification must be a JSON object.")

    workflow_id = _require_string(data, "workflow_id")
    description = _require_string(data, "description")
    annotations = _require_object(data, "annotations")
    regions_data = data.get("regions")
    if not isinstance(regions_data, list) or not regions_data:
        raise ValueError("Workflow specification must include a non-empty 'regions' list.")

    regions = [_parse_region(region_data) for region_data in regions_data]
    region_ids = {region.id for region in regions}
    if len(region_ids) != len(regions):
        raise ValueError("Region identifiers must be unique.")

    for region in regions:
        missing_dependencies = [dependency for dependency in region.dependencies if dependency not in region_ids]
        if missing_dependencies:
            raise ValueError(
                f"Region '{region.id}' depends on unknown regions: {', '.join(missing_dependencies)}."
            )

    return WorkflowSpec(
        workflow_id=workflow_id,
        description=description,
        annotations=annotations,
        regions=regions,
    )


def _parse_region(data: dict[str, Any]) -> WorkflowRegion:
    if not isinstance(data, dict):
        raise ValueError("Each region must be a JSON object.")

    region_id = _require_string(data, "id")
    label = _require_string(data, "label")
    region_type = _require_string(data, "region_type")
    dependencies = data.get("dependencies", [])
    if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
        raise ValueError(f"Region '{region_id}' must define 'dependencies' as a list of strings.")

    annotations = _require_object(data, "annotations")
    for key, expected_type in REQUIRED_REGION_ANNOTATIONS.items():
        value = annotations.get(key)
        if not isinstance(value, expected_type):
            raise ValueError(
                f"Region '{region_id}' annotation '{key}' must be of type {expected_type.__name__}."
            )

    for key in ("required_qubits", "circuit_depth", "shot_volume"):
        if annotations[key] <= 0:
            raise ValueError(f"Region '{region_id}' annotation '{key}' must be greater than zero.")

    if annotations["preferred_connectivity"] not in ALLOWED_CONNECTIVITY:
        allowed = ", ".join(sorted(ALLOWED_CONNECTIVITY))
        raise ValueError(f"Region '{region_id}' preferred_connectivity must be one of: {allowed}.")

    if annotations["scalability_target"] not in ALLOWED_SCALABILITY:
        allowed = ", ".join(sorted(ALLOWED_SCALABILITY))
        raise ValueError(f"Region '{region_id}' scalability_target must be one of: {allowed}.")

    return WorkflowRegion(
        id=region_id,
        label=label,
        region_type=region_type,
        dependencies=dependencies,
        annotations=annotations,
    )


def _require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Expected a non-empty string for '{key}'.")
    return value


def _require_object(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Expected '{key}' to be a JSON object.")
    return value
