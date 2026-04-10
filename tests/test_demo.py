"""Smoke tests for the example-driven demo."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from qmaple.backend_profile import load_backend_profiles
from qmaple.demo import run_demo
from qmaple.workflow_spec import load_workflow_spec

REPO_ROOT = Path(__file__).resolve().parents[1]


class DemoSmokeTest(unittest.TestCase):
    def test_example_files_and_demo(self) -> None:
        workflow = load_workflow_spec(REPO_ROOT / "examples" / "workflow_example.json")
        backends = load_backend_profiles(REPO_ROOT / "examples" / "backend_profiles_example.json")

        self.assertEqual(workflow.workflow_id, "adaptive_calibration_demo")
        self.assertEqual(len(workflow.regions), 3)
        self.assertEqual(len(backends), 4)

        with TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "result.json"
            result = run_demo(output_path=output_path, emit_summary=False)

            self.assertTrue(output_path.exists())
            written_result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written_result["workflow_id"], result["workflow_id"])
            self.assertGreaterEqual(len(written_result["recommendations"]), 1)
            self.assertIn("recommended_backend", written_result["recommendations"][0])


if __name__ == "__main__":
    unittest.main()
