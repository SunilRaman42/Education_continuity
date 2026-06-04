"""
06_4_aggregate_at_risk_schools.py
================================
Aggregates individual school risk scores into province-level annual summaries.
Used by the interactive map to show time-series trends and markers.

Dynamic Version: Calculates site-specific conflict risk based on proximity to granular events.
"""

import json
import os
import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ISO3    = os.environ.get("PIPELINE_ISO3", "BFA")
COUNTRY = os.environ.get("PIPELINE_COUNTRY", "Burkina Faso")
RADIUS_KM = 10.0  # Conflict influence radius

def aggregate_at_risk_schools():
    print(f"🚀 Calculating site-specific school risk for {ISO3} ({COUNTRY})...")
    
    out_dir = Path("artifacts") / ISO3
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    score_path = out_dir / f"schools/{ISO3}_school_vulnerability.csv"
    if not score_path.exists():
        print(f"✗ Base school score data missing: {score_path}")
        return
    
    schools_df = pd.read_csv(score_path)
    
    # Load granular conflicts
    conflict_path = Path(f"data/raw/conflicts/{ISO3}_granular_conflicts.csv")
    if not conflict_path.exists():
        print(f"✗ Granular conflict data missing: {conflict_path}")
        return
    conflicts_df = pd.read_csv(conflict_path)

    # Load provincial fragility (from 06_3)
    fragility_path = out_dir / "province_school_fragility.csv"
    if not fragility_path.exists():
        print(f"✗ Provincial fragility missing: {fragility_path}")
        return
    fragility_df = pd.read_csv(fragility_path)

    # Load boundaries for spatial join (to ensure consistent province assignment)
    admin2_path = Path(f"data/raw/boundaries/{ISO3}_admin2.geojson")
    if not admin2_path.exists():
        print(f"✗ Admin2 boundaries missing: {admin2_path}")
        return
    boundaries = gpd.read_file(admin2_path)

    # 2. Alignment & Mapping
    mapping_path = out_dir / "admin_mapping.json"
    official_to_acled = {}
    if mapping_path.exists():
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping_data = json.load(f)
            official_to_acled = mapping_data.get("official_to_acled", {})

    # Detect admin2 name column in boundaries
    name_col = next(
        (c for c in boundaries.columns
         if any(x in c.lower() for x in ["adm2_en", "adm2_name", "name_2", "shapename", "admin2name"])),
        boundaries.columns[0]
    )

    # Spatial Join to get consistent Province for all schools (Match 06_export_map_data)
    schools_gdf = gpd.GeoDataFrame(
        schools_df, 
        geometry=gpd.points_from_xy(schools_df.longitude, schools_df.latitude),
        crs="EPSG:4326"
    )
    if boundaries.crs != schools_gdf.crs:
        boundaries = boundaries.to_crs(schools_gdf.crs)
        
    joined = gpd.sjoin(schools_gdf, boundaries[[name_col, "geometry"]], how="left", predicate="within")
    
    # Assign province using spatial join + ACLED mapping
    schools_df['province_official'] = joined[name_col].str.strip().str.title().fillna("Unknown")
    schools_df['province'] = schools_df['province_official'].map(official_to_acled).fillna(schools_df['province_official'])
    schools_df["Admin2_ACLED"] = schools_df["province"] # Already mapped

    # 3. Site-Specific Conflict Exposure
    available_years = sorted(conflicts_df["year"].unique().tolist())
    available_years = sorted(list(set(available_years + fragility_df["year"].unique().tolist())))
    available_years = [y for y in available_years if 2015 <= y <= 2026]

    # Pre-pivot fragility for lookup
    fragility_lookup = fragility_df.pivot(index="Region", columns="year", values="school_fragility_score").to_dict()

    # Matrix to store yearly scores [school_idx][year]
    results_matrix = {y: [] for y in available_years}

    # Extract coordinates for distance calculation
    s_lats = schools_df['latitude'].values
    s_lons = schools_df['longitude'].values

    print(f"  → Computing yearly point-level exposure...")
    
    for year in available_years:
        # Get conflicts for this year and previous (2-year rolling window)
        window = [year, year - 1]
        c_yr = conflicts_df[conflicts_df['year'].isin(window)].copy()
        
        if c_yr.empty:
            for _ in range(len(schools_df)):
                results_matrix[year].append({
                    "conflict_score": 0.0,
                    "final_score": 0.0,
                    "fragility_score": 0.0
                })
            continue
            
        c_yr['weight'] = c_yr['year'].apply(lambda y: 1.0 if y == year else 0.6)
        c_yr['w_events'] = 1.0 * c_yr['weight']
        c_yr['w_fatalities'] = c_yr['best'].fillna(0) * c_yr['weight']
        
        c_lats = c_yr['latitude'].values
        c_lons = c_yr['longitude'].values
        
        # Batch distance calculation (Haversine approximation for small distances)
        # Using simple Euclidean for small degrees is often enough, but let's be better
        school_exposure = np.zeros((len(schools_df), 2)) # [events, fatalities]
        
        # Earth radius in km
        R = 6371.0
        
        # To avoid massive memory allocation, process in chunks if needed
        # but 2500 schools is small enough
        for i, s_lat in enumerate(s_lats):
            s_lon = s_lons[i]
            
            # Distance in degrees (rough filtering)
            dlat = np.radians(c_lats - s_lat)
            dlon = np.radians(c_lons - s_lon)
            
            a = np.sin(dlat/2)**2 + np.cos(np.radians(s_lat)) * np.cos(np.radians(c_lats)) * np.sin(dlon/2)**2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            dist = R * c
            
            # Mask for within radius
            mask = dist <= RADIUS_KM
            
            if mask.any():
                school_exposure[i, 0] = c_yr.loc[mask, 'w_events'].sum()
                school_exposure[i, 1] = c_yr.loc[mask, 'w_fatalities'].sum()
        
        # Normalize conflict scores for this year across all schools
        ev_max = school_exposure[:, 0].max() if school_exposure[:, 0].max() > 0 else 1
        fat_max = np.log1p(school_exposure[:, 1].max()) if school_exposure[:, 1].max() > 0 else 1
        
        c_scores = (0.55 * (school_exposure[:, 0] / ev_max) + 
                    0.45 * (np.log1p(school_exposure[:, 1]) / fat_max))
        
        # Combine with provincial fragility
        for s_idx, s in schools_df.iterrows():
            prov = s["Admin2_ACLED"]
            f_score = fragility_lookup.get(year, {}).get(prov, 0.5)
            
            final = (c_scores[s_idx] * (1 + f_score * 0.40)).clip(0, 1)
            results_matrix[year].append({
                "conflict_score": round(float(c_scores[s_idx]), 3),
                "final_score": round(float(final), 3),
                "fragility_score": round(float(f_score), 3)
            })

    # 4. Final Aggregation & Export
    school_yearly_scores = []
    aggregated_prov_stats = {}

    for s_idx, s in schools_df.iterrows():
        y_scores = {}
        y_metrics = {}
        at_risk_years = []
        prov = s["Admin2_ACLED"]
        
        for year in available_years:
            y_str = str(year)
            m = results_matrix[year][s_idx]
            y_scores[y_str] = m["final_score"]
            y_metrics[y_str] = m
            
            if m["final_score"] > 0.5:
                at_risk_years.append(year)
                
                if y_str not in aggregated_prov_stats:
                    aggregated_prov_stats[y_str] = {}
                if prov not in aggregated_prov_stats[y_str]:
                    aggregated_prov_stats[y_str][prov] = {"count": 0, "schools": []}
                
                aggregated_prov_stats[y_str][prov]["count"] += 1
                name = str(s.get("name", "Unknown"))
                aggregated_prov_stats[y_str][prov]["schools"].append({
                    "name": name,
                    "province": str(prov),
                    "lat": float(s.get("latitude", 0)),
                    "lon": float(s.get("longitude", 0)),
                    "v_score": float(m["final_score"])
                })
        
        school_yearly_scores.append({
            "yearly_scores": y_scores,
            "yearly_metrics": y_metrics, # New: detailed metrics per year
            "at_risk_years": at_risk_years,
            "v_score": y_scores.get("2024", y_scores.get(str(available_years[-1]), 0))
        })

    # Add back to dataframe
    scores_df = pd.DataFrame(school_yearly_scores)
    schools_df["yearly_scores"] = scores_df["yearly_scores"]
    schools_df["yearly_metrics"] = scores_df["yearly_metrics"]
    schools_df["at_risk_years"] = scores_df["at_risk_years"]
    schools_df["v_score"] = scores_df["v_score"]
    schools_df["trauma"] = (schools_df["v_score"] * 10).astype(int)

    # 5. Save Outputs
    out_path = out_dir / "province_at_risk_stats.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(aggregated_prov_stats, f, separators=(",", ":"), ensure_ascii=False)
    
    scores_json_path = out_dir / "school_vulnerability_scores.json"
    final_json_df = schools_df.drop(columns=["Admin2_ACLED"])
    final_json_df.to_json(scores_json_path, orient="records")

    print(f"✅ Success! Site-specific scores (with yearly_metrics) saved to {scores_json_path}")
    print(f"✅ Aggregated stats saved to {out_path}")

if __name__ == "__main__":
    aggregate_at_risk_schools()
