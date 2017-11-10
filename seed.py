import json, urllib, requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from model import Bathroom, User, Location, Rating, Comment, db, connect_to_db

def load_data():
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
                      city=v['city'], state=v['state'],
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
    else:
      break

    return "finished loading data"

# test that data is there
result = db.session.query(Bathroom.name).first()
print result[0] # pragma: no cover

if __name__ == '__main__':
    import os
    app = Flask(__name__)
    os.system("dropdb testdb")
    os.system("createdb testdb")

    connect_to_db(app)

    # Make our tables
    db.create_all()
    u = User(user_id=0, fname="refuge",lname="restrooms",email="whatever@refugerestrooms.com",pword="letmein")
    db.session.add(u)
    db.session.commit()
    # load data into db
    load_data()
