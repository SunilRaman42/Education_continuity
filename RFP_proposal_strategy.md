
# Strategy Proposal: Data-Driven Education Continuity for EBI

**To:** Education Bridge Initiative (EBI)
**From:** Sunil Raman
**Date:** May 27, 2026

---

## Executive Summary

Reduce time-to-understand cross-regional education risk from weeks to hours by delivering an open-data pipeline, an explainable vulnerability score, and a human-in-the-loop dashboard. Outcomes: (1) decision-ready vulnerability snapshots across all operating provinces; (2) measurable early-warning alerts to prioritize emergency support; (3) full handover and capacity building so EBI operates the system independently.

## How This Supports EBI (headline outcomes)
- **Faster Decisions:** Daily/weekly vulnerability snapshots enable leadership to reallocate resources within planning cycles rather than after crises.  
- **Broader Coverage:** HDX-first sourcing with OSM fallback gives near-complete geographic coverage where registries are incomplete.  
- **Actionable Outputs:** Explainable risk scores, one-click drilldowns to province→school, and AI-drafted plain-language briefs (validated by field focal points).
 - **Faster Decisions:** Daily/weekly vulnerability snapshots enable leadership to reallocate resources within planning cycles rather than after crises.  
 - **Proven Indicator (EVI):** The repository implements an Education Vulnerability Index (EVI) used in the prototype to surface province-level risk and rank schools by exposure.  
 - **Broader Coverage & Proven Fallbacks:** HDX-first sourcing with an explicit ACLED→official admin mapping and OSM fallback is already implemented in the prototype to improve geographic coverage.  
 - **Actionable Outputs:** Explainable risk scores (EVI), map drilldowns to school infrastructure, and draft AI summaries — all designed to be validated by field focal points.

## Alignment to RFP Evaluation Criteria
- **Relevance & Innovation:** Connects conflict metrics directly to school-level risk and intervention choices (rapid response vs. structural support).  
- **Data-driven Approach:** Automated ingestion, harmonization and geospatial modelling producing a harmonized dataset and provenance flags.  
- **Use of Technology (AI):** Bounded AI tasks (see below) that increase speed while preserving human judgment.  
- **Feasibility & Impact:** Phased delivery with prototype → MVP → production milestones and acceptance criteria.  
- **Scalability & Adaptability:** Modular pipeline and indicator-agnostic scoring to add countries or new metrics without rework.

## AI: Specific Roles and Safeguards
- **Tasks:** data normalization, anomaly detection (early-warning), explainable risk-scoring model, auto-draft briefs summarizing provincial changes.  
- **Safeguards:** All AI outputs are labeled, include confidence bands, show top contributing indicators, and require focal-point sign-off before operational use. Audit logs retained for every automated decision.  
Note: the repo contains example LLM-generated narrative drafts; in the proposal these remain explicitly draft outputs that require focal-point validation before operational use.

## Methodology (high level)
- **Data ingestion:** Prioritise HDX registries → national registries → OSM fallback. Automated validation rules flag gaps.  
- **Harmonisation:** Geocode reconciliation, deduplication, and provenance tagging.  
- **Risk model:** Combine conflict proximity, conflict recurrence (10-year window), school density, population exposure to produce an explainable vulnerability score.  
- **Field integration:** Field Notes and validation workflow embedded in dashboard for local corrections and overrides.
Notes from the repository:
- The prototype's methodology (see `docs/methodology.md`) computes a composite vulnerability score per admin1 region (EVI) combining ACLED conflict indicators with national education indicators; a documented limitation is that education data is national-level only for many countries, which we surface as an uncertainty in the dashboard.  
- The pipeline is country-agnostic; scripts under `scripts/` (e.g. `05_1_calculate_hybrid_vulnerability.py`, `05_build_analysis.py`) demonstrate the ingest→transform→export steps used in the prototype.

## Deliverables, Timeline & Acceptance Criteria
- **Prototype Central Analysis Hub — 8 weeks:** interactive dashboard with province-level view, one-country demo; acceptance: leadership demo and sign-off.  
- **MVP Hub + Harmonized Dataset — 20 weeks:** multi-country coverage, automated pipeline, explainable scoring; acceptance: 90% geolocation match rate vs registry sample and documented workflow.  
- **Capacity & Handover — weeks 18–22:** methodology guide, training workshops, runbooks; acceptance: trained focal points can run pipeline end-to-end and produce weekly briefs.  

## KPIs and Success Metrics
- **Time to synthesis:** reduce assembly time from weeks to <24 hours for cross-regional snapshot.  
- **Coverage:** % provinces with actionable data (target 90% in scoped countries).  
- **Data quality:** geolocation match rate ≥ 90% on validation sample.  
- **Alert precision:** initial AUC/precision metrics for early-warning (baseline to be established during pilot).

## UX for Non-Technical Users
The existing prototype UI (see `index.html`) is map-first: users select a province on the map to view its EVI and school infrastructure. For the RFP deliverable we will prioritise a single landing headline metric (top 3 provinces) but keep the map-first drilldown UX because it aligns with field workflows and is already implemented.

Key implemented UX behaviours to preserve:
- Map selection shows province EVI and school list.  
- Admin name mapping (ACLED→official) is applied so conflict events align with national boundaries (`artifacts/admin_mapping.json`).  
- ACLED fallback indicators and small helper notes appear where data are sparse in the prototype (`index.html` contains the ACLED fallback UI logic).

If you prefer an alternative landing (headline-first instead of map-first), I will update the prototype copy and the proposal text to reflect that preference.

## Existing prototype & repo features to incorporate
- `index.html`: interactive map UI, province drilldowns, EVI display.  
- `docs/methodology.md`: calculation details and data limitations (national-level education data caveat).  
- `scripts/05_1_calculate_hybrid_vulnerability.py`, `05_build_analysis.py`: pipeline examples for ingest and scoring.  
- `artifacts/admin_mapping.json`, `artifacts/schools.geojson`: admin mapping and school geometry used by the prototype.  
- Links in current repo to interactive visualisations and experiment pages (prototype available for demonstration).

## Data Governance & Do-No-Harm
- Use only open/public data unless otherwise authorised. Minimise identifiable information, apply location obfuscation where disclosure risk is high, and include community engagement steps for sensitive contexts.

## Risks & Mitigations
- **Data lag/coverage:** Mitigate via fallback chain and explicit uncertainty flags.  
- **False positives/negatives:** Mitigate with human-in-the-loop validation and conservative alert thresholds during pilot.  
- **Operational sustainability:** Deliver runbooks and training; recommend 3-month support window post-handover.

## Next Steps & Offerings
- Shortlist demo: run the prototype for one EBI country and present findings within 4 weeks of contract start.  
- On request: provide detailed budget and country-specific timeline for shortlisted applicants.

---

Prototype and past work are available for demonstration on request; all AI-generated summaries will be clearly labeled and auditable.

## Burkina Faso — Narrative Case Study (what the prototype shows)
The repository includes a complete Burkina Faso pilot that demonstrates how the EVI and the prototype UI translate data into operational choices. Key narrative points we will fold into the proposal:

- **Problem statement, grounded in local reality:** Field teams report persistent closures and access barriers in regions such as Sahel and Est; the prototype quantifies that reality by ranking provinces and schools using the EVI ([STRATEGY.md](STRATEGY.md#L1-L15)).  
- **What we found:** The EVI ranks provinces by combined conflict exposure and education fragility; provinces like **Soum**, **Yatenga** and parts of the **Sahel** consistently appear in the highest vulnerability tier in the pilot outputs (see the prototype map and province drilldowns in `index.html`).  
- **School-level insight:** The schools view provides a ranked list of infrastructure exposed within proximity thresholds (e.g., within 10km of recurring conflict hotspots), enabling targeted interventions for those facilities — this is implemented in `schools/index.html` and visible in the `artifacts/schools.geojson`.  
- **Operational recommendation tied to findings:** For BFA we recommend a two-track response: (1) immediate rapid-support for high-exposure schools within acute hotspots (short-term: security-sensitive repairs, community safety measures); (2) structural resilience investments in consistently high-EVI provinces (medium-term: teacher retention incentives, reconstruction, mobile learning interventions). The STRATEGY.md framing already articulates this shift from reactive to structural resilience.  
- **Caveats to communicate clearly in the proposal:** The methodology documentation notes that national-level education indicators are applied uniformly across subnational units where disaggregated data are unavailable; the dashboard surfaces this uncertainty so decisions remain evidence-informed rather than overconfident ([docs/methodology.md](docs/methodology.md#L32-L36)).

If you want, I will now incorporate a 300–500 word narrative case study into `RFP_proposal_strategy.md` that weaves these BFA findings into a persuasive story (problem → evidence → decision impact → recommended interventions and KPIs). Shall I add that full narrative paragraph now? 

## Narrative Case Study (300–500 words)
Burkina Faso presents a clear example of how data-driven prioritisation changes what is possible on the ground. Field teams in Sahel and Est routinely report school closures, teacher shortages, and disrupted learning; those observations are real but fragmented. The prototype aggregates those observations with open conflict data to produce an Education Vulnerability Index (EVI) that makes the pattern visible and actionable. In the BFA pilot, provinces such as Soum, Yatenga and parts of Sahel repeatedly score in the highest vulnerability tier — not only because of acute spikes in conflict, but because historical recurrence and low school density create a structural inability to absorb shocks. At the school level, the dashboard flags facilities within 10km of recurring hotspots, producing a ranked list that lets a program manager distinguish where rapid repairs or community safety measures will buy the most time versus where systemic investments (teacher incentives, reconstruction, alternative delivery modalities) are required.

This is a strategic shift. Rather than treating every closure as an isolated incident, EBI can use the EVI to separate urgent triage from long‑term resilience. Practically, this means short triage missions to secure and repair a small number of high‑exposure schools while channeling longer funding cycles and monitoring to provinces with persistently high EVI. The pilot also highlights important caveats: national‑level education indicators are used where subnational data are unavailable, which can bias within‑country comparisons; the prototype surfaces this uncertainty so program teams know which recommendations need stronger ground‑truthing. AI is used only to synthesize briefs and flag anomalies; every AI‑derived recommendation is presented with contributing indicators and a required focal‑point validation step.

Deliverables tied to the narrative are concrete: a one‑country prototype within 8 weeks that produces an operational priority list, an MVP covering additional countries by 20 weeks, and a handover package that trains field coordinators to validate and act on the EVI outputs. KPIs for BFA pilot success include reduction in time‑to‑synthesis (from weeks to <24 hours), a validated list of high‑priority schools with ground‑truth confirmation, and a documented decision trail for each operational intervention. The narrative and the pilot together show not just what the data reveals, but how EBI can change its approach to protect learning at scale.
