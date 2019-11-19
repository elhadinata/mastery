from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import  Api, fields
import pandas as pd

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







from app.models import User, Oprecord, OwnerPost, Michelin,Station,Df
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



from app import routes, models



