"""Backend profile loading and lightweight validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_BACKEND_STYLES = {
    "superconducting",
    "neutral_atom",
    "trapped_ion",
    "photonic",
}
ALLOWED_MEASUREMENT_SPEEDS = {"low", "medium", "high"}
ALLOWED_CONNECTIVITY = {"all_to_all", "broadcast", "grid", "reconfigurable"}
ALLOWED_SCALABILITY = {"low", "medium", "high"}

REQUIRED_COMPUTE_FIELDS = {
    "max_qubits": int,
    "depth_budget": int,
    "measurement_speed": str,
}

REQUIRED_STRUCTURAL_FIELDS = {
    "connectivity": str,
    "supports_feedback": bool,
    "scalability": str,
}

REQUIRED_COMMUNICATION_FIELDS = {
    "classical_latency_ms": (int, float),
    "remote_link_penalty": (int, float),
}


@dataclass(frozen=True)
class BackendProfile:
    """A simple capability profile for a backend."""

    id: str
    display_name: str
    style: str
    compute: dict[str, Any]
    structural: dict[str, Any]
    communication: dict[str, Any]


def load_backend_profiles(path: str | Path) -> list[BackendProfile]:
    """Load backend profiles from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_backend_profiles(data)


def parse_backend_profiles(data: dict[str, Any]) -> list[BackendProfile]:
    """Validate and convert raw backend profile data."""

    if not isinstance(data, dict):
        raise ValueError("Backend profile file must be a JSON object.")

    backends_data = data.get("backends")
    if not isinstance(backends_data, list) or not backends_data:
        raise ValueError("Backend profile file must include a non-empty 'backends' list.")

    backends = [_parse_backend_profile(entry) for entry in backends_data]
    backend_ids = {backend.id for backend in backends}
    if len(backend_ids) != len(backends):
        raise ValueError("Backend identifiers must be unique.")

    return backends


def _parse_backend_profile(data: dict[str, Any]) -> BackendProfile:
    if not isinstance(data, dict):
        raise ValueError("Each backend profile must be a JSON object.")

    backend_id = _require_string(data, "id")
    display_name = _require_string(data, "display_name")
    style = _require_string(data, "style")
    if style not in ALLOWED_BACKEND_STYLES:
        allowed = ", ".join(sorted(ALLOWED_BACKEND_STYLES))
        raise ValueError(f"Backend '{backend_id}' style must be one of: {allowed}.")

    compute = _require_object(data, "compute")
    structural = _require_object(data, "structural")
    communication = _require_object(data, "communication")

    _validate_fields(backend_id, "compute", compute, REQUIRED_COMPUTE_FIELDS)
    _validate_fields(backend_id, "structural", structural, REQUIRED_STRUCTURAL_FIELDS)
    _validate_fields(backend_id, "communication", communication, REQUIRED_COMMUNICATION_FIELDS)

    if compute["max_qubits"] <= 0 or compute["depth_budget"] <= 0:
        raise ValueError(f"Backend '{backend_id}' compute limits must be greater than zero.")
    if compute["measurement_speed"] not in ALLOWED_MEASUREMENT_SPEEDS:
        allowed = ", ".join(sorted(ALLOWED_MEASUREMENT_SPEEDS))
        raise ValueError(f"Backend '{backend_id}' measurement_speed must be one of: {allowed}.")
    if structural["connectivity"] not in ALLOWED_CONNECTIVITY:
        allowed = ", ".join(sorted(ALLOWED_CONNECTIVITY))
        raise ValueError(f"Backend '{backend_id}' connectivity must be one of: {allowed}.")
    if structural["scalability"] not in ALLOWED_SCALABILITY:
        allowed = ", ".join(sorted(ALLOWED_SCALABILITY))
        raise ValueError(f"Backend '{backend_id}' scalability must be one of: {allowed}.")
    if communication["classical_latency_ms"] < 0:
        raise ValueError(f"Backend '{backend_id}' classical_latency_ms must be non-negative.")
    if not 0 <= communication["remote_link_penalty"] <= 1:
        raise ValueError(f"Backend '{backend_id}' remote_link_penalty must be in the range [0, 1].")

    return BackendProfile(
        id=backend_id,
        display_name=display_name,
        style=style,
        compute=compute,
        structural=structural,
        communication=communication,
    )


def _validate_fields(
    backend_id: str,
    section_name: str,
    values: dict[str, Any],
    required_fields: dict[str, Any],
) -> None:
    for field_name, expected_type in required_fields.items():
        field_value = values.get(field_name)
        if not isinstance(field_value, expected_type):
            if isinstance(expected_type, tuple):
                type_name = " or ".join(item.__name__ for item in expected_type)
            else:
                type_name = expected_type.__name__
            raise ValueError(
                f"Backend '{backend_id}' field '{section_name}.{field_name}' must be of type {type_name}."
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
