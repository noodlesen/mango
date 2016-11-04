# SCore 0.01

from flask import Flask, request, session, render_template
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user

from flask_wtf.csrf import CsrfProtect
import json

from .cache import cache

from .db import db

from .config import DEBUG, SECRET_KEY, DBURI, MAINTENANCE, PROJECT_NAME, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL, MAIL_USERNAME, MAIL_PASSWORD
from .social import social, oauth
from .social.models import User, Notification
from .admin import admin
from .geo import geo
from .geo.models import Place

# from .mailer import mail
from .logger import Log



app = Flask(__name__)

app.register_blueprint(social)
app.register_blueprint(admin)
app.register_blueprint(geo)


app.debug = DEBUG

app.config['PROJECT_NAME']=PROJECT_NAME
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DBURI
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 60
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
app.config['BOOTSTRAP_SERVE_LOCAL']=True
app.config['CACHE_TYPE']='simple'
# app.config['MAIL_SERVER']=MAIL_SERVER
# app.config['MAIL_PASSWORD']=MAIL_PASSWORD
# app.config['MAIL_PORT']=MAIL_PORT
# app.config['MAIL_USE_SSL']=MAIL_USE_SSL
# app.config['MAIL_USE_TLS']=MAIL_USE_TLS
# app.config['MAIL_USERNAME']=MAIL_USERNAME
app.config['EMAIL_HOST']= MAIL_SERVER
app.config['EMAIL_PORT']= MAIL_PORT
app.config['EMAIL_HOST_USER']= MAIL_USERNAME
app.config['EMAIL_HOST_PASSWORD']= MAIL_PASSWORD
app.config['EMAIL_USE_SSL']= MAIL_USE_SSL
app.config['EMAIL_USE_TLS']= MAIL_USE_TLS

app.config['WTF_CSRF_TIME_LIMIT'] = 36000


#mail = Mail(app)


cache.init_app(app)

# mail.init_app(app)

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

# @csrf.error_handler
# def csrf_error(reason):
#     return render_template('error.html', reason=reason)


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
    return ("User-agent: *\nDisallow: /")


#for example
#@cache.cached(3600)

@app.route('/')
def root():
    Log.register(action='route:root')
    #places = Place.query.filter_by(chd_has_tips=1)
    #return render_template('test_places.html', places=places)
    return render_template('main.html')

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
    return render_template('404.html'), 404

@app.errorhandler(413)
def error413(e):
    return "Your error page for 413 status code", 413

# @app.route('/csrf-test', methods=['POST'])
# def csrf_test():
#     return ('okk')





