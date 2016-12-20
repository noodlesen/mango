import json
from datetime import datetime
from operator import itemgetter
from alphabet_detector import AlphabetDetector

from flask import request, url_for, redirect, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import desc

from . import geo
from .models import Place, Tip, Tag, Country, Direction
from . .social.models import User, UsersRelationship, Notification, UserToPlaceRelationship
from . .db import db
from . .logger import Log

from . .dttools import NEVER

ad = AlphabetDetector()


def get_tips_data(tips_list, **kwargs):
    td = {}
    td['tips'] = []
    related_users_ids = []

    if current_user.is_authenticated:
        if "place_id" in kwargs:
            pa = current_user.get_place_actions(kwargs["place_id"])
        elif len(list(tips_list))>0:
            ids = [t.id for t in tips_list]
            pa = current_user.get_list_actions(ids)
    else:
        pa = {"favorites":[], "likes":[], "dislikes":[]}

    for t in tips_list:
        favorite = True if t.id in pa["favorites"] else False
        like = True if t.id in pa["likes"] else False
        dislike = True if t.id in pa["dislikes"] else False
        comments = json.loads(t.comments) if t.comments else []
        for c in comments:
            if current_user.is_authenticated:
                c["is_mine"]=True if c["author_id"] == current_user.id else False

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
                'rating': t.chd_upvoted - t.chd_downvoted,
                'url': url_for('root', _external=True)+cached_data['url'][1:],
                'place_name': cached_data['place']['name'],
                'country_name': cached_data['place']['country']
                }

        tip['tags'] = cached_data['tags']
        if 'featured' in kwargs and kwargs['featured'] == str(tip['id']):
            td['featured']=tip
        else:
            td['tips'].append(tip)

    td['tips'] = sorted(td['tips'], key=itemgetter('rating'), reverse=True)

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
    if current_user.is_authenticated:
        td['related_users'].append({"id": current_user.id, "nickname": current_user.nickname})

    return td


def get_all_tags():
    all_tags = Tag.query.order_by(desc(Tag.count)).all()
    res=[]
    for t in all_tags:
        res.append({"name":t.name, "style":t.style, "count":t.count})
    return res



#  PLACE ROUTES =========================================================


# LEGACY URLS SUPPORT
@geo.route('/places/id/<pid>', methods=['GET'])
def old_places(pid):
    Log.register(action='geo.route:legacy_place', data=pid)
    p = Place.query.filter_by(fpid=pid).first()
    if p:
        return redirect(url_for('geo.places', us=p.url_string)), 301
    else:
        abort(404)


@geo.route('/place/<us>', methods=['GET'])
def places(us):

    try:
        featured = request.args['t'] if request.args and request.args['t'] else -1
        canonical = url_for('geo.places', us=us, _external=True) if featured != -1 else ''
    except KeyError:
        return redirect(url_for('geo.places', us=us)), 301

    Log.register(action='geo.route:place', data=us)
    p = Place.query.filter_by(url_string=us).first()
    if p:
        jd ={}
        td = get_tips_data(p.tips, place_id=p.id, featured=featured)
        jd.update(td)
        jd['all_tags']= get_all_tags()
        jd['config'] = {
                        'mode': 'place'
        }

        subscribed = False
        if current_user.is_authenticated:
            u2p = UserToPlaceRelationship.query.filter_by(user_id=current_user.id, place_id=p.id).first()
            if u2p:
                subscribed = True

        modified_at = p.modified_at
        if not modified_at:
            modified_at = NEVER

        last_modified = datetime.strftime(modified_at, '%a, %d %b %Y %H:%M:%S GMT')

        return render_template('place.html',
                               place=p,
                               place_data = jd,
                               json_data=json.dumps(jd),
                               airports=p.get_airports(),
                               signed=current_user.is_authenticated,
                               subscribed=subscribed,
                               place_tags = jd["place_tags"],
                               featured=featured,
                               canonical=canonical
                               ), 200

    else:
        abort(404)


@geo.route('/place-subscribe', methods=['POST'])
def place_subscribe():
    Log.register(action='geo.post:place-subscribe', data=request.json)
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


@geo.route('/json/place-search', methods=['POST'])
def place_search():
    Log.register(action='geo.post:place-search', data=request.json)
    def get_places(field, needle):
        urlbase = url_for('geo.places', us='')
        places = []
        needle=needle.replace('"','')
        sql = """SELECT id, %s, `number`, url_string, chd_has_tips FROM G_places WHERE %s LIKE "%s%%"  ORDER BY `number` DESC LIMIT 25""" % (field, field, needle)
        results = db.session.execute(sql)
        for r in results:
            places.append({"id": r[0], "name": r[1], "number": r[2], "url": urlbase+r[3], "has_tips":r[4]})
        return places

    q = request.json
    res={"status":"ok", "places":[]}
    if ad.is_cyrillic(q['needle']):
        res['places'] = get_places('rus_name', q['needle'])
    else:
        res['places'].extend(get_places('eng_name', q['needle']))

    return json.dumps(res)



@login_required
@geo.route('/json/tip', methods=['POST'])
def json_tip():
    Log.register(action='geo.post:json_tip', data=request.json)

    q = request.json
    res={"status":"ok"}

    if current_user.is_authenticated:
        if q['cmd']=='setFavorite':
            tip = Tip.query.get(q['id'])
            if q['value'] is True:
                current_user.fave(tip)
            else:
                current_user.remove_fave(tip)

        elif q['cmd']=='clickUpVote':
            tip = Tip.query.get(q['id'])
            if q['selected']=="none":
                current_user.upvote(tip)
            elif q['selected']=="upVote":
                current_user.remove_upvote(tip)
            elif q['selected']=="downVote":
                current_user.remove_downvote(tip)
                current_user.upvote(tip)
            res['upvoted']=tip.chd_upvoted
            res['downvoted']=tip.chd_downvoted

        elif q['cmd']=='clickDownVote':
            tip = Tip.query.get(q['id'])
            if q['selected']=="none":
                current_user.downvote(tip)
            elif q['selected']=="downVote":
                current_user.remove_downvote(tip)
            elif q['selected']=="upVote":
                current_user.remove_upvote(tip)
                current_user.downvote(tip)
            res['upvoted']=tip.chd_upvoted
            res['downvoted']=tip.chd_downvoted

        elif q['cmd']=='addComment':
            tip = Tip.query.get(q['id'])
            comments = json.loads(tip.comments) if tip.comments else []
            ts = (datetime.utcnow().strftime('%y %m %d %H %M %S'))
            comments.append({"text":q['text'], "author_id":current_user.id, "timestamp":ts})

            res_comments = [c for c in comments]
            for c in res_comments:
                c["is_mine"]=True if c["author_id"] == current_user.id else False

            tip.comments = json.dumps(comments)
            res['comments'] = res_comments

            tip.chd_comments_count = len(comments)

            db.session.add(tip)
            db.session.commit()

            msg = 'К вашему совету добавлен новый комментарий от пользователя '+current_user.nickname
            Notification.add(
                tip.user_id,
                'NC',
                msg,
                data=q['text'][:100]+"...",
                user_from=current_user.id,
                extra={"tip_url": url_for('geo.single_tip', tid=tip.id)}
            )

        elif q['cmd']=='saveComment':
            tip = Tip.query.get(q['id'])

            comments = json.loads(tip.comments) if tip.comments else []
            ts = (datetime.utcnow().strftime('%y %m %d %H %M %S'))

            if comments[q['cid']]['author_id']==current_user.id:
                comments[q['cid']]={"text":q['text'], "author_id":current_user.id, "timestamp":ts}

                res_comments = [c for c in comments]
                for c in res_comments:
                    c["is_mine"]=True if c["author_id"] == current_user.id else False

                res['comments'] = res_comments
                tip.comments = json.dumps(comments)


                tip.chd_comments_count = len(comments)

                db.session.add(tip)
                db.session.commit()
            else:
                res['status']='Error'
                Log.register('ERROR', 'unauthorized comment editing attempt')

        elif q['cmd']=='deleteComment':
            tip = Tip.query.get(q['id'])
            comments = json.loads(tip.comments)
            if comments[q['cid']]["author_id"]==current_user.id:
                del comments[q['cid']]
                tip.comments = json.dumps(comments)
                res['comments'] = comments
                tip.chd_comments_count = len(comments)
                db.session.add(tip)
                db.session.commit()
            else:
                res['status']='Error'
                Log.register('ERROR', 'unauthorized comment deleting attempt')

        elif q['cmd']=='addNew' or q['cmd']=='edit':

            if q['cmd']=='addNew':
                tip = Tip()
                tip.user_id = current_user.id
                tip.place_id = q['placeID']
            else:
                tip = Tip.query.get(q['tipID'])
                if not tip or tip.user_id!=current_user.id:
                    res['status']='Wrong id'
                    return json.dumps(res)

            tip.text = q['text'].strip()
            tag_names = q['tags']

            if tip.text!='' and len(tag_names)>0 and len(tip.text)<=600:

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

                tip.created_at = datetime.utcnow()
                db.session.add(tip)
                db.session.commit()
                tip.place.bake()
                tip.cache_it()
                res['tip_data']={'author_name': current_user.nickname, 'author_id':current_user.id, 'tip_id': tip.id}

            if q['cmd'] == 'addNew':
                msg = 'Новый совет от '+current_user.nickname
                subscribed_users = UsersRelationship.query.filter_by(user2=current_user.id, follows=True)
                for su in subscribed_users:
                    Notification.add(
                                    su.user1,
                                    'NP',
                                    msg,
                                    data=tip.text[:100]+"...",
                                    user_from=current_user.id,
                                    extra={"tip_url": url_for('geo.single_tip', tid=tip.id)}
                                    )

                subscribed_users = UserToPlaceRelationship.query.filter_by(place_id=tip.place_id)

                msg = tip.place.rus_name+': добавлен новый совет'
                for su in subscribed_users:
                    if su.user_id != current_user.id:
                        Notification.add(
                                        su.user_id,
                                        'NP',
                                        msg,
                                        data=tip.text[:100]+"...",
                                        user_from=current_user.id,
                                        extra={"tip_url": url_for('geo.single_tip', tid=tip.id)}
                                        )

        elif q['cmd'] == "delete":
            tip = Tip.query.get(q['id'])
            if tip and tip.user_id == current_user.id:
                db.session.delete(tip)
                db.session.commit()
            else:
                res['status']='Error deleting the tip'

    else:
        res['status']='error: not logged in'


    return json.dumps(res)


@geo.route('/country/<us>')
def country(us):
    c = Country.query.filter_by(url_string=us).first()
    if c:
        places = list(db.engine.execute(""" SELECT rus_name, url_string FROM G_places WHERE country_id=%d and chd_has_tips=1 ORDER BY `number` DESC""" % c.id))
        return render_template('country.html', c=c, places=places)
    else:
        abort(404)

@geo.route('/direction/<us>')
def direction(us):
    d = Direction.query.filter_by(url_string=us).first()
    if d:
        countries = list(db.engine.execute(""" SELECT c.rus_name, COUNT(p.id), c.url_string as cp FROM G_countries as c JOIN G_places as p ON p.country_id=c.id WHERE p.chd_has_tips=1 AND c.direction_id=%d GROUP BY c.rus_name ORDER BY cp DESC, rus_name""" % d.id))
        return render_template('direction.html', d=d, countries=countries)
    else:
        abort(404)

@geo.route('/world')
def world():
    return render_template('world.html')







