# Quickstart Guide: Education Risk Pipeline

This guide provides a succinct overview of how to run the Education Risk Pipeline to compute the Education Vulnerability Index (EVI).

## 🚀 One-Minute Setup

1. **Install Python**: Ensure you have Python 3.9+ installed.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Check Data Structure**: Ensure you have a `data/raw` and `data/clean` directory (the scripts will create them if missing).

## 🏃 Running the Full Pipeline

The master orchestrator `scripts/run_all.py` handles the execution of all 26 steps.

### Basic Command (Run for Burkina Faso)
```bash
python scripts/run_all.py --iso3 BFA
```

### Advanced Usage
- **Specific Country**: Use `--iso3 [CODE]` (e.g., `MLI`, `NER`).
- **Skip Steps**: Use `--skip 1 2 3` to bypass initial fetch steps if data is already downloaded.
- **Run Only Specific Steps**: Use `--only 22 23 24` to regenerate maps or update the dashboard.
- **Custom Name**: Use `--country "My Country Name"` to override default mapping.

## 🛠 Pipeline Summary

The pipeline is divided into four logical phases:

| Phase | Steps | Focus | Key Output |
| :--- | :--- | :--- | :--- |
| **1. Fetch** | 1-8 | Downloading raw data from HDX, WorldPop, UNESCO. | `data/raw/` |
| **2. Process**| 9-15 | Cleaning, geocoding, and aligning admin names. | `data/clean/` |
| **3. Analyze**| 16-21| Computing vulnerability scores and proximity risk. | `artifacts/` |
| **4. Export** | 22-26| Generating GeoJSONs and updating the Dashboard. | `index.html` |

## 💡 Quick Tips
- **Disk Space**: Step 8 (WorldPop) can be heavy. Use `--only 8` with specific years if you have low bandwidth.
- **Failsafe**: If steps 1-15 fail, the pipeline stops. Fix the data issue before continuing.
- **Results**: Check the `artifacts/[ISO3]/` folder for CSVs and the root `index.html` for the visual dashboard.

---
*For detailed technical specifications, see the [Technical Manual](./TECHNICAL_MANUAL.md).*
