import os
import requests
import unicodedata
from flask import Flask, request, url_for, flash, render_template, redirect, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import exc

#Fake Restaurants
# restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}
# restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers',
#                 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [{'name':'Cheese Pizza', 'description':'made with fresh cheese',
          'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake',
          'description':'made with Dutch Chocolate', 'price':'$3.99',
          'course':'Dessert','id':'2'},{'name':'Caesar Salad',
          'description':'with fresh organic vegetables','price':'$5.99',
          'course':'Entree','id':'3'},{'name':'Iced Tea',
          'description':'with lemon','price':'$.99', 'course':'Beverage',
          'id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach',
          'price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese',
        'price':'$5.99','course' :'Entree', 'id':'1'}

GEOCODER_API_KEY = 'AIzaSyAt6m54Qc8Vy40NayuNNYRkzcFhpi1OhYg'

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
