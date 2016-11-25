
# import warnings
# from flask.exthook import ExtDeprecationWarning

# warnings.simplefilter('ignore', ExtDeprecationWarning)


from flask import Flask, request, session, render_template, url_for, make_response, redirect
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from flask_wtf.csrf import CsrfProtect
import json
from datetime import datetime, timedelta

from .cache import cache
from .db import db
from .config import DEBUG, SECRET_KEY, DBURI, MAINTENANCE, PROJECT_NAME, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL, MAIL_USERNAME, MAIL_PASSWORD, ALLOW_ROBOTS
from .social import social, oauth
from .social.models import User, Notification
from .admin import admin
from .geo import geo
from .geo.models import Place
from .logger import Log




app = Flask(__name__)

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
        response = make_response("User-agent: *\nDisallow:")
    response.headers["content-type"] = "text/plain"
    return response

@app.route('/sitemap.xml', methods=['GET'])
@cache.cached(timeout=3600)
def sitemap():

    """Generate sitemap.xml. Makes a list of urls and date modified."""

    pages=[]
    ten_days_ago=(datetime.now() - timedelta(days=10)).date().isoformat()

    pages.append([url_for('root', _external = True), ten_days_ago])

    # PLACES

    places = list(db.engine.execute("""SELECT url_string, modified_at FROM G_places WHERE chd_has_tips=1"""))

    for p in places:
        date = ten_days_ago if not p[1] else p[1].date().isoformat()
        pages.append([url_for('geo.places', us=p[0], _external=True), date])

    #SINGLE TIPS

    tips = list(db.engine.execute("""SELECT id, updated_at FROM tips WHERE chd_comments_count >0 """))
    for t in tips:
        pages.append([url_for('geo.single_tip', tid=t[0], _external=True), t[1].date().isoformat()])

    # USER PROFILES

    users = list(db.engine.execute("""SELECT id, changed_at FROM users """))
    for u in users:
        date = ten_days_ago if not u[1] else u[1].date().isoformat()
        pages.append([url_for('social.public_profile', uid=u[0], _external=True), date])


    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    response= make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


#@cache.cached(3600)
@app.route('/')
def root():
    Log.register(action='route:root')
    return render_template('main.html')

@app.route('/active')
def active():
    places = list(db.engine.execute("""SELECT rus_name, url_string FROM G_places WHERE chd_has_tips=1 LIMIT 500"""))
    links = '<br/>'.join(['<a href="/place/%s">%s</a>' % (p[1], p[0]) for p in places])
    return links

@app.route('/inactive')
def inactive():
    places = list(db.engine.execute("""SELECT rus_name, url_string FROM G_places WHERE chd_has_tips=0 LIMIT 500"""))
    links = '<br/>'.join(['<a href="/place/%s">%s</a>' % (p[1], p[0]) for p in places])
    return links

@app.route('/users')
def users():
    users = User.query.all()
    if current_user.is_authenticated:
        notifications = Notification.count(current_user)
        return render_template(
                                'test_users.html',
                                users=users,
                                notifications_count=notifications['other'],
                                messages_count=notifications['messages']
                                )
    else:
        return render_template(
                                'test_users.html',
                                users=users
                                )


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





