import requests
import json
import time
import pandas as pd

INPUT_PATH = "./data/analysis/missing_location_cis.csv"
OUTPUT_PATH = "./data/analysis/found_location_cis.csv"
TIME_SLEEP_INTERVAL = 30  # seconds

def run(mcc, mnc, lac, cell_id):
    try:
        response = requests.get(f"https://opencellid.org/ajax/searchCell.php?mcc={mcc}&mnc={mnc}&lac={lac}&cell_id={cell_id}")
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        found_locations = pd.read_csv(OUTPUT_PATH)
        
        print("Request successful!")
        print("Status code:", response.status_code)
        print("Response content:", response.text)
        if response.status_code == 200:
            print(response.text)
            return json.loads(response.text)
        else:
            return None
        # If the response is JSON, you can parse it like this:
        # data = response.json()
        # print("JSON data:", data)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    missing_ci_pd = pd.read_csv(INPUT_PATH)
    ci_locs_this_run = []
    found_ci_locations_all = pd.read_csv(OUTPUT_PATH)
    found_ci_locations = found_ci_locations_all[found_ci_locations_all["ci"] == -1]
    bAPICalled = False
    for index, row in missing_ci_pd.iterrows():
        print("row/total=",index, len(missing_ci_pd))
        print("--------")
        if bAPICalled:
            time.sleep(TIME_SLEEP_INTERVAL)

        print("row = ", row)
        print("-------")
        
        '''
        if row["ci"] in found_ci_locations["ci"].values:
            print("Skipping " + str(row["ci"]))
            bAPICalled =False
            continue
        '''
        
        resp = run(row["mcc"], row["mnc"], row["tac"] , row["ci"])
        bAPICalled = True
        # Handle response
        # If invalid, do nothing. Try again next time.
        # If valid, update the output csv and remove from the input missing csv
        if resp == "Invalid Request" or resp == False or resp is None:
            ci_locs_this_run.append({"mcc": row["mcc"], "mnc": row["mnc"], "tac": row["tac"], "ci":row["ci"],"lat":-1, "lon":-1, "range":-1})
        else:
            ci_locs_this_run.append({"mcc": row["mcc"], "mnc": row["mnc"], "tac": row["tac"], "ci":row["ci"],"lat":resp["lat"], "lon":resp["lon"], "range":resp["range"]})
        pd.concat([found_ci_locations_all, pd.DataFrame(ci_locs_this_run)], ignore_index=True).to_csv(OUTPUT_PATH, index=False)
        
        
        

