#manage.py

from flask.ext.script import Manager
from mango import app
from mango.mailer import Mailer
from mango.toolbox import russian_plurals
from mango.geo.models import Tip, Tag

manager = Manager(app)

@manager.command
def mail_test():
    Mailer.welcome_mail()

@manager.command
def test_russian_plurals():
    for n in range(0,125):
        print ("%d %s назад" %(n, russian_plurals('секунда', n, ago=True)))

@manager.command
def check_prices():
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




if __name__ == "__main__":
    manager.run()
