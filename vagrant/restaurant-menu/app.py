import os
from flask import Flask, request, url_for, flash, render_template, redirect, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


app = Flask(__name__)
engine = engine = create_engine('sqlite:///menus.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    return 'This is the landing page'

@app.route('/restaurant/new')
def newRestaurant():
    return 'Create a new restaurant page'

@app.route('/restaurant/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
    return 'Edit the restaurant {}'.format(restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    return 'Delete the restaurant {}'.format(restaurant_id)

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    return 'This is the menu of restaurant {}'.format(restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/new')
def newMenuItem(restaurant_id):
    return 'Insert a new menu item'

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit')
def editMenuItem(restaurant_id, menu_id):
    return 'Edit the menu item {} for restuarant {}'.format(menu_id, restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete')
def deleteMenuItem(restaurant_id, menu_id):
    return 'Delete the menu item {} for restuarant {}'.format(menu_id, restaurant_id)




if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
