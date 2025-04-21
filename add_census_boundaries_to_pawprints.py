import pandas as pd
import argparse
import math
import numpy as np

from core import geoid_from_latlon

parser = argparse.ArgumentParser(description = "Adds county, census tract, and census block geo ids to each log row, using which latest demographic info are added from US census database.")

PAWPRINTS_SOURCE_PATH = "/home/simran/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/Split/aerpaw-1_cellular_seg_0.csv"
PAWPRINTS_OUTPUT_PATH = "/home/simran/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/Split/aerpaw-1_cellular_seg_0_demographics.csv"

pawprints_pd = pd.read_csv(PAWPRINTS_SOURCE_PATH)
total_rows = len(pawprints_pd)

for index,row in pawprints_pd.iterrows():
    print(index, "/" , total_rows, row["latitude"], row["longitude"])
    if np.isnan(row["latitude"]) or np.isnan(row["longitude"]):
        pawprints_pd.loc[index, 'state_abrv'] = ""
        pawprints_pd.loc[index, 'census_tract_geoid'] = ""
        pawprints_pd.loc[index, 'census_tract_arealand'] = ""
        pawprints_pd.loc[index, 'census_block_geoid'] = ""
        pawprints_pd.loc[index, 'census_block_arealand'] = ""
        pawprints_pd.loc[index, 'county_geoid'] = ""
        pawprints_pd.loc[index, 'county_name'] = ""
    else:
        geo_data = geoid_from_latlon.run(row["latitude"], row["longitude"])
        pawprints_pd.loc[index, 'state_abrv'] = geo_data["state_abrv"] 
        pawprints_pd.loc[index, 'census_tract_geoid'] = geo_data["census_tract_geoid"]
        pawprints_pd.loc[index, 'census_tract_arealand'] = geo_data["census_tract_geoid"]
        pawprints_pd.loc[index, 'census_block_geoid'] = geo_data["census_tract_arealand"]
        pawprints_pd.loc[index, 'census_block_arealand'] = geo_data["census_tract_arealand"]
        pawprints_pd.loc[index, 'county_geoid'] = geo_data["county_geoid"]
        pawprints_pd.loc[index, 'county_name'] = geo_data["county_name"]

pawprints_pd.to_csv(PAWPRINTS_OUTPUT_PATH, index=False)

