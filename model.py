from flask_sqlalchemy import SQLAlchemy
from bcrypt import hashpw, gensalt
import datetime
from collections import defaultdict
from flask import Flask

# PostgreSQL database connection.
# Flask-SQLAlchemy helper library.
db = SQLAlchemy()

class Bathroom(db.Model):
    """Bathroom table"""

    """
>>> Bathroom('sf city hall')
<Bathroom bathroom_id=None name=sf city hall>

>>> Bathroom()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: __init__() takes at least 2 arguments (1 given)
    """
    __tablename__ = "bathrooms"

    bathroom_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    unisex = db.Column(db.Boolean, nullable=True, default=False)
    accessible = db.Column(db.Boolean, nullable=True, default=False)
    changing_table = db.Column(db.Boolean, nullable=True, default=False)
    user_id = db.Column(db.Integer, nullable=True, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    update_dt = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, name, unisex=None,
                accessible=None, changing_table=None):
        """initial values"""
        self.name = name
        self.unisex = unisex
        self.accessible = accessible
        self.changing_table = changing_table


    def __repr__(self):
        """Provide useful representation when printed."""
        return"<Bathroom bathroom_id={} name={}>".format(self.bathroom_id, self.name)


class User(db.Model):
    """Users table"""

    """
>>> User('Lana','Del Rey','lana.delrey@google.com','letmein')
<User user_id=None fname=Lana lname=Del Rey email=lana.delrey@google.com display_name=None>

>>> User(email='mary.mcgoo@hotmail.com')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: __init__() takes at least 5 arguments (2 given)
    """
    __tablename__ = "users"

    # function needs to be defined before being referenced
    def default_fname(context):
        """default display_name if not provided"""
        return context.current_parameters.get('fname')

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    pword = db.Column(db.String(150), nullable=False)
    display_name = db.Column(db.String(25), nullable=True, default=default_fname)
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    last_login_dt = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        """Provide useful representation when printed."""
        return"<User user_id={} fname={} lname={} email={} display_name={}>".format(self.user_id, self.fname, self.lname, self.email, self.display_name)

    def __init__(self, fname, lname, email, pword,
                display_name=None, user_id=None):
        """initial values"""
        self.fname = fname
        self.lname = lname
        self.email = email
        self.pword = self.set_password(pword)
        self.user_id = user_id
        if display_name:
            self.display_name = display_name

    def set_password(self, pword):
        """hash user password before storing in db"""
        self.pwdhash = hashpw(pword, gensalt())
        return self.pwdhash

    def verify_password(self, pword):
        """verify user password"""
        return ".FIXME"

class Location(db.Model):
    """Locations table"""

    """
>>> Location(1,'683 Sutter Ave.','San Francisco','CA',37.773972, -122.431297)
<Location location_id=None bathroom_id=1 street=683 Sutter Ave. city=San Francisco state=CA latitude=37.773972 longitude=-122.431297

    """
    __tablename__ = "locations"

    location_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bathroom_id = db.Column(db.Integer, db.ForeignKey('bathrooms.bathroom_id'), nullable=False)
    street = db.Column(db.String(155), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state_abbr = db.Column(db.String(25), nullable=False)
    country = db.Column(db.String(50), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    directions = db.Column(db.String(512), nullable=True)
    # Define relationship to bathrooms
    bathrooms = db.relationship('Bathroom')

    __table_args__ = (
        db.CheckConstraint('latitude >= -90 and latitude <= 90', name='checklat'),
        db.CheckConstraint('longitude >= -180 and longitude <= 180', name='checklng'), {})

    def __init__(self, bathroom_id, street, city, state_abbr, latitude, longitude, country=None, directions=None):
        self.bathroom_id = bathroom_id
        self.street = street
        self.city = city
        self.state_abbr = state_abbr
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.directions = directions


    def __repr__(self):
        """Provide useful representation when printed."""
        return"<Location location_id={} bathroom_id={} street={} city={} state={} latitude={} longitude={}".format(self.location_id, self.bathroom_id, self.street, self.city, self.state_abbr, self.latitude, self.longitude)

        """
            No __init__ location should be created from 'add_bathroom_loc' method in Bathroom class
        """

class Comment(db.Model):
    """Comments table"""
    __tablename__ = "comments"

    comment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bathroom_id = db.Column(db.Integer, db.ForeignKey('bathrooms.bathroom_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    comment = db.Column(db.String(512), nullable=False)
    # Define relationship to bathrooms and users
    bathrooms = db.relationship('Bathroom')
    users = db.relationship('User')

    def __init__(self, bathroom_id, user_id, comment):
        """Inital values for comments"""
        self.bathroom_id = bathroom_id
        self.user_id = user_id
        self.comment = comment

    def __repr__(self):
        """Provide useful representation when printed."""
        return"<Comment comment_id={} bathroom_id={} user_id={} comment={}".format(self.comment_id, self.bathroom_id, self.user_id, self.comment)

class Rating(db.Model):
    """Ratings table"""
    __tablename__ = 'ratings'

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bathroom_id = db.Column(db.Integer, db.ForeignKey('bathrooms.bathroom_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    score = db.Column(db.Integer, db.CheckConstraint('score > 0 and score <= 5'), nullable=False)
    # Define relationship to bathrooms and users
    bathrooms = db.relationship('Bathroom')
    users = db.relationship('User')

    def __init__(self, bathroom_id, user_id, score):
        """Initial values for ratings"""
        self.bathroom_id = bathroom_id
        self.user_id = user_id
        self.score = score

    def __repr__(self):
        """Provide useful representation when printed."""
        return"<Rating rating_id={} bathroom_id={} user_id={} score={}".format(self.rating_id, self.bathroom_id, self.user_id, self.score)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///testdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # from server import app
    app = Flask(__name__)

    connect_to_db(app)
    db.create_all()
    print "Connected to DB."
