from app import app, db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Oprecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    location = db.Column(db.String(50))
    area = db.Column(db.String(50))
    type_room = db.Column(db.String(50))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    guest = db.Column(db.String(50))
    price_1 = db.Column(db.String(50))
    price_2 = db.Column(db.String(50))
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)
