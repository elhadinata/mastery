from app import app, db
from app.models import User, Oprecord, OwnerPost
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
        data = request.get_json()
        password = request.form.get("password")
        name = request.form.get("name")
        print("HERE")
        print(request.data)
        hashed_password = generate_password_hash(password, method='sha256')
        # first add a admin manully that control other user
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
    print(form.validate_on_submit())
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
        # first add a admin manully that control other user
        new_op = Oprecord(user_id="current_user.public_id", location=location, area=area,
                          type_room=type_room, start_date=start_date, end_date=end_date, guest=guest,
                          price_1=price_1, price_2=price_2)
        db.session.add(new_op)
        db.session.commit()
        return jsonify(temp_dic)
    return render_template('search.html', form=form)


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

@app.route('/remove_listing/<id>', methods=['POST'])
@token_required
def remove_listing(current_user, id):
    OwnerPost.query.filter_by(user_id=current_user.public_id, id=id).delete()
    db.session.commit()
    return "Deleted the post with id {}".format(id)
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


