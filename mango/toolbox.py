import hashlib
from datetime import datetime
from flask import render_template, current_app, request,session

def get_hash(s):
    hsh = hashlib.md5()
    hsh.update(s.encode("utf-8"))
    return hsh.hexdigest()


def create_marker(req):

    #print (req.remote_addr)
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    base = ip+"|"+req.headers.get("User-Agent")+"|"+datetime.now().strftime('%y%m%d%H%M%S')
    #hsh = hashlib.md5()
    #hsh.update(base.encode("utf-8"))
    #return hsh.hexdigest()
    return base


def copysome(objfrom, objto, names):
    for n in names:
        if hasattr(objfrom, n):
            v = getattr(objfrom, n)
            setattr(objto, n, v);

# def mark_newcomer(entry, label=''):
#     session['entry']=entry
#     session['label'] = label
    
#     if 'marker' not in session.keys():
#         marker = create_marker(request)
#         session['marker']=marker
#         LandingLog.write('new')
#     else:
#         LandingLog.write('int')

def russian_plurals(word, num, **kwargs):

    rus_dict={
        "секунда":["секунда","секунды", "секунд"],
        "минута":["минута","минуты", "минут"],
        "час":["час","часа", "часов"],
        "день":["день","дня", "дней"],
        "неделя":["неделя","недели", "недель"],
        "месяц":["месяц","месяца", "месяцев"],
        "год":["год","года", "лет"]
    }

    if 'ago' in kwargs and kwargs['ago'] is True:
        rus_dict['секунда'][0]='секунду'
        rus_dict['минута'][0]='минуту'
        rus_dict['неделя'][0]='неделю'

    if num >= 100:
        num %= 100
    if num >= 20:
        num %= 10
    if num == 1:
        return rus_dict[word][0]
    elif num in range(2,5):
        return rus_dict[word][1]
    elif num in range(5,20) or num==0:
        return rus_dict[word][2]

def how_long_ago(old_date):

    td = datetime.utcnow() - old_date
    s = "%d %s назад"

    if td.days >= 365:
        t = round(td.days/365)
        return s % (t, russian_plurals('год',t))

    elif td.days <365 and td.days >30:
        t =round(td.days/30)
        return s % (t, russian_plurals('месяц',t))

    elif td.days <=30 and td.days >6:
        t =round(td.days/7)
        return s % (t, russian_plurals('неделя',t, ago=True))

    elif td.days <7 and td.days >0:
        t =round(td.days/7)
        return s % (t, russian_plurals('день',t))

    elif td.days==0 and td.seconds>=3600:
        t =round(td.seconds/3600)
        return s % (t, russian_plurals('час',t))

    elif td.days==0 and td.seconds<3600 and td.seconds>59:
        t =round(td.seconds/60)
        return s % (t, russian_plurals('минута',t, ago=True))

    elif td.days==0 and td.seconds<60 and td.seconds:
        return 'Только что'


