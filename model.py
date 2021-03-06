"""model layer for application"""
# from collections import defaultdict
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import geoalchemy2
from flask_bcrypt import Bcrypt
from flask import Flask

# PostgreSQL database connection.
# Flask-SQLAlchemy helper library.
app = Flask(__name__)
db = SQLAlchemy()
bcrypt = Bcrypt(app)

class BathroomData(db.Model):
    """View of v_bathroom_data"""
    __tablename__ = "v_bathroom_data"

    bathroom_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    unisex = db.Column(db.Boolean)
    accessible = db.Column(db.Boolean)
    changing_table = db.Column(db.Boolean)
    street = db.Column(db.String(155))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    lnglat = db.Column(geoalchemy2.Geometry(geometry_type='POINT', srid=4326))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    directions = db.Column(db.String(2000))
    comment = db.Column(db.String(1024))
    user_id = db.Column(db.Integer)
    score = db.Column(db.Integer)

    def __repr__(self):
        """Provide useful representation when printed."""
        return ("{} {} {} {} {} {} {} {} {} {} {} {} {} {} {}".format(self.__class__.__name__, self.bathroom_id,
            self.name, self.unisex, self.accessible, self.changing_table,
            self.street, self.city, self.state, self.country, self.latitude,
            self.longitude, self.comment, self.user_id, self.score) )

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
    name = db.Column(db.String(150), nullable=False)
    unisex = db.Column(db.Boolean, nullable=True, default=False)
    accessible = db.Column(db.Boolean, nullable=True, default=False)
    changing_table = db.Column(db.Boolean, nullable=True, default=False)
    user_id = db.Column(db.Integer, nullable=True, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.now())
    update_dt = db.Column(db.DateTime, nullable=False,
        default=datetime.now(), onupdate=datetime.now())
    locations = db.relationship('Location', uselist=False)

    def __init__(self, name,
                 unisex=None,
                 accessible=None,
                 changing_table=None):
        """initial values"""
        self.name = name
        self.unisex = unisex
        self.accessible = accessible
        self.changing_table = changing_table

    def __repr__(self):
        """Provide useful representation when printed."""
        return "<Bathroom bathroom_id={} name={}>".format(self.bathroom_id, \
                    self.name)


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
    display_name = db.Column(db.String(25), nullable=True, \
        default=default_fname)
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.now())
    last_login_dt = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    # auth_token => FB, Twitter, etc
    auth_token = db.Column(db.String(255), nullable=True, unique=True)

    def __repr__(self):
        """Provide useful representation when printed."""
        return"<User user_id={} fname={} lname={} email={} \
            display_name={}>".format(self.user_id, self.fname, \
            self.lname, self.email, self.display_name)

    # def __init__(self, fname, lname, email, pword, \
    #             display_name=None, user_id=None):
    #     """initial values"""
    #     self.fname = fname
    #     self.lname = lname
    #     self.email = email
    #     # self.pword = self.set_password(pword)
    #     self.user_id = user_id
    #     if display_name:
    #         self.display_name = display_name

    @staticmethod
    def set_password(pword):
        """hash user password before storing in db"""
        # pwdhash = bcrypt.hashpw(pword.encode('utf-8'), bcrypt.gensalt(14))
        pwdhash = bcrypt.generate_password_hash(pword)
        return pwdhash

    @staticmethod
    def verify_password(email, pword):
        """verify user password"""
        hashedval = db.session.query(User.pword).filter_by(
            email=email).first()[0]

        if bcrypt.check_password_hash(hashedval, pword):
            return True
        else:
            print hashedval
            print hashedval.encode('utf-8')
            return False


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
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    directions = db.Column(db.String(2000), nullable=True)
    lnglat = db.Column(geoalchemy2.Geometry(geometry_type='POINT', srid=4326))
    # Define relationship to bathrooms
    bathrooms = db.relationship("Bathroom", foreign_keys=[bathroom_id], \
        uselist=False)

    __table_args__ = (
        db.CheckConstraint('latitude >= -90 and latitude <= 90', name='checklat'),
        db.CheckConstraint('longitude >= -180 and longitude <= 180', name='checklng'), {})

    def __init__(self, bathroom_id, street, city, state, \
                    latitude, longitude, country=None, \
                    directions=None, lnglat=None):
        self.bathroom_id = bathroom_id
        self.street = street
        self.city = city
        self.state = state
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.directions = directions
        self.lnglat = lnglat

    def __repr__(self):
        """Provide useful representation when printed."""
        return "<Location location_id={} bathroom_id={} street={} city={} \  state={} latitude={} longitude={}".format(self.location_id, \
            self.bathroom_id, self.street, self.city, self.state, \
            self.latitude, self.longitude)

        """
            No __init__ location should be created from \
            'add_bathroom_loc' method in Bathroom class
        """

class Comment(db.Model):
    """Comments table"""
    __tablename__ = "comments"

    comment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bathroom_id = db.Column(db.Integer, db.ForeignKey('bathrooms.bathroom_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), \
        nullable=False)
    comment = db.Column(db.String(1024), nullable=False)
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
        return "<Comment comment_id={} bathroom_id={} user_id={} \
                comment={}".format(self.comment_id, self.bathroom_id, \
                self.user_id, self.comment)

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
        return "<Rating rating_id={} bathroom_id={} user_id={} \
                score={}".format(self.rating_id, self.bathroom_id, \
                self.user_id, self.score)


class State(db.Model):
    """States table"""
    __tablename__ = 'states'

    state_abbr = db.Column(db.String(2), primary_key=True)
    state_full = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        """internal representation of object State"""
        return ("{} {} {}".format(self.__class__.__name__,
            self.state_abbr,
            self.state_full ))

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
    connect_to_db(app)
    db.create_all()
    print "Connected to DB."
