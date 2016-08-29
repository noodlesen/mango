# geo __init__.py

from flask import Blueprint

geo = Blueprint('geo', __name__, static_folder = 'static', template_folder = 'templates', static_url_path='/geo/static')

from . import views


