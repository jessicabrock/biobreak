from flask import Flask, request, render_template, flash, redirect
import urllib, os
from flask_sqlalchemy import SQLAlchemy
from model import User, Bathroom, Location, Comment, Rating, db, connect_to_db

CLIENT_ID = os.environ['RedditAppClientId']
CLIENT_SECRET = os.environ['RedditSecretKey']
REDIRECT_URI = "http://0.0.0.0:5000/reddit_callback"

app = Flask(__name__)
app.config['SECRET_KEY']='seek_rhett'
@app.route('/')
def index():
    """Return homepage."""

    return render_template("index.html")

@app.route('/login')
def login():
  """Sends user to the login/create account page"""
  return render_template("login.html")

@app.route('/login_validate', methods = ['POST'])
def login_validate():
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

@app.route('/login_auth')
def login_auth():
  """Send user to Reddit for authorization"""
  text = '<a href="%s">Authenticate with reddit</a>'
  return text % make_authorization_url()

def make_authorization_url():
  # Generate a random string for the state parameter
  # Save it for use later to prevent xsrf attacks
  from uuid import uuid4
  state = str(uuid4())
  save_created_state(state)
  params = {"client_id": CLIENT_ID,
        "response_type": "code",
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "duration": "temporary",
        "scope": "identity"}

  url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.urlencode(params)
  return url

def save_created_state(state):
  """Save credential to db"""
  pass

def is_valid_state(state):
  """check that state is valid"""
  return True

@app.route('/reddit_callback')
def reddit_callback():
  error = request.args.get('error', '')
  if error:
    return "Error: " + error
  state = request.args.get('state', '')
  if not is_valid_state(state):
    # Oh no, this request wasn't started by us!
    abort(403)
  code = request.args.get('code')
  # We'll change this next line in just a moment
  return "got a code! %s" % code


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, host='0.0.0.0')
