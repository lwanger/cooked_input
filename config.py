"""
config.py

Configuration file for flask app

author: Len Wanger
Copyright Impossible Objects, 2017

TODO:
"""


# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
SQLALCHEMY_DATABASE_URI = 'sqlite:///'

SQLALCHEMY_BINDS = {
    'users':     'sqlite:///' + os.path.join(BASE_DIR, 'users.db'),
    'builds':    'sqlite:///' + os.path.join(BASE_DIR, 'builds.db'),
    'part_nums': 'sqlite:///' + os.path.join(BASE_DIR, 'part_nums.db'),
    'inks':      'sqlite:///' + os.path.join(BASE_DIR, 'ink.db')
}

DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# This needs to be turned back on if models_committed or before_models_committed is used, otherwise keep it False.
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
# CSRF_SESSION_KEY = "secret"
CSRF_SESSION_KEY = "Impossible Silence"

# Secret key for signing cookies
# SECRET_KEY = "secret"
SECRET_KEY = "Loose Lips Sync Shyps!"
