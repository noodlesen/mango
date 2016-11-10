from flask_login import current_user
import json
from flask import session, request
from .dttools import RTS
from .toolbox import create_marker
from .path import _ROOT_DIR

class Log():

    def register(**kwargs):

        if 'marker' not in session.keys():
            session['marker']=create_marker(request)
        marker = session['marker']
        
        action = kwargs['action'] if 'action' in kwargs else None

        dt = RTS.utc_now()

        data = kwargs['data'] if 'data' in kwargs else None

        if current_user.is_authenticated:
            agent = {"name": current_user.nickname, "id":current_user.id}
            logfile = 'logs/users_%s.log' % dt[:10]
        else:
            agent = {"marker":marker}
            logfile = 'logs/strangers_%s.log' % dt[:10]

        logfile=_ROOT_DIR+"/"+logfile

        with open(logfile, 'a') as l:
            l.write(json.dumps([dt, agent, action, data])+',\n')














