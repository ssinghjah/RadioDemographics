import requests

def get_elevation(lat, lng, api_key):
    url = "https://maps.googleapis.com/maps/api/elevation/json"
    params = {
        "locations": f"{lat},{lng}",
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        elevation = data['results'][0]['elevation']
        return elevation
    else:
        raise Exception(f"Error from API: {data['status']}")

# Example usage
lat = 36.578581
lng = -118.291994
api_key = "AIzaSyB5P8g-kF_ilnEJG0t5eS4dooBC5vOJeA8"  # Replace this with your actual API key

elevation = get_elevation(lat, lng, api_key)
print(f"Elevation at ({lat}, {lng}) is {elevation:.2f} meters")




