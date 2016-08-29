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


class GeoAlias(db.Model):
    __tablename__='G_aliases'
    id = db.Column(db.Integer, primary_key = True)
    alias = db.Column(db.String(50))
    location_id = db.Column(db.Integer, db.ForeignKey('G_places.id'))
