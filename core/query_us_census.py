import requests

def get_census_data_by_geoid(geoid, variables, year=2020, dataset="dec/pl"):
    """
    Retrieves U.S. Census data for a given GEOID and variables.

    Args:
        geoid (str): The GEOID.
        variables (list): A list of census variables to retrieve (e.g., ["P1_001N", "P2_005N"]).
        year (int): The census year.
        dataset (str): The census dataset (e.g., "dec/pl", "acs/acs5").

    Returns:
        dict: A dictionary containing the retrieved data, or an error message.
    """

    base_url = f"https://api.census.gov/data/{year}/{dataset}"
    get_vars = ",".join(variables)

    # Determine the 'for' and 'in' parameters based on GEOID length
    geoid_len = len(geoid)
    if geoid_len == 15:  # Census Block
        for_param = f"block:{geoid[-4:]}"
        in_param = f"state:{geoid[0:2]}+county:{geoid[2:5]}+tract:{geoid[5:11]}"
    elif geoid_len == 11: # Census Tract
        for_param = f"tract:{geoid[-6:]}"
        in_param = f"state:{geoid[0:2]}+county:{geoid[2:5]}"
    elif geoid_len == 5: # County
        for_param = f"county:{geoid[-3:]}"
        in_param = f"state:{geoid[0:2]}"
    elif geoid_len == 2: # State
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

# Example usage:
block_geoid = "371830501003013" #Dallas County example
tract_geoid = "37183050100" #Dallas County example
county_geoid = "37183" #Dallas County example
state_geoid = "37" #Texas

variables_to_retrieve = ["P1_001N", "NAME"]  # Total Population, Geography name
block_data = get_census_data_by_geoid(block_geoid, variables_to_retrieve)
tract_data = get_census_data_by_geoid(tract_geoid, variables_to_retrieve)
county_data = get_census_data_by_geoid(county_geoid, variables_to_retrieve)
state_data = get_census_data_by_geoid(state_geoid, variables_to_retrieve)

print("Query GEOID = " + block_geoid)
print(f"Block Data: {block_data}")
print(f"Tract Data: {tract_data}")
print(f"County Data: {county_data}")
print(f"State Data: {state_data}")

# Example of using ACS data.
acs_vars = ["B01003_001E", "NAME"] #Total Population estimate from ACS.
acs_data = get_census_data_by_geoid(tract_geoid, acs_vars, year=2023, dataset="acs/acs5")
print(f"ACS Tract Data: {acs_data}")

