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
    __tablename__ = "bathrooms"

    bathroom_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    unisex = db.Column(db.Boolean, nullable=True, default=False)
    accessible = db.Column(db.Boolean, nullable=True, default=False)
    changing_table = db.Column(db.Boolean, nullable=True, default=False)
    user_id = db.Column(db.Integer, nullable=True, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    update_dt = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())

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
    __tablename__ = "users"

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

    def __init__(self, fname, lname, email, pword, display_name=None):
        """initial values"""
        self.fname = fname
        self.lname = lname
        self.email = email
        self.pword = self.set_password(pword)
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
    __tablename__ = "locations"

    location_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bathroom_id = db.Column(db.Integer, b.ForeignKey('bathrooms.bathroom_id'), nullable=False)
    street = db.Column(db.String(155), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state_abbr = db.Column(db.String(2), nullable=False)
    country = db.Column(db.String(50), nullable=True)
    latitude = db.Column(db.Double, nullable=False)
    longitude = db.Column(db.Double, nullable=False)
    directions = db.Column(db.String(512), nullable=True)
    # Define relationship to bathrooms
    bathrooms = db.relationship('Bathroom')
    CheckConstraint('latitude >= -90 and latitude <= 90', name='checklat')
    CheckConstraint('longitude >= -180 and longitude <= 180', name='checklng')



##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///bathrooms'
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
