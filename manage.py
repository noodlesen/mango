#manage.py

import json
from urllib.parse import unquote

from flask import url_for
from flask_script import Manager
from fuzzywuzzy import fuzz
from unidecode import unidecode
from werkzeug.datastructures import FileStorage

from mango import app
from mango.db import db
from mango.dttools import get_random_datetime
from mango.mailer import Mailer
from mango.toolbox import russian_plurals, get_distance
from mango.geo.models import Tip, Place
from mango.social.models import User
from mango.social.views import avatar_picture_upload
from operator import itemgetter

from sqlalchemy import desc

import os
from random import randint

from alphabet_detector import AlphabetDetector

ad = AlphabetDetector()

manager = Manager(app)


@manager.command
def check_tags():
    """ tries to predict if there should be some tag based on relevant keywords

    saves filtered tips to file

    """
    f = open('dive_report.txt', 'w')
    tips = Tip.query.all()
    words = ['дайв', 'Дайв', 'PADI']
    n = 1
    for tip in tips:
        found = False
        for w in words:
            if tip.text.find(w) >= 0:
                found = True
        if found:
            has_tag = False
            tags = ''
            for tag in tip.tags:
                tags += ' / ' + tag.name
                if tag.name == 'дайвинг':
                    has_tag = True
            if not has_tag:
                f.write('\n')
                f.write('\n')
                f.write('#'+str(n)+'\n')
                f.write(tip.place.rus_name)
                f.write('\n')
                f.write(tags)
                f.write('\n')
                f.write(tip.text)
                n += 1
    f.close()





@manager.command
def calculate_places_nearby():
    """ calculates distances between places with tips assigned

    Makes records into "_chd_places_nearby" table and into "chd_places_nearby" field of the Place models

    """
    places_res = db.engine.execute('SELECT t.place_id, p.lat, p.lng FROM tips AS t INNER JOIN G_places AS p ON p.id=t.place_id GROUP BY t.place_id')
    db.engine.execute('TRUNCATE _chd_places_nearby')
    places = []
    for p in places_res:
        places.append([p[0], p[1], p[2]])

    results = []
    for i in range(0, len(places)-1):
        p1lat = places[i][1]
        p1lng = places[i][2]
        for j in range(0, len(places)-1):
            if i != j:
                p2lat = places[j][1]
                p2lng = places[j][2]
                if (p1lat and p2lat):
                    dist = get_distance(p1lat, p1lng, p2lat, p2lng)
                    if dist < 400:
                        results.append([places[i][0], places[j][0], dist])
                        db.engine.execute('INSERT INTO _chd_places_nearby (place1, place2, distance) VALUES (%d, %d, %d)' % (places[i][0], places[j][0], dist))

    print (results)

    places_nearby = {}
    for r in results:
        place_query = list(db.engine.execute('SELECT p.rus_name, p.url_string , c.code FROM G_places AS p INNER JOIN G_countries AS c ON p.country_id = c.id WHERE p.id=%d' % r[1]))[0]
        place_name = place_query[0]
        place_url = url_for('geo.places', us=place_query[1])
        place_obj = {"place": place_name, "id": r[1], "distance": r[2], "url": place_url, "flag_url": url_for('geo.static', filename="images/flags/small/"+place_query[2].lower()+".gif")}
        if r[0] in places_nearby.keys():
            places_nearby[r[0]].append(place_obj)
        else:
            places_nearby[r[0]] = [place_obj]

    for k, v in places_nearby.items():
        print ('%d - %r' % (k, v))
        print()
        place = Place.query.get(k)
        try:
            v = sorted(v, key=itemgetter("distance"))
        except KeyError:
            pass
        place.chd_places_nearby = json.dumps(v)
        db.session.add(place)
        db.session.commit()






@manager.command
def calculate_airports_nearby():
    """ calculates nearest airports

        and saves data into chd_airports field of G_places table

    """
    #places_res = list(db.engine.execute('SELECT t.place_id, p.lat, p.lng FROM tips AS t INNER JOIN G_places AS p ON p.id=t.place_id GROUP BY t.place_id'))
    places_res = list(db.engine.execute('SELECT p.id, p.lat, p.lng FROM G_places as p'))
    airports = list(db.engine.execute('SELECT name, IATA, lat, lng, id, city_code, rating, size FROM airports'))
    results={}
    for p in places_res:
        print ('ID:%d' % p[0])
        plat = p[1]
        plng = p[2]
        for ap in airports:
            aplat = ap[2]
            aplng = ap[3]
            if plat and aplat:
                dist = get_distance(plat, plng, aplat, aplng)
                if dist<=70:
                    print(ap[1])
                    airport = {"ap_id":ap[4], "code":ap[1], "name":ap[0], "distance":dist, "rating":ap[6], "size":ap[7]}
                    if p[0] in results.keys():
                        results[p[0]].append(airport)
                    else:
                        results[p[0]]=[airport]
        try:
            results[p[0]] = sorted(results[p[0]], key=itemgetter("rating"))
        except KeyError:
            pass

    for k, v in results.items():
        print()
        print ("%d -> %r" %(k, v))
        place = Place.query.get(k)
        place.chd_airports = json.dumps(v)
        db.session.add(place)
        db.session.commit()


# EXPERIMENTAL ============================================================


@manager.command
def cache_all_tips():
    tips = Tip.query.all()
    for t in tips:
        print(t.id)
        t.cache_it()

@manager.command
def check_rusnames():
    with open('rusnames.txt', 'w') as f:
        places = Place.query.filter(Place.number>20).order_by(desc(Place.number)).all()
        i=1
        for p in places:
            if not ad.is_cyrillic(p.rus_name):
                f.write('%d | %s   (%s, %s ) | \n' % (p.id, p.rus_name, p.rus_address, p.country.rus_name))
                print(i)
                i+=1


@manager.command
def udtest():
    places = db.session.execute('SELECT id, url_string FROM G_places WHERE url_string LIKE ("%%\%%%%")')
    results = []
    for p in places:
        pp=  unidecode(unquote(p[1])).lower()
        pp = pp.replace("'",'')
        pp = pp.replace("%",'')
        pp = pp.replace("-",'_')
        pp = pp.replace(" ",'_')
        pp = pp.replace("/",'_')
        pp = pp.replace("(",'_')
        pp = pp.replace(")",'_')
        print(p[1],"  ==>  ",pp)
        results.append({"id":p[0], "url": pp})

    for r in results:
        place = Place.query.get(r["id"])
        place.url_string = r["url"]
        db.session.add(place)
        db.session.commit()


@manager.command
def lowerurl():
    places = Place.query.all()
    for p in places:
        p.url_string = p.url_string.lower()
        db.session.add(p)
        db.session.commit()


@manager.command
def load_avatars():

    ld = os.listdir('../utils/Avatar')

    _workers = db.session.execute('SELECT id, ws, nickname FROM users WHERE worker=1')
    workers =[]
    for w in _workers:
        workers.append({"id": w[0], "sex": w[1], "nickname":w[2], "pic": None})

    files = []
    for f in ld:
        if f.endswith("jpg"):
            files.append({"filename": f, "sex": f[:1].upper()})


    for f in files:
        sex = ''
        while sex != f["sex"]:
            picked = workers[randint(0, len(workers)-1)]
            if not picked["pic"]:
                sex = picked["sex"]
        picked["pic"] = f["filename"]


    for w in workers:
        print (w["nickname"], w["pic"])
        if w["pic"]:
            u = User.query.get(w["id"])
            fs = None
            path = "../utils/Avatar/"+w["pic"]
            print(path)
            with open(path, 'rb') as fl:
                fs = FileStorage(fl)
                avatar_picture_upload(fs, u, False)

    

@manager.command
def make_timestamps():
    order = []
    tips = db.engine.execute('SELECT id FROM tips WHERE created_at IS NULL')
    for t in tips:
        print (t[0])
        ts = get_random_datetime(2016,2016,9,10).strftime('%Y-%m-%d %H:%M:%S')
        order.append({"id":t[0], "ts":ts})
    for r in order:
        db.engine.execute('UPDATE tips SET created_at="%s" WHERE id=%d' % (r["ts"], r["id"]))

@manager.command
def assign_countries_to_workers():
    countries = db.engine.execute('SELECT c.id, c.rus_name FROM G_countries as c JOIN G_places as p ON p.country_id=c.id WHERE p.chd_has_tips=1 ') # GROUP BY c.id 
    field=[]
    field.extend([c[0] for c in countries])
    _workers = db.engine.execute('SELECT id, nickname FROM users WHERE worker=1')
    workers=[]
    for w in _workers:
        cs = []
        for n in range(1,4):
            while True:
                cn = field[randint(0, len(field)-1)]
                if cn not in cs:
                    cs.append(cn)
                    break
        print (w[1])
        print(cs)
        for c in cs:
            db.engine.execute('INSERT INTO workers2countries (`worker_id`, `country_id`) VALUES (%d, %d)' % (w[0], c))


@manager.command
def assign_tips_to_workers():
    tips = db.engine.execute('SELECT t.id, t.sex, c.id FROM tips as t JOIN G_places as p ON t.place_id=p.id JOIN G_countries as c ON c.id = p.country_id')
    i=0
    for t in tips:
        i+=1
        print(i)
        tip_sex = t[1]
        if tip_sex !='N':
            _candidates = db.engine.execute("""SELECT w.worker_id, u.ws FROM workers2countries as w JOIN users as u ON u.id = w.worker_id WHERE w.country_id=%d AND u.ws='%s' """ % (t[2], tip_sex))
        else:
            _candidates = db.engine.execute("""SELECT w.worker_id, u.ws FROM workers2countries as w JOIN users as u ON u.id = w.worker_id WHERE w.country_id=%d """ % (t[2]))
        candidates = [c for c in _candidates]
        print (candidates)
        if candidates:
            while True:
                cnd = candidates[randint(0, len(candidates)-1)]
                if cnd[1] == tip_sex or tip_sex == 'N':
                    break
            db.engine.execute('UPDATE tips SET user_id = %d WHERE id=%d' % (cnd[0], t[0]))
        else: 
            db.engine.execute('UPDATE tips SET user_id = %d WHERE id=%d' % (131, t[0]))


@manager.command
def rename_twins():
    LANG='rus'
    sql = 'SELECT %s_name, COUNT(%s_name) FROM G_places GROUP BY %s_name' % (LANG, LANG, LANG)
    res = db.engine.execute(sql)
    i=0
    twins=[]
    for r in res:
        if r[1]>1:
            i+=1
            print(i, r[0], r[1])
            twins.append(r[0])

    for t in twins:
        print()
        sql = """SELECT p.id, p.number, p.%s_address FROM G_places as p WHERE %s_name="%s" """ % (LANG, LANG, t)
        results = db.engine.execute(sql)

        res = [r for r in results]
        nmax=0
        for r in res:
            if r[1] and r[1]>nmax:
                nmax = r[1]

        for x in res:
            newname = t if x[1]==nmax else x[2]
            print (t, x[1], '>>>', newname)
            sql = """UPDATE G_places SET %s_name="%s" WHERE id=%d """ % (LANG, newname, x[0])
            print(sql)
            db.engine.execute(sql)
            

@manager.command
def seed_likes():
    COUNT = 10000
    workers = [w for w in db.engine.execute("""SELECT id, nickname FROM users WHERE worker=1""")]
    tips = [t for t in db.engine.execute("""SELECT id, user_id FROM tips""") ]
    for i in range(1, COUNT):
        print(">%d" % i)
        rw = randint(0, len(workers)-1)
        rt = randint(0, len(tips)-1)
        print (workers[rw][1],">>>>>",tips[rt][0])
        uid = workers[rw][0]
        tid = tips[rt][0]
        tuid = tips[rt][1]
        if uid != tuid:
            drc = 'up' if randint(0,100)<=75 else 'down'
            exists = [x for x in db.session.execute(""" SELECT id FROM users_%svotes WHERE user_id=%d AND tip_id=%d """ % (drc, uid, tid))]
            if not len(exists):
                user = User.query.get(uid)
                tip = Tip.query.get(tid)
                if drc=='up':
                    user.upvote(tip)
                else:
                    user.downvote(tip)

@manager.command
def count_comments():
    tips = list(db.engine.execute("""SELECT id, comments FROM tips"""))
    for t in tips:
        if t[1]:
            c = json.loads(t[1])
            cc = len(c)
        else:
            cc=0
        db.engine.execute("""UPDATE tips SET chd_comments_count=%d WHERE id=%d""" %(cc, t[0]))


@manager.command
def filter_my_comments():
    tips = list(db.engine.execute("""SELECT id, comments FROM tips"""))
    for t in tips:
        if t[1]:
            comments = json.loads(t[1])
            for c in comments:
                if c['author_id']==131:
                    print ('#%d' % t[0])
                    print(c['text'])
                    print()
            # new_comments = [c for c in comments if len(c['text'])>20 or c['author_id']!=131]
            # print (new_comments)
            # db.engine.execute("""UPDATE tips SET comments='%s' WHERE id=%d""" % (json.dumps(new_comments), t[0]))

@manager.command
def save_out_tweets():
    tweets=''
    tns = []
    with open('out_tweets.txt', 'r') as f:
        lines=f.read().split('\n')
        lc=0
        for l in lines:
            lc+=1
            tid = int(l.split('/')[-1])
            #print ("tid %d" % tid)

            #tip_res = list(db.engine.execute("""SELECT text, taglines, sex FROM tips WHERE id=%d""" % tid))

            t = Tip.query.get(tid)
            if t:
                print (tid, "OK")

    
                #tweets+="@"+'\n'.join([tip[2], tip[1], tip[0],'\n'])
                tweets+="\n".join(["^"+str(t.place.id)+"-"+t.place.rus_name+" ("+t.place.country.rus_name+")", "@"+t.sex, t.taglines, t.text, '\n'])
                # print(lc, tid, tip[2])
                if tid not in tns:
                    tns.append(tid)


    with open('excluded.txt','w') as w:
        w.write(tweets)

    print(tns)
    print("TOTAL", len(tns))



    db.engine.execute("""DELETE FROM tips WHERE id IN (%s)""" % ", ".join([str(x) for x in tns]))





if __name__ == "__main__":
    manager.run()
