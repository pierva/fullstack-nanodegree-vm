import json
import requests
import config
import sys
import codecs

from geocode import getGeocodeLocation

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

def getRestaurant(mealType, latLon):
    url = 'https://api.foursquare.com/v2/venues/search?'
    params = {
                'client_id': config.foursquare_client_id,
                'client_secret': config.foursquare_secret,
                'v': config.foursquare_v,
                'intent': 'browse',
                'radius': 50000,
                'll': latLon,
                'query': mealType
             }
    r = requests.get(url, params=params)
    results = r.json()
    if results['meta']['code'] == 200:
        return results['response']['venues'][0]
    else:
        return "Error code %s.\n %s" % (results['meta']['code'], results['meta']['errorDetail'])

def getVenuePicture(venueId):
    url = 'https://api.foursquare.com/v2/venues/%s/photos?' % venueId
    params = {
                'client_id': config.foursquare_client_id,
                'client_secret': config.foursquare_secret,
                'v': config.foursquare_v,
                'limit': 10
             }
    r = requests.get(url, params=params)
    results = r.json()
    if results['meta']['code'] == 200:
        details = results['response']['photos']['items'][0]
        return details['prefix'] + "300x300" + details['suffix']
    else:
        return "Error code %s.\n %s" % (results['meta']['code'], results['meta']['errorDetail'])
