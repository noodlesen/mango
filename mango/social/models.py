from . .db import db
from flask_login import UserMixin
from flask import session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from . .config import ADMIN_EMAILS
from datetime import datetime

#from sqlalchemy.sql import or_

import json


class PrivateMessage(db.Model):
    __tablename__ = "private_messages"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    user_from = db.Column(db.ForeignKey('users.id'))
    user_to = db.Column(db.ForeignKey('users.id'))
    sent_at = db.Column(db.DateTime)

    def __init__(self, user_to, text):
        self.sent_at = datetime.utcnow()
        self.text = text
        self.user_to = user_to


class UserToPlaceRelationship(db.Model):
    __tablename__ = 'users2places'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id'))
    place_id = db.Column(db.ForeignKey('G_places.id'))
    type = db.Column(db.String(1))


class UsersRelationship(db.Model):

    __tablename__ = 'users_relationships'
    id = db.Column(db.Integer, primary_key=True)
    user1 = db.Column(db.ForeignKey('users.id'))
    is_friend_to = db.Column(db.Boolean, default=False)
    follows = db.Column(db.Boolean, default=False)
    can_send_pm_to = db.Column(db.Boolean, default=True)
    user2 = db.Column(db.ForeignKey('users.id'))


users_favorites = db.Table('users_favorites',
                           db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                           db.Column('tip_id', db.Integer, db.ForeignKey('tips.id'))
                           )

users_upvotes = db.Table('users_upvotes',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                         db.Column('tip_id', db.Integer, db.ForeignKey('tips.id'))
                         )

users_downvotes = db.Table('users_downvotes',
                           db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                           db.Column('tip_id', db.Integer, db.ForeignKey('tips.id'))
                           )


class User (UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    register_email = db.Column(db.String(100), unique=True)
    contact_email = db.Column(db.String(100))
    contact_email_accepted = db.Column(db.Boolean, default = False)
    g_username = db.Column(db.String(50))
    f_username = db.Column(db.String(50))
    vk_username = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    password_hash = db.Column(db.String(64))
    google_id =db.Column(db.String(255), unique=True)
    facebook_id =db.Column(db.String(255), unique=True)
    vk_id =db.Column(db.String(255), unique=True)
    image =db.Column(db.String(250), unique=True)
    last_login = db.Column(db.DateTime)
    worker = db.Column(db.Boolean, default = False)
    registered_at = db.Column(db.DateTime)
    changed_at = db.Column(db.DateTime)
    status = db.Column(db.Text)
    url = db.Column(db.String(255))


    private_messages_from = db.relationship('PrivateMessage', backref='sender', lazy='dynamic', foreign_keys='PrivateMessage.user_from')
    private_messages_to = db.relationship('PrivateMessage', backref='recipient', lazy='dynamic', foreign_keys='PrivateMessage.user_to')
    users_relationships = db.relationship('UsersRelationship', backref='user', lazy='dynamic', foreign_keys='UsersRelationship.user1')
    notifications = db.relationship('Notification', backref='recipient', lazy='dynamic', foreign_keys='Notification.user_to')



    # MANGO EXTRAS ===============================
    tips = db.relationship('Tip', backref='user', lazy='dynamic', foreign_keys='Tip.user_id')
    subscribed_places = db.relationship(
                                        'UserToPlaceRelationship',
                                        backref='subscriber',
                                        lazy='dynamic',
                                        foreign_keys='UserToPlaceRelationship.user_id'
                                        )
    power = db.Column(db.Integer, default=1)

    faved = db.relationship('Tip',
        secondary = users_favorites,
        backref = db.backref('faved_by', lazy = 'dynamic'),
        lazy = 'dynamic')

    upvoted = db.relationship('Tip',
        secondary = users_upvotes,
        backref = db.backref('upvoted_by', lazy = 'dynamic'),
        lazy = 'dynamic')

    downvoted = db.relationship('Tip',
        secondary = users_downvotes,
        backref = db.backref('downvoted_by', lazy = 'dynamic'),
        lazy = 'dynamic')

    def is_faved(self, tip):
        return self.faved.filter(users_favorites.c.tip_id == tip.id).count() > 0

    def fave(self, tip):
        if not self.is_faved(tip):
            self.faved.append(tip)
            db.session.add(self)
            db.session.commit()

    def remove_fave(self, tip):
        if self.is_faved(tip):
            self.faved.remove(tip)
            db.session.add(self)
            db.session.commit()

    def is_upvoted(self, tip):
        return self.upvoted.filter(users_upvotes.c.tip_id == tip.id).count() > 0

    def upvote(self, tip):
        if not self.is_upvoted(tip):
            self.upvoted.append(tip)
            tip.chd_upvoted += self.power
            db.session.add(self)
            db.session.add(tip)
            db.session.commit()

    def remove_upvote(self, tip):
        if self.is_upvoted(tip):
            self.upvoted.remove(tip)
            tip.chd_upvoted -= self.power
            if tip.chd_upvoted <0:
                tip.chd_upvoted = 0
            db.session.add(self)
            db.session.add(tip)
            db.session.commit()

    def is_downvoted(self, tip):
        return self.downvoted.filter(users_downvotes.c.tip_id == tip.id).count() > 0

    def downvote(self, tip):
        if not self.is_downvoted(tip):
            self.downvoted.append(tip)
            tip.chd_downvoted += self.power
            db.session.add(self)
            db.session.add(tip)
            db.session.commit()

    def remove_downvote(self, tip):
        if self.is_downvoted(tip):
            self.downvoted.remove(tip)
            tip.chd_downvoted -= self.power
            if tip.chd_downvoted <0:
                tip.chd_downvoted = 0
            db.session.add(self)
            db.session.add(tip)
            db.session.commit()

    def get_place_actions(self, pid):
        res={}
        query = "SELECT f.tip_id, t.text FROM %s as f JOIN tips as t ON t.id=f.tip_id AND t.place_id=%d WHERE f.user_id=%d"
        res['favorites'] = [n[0] for n in db.session.execute(query % ("users_favorites", pid, self.id))]
        res['likes'] = [n[0] for n in db.session.execute(query % ("users_upvotes", pid, self.id))]
        res['dislikes'] = [n[0] for n in db.session.execute(query % ("users_downvotes", pid, self.id))]
        return res

    def get_list_actions(self, ids):
        res={}
        idss = ','.join([str(i) for i in ids])
        query = "SELECT tip_id FROM %s WHERE user_id=%d AND tip_id IN (%s)"
        res['favorites'] = [n[0] for n in db.session.execute(query % ("users_favorites",self.id, idss))]
        res['likes'] = [n[0] for n in db.session.execute(query % ("users_upvotes", self.id, idss))]
        res['dislikes'] = [n[0] for n in db.session.execute(query % ("users_downvotes",self.id, idss))]
        return res


    #=============================================

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register(username, password):
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def register_google_user(username, email, google_id):
        if username == '':
            username = email
        user = User(g_username=username, nickname=username, register_email=email, contact_email=email, google_id=google_id, contact_email_accepted=True)
        db.session.add(user)
        db.session.commit()
        #StrangersLog.write('google_sign_up')
        return user

    @staticmethod
    def register_facebook_user(username, email, facebook_id):
        if username == '':
            username = email
        user = User(f_username=username, nickname=username, register_email=email, contact_email=email, facebook_id=facebook_id, contact_email_accepted=True)
        db.session.add(user)
        db.session.commit()
        #StrangersLog.write('fb_sign_up')
        return user

    @staticmethod
    def register_vk_user(username, email, vk_id):
        if username == '':
            username = email
        user = User(vk_username=username, nickname=username, register_email=email, contact_email=email, vk_id=vk_id, contact_email_accepted=True)
        db.session.add(user)
        db.session.commit()
        #StrangersLog.write('vk_sign_up')
        return user

    def __repr__(self):
        return '<User {0}>'.format(self.nickname)


    def get_email_status(self):
        extra=''
        if self.contact_email_accepted:
            email = self.contact_email
            status = "ok"
            if self.contact_email == self.register_email:
                extra = 'not changed'
            else:
                extra = 'changed'
        else:
            email = self.register_email
            status = "not verified"
            extra = self.contact_email
        return {"email":email, "staus":status, "extra":extra}


    def is_admin(self):
        return (self.email in ADMIN_EMAILS)

    def send_private_message(self, user_to, text):
        pm = PrivateMessage(user_to, text)
        pm.user_from = self.id
        db.session.add(pm)
        db.session.commit()

    def get_contacted_users(self):
        #REBUILD IT
        contacted=[]
        #sent
        pms = PrivateMessage.query.filter(PrivateMessage.user_from==self.id)
        for m in pms:
            user_info={"name":m.recipient.nickname, "uid":m.recipient.id, "img":m.recipient.get_avatar()}
            if user_info not in contacted:
                contacted.append(user_info)
        #received
        pms = PrivateMessage.query.filter(PrivateMessage.user_to==self.id)
        for m in pms:
            user_info={"name":m.sender.nickname, "uid":m.sender.id, "img":m.sender.get_avatar()}
            if user_info not in contacted:
                contacted.append(user_info)

        return {"list":contacted, "length":len(contacted)}

    def get_avatar(self):
        image = self.image
        if not image:
            image='avatar_placeholder.png'
        return (url_for('social.static', filename='images/avatars/'+image))


class NotificationMixin():
    id = db.Column(db.Integer, primary_key=True)
    ntype = db.Column(db.String(20))
    user_from = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime)
    message = db.Column(db.Text)
    data = db.Column(db.Text)
    extra = db.Column(db.Text)

    def get_extras(self):
        return json.loads(self.extra)


class NotificationHistory(db.Model, NotificationMixin):
    __tablename__ = 'notification_history'
    user_to = db.Column(db.Integer)
    archived_at = db.Column(db.DateTime)


class Notification(db.Model, NotificationMixin):

    __tablename__ = 'notifications'
    user_to = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, user_to, ntype, message, **kwargs):
        self.user_to = user_to
        self.message = message

        if 'data' in kwargs:
            self.data = kwargs['data']
        else:
            self.data=''

        if 'extra' in kwargs:
            self.extra = json.dumps(kwargs['extra'])
        else:
            self.extra=None

        if 'user_from' in kwargs:
            self.user_from = kwargs['user_from']
        else:
            self.user_from = 0

        self.ntype = ntype
        self.created_at = datetime.utcnow()


    def add(user_to, ntype, message, **kwargs):
        n = Notification(user_to, ntype, message, **kwargs)
        db.session.add(n)
        db.session.commit()

    def get (recipient):
        return Notification.query.filter_by(user_to=recipient.id)

    def count (recipient, **kwargs):
        res={"total": 0, "messages": 0, "other":0}
        if 'sender' in kwargs:
            nots = Notification.query.filter_by(user_to=recipient.id, user_from=kwargs['sender'])
        else:
            nots = Notification.query.filter_by(user_to=recipient.id)
        for n in nots:
            res['total']+=1
            if n.ntype=='PM':
                res['messages'] += 1
            else:
                res['other'] += 1
        return res

    def release(mode, **kwargs):
        if mode == 'conversation':
            Notification.query.filter(
                Notification.user_from == kwargs["user_from"],
                Notification.user_to == kwargs["user_to"]
                ).delete()
            db.session.commit()
        elif mode == 'events':
            nots = Notification.query.filter(
                Notification.user_to == kwargs["user_to"],
                Notification.ntype != 'PM'
                )
            for n in nots:
                h = NotificationHistory()
                h.user_from = n.user_from
                h.user_to = n.user_to
                h.ntype = n.ntype
                h.created_at = n.created_at
                h.message = n.message
                h.data = n.data

                h.archived_at = datetime.utcnow()

                db.session.add(h)

            nots.delete()

            db.session.commit()













