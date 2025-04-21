import pandas as pd
import argparse
import math
import numpy as np
from core import population_density_from_latlon


parser = argparse.ArgumentParser(description = "Adds county, census tract, and census block geo ids to each log row, using which latest demographic info are added from US census database.")

PAWPRINTS_SOURCE_PATH = "/home/simran/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/Demographics/region_0_demographics.csv"
PAWPRINTS_OUTPUT_PATH = "/home/simran/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/Demographics/region_0_populations.csv"
DEMOGRAPHICS_SOURCE = "/home/simran/Work/AERPAW/ExperimentData/Cross_Country/PolicyMap/nm_population_density.csv"
DEMOGRAPHICS_KPI_COL = "rpopden"
DEMOGRAPHICS_LOC_COL = "GeoID"
DEMOGRAPHICS_COL_NAME = "population_density"

pawprints_pd = pd.read_csv(PAWPRINTS_SOURCE_PATH)
pawprints_pd["population"] = -1
total_rows = len(pawprints_pd)
unique_tracts = pawprints_pd["census_tract_geoid"].unique()
demographics_pd = pd.read_csv(DEMOGRAPHICS_SOURCE)
print(len(unique_tracts))
for unique_tract in unique_tracts:
    print(unique_tract)
    #area = population_density_from_latlon.get_population_density(str(unique_tract))
    # pop_info = population_density_from_latlon.get_population(str(unique_tract))
    demographics_kpi = float(demographics_pd[demographics_pd[DEMOGRAPHICS_LOC_COL] == unique_tract][DEMOGRAPHICS_KPI_COL].iloc[0])
    pawprints_pd.loc[pawprints_pd["census_tract_geoid"] == unique_tract, "population"] = demographics_kpi  
    print(demographics_kpi)
    print("----")

pawprints_pd.to_csv(PAWPRINTS_OUTPUT_PATH, index=False)

