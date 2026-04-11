# Workflow Specification

A Q-Maple workflow specification is the input document that Q-Maple uses to describe a heterogeneous workflow at the region level. In the current prototype, this specification serves as a lightweight, placement-oriented intermediate representation rather than a user-facing workflow DSL.

## Execution Regions

An execution region is a placement unit within the modeled workflow. In this repository, each region has:

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

## Upstream Sources

The current repository starts from the Q-Maple specification itself. In a broader toolchain, such specifications could come from:

- manual authoring
- workflow systems
- C2/Q outputs
- future partition or decomposition tools

Those upstream sources are not implemented here. This prototype focuses on the explicit input representation and the downstream placement-guidance logic.
