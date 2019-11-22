from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import  Api, fields
import pandas as pd
# from flask_restplus import cors

from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
api = Api(app, authorizations={
    'API-KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'api-token'
    }
},
    security='API-KEY',
	default="Airbnb",
	title="Airbnb dataset",
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



