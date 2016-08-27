# admin __init__.py

from flask import Blueprint

admin = Blueprint('admin', __name__, static_folder = 'static', template_folder = 'templates',  static_url_path='/admin/static')

from . import views

