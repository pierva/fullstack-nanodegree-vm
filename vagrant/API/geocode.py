import json
import config
import requests

def getGeocodeLocation(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    params = {
                'sensor': 'false',
                'address': address,
                'key' : config.GEOCODER_API_KEY
             }
    r = requests.get(url, params=params)
    results = r.json()
    if results['status'] == 'OK':
        location = results['results'][0]['geometry']['location']
        return location
    else:
        return results['status']
