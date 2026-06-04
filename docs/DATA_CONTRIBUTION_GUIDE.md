# Data Limitations & Field Contribution Guide

This document outlines the current data gaps within the Education Continuity pipeline, the structural reasons for these limitations, and how field teams can contribute data to improve the granularity and accuracy of the Education Vulnerability Index (EVI).

## 1. Current Data Gaps & "Proxy" Logic

The pipeline currently relies on several "proxies" where granular, real-time data is unavailable:

### A. Provincial Education Indicators (GER/OOS)
*   **Current State:** The system applies **National averages** (from UNESCO/World Bank) to all provinces. While the *population* numbers scale based on local density, the *percentage* (e.g., 72% Enrollment) is uniform across the country.
*   **The Gap:** In reality, a conflict-affected province like Soum likely has a much lower GER than a stable province like Kadiogo.
*   **How to Improve:** Add rows to `data/clean/education/master_education.csv` with the `region` column set to the specific Province name instead of "National".

### B. Real-Time School Status
*   **Current State:** School locations are largely based on historical datasets (HDX). 
*   **The Gap:** A school marked as "Functional" in a 2021 dataset may be closed or physically destroyed today.
*   **How to Improve:** Use the "Field Discovery" workflow to submit status updates (Open/Closed/Damaged) via the pipeline's merge scripts.

---

## 2. Field Team Challenges in Data Collection

Gathering granular data in conflict zones is inherently difficult. Field teams face the following "Friction Points":

1.  **Security Risks:** Accessing remote schools for verification often requires traveling through "Red Zones" with high risks of IEDs or kidnapping.
2.  **Information Decay:** In active conflict, a school's status can change weekly. Data gathered today may be obsolete by the time it is cleaned and processed.
3.  **Fragmented Reporting:** Local authorities (EMIS) may stop reporting in contested areas, leading to "data black holes" precisely where information is needed most.
4.  **Verification Fatigue:** Repeatedly asking local communities for status updates without providing immediate aid can lead to trust erosion.

---

## 3. How to Contribute Data

### Step 1: Format your Data
To replace a "National Average" with "Provincial Reality," your data should follow this structure:
| iso3 | year | region | indicator | value | source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| BFA | 2024 | Soum | Gross enrolment ratio, primary (%) | 24.5 | Field-EBI |

### Step 2: Inject into Pipeline
Place your updated CSV in `data/raw/education/` and re-run the cleaning script:
```bash
python scripts/03_x_merge_education.py
python scripts/09_generate_contextual_stats.py
```

### Step 3: Qualitative Notes
If numeric data is impossible to get, contribute **Qualitative Field Notes**. The dashboard is designed to display these in the "Field Observation" section of Map 2, which provides crucial context that a "Risk Score" cannot capture alone.

---

## 4. The "Data Maturity" Roadmap

1.  **Level 1 (Current):** National benchmarks + Population density + Conflict events.
2.  **Level 2:** Provincial education rates + Monthly ACLED updates.
3.  **Level 3:** Site-specific status (Open/Closed) verified by field teams.

By bridging the gap between **Remote Sensing** (Satellite/Conflict Data) and **Ground Truth** (Field Teams), the Education Bridge Initiative can move from "Estimates" to "Actionable Intelligence."
