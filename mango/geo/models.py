from . .db import db



class Direction(db.Model):
    __tablename__ = 'G_directions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    rus_name = db.Column(db.String(100))
    countries = db.relationship('Country', backref='direction', lazy='dynamic')


class Country(db.Model):
    __tablename__ = 'G_countries'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(2))
    name = db.Column(db.String(100))
    rus_name = db.Column(db.String(100))
    direction_id = db.Column(db.Integer, db.ForeignKey('G_directions.id'))
    places = db.relationship('Place', backref='country', lazy='dynamic')
    old_kdb_id = db.Column(db.Integer)


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
    active = db.Column(db.Boolean, default=False)


class GeoAlias(db.Model):
    __tablename__='G_aliases'
    id = db.Column(db.Integer, primary_key = True)
    alias = db.Column(db.String(50))
    location_id = db.Column(db.Integer, db.ForeignKey('G_places.id'))


tags2tips = db.Table ('tags2tips',
       db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')), 
       db.Column('tip_id', db.Integer, db.ForeignKey('tips.id'))
    )

class TipRelation():

    def get(user_id, rtype):
        sqlres = db.engine.execute('SELECT `tip_id` FROM `users2tips` WHERE `user_id`=%d AND `type`="%s"' % (user_id, rtype))
        res=[]
        for r in sqlres:
            res.append(r[0])
        return (res)

    def add(user_id, tip_id, rtype):
        db.engine.execute('INSERT INTO `users2tips` (`user_id`, `tip_id`, `type`) VALUES (%d, %d, "%s")' % (user_id, tip_id, rtype))

    def remove(user_id, tip_id, rtype):
        db.engine.execute('DELETE FROM `users2tips` WHERE `user_id`=%d AND `tip_id`=%d AND `type`="%s"' % (user_id, tip_id, rtype))

class Tip(db.Model):
    __tablename__ = 'tips'
    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer, db.ForeignKey('G_places.id'))
    text = db.Column(db.Text)
    comments = db.Column(db.Text)
    tags = db.relationship('Tag', secondary=tags2tips, backref=db.backref('tips', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    #temp
    taglines = db.Column(db.Text)
    sex = db.Column(db.String(1))

    def favorited_by(u):
        return TipRelation.get(u.id, "F")

    def set_as_favorite(self, u):
        TipRelation.add(u.id, self.id, "F")

    def remove_favorite(self, u):
        TipRelation.remove(u.id, self.id, "F")


    def liked_by(u):
        return TipRelation.get(u.id, "L")

    def set_like(self, u):
        TipRelation.add(u.id, self.id, "L")

    def remove_like(self, u):
        TipRelation.remove(u.id, self.id, "L")

    def disliked_by(u):
        return TipRelation.get(u.id, "D")

    def set_dislike(self, u):
        TipRelation.add(u.id, self.id, "D")

    def remove_dislike(self, u):
        TipRelation.remove(u.id, self.id, "D")




class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    style = db.Column(db.String(20))
    count = db.Column(db.Integer)








