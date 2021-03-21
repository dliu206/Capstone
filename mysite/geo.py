from cred import credentials
import requests

def get_google_data(locationName):

    locations = dict()

    # Geolocate
    try:
        location = requests.post("https://www.googleapis.com/geolocation/v1/geolocate?key=" + credentials.google_api_key)
        loc = location.json()
        latitude = loc['location']['lat']
        longitude = loc['location']['lng']
    except:
        print("404: Geo-locating failed")
        return

    invalid_status = ['ZERO_RESULTS', 'OVER_QUERY_LIMIT', 'REQUEST_DENIED', 'INVALID_REQUEST', 'UNKNOWN_ERROR']
    # Text Search Request
    try:
        params = {
            "query": locationName,
            "key": credentials.google_api_key,
            # "location": str(longitude) + "," + str(latitude),
            "location": "47.608013" + "," + "-122.335167",
            "radius": str(1000)
        }
        r = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json?", params=params)
        j = r.json()
        if j['status'] not in invalid_status:
            # print(json.dumps(j, indent=2))
            index = 0
            if len(j['results']) < 3:
                for result in j['results']:
                    data = {}
                    if 'name' in result:
                        data['name'] = result['name']
                    if 'formatted_address' in result:
                        data['formatted_address'] = result['formatted_address']
                    if 'place_id' in result:
                        data['place_id'] = result['place_id']
                    else:
                        continue
                    if 'price_level' in result:
                        data['price_level'] = result['price_level']
                    if 'rating' in result:
                        data['rating'] = result['rating']
                    locations[index] = data
                    index = index + 1
            else:
                for i in range(3):
                    # name, address, place_id, price_level, rating
                    result = j['results'][i]

                    data = {}
                    if 'name' in result:
                        data['name'] = result['name']
                    if 'formatted_address' in result:
                        data['formatted_address'] = result['formatted_address']
                    if 'place_id' in result:
                        data['place_id'] = result['place_id']
                    else:
                        continue
                    if 'price_level' in result:
                        data['price_level'] = result['price_level']
                    if 'rating' in result:
                        data['rating'] = result['rating']
                    locations[i] = data
            return locations
        else:
            print('Invalid Status occurred')
            print(j['status'])
            return
    except:
        print("Error occurred")
        return

def make_embedded_map(place_id):
    try:
        params = {
            "q": "place_id:" + place_id
        }
        MAP_MODE = "place"
        r = requests.get("https://www.google.com/maps/embed/v1/" + MAP_MODE + "?key=" + credentials.google_api_key + "&", params=params)
        return r.url
    except:
        print("Embedded Api Failed")
        return None

def get_maps(locations):
    if locations is not None:
        for key, value, in locations.items():
            locations[key]['map_url'] = make_embedded_map(locations[key]['place_id'])
        return locations
    else:
        print("Get Maps Failed")
        return None
