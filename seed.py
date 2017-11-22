"""Seed process for populating db"""
import urllib
import requests
import time
import geoalchemy2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from model import Bathroom, User, Location, Rating, Comment, db, connect_to_db

def load_data():
    """pull data from API and load into db"""
    page_num = 1

    while True:
        url = "https://www.refugerestrooms.org:443/api/v1/restrooms.json?per_page=100&page=" + str(page_num)
        results = []
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json()
            page_num += 1
        # loop thru json data
        for v in results:
            # add bathroom and location
            b = Bathroom(name=v['name'], unisex=v['unisex'],
                    accessible=v['accessible'],
                    changing_table=v['changing_table'])
            db.session.add(b)
            db.session.commit()
            # add location
            if v['latitude'] == None or v['longitude'] == None:
                v['latitude'] = 0.00
                v['longitude'] = 0.00

                l = Location(bathroom_id=b.bathroom_id,street=v['street'],
                            city=v['city'], state=v['state'], \
                            country=v['country'], latitude=v['latitude'],
                            longitude=v['longitude'], directions=v['directions'])
                db.session.add(l)
                db.session.commit()
            # add comment
            if len(v['comment']) > 1:
                c = Comment(comment=v['comment'],
                            bathroom_id=b.bathroom_id,
                            user_id=0)
                db.session.add(c)
                db.session.commit()
            # add ratings
            if v['downvote'] == 1:
                r = Rating(bathroom_id=b.bathroom_id,
                           user_id= 0,
                           score=2)
            elif v['upvote'] == 1:
                r = Rating(bathroom_id=b.bathroom_id,
                           user_id= 0,
                           score=5)

            db.session.add(r)
            db.session.commit()
            time.sleep(1)
        else:
            break

    return "finished loading data"

def setup():
    with app.app_context():
        password = User.set_password('letmein')
        u = User(user_id=0, fname="refuge", lname="restrooms", \
            email="whatever@refugerestrooms.com", pword=password)
        db.session.add(u)
        db.session.commit()

if __name__ == '__main__':
    import os
    app = Flask(__name__)
    os.system("dropdb biobreak")
    os.system("createdb biobreak")
    import subprocess
    try:
        subprocess.check_call([
            'psql', '-q',
            '-U', 'vagrant',
            '-f', '/home/vagrant/src/projects/biobreak/cr_ext.sql',
            'biobreak'
        ])
    except subprocess.CalledProcessError, ex:
        print "Failed to invoke psql: {}".format(ex)

    connect_to_db(app)
    # Make our tables
    db.create_all()
    # create default user needed to seed data
    setup()

    # load data from API into db
    load_data()
    # test that data is there
    print "verify we have data:"
    result = db.session.query(Bathroom.name).first()
    print result[0] # pragma: no cover
