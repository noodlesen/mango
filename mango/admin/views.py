from flask import render_template, request, abort, redirect, url_for, session
from flask_login import current_user, login_required, login_user, logout_user
from . .db import db
from . .social.models import User
from . import admin

import json



def relogin(u):
    session.pop('google_token', None)
    session.pop('facebook_token', None)
    logout_user()
    login_user(u)

@admin.route('/admin', methods=['GET'])
@login_required
def admin_main():
    return render_template('admin_main.html',wrk=[{"nickname":"test", "id":0}])
    # if current_user.is_admin() or current_user.worker==1:
    #     wrk = User.query.filter_by(worker=1)
    #     return render_template('admin_main.html', wrk=wrk)
    # else:
    #     return render_template('404.html')

@admin.route('/worker/login/<wid>', methods=['GET'])
@login_required
def worker_login(wid):
    try:
        u = User.query.filter_by(id = wid).first()
    except:
        return redirect(url_for('root'))

    if (current_user.is_admin() or current_user.worker==1) and u.worker == 1:
        relogin(u)
    return redirect(url_for('admin.admin_main'))



