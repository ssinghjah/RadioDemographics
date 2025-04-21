import pandas as pd
import argparse
import math
import numpy as np
import os, sys
import time
from core import geoid_from_latlon
import censusgeocode as cg


parser = argparse.ArgumentParser(description = "Adds county, census tract, and census block geo ids to each log row, using which latest demographic info are added from US census database.")

PAWPRINTS_ROOT_FOLDER = "/home/ubuntu/pawprints-processing/data/split_interpolated/"
PAWPRINTS_OUTPUT_FOLDER = "~/pawprints-processing/data/split_geoids/"
SLEEP = 0.2

def process_file(input_path, output_path):
    pawprints_pd = pd.read_csv(input_path)
    total_rows = len(pawprints_pd)
    
    for index,row in pawprints_pd.iterrows():
        sys.stdout.write("\r" + str(index) + "/" + str(total_rows))
        if np.isnan(row["latitude"]) or np.isnan(row["longitude"]):
            pawprints_pd.loc[index, 'state_abrv'] = ""
            pawprints_pd.loc[index, 'census_tract_geoid'] = ""
            pawprints_pd.loc[index, 'census_tract_arealand'] = ""
            pawprints_pd.loc[index, 'census_block_geoid'] = ""
            pawprints_pd.loc[index, 'census_block_arealand'] = ""
            pawprints_pd.loc[index, 'county_geoid'] = ""
            pawprints_pd.loc[index, 'county_name'] = ""
        else:
            try:
                result = cg.coordinates(row["longitude"], row["latitude"])  # Returns GEOID for block/tract
                geoid = result['2020 Census Blocks'][0]['GEOID']  # e.g., '060750179021000'
            except Exception as e:
                geoid = ""
            
            pawprints_pd.loc[index, "geo_id_cg_api"] = geoid
            geo_data = geoid_from_latlon.run(row["latitude"], row["longitude"])
            #sys.stdout.write("\r" + str(geo_data))
            #geo_data = None
           
            if geo_data is None:
                continue
            pawprints_pd.loc[index, 'state_abrv'] = geo_data["state_abrv"] 
            pawprints_pd.loc[index, 'census_tract_geoid'] = geo_data["census_tract_geoid"]
            pawprints_pd.loc[index, 'census_tract_arealand'] = geo_data["census_tract_arealand"]
            pawprints_pd.loc[index, 'census_block_geoid'] = geo_data["census_block_geoid"]
            pawprints_pd.loc[index, 'census_block_arealand'] = geo_data["census_block_arealand"]
            pawprints_pd.loc[index, 'county_geoid'] = geo_data["county_geoid"]
            pawprints_pd.loc[index, 'county_name'] = geo_data["county_name"]
            #sys.stdout.write("\r" + geo_data["county_name"] + geo_data["census_block_geoid"])
            #sys.stdout.flush()
        pawprints_pd.to_csv(output_path, index=False)


START = 0
END = 79
PREFIX = "aerpaw-1_cellular_interpolated_seg_"
for i in range(START, END + 1):
    if i % 4 != 0:
        continue
    print(i)
    input_file_path = os.path.join(PAWPRINTS_ROOT_FOLDER, PREFIX + str(i) + ".csv")
    output_path = os.path.join(PAWPRINTS_OUTPUT_FOLDER, PREFIX + str(i) + "_geoids.csv")
    process_file(input_file_path, output_path)


