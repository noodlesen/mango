from flask import session, request, url_for, redirect, render_template, flash, abort
from . import geo
from .models import Place
from flask.ext.login import login_user, login_required, logout_user, current_user


from . .config import GOOGLE_ID, GOOGLE_SECRET, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from . .path import ROOT_DIR, UPLOAD_DIR
from . .toolbox import get_hash, how_long_ago
from . .mailer import Mailer

from sqlalchemy.sql import or_, and_
from sqlalchemy import desc
from datetime import datetime
import json


@geo.route('/places/id/<pid>', methods=['GET'])
def old_places(pid):
    p = Place.query.filter_by(fpid=pid).first()
    return render_template('place.html', place=p)
