import json
import urllib
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from model import Bathroom, User, Location, Rating, Comment, db, connect_to_db


# db = SQLAlchemy()

# def connect_to_db(app):
#     """Connect to database."""

#     app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///testdb"
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     db.app = app
#     db.init_app(app)

def load_data():
    """load data from api"""
    url = "https://www.refugerestrooms.org:443/api/v1/restrooms.json"
    results = []

    response = requests.get(url)
    # print response.status_code
    results = response.json()

    # load data
    if response.status_code == 200:
      for v in results:
        # add bathroom and location
        # import pdb; pdb.set_trace()
        b = Bathroom(name=v['name'], unisex=v['unisex'], accessible=v['accessible'], changing_table=v['changing_table'])
        db.session.add(b)
        db.session.commit()
        if v['latitude'] != None and v['longitude'] != None:
          l = Location(bathroom_id=b.bathroom_id,street=v['street'],
                      city=v['city'], state_abbr=v['state'],
                      country=v['country'], latitude=v['latitude'],
                      longitude=v['longitude'], directions=v['directions'])
          db.session.add(l)
          db.session.commit()
        # add comment
        if v['comment'] != None:
          c = Comment(comment=v['comment'],
                      bathroom_id=b.bathroom_id, user_id=0)
        # add to db and commit
        # because of fk relationships only need to add bathroom and comments
          db.session.add(c)
          db.session.commit()

if __name__ == '__main__':
    import os
    app = Flask(__name__)
    os.system("dropdb testdb")
    os.system("createdb testdb")

    connect_to_db(app)

    # Make our tables
    db.create_all()
    u = User(user_id=0, fname="refuge",lname="restrooms",email="whatever@loser.com",pword="letmein")
    db.session.add(u)
    db.session.commit()
    load_data()
