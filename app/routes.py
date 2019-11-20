from app import app, db
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


mi_pandas, st_pandas, post_pandas = get_data_cluster()




def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'api-token' in request.headers:
            token = request.headers['api-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


@app.route('/index', methods=['GET'])
def index():
    form = SearchForm(request.form)
    return render_template('index.html', form=form)


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # data = request.get_json()
        password = request.form.get('name')
        name = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(public_id=str(uuid.uuid4()), name=name, password=hashed_password, admin=True)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New user created'})
    return render_template('register.html')



@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Non-ADMIN user cannot performe that function'})
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


@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Non-ADMIN user cannot performe that function'})
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({'user': user_data})


@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Empty fields - Could not verify', 401, {'www-auth': 'basic realm="Login required!"'})
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'www-auth': 'basic realm="Login required!"'})
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
        )+datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    return make_response('Could not verify', 401, {'www-auth': 'basic realm="Login required!"'})


# this part should receive json text, it just a temple now
@app.route('/search', methods=['GET', 'POST'])
# @token_required
def search_for():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        location = form.location.data
        area = form.area.data
        type_room = form.type_room.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        guest = form.guest.data
        price_1 = form.price_1.data
        price_2 = form.price_2.data
        temp_dic = {'location': location, 'area': area, 'type_room': type_room, 'start_date': start_date,
                    'end_date': end_date, 'guest': guest, 'price_1': price_1, 'price_2': price_2
                    }

        if start_date == "":
            start_date = "1970-01-01"
        if end_date == "":
            end_date = "2021-01-01"

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
        new_op = Oprecord(user_id="current_user.public_id", location=location, area=area,
                          type_room=type_room, start_date=start_date, end_date=end_date, guest=guest,
                          price_1=price_1, price_2=price_2)
        db.session.add(new_op)
        db.session.commit()
        # return jsonify(final_res)
        return render_template('search_res.html', res= final_res)
    return render_template('search.html', form=form)

@app.route('/want/<int:id>')
def user_want(id):
    print(id)
    ml_model = ML_model()
    ml_model.prep_price_preds(post_pandas)
    row = ml_model.data.loc[id]
    rt = ml_model.rt_dict[row["room_type"]]
    ml_model.prep_knn_preds(rt)
    
    
    latitude = row['latitude']
    longitude = row['longitude']
    room_type = row['room_type']
    price = row['price']
    minumum_nights = row['minimum_nights']
    
    
    result  = ml_model.knn_prediction(latitude,longitude,room_type,price,minimum_nights)
    
    print(result.to_string())
    return "yes"




@app.route('/stastic', methods=['GET'])
@token_required
def stastic(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Non-ADMIN user cannot performe that function'})
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


@api.route('/search_json')
class SearchResults(Resource):
    # @token_required
    @api.expect(search_model, validate=False)
    def post(self):
        data = request.form.get('token')
        token = data
        if not token:
            return make_response(jsonify({'message': 'Token is missing!'}), 401)
        try:
            _data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=_data['public_id']).first()
        except:
            return make_response(jsonify({'message': 'Token is invalid'}), 401)

        location = request.form.get('location')
        area = request.form.get('area')
        type_room = request.form.get('type_room')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        guest = request.form.get('guest')
        price_1 = request.form.get('price_1')
        price_2 = request.form.get('price_2')
        _uid = current_user.public_id
        temp_dic = {'location': location, 'area': area, 'type_room': type_room, 'start_date': start_date,
                    'end_date': end_date, 'guest': guest, 'price_1': price_1, 'price_2': price_2,
                    'user_id': _uid}

        # first add a admin manully that control other user
        new_op = Oprecord(user_id=current_user.public_id, location=location, area=area,
                          type_room=type_room, start_date=start_date, end_date=end_date, guest=guest,
                          price_1=price_1, price_2=price_2)
        db.session.add(new_op)
        db.session.commit()

        return jsonify(temp_dic)

@app.route('/owner_post', methods=['POST'])
@token_required
def owner_post(current_user):
    #para
    location = request.form.get('location')
    area = request.form.get('area')
    type_room = request.form.get('type_room')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    guest = request.form.get('guest')
    price_1 = request.form.get('price_1')
    price_2 = request.form.get('price_2')
    if(request.form.get('Available')=='True'):
        available=True
    else:
        available=False
    _uid = current_user.public_id
    temp_dic = {'location': location, 'area': area, 'type_room': type_room, 'start_date': start_date,
                'end_date': end_date, 'guest': guest, 'price_1': price_1, 'price_2': price_2,
                'user_id': _uid}

    # first add a admin manully that control other user
    new_op = OwnerPost(user_id=current_user.public_id, location=location, area=area,
                        type_room=type_room, start_date=start_date, end_date=end_date, guest=guest,
                        price_1=price_1, price_2=price_2, Available=available)
    db.session.add(new_op)
    db.session.commit()

    return jsonify(new_op.__repr__())

@app.route('/owner_get', methods=['GET'])
@token_required
def owner_get(current_user):
    records = OwnerPost.query.filter_by(user_id=current_user.public_id).all()
    return jsonify(records=[i.serialize for i in records])

@app.route('/owner_remove/<id>', methods=['POST'])
@token_required
def remove_listing(current_user, id):
    res = OwnerPost.query.filter_by(user_id=current_user.public_id, id=id)
    if len(res.all()) == 0:
        return "Listing does not exist"
    res.delete()
    db.session.commit()
    return "Deleted the post with id {}".format(id)

@app.route('/owner_edit/<id>', methods=['PUT'])
@token_required
def edit_listing(current_user, id):
    res = OwnerPost.query.filter_by(user_id=current_user.public_id, id=id)
    if len(res.all()) == 0:
        return "Listing does not exist"
    res = res.first()
    location = request.form.get('location')
    area = request.form.get('area')
    type_room = request.form.get('type_room')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    guest = request.form.get('guest')
    price_1 = request.form.get('price_1')
    price_2 = request.form.get('price_2')
    available = request.form.get('Available')

    res.location = location
    res.area = area
    res.type_room = type_room
    res.start_date = start_date
    res.end_date = end_date
    res.guest = guest
    res.price_1 = price_1
    res.price_2 = price_2
    res.available = available

    db.session.commit()
    return "Edited the post with id {}".format(id)

#put the public_id you want to subscribe
@app.route('/subscribe/<public_id>')
@token_required
def subscribe(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if user is None:
        return "user not exist"
    if user == current_user:
        return "wait, are you subscribe yourself?"
    current_user.follow(user)
    db.session.commit()
    return "success!"


#put the public_id you want to unsubscribe
@app.route('/unsubscribe/<public_id>')
@token_required
def unsubscribe(current_user, public_id):
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



