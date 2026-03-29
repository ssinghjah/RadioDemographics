import geopandas as gpd
from shapely.geometry import Point
import os
import pandas as pd
import numpy as np

PAWPRINTS_SEGMENTS_SOURCE_FOLDER = "./data/split_demographics"
OUTPUT_FOLDER = "./data/split_demo_physio_graphics"

PHYSIOGRAPHIC_SHP_FILE = "./data/USGSPhysioGraphic/physio_shp/physio.shp"
# Load physiographic divisions shapefile
divisions = gpd.read_file(PHYSIOGRAPHIC_SHP_FILE)

def run(lat, lon):
    point = Point(lon, lat)
    # Find which division contains the point
    matching = divisions[divisions.contains(point)]
    response = None
    if not matching.empty:
        response = {}
        # print(matching.iloc[0].index)# or relevant field
        for key in matching.iloc[0].index.to_list():
            value = matching.iloc[0][key]
            if isinstance(value, str):
                value = value.replace(" ", "_")
                value = value.lower()
            if "geometry" in key.lower():
                continue
            response["physiographic_region_" + key.lower()] = value
    return response

LIVE = False

if __name__ == "__main__":
    # Appalachian Highlands
    lat, lon = 35.9136495, -84.8970596
    print(lat, lon)
    print(run(lat, lon))
    print("------")


    # Atlantic Plains
    lat, lon = 32.918316, -96.9720373
    print(lat, lon) 
    print(run(lat, lon))
    print("------")


    # Interior Plains
    lat, lon = 35.0771392, -104.1358354
    print(lat, lon)
    print(run(lat, lon))
    print("------")

    # Intermontanne plateau
    lat, lon = 37.0888602, -111.7103645
    print(lat, lon) 
    print(run(lat, lon))
    print("------")


    if LIVE:
        segment_files = os.listdir(PAWPRINTS_SEGMENTS_SOURCE_FOLDER)

        for pawprints_segment_file in segment_files:
            file_name_with_extension = os.path.basename(pawprints_segment_file)
            file_name_without_extension = os.path.splitext(file_name_with_extension)[0]
            pawprints_df = pd.read_csv(os.path.join(PAWPRINTS_SEGMENTS_SOURCE_FOLDER, pawprints_segment_file))
            for index,row in pawprints_df.iterrows():
                print(index, len(pawprints_df), end="\r")
                if not np.isnan(row["latitude"]) and not np.isnan(row["longitude"]):
                    response = run(row["latitude"], row["longitude"])
                    if response:
                        for key in response:
                            pawprints_df.loc[index, key] = response[key]

            pawprints_df.to_csv(os.path.join(OUTPUT_FOLDER, file_name_without_extension + "_physiographics.csv"), index=False)

        
