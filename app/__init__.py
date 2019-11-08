from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import  Api, fields


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
api = Api(app, 
	default="airbnb",
	title="airbnb dataset",
	description="Login to get token, then search.")

search_model = api.model('airbnb search', {
	'token':fields.String, 
	'location' : fields.String, 
	'area': fields.String,
	'type_room': fields.String,
	'start_date': fields.String,
	'end_date': fields.String,
	'guest': fields.String,
	'price_1': fields.String,
	'price_2': fields.String
	})


from app import routes, models