import os
import config
import requests
import unicodedata
from flask import Flask, request, url_for, flash, render_template, redirect, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import exc

# libraries import for user authenthication
from flask import session as login_session
import random, string

# Google oauth2 libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# authenthication libraries
import httplib2
import json
from flask import make_response

GEOCODER_API_KEY = config.GEOCODER_API_KEY

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
engine = engine = create_engine('sqlite:///menus.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

def geocoder(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    params = {
                'sensor': 'false',
                'address': address,
                'key' : GEOCODER_API_KEY
             }
    r = requests.get(url, params=params)
    results = r.json()
    location = results['results'][0]['geometry']['location']
    return location

def formatAddress(formValues):
    address = """{street},', {city},',{state},',{zip}""".format(
              street = formValues['street'],
              city = formValues['city'],
              state = formValues['state'],
              zip = formValues['zip'])
    return address.replace(" ", "+")


# Create a state token to prevent requests forgery
# Store it in the session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 75px;-webkit-border-radius: 75px;-moz-border-radius: 75px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


#DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#  API Routes (GET requests)
@app.route('/restaurants/JSON')
def restaurantMenusJSON():
    try:
        session = DBSession()
        restaurants = session.query(Restaurant).all()
        return jsonify(Restaurant=[r.serialize_restaurants for r in restaurants])
    except Exception as e:
        return jsonify({"status": 500, "message": "Server error", "e": e.message})

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def menuJSON(restaurant_id):
    try:
        session = DBSession()
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
        return jsonify(Restaurant=restaurant.serialize_restaurants,
                       Menu=[i.serialize_menu for i in items])
    except Exception as e:
        return jsonify({"status": 500, "message": "Server error", "e": e.message})

@app.route('/restaurants/<int:restaurant_id>/menu/<int:item_id>/JSON')
def menuItemJSON(restaurant_id, item_id):
    try:
        session = DBSession()
        item = session.query(MenuItem).filter_by(restaurant_id = restaurant_id,
            id = item_id).one()
        return jsonify(MenuItem=item.serialize_menu)
    except Exception as e:
        return jsonify({"status": 500, "message": "Server error", "e": e.message})

@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    session = DBSession()
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = restaurants)


@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'GET':
        return render_template('newRestaurant.html', restaurant=[])
    elif request.method == 'POST':
        try:
            if request.form['submit'] == 'VALIDATE':
                address = formatAddress(request.form)
                location = geocoder(address)
                return render_template('newRestaurant.html', restaurant = request.form, location=location)
            elif request.form['submit'] == 'ADD':
                if not request.form['lat'] or request.form['lon']:
                    flash("Please validate address before adding restaurant.")
                    return redirect(url_for('newRestaurant'))
                else:
                    session = DBSession()
                    newRestaurant = Restaurant(name = request.form['name'],
                    street = request.form['street'],
                    city = request.form['city'],
                    state = request.form['state'],
                    zip = request.form['zip'],
                    lat = request.form['lat'],
                    lon = request.form['lon'])
                    session.add(newRestaurant)
                    session.commit()
                    flash("New restaurant succesfully added!")
                    return redirect(url_for('showRestaurants'))
        except Exception as e:
            render_template('error.html',
                            errMessage='Unable to add the restaurant')



@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    session = DBSession()
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form['submit'] == 'VALIDATE':
            address = formatAddress(request.form)
            location = geocoder(address)
            restaurant.street = request.form['street']
            restaurant.city = request.form['city']
            restaurant.state = request.form['state']
            restaurant.zip = request.form['zip']
            restaurant.lat = location['lat']
            restaurant.lon = location['lng']
            return render_template('editRestaurant.html',
                                    restaurant_id=restaurant.id,
                                    restaurant=restaurant)
        elif request.form['submit'] == 'EDIT':
            try:
                if request.form['name']:
                    restaurant.name = request.form['name']
                session.add(restaurant)
                session.commit()
                flash("{} succesfully updated!".format(restaurant.name))
                return redirect(url_for('showRestaurants'))
            except Exception as e:
                    render_template('error.html',
                                    errMessage='Unable to save the changes')
    else:
        try:
            return render_template('editRestaurant.html',
                                    restaurant_id=restaurant.id,
                                    restaurant=restaurant)
        except Exception as e:
            return render_template('error.html',
                                    errMessage="Unable to open the update page.")

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    try:
        session = DBSession()
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        if request.method == 'POST':
            session.delete(restaurant)
            session.commit()
            flash("{} sadly deleted from the database.".format(restaurant.name))
            return redirect(url_for('showRestaurants'))
        else:
            return render_template('deleteRestaurant.html', restaurant_id=restaurant_id,
                restaurant=restaurant)
    except exc.SQLAlchemyError as e:
        return render_template('error.html',
                                errMessage="Error while fetching data from the database.")

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    try:
        session = DBSession()
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menuItems = session.query(MenuItem).filter_by(
            restaurant_id=restaurant.id).all()
        return render_template('menu.html', restaurant=restaurant,
                                menuItems = menuItems)
    except exc.SQLAlchemyError as e:
        return render_template('error.html',
            errMessage="Error while fetching data from the database.")


@app.route('/restaurant/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    try:
        session = DBSession()
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        if request.method == 'POST':
            newItem = MenuItem(name = request.form['name'],
                               price = request.form['price'],
                               course = request.form['course'],
                               description = request.form['description'],
                               picture = request.form['picture'],
                               restaurant_id = restaurant.id)
            session.add(newItem)
            session.commit()
            flash("{} succesfully added in {}'s menu.".format(
                newItem.name, restaurant.name))
            return redirect(url_for('showMenu', restaurant_id=restaurant.id))
        else:
            return render_template("newMenuItem.html", restaurant=restaurant)
    except exc.SQLAlchemyError as e:
        return render_template('error.html',
            errMessage="Error while fetching data from the database.")


@app.route('/restaurant/<int:restaurant_id>/<int:item_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, item_id):
    try:
        session = DBSession()
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        item = session.query(MenuItem).filter_by(id=item_id).one()
        if request.method == 'POST':
            item.name = request.form['name']
            item.price = request.form['price']
            item.course = request.form['course']
            item.description = request.form['description']
            item.picture = request.form['picture']
            session.add(item)
            session.commit()
            flash("{} succesfully updated in {}'s menu.".format(
                item.name, restaurant.name))
            return redirect(url_for('showMenu', restaurant_id=restaurant.id))
        else:
            return render_template('editMenuItem.html', restaurant=restaurant,
                                   item= item)
    except exc.SQLAlchemyError as e:
        return render_template('error.html',
            errMessage="Error while communicating with the database.\n" + e.message)

@app.route('/restaurant/<int:restaurant_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, item_id):
    try:
        session = DBSession()
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        item = session.query(MenuItem).filter_by(id=item_id).one()
        if request.method == 'POST':
            session.delete(item)
            session.commit()
            flash("{} in {}'s menu sadly deleted.".format(
                item.name, restaurant.name))
            return redirect(url_for('showMenu', restaurant_id=restaurant.id))
        else:
            return render_template('deleteMenuItem.html', restaurant=restaurant, item = item)
    except exc.SQLAlchemyError as e:
        return render_template('error.html',
            errMessage="Error while communicating with the database.\n" + e.message)




if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
