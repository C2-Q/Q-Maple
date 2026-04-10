"""Placement guidance over predefined workflow regions."""

from __future__ import annotations

from .backend_profile import BackendProfile
from .cost_model import build_reason, score_region_backend
from .workflow_spec import WorkflowSpec


def generate_placement_guidance(
    workflow: WorkflowSpec, backends: list[BackendProfile]
) -> dict[str, object]:
    """Produce ranked backend guidance for each workflow region."""

    recommendations: list[dict[str, object]] = []

    for region in workflow.regions:
        scored_candidates = []

        for backend in backends:
            score = score_region_backend(region, backend)
            scored_candidates.append((backend, score))

        scored_candidates.sort(key=lambda item: (-item[1].total_score, item[0].id))
        ranked_candidates = [
            {
                "backend_id": backend.id,
                "style": backend.style,
                **score.to_dict(),
            }
            for backend, score in scored_candidates
        ]
        best_backend, best_score = scored_candidates[0]

        recommendations.append(
            {
                "region_id": region.id,
                "region_label": region.label,
                "region_type": region.region_type,
                "recommended_backend": best_backend.id,
                "reason": build_reason(region, best_backend, best_score),
                "candidates": ranked_candidates,
            }
        )

    return {
        "workflow_id": workflow.workflow_id,
        "description": workflow.description,
        "assumptions": [
            "Execution regions are assumed to be predefined in the workflow specification.",
            "Scores are comparative guidance from stylized profiles, not provider-side schedules, reservations, or execution measurements.",
        ],
        "recommendations": recommendations,
    }
