import sys
from sqlalchemy.types import Numeric
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base() # it creates a Base class instance

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(250))


class Restaurant(Base):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    street = Column(String(95), nullable=True)
    city = Column(String(40), nullable=False)
    state = Column(String(2), nullable=False)
    zip = Column(String(10), nullable=True)
    lat = Column(String(10), nullable=True)
    lon = Column(String(10), nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize_restaurants(self):
        """Returns object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'lat': self.lat,
            'lon': self.lon
        }


class MenuItem(Base):
    __tablename__ = 'menu_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    course = Column(String(30))
    description = Column(String(250))
    price = Column(String(6))
    picture = Column(String(250), nullable=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    restaurant = relationship(Restaurant)
    user = relationship(User)


    @property
    def serialize_menu(self):
        """Returns object data in easily serializeable format"""
        return {
            'restaurant': self.restaurant_id,
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'course': self.course,
            'description': self.description,
            'picture': self.picture
        }


engine = create_engine('sqlite:///menuswithusers.db')

# Create the classes we created above as a table in the database
Base.metadata.create_all(engine)
