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

# def get_data_cluster():
#     mmm = Michelin.query.all()
#     sss = Station.query.all()
#     ddd = Df.query.all()
#     mi_res = []
#     for mm in mmm:
#         mi_rec = {}
#         mi_rec['name'] = mm.name
#         mi_rec['year'] = mm.year
#         mi_rec['latitude'] = mm.latitude
#         mi_rec['longitude'] = mm.longitude
#         mi_rec['city'] = mm.city
#         mi_rec['cuisine'] = mm.cuisine
#         mi_rec['price'] = mm.price
#         mi_rec['url'] = mm.url
#         mi_rec['star'] = mm.star
#         mi_res.append(mi_rec)
#     df_mi = pd.DataFrame(mi_res)

#     sta_bus = []
#     for ss in sss:
#         sta_rec = {}
#         sta_rec['station_name'] = ss.station_name
#         sta_rec['_type'] = ss._type
#         sta_rec['latitude'] = ss.latitude
#         sta_rec['longitude'] = ss.longitude
#         sta_bus.append(sta_rec)

#     df_st = pd.DataFrame(sta_bus)


#     his_post = []
#     for dd in ddd:
#         his_rec = {}
#         his_rec['name'] = dd.name
#         his_rec['host_id'] = dd.host_id
#         his_rec['host_name'] = dd.host_name
#         his_rec['neighbourhood_group'] = dd.neighbourhood_group
#         his_rec['neighbourhood'] = dd.neighbourhood
#         his_rec['latitude'] = dd.latitude
#         his_rec['longitude'] = dd.longitude
#         his_rec['room_type'] = dd.room_type
#         his_rec['price'] = dd.price
#         his_rec['minimum_nights'] = dd.minimum_nights
#         his_rec['number_of_reviews'] = dd.number_of_reviews
#         his_rec['last_review'] = dd.last_review
#         his_rec['reviews_per_month'] = dd.reviews_per_month
#         his_rec['calculated_host_listings_count'] = dd.calculated_host_listings_count
#         his_rec['availability_365'] = dd.availability_365
#         his_post.append(his_rec)
#     df_po = pd.DataFrame(his_post)
#     return df_mi, df_st, df_po


# mi_pandas, st_pandas, post_pandas = get_data_cluster()




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
    @api.response(401, 'Repeat Username!')
    @api.doc(description="user register")
    @api.expect(register_model, validate=True)
    def post(self):
        data = request.get_json()
        password = data['password']
        name = data['username']
        user = User.query.filter_by(name = name).first()
        if user:
            return make_response('Repeat Username!', 401, {'Username': 'username conflict!"'})
        return jsonify({ "message": "User registered" })
#make_response('message', 401, {'Username': 'Token is missing!'})

@api.route('/userlist')
class GetUserList(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Forbidden : Need ADMIN')
    @api.doc(description="get all the user list, this function need admin user")
    def get(self):
        token = None
        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return make_response('message', 401, {'Username': 'Token is missing!'})
            #return make_response('message', 401, {'Username': 'Token is missing!'})# change to abort
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response('message', 401, {'Username': 'Token is Invalid!'})
            #return make_response('message', 401, {'Username': 'Token is Invalid!'})
        if not current_user.admin:
            make_response('message', 403, {'Username': 'need admin user'})
            #return make_response('message', 403, {'Username': 'need admin user to perform function'})
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


#input public userid
@api.route('/user/<public_id>')
class GetOneUser(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Forbidden : Need ADMIN')
    @api.doc(description="Get single user from the public_id, this function need admin user")
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

# sig_lg
@api.route('/token')
class TokenGeneration(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Generates a authentication token")
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

'''
return make_response('message', 401, {'Username': 'Token is missing!'})
return make_response('message', 401, {'Username': 'Token is Invalid!'})
return make_response('message', 403, {'Username': 'need admin user to perform function'})
'''


##room type accept the input private room / shared room / etc, room name can be part of the full name
@api.route('/search')
class SearchRoom(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Forbidden : Need ADMIN')
    @api.response(406, 'Input format error')
    @api.doc(description="Search the room you want, leave the empty string that you don't want to put")
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
        #print(during_time)
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



#token required
@api.route('/want/<int:id>')
class UserWant(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="return the recommendation according the room index to user")
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


@api.route('/stastic')
class SearchStastic(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.response(403, 'Forbidden : Need ADMIN')
    @api.doc(description="get all the user search records, this function need admin user")
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


###########
###########
###########
###########
###########
###########
# here is Jansen's route need to change to pure json

owner_model = api.model('accomodation', {
    'name': fields.String,
    # 'host_id': fields.String,
    # 'host_name': fields.String,
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

owner_parser = reqparse.RequestParser()
owner_parser.add_argument('name', type=str)
owner_parser.add_argument('host_id', type=str)
owner_parser.add_argument('host_name', type=str)
owner_parser.add_argument('neighbourhood_group', type=str)
owner_parser.add_argument('neighbourhood', type=str)

owner_parser.add_argument('latitude', type=str)
owner_parser.add_argument('longitude', type=str)
owner_parser.add_argument('room_type', type=str)
owner_parser.add_argument('price', type=str)
owner_parser.add_argument('minimum_nights', type=str)

owner_parser.add_argument('number_of_reviews', type=str)
owner_parser.add_argument('last_review', type=str)
owner_parser.add_argument('reviews_per_month', type=str)
owner_parser.add_argument('calculated_host_listings_count', type=str)
owner_parser.add_argument('availability_365', type=str)

# TODO
@app.route('/owner')
class Owner(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="Post a new accomodation")
    @api.expect(owner_parser, validate=True)
    def post(self):
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

        data = request.get_json()
        name = data['name']
        host_id = current_user.public_id
        host_name = current_user.name
        neighbourhood_group =data['location'] # REQ
        neighbourhood = data['area'] # REQ
        latitude = data['latitude']
        longitude = data['longitude']
        room_type = data['room_type'] # REQ
        price = data['price']
        minimum_nights = data['minimum_nights'] # REQ
        number_of_reviews = data['number_of_reviews']
        last_review = data['last_review']
        reviews_per_month = data['reviews_per_month']
        calculated_host_listings_count = data['calculated_host_listings_count']
        availability_365 = data['availability_365'] # REQ
        
        
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

        # first add a admin manully that control other user
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

        return jsonify({ "message": "Successful" })

@app.route('/owner_get', methods=['GET'])
@token_required
def owner_get(current_user):
    print(current_user.public_id)
    records = Df.query.filter_by(host_id=current_user.public_id).all()
    return jsonify(records=[i.serialize for i in records])

@app.route('/owner_remove/<id>', methods=['DELETE'])
@token_required
def remove_listing(current_user, id):
    res = Df.query.filter_by(id=id, host_id=current_user.public_id)
    if len(res.all()) == 0:
        return "Listing does not exist"
    res.delete()
    db.session.commit()
    return "Deleted the post with id {}".format(id)


# TODO
@app.route('/owner_edit/<id>', methods=['PUT'])
@token_required
def edit_listing(current_user, id):
    res = Df.query.filter_by(host_id=current_user.public_id, id=id)
    if len(res.all()) == 0:
        return "Listing does not exist"
    res = res.first()

    name = request.form.get('name')
    host_id = current_user.public_id
    host_name = current_user.name
    neighbourhood_group = request.form.get('location') # REQ
    neighbourhood = request.form.get('area') # REQ
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    room_type = request.form.get('room_type') # REQ
    price = request.form.get('price')
    minimum_nights = request.form.get('minimum_nights') # REQ
    number_of_reviews = request.form.get('number_of_reviews')
    last_review = request.form.get('last_review')
    reviews_per_month = request.form.get('reviews_per_month')
    calculated_host_listings_count = request.form.get('calculated_host_listings_count')
    availability_365 = request.form.get('availability_365') # REQ

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

    db.session.commit()
    return jsonify(temp_dic)

#put the public_id you want to subscribe


@api.route('/subscribe/<public_id>')
class SubscribeUser(Resource):
    @api.response(200, 'Successful')
    @api.response(401, 'Token is missing or Invalid')
    @api.doc(description="let user subscribe another user through public_id")
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
    @api.doc(description="let user unsubscribe another user through public_id")
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



###this part not for swagger , just for patment record
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
                    "price": "20.00",   #change the value at here
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "20.00",       #change total also here
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
@app.route('/book', methods=['GET'])
@token_required
def get_list_booking(current_user):
    booking = Booking.query.filter_by(renter_id=current_user.public_id).all()    
    return jsonify(booking=[i.serialize for i in booking])

# For customer to post a booking
@app.route('/book/<id>', methods=['POST'])
@token_required
def make_booking(current_user, id):
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

# for customer to cancel their booking
@app.route('/book/<id>', methods=['DELETE'])
@token_required
def del_booking(current_user, id):
    booking = Booking.query.filter_by(listing_id=id, renter_id=current_user.public_id)
    if len(booking.all()) == 0:
        return "404, Cant find accomodation"
    
    booking.delete()
    db.session.commit()
    return "Post with id {} is removed".format(id)


# ===================== OWNER ============================== #
# For owners to see all their renters
@app.route('/owner/bookings', methods=['GET'])
@token_required
def owner_bookings(current_user):
    owner_id = request.form.get('owner_id')
    booking = Booking.query.filter_by(owner_id=current_user.public_id).all()
    if len(booking) == 0:
        return "No bookings"
    return jsonify(booking=[i.serialize for i in booking])

# Delete bookings based on the listing id
@app.route('/owner/bookings/<int:id>', methods=['DELETE'])
@token_required
def del_owner_bookings(current_user, id):
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


# @app.route('/book', methods=['POST'])
# @token_required
# def post(self, current_user):
#     owner_id = request.form.get('owner_id')
#     listing_id = request.form.get('listing_id')
#     start_date = request.form.get('start_date')
#     end_date = request.form.get('end_date')
#     booking = Booking(owner_id=owner_id, listing_id=listing_id, start_date=start_date, end_date=end_date)
#     db.session.add(booking)
#     db.session.commit()
#     return "Booking created"