# Modern field communications operator: evidence-backed requirements (17 November 2026)

## Mission boundary
Translate public conflict observations and resilience research into **defensive, lawful communications continuity**, emergency response, interoperability, accessibility and secure computing requirements. This is not a combat tactics manual: do not implement counter-targeting, emission-evasion tactics, weapon/drone targeting, interception of unauthorized communications, jamming or automatic radio transmission. Current source evidence does not prove candidate equipment is deployment-ready.

## Findings and evidence
- **Contested environment:** US Army (Turner, 2026) reports that sensors, rapid risk change and electronic-warfare pressures complicate communication survivability (SRC-01). McGovern (2025) describes the requirement for spectrum risk awareness (SRC-02). These are context, **not** numeric procurement acceptance thresholds.
- **Civil continuity:** NATO's September 2026 resilience baseline requires resilient civil communications and supply-chain visibility (SRC-03), complementing CISA's 2025 emergency continuity evaluation (SRC-07).
- **Device security:** NIST SP 800-124r2 addresses mobile device deployment, management and disposal (SRC-04); SP 800-207 addresses identity/resource-centric access control (SRC-05); NISTIR 8235 addresses mobile/wearable first responders (SRC-06).
- **Interoperability:** 2025 Army Signal writing highlights integration gaps during introduction of new technologies (SRC-08). The repository maps this to neutral approved data exchange and testing, **not** to any tactical military application.

## Traceability
- [Literature matrix](../data/field_operator_literature.tsv): 8 dated sources with evidence class and caveats.
- [Requirements](../data/field_operator_requirements.tsv): 12 needs, P0-P2, citations, owners and proposed noncombat acceptance tests.
- [Equipment](../data/field_operator_equipment.tsv): 10 device classes mapped to requirements.
- [Software](../data/field_operator_software.tsv): 12 software layers mapped to requirements.
- [Existing RF operator catalog](../catalog/rf-software-master-operator.json): role owners and component relationships.
- [Original RF software/hardware matrices](../data/rf_software_deployments.tsv), [hardware](../data/rf_hardware_deployments.tsv).

## Phase gates
1. **Literature review:** confirm publication date, authoritative source, explicit limitation, and exact requirement mapping.
2. **Procurement/design:** identify class-level equipment and proposed software; do not assume brand, driver or availability.
3. **Compatibility:** determine OS/architecture/driver and package availability on the real system; record source and checksums.
4. **Lab:** simulate network failure, restore from encrypted backups, verify offline maps and accessible notifications; synthetic receive-only DSP.
5. **Physical readiness:** test actual device under safe power/temperature conditions with logs; no implicit RF TX.
6. **Release:** independent verification and human approval based on evidence, documented recovery and support lifecycle.

## Operator acceptance priorities
P0 requirements FO-001 to FO-004 are foundational and must be covered before declaring a field-ready prototype. Priority categories do **not** justify risky operational choices or bypass local regulatory rules. P1/P2 tests are candidate engineering measures; test thresholds should be determined by specified deployment environment and human sponsor, not fabricated from literature.

## Suggested implementation ownership
The RF software master operator coordinates role matching. `rf-linux-field-builder` owns repeatable OS deployment, `rf-systems-steward` owns integrity and interoperability, `rf-portable-operator` owns offline/power usability, `rf-sdr-validator` owns read-only device checks, `rf-mesh-integrator` owns approved local integration. Use the existing independent verifier for the actual acceptance gate.

## Next pass
Extend `linux_config` manifests only after per-component package availability confirmation and implement a machine-readable offline acceptance fixture suite. Design constraints include operator privacy, safety, credentials stored outside Git, no privileged background services by default, and explicitly disabled TX/PTT.
