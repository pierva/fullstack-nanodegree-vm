from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def response(self, status):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def redirect(self, location):
        self.send_response(303)
        self.send_header('Location', location)
        self.end_headers()

    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.response(200)
                index = open('front-end/index.html').read()
                self.wfile.write(index)
                print "Index sent"
                return
            if self.path.endswith("/hola"):
                response(200)
                hola = open('front-end/hola.html').read()
                self.wfile.write(hola)
                print "Index sent"
                return
            if self.path.endswith("/edit"):
                restaurantId = self.path.split("/")[2]
                self.response(200)
                page = open('front-end/edit-restaurant.html').read()
                restaurant = session.query(Restaurant).filter_by(id = restaurantId).one()
                if restaurant != []:
                    self.wfile.write(page.format(restaurant.id, restaurant.name))
                    return
            if self.path.endswith("/delete"):
                restaurantId = self.path.split("/")[2]
                self.response(200)
                page = open('front-end/delete-restaurant.html').read()
                restaurant = session.query(Restaurant).filter_by(id = restaurantId).one()
                if restaurant != []:
                    self.wfile.write(page.format(restaurant.name, restaurant.id))
                    return

            if self.path.endswith("/restaurants"):
                self.response(200)
                page = open('front-end/restaurants.html').read()
                restaurants = session.query(Restaurant).all()
                list = "\n".join("<p>{}</p>".format(restaurant.name) +
                        "<div><a href='/restaurants/{}/edit'>Edit</a>".format(restaurant.id) +
                        "&nbsp;&nbsp;<a href='/restaurants/{}/delete'>Delete</a></div><br>".format(restaurant.id)
                            for restaurant in restaurants)
                self.wfile.write(page.format(list))

            if self.path.endswith("restaurants/new"):
                self.response(200)
                form = open('front-end/new-restaurant.html').read()
                self.wfile.write(form)
                print "Sent new restaurant form"

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                # self.response(301)
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newRestaurant')
                newRestaurant = Restaurant(name = messagecontent[0])
                session.add(newRestaurant)
                session.commit()
                self.redirect('/restaurants')
                return
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('editedRestaurant')
                restaurantId = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id = restaurantId).one()
                if restaurant != []:
                    restaurant.name = messagecontent[0]
                    session.add(restaurant)
                    session.commit()
                    self.redirect('/restaurants')
                    return
            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                restaurantId = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id = restaurantId).one()
                if restaurant != []:
                    session.delete(restaurant)
                    session.commit()
                    self.redirect('/restaurants')
                    return
        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()
