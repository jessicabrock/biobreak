"""Main file for biobreak app"""
import os
import urllib
from uuid import uuid4
from flask import Flask, request, render_template, flash, redirect, jsonify, g, abort, session
import requests
import requests.auth
import json
import geocoder
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from geoalchemy2 import Geography, WKTElement
from model import User, Bathroom, Location, Comment, Rating, db, connect_to_db, BathroomData

REDDIT_CLIENT_ID = os.environ['RedditAppClientId']
CLIENT_SECRET = os.environ['RedditSecretKey']
GOOGLE_MAPS = os.environ['GoogleMapsAPIkey']
REDIRECT_URI = "http://0.0.0.0:5000/reddit_callback"
# REDDIT_USER = os.environ['RedditUser']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'seek_rhett'

@app.before_request
def before():
    """set variables for jinja"""
    g.googlemaps = GOOGLE_MAPS
    g.reddit = REDDIT_CLIENT_ID


@app.route('/')
def index():
    """Return homepage or query results"""
    return render_template("index.html")

@app.route('/index_maps.json')
def get_maps():
    """return markers to map"""
    data = {}
    lst = []
    location = request.args.get("searchRequest")
    if location == "":
        g_loc = geocoder.google("683 Sutter St., San Francisco, CA")
    else:
        g_loc = geocoder.google(location)

    latlng = g_loc.latlng

    point = "POINT({lng} {lat})".format(lat=latlng[0],lng=latlng[1])

    query = db.session.query(BathroomData).order_by(func.ST_Distance_Sphere( \
            point, BathroomData.lnglat) < 10000).filter(func.ST_Distance_Sphere( point, BathroomData.lnglat) < 10000).limit(5).all()

    for rec in query:
        qry_comments = db.session.query(Comment).filter(Comment.bathroom_id==rec.bathroom_id).all()
        data = {"bathroom_id": rec.bathroom_id,
                "lat": rec.latitude, "lng": rec.longitude,
                "name": rec.name, "address": rec.street,
                "city": rec.city, "state": rec.state,
                "directions": rec.directions,
                "unisex": rec.unisex,
                "accessible": rec.accessible,
                "changing_table": rec.changing_table,
                "comments": [comment.comment for comment in qry_comments]}

        lst.append(data)
    results = {"data": lst}

    return jsonify(results)

@app.route('/login')
def login():
    """Sends user to the login/create account page"""
    return render_template("login.html")

@app.route('/logout')
def logout():
    """log user out"""
    session.pop('displayname', None)
    return render_template("index.html")

@app.route('/login_validate', methods=['POST'])
def login_validate():
    """validate users login credentials"""
    email = request.form.get('login_email')
    password = request.form.get('login_password')
    rem = request.form.get('rem')

    # check if email/password are in db
    verify_acct = User.verify_password(email, password)
    if verify_acct:
        # if rem == 'checked':
        #     # create cookie for user
        display_name = db.session.query(User.display_name).filter_by(
            email=email).first()[0]
        session['displayname'] = display_name

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
    new_user = User(fname=fname, lname=lname, email=email, pword=hashedpw, display_name=dname)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/')

@app.route('/check_email_exists.json')
def check_acct():
    """check if user has an existing account"""
    email = request.args.get("email")

    cnt = db.session.query(User).filter_by(email=email).count()
    if cnt > 0:
        status = {"status": True}
    else:
        status = {"status": False}

    return jsonify(status)

@app.route('/add_bathroom')
def add_bathroom():
    """Add a new bathroom"""
    return render_template("add_bathroom.html")

@app.route('/get_states.json')
def get_states():
    """return states"""
    states = {}
    s = db.session.query(State).all()
    for state in s:
        states[state.state_abbr] = state.state_full

    return jsonify(sorted(states))


# Reddit OAuth2
@app.route('/login_auth')
def login_auth():
    """Send user to Reddit for authorization"""
    text = '<a href="%s">Authenticate with reddit</a>'
    print text
    return text % make_authorization_url()

def make_authorization_url():
    """
        Generate a random string for the state parameter
        Save it for use later to prevent xsrf attacks
    """
    state = str(uuid4())
    # displayname = get_username(access_token)
    save_created_state(state)

    params = {"client_id": REDDIT_CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI,
              "duration": "temporary",
              "scope": "identity"}

    url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.urlencode(params)
    print url
    return url

def save_created_state(state):
    """Save credential to db"""
    pass


def is_valid_state(state):
    """check that state is valid"""
    if state != None:
        return True
    else:
        print "is_valid_state false"
        return False

@app.route('/reddit_callback')
def reddit_callback():
    """returned call from reddit"""
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # unrecognized request - deny permission
        abort(403)

    code = request.args.get('code')
    access_token = get_token(code)
    displayname = get_username(access_token)

    u = User(fname="???", lname="???", \
            email="???", pword="???", display_name=displayname,
            auth_token=access_token)
    db.session.add(u)
    db.session.commit()
    session['displayname'] = displayname

    return redirect('/')

def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    headers = {"user-agent": "chrome"}
    response = requests.post("https://ssl.reddit.com/api/v1/access_token",
                             auth=client_auth,
                             headers=headers,
                             data=post_data)

    token_json = response.json()

    return token_json["access_token"]

def get_username(access_token):
    headers = {"Authorization": "bearer " + access_token,
        "user-agent": "chrome"}
    response = requests.get("https://oauth.reddit.com/api/v1/me",
        headers=headers)

    me_json = response.json()
    return me_json['name']


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, host='0.0.0.0')
