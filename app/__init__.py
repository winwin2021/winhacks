import os
from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_migrate import Migrate
from tempfile import mkdtemp
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) #db rep database
migrate = Migrate(app, db) #rep migration engine
# to ensure templates are autoreloaded

app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# initializing flask-login

login = LoginManager(app)
login.login_view = 'login'
from app import routes, models
#models define structure of database
