from flask import session, request, url_for, redirect, render_template, flash, abort
from . import geo
from .models import Place, Tip, Tag
from flask.ext.login import login_user, login_required, logout_user, current_user


from . .config import GOOGLE_ID, GOOGLE_SECRET, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from . .path import ROOT_DIR, UPLOAD_DIR
from . .toolbox import get_hash, how_long_ago
from . .mailer import Mailer
from . .db import db

from sqlalchemy.sql import or_, and_
from sqlalchemy import desc
from datetime import datetime
import json

from . .cache import cache

from operator import itemgetter



@geo.route('/places/id/<pid>', methods=['GET'])
def old_places(pid):
    p = Place.query.filter_by(fpid=pid).first()
    if p:
        #return render_template('place.html', place=p)
        return redirect(url_for('geo.places', us=p.url_string))
    else:
        abort(404)

#@cache.cached(50)
@geo.route('/place/<us>', methods=['GET'])
def places(us):
    p = Place.query.filter_by(url_string=us).first()
    if p:
        return render_template('place.html', place=p)
    else:
        abort(404)

@login_required
@geo.route('/json/place', methods=['POST'])
def json_place():
    res={}
    q = request.json
    place_id = q['place_id']
    p = Place.query.get(place_id)
    res['tips']=[]
    if current_user.is_authenticated:
        faves = Tip.favorited_by(current_user)
        likes = Tip.liked_by(current_user)
        dislikes = Tip.disliked_by(current_user)
    else:
        faves = []
        likes = []
        dislikes = []
    for t in p.tips:
        favorite = True if t.id in faves else False
        like = True if t.id in likes else False
        dislike = True if t.id in dislikes else False
        # if t.comments:
        #     comments = json.loads(t.comments)
        # else:
        #     comments = []
        comments = json.loads(t.comments) if t.comments else []
        tip = {"text":t.text, 
                "tags":[],
                "author":{'id':t.user.id, 'name':t.user.nickname},
                'id':t.id,
                'favorite':favorite,
                'like':like,
                'dislike':dislike,
                'comments': comments
                }
        for tag in t.tags:
            tip['tags'].append({"id": tag.id,
                                "name": tag.name,
                                "style": tag.style,
                                "count": tag.count
                })
        res['tips'].append(tip)
    
    place_tags=[]
    for t in res['tips']:
        for tag in t['tags']:
            if tag not in place_tags:
                place_tags.append(tag)
    all_tags = Tag.query.order_by(desc(Tag.count)).all()
    res['all_tags']=[]
    for t in all_tags:
        res['all_tags'].append({"name":t.name, "style":t.style, "count":t.count})
    res['place_tags'] = sorted(place_tags, key=itemgetter('count'), reverse=True)
    res['status']='ok'

    return json.dumps(res)


@login_required
@geo.route('/json/tip', methods=['POST'])
def json_tip():
    q = request.json
    res={}
    if q['cmd']=='setFavorite':
        res['status']='ok'
        tip = Tip.query.get(q['id'])
        if q['value'] is True:
            tip.set_as_favorite(current_user)
        else:
            tip.remove_favorite(current_user)


    elif q['cmd']=='clickAgree':
        res['status']='ok'
        tip = Tip.query.get(q['id'])
        if q['selected']=="none":
            tip.set_like(current_user)
        elif q['selected']=="agree":
            tip.remove_like(current_user)
        elif q['selected']=="disagree":
            tip.remove_dislike(current_user)
            tip.set_like(current_user)

    elif q['cmd']=='clickDisagree':
        res['status']='ok'
        tip = Tip.query.get(q['id'])
        if q['selected']=="none":
            tip.set_dislike(current_user)
        elif q['selected']=="disagree":
            tip.remove_dislike(current_user)
        elif q['selected']=="agree":
            tip.remove_like(current_user)
            tip.set_dislike(current_user)

    elif q['cmd']=='addComment':

        res['status']='ok'
        #try:
        tip = Tip.query.get(q['id'])
        comments = json.loads(tip.comments) if tip.comments else []
        ts = (datetime.utcnow().strftime('%y %m %d %H %M %S'))
        comments.append({"text":q['text'], "author_id":current_user.id, "timestamp":ts})
        
        tip.comments = json.dumps(comments)
        res['comments'] = comments
        db.session.add(tip)
        db.session.commit()
        print ("ADD COMMENT")

        #res['status']='error'

    
    return json.dumps(res)






