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
    f = open('food_report.txt', 'w')
    tips = Tip.query.all()
    words = ['евро', 'доллар', 'доллара', "долларов", "доллару", "рупий", "рупия", "EUR", "eur", "usd", "USD", "$", "юань", "юаней", "юаня"]
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
                if tag.name=='цены':
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




if __name__ == "__main__":
    manager.run()
