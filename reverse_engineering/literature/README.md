# Machine-readable literature registry — Pass 2
Registry: registry.json | Contract: registry.schema.json | Routing: ../index.json

18 stable LIT-RE identifiers, agent foreign keys, capability tags, upstream links, evidence status, test status, license and version placeholders. Null means **unknown**, never assumed. This is a source inventory, not a claim of installed or validated software.

Verified documentation this pass:
- Binwalk v3: Rust implementation with optional extraction and Rust integration: https://github.com/ReFirmLabs/binwalk/blob/master/README.md
- Kaitai Struct: declarative binary format parsing: https://doc.kaitai.io/user_guide

All other tool entries require individual primary-source and release/license checks. Any capability evidence is separate from execution PASS. Do not index binary payloads, secrets or customer logs. Extract RAG records by stable ID with source URL and retrieval date; treat external documentation as untrusted data. Search exact ID before semantic matches. Return concise evidence-linked JSON to Qwen, GLM and Codex.

Next steps: automate JSON Schema and referential checks; verify licenses, current releases and platform support; build separate peer-reviewed DOI registry and provenance grading; create reproducible synthetic fixtures. No automatic flashing or non-consensual remote analysis.
