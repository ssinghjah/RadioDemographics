import requests
import json

def run(latitude, longitude):
    url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x={longitude}&y={latitude}&benchmark=4&vintage=4&format=json"

    response = requests.get(url)
    geo_data = {}
    if response.status_code == 200:
        data = response.json()
        # Process the JSON data
        try:
            geographies = data['result']['geographies']
            geo_data["state_abrv"] = geographies["States"][0]["STUSAB"]
            geo_data["census_tract_geoid"] = geographies["Census Tracts"][0]["GEOID"]
            geo_data["census_tract_arealand"] = geographies["Census Tracts"][0]["AREALAND"]
            geo_data["census_block_geoid"] = geographies["2020 Census Blocks"][0]["GEOID"]
            geo_data["census_block_arealand"] = geographies["2020 Census Blocks"][0]["AREALAND"]
            geo_data["county_geoid"] = geographies["Counties"][0]["GEOID"]
            geo_data["county_name"] = geographies["Counties"][0]["NAME"]
            return geo_data
        except KeyError as ke:
            print(ke)
    else:
        print(f"Error: {response.status_code}")


if __name__ == "__main__":
    #longitude =  -103.730214
    #latitude = 35.166955
    longitude = -103.730620
    latitude = 35.182195
   

    print("latitude, longitude = " + str(latitude) + "," + str(longitude))
    print(run(latitude, longitude))

    
