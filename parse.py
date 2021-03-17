import pickle
from geopy.geocoders import Nominatim
from time import sleep
import requests
from credentials import yelp_api_key, yelp_api_key2, yelp_api_key3
from credentials import google_api_key
import sys
import os
import json


# Creates a business object to store all data in one location
class Business:
    def __init__(self, name, fb_classifier, lat=0, lon=0, content=None):
        self.lat = lat
        self.lon = lon
        self.name = name
        self.fb_classifier = fb_classifier
        self.content = content

    def setCoord(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def setName(self, name, fbClassifier):
        self.name = name
        self.fb_classifier = fbClassifier

    def setContent(self, content):
        self.content = content

    def getContent(self):
        return self.content

    def getCoord(self):
        return self.lat, self.lon

    def getName(self):
        return self.name, self.fb_classifier

    def getAll(self):
        return self.name, self.fb_classifier, self.lat, self.lon

    def __str__(self):
        return "Name: " + self.name + " FB: " + self.fb_classifier + " Coord: (" + \
               str(self.lat) + "," + str(self.lon) + ")" + " Content: " + str(self.content)

# Merges all the stored group user data into one pickle file
# Unfortunately by hand
def mergeData():
    try:
        dataOne = pickle.load(open("people2.p", "rb"))
        dataTwo = pickle.load(open("peopleHobbies.p", "rb"))
        dataThree = pickle.load(open("peopleHobbies2.p", "rb"))
        dataFour = pickle.load(open("peopleHobbies3.p", "rb"))
        dataFive = pickle.load(open("peopleHobbies4.p", "rb"))
    except:
        print("Missing File")
        dataOne = dict()
        dataTwo = dict()
        dataThree = dict()
        dataFour = dict()
        dataFive = dict()

    mergedData = dict()
    for i,j in dataOne.items():
        mergedData[i] = j
    for i,j in dataTwo.items():
        mergedData[i] = j
    for i,j in dataThree.items():
        mergedData[i] = j
    for i,j in dataFour.items():
        mergedData[i] = j
    for i,j in dataFive.items():
        mergedData[i] = j

    # Stored in mergedData
    pickle.dump(mergedData, open("mergedData.p", "wb"))



# Turns the scraped data into dictionary with the following structure:
# key: random index, value: tuple of interests
# Parameter - fileName - output of mergedData() - mergedData.p
def turnLegible(fileName):
    try:
        db = pickle.load(open(fileName, "rb"))
    except:
        db = dict()

    newDb = dict()
    index = 0
    for i, j in db.items():
        temp = []
        s = j.split("\n")
        for i in range(0, int(len(s) / 2)):
            temp.append(Business(s[2 * i], s[2 * i + 1]))
        newDb[index] = temp
        index = index + 1
    pickle.dump(newDb, open(fileName, "wb"))

# Gets relevant OSM data and stores it into merged
# OSM/Nominatim proved to be unnecessary
def get_osm(fileName):
    try:
        db = pickle.load(open(fileName, "rb"))
    except:
        db = dict()

    nom = Nominatim(user_agent="TestAgent")
    dbValues = db.values()
    index = 0
    for value in dbValues:
        for v in value:

            try:
                n = nom.geocode(v.getName()[0])
            except:
                n = None

            if n is not None:
                data = n.raw
                if 'lat' in data:
                    lat = data['lat']
                    print(data['lat'])
                else:
                    lat = None

                if 'lon' in data:
                    lon = data['lon']
                    print(data['lon'])
                else:
                    lon = None
                v.setCoord(lat, lon)
        index = index + 1

    pickle.dump(db, open(fileName, "wb"))


# Used to filter Facebook classification to generalized terms
# Proved to be unnecessary from user bias
def filter(fileName):
    try:
        db = pickle.load(open(fileName, "rb"))
    except:
        db = dict()

    newDb = dict()

    with open('filter_names.txt', 'r') as file:
        lines = file.read().split("\n")

    # print(lines)
    filterDict = dict()
    for item in lines:
        temp = item.split("|")
        # print(temp)
        if len(temp) == 1:
            filterDict[temp[0]] = []
        elif len(temp) > 1:
            filterDict[temp[0]] = temp[1:]

    for i, j in db.items():
        s = set()
        for k in j:
            if k[1] in filterDict.keys():
                for index in range(0, len(filterDict[k[1]])):
                    s.add(filterDict[k[1]][index])
        newDb[i] = s
    pickle.dump(newDb, open("filtered_osm.p", "wb"))


# Get Yelp classification of hobbies
def add_yelp_data(fileName):
    try:
        data = pickle.load(open(fileName, "rb"))
    except:
        data = dict()

    try:
        parseIndex = pickle.load(open("parseIndex.p", "rb"))
    except:
        parseIndex = 0

    BUSINESS_SEARCH_ENDPOINT = "https://api.yelp.com/v3/businesses/search"
    BUSINESS_INFO_ENDPOINT = "https://api.yelp.com/v3/businesses/"
    # Make a new Developer Yelp Account and cycle through keys daily to classify as much as possible
    HEADER = {"Authorization": "bearer %s" % yelp_api_key2}

    # To checkpoint as Yelp only processes X amount of requests for Developer users
    index = 0
    for i, j in data.items():
        # If we reached the correct index from last checkpoint if there was one
        if index > parseIndex:
            print(index)
            for v in j:
                sleep(0.5)
                param = {'location': v.getName()[0]}
                lat, lon = v.getCoord()
                try:
                    # If we don't have OSM data
                    if lat == 0 and lon == 0:
                        r = requests.get(BUSINESS_SEARCH_ENDPOINT, params=param, headers=HEADER)
                    else:
                        # If we have OSM coordinate data
                        param['latitude'] = lat
                        param['longitude'] = lon
                        r = requests.get(BUSINESS_SEARCH_ENDPOINT, params=param, headers=HEADER)
                    d = r.json()
                    print(d)
                    if 'error' not in d:
                        if len(d['businesses']) != 0:
                            # Get business ID
                            id = d['businesses'][0]['id']
                            try:
                                # Get business info
                                r2 = requests.get(BUSINESS_INFO_ENDPOINT + id, headers=HEADER)
                                d = r2.json()
                                catNames = []
                                # Store category names into db
                                if 'categories' in d:
                                    for i in range(len(d['categories'])):
                                        catNames.append(d['categories'][i])
                                # Store
                                if len(catNames) != 0:
                                    v.setContent(catNames)
                                    print(v)
                            except:
                                pass
                    else:
                        # If access limited reached, then saves and breaks
                        if d['error']['code'] == 'ACCESS_LIMIT_REACHED':
                            pickle.dump(index, open("parseIndex.p", "wb"))
                            pickle.dump(data, open("addedCat.p", "wb"))
                            return
                except:
                    pass
            # Checkpoint and save
            if index % 10 == 0:
                pickle.dump(data, open("addedCat.p", "wb"))
        # For reaching the last checkpoint and general looping
        index = index + 1

    pickle.dump(data, open("addedCat.p", "wb"))


# Filtered Yelp hobbies that I personally don't believe classifies as a "Hobby"
# Might shift to allow for all in the future
def filter_yelp(fileName):
    filterList = ['Georgian', 'Religious Organizations', 'International Grocery', 'Wedding Planning', 'Kids Activities'
                  , 'Northeastern Brazilian', 'Summer Camps', 'Corsican', 'Yucatan', 'Food', 'Basque', 'Butcher', 'Pierogis'
                  , 'Jaliscan', 'CSA', 'ATV Rentals/Tours', 'Drugstores', 'Speakeasies', 'Real Estate Agents']

    # Index - [hobbies]
    filteredYelp = dict()

    d = pickle.load(open(fileName, "rb"))
    for i, j in d.items():
        for k in j:
            temp = k.getContent()
            temp2 = set()
            if temp is not None:
                for h in range(len(temp)):
                    if temp[h]['title'] not in filterList and temp[h]['title'] not in temp2:
                        temp2.add(temp[h]['title'])
                    #     # temp2.append(temp[h]['title'])
                    #
                    # if temp[h]['title'] not in s:
                    #     s.add(temp[h]['title'])
            if len(temp2) != 0:
                filteredYelp[i] = temp2

    pickle.dump(filteredYelp, open("filteredYelp.p", "wb"))


# Gets google data about a hobby
def get_google_data(locationName):

    locations = dict()

    # Geolocation
    try:
        location = requests.post("https://www.googleapis.com/geolocation/v1/geolocate?key=" + google_api_key)
        loc = location.json()
        latitude = loc['location']['lat']
        longitude = loc['location']['lng']
        print(str(latitude) + "," + str(longitude))
    except:
        print("404: Geo-locating failed")
        return

    invalid_status = ['ZERO_RESULTS', 'OVER_QUERY_LIMIT', 'REQUEST_DENIED', 'INVALID_REQUEST', 'UNKNOWN_ERROR']
    # Text Search Request
    try:
        params = {
            "query": locationName,
            "key": google_api_key,
            "location": str(latitude) + "," + str(longitude),
            "radius": str(1000)
        }
        r = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json?", params=params)
        j = r.json()
        if j['status'] not in invalid_status:
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

# Makes an embedded map from Google maps API to be stored into an iframe
def make_embedded_map(place_id):
    try:
        params = {
            "q": "place_id:" + place_id
        }
        MAP_MODE = "place"
        r = requests.get("https://www.google.com/maps/embed/v1/" + MAP_MODE + "?key=" + google_api_key + "&", params=params)
        return r.url
    except:
        print("Embedded Api Failed")
        return None

# Stores embedded map into pickle file
def get_maps(locations):
    if locations is not None:
        for key, value, in locations.items():
            locations[key]['map_url'] = make_embedded_map(locations[key]['place_id'])
        return locations
    else:
        print("Get Maps Failed")
        return None

# Example:
# print(get_maps(get_google_data("Ice Cream & Frozen Yogurt")))