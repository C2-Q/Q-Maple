"""Minimal demo entry point for the Q-Maple prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .backend_profile import load_backend_profiles
from .placement_engine import generate_placement_guidance
from .workflow_spec import load_workflow_spec

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"
OUTPUTS_DIR = REPO_ROOT / "outputs"


def run_demo(
    workflow_path: Path | None = None,
    backend_path: Path | None = None,
    output_path: Path | None = None,
    emit_summary: bool = True,
) -> dict[str, Any]:
    """Run the example placement flow and write the result JSON."""

    workflow = load_workflow_spec(workflow_path or EXAMPLES_DIR / "workflow_example.json")
    backends = load_backend_profiles(backend_path or EXAMPLES_DIR / "backend_profiles_example.json")
    result = generate_placement_guidance(workflow, backends)

    destination = output_path or OUTPUTS_DIR / "sample_result.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if emit_summary:
        _print_summary(result)
    return result


def _print_summary(result: dict[str, Any]) -> None:
    print("Q-Maple demo")
    print(f"Workflow: {result['workflow_id']}")
    print("Recommendations:")
    for recommendation in result["recommendations"]:
        print(
            f"- {recommendation['region_id']} ({recommendation['region_type']}): "
            f"{recommendation['recommended_backend']} - {recommendation['reason']}"
        )


if __name__ == "__main__":
    run_demo()
