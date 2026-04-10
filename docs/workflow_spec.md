# Workflow Specification

A workflow specification is the input document that Q-Maple uses to describe a heterogeneous quantum workflow at the region level.

## Execution Regions

An execution region is a part of the workflow that is treated as a placement unit. In this repository, each region has:

- an `id`
- a short `label`
- a `region_type`
- a list of `dependencies`
- an `annotations` object

Dependencies describe the region-level ordering relationship. They do not model low-level scheduling.

## Annotations

Annotations provide lightweight hints that the placement model can interpret. The example schema uses:

- `required_qubits`
- `circuit_depth`
- `requires_fast_feedback`
- `preferred_connectivity`
- `scalability_target`
- `shot_volume`

The current prototype does not require a large ontology. The annotations are deliberately small and readable.

## Important Boundary

Q-Maple assumes that execution regions are already given in the workflow specification. They may be manually defined by the workflow author or provided by another tool. They are not automatically discovered by this repository.

That boundary matters. Q-Maple is about placement guidance over regions, not automatic semantic partitioning of quantum programs.
