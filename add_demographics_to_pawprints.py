import pandas as pd
import argparse
import math
import os
import numpy as np
import os, sys
import time
from core import geoid_from_latlon
import censusgeocode as cg

parser = argparse.ArgumentParser(description = "Add latest demographic info are added from US census database.")
INPUT_FOLDER = "./data/split_geoids"
OUTPUT_FOLDER = "./data/split_demographics"


DEMOGRAPHICS_SOURCE = "/home/simran/Work/AERPAW/ExperimentData/Cross_Country/PolicyMap/States/"
RUCC_SOURCE = "./data/RUCC/rucc.csv"
COUNTY_FIPS_SOURCE = "./data/FIPS/fips.csv"
DEMOGRAPHICS_KPI_COL = "rpopden"
DEMOGRAPHICS_LOC_COL = "GeoID"
DEMOGRAPHICS_COL_NAME = "population_density"

MISSING_FIPS = []

def _county_to_fips(county_name, fips_map):
    fips = None
    matching_rows = fips_map[fips_map["county"] == county_name]
    if (len(matching_rows) > 0):
        fips = matching_rows.iloc[0]["fips"]
    return fips

parser = argparse.ArgumentParser(description = "Adds county, census tract, and census block geo ids to each log row, using which latest demographic info are added from US census database.")

PAWPRINTS_ROOT_FOLDER = "/home/ubuntu/RadioDemographics/data/split/"
PAWPRINTS_OUTPUT_FOLDER = "~/RadioDemographics/data/split_geoids/"
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


START = 1
END = 79
OFFSET = 4
PREFIX = "aerpaw-1_cellular_interpolated_seg_"
current_seg = START
while current_seg <= END:
    print("Segment:" + str(current_seg))
    input_file_path = os.path.join(PAWPRINTS_ROOT_FOLDER, PREFIX + str(current_seg) + ".csv")
    output_path = os.path.join(PAWPRINTS_OUTPUT_FOLDER, PREFIX + str(current_seg) + "_geoids.csv")
    process_file(input_file_path, output_path)
    current_seg += OFFSET


def _rucc_from_fips(fips, rucc_pd):
    rucc = -1
    matching_rows = rucc_pd[rucc_pd["FIPS"] == fips]
    if len(matching_rows == 3):
        rucc = matching_rows[matching_rows["Attribute"] == "RUCC_2023"]["Value"].iloc[0]
    return rucc
    

def _add_rucc():
    pass


def run(input_file_path, output_file_path, all_state_demo_pds, fips_map, rucc_pd):
    rows_processed = 0
    rows_skipped = 0
    pawprints_pd = pd.read_csv(input_file_path)
    pawprints_pd["population_density"] = math.nan
    pawprints_pd["rucc"] = math.nan
    # total_rows = len(pawprints_pd)
    unique_tracts = pawprints_pd["census_tract_geoid"].unique()
    # demographics_pd = pd.read_csv(DEMOGRAPHICS_SOURCE)
    print(len(unique_tracts))
    for unique_tract in unique_tracts:
        if math.isnan(unique_tract):
            continue
        print(unique_tract)
        row = pawprints_pd[pawprints_pd["census_tract_geoid"] == unique_tract].iloc[0]
        state_abbrv = row["state_abrv"].lower()
        if state_abbrv in all_state_demo_pds:
            print(state_abbrv, " found")
            demographics_pd = all_state_demo_pds[state_abbrv]    
            demographics_kpi = float(demographics_pd[demographics_pd[DEMOGRAPHICS_LOC_COL] == unique_tract][DEMOGRAPHICS_KPI_COL].iloc[0])
            pawprints_pd.loc[pawprints_pd["census_tract_geoid"] == unique_tract, "population_density"] = demographics_kpi  
            rows_processed += sum(pawprints_pd["census_tract_geoid"] == unique_tract)
            # print(demographics_kpi)
        else:
            print(state_abbrv, " not found")
            rows_skipped += sum(pawprints_pd["census_tract_geoid"] == unique_tract)

        county_fips = _county_to_fips(row["county_name"].lower(), fips_map)
        if not county_fips:
            MISSING_FIPS.append(row["county_name"])
        else:
            rucc = _rucc_from_fips(county_fips, rucc_pd)
            if rucc:
                pawprints_pd.loc[pawprints_pd["census_tract_geoid"] == unique_tract, "rucc"] = rucc  
        print("----")

    pawprints_pd.to_csv(output_file_path, index=False)
    return len(pawprints_pd), rows_processed, rows_skipped

all_state_demo_pds = {}
for input_file in os.listdir(DEMOGRAPHICS_SOURCE):
    if not input_file.endswith(".csv"):
        continue
    state = input_file.split("_")[0]
    all_state_demo_pds[state] = pd.read_csv(os.path.join(DEMOGRAPHICS_SOURCE, input_file))

fips_map = pd.read_csv(COUNTY_FIPS_SOURCE)
rucc_pd = pd.read_csv(RUCC_SOURCE)
total_rows = 0
total_processed = 0
total_skipped = 0
for input_file in os.listdir(INPUT_FOLDER):
    if not input_file.endswith(".csv"):
        continue
    input_file_path = os.path.join(INPUT_FOLDER, input_file)
    output_file_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(input_file)[0] + "_demographics.csv")
    total, processed, skipped = run(input_file_path, output_file_path, all_state_demo_pds, fips_map, rucc_pd)
    total_rows += total
    total_processed += processed
    total_skipped += skipped

print("Total segments = " + str(len(os.listdir(INPUT_FOLDER))))
print("Total rows = " + str(total_rows))
print("Rows processed = ", total_processed, ", not processed = ", total_skipped)
print("Missing FIPS: " + str(MISSING_FIPS))
