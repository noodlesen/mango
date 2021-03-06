
import warnings
from flask.exthook import ExtDeprecationWarning

warnings.simplefilter('ignore', ExtDeprecationWarning)


from flask import Flask, request, session, render_template, url_for, make_response, redirect
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from flask_wtf.csrf import CsrfProtect

from flask_sslify import SSLify


import json
from datetime import datetime, timedelta

from .cache import cache
from .db import db
from .config import DEBUG, SECRET_KEY, DBURI, MAINTENANCE, PROJECT_NAME, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL, MAIL_USERNAME, MAIL_PASSWORD, ALLOW_ROBOTS
from .social import social, oauth
from .social.models import User, Notification
from .admin import admin
from .geo import geo
from .geo.models import Place, Tip
from .geo.views import get_tips_data
from .logger import Log

from .assets import assets

from .dttools import NEVER




app = Flask(__name__)

sslify = SSLify(app, permanent=True)

app.url_map.strict_slashes = False

app.register_blueprint(social)
app.register_blueprint(admin)
app.register_blueprint(geo)


app.debug = DEBUG

app.config['PROJECT_NAME']=PROJECT_NAME
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DBURI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 60
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
app.config['BOOTSTRAP_SERVE_LOCAL']=True
app.config['CACHE_TYPE']='simple'
app.config['EMAIL_HOST']= MAIL_SERVER
app.config['EMAIL_PORT']= MAIL_PORT
app.config['EMAIL_HOST_USER']= MAIL_USERNAME
app.config['EMAIL_HOST_PASSWORD']= MAIL_PASSWORD
app.config['EMAIL_USE_SSL']= MAIL_USE_SSL
app.config['EMAIL_USE_TLS']= MAIL_USE_TLS

app.config['WTF_CSRF_TIME_LIMIT'] = None

cache.init_app(app)

toolbar = DebugToolbarExtension(app)

csrf = CsrfProtect(app)

db.init_app(app)

bootstrap = Bootstrap(app)


lm = LoginManager(app)
lm.login_view = 'social.login'

#assets = Environment(app)

assets.init_app(app)

@app.context_processor
def set_global_mode():
    return {'debug_mode': DEBUG}


@lm.user_loader
def load_user(id):
    if id:
        return User.query.get(id)
    else:
        return None


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.before_request
def clear_trailing():
    rp = request.path
    if rp != '/' and rp.endswith('/'):
        return redirect(rp[:-1]), 301


@app.before_request
def check_for_maintenance():
    if MAINTENANCE and request.path != url_for('maintenance') and not 'static' in request.path:
        return redirect(url_for('maintenance'))

@app.route('/maintenance')
def maintenance():
    if MAINTENANCE:
        return render_template('maintenance.html')
    else:
        return redirect(url_for('root'))

@app.route('/robots.txt')
def robots():
    if not ALLOW_ROBOTS:
        response = make_response("User-agent: *\nDisallow: /")
    else:

        DA=['/profile',
            '/private-messages',
            '/my-tips',
            '/favorites',
            '/user',
            url_for('social.v_login'),
            url_for('social.g_login'),
            url_for('social.f_login')]
        daj = '\n'.join(['Disallow: '+d for d in DA])
        root = url_for('root', _external=True)[:-1]
        host = root if root.startswith('https') else root[7:]
        rt = 'User-agent: *\n'+daj+'\nHost: '+host+'\nSitemap: '+url_for('sitemap', _external=True)
        response = make_response(rt)
    response.headers["content-type"] = "text/plain"
    return response

@app.route('/sitemap.xml', methods=['GET'])
#@cache.cached(timeout=3600)
def sitemap():

    """Generate sitemap.xml. Makes a list of urls and date modified."""

    pages=[]

    never = NEVER.date().isoformat()
    pages.append([url_for('root', _external = True), never])

    places = list(db.engine.execute("""SELECT url_string, modified_at FROM G_places WHERE chd_has_tips=1"""))

    for p in places:
        date = never if not p[1] else p[1].date().isoformat()
        pages.append([url_for('geo.places', us=p[0], _external=True), date])


    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    response= make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response

@app.route('/static/photos/page_images/<pf>', methods=['GET'])
def place_picture(pf):
    return redirect(url_for('geo.static', filename='images/places/'+pf)), 301



@app.route('/')
#@cache.cached(timeout=3600)
def root():
    Log.register(action='route:root')
    #p = Place.query.get(2)
    jd = get_tips_data(Tip.query.order_by(Tip.chd_rating.desc()).limit(10))
    jd['config'] = {'mode': 'public_profile'}
    cuia = True if current_user and current_user.is_authenticated else False
    countries = list(db.engine.execute("""SELECT c.rus_name, c.url_string, count(p.id) as cn
                                          FROM G_countries as c
                                          JOIN  G_places as p
                                          ON p.country_id=c.id
                                          GROUP BY c.rus_name
                                          ORDER BY cn DESC
                                          LIMIT 10"""))

    places = list(db.engine.execute("""SELECT p.rus_name, p.url_string, count(t.id)*p.number as cn
                                          FROM G_places as p
                                          JOIN  tips as t
                                          ON t.place_id=p.id
                                          GROUP BY p.rus_name
                                          ORDER BY cn DESC
                                          LIMIT 10"""))

    users_raw = list(db.engine.execute("""SELECT u.nickname, u.id, u.image, count(t.id) as c FROM users as u JOIN tips as t ON t.user_id=u.id GROUP BY u.id ORDER BY c DESC LIMIT 10"""))
    users=[]
    for u in users_raw:
        if not u[2]:
            iname='avatar_placeholder.png'
        else:
            iname = u[2]
        ipth = url_for('social.static', filename='images/avatars/'+iname)
        users.append({'nickname':u[0],'id':u[1],'image':ipth,'count':u[3]})
    return render_template('main.html', json_data=json.dumps(jd), signed=cuia, countries=countries, places=places, users=users)


@app.template_filter('nl2br')
def nl2br(value):
    text = ""
    if value:
        for line in value.split('\n'):
            text += Markup.escape(line) + Markup('<br />')
    return text

@app.errorhandler(404)
def page_not_found(e):
    Log.register(action='route:404', data=request.url)
    return render_template('404.html'), 404

@app.errorhandler(413)
def error413(e):
    return "Your error page for 413 status code", 413


# @csrf.error_handler
# def csrf_error(reason):
#     return render_template('error.html', reason=reason)





