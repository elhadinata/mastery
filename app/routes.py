from app import app, db
from app.models import User, Oprecord, OwnerPost, Booking
from app.models import User, Oprecord, OwnerPost, Michelin,Station,Df
from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for
import uuid
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from functools import wraps
from app.forms import SearchForm
from app import search_model, api
from flask_restplus import Resource
import json
import paypalrestsdk
import pandas as pd
import time
from ml import *
from flask_restplus import Resource, Api, abort
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from sqlalchemy import or_, and_

paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AS9hENrxNu3ih4aoEKWdVcgSM3VWsKn7wPFE01C5C6fOneALiB6PmASnNpGPzwDOm9WTll6h_9gk3mla",
  "client_secret": "EJfjLG8mh3pi9AKaN97Sr7ackqvk6cUhD7zTAcy2d1IqPG_jPSP46hdbFviXzto_SWxksROVwajlIhS2" })

def get_data_cluster():
    mmm = Michelin.query.all()
    sss = Station.query.all()
    ddd = Df.query.all()
    mi_res = []
    for mm in mmm:
        mi_rec = {}
        mi_rec['name'] = mm.name
        mi_rec['year'] = mm.year
        mi_rec['latitude'] = mm.latitude
        mi_rec['longitude'] = mm.longitude
        mi_rec['city'] = mm.city
        mi_rec['cuisine'] = mm.cuisine
        mi_rec['price'] = mm.price
        mi_rec['url'] = mm.url
        mi_rec['star'] = mm.star
        mi_res.append(mi_rec)
    df_mi = pd.DataFrame(mi_res)

    sta_bus = []
    for ss in sss:
        sta_rec = {}
        sta_rec['station_name'] = ss.station_name
        sta_rec['_type'] = ss._type
        sta_rec['latitude'] = ss.latitude
        sta_rec['longitude'] = ss.longitude
        sta_bus.append(sta_rec)

    df_st = pd.DataFrame(sta_bus)


    his_post = []
    for dd in ddd:
        his_rec = {}
        his_rec['name'] = dd.name
        his_rec['host_id'] = dd.host_id
        his_rec['host_name'] = dd.host_name
        his_rec['neighbourhood_group'] = dd.neighbourhood_group
        his_rec['neighbourhood'] = dd.neighbourhood
        his_rec['latitude'] = dd.latitude
        his_rec['longitude'] = dd.longitude
        his_rec['room_type'] = dd.room_type
        his_rec['price'] = dd.price
        his_rec['minimum_nights'] = dd.minimum_nights
        his_rec['number_of_reviews'] = dd.number_of_reviews
        his_rec['last_review'] = dd.last_review
        his_rec['reviews_per_month'] = dd.reviews_per_month
        his_rec['calculated_host_listings_count'] = dd.calculated_host_listings_count
        his_rec['availability_365'] = dd.availability_365
        his_post.append(his_rec)
    df_po = pd.DataFrame(his_post)
    return df_mi, df_st, df_po

# global variable
mi_pandas, st_pandas, post_pandas = get_data_cluster()




def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated



register_model = api.model('register', {
    'username': fields.String,
    'password': fields.String
})
@api.route('/user_register')
class UserRegister(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Username already exists!')
    @api.doc(description="User registration.")
    @api.expect(register_model, validate=True)
    def post(self):
        data = request.get_json()
        password = data['password']
        name = data['username']
        print(name+' '+password)
        user = User.query.filter_by(name = name).first()
        if user:
            return make_response('Username already exists!', 401, {'Username': 'username already exists!"'})
        
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(public_id=str(uuid.uuid4()), name=name, password=hashed_password, admin=True)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({ "message": "User successfully registered" })


@api.route('/userlist')
class GetUserList(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Forbidden : Need ADMIN')
    @api.doc(description="Get all the users list, this function requires admin user.")
    def get(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})
        if not current_user.admin:
            make_response('message', 403, {'Username': 'need admin user'})
        users = User.query.all()
        output = []
        for user in users:
            user_data = {}
            user_data['public_id'] = user.public_id
            user_data['name'] = user.name
            user_data['password'] = user.password
            user_data['admin'] = user.admin
            output.append(user_data)
        return jsonify({'users': output})


@api.route('/user/<public_id>')
class GetOneUser(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Forbidden : Need ADMIN')
    @api.doc(description="Get a single user by their public_id, this function requires admin user.")
    def get(self,public_id):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
           
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})
        if not current_user.admin:
            return make_response('message', 403, {'Username': 'need admin user to perform function'})

        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return make_response('message', 403, {'Username': 'need admin user to perform function'})
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        return jsonify({'user': user_data})


credential_model = api.model('credential', {
    'username': fields.String,
    'password': fields.String
})


credential_parser = reqparse.RequestParser()
credential_parser.add_argument('username', type=str)
credential_parser.add_argument('password', type=str)


@api.route('/token')
class TokenGeneration(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Generates a authentication token.")
    @api.expect(credential_parser, validate=True)
    def get(self):
        args = credential_parser.parse_args()
        username = args.get('username')
        password = args.get('password')
        if not username or not password:
            return make_response('Empty fields - Could not verify', 401, {'www-auth': 'basic realm="authentication required!"'})
        user = User.query.filter_by(name=username).first()
        if not user:
            return make_response('Could not verify', 401, {'www-auth': 'basic realm="authentication required!"'})
        if check_password_hash(user.password, password):
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
            )+datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
            return jsonify({'token': token.decode('UTF-8')})
        return make_response('Could not verify', 401, {'www-auth': 'basic realm="authentication required!"'})

search_model = api.model('search', {
    'location': fields.String,
    'area': fields.String,
    'type_room':fields.String,
    'start_date': fields.String,
    'end_date' : fields.String,
    'guest': fields.String,
    'price_1': fields.String,
    'price_2': fields.String
})


@api.route('/search')
class SearchRoom(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Forbidden : Need ADMIN')
    @api.response(406, 'Input format error')
    @api.doc(description="Search for the room you want, leave empty parameters you don't want to input")
    @api.expect(search_model)
    def post(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})
        if not current_user.admin:
            return make_response('message', 403, {'Username': 'need admin user to perform function'})

        data = request.get_json()
        location = data['location']
        area = data['area']
        type_room = data['type_room']
        start_date = data['start_date']
        end_date = data['end_date']
        guest = data['guest']
        price_1 = data['price_1']
        price_2 = data['price_2']
        temp_dic = {'location': location, 'area': area, 'type_room': type_room, 'start_date': start_date,
                    'end_date': end_date, 'guest': guest, 'price_1': price_1, 'price_2': price_2
                    }
        if start_date == "":
            start_date = "1970-01-01"
        if end_date == "":
            end_date = "2021-01-01"
        try:

            time_s = time.mktime(time.strptime(start_date, "%Y-%m-%d"))

            # TODO check constraint
            time_e = time.mktime(time.strptime(end_date, "%Y-%m-%d"))


            during_time = int((time_e - time_s) / 86400)
            if price_1 == "":
                price_1 = 0
            if price_2 == "":
                price_2 = 9999999




            qq = Df.query.filter(Df.neighbourhood_group.ilike("%" + location + "%"),
                        Df.neighbourhood.ilike("%" + area + "%"),
                        Df.room_type.ilike("%" + type_room + "%"),
                        (Df.minimum_nights <= int(during_time)),
                        (Df.price >= int(price_1)),
                        (Df.price <= int(price_2))
                            ).all()
        except:
            return make_response('Format error', 406, {'value': 'format is Date: year-month-day, Price: integer, Room type:private room '})

        final_res = []

        for dd in qq:
            his_rec = {}

            his_rec['id'] = dd.id
            his_rec['name'] = dd.name
            his_rec['host_id'] = dd.host_id
            his_rec['host_name'] = dd.host_name
            his_rec['neighbourhood_group'] = dd.neighbourhood_group
            his_rec['neighbourhood'] = dd.neighbourhood
            his_rec['latitude'] = dd.latitude
            his_rec['longitude'] = dd.longitude
            his_rec['room_type'] = dd.room_type
            his_rec['price'] = dd.price
            his_rec['minimum_nights'] = dd.minimum_nights
            his_rec['number_of_reviews'] = dd.number_of_reviews
            his_rec['last_review'] = dd.last_review
            his_rec['reviews_per_month'] = dd.reviews_per_month
            his_rec['calculated_host_listings_count'] = dd.calculated_host_listings_count
            his_rec['availability_365'] = dd.availability_365
            final_res.append(his_rec)

        # first add a admin manully that control other user
        new_op = Oprecord(user_id=current_user.public_id, location=location, area=area,
                          type_room=type_room, start_date=start_date, end_date=end_date, guest=guest,
                          price_1=price_1, price_2=price_2)
        db.session.add(new_op)
        db.session.commit()
        return jsonify(final_res)



owner_model = api.model('accomodation', {
    'name': fields.String,
    'neighbourhood_group': fields.String,
    'neighbourhood': fields.String,
    'latitude': fields.String,
    'longitude': fields.String,
    'room_type': fields.String,
    'price': fields.String,
    'minimum_nights': fields.String,
    'number_of_reviews': fields.String,
    'last_review': fields.String,
    'reviews_per_month': fields.String,
    'calculated_host_listings_count': fields.String,
    'availability_365': fields.String,
})


@api.route('/accomodation/<int:id>')
class UserAccomodation(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Return recommendations according to room index.")
    def get(self, id):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})

        ml_model = ML_model()
        ml_model.prep_price_preds(post_pandas)
        row = ml_model.data.loc[id-1]
        rt = row["room_type"]
        ml_model.prep_knn_preds(rt)
        ml_model.build_knn_model()
        
        latitude = row['latitude']
        longitude = row['longitude']
        room_type = row['room_type']
        price = row['price']
        minimum_nights = row['minimum_nights']
        
        
        result  = ml_model.knn_prediction(latitude,longitude,room_type,price,minimum_nights)
        
        room_detail = []
        output = []
        count = 0
        for ind in result:
            row = post_pandas.loc[ind]
            ele_data = {}
            ele_data['id'] = str(ind+1)
            ele_data['name'] = str(row['name'])
            ele_data['host_id'] = str(row['host_id'])
            ele_data['host_name'] = str(row['host_name'])
            ele_data['neighbourhood_group'] = str(row['neighbourhood_group'])
            ele_data['neighbourhood'] = str(row['neighbourhood'])
            ele_data['latitude'] = str(row['latitude'])
            ele_data['longitude'] = str(row['longitude'])
            ele_data['room_type'] = str(row['room_type'])
            ele_data['price'] = str(row['price'])
            ele_data['minimum_nights'] = str(row['minimum_nights'])
            ele_data['number_of_reviews'] = str(row['number_of_reviews'])
            ele_data['last_review'] = str(row['last_review'])
            ele_data['reviews_per_month'] = str(row['reviews_per_month'])
            ele_data['calculated_host_listings_count'] = str(row['calculated_host_listings_count'])
            ele_data['availability_365'] = str(row['availability_365'])
            if count == 0:
                room_detail.append(ele_data)
                count += 1
            else:
                output.append(ele_data)
        return jsonify({'single_detail':room_detail,'recommendation': output})


    @api.response(200, 'Successful')
    @api.response(400, 'Failed')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Post a new accommodation listing.")
    @api.expect(owner_model)
    def put(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})


        data = request.get_json()
        name = data['name']
        host_id = current_user.public_id
        host_name = current_user.name
        neighbourhood_group =data['location']
        neighbourhood = data['area']
        latitude = data['latitude']
        longitude = data['longitude']
        room_type = data['room_type']
        price = data['price']
        minimum_nights = data['minimum_nights']
        number_of_reviews = data['number_of_reviews']
        last_review = data['last_review']
        reviews_per_month = data['reviews_per_month']
        calculated_host_listings_count = data['calculated_host_listings_count']
        availability_365 = data['availability_365']
        
        res = Df.query.filter_by(host_id=current_user.public_id, id=id)
        if len(res.all()) == 0:
            return make_response('message', 404, {'Accomodation': 'Not found!'})
        res = res.first()

        
        temp_dic = {'name': name, 'host_id': host_id
                    , 'neighbourhood_group': neighbourhood_group
                    , 'neighbourhood': neighbourhood
                    , 'latitude': latitude
                    , 'longitude': longitude
                    , 'room_type': room_type
                    , 'price': price
                    , 'minimum_nights': minimum_nights
                    , 'number_of_reviews': number_of_reviews
                    , 'last_review': last_review
                    , 'reviews_per_month': reviews_per_month
                    , 'calculated_host_listings_count': calculated_host_listings_count
                    , 'availability_365': availability_365}

        res.name = name
        res.neighbourhood_group = neighbourhood_group
        res.neighbourhood = neighbourhood
        res.latitude = latitude
        res.longitude = longitude
        res.room_type = room_type
        res.price = price
        res.minimum_nights = minimum_nights
        res.number_of_reviews = number_of_reviews
        res.last_review = last_review
        res.reviews_per_month = reviews_per_month
        res.calculated_host_listings_count = calculated_host_listings_count
        res.availability_365 = availability_365

        db.session.commit()
        global mi_pandas, st_pandas, post_pandas
        mi_pandas, st_pandas, post_pandas = get_data_cluster()
        
        return jsonify({ "message": "Successful" })


    @api.response(200, 'Successful')
    @api.response(400, 'Failed')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Post a new accommodation listing.")
    def delete(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})

        res = Df.query.filter_by(id=id, host_id=current_user.public_id)
        if len(res.all()) == 0:
            return "Listing does not exist"
        res.delete()
        db.session.commit()
        return "Deleted the post with id {}".format(id)


@api.route('/statistics')
class SearchStatistics(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Forbidden : Need ADMIN')
    @api.doc(description="Get all user search records, this function requires admin user.")
    def get(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})

        if not current_user.admin:
            return make_response('message', 403, {'Username': 'need admin user to perform function'})
        ops = Oprecord.query.all()
        output = []
        for op in ops:
            op_data = {}
            op_data['id'] = op.id
            op_data['user_id'] = op.user_id
            op_data['location'] = op.location
            op_data['area'] = op.area
            op_data['type_room'] = op.type_room
            op_data['start_date'] = op.start_date
            op_data['end_date'] = op.end_date
            op_data['guest'] = op.guest
            op_data['price_1'] = op.price_1
            op_data['price_2'] = op.price_2
            op_data['time'] = op.time_stamp
            output.append(op_data)
        return jsonify({'users': output})


@api.route('/accommodation')
class Accomodation(Resource):
    @api.response(200, 'Successful')
    @api.response(400, 'Failed')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Post a new accommodation listing.")
    @api.expect(owner_model)
    def post(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})

        data = request.get_json()
        name = data['name']
        host_id = current_user.public_id
        host_name = current_user.name
        neighbourhood_group =data['neighbourhood_group']
        neighbourhood = data['neighbourhood']
        latitude = data['latitude']
        longitude = data['longitude']
        room_type = data['room_type']
        price = data['price']
        minimum_nights = data['minimum_nights']
        number_of_reviews = data['number_of_reviews']
        last_review = data['last_review']
        reviews_per_month = data['reviews_per_month']
        calculated_host_listings_count = data['calculated_host_listings_count']
        availability_365 = data['availability_365']
        
        
        temp_dic = {'name': name, 'host_id': host_id
                    , 'neighbourhood_group': neighbourhood_group
                    , 'neighbourhood': neighbourhood
                    , 'latitude': latitude
                    , 'longitude': longitude
                    , 'room_type': room_type
                    , 'price': price
                    , 'minimum_nights': minimum_nights
                    , 'number_of_reviews': number_of_reviews
                    , 'last_review': last_review
                    , 'reviews_per_month': reviews_per_month
                    , 'calculated_host_listings_count': calculated_host_listings_count
                    , 'availability_365': availability_365}

        new_op = Df(name=name
        , host_id=host_id, host_name=host_name
        , neighbourhood_group=neighbourhood_group
        , neighbourhood=neighbourhood
        , latitude=latitude
        , longitude=longitude
        , room_type=room_type
        , price=price
        , minimum_nights=minimum_nights
        , number_of_reviews=number_of_reviews
        , last_review=last_review
        , reviews_per_month=reviews_per_month
        , calculated_host_listings_count=calculated_host_listings_count
        , availability_365=availability_365)
        db.session.add(new_op)
        db.session.commit()
        global mi_pandas, st_pandas, post_pandas
        mi_pandas, st_pandas, post_pandas = get_data_cluster()
        return jsonify({ "message": "Successful" })


@api.route('/subscribe/<public_id>')
class SubscribeUser(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Let a user subscribe to another user with public_id")
    def get(self, public_id):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})

        user = User.query.filter_by(public_id=public_id).first()
        if user is None:
            return "user not exist"
        if user == current_user:
            return "wait, are you subscribe yourself?"
        current_user.follow(user)
        db.session.commit()
        return "success!"


@api.route('/unsubscribe/<public_id>')
class UnSubscribeUser(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Let a user unsubscribe from another user with public_id")
    def get(self, public_id):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})
        user = User.query.filter_by(public_id=public_id).first()
        if user is None:
            return "user not exist"
        if user == current_user:
            return "wait, are you unsubscribe yourself?"
        current_user.unfollow(user)
        db.session.commit()
        return "unscribe success"


@app.route('/makepay')
def makepay():
    return render_template('makepay.html')


@app.route('/payment', methods=['POST'])
def payment():
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:5000/makepay/success",
            "cancel_url": "http://localhost:5000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "testitem",
                    "sku": "12345",
                    "price": "20.00",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "20.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        print('Payment success!')
    else:
        print(payment.error)
    return jsonify({'paymentID' : payment.id})


@app.route('/execute', methods=['POST'])
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        success = True
    else:
        print(payment.error)
    return jsonify({'success' : success})


# ===================== CUSTOMER ============================== #
# For customer to see all their bookings and make new bookings
@api.route('/book')
class GetBooking(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Get all the bookings of the current user")
    def get(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})
        booking = Booking.query.filter_by(renter_id=current_user.public_id).all()    
        return jsonify(booking=[i.serialize for i in booking])


@api.route('/book/<int:id>')
class MakeBooking(Resource):
    @api.response(201, 'Booking Created')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Make a booking on an accomodation")
    def post(self, id):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})

        owner_post = Df.query.filter_by(id=id)
    
        if len(owner_post.all()) == 0:
            return "404, Cant find accomodation"
        
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if start_date == "":
            start_date = "1970-01-01"
        if end_date == "":
            end_date = "2021-01-01"

        time_s = time.mktime(time.strptime(start_date, "%Y-%m-%d"))
        time_e = time.mktime(time.strptime(end_date, "%Y-%m-%d"))
        duration = int((time_e - time_s) / 86400)

        if duration < int(owner_post.first().minimum_nights):
            return "403, Duration below requirement"

        df_data = owner_post.first()
        df_data.availability_365 = str(int(df_data.availability_365)-duration)

        booking = Booking(owner_id=owner_post.first().host_id, listing_id=id, renter_id=current_user.public_id, start_date=start_date, end_date=end_date)
        host_id = owner_post.first().host_id
        
        db.session.add(booking)
        db.session.commit()
        return "Booking created"
    @api.response(204, 'Booking Removed')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Cancel a booking")
    def delete(self, id):
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})

        booking = Booking.query.filter_by(listing_id=id, renter_id=current_user.public_id)
        if len(booking.all()) == 0:
            return "404, Cant find accomodation"
        
        booking.delete()
        db.session.commit()
        return "Post with id {} is removed".format(id)


# ===================== OWNER ============================== #
# For owners to see all their renters
@api.route('/owner/bookings')
class GetOwnerBookings(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Get all of owner's bookings.")
    def get(self):
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})

        owner_id = request.form.get('owner_id')
        booking = Booking.query.filter_by(owner_id=current_user.public_id).all()
        if len(booking) == 0:
            return jsonify({ "message" : "No bookings found" })
        return jsonify(booking=[i.serialize for i in booking])


@api.route('/owner/bookings/<int:id>')
class CancelOwnerBookings(Resource):
    @api.response(204, 'Booking Cancelled')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Let owner cancel a booking with listing_id.")
    def delete(self, id):
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})

        booking = Booking.query.filter_by(owner_id=current_user.public_id, listing_id=id).all()
        if len(booking) == 0:
            return "Not found"
        
        booking.sort(key=lambda x:x.id, reverse=True)
        booking_id = booking[0].id
        print(booking_id)
        tmp = Booking.query.filter_by(id=booking_id)
        tmp.delete()
        db.session.commit()
        return "Deleted booking of accomodation with listing_id of {}".format(id)
