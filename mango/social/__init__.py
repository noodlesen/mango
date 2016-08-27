# social __init__.py

from flask import Blueprint

from flask_oauthlib.client import OAuth

social = Blueprint('social', __name__, static_folder = 'static', template_folder = 'templates', static_url_path='/social/static')
oauth = OAuth()
from . import views


