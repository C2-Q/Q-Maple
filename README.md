# Q-Maple

Q-Maple is a small research prototype for capability-driven placement guidance over heterogeneous quantum workflows.

It reads:

1. a workflow specification
2. backend capability profiles
3. a simple cost model

It produces placement guidance for each predefined execution region in the workflow, along with short explanations.

This repository is meant to support a positioning paper and early experimentation. It is intentionally small.

## Workflow At A Glance

![Q-Maple workflow overview](docs/figures/workflow_overview_readme.png)

## What Q-Maple Is

Q-Maple focuses on workflow-oriented placement guidance.

- It compares execution regions against backend capability profiles.
- It uses a small transparent scoring model.
- It returns interpretable recommendations rather than opaque optimizer output.

## What Q-Maple Is Not

- It does not solve provider-side scheduling.
- It does not perform full automatic semantic partitioning.
- Q-Maple currently operates on workflow specifications with predefined execution regions.
- Automatic semantic partitioning is out of scope for this initial version.
- It is not a production control plane or cloud integration layer.

## Current Scope

The current repository is meant to support a positioning paper and early experimentation. It contains one minimal demo, one example workflow, one example backend profile file, and a small smoke test.

## Repository Layout

```text
qmaple/
  README.md
  LICENSE
  CONTRIBUTING.md
  CITATION.cff
  requirements.txt
  .gitignore
  docs/
  examples/
  qmaple/
  outputs/
  tests/
```

Key files:

- `examples/workflow_example.json`: predefined execution regions for a small workflow.
- `examples/backend_profiles_example.json`: four example backend profiles.
- `qmaple/placement_engine.py`: ranking and recommendation logic.
- `qmaple/demo.py`: example entry point.
- `outputs/sample_result.json`: committed sample output from the demo.

## Example Input

The example workflow contains three regions:

- a compute region
- a measure-feedback region
- a scalable-compute region

The example backend file contains four illustrative backend styles:

- `SC` for superconducting
- `NA` for neutral atom
- `TI` for trapped ion
- `PH` for photonic

## Example Output

Running the demo produces a JSON file with one recommendation per region and a ranked candidate list for each region. A shortened example looks like this:

```json
{
  "workflow_id": "adaptive_calibration_demo",
  "recommendations": [
    {
      "region_id": "r1_compute",
      "recommended_backend": "SC",
      "reason": "SC offers a strong fit for the qubit and depth request and aligns with the preferred grid connectivity."
    }
  ]
}
```

The example scores and explanations are stylized comparative guidance from reference profiles, not hardware benchmarking or execution measurements.

See `examples/expected_output.md` and `outputs/sample_result.json` for the committed example.

## How To Run The Demo

Q-Maple targets Python 3.10+ and currently uses only the Python standard library.

```bash
python -m qmaple.demo
```

This command reads the example inputs and writes `outputs/sample_result.json`.

To run the smoke test:

```bash
python -m unittest discover -s tests -v
```

## Early Prototype Note

This is an early research prototype. The code is meant to stay readable and easy to inspect. The repository keeps the scope narrow on purpose.
