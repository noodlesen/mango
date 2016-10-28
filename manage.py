#manage.py

import json
from urllib.parse import unquote

from flask import url_for
from flask.ext.script import Manager
from fuzzywuzzy import fuzz
from unidecode import unidecode

from mango import app
from mango.db import db
from mango.mailer import Mailer
from mango.toolbox import russian_plurals, get_distance
from mango.geo.models import Tip, Place
from operator import itemgetter

from sqlalchemy import desc

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
    #words = ['евро', 'доллар', 'доллара', "долларов", "доллару", "рупий", "рупия", "EUR", "eur", "usd", "USD", "$", "юань", "юаней", "юаня"]
    #words = ['поесть', 'поели', 'еда', "кухня", "кухни", "блюдо", "ресторан", "ресторанчик", "ресторане", "ресторанчике", "перекусить", "пожрать", "сожрать", "вкусно", "вкуснятина"]
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
    places_res = list(db.engine.execute('SELECT t.place_id, p.lat, p.lng FROM tips AS t INNER JOIN G_places AS p ON p.id=t.place_id GROUP BY t.place_id'))
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
                if dist<=60:
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


# @manager.command
# def load_tp_cities():
#     fn = 'cities.json'
#     with open(fn, 'r') as f:
#         data = json.loads(f.read())
        
#         places = Place.query.filter(Place.city_code==None).all()
#         i = 1
#         for c in data:
#             print('#%d' % i)
#             if c['coordinates']:
#                 clat = round(c['coordinates']['lat'],0)
#                 clng = round(c['coordinates']['lon'],0)
#                 for p in places:
#                     if p.lat:
#                         plat = round(p.lat,0)
#                         plng = round(p.lng,0)
#                         if 'ru' in c['name_translations']:
#                             fz = fuzz.partial_ratio(c['name_translations']['ru'],p.rus_name)
#                             if plat ==clat and plng == clng and fz > 70:
#                                 print ('MATCH!!!  %s and %s    --- %d' % (c['name_translations']['ru'], p.rus_name, fz))
#                                 if 'ru' in  c['name_translations'].keys():
#                                     rus_name = c['name_translations']['ru'] 
#                                 else:
#                                     rus_name = ''
#                                 db.engine.execute('INSERT INTO tp_cities_match (`code`, `tp_name`, `rus_name`, `place_id`, `match`) VALUES ("%s", "%s", "%s", %d, %d)' % (c["code"], c["name"], rus_name,p.id, fz))

#             i+=1

# @manager.command
# def add_place_names():
#     db.engine.execute('UPDATE tp_cities_match INNER JOIN G_places AS p ON place_id = p.id SET place_name = p.eng_name')



# @manager.command
# def mail_test():
#     Mailer.welcome_mail()


# @manager.command
# def test_russian_plurals():
#     for n in range(0, 125):
#         print ("%d %s назад" % (n, russian_plurals('секунда', n, ago=True)))

# @manager.command
# def get_length():
#     tips = Tip.query.all()
#     tmax = 0
#     tmin = 10000
#     tsum = 0
#     tcount = 0
#     p300 = 0
#     p400 = 0
#     p500 = 0
#     for t in tips:
#         print (tcount)
#         tcount += 1
#         l = len(t.text)
#         tsum += l
#         if l < tmin:
#             tmin = l
#         if l > tmax:
#             tmax = l
#         if l > 300:
#             p300 += 1
#         if l > 400:
#             p400 += 1
#         if l > 500:
#             p500 += 1
#     tavg = round(tsum / tcount)
#     print ("MIN :%d MAX :%d AVG :%d" % (tmin, tmax, tavg))
#     print('TOTAL %d' % tcount)
#     print (">300 :%d >400 :%d >500 :%d" % (p300, p400, p500))

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
        # sql = 'UPDATE G_places SET new_url="%s" WHERE id=%d' % (r["url"], r["id"])
        # print(sql)
        # db.session.execute(sql)
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



if __name__ == "__main__":
    manager.run()
