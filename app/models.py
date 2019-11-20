from app import app, db
from datetime import datetime

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.public_id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.public_id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), index=True, unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    posts = db.relationship('OwnerPost', backref='author', lazy='dynamic')
    # booked_house = db.relationship('Booking', backref='renter')
    admin = db.Column(db.Boolean)
    followed = db.relationship('User', secondary=followers,
        primaryjoin=(followers.c.follower_id == public_id),
        secondaryjoin=(followers.c.followed_id == public_id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    def __repr__(self):
        return '<User {}>'.format(self.name)
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.public_id).count() > 0

    def followed_posts(self):
        followed = OwnerPost.query.join(
            followers, (followers.c.followed_id == OwnerPost.user_id)).filter(
                followers.c.follower_id == self.public_id)
        own = OwnerPost.query.filter_by(user_id=self.public_id)
        return followed.union(own).order_by(OwnerPost.timestamp.desc())



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

class OwnerPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking = db.relationship('Booking', backref='booked_post')
    user_id = db.Column(db.String(50),db.ForeignKey('user.public_id'), index=True)
    location = db.Column(db.String(50))
    area = db.Column(db.String(50))
    type_room = db.Column(db.String(50))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    guest = db.Column(db.String(50))
    price_1 = db.Column(db.String(50))
    price_2 = db.Column(db.String(50))
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)
    Available = db.Column(db.Boolean)
    def __repr__(self):
        return '<Post {}>'.format(self.location)
    @property
    def serialize(self):
        return {
            'location'  : self.location,
            'area'      : self.area,
            'type_room' : self.type_room,
            'start_date': self.start_date,
            'end_date'  : self.end_date,
            'guest'     : self.guest,
            'price_1'   : self.price_1,
            'price_2'   : self.price_2,
            'Available' : self.Available
        }


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.String(50), db.ForeignKey('user.public_id'))
    listing_id =  db.Column(db.String(50),db.ForeignKey('owner_post.id'))    
    renter_id =  db.Column(db.String(50),db.ForeignKey('user.public_id'))
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    owner = db.relationship('User', foreign_keys=[owner_id])
    renter = db.relationship('User', foreign_keys=[renter_id])
    @property
    def serialize(self):
        return {
            'owner_id'  : self.owner_id,
            'listing_id': self.listing_id,
            'renter_id': self.renter_id,
            'start_date': self.start_date,
            'end_date'  : self.end_date
        }

class Df(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    host_id = db.Column(db.String(50))
    host_name = db.Column(db.String(50))
    neighbourhood_group = db.Column(db.String(50))
    neighbourhood = db.Column(db.String(50))
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    room_type = db.Column(db.String(50))
    price = db.Column(db.Integer)
    minimum_nights = db.Column(db.Integer)
    number_of_reviews = db.Column(db.String(50))
    last_review = db.Column(db.String(50))
    reviews_per_month = db.Column(db.String(50))
    calculated_host_listings_count = db.Column(db.String(50))
    availability_365 = db.Column(db.String(50))
    @property
    def serialize(self):
        return {
            'id'  : self.id,
            'name': self.name,
            'host_id': self.host_id,
            'host_name': self.host_name,
            'neighbourhood_group'  : self.neighbourhood_group,
            'neighbourhood' : self.neighbourhood,
            'latitude' : self.latitude,
            'longitude' : self.longitude,
            'room_type' : self.room_type,
            'price' : self.price,
            'minimum_nights' : self.minimum_nights,
            'last_review' : self.last_review,
            'reviews_per_month' : self.reviews_per_month,
            'calculated_host_listings_count' : self.calculated_host_listings_count,
            'availability_365' : self.availability_365,
        }

class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String(50))
    _type = db.Column(db.String(50))
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))



class Michelin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    year = db.Column(db.String(50))
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    city = db.Column(db.String(50))
    cuisine = db.Column(db.String(50))
    price = db.Column(db.String(50))
    url = db.Column(db.String(50))
    star = db.Column(db.String(50))
