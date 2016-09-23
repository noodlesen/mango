#manage.py

from flask.ext.script import Manager
from mango import app
from mango.db import db 
from mango.mailer import Mailer
from mango.toolbox import russian_plurals, get_distance
from mango.geo.models import Tip, Tag, Place

import json

manager = Manager(app)

@manager.command
def mail_test():
    Mailer.welcome_mail()

@manager.command
def test_russian_plurals():
    for n in range(0,125):
        print ("%d %s назад" %(n, russian_plurals('секунда', n, ago=True)))

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
    n=1
    for tip in tips:
        found = False
        for w in words:
            if tip.text.find(w)>=0:
                found = True
        if found:
            has_tag = False
            tags=''
            for tag in tip.tags:
                tags+=' / '+tag.name
                if tag.name=='дайвинг':
                    has_tag=True
            if not has_tag:
                f.write('\n')
                f.write('\n')
                f.write('#'+str(n)+'\n')
                f.write(tip.place.rus_name)
                f.write('\n')
                f.write(tags)
                f.write('\n')
                f.write(tip.text)
                n+=1
    f.close()

@manager.command
def get_length():
    tips = Tip.query.all()
    tmax=0
    tmin=10000
    tsum = 0
    tcount = 0
    p300 = 0
    p400=0
    p500=0
    for t in tips:
        print (tcount)
        tcount+=1
        l = len(t.text)
        tsum+=l
        if l<tmin:
            tmin=l
        if l>tmax:
            tmax=l
        if l>300:
            p300+=1
        if l>400:
            p400+=1
        if l>500:
            p500+=1
    tavg = round(tsum/tcount)
    print ("MIN :%d MAX :%d AVG :%d" % (tmin, tmax, tavg))
    print('TOTAL %d' % tcount)
    print (">300 :%d >400 :%d >500 :%d" % (p300, p400, p500))


@manager.command
def calculate_places_nearby():
    """ calculates distances between places with tips assigned

    Makes records into "_chd_places_nearby" table and into "chd_places_nearby" field of the Place models

    """
    places_res = db.engine.execute('SELECT t.place_id, p.lat, p.lng FROM tips AS t INNER JOIN G_places AS p ON p.id=t.place_id GROUP BY t.place_id')
    db.engine.execute('TRUNCATE _chd_places_nearby')
    places=[]
    for p in places_res:
        places.append([p[0], p[1], p[2]])

    results=[]
    for i in range(0, len(places)-1):
        p1lat = places[i][1]
        p1lng = places[i][2]
        for j in range(0, len(places)-1):
            if i != j:
                p2lat = places[j][1]
                p2lng = places[j][2]
                if (p1lat and p2lat):
                    dist = get_distance (p1lat, p1lng, p2lat, p2lng)
                    if dist<250:
                        results.append([places[i][0], places[j][0], dist ])
                        db.engine.execute('INSERT INTO _chd_places_nearby (place1, place2, distance) VALUES (%d, %d, %d)' % (places[i][0], places[j][0], dist ))

    print (results)

    places_nearby = {}
    for r in results:
        place_query = db.engine.execute('SELECT rus_name FROM G_places WHERE id=%d' % r[1])
        place_name = list(place_query)[0][0]
        place_obj = {"place":place_name, "id":r[1], "distance":r[2]}
        if r[0] in places_nearby.keys():
            places_nearby[r[0]].append(place_obj)
        else:
            places_nearby[r[0]]=[place_obj]

    for k,v in places_nearby.items():
        print ('%d - %r' % (k,v))
        print()
        place = Place.query.get(k)
        place.chd_places_nearby=json.dumps(v)
        db.session.add(place)
        db.session.commit()





if __name__ == "__main__":
    manager.run()
