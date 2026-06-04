# Technical Manual: Education Risk Pipeline

This document provides a comprehensive technical reference for the Education Risk Pipeline. It is intended for data scientists and developers who need to maintain, extend, or deeply understand the pipeline's logic.

---

## 🏗 System Architecture

The pipeline follows a **Modular Data-Flow Architecture**. Each script is designed to be idempotent: it reads from a known location (usually `data/raw` or `data/clean`) and writes to a known location (`data/clean` or `artifacts`).

### High-Level Workflow
1.  **Ingestion**: Pulls from global datasets (ACLED, WorldPop, UNESCO).
2.  **Normalization**: Standardizes administrative names and geocodes locations.
3.  **Scoring**: Computes multi-factor vulnerability indices at both province and school levels.
4.  **Serialization**: Exports to GeoJSON and JSON for web-based visualization.

---

## 📂 Phase 1: Data Acquisition (Steps 1-8)

These scripts handle the ingestion of raw data.

### `01_fetch_acled_hdx.py`
- **Purpose**: Downloads the global ACLED conflict archive (XLSX).
- **Input**: HDX API.
- **Output**: `data/raw/acled/acled_latest.xlsx`.
- **Note**: This is a large download (~100MB).

### `04_1_fetch_worldpop.py`
- **Purpose**: Fetches high-resolution population density rasters (.tif).
- **Input**: WorldPop REST API.
- **Output**: `data/clean/{iso3}_pop_density/{iso3}_pop_{year}.json` (downsampled heatmap).
- **Parameters**: `--years` (latest/all), `--clean` (removes .tif after processing).

---

## 📂 Phase 2: Processing & Cleaning (Steps 9-15)

Transforms raw files into analysis-ready formats.

### `04_x_align_admin_names.py`
- **Purpose**: Solves the "Mismatched Names" problem between ACLED and official GeoJSON boundaries.
- **Logic**: Performs a spatial join. If ACLED says a point is in "Region A" but the GeoJSON says it's in "Region B", it creates a mapping.
- **Output**: `artifacts/{ISO3}/admin_mapping.json`.

### `04_y_validate_data_integrity.py`
- **Purpose**: Quality Gate.
- **Logic**: Checks for existence of critical files (Boundaries, Conflict Data, Education Indicators).
- **Action**: Aborts the pipeline if dependencies are missing, preventing "Garbage In, Garbage Out".

---

## 📂 Phase 3: Analysis & Scoring (Steps 16-21)

This is the core "intelligence" layer of the pipeline.

### `05_build_analysis.py` (The EVI Formula)
Computes the Education Vulnerability Index (EVI) per province per year.
- **Conflict Score (40%)**: Mean of normalized Event Count and Fatality Count.
- **Education Score (60%)**: Mean of normalized Out-of-School rate and Primary Survival rate.
- **Result**: `artifacts/{ISO3}/{ISO3}_vulnerability.csv`.

### `06_2_school_fragility.py`
Scores individual schools based on hyper-local risk.
- **Step 1**: School inherits the conflict score of its parent province (2-year rolling window).
- **Step 2**: National fragility boost (0-40% uplift) based on UNESCO/WB indicators.
- **Output**: `artifacts/{ISO3}/schools/schools_{ISO3}.geojson`.

---

## 📂 Phase 4: Export & Finalization (Steps 22-26)

### `06_export_map_data.py`
- **Purpose**: Combines all scores into a single GeoJSON for the Mapbox dashboard.
- **Logic**: Merges `vulnerability.csv` with `admin2.geojson`.
- **Output**: `artifacts/{ISO3}/data.geojson`.

### `09_generate_contextual_stats.py`
- **Purpose**: Generates demographic projections (Population 2015-2026).
- **Logic**: Uses WorldBank growth rates to extrapolate 2020 WorldPop data.
- **Output**: `artifacts/{ISO3}/contextual_stats.json`.

---

## 📊 Data Dictionary (Common Columns)

| Column | Meaning | Range |
| :--- | :--- | :--- |
| `score` | Final EVI score. | 0.0 (Safe) to 1.0 (Critical) |
| `events_norm` | Normalized conflict frequency. | 0.0 to 1.0 |
| `at_risk` | Binary flag if school is near recent conflict. | 0 or 1 |
| `tier` | Qualitative risk bucket. | Low, Medium, High, Critical |
| `score_basis` | Metadata on how many indicators were available. | e.g., "3/3 indicators" |

---

## 🌍 Extending to a New Country

To add support for a new country (e.g., Sudan - `SDN`):

1.  **Add to Mapping**: Open `scripts/run_all.py` and add `"SDN": "Sudan"` to the `COUNTRY_MAP`.
2.  **Initialize Folders**:
    ```bash
    mkdir -p data/raw/boundaries data/raw/conflicts
    ```
3.  **Run Pipeline**:
    ```bash
    python scripts/run_all.py --iso3 SDN
    ```
4.  **Verify**: Check the `artifacts/SDN` folder for results.

---
*Developed by the EBI Data Team. Version 1.0.*
