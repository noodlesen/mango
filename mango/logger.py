from .db import db
from flask import session
from datetime import datetime
from flask.ext.login import current_user
import json


class UsersLog(db.Model):

    __tablename__ = 'users_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    action = db.Column(db.String(50))
    data = db.Column(db.Text)
    logged_at = db.Column(db.DateTime)

    @staticmethod
    def write(act, data=""):
        if current_user.is_authenticated:
            l = UsersLog()
            l.user_id = current_user.id
            l.action = act
            l.data = json.dumps(data)
            l.logged_at = datetime.now()
            db.session.add(l)
            db.session.commit()


class StrangersLog(db.Model):
    __tablename__ = 'strangers_log'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50))
    entry = db.Column(db.String(50))
    label = db.Column(db.String(50))
    marker = db.Column(db.Text)
    note = db.Column(db.Text)
    logged_at = db.Column(db.DateTime)

    @staticmethod
    def write(action, note=''):
        l = StrangersLog()
        if 'marker' in session.keys():
            l.marker = session['marker']
        else:
            l.marker = 'None'
        if 'entry' in session.keys():
            l.entry = session['entry']
        else:
            l.entry = 'None'
        if 'label' in session.keys():
            l.label = session['label']
        else:
            l.label = 'None'

            l.note = note

        l.action = action
        l.logged_at = datetime.utcnow()
        db.session.add(l)
        db.session.commit()
