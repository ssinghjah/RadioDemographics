import pandas as pd
import matplotlib.pyplot as plt
import math
import os

SOURCE_FILE_PATHs = ["/home/simran/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/Demographics/region_0_populations.csv", "/home/simran/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/Demographics/region_1_populations.csv"]
OUTPUT_FOLDER = "/home/simran/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/Demographics/"
DEMOGRAPHICS_COL = "population"
RADIO_COL = "rsrp"
LOCATION_COL = "census_tract_geoid"
DIST_THRESH = 0.1 # in km

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

def calculate_num_handovers_per_dist(cell_rows):
    curr_dist_counter = 0
    num_handovers_segment = 0
    population_density_seg = {}
    dist_seg_info = []
    num_rows = len(cell_rows)
    for i in range(num_rows-1):
        row = cell_rows.iloc[i]
        next_row = cell_rows.iloc[i+1]
        dist_increase = calculate_distance((row["latitude"], row["longitude"], row["altitude"]), (next_row["latitude"], next_row["longitude"], next_row["altitude"])) / 1000.0
        curr_dist_counter += dist_increase
        if cell_rows.iloc[i]["pci"] != cell_rows.iloc[i+1]["pci"]:
            num_handovers_segment += 1
        
        if row[LOCATION_COL] not in population_density_seg:
                population_density_seg[row[LOCATION_COL]] = {"distance":  0, "pop_density": row["population"]}

        if row[LOCATION_COL] == next_row[LOCATION_COL]:
            population_density_seg[row[LOCATION_COL]]["distance"] += dist_increase
        else:
            if next_row[LOCATION_COL] not in population_density_seg:
                population_density_seg[next_row[LOCATION_COL]] = {"distance":  0, "pop_density": next_row["population"]}
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
for source_file_path in SOURCE_FILE_PATHs:
    source_df = pd.read_csv(source_file_path)
    handovers_per_dist = calculate_num_handovers_per_dist(source_df)
    output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(source_file_path)[0] + "_handovers_per_dist_" + str(DIST_THRESH) + "_km" + ".csv")
    pd.DataFrame(handovers_per_dist).to_csv(output_path, index=False)



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






