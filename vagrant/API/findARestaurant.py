import json
import requests
import config
import sys
import codecs

from geocode import getGeocodeLocation

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

def getRestaurant(mealType, latLon):
    #latLon is a string => '25.54654,-80.5834336'
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
        venues = results['response']['venues'][0]
        if len(venues) > 0:
            return results['response']['venues'][0]
        else:
            return 'No restaurants available.'
    else:
        return "Error code %s.\n %s" % (results['meta']['code'], results['meta']['errorDetail'])

def getVenuePicture(venueId):
    url = 'https://api.foursquare.com/v2/venues/%s/photos?' % venueId
    params = {
                'client_id': config.foursquare_client_id,
                'client_secret': config.foursquare_secret,
                'v': config.foursquare_v,
                'limit': 1
             }
    r = requests.get(url, params=params)
    results = r.json()
    if results['meta']['code'] == 200:
        details = results['response']['photos']['items']
        if len(details) > 0:
            return details[0]['prefix'] + "300x300" + details[0]['suffix']
        else:
            return 'https://doc-0s-1k-docs.googleusercontent.com/docs/securesc/ha0ro937gcuc7l7deffksulhg5h7mbp1/l05jvvf8tsrtagddeheq3tev685asuie/1551045600000/11804516247872681719/*/1PktSHS6Hz_TTkvVybb3bXZrfzMKjYnzl'
    else:
        return "Error code %s.\n %s" % (results['meta']['code'], results['meta']['errorDetail'])

def findARestaurant(mealType, location):
    coord = getGeocodeLocation(location)
    coordString = '{},{}'.format(coord['lat'], coord['lng'])
    restaurant = getRestaurant(mealType, coordString)
    picture = getVenuePicture(restaurant['id'])
    try:
        if 'name' in restaurant:
            print 'Restaurant Name: %s' % restaurant['name']
            if 'address' in restaurant:
                print 'Restaurant Address: %s' % restaurant['location']['address']
            elif len(restaurant['location']['formattedAddress']) > 0:
                print 'Restaurant Address: %s' % restaurant['location']['formattedAddress'][0]
            else:
                print 'Restaurant Address unavailable.'
            print 'Image: %s' % picture
            print '\n'
        else:
            print 'Somenthing when wrong. Unable to find a restaurant.\n'
    except Exception as e:
        print 'Error while processing your request.\n'

if __name__ == '__main__':
	findARestaurant("Pizza", "Tokyo, Japan")
	findARestaurant("Tacos", "Jakarta, Indonesia")
	findARestaurant("Tapas", "Maputo, Mozambique")
	findARestaurant("Falafel", "Cairo, Egypt")
	findARestaurant("Spaghetti", "New Delhi, India")
	findARestaurant("Cappuccino", "Geneva, Switzerland")
	findARestaurant("Sushi", "Los Angeles, California")
	findARestaurant("Steak", "La Paz, Bolivia")
	findARestaurant("Gyros", "Sydney, Australia")
