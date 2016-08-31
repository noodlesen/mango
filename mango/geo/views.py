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
    if p:
        #return render_template('place.html', place=p)
        return redirect(url_for('geo.places', us=p.url_string))
    else:
        abort(404)

@geo.route('/place/<us>', methods=['GET'])
def places(us):
    p = Place.query.filter_by(url_string=us).first()
    if p:
        return render_template('place.html', place=p)
    else:
        abort(404)

@geo.route('/json/place', methods=['POST'])
def json_place():
    q = request.json
    place_id = q['place_id']
    p = Place.query.get(place_id)
    res={}
    res['tips']=[]
    for t in p.tips:
        tip = {"text":t.text, "tags":[]}
        for tag in t.tags:
            tip['tags'].append({"id": tag.id,
                                "name": tag.name,
                                "style": tag.style,
                                "count": tag.count
                })
        res['tips'].append(tip)
    place_tags=[]
    for t in res['tips']:
        print ('>>>>>>>>>>>>>>>>>>>>>>>')
        print (t)
        for tag in t['tags']:
            if tag not in place_tags:
                place_tags.append(tag)
    res['place_tags'] = place_tags
    res['status']='ok'
    return json.dumps(res)
