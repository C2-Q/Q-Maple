"""Focused tests for workflow and backend loaders."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from qmaple.backend_profile import load_backend_profiles, parse_backend_profiles
from qmaple.workflow_spec import load_workflow_spec, parse_workflow_spec

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


class WorkflowSpecLoaderTest(unittest.TestCase):
    def test_load_workflow_spec_reads_example_regions(self) -> None:
        workflow = load_workflow_spec(EXAMPLES_DIR / "workflow_example.json")

        self.assertEqual(workflow.workflow_id, "adaptive_calibration_demo")
        self.assertEqual([region.id for region in workflow.regions], ["r1_compute", "r2_feedback", "r3_scale"])
        self.assertEqual(workflow.regions[1].dependencies, ["r1_compute"])

    def test_parse_workflow_spec_rejects_unknown_dependencies(self) -> None:
        payload = json.loads((EXAMPLES_DIR / "workflow_example.json").read_text(encoding="utf-8"))
        payload = copy.deepcopy(payload)
        payload["regions"][1]["dependencies"] = ["missing_region"]

        with self.assertRaisesRegex(ValueError, "unknown regions"):
            parse_workflow_spec(payload)


class BackendProfileLoaderTest(unittest.TestCase):
    def test_load_backend_profiles_reads_example_backends(self) -> None:
        backends = load_backend_profiles(EXAMPLES_DIR / "backend_profiles_example.json")

        self.assertEqual([backend.id for backend in backends], ["SC", "NA", "TI", "PH"])
        self.assertEqual(backends[0].style, "superconducting")
        self.assertIn("communication", backends[0].__dict__)

    def test_parse_backend_profiles_rejects_invalid_penalty_range(self) -> None:
        payload = json.loads((EXAMPLES_DIR / "backend_profiles_example.json").read_text(encoding="utf-8"))
        payload = copy.deepcopy(payload)
        payload["backends"][0]["communication"]["remote_link_penalty"] = 1.5

        with self.assertRaisesRegex(ValueError, "remote_link_penalty"):
            parse_backend_profiles(payload)


if __name__ == "__main__":
    unittest.main()
