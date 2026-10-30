# R5 — Catalog assurance gate

Run `python3 -m agent_toolset.catalog_validator --repo .` and `python3 -m unittest discover -s tests -v`.

This offline validator checks role and stage identifiers, reporting parents, catalog resource names, stage dependencies, cycles, skill entrypoints, and metadata presence. It does not execute skill text and never grants release authorization. Missing or inconsistent references produce FAIL. Follow-up: add this gate to CI after review, and add adversarial JSON type fixtures.

**Coordination:** isolated branch; avoid modifying Codex-owned R3/R4 cache and evaluation modules.