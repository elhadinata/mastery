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
from flask_cors import CORS, cross_origin

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
            return make_response('message: Token is missing!', 401, {'Username': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message: Token is Invalid!', 401, {'Username': 'Token is Invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated



register_model = api.model('register', {
    'username': fields.String,
    'password': fields.String
})
@api.route('/user_register')
class UserRegister(Resource):
    @api.response(200, 'Successful')
    @api.response(406, 'Invalid username or password!')
    @api.doc(description="User registration. Please enter your username and password.\ne.g. input: username: 'testuser', password:'123456'\ne.g. output: message: User successfully registered")
    @api.expect(register_model, validate=True)
    def post(self):
        data = request.get_json()
        password = data['password']
        name = data['username']
        if len(name) < 4 or len(password) < 4:
            return make_response('message: invalid username or password', 406, {'Username': 'invalid username or password"'})
        user = User.query.filter_by(name = name).first()
        if user:
            return make_response('message: Username already exists!', 406, {'Username': 'username already exists!"'})
        
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(public_id=str(uuid.uuid4()), name=name, password=hashed_password, admin=True)
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({ "message: User successfully registered": "User successfully registered" }), 200)


@api.route('/userlist')
class GetUserList(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Forbidden : Need ADMIN')
    @api.doc(description="Get all the registered users, this function requires admin access.\ne.g.  output: users:[admin:true, name:admin, password:sha256$bcx15R3h$ff1494acab73103112d4ea6ec4a0e16, publid_id:e1132e1b-5508-4083-ac8a-021]")
    def get(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message: Token is missing!', 401, {'Username': 'Token is missing!'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message: Token is Invalid!', 401, {'Username': 'Token is Invalid!'})
        if not current_user.admin:
            make_response('message: need admin user access', 403, {'Username': 'need admin user access'})
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
    @api.response(403, 'Forbidden : Invalid ID')
    @api.doc(description="Get a single user according to his/her public_id, this function requires admin access. The input is the user's public id\ne.g. input: public_id: e1132e1b-5508-4083-ac8a-021\ne.g. output: users:[admin:true, name:admin, password:sha256$bcx15R3h$ff1, publid_id:e1132e1b-5508-4083-ac8a-021]")
    def get(self,public_id):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message: Token is missing!', 401, {'Username': 'Token is missing!'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
           
        except:
            return make_response('message: Token is Invalid!', 401, {'Username': 'Token is Invalid!'})
        if not current_user.admin:
            return make_response('message: Invalid ID', 403, {'Username': 'Invalid ID'})

        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return make_response('message: Invalid ID', 403, {'Username': 'Invalid ID'})
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
    @api.doc(description="Generates a authentication token. Please login using your username and password and get the token.\n e.g. input: username:'testuser', password:'123456'\n e.g. output: token:eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9")
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
            return make_response(jsonify({'token': token.decode('UTF-8')}), 200)
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
    @api.response(404, 'Room not found')
    @api.response(406, 'Input format error')
    @api.doc(description="Search for the room you are interested, you can leave the box empty if you like.\n e.g. input: location:'Central Region', area:'Queenstown', type_room:'Private room', start_Date:'', end_date:'',price_1:10, price_2:200\ne.g. output: ...")
    @api.expect(search_model)
    def post(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message:Token is missing!', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:

            return make_response('message', 401, {'Username': 'Token is Invalid!'})
        # if not current_user.admin:
        #     return make_response('message', 403, {'Username': 'need admin user to perform function'})
       
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
           # if not guest.is_integer():
           #     return make_response('Format error:format is Date: year-month-day, Price: integer, Room type:Private room, guest number should be integer', 406, {'value': 'format is Date: year-month-day, Price: integer, Room type:Private room, guest number should be integer '})
            time_s = time.mktime(time.strptime(start_date, "%Y-%m-%d"))
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
            if len(qq) == 0:
                return make_response('Not found', 404, {'value': 'cannot find any room according to hte input'})
        except:
            return make_response('Format error', 406, {'value': 'format is Date: year-month-day, Price: integer, Room type:Private room, guest number should be integer '})

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
        return make_response(jsonify(final_res), 200)



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
    'price' :fields.String,
})

price_pred_model = api.model('accomodation', {
    'name': fields.String,
    'location': fields.String,
    'area': fields.String,
    'latitude': fields.String,
    'longitude': fields.String,
    'room_type': fields.String,
    'minimum_nights': fields.String,
    'availability_365': fields.String,
})


@api.route('/accommodation/<int:id>/details')
class Details(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Return the details of the room according to its id.\ne.g. input: id:1\ne.g. output: record: {availability_365: 353, calculated_host_listings_count: 9, host_id: 367042, host_name: Belinda, ..., room_type: Private room")
    def get(self, id):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message: Token is missing!', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message: Token is Invalid!', 401, {'Username': 'Token is Invalid!'})

        record = Df.query.filter_by(id=id).first()
        if record is None:
            return make_response(jsonify(record=[]), 200)
        return make_response(jsonify(record=record.serialize), 200)

@api.route('/priceadvice')
class PricePrediction(Resource):
    
    @api.response(200, 'Successful')
    @api.response(400, 'Failed')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(406, 'Input format error')
    @api.doc(description="Provide price suggestions according to host's room information. You can leave the geo-location empty if you don't know. Blank input will be replaced by default values.\ne.g. input: name: 'clean rooms', location:'Central Region', area:'Queenstown', latitude:'', longitude:'',type_room:'Private room', minimum_nights:5, availability_365:365 \ne.g. output: message: 'suggested price range:', price_range_lower: 65, price_range_upper: 95")
    @api.expect(price_pred_model)
    def put(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message: Token is missing!', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message: Token is Invalid!', 401, {'Username': 'Token is Invalid!'})

  
        data = request.get_json()
  
       
        try:
            query = {}
            query['name'] = data['name']
            query['neighbourhood_group'] =data['neighbourhood_group']
            query['neighbourhood'] = data['neighbourhood']
            query['latitude'] = float(data['latitude'])
            query['longitude'] = float(data['longitude'])
            query['room_type'] = data['room_type']
            query['minimum_nights'] = int(data['minimum_nights'])
            query['availability_365'] = int(data['availability_365'])
            
            ml_model = ML_model()
            ml_model.prep_price_preds(post_pandas)
            if data['room_type'] =="":
                rt = 0
            else:
                rt = ml_model.rt_dict[data['room_type']]
            ml_model.build_price_model(rt)
            
            
            
            result  = ml_model.price_prediction(query)
            #print(result)
            lower = int(result[0])-15
            upper = int(result[0])+15 
            return make_response(jsonify({'message':"suggested price range:",'price_range_lower': lower,'price_range_upper':upper }), 200)

        except:
            return make_response('Format error', 406, {'value': "format is location: 'Central Region' etc., area: 'Queenstown' etc., Room type:'Private room', 'Entire home/apt', 'Shared room', minimum_nights and availability_365 shoule be integers"})
       

@api.route('/accommodation/<int:id>')
class UserAccomodation(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(404, 'Room ID not found')
    @api.doc(description="Return recommendations, nearby trainstations and nearby Michelin restaurants according to the room id.\ne.g. input: room id: 5\n e.g. output: {mi_listing: [nearby Michelin restaurants], recommendation: [rooms], single_detail:information of the chosen room, st_listing:[nearby train stations]}")
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
        try:
            row = ml_model.data.loc[id-1]
            rt = row["room_type"]
        except:
            return make_response('message', 404, {'ID': 'Room ID not found'})
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
        

        #mi_pandas, st_pandas, post_pandas
        #print(mi_pandas.columns)
        
        mi_lat_upper = float(room_detail[0]['latitude'])+0.04
        mi_lat_lower = float(room_detail[0]['latitude'])-0.04
        mi_lng_upper = float(room_detail[0]['longitude'])+0.04
        mi_lng_lower = float(room_detail[0]['longitude'])-0.04
        
        mi_pandas['latitude'] = pd.to_numeric(mi_pandas['latitude'])
        mi_pandas['longitude'] = pd.to_numeric(mi_pandas['longitude'])
        mi_lat_upper = mi_pandas[mi_pandas['latitude']<mi_lat_upper].copy()
        mi_lat_lower = mi_lat_upper[mi_lat_upper['latitude']>mi_lat_lower].copy()
        mi_lng_upper = mi_lat_lower[mi_lat_lower['longitude']<mi_lng_upper].copy()
        mi_lng_lower = mi_lng_upper[mi_lng_upper['longitude']>mi_lng_lower].copy()
        
        mi_listing = mi_lng_lower.T.to_dict().values()
        
        st_lat_upper = float(room_detail[0]['latitude'])+0.01
        st_lat_lower = float(room_detail[0]['latitude'])-0.01
        st_lng_upper = float(room_detail[0]['longitude'])+0.01
        st_lng_lower = float(room_detail[0]['longitude'])-0.01
        st_pandas['latitude'] = pd.to_numeric(st_pandas['latitude'])
        st_pandas['longitude'] = pd.to_numeric(st_pandas['longitude'])
        st_lat_upper = st_pandas[st_pandas['latitude']<st_lat_upper].copy()
        st_lat_lower = st_lat_upper[st_lat_upper['latitude']>st_lat_lower].copy()
        st_lng_upper = st_lat_lower[st_lat_lower['longitude']<st_lng_upper].copy()
        st_lng_lower = st_lng_upper[st_lng_upper['longitude']>st_lng_lower].copy()
        
        st_listing = st_lng_lower.T.to_dict().values()
        
        print(list(st_listing))
        return make_response(jsonify({'single_detail':room_detail,'recommendation': output,'mi_listing':list(mi_listing),'st_listing':list(st_listing)}), 200)

    @api.response(200, 'Successful')
    @api.response(400, 'Failed')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Post a new accommodation listing.\ne.g. input: availability_365: 355, calculated_host_listings_count: 9, host_id: 367042, host_name: Belinda, id: 5, last_review: 2019-07-28, latitude: 1.3456700000000001, longitude: 103.95963, minimum_nights: 1, name: B&B  Room 1 near Airport & EXPO, neighbourhood: Tampines, neighbourhood_group: East Region, number_of_reviews: 22, price: 94, reviews_per_month: 0.22, room_type: Private room\n e.g. output: Successful")
    @api.expect(owner_model)
    def put(self, id):
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
        
        return make_response({ "message": "Successfully Updated" }, 200)


    @api.response(200, 'Successful')
    @api.response(400, 'Failed')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Remove an accommodation.\ne.g. input: room id: 5\n e.g. output: Successful")
    def delete(self,id):
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
        return {"message": "Deleted the post with id {}".format(id)}, 200

@api.route('/statistics')
class SearchStatistics(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Forbidden : Admin priviledges required')
    @api.doc(description="Get all user search records, this function requires admin access.\ne.g. output: users: {area: b, end_date: 2021-01-01, guest: ""...}")
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

        if not curre10nt_user.admin:
            return make_response('message', 403, {'Username': 'Admin priviledges required to perform action'})
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
    @api.doc(description="Post a new accommodation listing.\ne.g. input: availability_365: 355, calculated_host_listings_count: 9, host_id: 367042, host_name: Belinda, id: 5, last_review: 2019-07-28, latitude: 1.3456700000000001, longitude: 103.95963, minimum_nights: 1, name: B&B  Room 1 near Airport & EXPO, neighbourhood: Tampines, neighbourhood_group: East Region, number_of_reviews: 22, price: 94, reviews_per_month: 0.22, room_type: Private room\n e.g. output: Successful")
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
    @api.response(403, 'Cannot subscribe yourself')
    @api.response(404, 'User not found')
    @api.doc(description="Let a user subscribe to another user with public_id.\ne.g. input: public_id: e1132e1b-5508-4083-ac8a-021\ne.g. output: Successful")
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
            return make_response('message', 404, {'User': 'User does not exist'})
        if user == current_user:
            return make_response('message', 403, {'User': 'Cannot subscribe yourself'})
        current_user.follow(user)
        db.session.commit()
        return jsonify({ "message": "Successfully subscribed"}), 200


@api.route('/unsubscribe/<public_id>')
class UnSubscribeUser(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Cannot unsubscribe yourself')
    @api.response(404, 'User not found')
    @api.doc(description="Let a user unsubscribe from another user with public_id.\ne.g. input: public_id: e1132e1b-5508-4083-ac8a-021\ne.g. output: Successful")
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
            return make_response('message', 404, {'User': 'User does not exist'})
        if user == current_user:
            return make_response('message', 403, {'User': 'Cannot unsubscribe from yourself'})
        current_user.unfollow(user)
        db.session.commit()
        return jsonify({ "message": "Successfully unsubscribed"}), 200


@app.route('/makepay/<int:id>', methods=['POST'])
def makepay(id):
    id = request.form.get('id')
    return render_template('makepay.html', data=id)


@app.route('/payment/<int:id>', methods=['POST'])
def payment(id):
    try:
        booking = Booking.query.filter_by(listing_id=id).all()[-1]
        listing = Df.query.filter_by(id=id).first()
        time_s = time.mktime(time.strptime(booking.start_date, "%Y-%m-%d"))
        time_e = time.mktime(time.strptime(booking.end_date, "%Y-%m-%d"))
        duration = int((time_e - time_s) / 86400)
        subtotal = duration * listing.price
    except:
        return make_response('Message',406, {'error':'Invalid booking'})
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
                    "name": f"{str(listing.name)}",
                    "sku": "12345",
                    "price": f"{str(subtotal)}",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": f"{str(subtotal)}",
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
    @api.doc(description="Get all the bookings of the current user.\ne.g. output: bookind=[...]")
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


book_model = api.model('booking', {
    'start_date': fields.String,
    'end_date': fields.String
})

@api.route('/book/<int:id>')
class MakeBooking(Resource):
    @api.response(201, 'Booking Created')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(406, 'Invalid information supplied')
    @api.doc(description="Make a booking on an accomodation.\ne.g. input: start_date: 2019-07-01, end_date: 2019-07-08\ne.g. output: Booking Created")
    @api.expect(book_model, validate=True)
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
            return make_response('message', 404, {'Accomodation': 'Cannot find accommodation'})
        
        data = request.get_json()
        start_date = data['start_date']
        end_date = data['end_date']
        if start_date == "":
            start_date = "1970-01-01"
        if end_date == "":
            end_date = "2021-01-01"

        try:
            time_s = time.mktime(time.strptime(start_date, "%Y-%m-%d"))
            time_e = time.mktime(time.strptime(end_date, "%Y-%m-%d"))
            duration = int((time_e - time_s) / 86400)
        except:
            return make_response('message', 406, {'Date': 'Format should be %Y-%m-%d'})
        if duration < int(owner_post.first().minimum_nights):
            return make_response('message', 406, {'Date': 'Length of stay below requirement'})
        
        df_data = owner_post.first()
        df_data.availability_365 = str(int(df_data.availability_365)-duration)

        booking = Booking(owner_id=owner_post.first().host_id, listing_id=id, renter_id=current_user.public_id, start_date=start_date, end_date=end_date)
        host_id = owner_post.first().host_id
        
        db.session.add(booking)
        db.session.commit()
        return "Booking created"
    @api.response(204, 'Booking Removed')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Cancel a booking using the booking id.\ne.g. input: booking id: 460\ne.g. output: Booking Removed")
    def delete(self, id):
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

        booking = Booking.query.filter_by(listing_id=id, renter_id=current_user.public_id)
        if len(booking.all()) == 0:
            return make_response('message', 404, {'Accomodation': 'Cannot find accommodation'})
        
        booking.delete()
        db.session.commit()
        return "Post with id {} is removed".format(id)


# ===================== OWNER ============================== #
# For owners to see all their renters
@api.route('/owner/bookings')
class GetOwnerBookings(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Get all of owner's bookings.\ne.g. output: booking:[...]")
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

        owner_id = request.form.get('owner_id')
        booking = Booking.query.filter_by(owner_id=current_user.public_id).all()
        if len(booking) == 0:
            return make_response(jsonify({ "message" : "No bookings found" }), 200)
        return make_response(jsonify(booking=[i.serialize for i in booking]), 200)


@api.route('/owner/bookings/<int:id>')
class CancelOwnerBookings(Resource):
    @api.response(200, 'Booking Cancelled')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Let owner cancel a booking with listing_id.\ne.g. input: booking id: 460\ne.g. output: Deleted booking of accomodation with listing_id of 460")
    def delete(self, id):
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

        booking = Booking.query.filter_by(owner_id=current_user.public_id, listing_id=id).all()
        if len(booking) == 0:
            return jsonify(booking=[])
        
        booking.sort(key=lambda x:x.id, reverse=True)
        booking_id = booking[0].id
        print(booking_id)
        tmp = Booking.query.filter_by(id=booking_id)
        tmp.delete()
        db.session.commit()
        return {"message":"Deleted booking of accomodation with listing_id of {}".format(id)}, 200
