import json
import requests
import config
import sys
import codecs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

def getGeocodeLocation(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    params = {
                'sensor': 'false',
                'address': address,
                'key' : cofig.GEOCODER_API_KEY
             }
    r = requests.get(url, params=params)
    results = r.json()
    location = results['results'][0]['geometry']['location']
    return location

def getRestaurant(mealType, latLon):
    url = 'https://api.foursquare.com/v2/venues/search?'
    params = {
                'client_id': config.foursquare_client_id,
                'client_secret': config.foursquare_secret,
                'v': 20180323,
                'intent': 'browse',
                'radius': 50000,
                'll': latLon,
                'query': mealType
             }
    r = requests.get(url, params=params)
    results = r.json()
    print results
