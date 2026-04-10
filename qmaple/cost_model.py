"""Transparent scoring utilities for backend placement guidance."""

from __future__ import annotations

from dataclasses import dataclass

from .backend_profile import BackendProfile
from .workflow_spec import WorkflowRegion

MEASUREMENT_SPEED_SCORES = {
    "low": 0.4,
    "medium": 0.7,
    "high": 1.0,
}

SCALABILITY_LEVELS = {
    "low": 1,
    "medium": 2,
    "high": 3,
}

CONNECTIVITY_MATCH = {
    "all_to_all": {"all_to_all": 1.0, "reconfigurable": 0.8, "grid": 0.6, "broadcast": 0.45},
    "broadcast": {"broadcast": 1.0, "reconfigurable": 0.7, "grid": 0.6, "all_to_all": 0.6},
    "grid": {"grid": 1.0, "reconfigurable": 0.8, "all_to_all": 0.65, "broadcast": 0.5},
    "reconfigurable": {"reconfigurable": 1.0, "all_to_all": 0.75, "grid": 0.65, "broadcast": 0.5},
}


@dataclass(frozen=True)
class ScoreBreakdown:
    """A region-backend compatibility score with interpretable components."""

    compute_fit: float
    structural_fit: float
    communication_penalty: float
    total_score: float

    def to_dict(self) -> dict[str, float]:
        """Return rounded values for output."""

        return {
            "compute_fit": round(self.compute_fit, 2),
            "structural_fit": round(self.structural_fit, 2),
            "communication_penalty": round(self.communication_penalty, 2),
            "total_score": round(self.total_score, 2),
        }


def score_region_backend(region: WorkflowRegion, backend: BackendProfile) -> ScoreBreakdown:
    """Score how well a backend fits a workflow region."""

    compute_fit = _compute_fit(region, backend)
    structural_fit = _structural_fit(region, backend)
    communication_penalty = _communication_penalty(region, backend)
    total_score = (0.5 * compute_fit) + (0.35 * structural_fit) - (0.15 * communication_penalty)

    return ScoreBreakdown(
        compute_fit=compute_fit,
        structural_fit=structural_fit,
        communication_penalty=communication_penalty,
        total_score=total_score,
    )


def build_reason(region: WorkflowRegion, backend: BackendProfile, score: ScoreBreakdown) -> str:
    """Generate a short explanation for a placement recommendation."""

    notes: list[str] = []
    required_qubits = region.annotations["required_qubits"]
    circuit_depth = region.annotations["circuit_depth"]
    preferred_connectivity = region.annotations["preferred_connectivity"]
    scalability_target = region.annotations["scalability_target"]
    requires_fast_feedback = region.annotations["requires_fast_feedback"]

    if backend.compute["max_qubits"] >= required_qubits and backend.compute["depth_budget"] >= circuit_depth:
        notes.append("offers a strong fit for the qubit and depth request")
    elif backend.compute["max_qubits"] >= required_qubits:
        notes.append("offers a workable qubit fit with limited depth headroom")
    else:
        notes.append("offers the closest compute fit among the current candidates")

    if backend.structural["connectivity"] == preferred_connectivity:
        notes.append(f"aligns with the preferred {preferred_connectivity} connectivity")
    elif requires_fast_feedback and backend.structural["supports_feedback"]:
        notes.append("supports feedback-oriented execution")
    elif scalability_target == "high" and backend.structural["scalability"] == "high":
        notes.append("aligns with the high scalability target")
    elif score.communication_penalty <= 0.25:
        notes.append("keeps communication overhead low")

    if requires_fast_feedback and backend.compute["measurement_speed"] == "high":
        notes.append("offers fast measurement handling")

    reason = f"{backend.id} {notes[0]}"
    if len(notes) > 1:
        reason += f" and {notes[1]}"
    reason += "."

    if score.communication_penalty >= 0.6:
        reason += " Communication overhead is still a visible tradeoff."

    return reason


def _compute_fit(region: WorkflowRegion, backend: BackendProfile) -> float:
    required_qubits = region.annotations["required_qubits"]
    circuit_depth = region.annotations["circuit_depth"]
    requires_fast_feedback = region.annotations["requires_fast_feedback"]

    qubit_fit = min(backend.compute["max_qubits"] / required_qubits, 1.0)
    depth_fit = min(backend.compute["depth_budget"] / circuit_depth, 1.0)

    if requires_fast_feedback or region.region_type == "measure_feedback":
        measurement_speed = backend.compute["measurement_speed"]
        measurement_fit = MEASUREMENT_SPEED_SCORES[measurement_speed]
        return (qubit_fit + depth_fit + measurement_fit) / 3.0

    return (qubit_fit + depth_fit) / 2.0


def _structural_fit(region: WorkflowRegion, backend: BackendProfile) -> float:
    preferred_connectivity = region.annotations["preferred_connectivity"]
    requires_fast_feedback = region.annotations["requires_fast_feedback"]
    scalability_target = region.annotations["scalability_target"]

    connectivity_fit = CONNECTIVITY_MATCH[preferred_connectivity][backend.structural["connectivity"]]
    feedback_fit = 1.0
    if requires_fast_feedback:
        feedback_fit = 1.0 if backend.structural["supports_feedback"] else 0.0

    backend_scale = SCALABILITY_LEVELS[backend.structural["scalability"]]
    target_scale = SCALABILITY_LEVELS[scalability_target]
    scalability_fit = 1.0 if backend_scale >= target_scale else backend_scale / target_scale

    return (connectivity_fit + feedback_fit + scalability_fit) / 3.0


def _communication_penalty(region: WorkflowRegion, backend: BackendProfile) -> float:
    requires_fast_feedback = region.annotations["requires_fast_feedback"]
    latency_penalty = min(backend.communication["classical_latency_ms"] / 25.0, 1.0)
    remote_link_penalty = min(float(backend.communication["remote_link_penalty"]), 1.0)

    if requires_fast_feedback:
        return (0.7 * latency_penalty) + (0.3 * remote_link_penalty)

    return (0.4 * latency_penalty) + (0.6 * remote_link_penalty)
