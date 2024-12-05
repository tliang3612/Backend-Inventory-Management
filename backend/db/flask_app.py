from contextlib import contextmanager
from datetime import timedelta
import secrets

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) #clears session after certain amount of time
app.config['SESSION_COOKIE_HTTPONLY'] = True # makes cookies accessible through http requests only
app.config['SESSION_COOKIE_SECURE'] = True # secures sending of cookies
