# Overview

Q-Maple is a small framework for specification-driven placement guidance over heterogeneous quantum workflows.

The current prototype operates on an explicit Q-Maple workflow specification: a lightweight, placement-oriented intermediate representation in which execution regions and annotations are already provided. Those regions may come from manual authoring, domain knowledge, or an external preprocessing step. Q-Maple does not try to discover them automatically.

For each region, Q-Maple compares the region requirements against a set of backend capability profiles. The current prototype uses three capability groups:

- compute
- structural
- communication

The compute group captures basic resource fit such as qubit capacity and a rough depth budget. The structural group captures workflow-facing properties such as connectivity, feedback support, and scalability. The communication group captures simple latency and switching costs that matter when a region interacts with classical control or remote orchestration.

The output is placement guidance, not a scheduler. Q-Maple does not reserve devices, negotiate cloud access, or solve provider-side queueing. It also does not claim to infer the meaning of arbitrary quantum programs. It works on a modest problem statement: given a placement-oriented specification with predefined regions and a small set of backend profiles, which backends look most suitable for each region, and why.

In a broader toolchain, that specification could be authored manually or produced by workflow systems, C2/Q outputs, or future partition/decomposition tools. The current repository starts from the specification itself and focuses on the guidance layer.

This repository keeps the implementation deliberately small. The goal is to make the assumptions easy to inspect and adapt during early research work.
