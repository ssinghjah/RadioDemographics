import pandas as pd
import matplotlib.pyplot as plt
import math
import os
import sys
import numpy as np
import tqdm
import time
import opencellid_get_cell_location

INPUT_FOLDER = "./data/split_demophysiographics_elevations//"
OUTPUT_FOLDER = "./data/analysis/"
DEMOGRAPHICS_COL = "population_density"
OPEN_CELL_ID_DATA = "./data/opencellid/310.csv"
RADIO_COL = "rsrp"
LOCATION_COL = "census_tract_geoid"
DIST_THRESH = 0.1 # in km
OPEN_CELL_ID_LAT_COL = 7 
OPEN_CELL_ID_LON_COL = 6

def calculate_num_handovers(cell_rows):
    num_handovers = 0
    cell_connection_durations = []
    num_rows = len(cell_rows)
    curr_cell_connection_duration = 0
    for i in range(num_rows-1):
        if cell_rows.iloc[i]["pci"] != cell_rows.iloc[i+1]["pci"]:
            num_handovers += 1
            cell_connection_durations.append(curr_cell_connection_duration)
        else:
            curr_cell_connection_duration += float(cell_rows.iloc[i+1]["phone_abs_time"]) - float(cell_rows.iloc[i]["phone_abs_time"])
    cell_connection_durations.append(curr_cell_connection_duration)
    return num_handovers, cell_connection_durations


def point_dist_3D(p1, p2):
    dist = math.sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2) + pow(p1[2] - p2[2], 2))
    return dist

def calculate_seg_population_density(seg_pop_density_info, total_distance):
    pop_density = 0
    for census_tract_info in seg_pop_density_info:
        population_density = seg_pop_density_info[census_tract_info]["pop_density"]
        distance_fraction = seg_pop_density_info[census_tract_info]["distance"] / total_distance
        pop_density += population_density*distance_fraction
    return pop_density

# Format of point is (lat, lon, alt)
def calculate_distance(point_1, point_2):
    ecef1 = lla_to_ecef(point_1)
    ecef2 = lla_to_ecef(point_2)
    return point_dist_3D(ecef1, ecef2)

def lla_to_ecef(lla):
    # Convert latitude and longitude to radians
    lat_rad = math.radians(lla[0])
    lon_rad = math.radians(lla[1])

    # WGS84 parameters
    a = 6378137.0  # semi-major axis
    f_inv = 298.257223563  # inverse flattening
    f = 1.0 / f_inv
    e2 = 1 - (1 - f) * (1 - f)

    # Radius of curvature in the prime vertical
    N = a / math.sqrt(1 - e2 * math.sin(lat_rad)**2)

    # Convert LLA to ECEF
    X = (N + lla[2]) * math.cos(lat_rad) * math.cos(lon_rad)
    Y = (N + lla[2]) * math.cos(lat_rad) * math.sin(lon_rad)
    Z = (N * (1 - e2) + lla[2]) * math.sin(lat_rad)
    return [X, Y, Z]

def add_num_seen_cells(cell_rows):
    num_seen_cells = []
    times = cell_rows["phone_abs_time"].unique()
    cell_rows["num_seen_cells"] = math.nan
    for unique_time in times:
        matching_rows =  cell_rows[cell_rows["phone_abs_time"] == unique_time]
        num_unique_pcis = len(matching_rows["pci"].unique())
        # population = cell_rows[cell_rows["phone_abs_time"] == unique_time][0]["population"]
        # num_unique_pcis = len(cell_rows[cell_rows["phone_abs_time"] == unique_time, "pci"].unique())
        cell_rows.loc[cell_rows["phone_abs_time"] == unique_time, "num_seen_cells"] = num_unique_pcis
        
def calculate_handover_intervals(cell_rows_original):
    cell_rows = cell_rows_original[cell_rows_original["is_connected"] == 1]
    handover_interval_info = []
    num_rows = len(cell_rows)
    curr_dist_counter = 0
    start_gps = (cell_rows.iloc[0]["latitude"], cell_rows.iloc[0]["longitude"], cell_rows.iloc[0]["altitude"])
    start_census_tract_id = cell_rows.iloc[0]["census_tract_geoid"]
    
    for i in range(num_rows - 1):
        sys.stdout.write("\r" + str(i) + " / " + str(num_rows))
        row = cell_rows.iloc[i]
        next_row = cell_rows.iloc[i+1]
        dist_increase = calculate_distance((row["latitude"], row["longitude"], row["altitude"]), (next_row["latitude"], next_row["longitude"], next_row["altitude"])) / 1000.0
        curr_dist_counter += dist_increase
        if row["pci"] != next_row["pci"]:
            # Handover occured
            end_gps = (next_row["latitude"], next_row["longitude"], next_row["altitude"])
            population_density = math.nan
            if start_census_tract_id == next_row["census_tract_geoid"]:
                population_density = next_row["population_density"]
                rucc = next_row["rucc"]
                handover_interval_info.append({"start_gps":start_gps, 
                                            "end_gps":end_gps,
                                            "start_census_tract_id": start_census_tract_id,
                                            "association_length": curr_dist_counter,  
                                            "end_census_tract_id": next_row["census_tract_geoid"],
                                            "population_density": population_density,
                                            "rucc": rucc,
                                            "associated_pci":row["pci"]})
            start_gps = end_gps
            curr_dist_counter = 0
            start_census_tract_id = next_row["census_tract_geoid"]
    return handover_interval_info

def _calc_dist_to_cell_tower(cell_row, matching_row):
    pass

def calculate_distance_to_cell_towers(cell_rows, opencellid_data):
    unique_cis = cell_rows["ci"].unique()
    cell_rows["cell_tower_distance"] = math.nan
    num_matches = 0
    num_rows_match = 0
    num_rows_with_ci = 0
    unknown_ci_count = 0
    attached_rows = []
    missing_cis = []
    for ci in unique_cis:
        # time.sleep(3)
        matching_cell_rows = cell_rows[cell_rows["ci"] == ci]
        num_rows_with_ci += len(matching_cell_rows)
        if ci == 2147483647:
            continue
        ci_location = None
        matching_cell_location_rows = opencellid_data[opencellid_data["ci"] == ci]
        
        if len(matching_cell_location_rows) > 0 and matching_cell_location_rows.iloc[0]["lat"] != -1:
            ci_location = {"lat": matching_cell_location_rows.iloc[0]["lat"], "lon": matching_cell_location_rows.iloc[0]["lon"]} 
        else: 
            print("Not found:", ci)
            # unknown_ci_count += len(matching_cell_rows)

            pass
            #ci_location = opencellid_get_cell_location.run(matching_cell_rows.iloc[0]["mcc"], matching_cell_rows.iloc[0]["mnc"], matching_cell_rows.iloc[0]["tac"], matching_cell_rows.iloc[0]["ci"])
        
        if ci_location:
            num_matches += 1
            num_rows_match += len(matching_cell_rows)
            for row_num, matching_cell_row in matching_cell_rows.iterrows():
                cell_tower_distance = calculate_distance((matching_cell_row["latitude"], matching_cell_row["longitude"], 0), (ci_location["lat"], ci_location["lon"], 0)) / 1000.0
                matching_cell_row["cell_tower_distance"] = cell_tower_distance
                attached_rows.append(matching_cell_row)
                # matching_cell_rows["distance"] = matching_cell_rows.apply(_calc_dist_to_cell_tower)
                # cell_rows[matching_cell_row.loc, "cell_tower_distance"] = cell_tower_distance
        else:
            missing_cis.append({"ci":ci, "mcc": matching_cell_rows["mcc"].iloc[0], "mnc": matching_cell_rows["mnc"].iloc[0], "tac": matching_cell_rows["tac"].iloc[0]})
                
    unique_mcc = cell_rows["mcc"].unique()
    if len(unique_mcc) > 1:
        print(unique_mcc)

    return num_rows_with_ci, num_rows_match, num_matches, len(unique_cis), missing_cis, attached_rows

       
def calculate_num_handovers_per_dist(cell_rows):
    curr_dist_counter = 0
    num_handovers_segment = 0
    population_density_seg = {}
    dist_seg_info = []
    num_rows = len(cell_rows)
    cell_rows = cell_rows[cell_rows["is_connected"] == 1]
    for i in range(num_rows-1):
        row = cell_rows.iloc[i]
        next_row = cell_rows.iloc[i+1]
        dist_increase = calculate_distance((row["latitude"], row["longitude"], row["altitude"]), (next_row["latitude"], next_row["longitude"], next_row["altitude"])) / 1000.0
        curr_dist_counter += dist_increase
        if cell_rows.iloc[i]["pci"] != cell_rows.iloc[i+1]["pci"]:
            num_handovers_segment += 1
        
        if row[LOCATION_COL] not in population_density_seg:
                population_density_seg[row[LOCATION_COL]] = {"distance":  0, "pop_density": row["population_density"]}

        if row[LOCATION_COL] == next_row[LOCATION_COL]:
            population_density_seg[row[LOCATION_COL]]["distance"] += dist_increase
        else:
            if next_row[LOCATION_COL] not in population_density_seg:
                population_density_seg[next_row[LOCATION_COL]] = {"distance":  0, "pop_density": next_row["population_density"]}
            population_density_seg[next_row[LOCATION_COL]]["distance"] += 0.5*dist_increase
            population_density_seg[row[LOCATION_COL]]["distance"] += 0.5*dist_increase


        if curr_dist_counter > DIST_THRESH:
            population_density = calculate_seg_population_density(population_density_seg, curr_dist_counter)
            dist_seg_info.append({"distance": curr_dist_counter, "num_handovers": num_handovers_segment, "population_density": population_density}), 
            num_handovers_segment = 0
            population_density_seg = {}
            curr_dist_counter = 0

    return dist_seg_info

# KPI Analysis
merged_pd = []
radio_kpis_all = pd.DataFrame()
open_cell_id_data = pd.read_csv(OPEN_CELL_ID_DATA)
missing_cis_all = []
found_cis = 0
unique_cis = 0
found_ci_rows = 0
total_rows = 0
cell_dist_attached_rows = []
for source_file in tqdm.tqdm(sorted(os.listdir(INPUT_FOLDER))):
    if not source_file.endswith(".csv"):
        continue

    source_file_path = os.path.join(INPUT_FOLDER, source_file)
    source_df = pd.read_csv(source_file_path)
    # handovers_per_dist = calculate_num_handovers_per_dist(source_df)
    handover_info = calculate_handover_intervals(source_df)
    add_num_seen_cells(source_df)
    num_rows_with_ci, num_row_matches, num_matches, total, missing_cis, attached_rows = calculate_distance_to_cell_towers(source_df, open_cell_id_data)
    found_cis += num_matches
    total_rows += num_rows_with_ci
    unique_cis += total
    found_ci_rows += num_row_matches
    cell_dist_attached_rows.extend(attached_rows)
    missing_cis_all.extend(missing_cis)
    radio_kpis_this_seg = source_df[source_df["is_connected"] == 1][["population_density", "rucc", "longitude", "latitude",  "elevation", "altitude", "phone_abs_time", "num_seen_cells", "rsrp", "rsrq", "rssi",  "physiographic_region_provcode", "physiographic_region_fencode", "cell_tower_distance"]]
    merged_pd.extend(handover_info)
    output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(source_file)[0] + "_handovers_dist" + ".csv")
    pd.DataFrame(handover_info).to_csv(output_path, index=False)
    radio_kpis_all = pd.concat([radio_kpis_all, radio_kpis_this_seg], ignore_index=True)
    output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(source_file)[0] + "_radio_kpis" + ".csv")
    source_df.to_csv(output_path, index=False)
    # radio_kpis_all = pd.concat([radio_kpis_all, source_df], ignore_index=True)

print("Summary:")
print("found ci rows = ", found_ci_rows, "total ci rows = ", total_rows, found_cis, unique_cis)
pd.DataFrame(merged_pd).to_csv(os.path.join(OUTPUT_FOLDER, "handover_dist_all.csv"), index=False)
radio_kpis_all.to_csv(os.path.join(OUTPUT_FOLDER, "radio_kpis_all.csv"), index=False)
pd.DataFrame(missing_cis_all).to_csv(os.path.join(OUTPUT_FOLDER, "missing_location_cis.csv"), index=False)
pd.DataFrame(cell_dist_attached_rows).to_csv(os.path.join(OUTPUT_FOLDER, "cell_tower_distances.csv"), index=False)
# KPI Analysis
# demo_kpis = []
# mean_radios = []
# num_handovers = []
# cell_connection_durations = []
# cell_connection_durations_mean = []

# for source_file_path in SOURCE_FILE_PATHs:
#     source_df = pd.read_csv(source_file_path)
#     unique_tracts = source_df[LOCATION_COL].unique()

#     for tract in unique_tracts:
#         rows = source_df[source_df[LOCATION_COL] == tract]
#         mean_radio_kpi = sum(rows[RADIO_COL])/len(rows[RADIO_COL])
#         demo_kpi = rows.iloc[0][DEMOGRAPHICS_COL]
#         print(mean_radio_kpi)
#         print(demo_kpi)
#         demo_kpis.append(demo_kpi)
#         mean_radios.append(mean_radio_kpi)
#         num_handover, cell_connection_duration = calculate_num_handovers(rows)
#         cell_connection_durations.append(cell_connection_duration)
#         num_handovers.append(num_handover)
#         cell_connection_durations_mean.append(sum(cell_connection_duration)/ (len(cell_connection_durations)*1000.0))

# print(mean_radios)
# print(demo_kpis)



# plt.rcParams.update({'font.size': 28}) # Set font size to 20


# plt.scatter(demo_kpis, mean_radios)
# plt.xlabel("Estimated number of people per square mile, between 2019-2023.")
# plt.ylabel("RSRP (dBm)")
# plt.grid()

# plt.figure()
# plt.scatter(demo_kpis, num_handovers)
# plt.xlabel("Estimated number of people per square mile, between 2019-2023.")
# plt.ylabel("Num handovers")
# plt.grid()

# plt.figure()
# plt.scatter(demo_kpis, cell_connection_durations_mean)
# plt.xlabel("Estimated number of people per square mile, between 2019-2023.")
# plt.ylabel("Mean cell connection duration (seconds)")
# plt.grid()
# plt.show()






