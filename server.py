"""Main file for biobreak app"""
import os
from flask import Flask, request, render_template, flash, redirect, jsonify, g
import geocoder
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from geoalchemy2 import Geography, WKTElement
from model import User, Bathroom, Location, Comment, Rating, db, connect_to_db

REDDIT_CLIENT_ID = os.environ['RedditAppClientId']
CLIENT_SECRET = os.environ['RedditSecretKey']
GOOGLE_MAPS = os.environ['GoogleMapsAPIkey']
REDIRECT_URI = "http://0.0.0.0:5000/reddit_callback"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'seek_rhett'
@app.before_request
def before():
    g.googlemaps = GOOGLE_MAPS
    g.reddit = REDDIT_CLIENT_ID


@app.route('/')
def index():
    """Return homepage or query results"""
    # qry = request.args.get('txtSearch')

    # if qry is None:
    #     g_loc = geocoder.google("683 Sutter St., San Francisco, CA")
    #     latlng = g_loc.latlng
      #  print latlng
      #  latlng[1], latlng[0] = latlng[0], latlng[1]
      #  print latlng
        # query db
      #  query = db.session.query(Location).filter(ST_Within(            Location.lnglat, 'POINT(latlng)'))
  #      point = WKTElement('POINT({0} {1})'.format(latlng[0],latlng[1]), srid=4326)
        # point = "POINT({lng} {lat})".format(lat=latlng[0],lng=latlng[1])
        # query = db.session.query(Location).filter(func.ST_Distance_Sphere( \
        #         point, Location.lnglat) < 10000).limit(5).all()

        # testing
        # print query
        # for loc in query:
        #     print str(loc.longitude) + " " + str(loc.latitude)
        #     print loc.bathrooms.name
        #     print loc.street + " " + loc.city + ", " + loc.state
        #     print loc.directions
        #     print


    return render_template("index.html")


@app.route('/index_maps.json')
def get_maps():
    """return markers to map"""
    data = {}
    lst = []
    address = request.args.get("txtSearch")
    if address is None:
        g_loc = geocoder.google("683 Sutter St., San Francisco, CA")
        latlng = g_loc.latlng
        point = "POINT({lng} {lat})".format(lat=latlng[0],lng=latlng[1])
        query = db.session.query(Location).filter(func.ST_Distance_Sphere( \
                point, Location.lnglat) < 10000).limit(5).all()
        for rec in query:
            data = {"lat": rec.latitude, "lng": rec.longitude, \
                    "name": rec.bathrooms.name, "address": rec.street, \
                    "city": rec.city, "state": rec.state, \
                    "directions": rec.directions}
            lst.append(data)

    return jsonify(lst)

@app.route('/login')
def login():
    """Sends user to the login/create account page"""
    return render_template("login.html")

@app.route('/login_validate', methods=['POST'])
def login_validate():
    """validate users login credentials"""
    email = request.form.get('login_email')
    password = request.form.get('login_password')
    rem = request.form.get('rem')
    # check if email/password are in db
    if User.verify_password(email, password):
        if rem == 'checked':
            # create cookie for user
            pass
        Session['user_id'] = rec.user_id
        return redirect('/')
    else:
        msg = flash("Login Failed")
        return redirect('/login', msg)

@app.route('/create_acct', methods=['POST'])
def create_acct():
    """create new user account"""
    fname = request.form.get('first_name')
    lname = request.form.get('last_name')
    dname = request.form.get('display_name')
    email = request.form.get('email')
    pword = request.form.get('password')

    hashedpw = User.set_password(pword)
    new_user = User(fname, lname, email, hashedpw, dname)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/')

@app.route('/check_email_exists.json')
def check_acct():
    """check if user has an existing account"""
    email = request.args.get('email')
    cnt = db.session.query(User).filter_by(email=email).count()
    if cnt > 0:
        status = {"status": True}
    else:
        status = {"status": False}

    return jsonify(status)



# OAuth2 for Reddit
# @app.route('/login_auth')
# def login_auth():
#   """Send user to Reddit for authorization"""
#   text = '<a href="%s">Authenticate with reddit</a>'
#   return text % make_authorization_url()

# def make_authorization_url():
#   # Generate a random string for the state parameter
#   # Save it for use later to prevent xsrf attacks
#   from uuid import uuid4
#   state = str(uuid4())
#   save_created_state(state)
#   params = {"client_id": CLIENT_ID,
#         "response_type": "code",
#         "state": state,
#         "redirect_uri": REDIRECT_URI,
#         "duration": "temporary",
#         "scope": "identity"}

#   url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.urlencode(params)
#   return url

# def save_created_state(state):
#   """Save credential to db"""
#   pass

# def is_valid_state(state):
#   """check that state is valid"""
#   return True

# @app.route('/reddit_callback')
# def reddit_callback():
#   error = request.args.get('error', '')
#   if error:
#     return "Error: " + error
#   state = request.args.get('state', '')
#   if not is_valid_state(state):
#     # Oh no, this request wasn't started by us!
#     abort(403)
#   code = request.args.get('code')
#   # We'll change this next line in just a moment
#   return "got a code! %s" % code


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, host='0.0.0.0')
