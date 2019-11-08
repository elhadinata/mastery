from app import app, db
from app.models import User, Oprecord
from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for
import uuid
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from functools import wraps
from app.forms import SearchForm

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
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    # first add a admin manully that control other user
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created'})


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
        return make_response('Could not verify', 401, {'www-auth': 'basic realm="Login required!"'})
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'www-auth': 'basic realm="Login required!"'})
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    return make_response('Could not verify', 401, {'www-auth': 'basic realm="Login required!"'})



# this part should receive json text, it just a temple now
@app.route('/search', methods=['GET', 'POST'])
#@token_required
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
        temp_dic = {'location':location, 'area':area, 'type_room':type_room, 'start_date':start_date,
            'end_date':end_date, 'guest':guest, 'price_1': price_1, 'price_2': price_2
            }

        # first add a admin manully that control other user
        new_op = Oprecord(user_id = "current_user.public_id", location=location, area=area,
        	type_room=type_room, start_date=start_date, end_date=end_date,guest=guest,
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






