import pandas as pd
import argparse
import math
import os
import numpy as np
from core import population_density_from_latlon

parser = argparse.ArgumentParser(description = "Add elevation information.")
INPUT_FOLDER = "./data/split_demo_physio_graphics"
OUTPUT_FOLDER = "./data/split_demophysiographics_elevations"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

import requests

def get_elevation(lat, lng):
    api_key = "AIzaSyB5P8g-kF_ilnEJG0t5eS4dooBC5vOJeA8"  # Replace this with your actual API key

    url = "https://maps.googleapis.com/maps/api/elevation/json"
    params = {
        "locations": f"{lat},{lng}",
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        elevation = data['results'][0]['elevation']
        return elevation
    else:
        raise Exception(f"Error from API: {data['status']}")


def run(input_file_path, output_file_path):
    rows_processed = 0
    rows_skipped = 0
    pawprints_pd = pd.read_csv(input_file_path)

    for index, row in pawprints_pd.iterrows():
        print(index, "/", len(pawprints_pd), row["latitude"], row["longitude"])
        if np.isnan(row["latitude"]) or np.isnan(row["longitude"]):
            pawprints_pd.loc[index, 'elevation'] = math.nan
        else:
            try:
                elevation = get_elevation(row["latitude"], row["longitude"])
                pawprints_pd.loc[index, 'elevation'] = elevation
            except Exception as e:
                print(f"Error fetching elevation for ({row['latitude']}, {row['longitude']}): {e}")
                pawprints_pd.loc[index, 'elevation'] = math.nan


    pawprints_pd.to_csv(output_file_path, index=False)
    return len(pawprints_pd), rows_processed, rows_skipped

for input_file in os.listdir(INPUT_FOLDER):
    if not input_file.endswith(".csv"):
        continue
    input_file_path = os.path.join(INPUT_FOLDER, input_file)
    output_file_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(input_file)[0] + "_demographics.csv")
    total, processed, skipped = run(input_file_path, output_file_path)

    total_rows += total
    total_processed += processed
    total_skipped += skipped

print("Total segments = " + str(len(os.listdir(INPUT_FOLDER))))
print("Total rows = " + str(total_rows))
print("Rows processed = ", total_processed, ", not processed = ", total_skipped)
