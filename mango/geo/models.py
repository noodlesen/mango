import json
from datetime import datetime
from flask import url_for

from . .db import db



class Direction(db.Model):
    __tablename__ = 'G_directions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    rus_name = db.Column(db.String(100))
    countries = db.relationship('Country', backref='direction', lazy='dynamic')
    url_string = db.Column(db.String(50))







class Country(db.Model):
    __tablename__ = 'G_countries'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(2))
    name = db.Column(db.String(100))
    rus_name = db.Column(db.String(100))
    direction_id = db.Column(db.Integer, db.ForeignKey('G_directions.id'))
    places = db.relationship('Place', backref='country', lazy='dynamic')
    old_kdb_id = db.Column(db.Integer)
    url_string = db.Column(db.String(50))







class Place(db.Model):
    __tablename__ = 'G_places'
    id = db.Column(db.Integer, primary_key=True)
    eng_name = db.Column(db.String(50))
    rus_name = db.Column(db.String(50))
    number = db.Column(db.Integer)
    UFI = db.Column(db.Integer)
    eng_address = db.Column(db.Text)
    rus_address = db.Column(db.Text)
    lat=db.Column(db.Float)
    lng=db.Column(db.Float)
    aliases = db.relationship('GeoAlias', backref='place', lazy='dynamic')
    country_id = db.Column(db.Integer, db.ForeignKey('G_countries.id'))
    fpid = db.Column(db.Integer)
    url_string = db.Column(db.String(50))
    image = db.Column(db.String(50))
    tips = db.relationship('Tip', backref='place', lazy='dynamic')
    chd_has_tips = db.Column(db.Boolean, default=False)
    chd_places_nearby = db.Column(db.Text)
    chd_airports = db.Column(db.Text)
    tp_rus_name = db.Column(db.String(50))
    tp_eng_name = db.Column(db.String(50))
    city_code = db.Column(db.String(3))
    modified_at = db.Column(db.DateTime)

    def get_places_nearby(self):
        pn_json = self.chd_places_nearby
        if pn_json:
            pn_list = json.loads(pn_json)
        else:
            pn_list = []
        return {"list": pn_list, "count": len(pn_list)}

    def get_airports(self):
        ap_json = self.chd_airports
        if ap_json:
            ap_list = json.loads(ap_json)
        else:
            ap_list = []
        return {"list": ap_list, "count": len(ap_list)}

    def bake(self):
        self.modified_at = datetime.utcnow()
        if self.tips.count()>0:
            self.chd_has_tips=True
        db.session.add(self)
        db.session.commit()




class GeoAlias(db.Model):
    __tablename__='G_aliases'
    id = db.Column(db.Integer, primary_key = True)
    alias = db.Column(db.String(50))
    location_id = db.Column(db.Integer, db.ForeignKey('G_places.id'))







tags2tips = db.Table ('tags2tips',
       db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')), 
       db.Column('tip_id', db.Integer, db.ForeignKey('tips.id'))
    )





# TIP CLASS ================================================================================

class Tip(db.Model):
    __tablename__ = 'tips'
    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer, db.ForeignKey('G_places.id'))
    text = db.Column(db.Text)
    comments = db.Column(db.Text)
    tags = db.relationship('Tag', secondary=tags2tips, backref=db.backref('tips', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    chd_upvoted = db.Column(db.Integer, default=0)
    chd_downvoted = db.Column(db.Integer, default=0)
    chd_rating = db.Column(db.Integer, default=0)
    chd_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    chd_comments_count = db.Column(db.Integer, default=0)
    taglines = db.Column(db.Text)
    attached_url = db.Column(db.String(255))

    #temp
    taglines = db.Column(db.Text)
    sex = db.Column(db.String(1))


    def cache_it(self):
        cache = {
                "author":{'id':self.user.id, 'name':self.user.nickname},
                "tags":[],
                "url": url_for('geo.places', us=self.place.url_string)+"?t="+str(self.id),
                "place": {"name": self.place.rus_name, "country": self.place.country.rus_name}
                }

        for tag in self.tags:
            cache['tags'].append({"id": tag.id,
                                "name": tag.name,
                                "style": tag.style,
                                "count": tag.count
                })

        self.chd_rating = self.chd_upvoted - self.chd_downvoted
        self.chd_data = json.dumps(cache)

        db.session.add(self)
        db.session.commit()

    def resetRating(self):
        db.session.execute('DELETE FROM users_upvotes WHERE tip_id=%d' % self.id)
        db.session.execute('DELETE FROM users_downvotes WHERE tip_id=%d' % self.id)
        self.chd_downvoted = 0
        self.chd_upvoted = 0
        self.chd_rating = 0
        db.session.add(self)
        db.session.commit()






# TAG CLASS ==========================================================================================

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    style = db.Column(db.String(20))
    count = db.Column(db.Integer)








