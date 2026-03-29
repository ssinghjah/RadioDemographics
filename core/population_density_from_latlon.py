import requests

def get_census_data_by_geoid(geoid, variables, year=2020, dataset="dec/pl"):
    """Retrieves U.S. Census data for a given GEOID and variables."""

    base_url = f"https://api.census.gov/data/{year}/{dataset}"
    get_vars = ",".join(variables)

    geoid_len = len(geoid)
    if geoid_len == 15:
        for_param = f"block:{geoid[-4:]}"
        in_param = f"state:{geoid[0:2]}+county:{geoid[2:5]}+tract:{geoid[5:11]}"
    elif geoid_len == 11:
        for_param = f"tract:{geoid[-6:]}"
        in_param = f"state:{geoid[0:2]}+county:{geoid[2:5]}"
    elif geoid_len == 5:
        for_param = f"county:{geoid[-3:]}"
        in_param = f"state:{geoid[0:2]}"
    elif geoid_len == 2:
        for_param = f"state:{geoid}"
        in_param = ""
    else:
        return "Error: Invalid GEOID length."

    url = f"{base_url}?get={get_vars}&for={for_param}"
    if in_param:
        url += f"&in={in_param}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if len(data) > 1:
            header = data[0]
            values = data[1]
            result = dict(zip(header, values))
            return result
        else:
            return "Data not found."

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except ValueError:
        return "Error: Invalid JSON response."
    
    

def get_area_from_boundary_api(geoid, year):
    """Gets the area from the Geographic Boundary APIs."""
    geoid_len = len(geoid)
    if geoid_len == 15:
        url = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/2/query?where=GEOID%3D'{geoid}'&outFields=AREALAND,AREAWATER&f=json"
    elif geoid_len == 11:
        url = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/5/query?where=GEOID%3D'{geoid}'&outFields=AREALAND,AREAWATER&f=json"
    elif geoid_len == 5:
        url = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/1/query?where=GEOID%3D'{geoid}'&outFields=AREALAND,AREAWATER&f=json"
    elif geoid_len == 2:
        url = f"https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Current/MapServer/0/query?where=GEOID%3D'{geoid}'&outFields=AREALAND,AREAWATER&f=json"
    else:
        return "Error: Invalid GEOID length."

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "fields" in data and len(data["fields"]) > 0:
            feature = data["fields"][0]["attributes"]
            aland = feature["AREALAND"]
            awater = feature["AREAWATER"]
            total_area_meters = aland + awater
            total_area_miles = total_area_meters * 0.000000386102
            return total_area_miles
        else:
            return "Area data not found."

    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except ValueError:
        return "Error: Invalid JSON response."


def get_population(geoid, year=2020):
    """Calculates population for a given GEOID"""
    try:
        population_data = get_census_data_by_geoid(geoid, ["P1_001N"], year)
        if isinstance(population_data, str):
            return population_data
        population = int(population_data["P1_001N"])

        return population

    except Exception as e:
        return f"Error: {e}"

def get_population_density(geoid, year=2020):
    """Calculates population density for a given GEOID using the Geographic Boundary APIs."""

    try:
        population_data = get_census_data_by_geoid(geoid, ["P1_001N"], year)
        if isinstance(population_data, str):
            return population_data
        population = int(population_data["P1_001N"])

        area_data = get_area_from_boundary_api(geoid, year)
        if isinstance(area_data, str):
            return area_data
        total_area_miles = area_data

        if total_area_miles == 0:
            return "Error: Area is zero."

        density = population / total_area_miles
        return density

    except Exception as e:
        return f"Error: {e}"

# Example usage:
# block_geoid = "481130021001001"
# tract_geoid = "37183050100"
# county_geoid = "48113"
# state_geoid = "48"

# block_density = get_population_density(block_geoid)
# tract_density = get_population_density(tract_geoid)
# county_density = get_population_density(county_geoid)
# state_density = get_population_density(state_geoid)

# print(f"Block Density: {block_density}")
# print(f"Tract Density: {tract_density}")
# print(f"County Density: {county_density}")
# print(f"State Density: {state_density}")



