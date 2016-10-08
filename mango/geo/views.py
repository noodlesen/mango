import json
from datetime import datetime
from operator import itemgetter

from flask import session, request, url_for, redirect, render_template, flash, abort
from flask.ext.login import login_user, login_required, logout_user, current_user
from sqlalchemy.sql import or_, and_
from sqlalchemy import desc
from . .cache import cache

from . import geo
from .models import Place, Tip, Tag
from . .social.models import User, UsersRelationship, Notification, UserToPlaceRelationship
from . .config import GOOGLE_ID, GOOGLE_SECRET, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from . .path import ROOT_DIR, UPLOAD_DIR
from . .toolbox import get_hash, how_long_ago
from . .mailer import Mailer
from . .db import db


# def get_tips_data(obj):
#     # NON CACHED
#     td = {}
#     td['tips']=[]
#     related_users_ids = []
#     if current_user.is_authenticated:
#         faves = Tip.favorited_by(current_user)
#         likes = Tip.liked_by(current_user)
#         dislikes = Tip.disliked_by(current_user)
#     else:
#         faves = []
#         likes = []
#         dislikes = []
#     for t in obj.tips:
#         favorite = True if t.id in faves else False
#         like = True if t.id in likes else False
#         dislike = True if t.id in dislikes else False
#         comments = json.loads(t.comments) if t.comments else []
#         for c in comments:
#             related_users_ids.append(c['author_id'])
#         tip = {"text":t.text, 
#                 "tags":[],
#                 "author":{'id':t.user.id, 'name':t.user.nickname},
#                 'id':t.id,
#                 'favorite':favorite,
#                 'like':like,
#                 'dislike':dislike,
#                 'comments': comments,
#                 'upvoted': t.chd_upvoted,
#                 'downvoted': t.chd_downvoted,
#                 'url': url_for('geo.single_tip', tid=t.id, _external = True)
#                 }
                
#         for tag in t.tags:
#             tip['tags'].append({"id": tag.id,
#                                 "name": tag.name,
#                                 "style": tag.style,
#                                 "count": tag.count
#                 })
#         td['tips'].append(tip)
    
#     place_tags=[]
#     for t in td['tips']:
#         for tag in t['tags']:
#             if tag not in place_tags:
#                 place_tags.append(tag)
#     td['place_tags'] = sorted(place_tags, key=itemgetter('count'), reverse=True)

#     td['related_users']=[]
#     ru = User.query.filter(User.id.in_(related_users_ids)).all()
#     for u in ru:
#         td['related_users'].append({"id": u.id, "nickname": u.nickname})

#     return td

def get_tips_data(obj):
    # CACHED
    td = {}
    td['tips']=[]
    related_users_ids = []
    if current_user.is_authenticated:
        faves = Tip.favorited_by(current_user)
        likes = Tip.liked_by(current_user)
        dislikes = Tip.disliked_by(current_user)
    else:
        faves = []
        likes = []
        dislikes = []
    for t in obj.tips:
        favorite = True if t.id in faves else False
        like = True if t.id in likes else False
        dislike = True if t.id in dislikes else False
        comments = json.loads(t.comments) if t.comments else []
        chd_data = t.chd_data
        if not chd_data:
            t.cache_it()
            chd_data = t.chd_data
        cached_data = json.loads(chd_data)
        for c in comments:
            related_users_ids.append(c['author_id'])
        tip = {"text":t.text, 
                "tags":[],
                "author":{'id':cached_data['author']['id'], 'name':cached_data['author']['name']},
                'id':t.id,
                'favorite':favorite,
                'like':like,
                'dislike':dislike,
                'comments': comments,
                'upvoted': t.chd_upvoted,
                'downvoted': t.chd_downvoted,
                'url': url_for('geo.single_tip', tid=t.id, _external = True)
                }
                
        tip['tags'] = cached_data['tags']
        td['tips'].append(tip)
    
    place_tags=[]
    for t in td['tips']:
        for tag in t['tags']:
            if tag not in place_tags:
                place_tags.append(tag)
    td['place_tags'] = sorted(place_tags, key=itemgetter('count'), reverse=True)

    td['related_users']=[]
    ru = User.query.filter(User.id.in_(related_users_ids)).all()
    for u in ru:
        td['related_users'].append({"id": u.id, "nickname": u.nickname})

    return td


#  PLACE ROUTES =========================================================

# LEGACY URLS SUPPORT
@geo.route('/places/id/<pid>', methods=['GET'])
def old_places(pid):
    p = Place.query.filter_by(fpid=pid).first()
    if p:
        return redirect(url_for('geo.places', us=p.url_string))
    else:
        abort(404)


#@cache.cached(50)
@geo.route('/place/<us>', methods=['GET'])
def places(us):
    p = Place.query.filter_by(url_string=us).first()
    if p:
        jd ={}
        
        td = get_tips_data(p)

        jd.update(td)

        all_tags = Tag.query.order_by(desc(Tag.count)).all()
        jd['all_tags']=[]
        for t in all_tags:
            jd['all_tags'].append({"name":t.name, "style":t.style, "count":t.count})


        jd['mode'] = 'place'

        subscribed = False
        if current_user.is_authenticated:
            u2p = UserToPlaceRelationship.query.filter_by(user_id=current_user.id, place_id=p.id).first()
            if u2p:
                subscribed = True

        return render_template('place.html', 
                                place=p, 
                                json_data=json.dumps(jd), 
                                airports=p.get_airports(),
                                signed=current_user.is_authenticated,
                                subscribed=subscribed
                                )

    else:
        abort(404)


@geo.route('/place-subscribe', methods=['POST'])
def place_subscribe():
    q = request.json
    pid = q['pid']
    res = {}
    if current_user.is_authenticated:
        u2p = UserToPlaceRelationship.query.filter_by(user_id=current_user.id, place_id=pid).first()
        if q['cmd'] == 'subscribe' and not u2p:
            u2p = UserToPlaceRelationship()
            u2p.user_id = current_user.id
            u2p.place_id = pid
            u2p.type = 'S'
            db.session.add(u2p)
            db.session.commit()
            res['status'] = 'ok'
        elif q['cmd'] == 'unsubscribe' and u2p:
            db.session.delete(u2p)
            db.session.commit()
            res['status'] = 'ok'

    return json.dumps(res)





# @login_required
# @geo.route('/json/place', methods=['POST'])
# def json_place():
#     res={}
#     q = request.json
#     place_id = q['place_id']
#     p = Place.query.get(place_id)
#     res['tips']=[]
#     if current_user.is_authenticated:
#         faves = Tip.favorited_by(current_user)
#         likes = Tip.liked_by(current_user)
#         dislikes = Tip.disliked_by(current_user)
#     else:
#         faves = []
#         likes = []
#         dislikes = []
#     for t in p.tips:
#         favorite = True if t.id in faves else False
#         like = True if t.id in likes else False
#         dislike = True if t.id in dislikes else False
#         comments = json.loads(t.comments) if t.comments else []
#         tip = {"text":t.text, 
#                 "tags":[],
#                 "author":{'id':t.user.id, 'name':t.user.nickname},
#                 'id':t.id,
#                 'favorite':favorite,
#                 'like':like,
#                 'dislike':dislike,
#                 'comments': comments
#                 }
#         for tag in t.tags:
#             tip['tags'].append({"id": tag.id,
#                                 "name": tag.name,
#                                 "style": tag.style,
#                                 "count": tag.count
#                 })
#         res['tips'].append(tip)
    
#     place_tags=[]
#     for t in res['tips']:
#         for tag in t['tags']:
#             if tag not in place_tags:
#                 place_tags.append(tag)
#     all_tags = Tag.query.order_by(desc(Tag.count)).all()
#     res['all_tags']=[]
#     for t in all_tags:
#         res['all_tags'].append({"name":t.name, "style":t.style, "count":t.count})
#     res['place_tags'] = sorted(place_tags, key=itemgetter('count'), reverse=True)
#     res['status']='ok'

#     return json.dumps(res)


#  TIP ROUTES =========================================================

@geo.route('/tip/<tid>', methods=['GET'])
def single_tip(tid):
    tip = Tip.query.get(tid)
    if tip:
        return render_template('single_tip.html', tip=tip)
    else:
        abort(404)


@login_required
@geo.route('/json/tip', methods=['POST'])
def json_tip():
    
    q = request.json
    res={"status":"ok"}

    if current_user.is_authenticated:
        if q['cmd']=='setFavorite':
            tip = Tip.query.get(q['id'])
            if q['value'] is True:
                tip.set_as_favorite(current_user)
            else:
                tip.remove_favorite(current_user)

        elif q['cmd']=='clickUpVote':
            tip = Tip.query.get(q['id'])
            if q['selected']=="none":
                tip.set_like(current_user)
            elif q['selected']=="upVote":
                tip.remove_like(current_user)
            elif q['selected']=="downVote":
                tip.remove_dislike(current_user)
                tip.set_like(current_user)
            res['upvoted']=tip.chd_upvoted
            res['downvoted']=tip.chd_downvoted

        elif q['cmd']=='clickDownVote':
            tip = Tip.query.get(q['id'])
            if q['selected']=="none":
                tip.set_dislike(current_user)
            elif q['selected']=="downVote":
                tip.remove_dislike(current_user)
            elif q['selected']=="upVote":
                tip.remove_like(current_user)
                tip.set_dislike(current_user)
            res['upvoted']=tip.chd_upvoted
            res['downvoted']=tip.chd_downvoted

        elif q['cmd']=='addComment':
            tip = Tip.query.get(q['id'])
            comments = json.loads(tip.comments) if tip.comments else []
            ts = (datetime.utcnow().strftime('%y %m %d %H %M %S'))
            comments.append({"text":q['text'], "author_id":current_user.id, "timestamp":ts})
            
            tip.comments = json.dumps(comments)
            res['comments'] = comments
            db.session.add(tip)
            db.session.commit()


        elif q['cmd']=='addNew':
            tip = Tip()
            tip.text = q['text'].strip()
            tip.user_id = current_user.id
            tip.place_id = q['placeID']
            tag_names = q['tags']

            if tip.text!='' and len(tag_names)>0:
                for tn in tag_names:
                    tag = Tag.query.filter_by(name=tn['name']).first()
                    if tag:
                        tip.tags.append(tag)
                        
                    else:
                        new_tag = Tag()
                        new_tag.name = tn['name']
                        new_tag.style = tn['style']
                        new_tag.count = 1
                        db.session.add(new_tag)
                        tip.tags.append(new_tag)
                        
                db.session.add(tip)
                db.session.commit()
                res['tip_data']={'author_name': current_user.nickname, 'author_id':current_user.id, 'tip_id': tip.id}


            subscribed_users = UsersRelationship.query.filter_by(user2=current_user.id, follows=True)
            for su in subscribed_users:
                Notification.add(
                                su.user1, 
                                'NP', 
                                'Новый совет от '+current_user.nickname, 
                                data=tip.text[:100]+"...", 
                                user_from=current_user.id,
                                extra={"tip_url": url_for('geo.single_tip', tid=tip.id)}
                                )

            subscribed_users = UserToPlaceRelationship.query.filter_by(place_id=tip.place_id)
            for su in subscribed_users:
                Notification.add(
                                su.user_id, 
                                'NP', 
                                tip.place.rus_name+': добавлен новый совет', 
                                data=tip.text[:100]+"...", 
                                user_from=current_user.id,
                                extra={"tip_url": url_for('geo.single_tip', tid=tip.id)}
                                )



    else:
        res['status']='error: not logged in'

    
    return json.dumps(res)






