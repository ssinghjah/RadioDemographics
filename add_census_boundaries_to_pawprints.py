import pandas as pd
import argparse
import math
import numpy as np
from pathlib import Path
import os
import time
import json

from core import geoid_from_latlon

parser = argparse.ArgumentParser(description = "Adds county, census tract, and census block geo ids to each log row, using which latest demographic info are added from US census database.")

PAWPRINTS_SOURCE_PATH = "C:\\Users\\ssingh28\\RadioDemographics\\data\\PawPrints_2\\original\\aug_18_2024a_merged.csv"
PAWPRINTS_OUTPUT_PATH = "C:\\Users\\ssingh28\\RadioDemographics\\data\\PawPrints_2\\geoids\\aug_18_2024a_demographics.csv"
GEO_CACHE_FILE = "C:\\Users\\ssingh28\\RadioDemographics\\data\\PawPrints_2\\geoids\\geo_cache.json"


def _load_cache():
    """Load the persistent lat/lon → geo_data cache from disk."""
    if os.path.exists(GEO_CACHE_FILE):
        with open(GEO_CACHE_FILE, "r") as f:
            raw = json.load(f)
        # JSON keys are strings; convert back to (lat, lon) float tuples
        return {tuple(map(float, k.split(","))): v for k, v in raw.items()}
    return {}


def _save_cache(cache):
    """Persist the cache to disk after every new entry."""
    raw = {",".join(map(str, k)): v for k, v in cache.items()}
    with open(GEO_CACHE_FILE, "w") as f:
        json.dump(raw, f)


def _write_status(status_file, current, total, lat, lon, cached=False):
    """Overwrite the per-file status file with the latest progress line."""
    tag = " [cached]" if cached else ""
    line = f"{current}/{total}  lat={lat}  lon={lon}{tag}\n"
    with open(status_file, "w") as f:
        f.write(line)


def run():
    # Status file is placed next to the output file, named after the source stem
    source_stem = Path(PAWPRINTS_SOURCE_PATH).stem
    status_file = os.path.join(os.path.dirname(PAWPRINTS_OUTPUT_PATH), source_stem + "_status.txt")

    print(PAWPRINTS_SOURCE_PATH)
    if os.path.exists(PAWPRINTS_OUTPUT_PATH):
        print("Output file already exists, skipping...")
        return
    pawprints_pd = pd.read_csv(PAWPRINTS_SOURCE_PATH)

    # Build a cache keyed by (lat, lon) so each unique coordinate is queried once
    unique_coords = pawprints_pd[["latitude", "longitude"]].drop_duplicates()
    total_unique = len(unique_coords)
    print(f"Total rows: {len(pawprints_pd)} | Unique lat/lon pairs: {total_unique}")

    geo_cache = _load_cache()
    print(f"Persistent cache loaded: {len(geo_cache)} entries")

    for i, (_, coord) in enumerate(unique_coords.iterrows()):
        lat, lon = coord["latitude"], coord["longitude"]
        key = (lat, lon)
        if key in geo_cache:
            print(f"{i + 1}/{total_unique}  lat={lat}  lon={lon}  [cached]")
            _write_status(status_file, i + 1, total_unique, lat, lon, cached=True)
            continue
        print(f"{i + 1}/{total_unique}  lat={lat}  lon={lon}")
        _write_status(status_file, i + 1, total_unique, lat, lon)
        if np.isnan(lat) or np.isnan(lon):
            geo_cache[key] = None
        else:
            geo_cache[key] = geoid_from_latlon.run(lat, lon)
            time.sleep(3)
        _save_cache(geo_cache)

    # Map cached results back to every row
    empty_fields = {
        'state_abrv': "",
        'census_tract_geoid': "",
        'census_tract_arealand': "",
        'census_block_geoid': "",
        'census_block_arealand': "",
        'county_geoid': "",
        'county_name': "",
    }
    for index, row in pawprints_pd.iterrows():
        geo_data = geo_cache.get((row["latitude"], row["longitude"]))
        if geo_data is None:
            for field, default in empty_fields.items():
                pawprints_pd.loc[index, field] = default
        else:
            pawprints_pd.loc[index, 'state_abrv'] = geo_data["state_abrv"]
            pawprints_pd.loc[index, 'census_tract_geoid'] = geo_data["census_tract_geoid"]
            pawprints_pd.loc[index, 'census_tract_arealand'] = geo_data["census_tract_geoid"]
            pawprints_pd.loc[index, 'census_block_geoid'] = geo_data["census_tract_arealand"]
            pawprints_pd.loc[index, 'census_block_arealand'] = geo_data["census_tract_arealand"]
            pawprints_pd.loc[index, 'county_geoid'] = geo_data["county_geoid"]
            pawprints_pd.loc[index, 'county_name'] = geo_data["county_name"]

    pawprints_pd.to_csv(PAWPRINTS_OUTPUT_PATH, index=False)

ORIGINAL_FOLDER = "C:\\Users\\ssingh28\\RadioDemographics\\data\\PawPrints_2\\geoids\\"
GEOIDS_FOLDER   = "C:\\Users\\ssingh28\\RadioDemographics\\data\\PawPrints_2\\geoids\\"

