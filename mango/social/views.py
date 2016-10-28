from flask import session, request, url_for, redirect, render_template, flash, abort
from .models import User, PrivateMessage, UsersRelationship, Notification, NotificationHistory
from flask.ext.login import login_user, login_required, logout_user, current_user
from . .db import db
from . .config import GOOGLE_ID, GOOGLE_SECRET, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, VK_APP_KEY, VK_APP_SECRET
from datetime import datetime
import json

from . import social, oauth

from . .path import ROOT_DIR, UPLOAD_DIR

from PIL import Image
from . .toolbox import get_hash, how_long_ago

from sqlalchemy.sql import or_, and_

from . .mailer import Mailer

from sqlalchemy import desc

import requests

from . .geo.views import get_tips_data, get_all_tags
from . .geo.models import Tip



def welcome_procedure():
    Notification.add(current_user.id, 'personal', 'Добро пожаловать в органы, сынок! (Пример приветственного сообщения) Параллельно должно прийти письмо на почту')
    Mailer.welcome_mail(current_user.contact_email)


# VK OAUTH
#=============================================================

vk = oauth.remote_app(
    'vk',
    consumer_key=VK_APP_KEY,
    consumer_secret=VK_APP_SECRET,
    request_token_params={'scope': 'email, username'},
    base_url='https://api.vk.com/method/',
    request_token_url=None,
    access_token_url='https://oauth.vk.com/access_token',
    authorize_url='https://oauth.vk.com/authorize'
)

@social.route('/vk-login', methods=['GET'])
def v_login():
    if request.args and request.args['follow']:
        session['follow'] = request.args['follow']
    return vk.authorize(callback=url_for('social.v_authorized', _external=True))


@social.route('/vk-login/authorized')
def v_authorized():
    just_registered = False
    resp = vk.authorized_response()
    print('RESPONSE:')
    print(resp)
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    print ('TOKEN')
    ac_token  = resp['access_token']
    session['vk_token'] = (resp['access_token'], '')

    user_info = json.loads(
                    requests.get('https://api.vk.com/method/users.get?user_ids=%s&access_token=%s' % (resp['user_id'], ac_token))
                    .text)
    user_info = user_info['response'][0]

    username = user_info['first_name']+" "+user_info['last_name']
    email = resp['email']
    uid = user_info["uid"]

    # check for user
    user = User.query.filter_by(vk_id=uid).first()
    if user is None:
        user = User.query.filter_by(register_email=email).first()
        if user is None:
            user = User.register_vk_user(username, email, uid)
            just_registered = True
        else:
            user.vk_id = uid
            user.vk_username = username
    user.last_login = datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    login_user(user)
    if just_registered:
        welcome_procedure()
    if "follow" in session:
        next_url = session["follow"]
    else:
        next_url = url_for('root')
    return redirect(next_url)


@vk.tokengetter
def get_vk_oauth_token():
    return session.get('vk_token')

# GOOGLE OAUTH
#=============================================================
google = oauth.remote_app(
    'google',
    consumer_key=GOOGLE_ID,
    consumer_secret=GOOGLE_SECRET,
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


@social.route('/google-login', methods=['GET'])
def g_login():
    if request.args and request.args['follow']:
        session['follow'] = request.args['follow']
    return google.authorize(callback=url_for('social.g_authorized', _external=True))


@social.route('/google-login/authorized')
def g_authorized():
    just_registered = False
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    print(me.data['email'])

    # check for user
    user = User.query.filter_by(google_id=me.data['id']).first()
    if user is None:
        user = User.query.filter_by(register_email=me.data['email']).first()
        if user is None:
            user = User.register_google_user(me.data['name'], me.data['email'], me.data['id'])
            just_registered = True
        else:
            user.google_id = me.data['id']
            user.g_username = me.data['name']
    user.last_login = datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    login_user(user)
    if just_registered:
        welcome_procedure()
    if "follow" in session:
        next_url = session["follow"]
    else:
        next_url = url_for('root')
    return redirect(next_url)


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


# FACEBOOK OAUTH
#=============================================================

facebook = oauth.remote_app('facebook',
                            base_url='https://graph.facebook.com/',
                            request_token_url=None,
                            access_token_url='/oauth/access_token',
                            authorize_url='https://www.facebook.com/dialog/oauth',
                            consumer_key=FACEBOOK_APP_ID,
                            consumer_secret=FACEBOOK_APP_SECRET,
                            request_token_params={'scope': ['email', 'public_profile']}
                            )


@social.route('/facebook-login', methods=['GET'])
def f_login():
    if request.args and request.args['follow']:
        session['follow'] = request.args['follow']
    return facebook.authorize(callback=url_for('social.f_authorized', _external=True))


@social.route('/facebook-login/authorized')
def f_authorized():
    just_registered = False
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['facebook_token'] = (resp['access_token'], '')
    me = facebook.get('/me?fields=name,email,picture')

    # check for user
    user = User.query.filter_by(facebook_id=me.data['id']).first()
    if user is None:
        user = User.query.filter_by(register_email=me.data['email']).first()
        if user is None:
            user = User.register_facebook_user(me.data['name'], me.data['email'], me.data['id'])
            just_registered = True
        else:
            user.facebook_id = me.data['id']
            user.f_username = me.data['name']
    user.last_login = datetime.utcnow()
    print(me.data)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    if just_registered:
        welcome_procedure()
    if "follow" in session:
        next_url = session["follow"]
    else:
        next_url = url_for('root')
    return redirect(next_url)


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_token')


# LOGIN LOGOUT
#=============================================================

@social.route('/login')
def login():
    return redirect(url_for('root'))


@social.route('/logout')
@login_required
def logout():
    session.pop('google_token', None)
    session.pop('facebook_token', None)
    logout_user()
    return redirect(url_for('root'))




# USER PROFILE
#=============================================================
@social.route('/profile')
@login_required
def profile():
    u = current_user
    return render_template('profile.html', u=u)


@social.route('/check-nick', methods=['POST'])
@login_required
def check_nick():
    query = request.json
    res = User.query.filter_by(nickname=query['val']).count()
    return json.dumps({"val": res})


@social.route('/save-nick', methods=['POST'])
@login_required
def save_nick():
    query = request.json
    if User.query.filter_by(nickname=query['val']).count() == 0:
        current_user.nickname = query['val']
        db.session.add(current_user)
        db.session.commit()
        return json.dumps({"val": True})
    return json.dumps({"val": False})


# AVATAR UPLOAD
#=============================================================

import os
from werkzeug.utils import secure_filename

AVATAR_ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_FILE_SIZE = 1024*1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in AVATAR_ALLOWED_EXTENSIONS


def avatar_picture_upload(f, user, skipFileSize): #  f - FileStorage objct

    has_size_error = False
    if not skipFileSize:
        if bool(f.filename):
            file_bytes = f.read(MAX_FILE_SIZE)
            f.seek(0)
            has_size_error = len(file_bytes) == MAX_FILE_SIZE

    if f and allowed_file(f.filename) and not has_size_error:
        filename = secure_filename(f.filename)
        file_path = os.path.join(ROOT_DIR, UPLOAD_DIR, 'avatars', filename)
        f.save(file_path)
        f = open(file_path, "rb")
        img = Image.open(f)
        max_size = 160

        if (img.size[0] >= img.size[1]):
            img.thumbnail([max_size*100, max_size])
            off = int((img.size[0]-max_size)/2)
            img2 = img.crop([off, 0, off+max_size, max_size])
        else:
            img.thumbnail([max_size, max_size*100])
            off = int((img.size[1]-max_size)/2)
            img2 = img.crop([0, off, max_size, off+max_size])

        ava_name = get_hash(str(user.id)+filename)+".png"
        print('ava name: '+ava_name)
        old_ava_name = user.image
        user.image = ava_name
        db.session.add(user)
        db.session.commit()

        img2.save(os.path.join(ROOT_DIR, 'social', 'static', 'images', 'avatars', ava_name), "PNG")
        f.close()
        os.remove(file_path)
        if old_ava_name:
            os.remove(os.path.join(ROOT_DIR, 'social', 'static', 'images', 'avatars', old_ava_name))


@social.route('/avatar-upload', methods=['POST'])
def avatar_upload():

    if 'file' not in request.files:
        flash('Выберите файл с помощью кнопки Обзор')

    file = request.files['file']

    print()
    print (file)



    if file.filename == '':

        flash('Выберите файл с помощью кнопки Обзор')

    avatar_picture_upload(file, current_user)

    return json.dumps({"url": current_user.get_avatar()})


# USER EVENTS
#=============================================================
@login_required
@social.route('/user/events', methods=['GET', 'POST'])
def user_events():
    if request.method == 'GET':
        nots = Notification.get(current_user).order_by(desc(Notification.id))
        nots_history = NotificationHistory.query.filter_by(user_to=current_user.id).order_by(desc(NotificationHistory.id))
        return render_template('user_events.html', nots=nots, nots_history=nots_history)

    elif request.method == 'POST':
        q = request.json
        if q['cmd']=='releaseNotifications':
            Notification.release('events', user_to=current_user.id)
            return (json.dumps({'status':'ok'}))


# USER TIPS
#=============================================================
@login_required
@social.route('/my-tips', methods=['GET'])
def my_tips():
    if current_user.is_authenticated:
        tips = get_tips_data(current_user.tips)
        tips['config'] = {
                        'page': 'public_profile',
                        'allowFilters': False,
                        'allowAddNewTip': False,
                        'allowEdit': True
                    }
        tips['all_tags'] = get_all_tags()
        return render_template('my_tips.html', json_data=json.dumps(tips), signed_in=True)
    else:
        return redirect(url_for('root'))


# PRIVATE MESSAGES
#=============================================================
@login_required
@social.route('/private-messages', methods=['GET'])
def messenger():
    sel = request.args.get('user')
    u = current_user
    return render_template('messenger.html', u=u, sel=sel)


@login_required
@social.route('/post-messenger', methods=['POST'])
def post_messenger():

    query = request.json

    if query['cmd'] == 'sendMessage':
        print('sendMessage')
        ur = UsersRelationship.query.filter(
            and_(
                UsersRelationship.user1 == current_user.id,
                UsersRelationship.user2 == query['uid'])
            ).first()

        if (not ur or ur.can_send_pm_to):
            print('allowed')
            txt = query['text']
            current_user.send_private_message(query['uid'], txt)
            status = 'ok'
            Notification.add(
                                query['uid'],
                                'PM',
                                'Вы получили новое сообщение от пользователя '
                                +current_user.nickname,
                                user_from=current_user.id,
                                data=txt
                            )
        else:
            print('disabled')
            status = 'disabled'
        return json.dumps({'status': status})

    elif query['cmd'] == 'loadUserData':
        u = User.query.get(query['uid'])

        pm = PrivateMessage.query.filter(
            or_(
                and_(
                    PrivateMessage.user_from == current_user.id,
                    PrivateMessage.user_to == query['uid']
                ),
                and_(
                    PrivateMessage.user_to == current_user.id,
                    PrivateMessage.user_from == query['uid']
                )
            )
        )

        msgs = []

        ur = UsersRelationship.query.filter(
            and_(
                UsersRelationship.user2 == current_user.id,
                UsersRelationship.user1 == query['uid']
            )
        ).first()

        isBanned = True
        if not ur or ur.can_send_pm_to:
            isBanned = False

        for m in pm:
            msgs.append({"text": m.text, "sender": m.user_from, "ago":how_long_ago(m.timestamp)})
        return json.dumps({'name': u.nickname, 'status': 'ok', 'messages': msgs, 'isBanned': isBanned})

    elif query['cmd'] == 'getContacts':
        cl = current_user.get_contacted_users()
        for c in cl['list']:
            c['unread']=Notification.count(current_user, sender=c['uid'])['messages']
        cl['status'] = 'ok'
        return json.dumps(cl)

    elif query['cmd'] == 'toggleBanUser':
        ur = UsersRelationship.query.filter(
            and_(
                UsersRelationship.user2 == current_user.id,
                UsersRelationship.user1 == query['uid']
            )
        ).first()
        if not ur:
            ur = UsersRelationship()
            ur.user1 = query['uid']
            ur.user2 = current_user.id
            ur.can_send_pm_to = False
        else:
            ur.can_send_pm_to = not ur.can_send_pm_to

        db.session.add(ur)
        db.session.commit()
        return json.dumps({'status': 'ok', 'banValue': ur.can_send_pm_to})

    elif query['cmd'] == 'releaseNotifications':
        Notification.release(
                            'conversation',
                            user_from=query['user_from'],
                            user_to=current_user.id
                            )
        unread = Notification.count(current_user)['messages']
        return json.dumps({'status': 'ok', 'unread': unread})


# PUBLIC PROFILE
#=============================================================
@social.route('/user/<uid>')
def public_profile(uid):

    u = User.query.get(uid)
    td = get_tips_data(u.tips)
    td['config'] = {
                        'page': 'public_profile',
                        'allowFilters': False,
                        'allowAddNewTip': True
        }


    cuia = current_user.is_authenticated
    if u:
        if cuia:
            ur = UsersRelationship.query.filter_by(user1=current_user.id, user2=u.id).first()
            subscribed = True if ur and ur.follows is True else False
            if (ur and ur.can_send_pm_to) or not ur:
                can_send_pm = True
            else:
                can_send_pm = False
        else:
            subscribed = False
            can_send_pm = True
        return render_template('public_profile.html', u=u,
                            json_data=json.dumps(td),
                            subscribed=subscribed,
                            can_send_pm=can_send_pm,
                            signed_in=cuia)
    else:
        abort(404)

# FAVORITES
#=============================================================
@login_required
@social.route('/favorites', methods=['GET'])
def favorites():
    tips = get_tips_data(current_user.faved)
    tips['config'] = {
                        'page': 'favorites',
                        'allowFilters': False,
                        'allowAddNewTip': False,
                        'allowPlacesList':True
                    }
    return render_template('favorites.html',
                            json_data=json.dumps(tips),
                            signed_in=True
                            )


# SUBSCRIPTIONS ***RESERVED***
#=============================================================
# @login_required
# @social.route('/subscriptions')
# def subscriptions():
#     return render_template('subscriptions.html')


# NOTIFIER
#=============================================================
@login_required
@social.route('/notifier', methods=['POST'])
def notifier():
    q=request.json
    if q['cmd'] == 'checkNotifications':
        if current_user.is_authenticated:
            notifications = Notification.count(current_user)
            return json.dumps({'messages': notifications['messages'],
                                'notifications': notifications['other'],
                                'status':'ok'})
        else:
            return json.dumps({'status':'not logged in'})


# USER SUBSCRIBE
#=============================================================
@social.route('/user-subscribe', methods=['POST'])
def user_subscribe():
    res = {"status":"ok"}
    print(request.json)
    uid = request.json['uid']
    bval = True if request.json['cmd']=="subscribe" else False
    if current_user.is_authenticated:
        ur = UsersRelationship.query.filter_by(user1=current_user.id, user2=uid).first()
        if not ur:
            ur = UsersRelationship()
            ur.user1 = current_user.id
            ur.user2 = uid
            ur.follows = bval
        else:
            if ur.follows is bval:
                res['status'] = "Already (un)subscribed"
            else:
                ur.follows = bval

        db.session.add(ur)
        db.session.commit()

    return json.dumps(res)





# EMAIL VERIFICATION
#=============================================================
@social.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'POST' and current_user.is_authenticated:
        email = request.json['email']
        current_user.contact_email = email
        current_user.contact_email_accepted = False
        db.session.add(current_user)
        db.session.commit()
        uid = current_user.id
        regmail = current_user.register_email
        hsh = get_hash(regmail+email)
        status = 'ok'
        try:
            Mailer.verify_mail(uid=uid, hash=hsh, email=email)
        except:
            status = 'not ok'
        return json.dumps({'status': status})
    else:
        uid = request.args['uid']
        hsh = request.args['code']
        u = User.query.get(uid)
        uhsh = get_hash(u.register_email+u.contact_email)
        if uhsh == hsh:
            u.contact_email_accepted = True
            db.session.add(u)
            db.session.commit()
            return redirect(url_for('social.profile'))
        else:
            return render_template('error.html', error='Bad confirmation code')
