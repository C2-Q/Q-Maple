"""Small deterministic tests for scoring and placement guidance."""

from __future__ import annotations

import unittest
from pathlib import Path

from qmaple.backend_profile import load_backend_profiles
from qmaple.cost_model import build_reason, score_region_backend
from qmaple.placement_engine import generate_placement_guidance
from qmaple.workflow_spec import load_workflow_spec

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


class CostModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        workflow = load_workflow_spec(EXAMPLES_DIR / "workflow_example.json")
        backends = load_backend_profiles(EXAMPLES_DIR / "backend_profiles_example.json")
        cls.feedback_region = next(region for region in workflow.regions if region.id == "r2_feedback")
        cls.scale_region = next(region for region in workflow.regions if region.id == "r3_scale")
        cls.backends = {backend.id: backend for backend in backends}

    def test_feedback_region_prefers_superconducting_over_neutral_atom(self) -> None:
        sc_score = score_region_backend(self.feedback_region, self.backends["SC"])
        na_score = score_region_backend(self.feedback_region, self.backends["NA"])

        self.assertGreater(sc_score.total_score, na_score.total_score)
        self.assertAlmostEqual(sc_score.compute_fit, 1.0, places=3)
        self.assertAlmostEqual(sc_score.communication_penalty, 0.172, places=3)

    def test_reason_mentions_feedback_support_for_feedback_region(self) -> None:
        sc_score = score_region_backend(self.feedback_region, self.backends["SC"])
        reason = build_reason(self.feedback_region, self.backends["SC"], sc_score)

        self.assertIn("supports feedback-oriented execution", reason)


class PlacementEngineTest(unittest.TestCase):
    def test_example_workflow_recommendations_match_committed_demo(self) -> None:
        workflow = load_workflow_spec(EXAMPLES_DIR / "workflow_example.json")
        backends = load_backend_profiles(EXAMPLES_DIR / "backend_profiles_example.json")

        result = generate_placement_guidance(workflow, backends)
        recommendations = {
            item["region_id"]: item["recommended_backend"] for item in result["recommendations"]
        }

        self.assertEqual(
            recommendations,
            {
                "r1_compute": "SC",
                "r2_feedback": "SC",
                "r3_scale": "NA",
            },
        )

    def test_ranked_candidates_are_sorted_by_score(self) -> None:
        workflow = load_workflow_spec(EXAMPLES_DIR / "workflow_example.json")
        backends = load_backend_profiles(EXAMPLES_DIR / "backend_profiles_example.json")

        result = generate_placement_guidance(workflow, backends)
        candidates = result["recommendations"][0]["candidates"]
        scores = [candidate["total_score"] for candidate in candidates]

        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
